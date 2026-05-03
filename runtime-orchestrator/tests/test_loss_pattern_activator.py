from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter


def _field(field: str, value, *, source_id: str | None = None) -> dict:
    return {
        "field": field,
        "value": value,
        "status": "OBSERVED",
        "source_id": source_id or f"test::{field}",
        "scope": "ASSET_LEVEL",
        "authority_score": "high",
        "recency": "current",
        "admissibility": "CONFIRMED_ASSET_LEVEL",
        "notes": "",
    }


def _warehouse_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "warehouse_distribution",
                "target_name": "Sunrise Logistics Hub",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution"}},
            "asset_field_register": [_field("asset_class", "warehouse_distribution")],
        },
        "motor_028": {
            "source_register": [],
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
                {"need_id": "warehouse_subtype_classification", "discovery_need": "Confirm warehouse subtype."},
                {"need_id": "dock_and_service_intensity", "discovery_need": "Bound dock density and service-level intensity."},
                {"need_id": "operator_boundary_and_control", "discovery_need": "Confirm tenant / operator boundary and who controls docks, charging, and schedules."},
                {"need_id": "mhe_charging_and_mechanical_clues", "discovery_need": "Look for motive-power charging and roof/HVAC/mechanical clues."},
                {"need_id": "utility_territory_and_tariff_context", "discovery_need": "Confirm utility territory and tariff context."},
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


def _manufacturing_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "TEMPLE, TX",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "manufacturing_facility"}},
            "asset_field_register": [_field("asset_class", "manufacturing_facility")],
        },
        "motor_028": {"source_register": []},
    }


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    return Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})


def test_warehouse_loss_pattern_activator_emits_relevant_subset_and_discrimination_logic():
    out = _run(_warehouse_inputs())

    pattern_names = {row["pattern_name"] for row in out["loss_pattern_hypothesis_register"]}
    assert "dock_infiltration_and_door_discipline_plausible" in pattern_names
    assert "high_bay_lighting_waste_plausible" in pattern_names
    assert "rooftop_hvac_degradation_plausible" in pattern_names
    assert "forklift_charging_and_demand_spike_plausible" in pattern_names
    assert "poor_submetering_and_boundary_visibility_plausible" in pattern_names
    assert "schedule_and_idle_conditioning_waste_plausible" in pattern_names
    assert "door_discipline_breakdown_plausible" in pattern_names

    discrimination = {row["pattern_name"]: row for row in out["pattern_discrimination_register"]}
    dock = discrimination["dock_infiltration_and_door_discipline_plausible"]
    assert dock["what_confirms"]
    assert dock["what_falsifies"]
    assert dock["tad_action"] == "VALIDATE_LOSS_PATTERN"

    activated = {row["pattern_name"]: row for row in out["activated_pattern_register"]}
    assert activated["forklift_charging_and_demand_spike_plausible"]["tad_action"] == "VALIDATE_TARIFF_EXPOSURE"

    for row in out["loss_pattern_hypothesis_register"]:
        assert row["evidence_state"] != "OBSERVED_FACT"
        assert "Do not state that the site has this loss" in row["prohibited_language"]


def test_manufacturing_loss_pattern_activator_preserves_anti_hallucination_and_maintenance_lane():
    out = _run(_manufacturing_inputs())

    pattern_names = {row["pattern_name"] for row in out["loss_pattern_hypothesis_register"]}
    assert "compressed_air_leakage_or_pressure_overuse_plausible" in pattern_names
    assert "thermal_combustion_and_recovery_losses_plausible" in pattern_names
    assert "demand_pf_or_reactive_exposure_plausible" in pattern_names
    assert "poor_lubrication_or_reactive_maintenance_plausible" in pattern_names

    pattern_rows = {row["pattern_name"]: row for row in out["loss_pattern_hypothesis_register"]}
    maintenance_row = pattern_rows["poor_lubrication_or_reactive_maintenance_plausible"]
    assert maintenance_row["what_confirms"]
    assert maintenance_row["what_falsifies"]
    assert maintenance_row["tad_action"] == "VALIDATE_MAINTENANCE_REALITY"
