from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.congruence_intelligence.dynamic_intake import build_dynamic_intake_question_register
from runtime_orchestrator.congruence_intelligence.gap_taxonomy import (
    build_evidence_need_class_register,
    build_gap_taxonomy_register,
    extend_gap_taxonomy_with_comparison_risks,
)
from runtime_orchestrator.congruence_intelligence.hypothesis_ingestion import build_claim_impact_register


def _warehouse_questions_and_claims() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    stop_condition_register = [
        {
            "path_id": "dock_and_service_intensity",
            "minimum_sufficient_evidence": "Observed dock or service-intensity clue plus schedule or operator context.",
            "escalation_condition": "ask operator for dock count, shifts, and throughput window",
        },
        {
            "path_id": "mhe_charging_and_mechanical_clues",
            "minimum_sufficient_evidence": "Public clues showing charging or mechanical systems relevant to demand and conditioning.",
            "escalation_condition": "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type",
        },
        {
            "path_id": "operator_boundary_and_control",
            "minimum_sufficient_evidence": "At least one operator clue plus one ownership or lease-boundary clue.",
            "escalation_condition": "ask owner/operator for lease responsibility and metering boundary",
        },
        {
            "path_id": "throughput_schedule_pack",
            "minimum_sufficient_evidence": "operator-confirmed shifts and throughput window",
            "escalation_condition": "ask operator / facility manager for operating hours and throughput windows",
        },
        {
            "path_id": "utility_bill_pack",
            "minimum_sufficient_evidence": "12 months of utility bills",
            "escalation_condition": "ask owner / accounting / operator for 12 months of bills",
        },
        {
            "path_id": "utility_tariff_pack",
            "minimum_sufficient_evidence": "tariff sheet or bill page showing rate class",
            "escalation_condition": "ask owner / accounting / operator for tariff sheet",
        },
        {
            "path_id": "lease_responsibility_pack",
            "minimum_sufficient_evidence": "owner/operator lease matrix",
            "escalation_condition": "ask owner / asset manager / operator for lease matrix",
        },
    ]
    questions = build_dynamic_intake_question_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
                {"pack_name": "lease_responsibility_pack", "current_state": "requested_but_absent"},
            ]
        },
        discovery_need_register=[
            {
                "need_id": "dock_and_service_intensity",
                "discovery_need": "Bound dock density and service-level intensity.",
                "search_families_to_explore": ["property_listing", "site_plan_or_photo_clues"],
            },
            {
                "need_id": "mhe_charging_and_mechanical_clues",
                "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues.",
                "search_families_to_explore": ["property_photo_clues", "permit_record"],
            },
            {
                "need_id": "operator_boundary_and_control",
                "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules.",
                "search_families_to_explore": ["tenant_operator_page", "lease_summary"],
            },
        ],
        stop_condition_register=stop_condition_register,
    )
    claim_impact_register = build_claim_impact_register(
        dynamic_intake_question_register=questions,
        stop_condition_register=stop_condition_register,
    )
    return questions, claim_impact_register


def test_gap_taxonomy_classifies_control_tariff_and_comparability_gaps():
    questions, claim_impact_register = _warehouse_questions_and_claims()
    gap_taxonomy = build_gap_taxonomy_register(
        dynamic_intake_question_register=questions,
        promotion_blocker_register=[],
        claim_impact_register=claim_impact_register,
    )
    by_id = {row["gap_id"]: row for row in gap_taxonomy}
    assert by_id["warehouse_dock_cycles_and_operating_hours"]["gap_class"] == "missing_comparability"
    assert by_id["warehouse_dock_cycles_and_operating_hours"]["next_action_type"] == "comparison_building"
    assert by_id["warehouse_mhe_charging_profile"]["gap_class"] == "missing_tariff_evidence"
    assert by_id["warehouse_control_boundary"]["gap_class"] == "missing_control_evidence"

    evidence_need_class_register = build_evidence_need_class_register(
        gap_taxonomy_register=gap_taxonomy,
    )
    assert any(row["evidence_need_class"] == "missing_control_evidence" for row in evidence_need_class_register)
    assert any(row["next_action_type"] == "comparison_building" for row in evidence_need_class_register)


def test_motor_049_and_051_extend_gap_taxonomy_with_comparison_risks():
    m49 = Motor049Adapter().run(
        {
            "motor_007": {
                "target_definition_contract": {
                    "target_name": "Sunrise Logistics Hub",
                    "target_identifier": "sunrise-logistics-hub-2026",
                    "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                    "target_type": "warehouse_distribution",
                    "jurisdiction_scope": ["US-TX"],
                },
                "target_classification_object": {
                    "target_type": "OPERATING_ASSET",
                    "classification_confidence": "high",
                },
            },
            "motor_012": {
                "facility_prior": {},
                "asset_field_register": [],
            },
            "motor_028": {
                "source_register": [],
                "enriched_data": {},
                "search_budget_register": [
                    {
                        "budget_scope": "total_public_discovery",
                        "budget_state": "bounded",
                        "budget_class": "bounded_public_discovery",
                    }
                ],
                "search_attempt_ledger": [],
                "search_attempt_outcome_register": [],
                "search_exhaustion_register": [],
                "discovery_need_register": [
                    {
                        "need_id": "dock_and_service_intensity",
                        "discovery_need": "Bound dock density and service-level intensity.",
                        "search_families_to_explore": ["property_listing", "site_plan_or_photo_clues"],
                    },
                    {
                        "need_id": "mhe_charging_and_mechanical_clues",
                        "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues.",
                        "search_families_to_explore": ["property_photo_clues", "permit_record"],
                    },
                ],
                "search_family_execution_plan": [],
                "accepted_evidence_type_register": [],
                "discovery_stop_condition_register": [],
                "next_best_search_register": [],
                "search_target_priority_register": [],
                "search_success_effect_register": [],
                "search_failure_effect_register": [],
            },
        }
    )
    assert m49["gap_taxonomy_count"] >= 2
    assert m49["evidence_need_class_count"] == m49["gap_taxonomy_count"]

    m51 = Motor051Adapter().run(
        {
            "motor_049": m49,
            "motor_050": {
                "process_map": {},
                "subsystem_register": [],
                "control_boundary_map": [],
                "maintenance_dependency_map": [],
            },
        }
    )
    assert m51["gap_taxonomy_count"] >= m49["gap_taxonomy_count"]
    assert any(
        row["source_type"] == "invalid_comparison_risk" and row["next_action_type"] == "comparison_building"
        for row in m51["gap_taxonomy_register"]
    )
    assert any(row["evidence_need_class"] == "missing_comparability" for row in m51["evidence_need_class_register"])


def test_extend_gap_taxonomy_with_comparison_risks_produces_comparison_building_rows():
    extended = extend_gap_taxonomy_with_comparison_risks(
        gap_taxonomy_register=[],
        invalid_comparison_risk_register=[
            {
                "risk_name": "warehouse_area_only_comparison",
                "trigger": "Service-level complexity and charging schedule invalidate area-only comparison.",
                "blocked_claims": ["peer_superiority"],
                "required_normalization": ["service level", "throughput proxy", "dock activity profile"],
            }
        ],
    )
    assert extended[0]["gap_class"] == "missing_comparability"
    assert extended[0]["next_action_type"] == "comparison_building"
