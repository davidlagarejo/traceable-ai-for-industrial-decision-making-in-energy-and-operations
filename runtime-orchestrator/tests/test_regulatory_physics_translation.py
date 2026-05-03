from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter


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
            "facility_prior": {"target_definition": {"target_type": "commercial_building", "jurisdiction_scope": ["US-NY-NYC"]}},
            "asset_field_register": [_field("asset_class", "commercial_building")],
        },
        "motor_028": {
            "source_register": [
                {"source_id": "ll84::site", "source_family": "benchmarking_disclosure_record", "title": "LL84"},
                {"source_id": "climate::site", "source_family": "climate_normals_record", "title": "Climate"},
            ]
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
            "facility_prior": {"target_definition": {"target_type": "manufacturing_facility", "jurisdiction_scope": ["US-TX"]}},
            "asset_field_register": [_field("asset_class", "manufacturing_facility")],
        },
        "motor_028": {
            "source_register": [
                {"source_id": "permit::site", "source_family": "permit_record", "title": "Permit"},
                {"source_id": "reg::site", "source_family": "regulatory_coverage_record", "title": "Reg coverage"},
            ]
        },
    }


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    return Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})


def test_motor_053_building_translates_ll84_ll97_context_without_claiming_closure():
    out = _run(_building_inputs())

    signals = {row["regulatory_signal"] for row in out["regulatory_physics_register"]}
    assert "NYC benchmarking and building performance obligations" in signals
    permit_rows = out["permit_signal_register"]
    assert permit_rows[0]["implied_physical_domain"] == "whole-building energy and covered-load logic"
    assert "full control-boundary proof" in permit_rows[0]["non_substitutable_for"]


def test_motor_053_manufacturing_translates_permit_context_to_physical_domain_only():
    out = _run(_manufacturing_inputs())

    signals = {row["regulatory_signal"] for row in out["regulatory_physics_register"]}
    assert "Industrial environmental or process permit context" in signals
    constraints = {row["constraint_name"] for row in out["regulatory_constraint_register"]}
    assert "Industrial environmental or process permit context" in constraints
