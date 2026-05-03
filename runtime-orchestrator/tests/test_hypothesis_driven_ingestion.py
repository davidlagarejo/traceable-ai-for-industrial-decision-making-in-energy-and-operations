from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.congruence_intelligence.dynamic_intake import (
    build_dynamic_intake_question_register,
)
from runtime_orchestrator.congruence_intelligence.hypothesis_ingestion import (
    build_claim_impact_register,
    build_hypothesis_discrimination_register,
    build_rival_hypothesis_register,
)


def _warehouse_questions() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    stop_condition_register = [
        {
            "path_id": "warehouse_subtype_classification",
            "minimum_sufficient_evidence": "Subtype clue from listing, brochure, zoning, operator, or permit context.",
            "escalation_condition": "ask operator whether facility is dry, cold-chain, fulfillment, cross-dock, or mixed",
        },
        {
            "path_id": "dock_and_service_intensity",
            "minimum_sufficient_evidence": "Observed dock or service-intensity clue plus schedule or operator context.",
            "escalation_condition": "ask operator for dock count, shifts, and throughput window",
        },
        {
            "path_id": "utility_territory_and_tariff_context",
            "minimum_sufficient_evidence": "Utility territory plus one tariff or rate-family anchor.",
            "escalation_condition": "ask operator or owner for utility bills and tariff sheets",
        },
        {
            "path_id": "operator_boundary_and_control",
            "minimum_sufficient_evidence": "At least one operator clue plus one ownership or lease-boundary clue.",
            "escalation_condition": "ask owner/operator for lease responsibility and metering boundary",
        },
        {
            "path_id": "mhe_charging_and_mechanical_clues",
            "minimum_sufficient_evidence": "Public clues showing charging or mechanical systems relevant to demand and conditioning.",
            "escalation_condition": "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type",
        },
        {
            "path_id": "throughput_schedule_pack",
            "minimum_sufficient_evidence": "operator-confirmed shifts and throughput window",
            "escalation_condition": "ask operator / facility manager for operating hours and throughput windows",
        },
        {
            "path_id": "lease_responsibility_pack",
            "minimum_sufficient_evidence": "owner/operator lease matrix",
            "escalation_condition": "ask owner / asset manager / operator for lease matrix",
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
    ]
    next_best_search_register = [
        {
            "need_id": "warehouse_subtype_classification",
            "next_search_target": "Property listing or leasing brochure confirming subtype.",
        },
        {
            "need_id": "dock_and_service_intensity",
            "next_search_target": "Site plan or photo clue confirming dock density.",
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
                "need_id": "warehouse_subtype_classification",
                "discovery_need": "Confirm warehouse subtype.",
                "search_families_to_explore": ["property_listing", "leasing_brochure"],
            },
            {
                "need_id": "dock_and_service_intensity",
                "discovery_need": "Bound dock density and service-level intensity.",
                "search_families_to_explore": ["property_listing", "site_plan_or_photo_clues"],
            },
            {
                "need_id": "operator_boundary_and_control",
                "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules.",
                "search_families_to_explore": ["tenant_operator_page", "lease_summary"],
            },
            {
                "need_id": "mhe_charging_and_mechanical_clues",
                "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues.",
                "search_families_to_explore": ["property_photo_clues", "permit_record"],
            },
            {
                "need_id": "utility_territory_and_tariff_context",
                "discovery_need": "Confirm utility territory and tariff context.",
                "search_families_to_explore": ["utility_service_territory", "utility_tariff_schedule"],
            },
        ],
        stop_condition_register=stop_condition_register,
    )
    return questions, stop_condition_register, next_best_search_register


def test_hypothesis_driven_ingestion_registers_public_search_intake_and_claim_impact():
    questions, stop_condition_register, next_best_search_register = _warehouse_questions()

    rival_register = build_rival_hypothesis_register(
        dynamic_intake_question_register=questions,
        stop_condition_register=stop_condition_register,
        next_best_search_register=next_best_search_register,
    )
    discrimination_register = build_hypothesis_discrimination_register(
        dynamic_intake_question_register=questions,
        stop_condition_register=stop_condition_register,
        next_best_search_register=next_best_search_register,
    )
    claim_impact_register = build_claim_impact_register(
        dynamic_intake_question_register=questions,
        stop_condition_register=stop_condition_register,
    )

    subtype_row = next(row for row in rival_register if row["question_id"] == "warehouse_subtype_and_cold_chain_status")
    assert len(subtype_row["rival_hypotheses"]) == 2
    assert subtype_row["public_search_first"] is True
    assert "property_listing" in subtype_row["public_search_attempted"]
    assert subtype_row["evidence_needed"]
    assert "dry-only, cold-chain" in subtype_row["intake_if_missing"]

    dock_row = next(row for row in discrimination_register if row["question_id"] == "warehouse_dock_cycles_and_operating_hours")
    assert "service-level intensity denominator problem" in dock_row["hypothesis_it_discriminates"]
    assert "Site plan or photo clue confirming dock density." in dock_row["next_public_search_target"]

    claim_row = next(row for row in claim_impact_register if row["question_id"] == "warehouse_mhe_charging_profile")
    charging_row = next(row for row in discrimination_register if row["question_id"] == "warehouse_mhe_charging_profile")
    assert "tariff-exposure" in claim_row["claim_impact"] or "tariff" in claim_row["claim_impact"].lower()
    assert "demand_charge_claim" in claim_row["blocked_claims"]
    assert claim_row["claim_governance_basis"] == "structured_question_metadata"
    assert {row["claim_governance_basis"] for row in claim_impact_register} == {"structured_question_metadata"}
    assert any(row["relation"] == "supports" for row in claim_row["structured_hypotheses"])
    assert "control_boundary_and_tariff" in charging_row["comparison_requirements_unlocked"]


def test_structured_claim_governance_survives_question_id_rename():
    question = {
        "question_id": "custom_operator_boundary_probe",
        "hypothesis_it_discriminates": "owner-capturable efficiency opportunity vs control-boundary value leakage",
        "claim_impact_if_missing": "No owner-capturable retrofit or ROI claim until the control boundary is evidenced.",
        "intake_question": "Who controls docks, charging, HVAC schedules, and who pays utility or CAPEX?",
        "linked_need_ids": ["operator_boundary_and_control"],
        "linked_pack_names": ["lease_responsibility_pack"],
        "public_search_context": ["tenant_operator_page"],
        "priority": "critical",
        "rival_hypotheses": [
            "The owner can capture the value of an energy intervention.",
            "The operator controls the dominant drivers and value leaks across the boundary.",
        ],
        "blocked_claims_if_missing": ["owner_capturable_roi_claim", "retrofit_capture_claim"],
        "supports_hypotheses": ["The operator controls the dominant drivers and value leaks across the boundary."],
        "falsifies_hypotheses": ["The owner can capture the value of an energy intervention."],
        "comparison_requirements_unlocked": ["control_boundary_and_tariff"],
    }
    stop_condition_register = [
        {
            "path_id": "operator_boundary_and_control",
            "minimum_sufficient_evidence": "At least one operator clue plus one ownership or lease-boundary clue.",
            "escalation_condition": "ask owner/operator for lease responsibility and metering boundary",
        },
        {
            "path_id": "lease_responsibility_pack",
            "minimum_sufficient_evidence": "owner/operator lease matrix",
            "escalation_condition": "ask owner / asset manager / operator for lease matrix",
        },
    ]

    claim_impact_register = build_claim_impact_register(
        dynamic_intake_question_register=[question],
        stop_condition_register=stop_condition_register,
    )
    discrimination_register = build_hypothesis_discrimination_register(
        dynamic_intake_question_register=[question],
        stop_condition_register=stop_condition_register,
        next_best_search_register=[],
    )

    assert claim_impact_register[0]["blocked_claims"] == ["owner_capturable_roi_claim", "retrofit_capture_claim"]
    assert claim_impact_register[0]["claim_governance_basis"] == "structured_question_metadata"
    assert discrimination_register[0]["supports_hypotheses"] == [
        "The operator controls the dominant drivers and value leaks across the boundary."
    ]
    assert discrimination_register[0]["falsifies_hypotheses"] == [
        "The owner can capture the value of an energy intervention."
    ]
    assert discrimination_register[0]["comparison_requirements_unlocked"] == ["control_boundary_and_tariff"]


def test_missing_structured_claim_metadata_now_blocks_via_metadata_gap() -> None:
    question = {
        "question_id": "legacy_like_probe_without_metadata",
        "hypothesis_it_discriminates": "demand-charge orchestration problem vs generic energy inefficiency problem",
        "claim_impact_if_missing": "No tariff claim should harden until charging behavior is known.",
        "intake_question": "Do forklifts charge on-site and during what windows?",
        "linked_need_ids": ["mhe_charging_and_mechanical_clues"],
        "linked_pack_names": ["utility_bill_pack"],
        "public_search_context": ["property_photo_clues"],
        "priority": "critical",
    }
    stop_condition_register = [
        {
            "path_id": "mhe_charging_and_mechanical_clues",
            "minimum_sufficient_evidence": "Public clues showing charging or mechanical systems relevant to demand and conditioning.",
            "escalation_condition": "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type",
        }
    ]

    claim_impact_register = build_claim_impact_register(
        dynamic_intake_question_register=[question],
        stop_condition_register=stop_condition_register,
    )

    assert claim_impact_register[0]["blocked_claims"] == ["claim_governance_metadata_missing"]
    assert claim_impact_register[0]["claim_governance_basis"] == "metadata_gap_prohibition"


def test_legacy_string_fallback_requires_explicit_compatibility_path() -> None:
    question = {
        "question_id": "legacy_like_probe_with_compatibility_flag",
        "hypothesis_it_discriminates": "demand-charge orchestration problem vs generic energy inefficiency problem",
        "claim_impact_if_missing": "No tariff claim should harden until charging behavior is known.",
        "intake_question": "Do forklifts charge on-site and during what windows?",
        "linked_need_ids": ["mhe_charging_and_mechanical_clues"],
        "linked_pack_names": ["utility_bill_pack"],
        "public_search_context": ["property_photo_clues"],
        "priority": "critical",
        "allow_legacy_string_fallback": True,
    }
    stop_condition_register = [
        {
            "path_id": "mhe_charging_and_mechanical_clues",
            "minimum_sufficient_evidence": "Public clues showing charging or mechanical systems relevant to demand and conditioning.",
            "escalation_condition": "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type",
        }
    ]

    claim_impact_register = build_claim_impact_register(
        dynamic_intake_question_register=[question],
        stop_condition_register=stop_condition_register,
    )

    assert claim_impact_register[0]["claim_governance_basis"] == "legacy_string_fallback_explicit"
    assert "generic_efficiency_retrofit" in claim_impact_register[0]["blocked_claims"]


def test_motor_049_and_051_propagate_hypothesis_driven_ingestion_registers():
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
                        "need_id": "warehouse_subtype_classification",
                        "discovery_need": "Confirm warehouse subtype.",
                        "search_families_to_explore": ["property_listing", "leasing_brochure"],
                    },
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
                "next_best_search_register": [
                    {
                        "need_id": "dock_and_service_intensity",
                        "next_search_target": "Site plan or photo clue confirming dock density.",
                    }
                ],
                "search_target_priority_register": [],
                "search_success_effect_register": [],
                "search_failure_effect_register": [],
            },
        }
    )

    assert m49["rival_hypothesis_count"] >= 3
    assert m49["hypothesis_discrimination_count"] >= 3
    assert m49["claim_impact_count"] >= 3
    assert m49["rival_hypothesis_seed_count"] >= 3
    assert m49["dominant_hypothesis_count"] >= 1
    assert m49["hypothesis_evidence_gap_count"] >= 1
    assert m49["hypothesis_claim_blocker_count"] >= 1
    assert len(m49["operational_intake_pack"]["rival_hypothesis_register"]) >= 3
    assert len(m49["operational_intake_pack"]["hypothesis_discrimination_register"]) >= 3
    assert len(m49["operational_intake_pack"]["claim_impact_register"]) >= 3
    assert len(m49["operational_intake_pack"]["rival_hypothesis_seed_register"]) >= 3
    assert len(m49["operational_intake_pack"]["dominant_hypothesis_register"]) >= 1
    assert "dominant_hypothesis_ids" in m49["congruence_case_state"]
    assert "dominant_hypothesis_labels" in m49["congruence_case_state"]

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
    assert m51["rival_hypothesis_count"] == m49["rival_hypothesis_count"]
    assert m51["hypothesis_discrimination_count"] == m49["hypothesis_discrimination_count"]
    assert m51["claim_impact_count"] == m49["claim_impact_count"]
