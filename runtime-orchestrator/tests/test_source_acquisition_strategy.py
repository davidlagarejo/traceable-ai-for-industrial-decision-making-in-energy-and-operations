from __future__ import annotations

from runtime_orchestrator.source_acquisition.strategy_selector import (
    select_public_page_acquisition_strategy,
)


def test_strategy_prefers_static_when_probe_is_usable() -> None:
    decision = select_public_page_acquisition_strategy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        static_probe={"render_mode": "static_usable"},
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["selected_mode"] == "static_only"
    assert decision["selection_reason"] == "static_probe_sufficient"
    assert decision["browser_allowed"] is True


def test_strategy_escalates_to_playwright_when_probe_is_shell_and_policy_allows() -> None:
    decision = select_public_page_acquisition_strategy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        static_probe={"render_mode": "shell_or_sparse"},
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["selected_mode"] == "playwright_public_page"
    assert decision["selection_reason"] == "static_probe_insufficient"
    assert decision["browser_allowed"] is True


def test_strategy_stays_static_when_browser_capability_is_disabled() -> None:
    decision = select_public_page_acquisition_strategy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        static_probe={"render_mode": "shell_or_sparse"},
        env={},
    )

    assert decision["selected_mode"] == "static_only"
    assert decision["selection_reason"] == "browser_capability_disabled"
    assert decision["browser_allowed"] is False


def test_strategy_prefers_browser_when_previous_acquisition_memory_recommends_it() -> None:
    decision = select_public_page_acquisition_strategy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        static_probe={"render_mode": "unknown"},
        previous_acquisition_memory={"recommended_acquisition_mode": "prefer_browser"},
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["selected_mode"] == "playwright_public_page"
    assert decision["selection_reason"] == "browser_history_preferred"


def test_strategy_avoids_browser_when_previous_acquisition_memory_marks_it_low_yield() -> None:
    decision = select_public_page_acquisition_strategy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="official_portal_context",
        public_url="https://www.dallascad.org/SearchOwner.aspx",
        static_probe={"render_mode": "unknown"},
        previous_acquisition_memory={"recommended_acquisition_mode": "avoid_browser"},
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["selected_mode"] == "static_only"
    assert decision["selection_reason"] == "browser_history_low_yield"


def test_strategy_allows_explicit_source_type_expansion_without_family_whitelist() -> None:
    decision = select_public_page_acquisition_strategy(
        technical_scraping_allowed=True,
        route_allowed=True,
        source_family="energy_environment_record",
        source_type="utility_pge_service_territory",
        browser_eligible=True,
        public_page_kind="utility_territory_page",
        max_browser_navigations=1,
        public_url="https://www.pge.com/",
        static_probe={"render_mode": "shell_or_sparse"},
        env={"ZLAB_ENABLE_BROWSER_ACQUISITION": "1"},
    )

    assert decision["selected_mode"] == "playwright_public_page"
    assert decision["selection_reason"] == "static_probe_insufficient"
    assert decision["browser_eligible"] is True
    assert decision["public_page_kind"] == "utility_territory_page"
    assert decision["max_browser_navigations"] == 1
