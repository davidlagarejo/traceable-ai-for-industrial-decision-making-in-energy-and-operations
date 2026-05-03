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


def _building_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
            },
            "target_classification_object": {"target_type": "OPERATING_ASSET", "classification_confidence": "high"},
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "commercial_building"}},
            "asset_field_register": [_field("asset_class", "commercial_building")],
        },
        "motor_028": {"source_register": []},
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


def test_motor_052_building_emits_bounded_control_and_schedule_loss_hypotheses():
    out = _run(_building_inputs())

    patterns = {row["pattern_name"]: row for row in out["loss_pattern_hypothesis_register"]}
    assert "schedule_and_after_hours_waste_plausible" in patterns
    assert "missing_control_boundary_visibility" in patterns
    assert patterns["schedule_and_after_hours_waste_plausible"]["pattern_class"] == "structural_pattern"
    assert "Do not state that the site has this loss" in patterns["schedule_and_after_hours_waste_plausible"]["prohibited_language"]


def test_motor_052_manufacturing_emits_compressed_air_thermal_and_pf_patterns():
    out = _run(_manufacturing_inputs())

    pattern_names = {row["pattern_name"] for row in out["loss_pattern_hypothesis_register"]}
    assert "compressed_air_leakage_or_pressure_overuse_plausible" in pattern_names
    assert "thermal_combustion_and_recovery_losses_plausible" in pattern_names
    assert "demand_pf_or_reactive_exposure_plausible" in pattern_names
