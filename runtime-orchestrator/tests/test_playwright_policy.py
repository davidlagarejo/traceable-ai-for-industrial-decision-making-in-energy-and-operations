from __future__ import annotations

from runtime_orchestrator.source_acquisition.policy import (
    browser_acquisition_enabled,
    evaluate_public_page_policy,
)


def test_browser_acquisition_disabled_by_default() -> None:
    assert browser_acquisition_enabled(env={}) is False


def test_public_page_policy_blocks_when_technical_scraping_is_not_allowed() -> None:
    decision = evaluate_public_page_policy(
        technical_scraping_allowed=False,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["allowed"] is False
    assert decision["policy_reason"] == "technical_scraping_not_allowed"


def test_public_page_policy_allows_whitelisted_public_portal_when_flag_enabled() -> None:
    decision = evaluate_public_page_policy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "true"},
    )

    assert decision["allowed"] is True
    assert decision["policy_reason"] == "allowed"
    assert decision["page_is_public"] is True
    assert decision["whitelisted_source_family"] is True


def test_public_page_policy_blocks_login_like_urls() -> None:
    decision = evaluate_public_page_policy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://portal.example.com/login",
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["allowed"] is False
    assert decision["policy_reason"] == "page_not_public_or_login_gated"


def test_public_page_policy_allows_explicitly_eligible_source_type_outside_family_whitelist() -> None:
    decision = evaluate_public_page_policy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="energy_environment_record",
        source_type="utility_pge_service_territory",
        browser_eligible=True,
        public_url="https://www.pge.com/",
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["allowed"] is True
    assert decision["policy_reason"] == "allowed"
    assert decision["whitelisted_source_family"] is False
    assert decision["explicitly_eligible_source_type"] is True
