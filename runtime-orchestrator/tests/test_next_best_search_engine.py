from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.discovery_planner import (
    build_discovery_need_register,
    build_discovery_stop_condition_register,
)
from runtime_orchestrator.congruence_intelligence.dynamic_case_state import (
    build_discovery_case_state,
)
from runtime_orchestrator.congruence_intelligence.next_best_search import (
    build_next_best_search_register,
    build_search_failure_effect_register,
    build_search_success_effect_register,
    build_search_target_priority_register,
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


def _warehouse_target(*, jurisdiction_scope: list[str]) -> dict:
    return {
        "target_id": "warehouse-sunrise-logistics-hub",
        "target_identifier": "sunrise-logistics-hub-2026",
        "target_name": "Sunrise Logistics Hub",
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": list(jurisdiction_scope),
        "decision_intent": "asset_screening",
        "report_intent": "asset_preverification_screening",
        "owner_entity": "Sunrise Logistics REIT",
        "operator_entity": "Sunrise Operations LLC",
    }


def _manufacturing_target(*, jurisdiction_scope: list[str]) -> dict:
    return {
        "target_id": "manufacturing-lone-star-processing",
        "target_identifier": "lone-star-processing-2026",
        "target_name": "Lone Star Processing Plant",
        "target_type": "manufacturing_facility",
        "jurisdiction_scope": list(jurisdiction_scope),
        "decision_intent": "asset_screening",
        "report_intent": "asset_preverification_screening",
        "owner_entity": "Lone Star Processing",
        "operator_entity": "Lone Star Operations",
    }


def test_next_best_search_prioritizes_critical_warehouse_gap_and_explains_consequences():
    discovery_needs = build_discovery_need_register(
        target_definition={
            "target_type": "warehouse_distribution",
            "jurisdiction_scope": ["US-TX"],
        },
        coverage_gaps=[
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
            {"gap_type": "asset_primary_anchor_missing", "severity": "critical"},
        ],
        requestable_evidence_items=[
            {
                "evidence_item": "Dock count and service-level profile",
                "source": "Operator or leasing brochure",
                "why_needed": "Needed before EUI comparison.",
                "related_clusters": ["operating_regime_cluster"],
            }
        ],
        attempts=[],
        search_budget_register=[
            {
                "budget_scope": "total_public_discovery",
                "budget_state": "bounded",
                "budget_class": "bounded_public_discovery",
            }
        ],
    )
    stop_register = build_discovery_stop_condition_register(
        discovery_need_register=discovery_needs,
    )

    next_search = build_next_best_search_register(
        discovery_need_register=discovery_needs,
        discovery_stop_condition_register=stop_register,
        search_budget_register=[
            {
                "budget_scope": "total_public_discovery",
                "budget_state": "bounded",
                "budget_class": "bounded_public_discovery",
            }
        ],
    )
    priority = build_search_target_priority_register(
        next_best_search_register=next_search,
    )
    success = build_search_success_effect_register(
        next_best_search_register=next_search,
    )
    failure = build_search_failure_effect_register(
        next_best_search_register=next_search,
    )

    assert next_search
    top = next_search[0]
    assert top["target_rank"] == 1
    assert top["why"]
    assert top["search_family"]
    assert top["family_rank_register"]
    assert top["selected_search_family_reason"]
    assert top["selected_search_family_score"] >= 0
    assert top["family_score_components"]
    assert top["expected_evidence"]
    assert top["if_found"]
    assert top["if_not_found"]
    assert top["stop_condition"]
    assert priority[0]["priority_score"] >= priority[-1]["priority_score"]
    assert any(row["if_found"] for row in success)
    assert any(row["if_not_found"] for row in failure)


def test_next_best_search_demotes_repeatedly_failing_listing_family_for_warehouse_subtype() -> None:
    target_definition = _warehouse_target(jurisdiction_scope=["US-TX-DALLAS"])
    dynamic_case_state = build_discovery_case_state(
        target_definition=target_definition,
        routing_output=_routing_output(
            technical_scraping_allowed=True,
            regulatory_stack=["ERCOT", "TCEQ"],
            report_type_allowed="Minimum Evidence Report",
        ),
        coverage_gaps=[
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        ],
        requestable_evidence_items=[
            {
                "evidence_item": "Warehouse subtype and operating regime",
                "why_needed": "Needed before fair warehouse comparison.",
                "source": "Public asset and operator records",
            }
        ],
        attempts=[
            {"source_family": "property_listing_record", "status": "failed"},
            {"source_family": "property_listing_record", "status": "no_data"},
        ],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        case_fingerprint="case-warehouse-rerank",
        asset_context_readiness={"state": "asset_localized"},
        runtime_context={
            "source_yield_memory_summary": {
                "by_source_family": {
                    "county_assessor": {"yield_score": 3, "yield_band": "medium"}
                }
            }
        },
        routing_plan_compliance={
            "mandatory_sources_missing_from_executor": ["county_assessor_asset_anchor"]
        },
    )
    discovery_needs = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=[{"gap_type": "asset_energy_behavior_reference", "severity": "high"}],
        requestable_evidence_items=[
            {
                "evidence_item": "Warehouse subtype and operating regime",
                "why_needed": "Needed before fair warehouse comparison.",
                "source": "Public asset and operator records",
            }
        ],
        attempts=[
            {"source_family": "property_listing_record", "status": "failed"},
            {"source_family": "property_listing_record", "status": "no_data"},
        ],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        dynamic_case_state=dynamic_case_state,
    )
    stop_register = build_discovery_stop_condition_register(discovery_need_register=discovery_needs)
    next_search = build_next_best_search_register(
        discovery_need_register=discovery_needs,
        discovery_stop_condition_register=stop_register,
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        dynamic_case_state=dynamic_case_state,
    )

    subtype_row = next(
        row for row in next_search if row["need_id"] == "warehouse_subtype_classification"
    )
    family_ranks = {
        row["search_family"]: row
        for row in subtype_row["family_rank_register"]
    }

    assert subtype_row["search_family"] != "property_listing"
    assert family_ranks["county_assessor"]["family_rank"] < family_ranks["property_listing"]["family_rank"]
    assert family_ranks["property_listing"]["score_components"]["failure_penalty"] < 0


def test_next_best_search_elevates_utility_service_territory_for_tariff_sensitive_manufacturing_case() -> None:
    target_definition = _manufacturing_target(jurisdiction_scope=["US-TX-DALLAS"])
    dynamic_case_state = build_discovery_case_state(
        target_definition=target_definition,
        routing_output=_routing_output(
            technical_scraping_allowed=True,
            regulatory_stack=["ERCOT", "TCEQ"],
            report_type_allowed="Minimum Evidence Report",
        ),
        coverage_gaps=[
            {"gap_type": "asset_energy_behavior_reference", "severity": "critical"},
        ],
        requestable_evidence_items=[
            {
                "evidence_item": "Utility tariff, thermal systems, and steam or boiler context",
                "why_needed": "Needed to distinguish tariff exposure from process thermal load.",
                "source": "Public utility and permit records",
            }
        ],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        case_fingerprint="case-manufacturing-tariff",
        routing_plan_compliance={
            "mandatory_sources_missing_from_executor": ["utility_oncor_service_territory"]
        },
    )
    discovery_needs = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=[{"gap_type": "asset_energy_behavior_reference", "severity": "critical"}],
        requestable_evidence_items=[
            {
                "evidence_item": "Utility tariff, thermal systems, and steam or boiler context",
                "why_needed": "Needed to distinguish tariff exposure from process thermal load.",
                "source": "Public utility and permit records",
            }
        ],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        dynamic_case_state=dynamic_case_state,
    )
    stop_register = build_discovery_stop_condition_register(discovery_need_register=discovery_needs)
    next_search = build_next_best_search_register(
        discovery_need_register=discovery_needs,
        discovery_stop_condition_register=stop_register,
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        dynamic_case_state=dynamic_case_state,
    )

    thermal_row = next(
        row for row in next_search if row["need_id"] == "thermal_system_and_utility_mix"
    )

    assert thermal_row["search_family"] == "utility_service_territory"
    assert thermal_row["family_score_components"]["jurisdiction_fit"] > 0
    assert thermal_row["family_score_components"]["regulatory_value"] > 0
    assert "tariff or regulatory triggers" in thermal_row["selected_search_family_reason"]


def test_next_best_search_demotes_high_difficulty_visual_route_when_budget_is_exhausted() -> None:
    target_definition = _warehouse_target(jurisdiction_scope=["US-TX-DALLAS"])

    def _state_for_budget(budget_state: str) -> dict:
        return build_discovery_case_state(
            target_definition=target_definition,
            routing_output=_routing_output(
                technical_scraping_allowed=True,
                regulatory_stack=["ERCOT"],
                report_type_allowed="Minimum Evidence Report",
            ),
            coverage_gaps=[
                {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
            ],
            requestable_evidence_items=[
                {
                    "evidence_item": "Dock count and service-level profile",
                    "why_needed": "Needed before EUI comparison.",
                    "source": "Leasing brochure, site plan, or operator page",
                }
            ],
            attempts=[],
            search_budget_register=[
                {"budget_scope": "total_public_discovery", "budget_state": budget_state}
            ],
            case_fingerprint=f"case-budget-{budget_state}",
            runtime_context={
                "source_yield_memory_summary": {
                    "by_source_family": {
                        "site_plan_or_photo_clues": {"yield_score": 4, "yield_band": "high"}
                    }
                }
            },
        )

    bounded_state = _state_for_budget("bounded")
    exhausted_state = _state_for_budget("exhausted")
    discovery_needs_bounded = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=[{"gap_type": "asset_energy_behavior_reference", "severity": "high"}],
        requestable_evidence_items=[
            {
                "evidence_item": "Dock count and service-level profile",
                "why_needed": "Needed before EUI comparison.",
                "source": "Leasing brochure, site plan, or operator page",
            }
        ],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        dynamic_case_state=bounded_state,
    )
    discovery_needs_exhausted = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=[{"gap_type": "asset_energy_behavior_reference", "severity": "high"}],
        requestable_evidence_items=[
            {
                "evidence_item": "Dock count and service-level profile",
                "why_needed": "Needed before EUI comparison.",
                "source": "Leasing brochure, site plan, or operator page",
            }
        ],
        attempts=[],
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "exhausted"}
        ],
        dynamic_case_state=exhausted_state,
    )
    stop_bounded = build_discovery_stop_condition_register(discovery_need_register=discovery_needs_bounded)
    stop_exhausted = build_discovery_stop_condition_register(discovery_need_register=discovery_needs_exhausted)
    bounded_next_search = build_next_best_search_register(
        discovery_need_register=discovery_needs_bounded,
        discovery_stop_condition_register=stop_bounded,
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "bounded"}
        ],
        dynamic_case_state=bounded_state,
    )
    exhausted_next_search = build_next_best_search_register(
        discovery_need_register=discovery_needs_exhausted,
        discovery_stop_condition_register=stop_exhausted,
        search_budget_register=[
            {"budget_scope": "total_public_discovery", "budget_state": "exhausted"}
        ],
        dynamic_case_state=exhausted_state,
    )

    bounded_row = next(
        row for row in bounded_next_search if row["need_id"] == "dock_and_service_intensity"
    )
    exhausted_row = next(
        row for row in exhausted_next_search if row["need_id"] == "dock_and_service_intensity"
    )
    exhausted_family_ranks = {
        row["search_family"]: row
        for row in exhausted_row["family_rank_register"]
    }

    assert bounded_row["search_family"] == "site_plan_or_photo_clues"
    assert exhausted_row["search_family"] != "site_plan_or_photo_clues"
    assert exhausted_family_ranks["site_plan_or_photo_clues"]["score_components"]["budget_fit"] < 0
