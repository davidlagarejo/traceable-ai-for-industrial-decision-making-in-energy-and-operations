"""Vendor whitepaper crawler — visita los hubs de recursos de marcas
industriales confiables (VENDOR_TRUST_PUBLISHERS) y descarga PDFs.

Each vendor entry has:
  · vendor key (matches manifest.VENDOR_TRUST_PUBLISHERS)
  · hub URLs (1+ pages listing whitepapers/technical bulletins)
  · asset_families this vendor's content applies to

Pipeline per vendor:
  1. Playwright loads the hub page
  2. Find every <a> with href ending in .pdf (or matching whitepaper URL pattern)
  3. For each PDF link:
       · skip if URL hash already in industry_corpus
       · fetch_pdf_from_url (already has Playwright fallback)
       · auto-approve because publisher is in VENDOR_TRUST_PUBLISHERS

Phase 0: keyword filter, no LLM. Domain allowlist enforced.
"""
from __future__ import annotations

import datetime as _dt
import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Curated vendor hubs. Each entry: hub_url, asset_families.
# Selected for high signal (these pages aggregate technical PDFs):
VENDOR_HUBS: dict[str, list[dict[str, Any]]] = {
    "spirax sarco": [{
        "hub_url": "https://www.spiraxsarco.com/resources-and-design-tools/whitepapers",
        "asset_families": ["manufacturing_facility", "infrastructure_node"],
    }],
    "armstrong international": [{
        "hub_url": "https://www.armstronginternational.com/resources",
        "asset_families": ["manufacturing_facility", "infrastructure_node"],
    }],
    "trane": [{
        "hub_url": "https://www.trane.com/commercial/north-america/us/en/products-systems/equipment-and-systems.html",
        "asset_families": ["commercial_building"],
    }],
    "carrier": [{
        "hub_url": "https://www.carrier.com/commercial/en/us/news/",
        "asset_families": ["commercial_building", "cold_chain_facility"],
    }],
    "johnson controls": [{
        "hub_url": "https://www.johnsoncontrols.com/insights",
        "asset_families": ["commercial_building"],
    }],
    "danfoss": [{
        "hub_url": "https://www.danfoss.com/en/about-danfoss/news-and-media/",
        "asset_families": ["cold_chain_facility", "manufacturing_facility"],
    }],
    "abb": [{
        "hub_url": "https://library.e.abb.com/public",
        "asset_families": ["manufacturing_facility", "infrastructure_node"],
    }],
    "siemens": [{
        "hub_url": "https://www.siemens.com/global/en/products/energy/news.html",
        "asset_families": ["manufacturing_facility", "infrastructure_node"],
    }],
    "schneider electric": [{
        "hub_url": "https://www.se.com/us/en/work/insights/",
        "asset_families": ["commercial_building", "manufacturing_facility"],
    }],
    "honeywell": [{
        "hub_url": "https://www.honeywell.com/us/en/news",
        "asset_families": ["manufacturing_facility", "commercial_building"],
    }],
    "emerson": [{
        "hub_url": "https://www.emerson.com/en-us/automation/asset-monitoring",
        "asset_families": ["manufacturing_facility"],
    }],
    "atlas copco": [{
        "hub_url": "https://www.atlascopco.com/en-us/compressors/wiki",
        "asset_families": ["manufacturing_facility"],
    }],
    "ingersoll rand": [{
        "hub_url": "https://www.ingersollrand.com/en-us/services-and-support",
        "asset_families": ["manufacturing_facility"],
    }],
    "linde": [{
        "hub_url": "https://www.lindeus.com/about-us/resources",
        "asset_families": ["manufacturing_facility", "_shared"],
    }],
    "air products": [{
        "hub_url": "https://www.airproducts.com/resources",
        "asset_families": ["manufacturing_facility", "_shared"],
    }],
    "grundfos": [{
        "hub_url": "https://www.grundfos.com/about-us/insights",
        "asset_families": ["commercial_building", "infrastructure_node"],
    }],
    "alfa laval": [{
        "hub_url": "https://www.alfalaval.com/about-us/news/",
        "asset_families": ["manufacturing_facility", "cold_chain_facility"],
    }],
}


@dataclass(frozen=True)
class VendorWhitepaperCandidate:
    publisher:        str          # vendor key e.g. "spirax sarco"
    source_id:        str          # vendor_<slug>_<hash>
    title:            str
    url:              str          # direct PDF URL
    asset_families:   tuple[str, ...]
    publication_date: str = ""
    abstract:         str = ""
    raw_subjects:     tuple[str, ...] = ()


_PDF_HREF = re.compile(r"\.pdf(?:[?#].*)?$", re.IGNORECASE)


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:60] or "untitled"


def _absolute_url(href: str, base: str) -> str:
    return urllib.parse.urljoin(base, href)


def _scrape_vendor_hub(
    hub_url: str,
    *, max_pdfs: int = 25, timeout_ms: int = 25_000,
) -> list[tuple[str, str]]:
    """Open hub_url with Playwright (real browser UA), find every PDF link.
    Returns [(pdf_url, link_text), …]. Empty list on any failure.
    """
    try:
        from runtime_orchestrator.zlab_skill.licensed_playwright_fetch import _load_playwright_sync_api
    except Exception:
        return []
    try:
        sync_playwright, _ = _load_playwright_sync_api()
    except Exception:
        return []

    out: list[tuple[str, str]] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/17.2 Safari/605.1.15"
                ),
                locale="en-US",
            )
            page = context.new_page()
            try:
                page.goto(hub_url, wait_until="domcontentloaded", timeout=timeout_ms)
                try:
                    page.wait_for_load_state("networkidle", timeout=8_000)
                except Exception:
                    pass
                anchors = page.query_selector_all("a[href]")
                for a in anchors:
                    try:
                        href = a.get_attribute("href") or ""
                        if not href or not _PDF_HREF.search(href):
                            continue
                        text = (a.inner_text() or "").strip()[:200]
                        abs_url = _absolute_url(href, hub_url)
                        out.append((abs_url, text))
                        if len(out) >= max_pdfs * 2:  # gather extras for dedup
                            break
                    except Exception:
                        continue
            finally:
                browser.close()
    except Exception:
        return out  # whatever we got before failure
    return out


_VENDOR_DOMAIN: dict[str, list[str]] = {
    "spirax sarco":            ["spiraxsarco.com"],
    "armstrong international": ["armstronginternational.com"],
    "trane":                   ["trane.com"],
    "carrier":                 ["carrier.com"],
    "johnson controls":        ["johnsoncontrols.com"],
    "danfoss":                 ["danfoss.com"],
    "abb":                     ["abb.com", "e.abb.com"],
    "siemens":                 ["siemens.com"],
    "schneider electric":      ["se.com", "schneider-electric.com"],
    "honeywell":               ["honeywell.com"],
    "emerson":                 ["emerson.com"],
    "atlas copco":             ["atlascopco.com"],
    "ingersoll rand":          ["ingersollrand.com"],
    "linde":                   ["linde.com", "lindeus.com"],
    "air products":            ["airproducts.com"],
    "grundfos":                ["grundfos.com"],
    "alfa laval":              ["alfalaval.com"],
}


def _ddg_pdf_search(vendor_domains: list[str], topic: str, *, max_results: int = 10) -> list[dict[str, str]]:
    """Search DuckDuckGo for PDFs limited to vendor domains.
    Returns [{url, title, snippet}]. Reuses the company_web_scraper logic.
    """
    try:
        from runtime_orchestrator.discovery_fetchers.company_web_scraper import _ddg_search
    except Exception:
        return []
    domain_filter = " OR ".join(f"site:{d}" for d in vendor_domains)
    query = f"({domain_filter}) {topic} filetype:pdf"
    hits = _ddg_search(query, limit=max_results)
    return hits


_VENDOR_TOPICS_BY_FAMILY = {
    "manufacturing_facility":    ["energy efficiency", "industrial heat recovery",
                                  "compressed air audit", "process optimization"],
    "cold_chain_facility":       ["refrigeration", "ammonia safety", "cold storage energy"],
    "datacenter":                ["data center cooling", "PUE optimization"],
    "commercial_building":       ["HVAC chiller efficiency", "building automation"],
    "warehouse_distribution":    ["warehouse energy", "fulfillment center"],
    "infrastructure_node":       ["substation", "transmission", "grid integration"],
}


def discover_vendor_whitepapers(
    vendor_key: str,
    *,
    max_pdfs: int = 10,
) -> list[VendorWhitepaperCandidate]:
    """Find PDF whitepapers from a vendor via DuckDuckGo + domain filter.

    More reliable than scraping hub pages — modern vendor sites gate
    their resources behind JS or forms. DDG indexes the public PDFs that
    leaked into the search engine, which is what's actually citable.
    """
    domains = _VENDOR_DOMAIN.get(vendor_key, [])
    hubs = VENDOR_HUBS.get(vendor_key, [])
    if not domains or not hubs:
        return []
    # Aggregate topics from every asset_family this vendor serves
    asset_families = sorted({af for h in hubs for af in h["asset_families"]})
    topics: list[str] = []
    for af in asset_families:
        topics.extend(_VENDOR_TOPICS_BY_FAMILY.get(af, []))
    topics = topics or ["whitepaper technical"]

    seen_urls: set[str] = set()
    out: list[VendorWhitepaperCandidate] = []
    for topic in topics:
        if len(out) >= max_pdfs:
            break
        hits = _ddg_pdf_search(domains, topic, max_results=max_pdfs * 2)
        for h in hits:
            url = (h.get("url") or "").strip()
            if not url or not _PDF_HREF.search(url):
                continue
            # Confirm URL is in vendor domains (DDG can drift)
            parsed = urllib.parse.urlparse(url)
            if not any(d in parsed.netloc.lower() for d in domains):
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            title = (h.get("title") or "").strip()[:200]
            slug = _slugify(title or url.rsplit("/", 1)[-1])
            import hashlib
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:8]
            source_id = f"vendor_{_slugify(vendor_key)}_{slug[:30]}_{url_hash}"
            out.append(VendorWhitepaperCandidate(
                publisher=vendor_key,
                source_id=source_id,
                title=title or url.rsplit("/", 1)[-1],
                url=url,
                asset_families=tuple(asset_families),
                abstract=h.get("snippet", "")[:280],
            ))
            if len(out) >= max_pdfs:
                break
    return out


def discover_all_vendors(
    *, max_pdfs_per_vendor: int = 8,
) -> dict[str, list[VendorWhitepaperCandidate]]:
    """Crawl every vendor in VENDOR_HUBS."""
    return {
        vendor: discover_vendor_whitepapers(vendor, max_pdfs=max_pdfs_per_vendor)
        for vendor in VENDOR_HUBS
    }
