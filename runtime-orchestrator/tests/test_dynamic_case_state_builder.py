from __future__ import annotations

import runtime_orchestrator.adapters.motor_028 as motor_028_module
from runtime_orchestrator.adapters.motor_028 import Motor028Adapter
from runtime_orchestrator.congruence_intelligence.dynamic_case_state import (
    build_discovery_case_state,
)


def _routing_output(*, technical_scraping_allowed: bool, regulatory_stack: list[str], report_type_allowed: str) -> dict:
    return {
        "routing_ready": technical_scraping_allowed,
        "report_type_allowed": report_type_allowed,
        "regulatory_stack": list(regulatory_stack),
        "target_classification_result": {
            "technical_scraping_allowed": technical_scraping_allowed,
        },
    }


def _target_definition(*, jurisdiction_scope: list[str]) -> dict:
    return {
        "target_id": "warehouse-distribution-sunrise-logistics-hub",
        "target_identifier": "sunrise-logistics-hub-2026",
        "target_name": "Sunrise Logistics Hub",
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": list(jurisdiction_scope),
        "decision_intent": "asset_screening",
        "report_intent": "asset_preverification_screening",
        "owner_entity": "Sunrise Logistics REIT",
        "operator_entity": "Sunrise Operations LLC",
    }


def test_discovery_case_state_builder_captures_budget_memory_and_family_outcomes() -> None:
    state = build_discovery_case_state(
        target_definition=_target_definition(jurisdiction_scope=["US-TX-DALLAS"]),
        routing_output=_routing_output(
            technical_scraping_allowed=True,
            regulatory_stack=["ERCOT", "TCEQ"],
            report_type_allowed="Minimum Evidence Report",
        ),
        coverage_gaps=[
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
            {"gap_type": "asset_context_readiness", "severity": "medium"},
        ],
        requestable_evidence_items=[
            {
                "evidence_item": "Dock count, charging windows, tariff sheets, and lease boundary",
                "why_needed": "Needed to separate tariff exposure from generic energy intensity.",
                "source": "Owner, operator, and utility records",
            }
        ],
        attempts=[
            {"source_family": "geospatial_public_record", "status": "found"},
            {"source_family": "utility_service_record", "status": "failed"},
            {"source_family": "property_listing_record", "status": "no_data"},
        ],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        case_fingerprint="case-1234abcd",
        asset_context_readiness={"state": "asset_localized"},
        runtime_context={
            "case_delta_summary": {"progress_signals": ["accepted_source_coverage_up"]},
            "source_yield_memory_summary": {
                "by_source_family": {
                    "county_assessor": {"yield_score": 2, "yield_band": "productive"}
                },
                "source_acquisition_yield_memory": {
                    "by_source_family": {
                        "dallas_building_permit_portal": {
                            "recommended_acquisition_mode": "prefer_browser"
                        }
                    },
                    "browser_justified_source_families": ["dallas_building_permit_portal"],
                    "browser_waste_source_families": ["harris_cad_property_search_portal"],
                },
                "browser_success_failure_summary": {"success_count": 1, "failure_count": 0},
                "static_success_failure_summary": {"success_count": 0, "failure_count": 1},
            },
        },
        routing_plan_compliance={
            "mandatory_sources_missing_from_executor": ["utility_oncor_service_territory"]
        },
    )

    assert state["asset_family"] == "logistics_warehouse"
    assert state["budget_state"] == "bounded"
    assert state["technical_scraping_allowed"] is True
    assert state["route_report_type_allowed"] == "Minimum Evidence Report"
    assert state["source_family_successes"] == ["geospatial_public_record"]
    assert set(state["source_family_failures"]) == {"utility_service_record", "property_listing_record"}
    assert state["mandatory_source_gaps"] == ["utility_oncor_service_territory"]
    assert state["source_family_yield_memory"]["county_assessor"]["yield_band"] == "productive"
    assert state["source_acquisition_yield_memory"]["by_source_family"]["dallas_building_permit_portal"]["recommended_acquisition_mode"] == "prefer_browser"
    assert state["browser_justified_source_families"] == ["dallas_building_permit_portal"]
    assert state["browser_waste_source_families"] == ["harris_cad_property_search_portal"]
    assert state["browser_success_failure_summary"]["success_count"] == 1
    assert "warehouse_tariff_orchestration" in state["active_rival_hypotheses"]
    assert "warehouse_control_boundary_value_leakage" in state["active_rival_hypotheses"]
    assert "utility_territory_and_tariff_context" in state["active_comparison_blockers"]
    assert "operator_boundary_and_control" in state["active_comparison_blockers"]
    assert "demand_charge_exposure_hidden" in state["active_financial_exposure_candidates"]
    assert "tariff_vs_efficiency" in state["active_contradiction_targets"]
    assert any(row["source_family"] == "utility_service_record" for row in state["source_family_failure_pressure"])
    assert state["previous_run_progress_signals"] == ["accepted_source_coverage_up"]


def test_discovery_case_state_builder_differs_for_tx_and_nyc_routes() -> None:
    tx_state = build_discovery_case_state(
        target_definition=_target_definition(jurisdiction_scope=["US-TX-DALLAS"]),
        routing_output=_routing_output(
            technical_scraping_allowed=True,
            regulatory_stack=["ERCOT", "TCEQ"],
            report_type_allowed="Minimum Evidence Report",
        ),
        coverage_gaps=[],
        requestable_evidence_items=[],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        case_fingerprint="case-tx",
    )
    nyc_state = build_discovery_case_state(
        target_definition=_target_definition(jurisdiction_scope=["US-NY-NYC"]),
        routing_output=_routing_output(
            technical_scraping_allowed=True,
            regulatory_stack=["LL84", "LL97"],
            report_type_allowed="Minimum Evidence Report",
        ),
        coverage_gaps=[],
        requestable_evidence_items=[],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        case_fingerprint="case-nyc",
    )

    assert tx_state["jurisdiction_scope"] == ["US-TX-DALLAS"]
    assert nyc_state["jurisdiction_scope"] == ["US-NY-NYC"]
    assert tx_state["active_regulatory_triggers"] != nyc_state["active_regulatory_triggers"]


def test_discovery_case_state_builder_respects_technical_scraping_gate() -> None:
    state = build_discovery_case_state(
        target_definition=_target_definition(jurisdiction_scope=["US-CA-SF"]),
        routing_output=_routing_output(
            technical_scraping_allowed=False,
            regulatory_stack=["classification_only"],
            report_type_allowed="Target Classification Brief",
        ),
        coverage_gaps=[{"gap_type": "asset_primary_anchor_missing", "severity": "high"}],
        requestable_evidence_items=[],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        case_fingerprint="case-blocked",
        asset_context_readiness={"state": "address_only"},
    )

    assert state["technical_scraping_allowed"] is False
    assert state["identity_state"] == "routing_blocked"
    assert state["route_report_type_allowed"] == "Target Classification Brief"


def test_motor_028_emits_discovery_case_state_additively(monkeypatch) -> None:
    class _DummyCrawler:
        def get_cached_or_live(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(
        motor_028_module,
        "_fetch_census_geocoder",
        lambda _ctx: {
            "coordinates": {"x": -96.8, "y": 32.8},
            "addressComponents": {"city": "Dallas", "zip": "75201"},
            "geographies": {"Counties": [{"GEOID": "48113", "STATE": "48"}]},
        },
    )
    monkeypatch.setattr(motor_028_module, "_fetch_ashrae_climate_zone", lambda _ctx: None)
    monkeypatch.setattr(motor_028_module, "_get_crawler", lambda _ctx: _DummyCrawler())
    monkeypatch.setattr(motor_028_module, "_select_extended_registry", lambda *_args, **_kwargs: [])

    out = Motor028Adapter().run(
        {
            "motor_001": {
                "ingestion_contract_status": "active",
                "target_type_classification_seed": {},
            },
            "motor_003": {"term_index": {}},
            "motor_008": {"source_registry": {}},
            "motor_035": {
                "routing_ready": True,
                "report_type_allowed": "Minimum Evidence Report",
                "regulatory_stack": ["ERCOT"],
                "source_routing_plan": {},
                "target_classification_result": {"technical_scraping_allowed": True},
            },
            "__runtime__": {
                "case_delta_summary": {"progress_signals": ["accepted_source_coverage_up"]},
                "source_yield_memory_summary": {"by_source_family": {"county_assessor": {"yield_score": 1}}},
            },
            "__pipeline__": {
                "target_definition_contract": {
                    "target_name": "Sunrise Logistics Hub",
                    "target_identifier": "sunrise-logistics-hub-2026",
                    "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                    "jurisdiction_scope": ["US-TX-DALLAS"],
                    "target_type": "warehouse_distribution",
                    "target_scope": "asset",
                },
                "facility_inputs": {
                    "input_01_location": {
                        "address": "1450 Logistics Parkway, Dallas, TX 75201",
                        "city": "Dallas",
                        "state": "TX",
                        "country": "US",
                        "jurisdiction_codes": ["US-TX-DALLAS"],
                    },
                    "input_03_sector": {},
                },
                "subject": {},
            },
        }
    )

    state = out["discovery_case_state"]
    assert state["asset_family"] == "logistics_warehouse"
    assert state["technical_scraping_allowed"] is True
    assert state["previous_run_progress_signals"] == ["accepted_source_coverage_up"]
    assert "active_rival_hypotheses" in state
    assert "active_comparison_blockers" in state
    assert "active_financial_exposure_candidates" in state
    assert out["enriched_data"]["discovery_case_state"] == state
