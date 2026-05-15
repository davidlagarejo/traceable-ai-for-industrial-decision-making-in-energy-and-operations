"""Company Web Scraper — DuckDuckGo search + Playwright render.

For facilities that are PRIVATE (not in SEC EDGAR, not in county records
we can fetch automatically), we fall back to a web search of the
company's own public footprint:

  1. Build query: "{facility_name} {city} {state}"
  2. DuckDuckGo HTML search (no key, no rate limit on light use)
  3. Filter out unrelated results
  4. For top 3 candidate hits, render with Playwright to extract:
       · facility size / sq ft if mentioned
       · services / business lines
       · contact info / address validation
       · any technical claims (capacity, equipment, etc.)

This is BEST-EFFORT — quality depends on whether the company has
a useful public website. Returns a structured payload with the raw
text extracted; downstream consumers parse what they need.
"""
from __future__ import annotations

import datetime as _dt
import html
import re
import urllib.parse

from .base import (
    DEFAULT_USER_AGENT,
    FetcherContext,
    FetcherResult,
    FetcherStatus,
    http_get_text,
)
from . import playwright_scraper


SOURCE_KEY = "company_web_scraper"

_DDG_HTML = "https://html.duckduckgo.com/html/"


def _ddg_search(query: str, limit: int = 5) -> list[dict[str, str]]:
    """DuckDuckGo HTML search. Returns list of {title, url, snippet}.

    Uses POST to the lite HTML endpoint. No API key. Light scraping —
    DDG's terms allow this for legitimate use.
    """
    import urllib.request
    body = urllib.parse.urlencode({"q": query, "kl": "us-en"}).encode("utf-8")
    req = urllib.request.Request(_DDG_HTML, data=body, method="POST")
    req.add_header("User-Agent", DEFAULT_USER_AGENT)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return []
    # Parse results from HTML — DDG HTML output is reasonably stable
    results: list[dict[str, str]] = []
    # Each result is roughly: <a class="result__a" href="URL">TITLE</a> ... <a class="result__snippet">SNIPPET</a>
    pattern = re.compile(
        r'<a\s+[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?<a\s+[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        raw_url = html.unescape(m.group(1))
        title   = re.sub(r"<[^>]+>", "", html.unescape(m.group(2))).strip()
        snippet = re.sub(r"<[^>]+>", "", html.unescape(m.group(3))).strip()
        # DDG redirect — unwrap
        if "duckduckgo.com" in raw_url and "uddg=" in raw_url:
            try:
                qs = urllib.parse.urlparse(raw_url).query
                params = urllib.parse.parse_qs(qs)
                if "uddg" in params:
                    raw_url = params["uddg"][0]
            except Exception:
                pass
        results.append({
            "title":   title,
            "url":     raw_url,
            "snippet": snippet[:280],
        })
        if len(results) >= limit:
            break
    return results


_NEGATIVE_DOMAINS: set[str] = {
    "facebook.com", "linkedin.com/in/", "twitter.com", "x.com",
    "instagram.com", "tiktok.com", "youtube.com",
    # Aggregators that rarely add value
    "bizapedia.com", "manta.com", "yelp.com", "tripadvisor.com",
}


def _is_useful(url: str) -> bool:
    """Filter out social/aggregator domains."""
    u = (url or "").lower()
    for bad in _NEGATIVE_DOMAINS:
        if bad in u:
            return False
    return True


def _extract_useful_signals(text: str) -> dict[str, list[str]]:
    """Extract technical / commercial signals from rendered page text."""
    signals: dict[str, list[str]] = {
        "sq_ft_mentions":     [],
        "capacity_mentions":  [],
        "service_mentions":   [],
        "equipment_mentions": [],
        "certification_mentions": [],
        "address_mentions":   [],
    }
    text_l = (text or "").lower()
    # Square footage
    for m in re.finditer(r"(\d[\d,\.]*\s*(?:million\s+)?(?:sq[\.\s]*ft|square\s+feet|square\s+foot))", text_l):
        signals["sq_ft_mentions"].append(m.group(1)[:80])
    # Storage capacity (cubic ft, pallets, etc.)
    for m in re.finditer(r"(\d[\d,\.]*\s*(?:pallets?|cubic\s+(?:feet|foot|meters)|tons?\s+of\s+storage))", text_l):
        signals["capacity_mentions"].append(m.group(1)[:80])
    # Service / business lines (cold chain specific + generic)
    for kw in ["cold storage", "frozen storage", "refrigerated warehouse",
               "blast freezing", "third-party logistics", "3pl",
               "distribution center", "food grade",
               "ammonia refrigeration", "fda registered",
               "haccp", "ce certified", "iso 9001", "iso 22000"]:
        if kw in text_l:
            signals["service_mentions"].append(kw)
    # Equipment hints
    for kw in ["compressor", "evaporator", "condenser", "ammonia",
               "freon", "co2 refrigeration", "blast chiller",
               "racking", "dock door", "automated storage"]:
        if kw in text_l:
            signals["equipment_mentions"].append(kw)
    # Certifications
    for kw in ["sqf certified", "brc certified", "haccp", "usda",
               "fda registered", "iso 9001", "iso 14001", "iso 22000",
               "global gap"]:
        if kw in text_l:
            signals["certification_mentions"].append(kw)
    # Dedup
    for k in signals:
        signals[k] = sorted(set(signals[k]))[:10]
    return signals


def fetch(context: FetcherContext, *, max_pages: int = 3) -> FetcherResult:
    """Search for company website + scrape candidates with Playwright.

    Uses Playwright when installed (renders JS-heavy company sites);
    falls back to a no-render HTTP fetch otherwise.
    """
    now = _dt.datetime.utcnow().isoformat() + "Z"
    name = (context.facility_name or "").strip()
    if not name:
        # Try to derive from address as fallback (best-effort)
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="no facility_name provided",
            fetched_at=now,
        )

    # Build query
    query_parts = [name]
    if context.city:
        query_parts.append(context.city)
    if context.state:
        query_parts.append(context.state)
    query = " ".join(query_parts)

    hits = _ddg_search(query, limit=10)
    useful = [h for h in hits if _is_useful(h.get("url", ""))][:max_pages]

    if not useful:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.NO_DATA,
            payload={"query": query, "all_hits": hits[:5]},
            error="no useful web hits for company",
            fetched_at=now,
        )

    pages: list[dict] = []
    aggregate_signals: dict[str, set[str]] = {
        "sq_ft_mentions":         set(),
        "capacity_mentions":      set(),
        "service_mentions":       set(),
        "equipment_mentions":     set(),
        "certification_mentions": set(),
        "address_mentions":       set(),
    }
    for h in useful:
        url = h["url"]
        # Try Playwright first for full render; fall back to HTTP if not available
        page_result = playwright_scraper.fetch_page(
            url, timeout_ms=20000, wait_ms=1500,
        )
        rendered_text = ""
        if page_result.status == FetcherStatus.OK:
            rendered_text = str(page_result.payload.get("text", ""))
        else:
            # HTTP fallback
            try:
                text, _ = http_get_text(url, timeout=12)
                # Strip HTML tags quickly
                rendered_text = re.sub(r"<[^>]+>", " ", text)
            except Exception:
                rendered_text = ""
        signals = _extract_useful_signals(rendered_text)
        for k, vs in signals.items():
            aggregate_signals[k].update(vs)
        pages.append({
            "url":       url,
            "title":     h.get("title", ""),
            "snippet":   h.get("snippet", ""),
            "rendered":  page_result.status.value if hasattr(page_result.status, "value") else str(page_result.status),
            "text_len":  len(rendered_text),
            "signals":   signals,
        })

    payload: dict = {
        "query":                 query,
        "hits_considered":       len(hits),
        "hits_visited":          len(pages),
        "pages":                 pages,
        "aggregate_signals":     {k: sorted(v) for k, v in aggregate_signals.items()},
        "total_signals":         sum(len(v) for v in aggregate_signals.values()),
    }
    has_useful = payload["total_signals"] > 0
    return FetcherResult(
        source_key=SOURCE_KEY,
        status=FetcherStatus.OK if has_useful else FetcherStatus.NO_DATA,
        payload=payload,
        locator=f"web_scrape:{query[:80]}",
        record_count=len(pages),
        fetched_at=now,
    )
