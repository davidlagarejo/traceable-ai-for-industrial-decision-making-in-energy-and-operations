from __future__ import annotations

from typing import Any, Mapping

from .policy import evaluate_public_page_policy


def select_public_page_acquisition_strategy(
    *,
    technical_scraping_allowed: bool,
    route_allowed: bool,
    source_family: str,
    public_url: str,
    source_type: str | None = None,
    browser_eligible: bool = False,
    public_page_kind: str = "",
    max_browser_navigations: int = 1,
    static_probe: dict[str, Any] | None,
    previous_acquisition_memory: dict[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    policy = evaluate_public_page_policy(
        technical_scraping_allowed=technical_scraping_allowed,
        route_allowed=route_allowed,
        source_family=source_family,
        public_url=public_url,
        source_type=source_type,
        browser_eligible=browser_eligible,
        env=env,
    )
    static_probe = dict(static_probe) if isinstance(static_probe, dict) else {}
    previous_acquisition_memory = (
        dict(previous_acquisition_memory)
        if isinstance(previous_acquisition_memory, dict)
        else {}
    )
    render_mode = str(static_probe.get("render_mode", "")).strip() or "unknown"
    recommended_mode = str(
        previous_acquisition_memory.get("recommended_acquisition_mode", "")
    ).strip()

    if not policy["allowed"]:
        return {
            "selected_mode": "static_only",
            "selection_reason": policy["policy_reason"],
            "browser_allowed": False,
            "browser_eligible": browser_eligible,
            "public_page_kind": str(public_page_kind or "").strip(),
            "max_browser_navigations": int(max_browser_navigations or 1),
            "policy": policy,
            "render_mode": render_mode,
        }
    if render_mode == "static_usable":
        return {
            "selected_mode": "static_only",
            "selection_reason": "static_probe_sufficient",
            "browser_allowed": True,
            "browser_eligible": browser_eligible,
            "public_page_kind": str(public_page_kind or "").strip(),
            "max_browser_navigations": int(max_browser_navigations or 1),
            "policy": policy,
            "render_mode": render_mode,
        }
    if recommended_mode == "avoid_browser":
        return {
            "selected_mode": "static_only",
            "selection_reason": "browser_history_low_yield",
            "browser_allowed": True,
            "browser_eligible": browser_eligible,
            "public_page_kind": str(public_page_kind or "").strip(),
            "max_browser_navigations": int(max_browser_navigations or 1),
            "policy": policy,
            "render_mode": render_mode,
        }
    if recommended_mode == "prefer_browser":
        return {
            "selected_mode": "playwright_public_page",
            "selection_reason": "browser_history_preferred",
            "browser_allowed": True,
            "browser_eligible": browser_eligible,
            "public_page_kind": str(public_page_kind or "").strip(),
            "max_browser_navigations": int(max_browser_navigations or 1),
            "policy": policy,
            "render_mode": render_mode,
        }
    if render_mode in {"shell_or_sparse", "empty", "unknown"}:
        return {
            "selected_mode": "playwright_public_page",
            "selection_reason": "static_probe_insufficient",
            "browser_allowed": True,
            "browser_eligible": browser_eligible,
            "public_page_kind": str(public_page_kind or "").strip(),
            "max_browser_navigations": int(max_browser_navigations or 1),
            "policy": policy,
            "render_mode": render_mode,
        }
    return {
        "selected_mode": "static_only",
        "selection_reason": "non_browser_fallback",
        "browser_allowed": True,
        "browser_eligible": browser_eligible,
        "public_page_kind": str(public_page_kind or "").strip(),
        "max_browser_navigations": int(max_browser_navigations or 1),
        "policy": policy,
        "render_mode": render_mode,
    }
