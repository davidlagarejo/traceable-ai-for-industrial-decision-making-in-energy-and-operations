from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.dynamic_intake import (
    build_dynamic_intake_question_register,
)
from runtime_orchestrator.congruence_intelligence.hypothesis_backbone import (
    build_dominant_hypothesis_register,
    build_hypothesis_claim_blocker_register,
    build_hypothesis_evidence_gap_register,
    build_rival_hypothesis_seed_register,
)


def _stop_row(path_id: str, minimum: str, escalation: str) -> dict[str, str]:
    return {
        "path_id": path_id,
        "minimum_sufficient_evidence": minimum,
        "escalation_condition": escalation,
    }


def test_hypothesis_backbone_surfaces_different_dominant_warehouse_hypotheses_from_case_pressure() -> None:
    discovery_need_register = [
        {"need_id": "warehouse_subtype_classification"},
        {"need_id": "dock_and_service_intensity"},
        {"need_id": "mhe_charging_and_mechanical_clues"},
        {"need_id": "utility_territory_and_tariff_context"},
        {"need_id": "operator_boundary_and_control"},
    ]

    tariff_seed_register = build_rival_hypothesis_seed_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
            ],
            "tariff_exposure_register": [{"exposure_type": "demand_charge_exposure_hidden"}],
            "utility_charge_breakdown_register": [{"charge_driver": "demand"}],
        },
        discovery_need_register=discovery_need_register,
        congruence_case_state={
            "financial_exposure_priority": ["demand_charge_exposure_hidden", "wrong_underwriting_premium"],
        },
    )
    control_seed_register = build_rival_hypothesis_seed_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "lease_responsibility_pack", "current_state": "requested_but_absent"},
                {"pack_name": "metering_boundary_pack", "current_state": "requested_but_absent"},
            ],
            "control_boundary_evidence_register": [{"source_family": "tenant_operator_page"}],
            "owner_operator_tenant_responsibility_register": [{"control_domain": "operator"}],
        },
        discovery_need_register=discovery_need_register,
        congruence_case_state={
            "financial_exposure_priority": ["tenant_operator_value_leakage", "wrong_underwriting_premium"],
        },
    )

    tariff_dominant = build_dominant_hypothesis_register(
        rival_hypothesis_seed_register=tariff_seed_register,
    )[0]
    control_dominant = build_dominant_hypothesis_register(
        rival_hypothesis_seed_register=control_seed_register,
    )[0]

    assert tariff_dominant["hypothesis_id"] == "warehouse_tariff_orchestration"
    assert control_dominant["hypothesis_id"] == "warehouse_control_boundary_value_leakage"


def test_hypothesis_backbone_registers_feed_intake_alignment_without_question_id_dependency() -> None:
    seed_register = build_rival_hypothesis_seed_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        operational_intake_pack={
            "diligence_pack_register": [
                {"pack_name": "throughput_schedule_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_bill_pack", "current_state": "requested_but_absent"},
                {"pack_name": "utility_tariff_pack", "current_state": "requested_but_absent"},
            ],
            "tariff_exposure_register": [{"exposure_type": "demand_charge_exposure_hidden"}],
        },
        discovery_need_register=[
            {"need_id": "mhe_charging_and_mechanical_clues"},
            {"need_id": "utility_territory_and_tariff_context"},
        ],
        congruence_case_state={
            "financial_exposure_priority": ["demand_charge_exposure_hidden"],
        },
    )
    dominant_register = build_dominant_hypothesis_register(
        rival_hypothesis_seed_register=seed_register,
    )
    evidence_gap_register = build_hypothesis_evidence_gap_register(
        rival_hypothesis_seed_register=seed_register,
        stop_condition_register=[
            _stop_row(
                "mhe_charging_and_mechanical_clues",
                "Public clues showing charging or mechanical systems relevant to demand and conditioning.",
                "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type",
            ),
            _stop_row(
                "utility_territory_and_tariff_context",
                "Utility territory plus one tariff or rate-family anchor.",
                "ask operator or owner for utility bills and tariff sheets",
            ),
            _stop_row(
                "utility_bill_pack",
                "12 months of utility bills",
                "ask owner / accounting / operator for 12 months of bills",
            ),
            _stop_row(
                "utility_tariff_pack",
                "tariff sheet or bill page showing rate class",
                "ask owner / accounting / operator for tariff sheet",
            ),
            _stop_row(
                "throughput_schedule_pack",
                "operator-confirmed shifts and throughput window",
                "ask operator / facility manager for operating hours and throughput windows",
            ),
        ],
        next_best_search_register=[
            {
                "need_id": "mhe_charging_and_mechanical_clues",
                "next_search_target": "Permit record or photo clue showing charging or HVAC context.",
            }
        ],
    )
    claim_blocker_register = build_hypothesis_claim_blocker_register(
        rival_hypothesis_seed_register=seed_register,
    )

    assert dominant_register[0]["hypothesis_id"] == "warehouse_tariff_orchestration"
    assert evidence_gap_register[0]["evidence_needed"]
    assert "demand_charge_claim" in {
        row["blocked_claim"]
        for row in claim_blocker_register
        if row["hypothesis_id"] == "warehouse_tariff_orchestration"
    }

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
            _stop_row("mhe_charging_and_mechanical_clues", "", "ask operator for forklift fleet, charging windows, and HVAC / rooftop system type"),
            _stop_row("utility_territory_and_tariff_context", "", "ask operator or owner for utility bills and tariff sheets"),
            _stop_row("throughput_schedule_pack", "", "ask operator / facility manager for operating hours and throughput windows"),
            _stop_row("utility_bill_pack", "", "ask owner / accounting / operator for 12 months of bills"),
            _stop_row("utility_tariff_pack", "", "ask owner / accounting / operator for tariff sheet"),
        ],
        congruence_case_state={
            "comparison_blockers": ["control_boundary_and_tariff"],
            "active_loss_pattern_tags": ["mhe_charging_peak_demand"],
            "financial_exposure_priority": ["demand_charge_exposure_hidden"],
            "search_budget_state": "bounded",
            "tariff_exposure_active": True,
            "control_boundary_active": False,
            "dominant_hypothesis_ids": [row["hypothesis_id"] for row in dominant_register],
            "dominant_hypothesis_labels": [row["hypothesis_label"] for row in dominant_register],
        },
    )
    question_by_id = {row["question_id"]: row for row in questions}

    assert (
        question_by_id["warehouse_mhe_charging_profile"]["question_score_components"][
            "dominant_hypothesis_alignment_value"
        ]
        > 0
    )
    assert any(
        reason.startswith("dominant_hypothesis:warehouse_tariff_orchestration")
        for reason in question_by_id["warehouse_mhe_charging_profile"]["activation_reasons"]
    )
