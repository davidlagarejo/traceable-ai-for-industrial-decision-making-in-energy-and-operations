"""Playwright fallback — for JS-heavy public portals.

Many county / state portals (assessor records, environmental permits)
are rendered with heavy JS and don't expose REST APIs. For those,
Playwright (headless Chromium) is the right tool.

This module is OPTIONAL. If playwright is not installed:
  pip install playwright && playwright install chromium

…the fetcher returns status=SKIP with a clear message instead of
crashing. So the rest of the discovery layer keeps working.

Usage:
  from runtime_orchestrator.discovery_fetchers import playwright_scraper
  result = playwright_scraper.fetch_page(url="https://...", wait_for=".some-selector")
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from .base import FetcherResult, FetcherStatus


SOURCE_KEY = "playwright_scraper"

# Real-browser UA — federal/state portals and many corporate sites 403
# obvious bot UAs like "compatible; ZLab-Discovery/1.0".
_REAL_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15"
)


def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def fetch_page(
    url: str,
    *,
    wait_for_selector: str | None = None,
    wait_ms: int = 0,
    timeout_ms: int = 30000,
    headers: dict[str, str] | None = None,
) -> FetcherResult:
    """Render `url` with headless Chromium, return cleaned text + HTML."""
    now = _dt.datetime.utcnow().isoformat() + "Z"
    if not _playwright_available():
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error=(
                "playwright not installed. Run: "
                "pip install playwright && playwright install chromium"
            ),
            locator=url,
            fetched_at=now,
        )
    if not url:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="no url provided",
            fetched_at=now,
        )
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="playwright import failed",
            locator=url,
            fetched_at=now,
        )
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=_REAL_BROWSER_UA,
                viewport={"width": 1280, "height": 800},
                locale="en-US",
            )
            page = context.new_page()
            if headers:
                page.set_extra_http_headers(headers)
            page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            if wait_for_selector:
                try:
                    page.wait_for_selector(wait_for_selector, timeout=timeout_ms)
                except Exception:
                    pass  # selector didn't appear; continue with what loaded
            if wait_ms:
                page.wait_for_timeout(wait_ms)
            title = page.title()
            text  = page.inner_text("body")
            html  = page.content()
            browser.close()
            payload = {
                "title":   title,
                "text":    text[:50000],   # cap to 50k chars
                "html":    html[:200000],  # cap to 200k chars
                "url":     url,
                "rendered_at": now,
            }
            return FetcherResult(
                source_key=SOURCE_KEY,
                status=FetcherStatus.OK,
                payload=payload,
                locator=url,
                record_count=1,
                fetched_at=now,
            )
    except Exception as exc:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.ERROR,
            error=f"{type(exc).__name__}: {exc}",
            locator=url,
            fetched_at=now,
        )
