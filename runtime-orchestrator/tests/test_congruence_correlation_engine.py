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


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    return Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})


def test_motor_051_detects_regulation_vs_control_mismatch_for_building():
    out = _run(_building_inputs())

    contradictions = {row["contradiction"] for row in out["cross_layer_congruence_register"]}
    assert "Regulation vs control boundary" in contradictions
    problem_frames = {row["apparent_problem"] for row in out["invalid_problem_frame_register"]}
    assert "high_building_energy_means_owner_retrofit_opportunity" in problem_frames


def test_motor_051_detects_finance_and_process_mismatch_for_manufacturing():
    out = _run(_manufacturing_inputs())

    contradictions = {row["contradiction"] for row in out["cross_layer_congruence_register"]}
    assert "Finance framing vs physical dependency" in contradictions
    assert "Benchmark vs process reality" in contradictions


def test_motor_051_detects_power_quality_and_maintenance_correlations_for_manufacturing():
    out = _run(_manufacturing_inputs())

    correlations = {row["correlation"] for row in out["structural_correlation_register"]}
    assert "Inductive support systems + tariff context" in correlations
    assert "Support-system complexity + maintenance dependency" in correlations
