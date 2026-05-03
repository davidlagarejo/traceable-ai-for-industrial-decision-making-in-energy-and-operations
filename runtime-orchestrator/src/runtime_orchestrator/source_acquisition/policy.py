from __future__ import annotations

import os
from typing import Any, Mapping

_BROWSER_FLAG = "ZLAB_ENABLE_BROWSER_ACQUISITION"
_WHITELISTED_SOURCE_FAMILIES = {"official_portal_context"}
_NON_PUBLIC_URL_TOKENS = ("login", "signin", "captcha", "oauth", "auth")


def browser_acquisition_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = env if env is not None else os.environ
    return str(values.get(_BROWSER_FLAG, "")).strip().lower() in {"1", "true", "yes", "on"}


def is_public_page_url(url: str) -> bool:
    lowered = str(url or "").strip().lower()
    if not lowered.startswith(("http://", "https://")):
        return False
    return not any(token in lowered for token in _NON_PUBLIC_URL_TOKENS)


def evaluate_public_page_policy(
    *,
    technical_scraping_allowed: bool,
    route_allowed: bool,
    source_family: str,
    public_url: str,
    source_type: str | None = None,
    browser_eligible: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    capability_enabled = browser_acquisition_enabled(env)
    whitelisted_source_family = source_family in _WHITELISTED_SOURCE_FAMILIES
    explicitly_eligible_source_type = bool(browser_eligible)
    page_is_public = is_public_page_url(public_url)

    if not technical_scraping_allowed:
        reason = "technical_scraping_not_allowed"
        allowed = False
    elif not route_allowed:
        reason = "source_not_allowed_by_routing"
        allowed = False
    elif not whitelisted_source_family and not explicitly_eligible_source_type:
        reason = "source_family_not_whitelisted"
        allowed = False
    elif not page_is_public:
        reason = "page_not_public_or_login_gated"
        allowed = False
    elif not capability_enabled:
        reason = "browser_capability_disabled"
        allowed = False
    else:
        reason = "allowed"
        allowed = True

    return {
        "allowed": allowed,
        "policy_reason": reason,
        "browser_capability_enabled": capability_enabled,
        "page_is_public": page_is_public,
        "whitelisted_source_family": whitelisted_source_family,
        "explicitly_eligible_source_type": explicitly_eligible_source_type,
        "source_type": str(source_type or "").strip(),
        "technical_scraping_allowed": technical_scraping_allowed,
        "route_allowed": route_allowed,
    }
