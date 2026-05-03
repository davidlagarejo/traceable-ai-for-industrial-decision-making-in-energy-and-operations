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


def test_motor_052_building_prefers_bills_maps_and_bms_before_new_hardware():
    out = _run(_building_inputs())

    hypotheses = {row["hypothesis"]: row for row in out["measurement_strategy_register"]}
    assert "owner_vs_tenant_control_boundary_drives_the_case" in hypotheses
    assert "tenant metering map" in hypotheses["owner_vs_tenant_control_boundary_drives_the_case"]["minimum_measurement"]
    assert out["power_quality_hypothesis_register"] == []
    assert out["leakage_hypothesis_register"] == []


def test_motor_052_manufacturing_considers_bills_and_tariff_before_analyzer():
    out = _run(_manufacturing_inputs())

    pq = out["power_quality_hypothesis_register"]
    assert len(pq) == 1
    assert pq[0]["measurement_priority"] == "bills_first_then_targeted_analyzer_if_material"
    measurement_rows = {row["hypothesis"]: row for row in out["measurement_strategy_register"]}
    assert "power_quality_or_pf_exposure_is_material" in measurement_rows
    hardware_rows = {row["data_need"]: row for row in out["hardware_minimality_register"]}
    assert hardware_rows["power_quality_or_pf_exposure_is_material"]["cheapest_valid_source"] == "utility bills / tariff records"
    assert "temporary analyzer only if needed" in measurement_rows["power_quality_or_pf_exposure_is_material"]["minimum_measurement"]


def test_motor_052_leakage_hypotheses_only_appear_when_family_and_subsystems_justify_them():
    manufacturing = _run(_manufacturing_inputs())
    building = _run(_building_inputs())

    assert manufacturing["leakage_hypothesis_count"] > 0
    assert building["leakage_hypothesis_register"] == []
