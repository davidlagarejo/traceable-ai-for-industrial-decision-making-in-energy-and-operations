from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.discovery_planner import (
    build_accepted_evidence_type_register,
    build_discovery_need_register,
    build_discovery_stop_condition_register,
    build_search_family_execution_plan,
)
from runtime_orchestrator.congruence_intelligence.dynamic_case_state import (
    build_discovery_case_state,
)


def test_warehouse_discovery_planner_activates_subtype_docks_and_refrigeration_routes():
    discovery_needs = build_discovery_need_register(
        target_definition={
            "target_type": "warehouse_distribution",
            "jurisdiction_scope": ["US-TX"],
        },
        coverage_gaps=[
            {"gap_type": "asset_primary_anchor_missing", "severity": "high"},
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        ],
        requestable_evidence_items=[
            {
                "evidence_item": "Verified building area, dock count, and refrigerated footprint if applicable",
                "source": "Owner records, site plan, or operator layout",
                "why_needed": "Sets the scale of logistics throughput, refrigeration exposure, and retrofit scope.",
                "related_clusters": ["geometry_size_cluster", "regulatory_cluster"],
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

    by_id = {row["need_id"]: row for row in discovery_needs}
    assert "warehouse_subtype_classification" in by_id
    assert "dock_and_service_intensity" in by_id
    assert "refrigeration_presence" in by_id
    assert "operator_boundary_and_control" in by_id
    assert "utility_territory_and_tariff_context" in by_id
    assert "leasing_brochure" in by_id["warehouse_subtype_classification"]["search_families_to_explore"]
    assert "county_assessor" in by_id["warehouse_subtype_classification"]["search_families_to_explore"]
    assert "satellite_photo_clues" in by_id["dock_and_service_intensity"]["search_families_to_explore"]
    assert "refrigeration_clues" in by_id["refrigeration_presence"]["search_families_to_explore"]

    execution_plan = build_search_family_execution_plan(
        discovery_need_register=discovery_needs,
    )
    accepted_evidence = build_accepted_evidence_type_register(
        discovery_need_register=discovery_needs,
    )
    stop_register = build_discovery_stop_condition_register(
        discovery_need_register=discovery_needs,
    )

    assert any(row["search_family"] == "leasing_brochure" for row in execution_plan)
    assert any(row["accepted_evidence_type"] == "dock_count_clue" for row in accepted_evidence)
    assert any(row["need_id"] == "refrigeration_presence" for row in stop_register)


def test_manufacturing_discovery_planner_activates_permit_thermal_and_throughput_routes():
    discovery_needs = build_discovery_need_register(
        target_definition={
            "target_type": "manufacturing_facility",
            "jurisdiction_scope": ["US-TX"],
        },
        coverage_gaps=[
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        ],
        requestable_evidence_items=[
            {
                "evidence_item": "Throughput by shift and process map",
                "source": "Operator and production records",
                "why_needed": "Required to normalize manufacturing intensity.",
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

    by_id = {row["need_id"]: row for row in discovery_needs}
    assert "process_and_permit_profile" in by_id
    assert "thermal_system_and_utility_mix" in by_id
    assert "throughput_proxy_and_schedule" in by_id
    assert "permit_record" in by_id["process_and_permit_profile"]["search_families_to_explore"]
    assert "environmental_registry" in by_id["thermal_system_and_utility_mix"]["search_families_to_explore"]
    assert "operator_page" in by_id["throughput_proxy_and_schedule"]["search_families_to_explore"]


def test_discovery_planner_uses_dynamic_case_state_for_activation_reasons_and_jurisdiction_hints():
    tx_target = {
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": ["US-TX-DALLAS"],
        "decision_intent": "asset_screening",
        "report_intent": "asset_preverification_screening",
    }
    nyc_target = {
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": ["US-NY-NYC"],
        "decision_intent": "asset_screening",
        "report_intent": "asset_preverification_screening",
    }
    coverage_gaps = [
        {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        {"gap_type": "asset_context_readiness", "severity": "high"},
    ]
    requestable = [
        {
            "evidence_item": "Charging schedule, tariff sheets, and lease boundary",
            "source": "Owner, operator, and utility records",
            "why_needed": "Needed before cost interpretation and peer comparison.",
            "related_clusters": ["fuel_energy_cluster", "operating_regime_cluster"],
        }
    ]
    budget = [
        {
            "budget_scope": "total_public_discovery",
            "budget_state": "bounded",
            "budget_class": "bounded_public_discovery",
        }
    ]

    tx_state = build_discovery_case_state(
        target_definition=tx_target,
        routing_output={
            "routing_ready": True,
            "report_type_allowed": "Minimum Evidence Report",
            "regulatory_stack": ["ERCOT", "TCEQ"],
            "target_classification_result": {"technical_scraping_allowed": True},
        },
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=requestable,
        attempts=[],
        search_budget_register=budget,
        case_fingerprint="tx-case",
        asset_context_readiness={"state": "asset_localized"},
    )
    nyc_state = build_discovery_case_state(
        target_definition=nyc_target,
        routing_output={
            "routing_ready": True,
            "report_type_allowed": "Minimum Evidence Report",
            "regulatory_stack": ["LL84", "LL97"],
            "target_classification_result": {"technical_scraping_allowed": True},
        },
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=requestable,
        attempts=[],
        search_budget_register=budget,
        case_fingerprint="nyc-case",
        asset_context_readiness={"state": "asset_localized"},
    )

    tx_needs = build_discovery_need_register(
        target_definition=tx_target,
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=requestable,
        attempts=[],
        search_budget_register=budget,
        dynamic_case_state=tx_state,
    )
    nyc_needs = build_discovery_need_register(
        target_definition=nyc_target,
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=requestable,
        attempts=[],
        search_budget_register=budget,
        dynamic_case_state=nyc_state,
    )

    tx_utility = next(row for row in tx_needs if row["need_id"] == "utility_territory_and_tariff_context")
    nyc_utility = next(row for row in nyc_needs if row["need_id"] == "utility_territory_and_tariff_context")

    assert tx_utility["activation_reasons"]
    assert tx_utility["activation_basis_register"]
    assert tx_utility["state_signals_used"]
    assert tx_utility["source_family_preference_hints"] == ["utility_service_territory"]
    assert tx_utility["jurisdiction_fit"] in {"high", "medium"}
    assert tx_utility["hypothesis_pressure_score"] > 0
    assert tx_utility["financial_pressure_score"] > 0
    assert nyc_utility["source_family_preference_hints"] == []
    assert nyc_utility["jurisdiction_fit"] == "generic"


def test_discovery_planner_suppresses_non_identity_routes_when_technical_scraping_is_blocked():
    blocked_state = build_discovery_case_state(
        target_definition={
            "target_type": "warehouse_distribution",
            "jurisdiction_scope": ["US-CA-SF"],
        },
        routing_output={
            "routing_ready": False,
            "report_type_allowed": "Target Classification Brief",
            "regulatory_stack": ["classification_only"],
            "target_classification_result": {"technical_scraping_allowed": False},
        },
        coverage_gaps=[
            {"gap_type": "asset_primary_anchor_missing", "severity": "high"},
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        ],
        requestable_evidence_items=[],
        attempts=[],
        search_budget_register=[
            {
                "budget_scope": "total_public_discovery",
                "budget_state": "bounded",
                "budget_class": "classification_only",
            }
        ],
        case_fingerprint="blocked-case",
        asset_context_readiness={"state": "address_only"},
    )

    discovery_needs = build_discovery_need_register(
        target_definition={
            "target_type": "warehouse_distribution",
            "jurisdiction_scope": ["US-CA-SF"],
        },
        coverage_gaps=[
            {"gap_type": "asset_primary_anchor_missing", "severity": "high"},
            {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        ],
        requestable_evidence_items=[],
        attempts=[],
        search_budget_register=[
            {
                "budget_scope": "total_public_discovery",
                "budget_state": "bounded",
                "budget_class": "classification_only",
            }
        ],
        dynamic_case_state=blocked_state,
    )

    assert [row["need_id"] for row in discovery_needs] == ["asset_identity_anchor"]


def test_discovery_planner_reprioritizes_same_family_cases_from_tariff_vs_boundary_pressure() -> None:
    target_definition = {
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": ["US-TX-DALLAS"],
        "decision_intent": "asset_screening",
        "report_intent": "asset_preverification_screening",
    }
    coverage_gaps = [{"gap_type": "asset_energy_behavior_reference", "severity": "high"}]
    budget = [
        {
            "budget_scope": "total_public_discovery",
            "budget_state": "bounded",
            "budget_class": "bounded_public_discovery",
        }
    ]

    tariff_state = build_discovery_case_state(
        target_definition=target_definition,
        routing_output={
            "routing_ready": True,
            "report_type_allowed": "Minimum Evidence Report",
            "regulatory_stack": ["ERCOT", "TCEQ"],
            "target_classification_result": {"technical_scraping_allowed": True},
        },
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=[
            {
                "evidence_item": "Charging schedule, utility tariff, and demand-charge structure",
                "source": "Owner, operator, and utility records",
                "why_needed": "Needed to test whether charging peaks drive the cost story.",
            }
        ],
        attempts=[],
        search_budget_register=budget,
        case_fingerprint="tariff-case",
        asset_context_readiness={"state": "asset_localized"},
    )
    boundary_state = build_discovery_case_state(
        target_definition=target_definition,
        routing_output={
            "routing_ready": True,
            "report_type_allowed": "Minimum Evidence Report",
            "regulatory_stack": ["ERCOT", "TCEQ"],
            "target_classification_result": {"technical_scraping_allowed": True},
        },
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=[
            {
                "evidence_item": "Lease matrix, operator boundary, and metering responsibility",
                "source": "Owner and operator records",
                "why_needed": "Needed to test whether value leaks across the control boundary.",
            }
        ],
        attempts=[],
        search_budget_register=budget,
        case_fingerprint="boundary-case",
        asset_context_readiness={"state": "asset_localized"},
    )

    tariff_needs = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=[
            {
                "evidence_item": "Charging schedule, utility tariff, and demand-charge structure",
                "source": "Owner, operator, and utility records",
                "why_needed": "Needed to test whether charging peaks drive the cost story.",
            }
        ],
        attempts=[],
        search_budget_register=budget,
        dynamic_case_state=tariff_state,
    )
    boundary_needs = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=[
            {
                "evidence_item": "Lease matrix, operator boundary, and metering responsibility",
                "source": "Owner and operator records",
                "why_needed": "Needed to test whether value leaks across the control boundary.",
            }
        ],
        attempts=[],
        search_budget_register=budget,
        dynamic_case_state=boundary_state,
    )

    tariff_utility = next(row for row in tariff_needs if row["need_id"] == "utility_territory_and_tariff_context")
    boundary_utility = next(row for row in boundary_needs if row["need_id"] == "utility_territory_and_tariff_context")
    tariff_boundary = next(row for row in tariff_needs if row["need_id"] == "operator_boundary_and_control")
    boundary_boundary = next(row for row in boundary_needs if row["need_id"] == "operator_boundary_and_control")

    assert tariff_utility["hypothesis_pressure_score"] > boundary_utility["hypothesis_pressure_score"]
    assert boundary_boundary["hypothesis_pressure_score"] > tariff_boundary["hypothesis_pressure_score"]
    assert any(
        value == "hypothesis_pressure:warehouse_tariff_orchestration"
        for value in tariff_utility["activation_basis_register"]
    )
    assert any(
        value == "hypothesis_pressure:warehouse_control_boundary_value_leakage"
        for value in boundary_boundary["activation_basis_register"]
    )
