from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter


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
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
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
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "manufacturing_facility"}},
            "asset_field_register": [_field("asset_class", "manufacturing_facility")],
        },
        "motor_028": {"source_register": []},
    }


def _warehouse_inputs() -> dict:
    return {
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "500 DISTRIBUTION LOOP, DALLAS, TX 75001",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "warehouse_distribution_asset",
                "target_name": "Regional distribution warehouse",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution_asset"}},
            "asset_field_register": [_field("asset_class", "warehouse_distribution_asset")],
        },
        "motor_028": {"source_register": []},
    }


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    return Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})


def test_motor_051_requires_control_boundary_for_building_peer_logic():
    out = _run(_building_inputs())

    risk_names = {row["risk_name"] for row in out["invalid_comparison_risk_register"]}
    assert "whole_building_owner_capturable_comparison" in risk_names
    dimensions = {row["normalization_dimension"] for row in out["normalization_requirements_register"]}
    assert "owner_tenant_control_boundary" in dimensions


def test_motor_051_fails_manufacturing_area_comparison_without_throughput_normalization():
    out = _run(_manufacturing_inputs())

    rows = {row["peer_frame"]: row for row in out["comparison_validity_register"]}
    assert rows["area_based_energy_intensity_comparison"]["comparable"] is False
    assert "throughput by shift" in rows["area_based_energy_intensity_comparison"]["normalization_required"]


def test_motor_051_fails_logistics_area_comparison_without_service_level_normalization():
    out = _run(_warehouse_inputs())

    rows = {row["peer_frame"]: row for row in out["comparison_validity_register"]}
    assert rows["warehouse_area_only_comparison"]["comparable"] is False
    assert "service level" in " ".join(rows["warehouse_area_only_comparison"]["normalization_required"]).lower()
