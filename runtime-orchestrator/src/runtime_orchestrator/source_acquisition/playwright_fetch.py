from __future__ import annotations

from typing import Any


def fetch_public_page_with_playwright(
    *,
    url: str,
    selector_plan: list[str] | None = None,
    timeout_ms: int = 8_000,
    max_navigations: int = 1,
) -> dict[str, Any]:
    selector_plan = list(selector_plan or [])
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception:
        return {
            "status": "unavailable",
            "error": "playwright_not_installed",
            "requested_url": url,
            "final_url": url,
            "html": "",
            "visible_text": "",
            "selector_lineage": [],
            "acquisition_mode": "playwright_public_page",
        }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 5_000))
            except Exception:
                pass
            final_url = page.url
            html = page.content()
            selector_lineage: list[dict[str, Any]] = []
            selector_probe_plan = [selector for selector in selector_plan if str(selector or "").strip()]
            if "body" not in selector_probe_plan:
                selector_probe_plan.append("body")
            preferred_text_selectors = [selector for selector in selector_probe_plan if selector != "body"] + ["body"]
            selector_wait_timeout = max(min(timeout_ms // 4, 3_000), 750)
            for selector in selector_probe_plan[: max_navigations + len(selector_probe_plan)]:
                locator = page.locator(selector).first
                try:
                    locator.wait_for(state="attached", timeout=selector_wait_timeout)
                except Exception:
                    pass
                try:
                    count = locator.count()
                except Exception:
                    count = 0
                text_length = 0
                if count:
                    try:
                        text_length = len(locator.inner_text(timeout=selector_wait_timeout).strip())
                    except Exception:
                        text_length = 0
                selector_lineage.append(
                    {
                        "selector": selector,
                        "match_count": count,
                        "visible_text_length": text_length,
                    }
                )
            visible_text = ""
            for selector in preferred_text_selectors:
                locator = page.locator(selector).first
                try:
                    candidate_text = locator.inner_text(timeout=max(timeout_ms // 2, 1_000)).strip()
                except Exception:
                    candidate_text = ""
                if candidate_text:
                    visible_text = candidate_text
                    break
            if not visible_text:
                try:
                    page.wait_for_timeout(1_000)
                    visible_text = page.locator("body").inner_text(timeout=max(timeout_ms // 2, 1_000)).strip()
                except Exception:
                    visible_text = ""
            context.close()
            browser.close()
            return {
                "status": "success",
                "requested_url": url,
                "final_url": final_url,
                "html": html,
                "visible_text": visible_text,
                "selector_lineage": selector_lineage,
                "acquisition_mode": "playwright_public_page",
            }
    except PlaywrightTimeoutError as exc:
        return {
            "status": "timeout",
            "error": str(exc)[:200],
            "requested_url": url,
            "final_url": url,
            "html": "",
            "visible_text": "",
            "selector_lineage": [],
            "acquisition_mode": "playwright_public_page",
        }
    except Exception as exc:
        return {
            "status": "failed",
            "error": str(exc)[:200],
            "requested_url": url,
            "final_url": url,
            "html": "",
            "visible_text": "",
            "selector_lineage": [],
            "acquisition_mode": "playwright_public_page",
        }
