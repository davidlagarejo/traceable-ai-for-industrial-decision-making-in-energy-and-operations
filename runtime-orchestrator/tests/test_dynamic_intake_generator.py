from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.congruence_intelligence.dynamic_intake import (
    build_congruence_case_state,
    build_decision_context_register,
    build_dynamic_intake_question_register,
    build_intake_priority_register,
    build_question_candidate_register,
    build_question_normalization_register,
    build_required_from_register,
    build_truncated_question_register,
)


def _stop_row(path_id: str, escalation_condition: str) -> dict[str, str]:
    return {
        "path_id": path_id,
        "escalation_condition": escalation_condition,
    }


def test_warehouse_dynamic_intake_generator_produces_discriminating_questions():
    questions = build_dynamic_intake_question_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
                {"pack_name": "lease_responsibility_pack", "current_state": "requested_but_absent"},
                {"pack_name": "metering_boundary_pack", "current_state": "requested_but_absent"},
                {"pack_name": "equipment_inventory_pack", "current_state": "requested_but_absent"},
            ]
        },
        discovery_need_register=[
            {
                "need_id": "warehouse_subtype_classification",
                "discovery_need": "Confirm warehouse subtype.",
                "search_families_to_explore": ["property_listing", "leasing_brochure"],
            },
            {
                "need_id": "refrigeration_presence",
                "discovery_need": "Determine whether any refrigerated footprint exists.",
                "search_families_to_explore": ["permit_record", "operator_page"],
            },
            {
                "need_id": "dock_and_service_intensity",
                "discovery_need": "Bound dock density and service-level intensity.",
                "search_families_to_explore": ["property_listing", "satellite_photo_clues"],
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
        stop_condition_register=[
            _stop_row("warehouse_subtype_classification", "ask operator whether facility is dry, cold-chain, fulfillment, cross-dock, or mixed"),
            _stop_row("refrigeration_presence", "ask operator whether any portion is refrigerated or temperature-controlled"),
            _stop_row("dock_and_service_intensity", "ask operator for dock count, shifts, and throughput window"),
            _stop_row("operator_boundary_and_control", "ask owner/operator for lease responsibility and metering boundary"),
            _stop_row("mhe_charging_and_mechanical_clues", "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type"),
            _stop_row("utility_territory_and_tariff_context", "ask operator or owner for utility bills and tariff sheets"),
            _stop_row("throughput_schedule_pack", "ask operator / facility manager for operating hours and throughput windows"),
            _stop_row("utility_bill_pack", "ask owner / accounting / operator for 12 months of bills"),
            _stop_row("utility_tariff_pack", "ask owner / accounting / operator for tariff sheet"),
            _stop_row("lease_responsibility_pack", "ask owner / asset manager / operator for lease matrix"),
            _stop_row("metering_boundary_pack", "ask owner / operator / energy manager for meter map"),
            _stop_row("equipment_inventory_pack", "ask maintenance / facility engineer for equipment inventory"),
        ],
    )

    question_ids = {row["question_id"] for row in questions}
    assert "warehouse_subtype_and_cold_chain_status" in question_ids
    assert "warehouse_dock_cycles_and_operating_hours" in question_ids
    assert "warehouse_mhe_charging_profile" in question_ids
    assert "warehouse_control_boundary" in question_ids
    assert any("dry-only, cold-chain" in row["intake_question"] for row in questions)
    assert any("dock doors" in row["intake_question"] for row in questions)
    assert any("charge on-site" in row["intake_question"] for row in questions)
    assert any("who controls docks, charging schedules" in row["intake_question"].lower() for row in questions)
    assert any(row["priority"] == "critical" for row in questions)
    assert all("question_score" in row for row in questions)
    assert all("question_score_components" in row for row in questions)
    assert any("blocked_claims_if_missing" in row for row in questions)
    assert any("comparison_requirements_unlocked" in row for row in questions)
    assert any("supports_hypotheses" in row for row in questions)
    assert any("questions_dropped_due_to_cap" in row for row in questions)

    required_from = build_required_from_register(
        dynamic_intake_question_register=questions,
    )
    priorities = build_intake_priority_register(
        dynamic_intake_question_register=questions,
    )
    assert len(required_from) == len(questions)
    assert len(priorities) == len(questions)
    assert any(row["priority_score"] == 100 for row in priorities)


def test_manufacturing_dynamic_intake_generator_produces_compressed_air_throughput_and_maintenance_questions():
    questions = build_dynamic_intake_question_register(
        asset_family_research_profile={"asset_family": "industrial_manufacturing"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "equipment_inventory_pack", "current_state": "requested_but_absent"},
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "maintenance_proof_pack", "current_state": "requested_but_absent"},
                {"pack_name": "cmms_or_workorder_pack", "current_state": "requested_but_absent"},
                {"pack_name": "permit_detail_pack", "current_state": "requested_but_absent"},
            ]
        },
        discovery_need_register=[
            {
                "need_id": "process_and_permit_profile",
                "discovery_need": "Confirm process family and permit-bearing systems.",
                "search_families_to_explore": ["permit_record", "environmental_registry"],
            },
            {
                "need_id": "thermal_system_and_utility_mix",
                "discovery_need": "Identify thermal systems and utility mix.",
                "search_families_to_explore": ["permit_record", "operator_page"],
            },
            {
                "need_id": "throughput_proxy_and_schedule",
                "discovery_need": "Find throughput proxies and operating schedule clues.",
                "search_families_to_explore": ["operator_page", "market_or_product_description"],
            },
        ],
        stop_condition_register=[
            _stop_row("process_and_permit_profile", "ask operator for process map and regulated equipment inventory"),
            _stop_row("thermal_system_and_utility_mix", "ask operator for boiler, furnace, steam, chilled-water and primary fuel inventory"),
            _stop_row("throughput_proxy_and_schedule", "ask operator for throughput by shift, duty cycle, and product mix"),
            _stop_row("equipment_inventory_pack", "ask maintenance / facility engineer for equipment inventory"),
            _stop_row("throughput_schedule_pack", "ask operator / facility manager for operating schedule"),
            _stop_row("maintenance_proof_pack", "ask maintenance manager for PM proof and downtime history"),
            _stop_row("cmms_or_workorder_pack", "ask maintenance manager for CMMS or work orders"),
            _stop_row("permit_detail_pack", "ask owner / operator / EHS lead for permit detail pack"),
        ],
    )

    assert any("compressed air" in row["intake_question"] for row in questions)
    assert any("throughput by shift" in row["intake_question"] for row in questions)
    assert any("PM logs, work orders, and downtime records" in row["intake_question"] for row in questions)
    assert any("boilers, furnaces, steam, chilled-water" in row["intake_question"] for row in questions)
    assert any(row["priority"] == "critical" for row in questions)
    assert all(int(row["question_score"]) >= int(row["priority_score"]) for row in questions)


def test_dynamic_intake_scoring_elevates_tariff_comparison_and_loss_pattern_questions():
    operational_intake_pack = {
        "diligence_pack_register": [
            {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
            {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
            {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
            {"pack_name": "lease_responsibility_pack", "current_state": "requested_but_absent"},
            {"pack_name": "metering_boundary_pack", "current_state": "requested_but_absent"},
            {"pack_name": "equipment_inventory_pack", "current_state": "requested_but_absent"},
        ],
        "tariff_exposure_register": [{"exposure_type": "demand_charge_exposure_hidden"}],
        "search_budget_register": [
            {
                "budget_scope": "total_public_discovery",
                "budget_state": "exhausted",
                "budget_class": "bounded_public_discovery",
            }
        ],
    }
    discovery_need_register = [
        {
            "need_id": "warehouse_subtype_classification",
            "discovery_need": "Confirm warehouse subtype.",
            "search_families_to_explore": ["property_listing", "leasing_brochure"],
        },
        {
            "need_id": "dock_and_service_intensity",
            "discovery_need": "Bound dock density and service-level intensity.",
            "search_families_to_explore": ["property_listing", "satellite_photo_clues"],
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
    ]
    stop_condition_register = [
        _stop_row("warehouse_subtype_classification", "ask operator whether facility is dry, cold-chain, fulfillment, cross-dock, or mixed"),
        _stop_row("dock_and_service_intensity", "ask operator for dock count, shifts, and throughput window"),
        _stop_row("operator_boundary_and_control", "ask owner/operator for lease responsibility and metering boundary"),
        _stop_row("mhe_charging_and_mechanical_clues", "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type"),
        _stop_row("utility_territory_and_tariff_context", "ask operator or owner for utility bills and tariff sheets"),
        _stop_row("throughput_schedule_pack", "ask operator / facility manager for operating hours and throughput windows"),
        _stop_row("utility_bill_pack", "ask owner / accounting / operator for 12 months of bills"),
        _stop_row("utility_tariff_pack", "ask owner / accounting / operator for tariff sheet"),
        _stop_row("lease_responsibility_pack", "ask owner / asset manager / operator for lease matrix"),
        _stop_row("metering_boundary_pack", "ask owner / operator / energy manager for meter map"),
        _stop_row("equipment_inventory_pack", "ask maintenance / facility engineer for equipment inventory"),
    ]
    case_state = build_congruence_case_state(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        target_definition={"decision_intent": "underwriting"},
    )

    questions = build_dynamic_intake_question_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        stop_condition_register=stop_condition_register,
        congruence_case_state=case_state,
        target_definition={"decision_intent": "underwriting"},
    )

    question_by_id = {row["question_id"]: row for row in questions}

    assert {questions[0]["question_id"], questions[1]["question_id"]} == {
        "warehouse_mhe_charging_profile",
        "warehouse_control_boundary",
    }
    assert "tariff_exposure_priority" in question_by_id["warehouse_mhe_charging_profile"]["activation_reasons"]
    assert "public_search_exhausted" in question_by_id["warehouse_mhe_charging_profile"]["activation_reasons"]
    assert question_by_id["warehouse_mhe_charging_profile"]["question_score_components"]["tariff_consequence_value"] > 0
    assert question_by_id["warehouse_mhe_charging_profile"]["question_score_components"]["public_search_exhaustion_value"] > 0
    assert "control_boundary_priority" in question_by_id["warehouse_control_boundary"]["activation_reasons"]
    assert any(reason.startswith("comparison_blocker:") for reason in question_by_id["warehouse_dock_cycles_and_operating_hours"]["activation_reasons"])
    assert any("dock_infiltration" in reason for row in questions for reason in row["activation_reasons"])


def test_dynamic_intake_scoring_respects_dominant_hypothesis_alignment() -> None:
    questions = build_dynamic_intake_question_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
            ]
        },
        discovery_need_register=[
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
        stop_condition_register=[
            _stop_row("mhe_charging_and_mechanical_clues", "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type"),
            _stop_row("utility_territory_and_tariff_context", "ask operator or owner for utility bills and tariff sheets"),
            _stop_row("throughput_schedule_pack", "ask operator / facility manager for operating hours and throughput windows"),
            _stop_row("utility_bill_pack", "ask owner / accounting / operator for 12 months of bills"),
            _stop_row("utility_tariff_pack", "ask owner / accounting / operator for tariff sheet"),
        ],
        congruence_case_state={
            "comparison_blockers": ["control_boundary_and_tariff"],
            "active_loss_pattern_tags": ["mhe_charging_peak_demand"],
            "financial_exposure_priority": ["demand_charge_exposure_hidden"],
            "search_budget_state": "bounded",
            "tariff_exposure_active": True,
            "control_boundary_active": False,
            "dominant_hypothesis_ids": ["warehouse_tariff_orchestration"],
            "dominant_hypothesis_labels": ["Demand cost is being driven by charging peaks."],
        },
    )

    question_by_id = {row["question_id"]: row for row in questions}
    charging_row = question_by_id["warehouse_mhe_charging_profile"]

    assert charging_row["question_score_components"]["dominant_hypothesis_alignment_value"] > 0
    assert any(
        reason.startswith("dominant_hypothesis:warehouse_tariff_orchestration")
        for reason in charging_row["activation_reasons"]
    )


def test_dynamic_intake_exposes_decision_context_candidate_and_normalization_registers() -> None:
    operational_intake_pack = {
        "diligence_pack_register": [
            {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
            {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
            {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
            {"pack_name": "lease_responsibility_pack", "current_state": "requested_but_absent"},
        ]
    }
    discovery_need_register = [
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
    ]
    stop_condition_register = [
        _stop_row("dock_and_service_intensity", "ask operator for dock count, shifts, and throughput window"),
        _stop_row("operator_boundary_and_control", "ask owner/operator for lease responsibility and metering boundary"),
        _stop_row("mhe_charging_and_mechanical_clues", "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type"),
        _stop_row("utility_territory_and_tariff_context", "ask operator or owner for utility bills and tariff sheets"),
        _stop_row("throughput_schedule_pack", "ask operator / facility manager for operating hours and throughput windows"),
        _stop_row("utility_bill_pack", "ask owner / accounting / operator for 12 months of bills"),
        _stop_row("utility_tariff_pack", "ask owner / accounting / operator for tariff sheet"),
        _stop_row("lease_responsibility_pack", "ask owner / asset manager / operator for lease matrix"),
    ]
    congruence_case_state = {
        "asset_family": "logistics_warehouse",
        "comparison_blockers": ["control_boundary_and_tariff", "dock_density_and_service_intensity"],
        "active_loss_pattern_tags": ["mhe_charging_peak_demand", "dock_infiltration"],
        "financial_exposure_priority": ["demand_charge_exposure_hidden", "tenant_operator_value_leakage"],
        "search_budget_state": "exhausted",
        "tariff_exposure_active": True,
        "control_boundary_active": True,
        "dominant_hypothesis_ids": ["warehouse_tariff_orchestration"],
        "dominant_hypothesis_labels": ["Demand cost is being driven by charging peaks."],
        "unresolved_pack_names": ["utility_bill_pack", "lease_responsibility_pack"],
        "decision_intent": "underwriting",
        "report_intent": "strategic_brief",
    }

    decision_context_register = build_decision_context_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        congruence_case_state=congruence_case_state,
        target_definition={"decision_intent": "underwriting", "report_intent": "strategic_brief"},
    )
    question_candidate_register = build_question_candidate_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        stop_condition_register=stop_condition_register,
        congruence_case_state=congruence_case_state,
        decision_context_register=decision_context_register,
        target_definition={"decision_intent": "underwriting", "report_intent": "strategic_brief"},
    )
    question_normalization_register = build_question_normalization_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        question_candidate_register=question_candidate_register,
    )

    assert any(row["context_type"] == "decision_intent" and row["context_value"] == "underwriting" for row in decision_context_register)
    assert any(row["context_type"] == "dominant_hypothesis" and row["context_value"] == "warehouse_tariff_orchestration" for row in decision_context_register)

    candidate_by_id = {row["question_id"]: row for row in question_candidate_register}
    charging_candidate = candidate_by_id["warehouse_mhe_charging_profile"]
    assert charging_candidate["candidate_origin"] == "state_native_synthesis"
    assert charging_candidate["candidate_status"] == "triggered"
    assert "decision_intent:underwriting" in charging_candidate["decision_context_keys"]
    assert "search_budget_state:exhausted" in charging_candidate["decision_context_keys"]
    assert any(key.startswith("dominant_hypothesis:warehouse_tariff_orchestration") for key in charging_candidate["decision_context_keys"])
    assert "need:mhe_charging_and_mechanical_clues" in charging_candidate["candidate_trigger_basis"]
    assert charging_candidate["normalization_required"] is True

    normalization_by_id = {row["question_id"]: row for row in question_normalization_register}
    charging_normalization = normalization_by_id["warehouse_mhe_charging_profile"]
    assert charging_normalization["normalization_basis"] == "governed_question_library"
    assert charging_normalization["normalization_status"] == "normalized"
    assert "charge on-site" in charging_normalization["normalized_intake_question"]
    assert "demand_charge_claim" in charging_normalization["blocked_claims_if_missing"]
    assert "control_boundary_and_tariff" in charging_normalization["comparison_requirements_unlocked"]


def test_dynamic_intake_truncation_is_explicit_and_auditable():
    operational_intake_pack = {
        "diligence_pack_register": [
            {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
            {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
            {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
            {"pack_name": "lease_responsibility_pack", "current_state": "requested_but_absent"},
            {"pack_name": "metering_boundary_pack", "current_state": "requested_but_absent"},
            {"pack_name": "equipment_inventory_pack", "current_state": "requested_but_absent"},
        ]
    }
    discovery_need_register = [
        {
            "need_id": "warehouse_subtype_classification",
            "discovery_need": "Confirm warehouse subtype.",
            "search_families_to_explore": ["property_listing", "leasing_brochure"],
        },
        {
            "need_id": "refrigeration_presence",
            "discovery_need": "Determine whether any refrigerated footprint exists.",
            "search_families_to_explore": ["permit_record", "operator_page"],
        },
        {
            "need_id": "dock_and_service_intensity",
            "discovery_need": "Bound dock density and service-level intensity.",
            "search_families_to_explore": ["property_listing", "satellite_photo_clues"],
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
    ]
    stop_condition_register = [
        _stop_row("warehouse_subtype_classification", "ask operator whether facility is dry, cold-chain, fulfillment, cross-dock, or mixed"),
        _stop_row("refrigeration_presence", "ask operator whether any portion is refrigerated or temperature-controlled"),
        _stop_row("dock_and_service_intensity", "ask operator for dock count, shifts, and throughput window"),
        _stop_row("operator_boundary_and_control", "ask owner/operator for lease responsibility and metering boundary"),
        _stop_row("mhe_charging_and_mechanical_clues", "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type"),
        _stop_row("utility_territory_and_tariff_context", "ask operator or owner for utility bills and tariff sheets"),
        _stop_row("throughput_schedule_pack", "ask operator / facility manager for operating hours and throughput windows"),
        _stop_row("utility_bill_pack", "ask owner / accounting / operator for 12 months of bills"),
        _stop_row("utility_tariff_pack", "ask owner / accounting / operator for tariff sheet"),
        _stop_row("lease_responsibility_pack", "ask owner / asset manager / operator for lease matrix"),
        _stop_row("metering_boundary_pack", "ask owner / operator / energy manager for meter map"),
        _stop_row("equipment_inventory_pack", "ask maintenance / facility engineer for equipment inventory"),
    ]

    visible_questions = build_dynamic_intake_question_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        stop_condition_register=stop_condition_register,
        question_cap=3,
    )
    dropped_questions = build_truncated_question_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack=operational_intake_pack,
        discovery_need_register=discovery_need_register,
        stop_condition_register=stop_condition_register,
        question_cap=3,
    )

    assert len(visible_questions) == 3
    assert len(dropped_questions) > 0
    assert all(row["truncation_reason"] == "top_question_cap_applied" for row in visible_questions)
    assert all(int(row["questions_dropped_due_to_cap"]) == len(dropped_questions) for row in visible_questions)
    assert all(row["drop_reason"] == "question_cap_exceeded" for row in dropped_questions)
    assert visible_questions[-1]["question_score"] >= dropped_questions[0]["question_score"]


def test_motor_049_emits_dynamic_intake_registers():
    out = Motor049Adapter().run(
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
                    },
                    {
                        "need_id": "dock_and_service_intensity",
                        "discovery_need": "Bound dock density and service-level intensity.",
                    },
                    {
                        "need_id": "operator_boundary_and_control",
                        "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules.",
                    },
                    {
                        "need_id": "mhe_charging_and_mechanical_clues",
                        "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues.",
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

    assert out["dynamic_intake_question_count"] >= 4
    assert out["truncated_question_count"] == 0
    assert out["required_from_count"] == out["dynamic_intake_question_count"]
    assert out["intake_priority_count"] == out["dynamic_intake_question_count"]
    assert out["congruence_case_state"]["asset_family"] == "logistics_warehouse"
    assert "comparison_blockers" in out["congruence_case_state"]
    assert len(out["operational_intake_pack"]["decision_context_register"]) > 0
    assert len(out["operational_intake_pack"]["question_candidate_register"]) >= out["dynamic_intake_question_count"]
    assert len(out["operational_intake_pack"]["question_normalization_register"]) >= out["dynamic_intake_question_count"]
    assert out["decision_context_count"] == len(out["operational_intake_pack"]["decision_context_register"])
    assert out["question_candidate_count"] == len(out["operational_intake_pack"]["question_candidate_register"])
    assert out["question_normalization_count"] == len(out["operational_intake_pack"]["question_normalization_register"])
    assert len(out["operational_intake_pack"]["dynamic_intake_question_register"]) >= 4
    assert out["operational_intake_pack"]["truncated_question_register"] == []
    assert len(out["operational_intake_pack"]["required_from_register"]) >= 4
    assert len(out["operational_intake_pack"]["intake_priority_register"]) >= 4
