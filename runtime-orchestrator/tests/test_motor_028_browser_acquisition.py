from __future__ import annotations

import runtime_orchestrator.adapters.motor_028 as motor_028_module
import runtime_orchestrator.source_acquisition as source_acquisition_module


class _DummyResponse:
    def __init__(self, text: str, url: str) -> None:
        self.text = text
        self.url = url
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None


def test_motor_028_enriches_official_portal_context_with_static_provenance(monkeypatch) -> None:
    monkeypatch.delenv("ZLAB_ENABLE_BROWSER_ACQUISITION", raising=False)
    monkeypatch.setattr(
        motor_028_module.requests,
        "get",
        lambda *args, **kwargs: _DummyResponse(
            "<html><body><main>Dallas CAD Property Search</main></body></html>",
            "https://www.dallascad.org/SearchOwner.aspx",
        ),
    )

    enriched = motor_028_module._maybe_enrich_official_portal_payload(
        data={
            "source_dataset": "dallas_cad_property_search_portal",
            "title": "Dallas Central Appraisal District property-search portal context",
            "official_url": "https://www.dallascad.org/SearchOwner.aspx",
            "scope": "JURISDICTION_LEVEL",
            "notes": ["Portal context only."],
        },
        spec={"source_type": "dallas_cad_property_search_portal"},
        routing_output={
            "routing_ready": True,
            "target_classification_result": {"technical_scraping_allowed": True},
        },
    )

    acquisition = enriched["public_page_acquisition"]
    assert acquisition["source_family"] == "official_portal_context"
    assert acquisition["selected_mode"] == "static_only"
    assert acquisition["selection_reason"] == "browser_capability_disabled"
    assert acquisition["static_probe"]["render_mode"] == "static_usable"
    assert acquisition["static_provenance_manifest"]["attempt_outcome"] == "success"


def test_motor_028_escalates_experience_builder_shell_to_browser_mode(monkeypatch) -> None:
    shell_html = """
    <!doctype html>
    <html lang="en-us">
      <head><title>Experience</title></head>
      <body>
        <div id="loading">
          <div class="loading-content">
            <div class="jimu-primary-loading-app"></div>
          </div>
        </div>
        <div id="app"></div>
        <script type="systemjs-importmap">{}</script>
      </body>
    </html>
    """
    monkeypatch.setenv("ZLAB_ENABLE_BROWSER_ACQUISITION", "1")
    monkeypatch.setattr(
        motor_028_module.requests,
        "get",
        lambda *args, **kwargs: _DummyResponse(
            shell_html,
            "https://experience.arcgis.com/experience/8f2b67be060945d48e779eac2d2bc1df",
        ),
    )
    monkeypatch.setattr(
        source_acquisition_module,
        "fetch_public_page_with_playwright",
        lambda **kwargs: {
            "status": "success",
            "requested_url": kwargs["url"],
            "final_url": kwargs["url"],
            "html": "<html><body><div id='app'><main>Marin Map Viewer Search Layers About</main></div></body></html>",
            "visible_text": "Marin Map Viewer Search Layers About",
            "selector_lineage": [
                {"selector": "#app", "match_count": 1, "visible_text_length": 36},
            ],
            "acquisition_mode": "playwright_public_page",
        },
    )

    enriched = motor_028_module._maybe_enrich_official_portal_payload(
        data={
            "source_dataset": "marinmap_viewer_portal_context",
            "title": "MarinMap Viewer portal context",
            "official_url": "https://experience.arcgis.com/experience/8f2b67be060945d48e779eac2d2bc1df",
            "scope": "JURISDICTION_LEVEL",
            "notes": ["Portal context only."],
        },
        spec={"source_type": "marinmap_experience_builder_portal"},
        routing_output={
            "routing_ready": True,
            "target_classification_result": {"technical_scraping_allowed": True},
        },
    )

    acquisition = enriched["public_page_acquisition"]
    assert acquisition["source_family"] == "official_portal_context"
    assert acquisition["selected_mode"] == "playwright_public_page"
    assert acquisition["selection_reason"] == "static_probe_insufficient"
    assert acquisition["static_probe"]["render_mode"] == "shell_or_sparse"
    assert acquisition["browser_attempt"]["status"] == "success"
    assert acquisition["browser_provenance_manifest"]["attempt_outcome"] == "success"
    assert acquisition["browser_provenance_manifest"]["visible_text_length"] > 0


def test_motor_028_supports_explicit_browser_eligible_utility_context(monkeypatch) -> None:
    shell_html = """
    <html>
      <body>
        <div id="app"></div>
        <div>loading...</div>
        <script>window.__APP_SHELL__ = true;</script>
      </body>
    </html>
    """
    monkeypatch.setenv("ZLAB_ENABLE_BROWSER_ACQUISITION", "1")
    monkeypatch.setattr(
        motor_028_module.requests,
        "get",
        lambda *args, **kwargs: _DummyResponse(
            shell_html,
            "https://www.pge.com/",
        ),
    )
    monkeypatch.setattr(
        source_acquisition_module,
        "fetch_public_page_with_playwright",
        lambda **kwargs: {
            "status": "success",
            "requested_url": kwargs["url"],
            "final_url": kwargs["url"],
            "html": "<html><body><main>PG&E electric service territory and account support</main></body></html>",
            "visible_text": "PG&E electric service territory and account support",
            "selector_lineage": [
                {"selector": "main", "match_count": 1, "visible_text_length": 47},
            ],
            "acquisition_mode": "playwright_public_page",
        },
    )

    enriched = motor_028_module._maybe_enrich_official_portal_payload(
        data={
            "source_dataset": "utility_pge_service_territory",
            "title": "PG&E service territory context",
            "official_url": "https://www.pge.com/",
            "scope": "JURISDICTION_LEVEL",
            "notes": ["Territory context only."],
        },
        spec={"source_type": "utility_pge_service_territory", "key": "utility_pge_service_territory"},
        routing_output={
            "routing_ready": True,
            "target_classification_result": {"technical_scraping_allowed": True},
        },
    )

    acquisition = enriched["public_page_acquisition"]
    assert acquisition["source_family"] == "energy_environment_record"
    assert acquisition["browser_eligible"] is True
    assert acquisition["public_page_kind"] == "utility_territory_page"
    assert acquisition["selected_mode"] == "playwright_public_page"
    assert acquisition["selection_reason"] == "static_probe_insufficient"
    assert acquisition["browser_attempt"]["status"] == "success"
    assert acquisition["browser_provenance_manifest"]["visible_text_length"] > 0
