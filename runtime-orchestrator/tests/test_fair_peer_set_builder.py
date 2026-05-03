from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.congruence_intelligence.peer_set_builder import (
    build_comparison_blocker_register,
    build_comparison_not_yet_valid_register,
    build_peer_candidate_family_register,
    build_peer_requirement_register,
)


def test_warehouse_peer_set_builder_produces_requirements_and_blocks_generic_comparison():
    peer_requirements = build_peer_requirement_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        fair_comparison_profile={
            "asset_family": "logistics_warehouse",
            "climate_context_state": "public_context_seeded",
            "operating_schedule_state": "not_yet_evidenced",
            "control_boundary_state": "not_yet_evidenced",
        },
        operational_intake_pack={},
        dynamic_intake_question_register=[
            {"question_id": "warehouse_subtype_and_cold_chain_status"},
            {"question_id": "warehouse_dock_cycles_and_operating_hours"},
            {"question_id": "warehouse_mhe_charging_profile"},
            {"question_id": "warehouse_control_boundary"},
        ],
    )

    by_key = {row["requirement_key"]: row for row in peer_requirements}
    assert by_key["asset_subtype_or_temperature_regime"]["comparison_status"] == "blocked"
    assert by_key["dock_density_and_service_intensity"]["comparison_status"] == "blocked"
    assert by_key["control_boundary_and_tariff"]["comparison_status"] == "blocked"
    assert by_key["asset_subtype_or_temperature_regime"]["peer_requirement_evidence_state"] == "not_yet_evidenced"
    assert by_key["asset_subtype_or_temperature_regime"]["why_still_unbounded"]
    assert by_key["control_boundary_and_tariff"]["evidence_basis"] == [
        "control boundary state",
        "lease responsibility pack",
        "metering boundary pack",
        "utility tariff pack",
    ]

    peer_candidates = build_peer_candidate_family_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        peer_requirement_register=peer_requirements,
    )
    assert any(row["candidate_family"] == "dry_warehouse_peers" for row in peer_candidates)
    assert all(row["candidate_state"] == "blocked_pending_requirements" for row in peer_candidates)

    comparison_blockers = build_comparison_blocker_register(
        peer_requirement_register=peer_requirements,
        comparison_validity_register=[],
    )
    comparison_not_yet_valid = build_comparison_not_yet_valid_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        comparison_blocker_register=comparison_blockers,
    )
    assert comparison_not_yet_valid
    assert "Do not compare this warehouse" in comparison_not_yet_valid[0]["explanation"]


def test_peer_requirement_builder_does_not_auto_bound_without_affirmative_evidence():
    peer_requirements = build_peer_requirement_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        fair_comparison_profile={
            "asset_family": "logistics_warehouse",
            "climate_context_state": "public_context_seeded",
            "operating_schedule_state": "not_yet_evidenced",
            "control_boundary_state": "not_yet_evidenced",
        },
        operational_intake_pack={},
        dynamic_intake_question_register=[],
    )

    by_key = {row["requirement_key"]: row for row in peer_requirements}
    assert by_key["asset_subtype_or_temperature_regime"]["comparison_status"] == "blocked"
    assert by_key["charging_and_power_mode"]["comparison_status"] == "blocked"
    assert by_key["control_boundary_and_tariff"]["comparison_status"] == "blocked"
    assert by_key["charging_and_power_mode"]["bounded_by"] == []
    assert "No affirmative evidence surface currently bounds this requirement." in by_key["asset_subtype_or_temperature_regime"]["why_still_unbounded"]


def test_peer_requirement_builder_uses_affirmative_evidence_not_question_absence_to_unlock():
    peer_requirements = build_peer_requirement_register(
        asset_family_research_profile={"asset_family": "logistics_warehouse"},
        fair_comparison_profile={
            "asset_family": "logistics_warehouse",
            "climate_context_state": "public_context_seeded",
            "operating_schedule_state": "partially_evidenced",
            "control_boundary_state": "evidenced",
        },
        operational_intake_pack={
            "throughput_schedule_pack": {"current_state": "evidenced"},
            "utility_bill_pack": {"current_state": "evidenced"},
            "utility_tariff_pack": {"current_state": "evidenced"},
            "lease_responsibility_pack": {"current_state": "evidenced"},
            "metering_boundary_pack": {"current_state": "evidenced"},
            "equipment_inventory_pack": {"current_state": "evidenced"},
        },
        dynamic_intake_question_register=[],
    )

    by_key = {row["requirement_key"]: row for row in peer_requirements}
    assert by_key["dock_density_and_service_intensity"]["comparison_status"] == "conditional"
    assert by_key["charging_and_power_mode"]["comparison_status"] == "conditional"
    assert by_key["control_boundary_and_tariff"]["comparison_status"] == "conditional"
    assert by_key["control_boundary_and_tariff"]["why_still_unbounded"] == ""
    assert "utility tariff pack" in by_key["control_boundary_and_tariff"]["bounded_by"]


def test_motor_051_emits_peer_requirements_candidate_families_and_explanation():
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
                        "need_id": "operator_boundary_and_control",
                        "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules.",
                        "search_families_to_explore": ["tenant_operator_page", "lease_summary"],
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

    assert m51["peer_requirement_count"] >= 4
    assert m51["peer_candidate_family_count"] >= 3
    assert m51["comparison_blocker_count"] >= 1
    assert m51["comparison_not_yet_valid_count"] == 1
    assert any(row["comparison_status"] == "blocked" for row in m51["peer_requirement_register"])
    assert "Do not compare this warehouse" in m51["comparison_not_yet_valid_register"][0]["explanation"]
