"""Licensed journal discoverer — IEEE Xplore, Springer Link, Scopus.

Reuses the existing licensed-session machinery built earlier:
  · zlab_skill/playwright_profiles.py — profile path per provider
  · zlab_skill/provider_sessions.py    — session plan + login state
  · zlab_skill/licensed_playwright_fetch.py — Playwright fetch with profile

This module adds the SEARCH layer:
  1. search_ieee(keyword)       → list of paper landing URLs
  2. search_springer(keyword)   → idem
  3. search_scopus(keyword)     → idem (requires Scopus session)
  4. discover_for_family(af)    → unified CandidateSource list

Phase 0 doctrine:
  · Paywall content → chunks_pending/ (NEVER auto-approve).
  · License tagged "licensed_journal" — only verbatim short quotes (Regla 11
    fair-use ≤300 chars per chunk citation).
  · Search is keyword filtering, no LLM.

Pre-requirement: user must run once
  scripts/bootstrap_licensed_provider_session.py --provider ieee
  (and same for springer / scopus) — opens Playwright headed for manual
  login. Cookies persist in ~/.zlab_skill/playwright_profiles/.
"""
from __future__ import annotations

import datetime as _dt
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Reuse the existing keyword maps from osti_discoverer
from .osti_discoverer import SUBJECT_KEYWORDS


# ── Search URL templates per provider ─────────────────────────────────


_SEARCH_TEMPLATES: dict[str, str] = {
    "ieee": (
        "https://ieeexplore.ieee.org/search/searchresult.jsp"
        "?queryText={q}&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true"
    ),
    "springer": (
        "https://link.springer.com/search"
        "?query={q}&search-submit=Submit"
    ),
    "scopus": (
        "https://www.scopus.com/results/results.uri"
        "?src=s&s=TITLE-ABS-KEY%28{q}%29"
    ),
}


# Selector strategies for each provider's search-result page
_RESULT_SELECTORS: dict[str, dict[str, str]] = {
    "ieee": {
        "result_container": ".List-results-items, xpl-results-item",
        "title":            ".result-item-title a, h3.text-md-md-lh a",
        "abstract":         ".description, .result-item-abstract",
        "doi":              "[data-doi], .stats-document-abstract-publishedIn",
    },
    "springer": {
        "result_container": "li.has-cover-art, .gst-result",
        "title":            ".title a, .gst-result-title a, h2 a",
        "abstract":         ".snippet, .gst-result-content",
        "doi":              ".doi, .gst-result-doi",
    },
    "scopus": {
        "result_container": ".result-item, .searchResult",
        "title":            ".result-list-title-link, .resultDocTitle",
        "abstract":         ".result-item-description",
        "doi":              ".doi",
    },
}


# ── Public candidate type (shape-compatible with osti/arxiv) ──────────


@dataclass(frozen=True)
class LicensedJournalCandidate:
    publisher:       str               # "ieee" | "springer" | "scopus"
    source_id:       str               # "ieee_doc_<arnumber>" | "springer_<doi_slug>"
    title:           str
    url:             str               # landing page URL (paper page, not PDF)
    asset_families:  tuple[str, ...]
    publication_date: str
    abstract:        str
    doi:             str
    raw_subjects:    tuple[str, ...] = ()   # for compat with orchestrator


# ── Provider-specific search functions ────────────────────────────────


def _run_playwright_search(
    *,
    provider_key: str,
    keyword: str,
    max_results: int = 10,
    timeout_ms: int = 20_000,
    headless: bool = True,
) -> list[dict[str, Any]]:
    """Open the provider's search results page in a persistent Playwright
    session and extract the top-N result rows. Returns list[dict] with
    title/url/abstract/doi keys. Empty list if session expired or no hits.
    """
    try:
        from runtime_orchestrator.zlab_skill.licensed_playwright_fetch import (
            _load_playwright_sync_api,
        )
        from runtime_orchestrator.zlab_skill.provider_sessions import (
            build_provider_session_plan,
        )
    except Exception:
        return []

    template = _SEARCH_TEMPLATES.get(provider_key)
    if not template:
        return []
    search_url = template.format(q=urllib.parse.quote_plus(keyword))
    plan = build_provider_session_plan(
        url=search_url, retrieval_purpose="industry_corpus_discovery",
        session_label="licensed",
    )
    profile_path = Path(
        str(plan.get("profile_plan", {}).get("profile_path", "")).strip()
    ).expanduser()
    if not profile_path.exists():
        return []

    selectors = _RESULT_SELECTORS.get(provider_key, {})
    try:
        sync_playwright, PWTimeout = _load_playwright_sync_api()
    except Exception:
        return []

    results: list[dict[str, Any]] = []
    try:
        with sync_playwright() as pw:
            ctx = pw.chromium.launch_persistent_context(
                user_data_dir=str(profile_path),
                headless=headless,
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
                ),
            )
            try:
                page = ctx.new_page()
                page.goto(search_url, wait_until="domcontentloaded", timeout=timeout_ms)
                try:
                    page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 8_000))
                except Exception:
                    pass
                container_sel = selectors.get("result_container") or "*"
                items = page.query_selector_all(container_sel)
                for item in items[:max_results]:
                    try:
                        title_el = item.query_selector(selectors.get("title", "a")) if selectors.get("title") else None
                        abst_el = item.query_selector(selectors.get("abstract", "")) if selectors.get("abstract") else None
                        doi_el = item.query_selector(selectors.get("doi", "")) if selectors.get("doi") else None
                        title = (title_el.inner_text() if title_el else "").strip()[:300]
                        href = (title_el.get_attribute("href") if title_el else "") or ""
                        if href and href.startswith("/"):
                            # Relative → absolute via search_url netloc
                            netloc = urllib.parse.urlparse(search_url).netloc
                            href = f"https://{netloc}{href}"
                        abstract = (abst_el.inner_text() if abst_el else "").strip()[:600]
                        doi = (doi_el.inner_text() if doi_el else "").strip()[:200]
                        if title and href:
                            results.append({
                                "title": title, "url": href,
                                "abstract": abstract, "doi": doi,
                            })
                    except Exception:
                        continue
            finally:
                ctx.close()
    except Exception:
        return []
    return results


def _candidate_from_row(row: dict[str, Any], provider: str,
                        asset_family: str) -> LicensedJournalCandidate | None:
    """Convert a raw search row into a typed CandidateSource."""
    title = (row.get("title") or "").strip()
    url = (row.get("url") or "").strip()
    if not title or not url:
        return None
    # Stable source_id from URL hash (last path segment usually carries the id)
    parsed = urllib.parse.urlparse(url)
    last_seg = parsed.path.rstrip("/").rsplit("/", 1)[-1]
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", last_seg)[:48] or "unknown"
    source_id = f"{provider}_{safe}"
    return LicensedJournalCandidate(
        publisher=provider,
        source_id=source_id,
        title=title,
        url=url,
        asset_families=(asset_family,),
        publication_date="",
        abstract=(row.get("abstract") or "").strip()[:600],
        doi=(row.get("doi") or "").strip()[:200],
    )


def discover_for_family(
    asset_family: str,
    *,
    providers: tuple[str, ...] = ("ieee", "springer"),
    max_per_keyword: int = 5,
    max_candidates: int = 25,
    headless: bool = True,
) -> list[LicensedJournalCandidate]:
    """Search every enabled licensed provider for papers relevant to
    `asset_family`, using the existing per-provider Playwright session
    profile. Returns dedup-by-source_id list.

    If a provider's session is expired, results from that provider will
    be empty — callers should detect this and prompt re-authentication.
    """
    keywords = SUBJECT_KEYWORDS.get(asset_family, [])
    if not keywords:
        return []
    seen: set[str] = set()
    out: list[LicensedJournalCandidate] = []
    for provider in providers:
        for kw in keywords:
            if len(out) >= max_candidates:
                break
            rows = _run_playwright_search(
                provider_key=provider, keyword=kw,
                max_results=max_per_keyword, headless=headless,
            )
            for row in rows:
                cand = _candidate_from_row(row, provider, asset_family)
                if not cand or cand.source_id in seen:
                    continue
                seen.add(cand.source_id)
                out.append(cand)
                if len(out) >= max_candidates:
                    break
    return out


def session_status() -> dict[str, dict[str, Any]]:
    """Audit current state of every provider's persistent session.

    Reads the actual profile directories under
    ~/.zlab_skill/playwright_profiles/zlab_skill_<provider>_licensed/.
    Returns per provider: profile_exists, cookies_present,
    cookies_age_days, likely_expired.
    """
    try:
        from runtime_orchestrator.zlab_skill.playwright_profiles import (
            provider_profile_path,
        )
    except Exception as exc:
        return {"_error": str(exc)}

    out: dict[str, dict[str, Any]] = {}
    for provider in ("ieee", "springer", "scopus", "elsevier"):
        try:
            profile = provider_profile_path(provider, session_label="licensed")
            cookies = profile / "Default" / "Cookies"
            entry = {
                "profile_path":   str(profile),
                "profile_exists": profile.exists(),
                "cookies_present": cookies.exists(),
            }
            if cookies.exists():
                age_days = (
                    _dt.datetime.utcnow()
                    - _dt.datetime.utcfromtimestamp(cookies.stat().st_mtime)
                ).days
                entry["cookies_age_days"] = age_days
                entry["likely_expired"] = age_days > 7
            out[provider] = entry
        except Exception as exc:
            out[provider] = {"error": str(exc)}
    return out
