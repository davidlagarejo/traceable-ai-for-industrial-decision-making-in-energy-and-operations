from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse


_LOGIN_URL_TOKENS = ("login", "signin", "sign-in", "oauth", "auth")
_LOGIN_TEXT_TOKENS = (
    "sign in",
    "log in",
    "institutional access",
    "access through your institution",
    "your institution",
)


def _load_playwright_sync_api() -> tuple[Any, Any]:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    return sync_playwright, PlaywrightTimeoutError


def _host(url: str) -> str:
    return urlparse(str(url or "").strip()).netloc.strip().lower()


def _matches_allowed_domain(host: str, allowed_domains: list[str]) -> bool:
    lowered_host = str(host or "").strip().lower()
    for domain in list(allowed_domains or []):
        domain_text = str(domain or "").strip().lower()
        if lowered_host == domain_text or lowered_host.endswith(f".{domain_text}"):
            return True
    return False


def _looks_like_login_gate(final_url: str, visible_text: str) -> bool:
    lowered_url = str(final_url or "").strip().lower()
    lowered_text = str(visible_text or "").strip().lower()
    return any(token in lowered_url for token in _LOGIN_URL_TOKENS) or any(
        token in lowered_text for token in _LOGIN_TEXT_TOKENS
    )


def default_provider_selector_plan(provider_key: str) -> list[str]:
    provider = str(provider_key or "").strip().lower()
    plans = {
        "scopus": ["main", "section", "article", "[role='main']", "body"],
        "elsevier": ["article", "main", ".Article", "#body", "body"],
        "ieee": ["main", "article", ".document-main", ".stats-document-abstract-publishedIn", "body"],
        "springer": ["main", "article", ".c-article-body", "#main-content", "body"],
        "ashrae": ["main", "article", ".content", "body"],
        "doe": ["main", "article", ".layout-content", "body"],
        "epa": ["main", "article", ".main-content", "body"],
    }
    return list(plans.get(provider, ["main", "article", "body"]))


def fetch_licensed_document_with_persistent_session(
    *,
    url: str,
    provider_session_plan: dict[str, Any],
    selector_plan: list[str] | None = None,
    timeout_ms: int = 12_000,
    headless: bool = True,
) -> dict[str, Any]:
    selector_plan = list(selector_plan or default_provider_selector_plan(provider_session_plan.get("provider_key", "")))
    profile_plan = dict(provider_session_plan.get("profile_plan", {}) or {})
    profile_path = Path(str(profile_plan.get("profile_path", "")).strip()).expanduser()
    allowed_domains = list(
        provider_session_plan.get("session_domain_allowlist", [])
        or []
    ) or list(
        provider_session_plan.get("target_domain_allowlist", [])
        or profile_plan.get("domain_allowlist", [])
        or []
    )

    try:
        sync_playwright, PlaywrightTimeoutError = _load_playwright_sync_api()
    except Exception:
        return {
            "status": "unavailable",
            "error": "playwright_not_installed",
            "requested_url": url,
            "final_url": url,
            "html": "",
            "visible_text": "",
            "selector_lineage": [],
            "acquisition_mode": "playwright_persistent_session",
            "provider_key": str(provider_session_plan.get("provider_key", "")).strip(),
            "profile_path": str(profile_path),
        }

    try:
        profile_path.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_path),
                headless=headless,
            )
            try:
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                try:
                    page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 6_000))
                except Exception:
                    pass
                final_url = str(page.url or url)
                html = page.content()
                selector_lineage: list[dict[str, Any]] = []
                visible_text = ""
                for selector in selector_plan:
                    locator = page.locator(selector).first
                    try:
                        count = locator.count()
                    except Exception:
                        count = 0
                    text_value = ""
                    if count:
                        try:
                            text_value = locator.inner_text(timeout=max(timeout_ms // 2, 1_000)).strip()
                        except Exception:
                            text_value = ""
                    selector_lineage.append(
                        {
                            "selector": selector,
                            "match_count": count,
                            "visible_text_length": len(text_value),
                        }
                    )
                    if text_value and not visible_text:
                        visible_text = text_value
                if not visible_text:
                    try:
                        visible_text = page.locator("body").inner_text(timeout=max(timeout_ms // 2, 1_000)).strip()
                    except Exception:
                        visible_text = ""
            finally:
                context.close()

        final_host = _host(final_url)
        if allowed_domains and not _matches_allowed_domain(final_host, allowed_domains):
            status = "blocked_domain_redirect"
            error = f"redirected_outside_allowed_domains:{final_host}"
        elif _looks_like_login_gate(final_url, visible_text):
            status = "login_required"
            error = "provider_session_not_authenticated"
        else:
            status = "success"
            error = ""
        return {
            "status": status,
            "error": error,
            "requested_url": url,
            "final_url": final_url,
            "html": html,
            "visible_text": visible_text,
            "selector_lineage": selector_lineage,
            "acquisition_mode": "playwright_persistent_session",
            "provider_key": str(provider_session_plan.get("provider_key", "")).strip(),
            "profile_path": str(profile_path),
            "allowed_domains": allowed_domains,
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
            "acquisition_mode": "playwright_persistent_session",
            "provider_key": str(provider_session_plan.get("provider_key", "")).strip(),
            "profile_path": str(profile_path),
            "allowed_domains": allowed_domains,
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
            "acquisition_mode": "playwright_persistent_session",
            "provider_key": str(provider_session_plan.get("provider_key", "")).strip(),
            "profile_path": str(profile_path),
            "allowed_domains": allowed_domains,
        }
