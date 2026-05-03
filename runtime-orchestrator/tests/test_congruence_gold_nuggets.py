from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter
from runtime_orchestrator.adapters.motor_054 import Motor054Adapter


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


def _run(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})
    return Motor054Adapter().run({
        **inputs,
        "motor_049": m49,
        "motor_050": m50,
        "motor_051": m51,
        "motor_052": m52,
        "motor_053": m53,
    })


def test_motor_054_emits_wrong_problem_and_wrong_measurement_gold_nuggets():
    out = _run(_building_inputs())

    nugget_ids = {row["nugget_id"] for row in out["strategic_gold_nugget_register"]}
    assert "wrong_problem_frame" in nugget_ids
    assert "wrong_measurement_instinct" in nugget_ids


def test_motor_054_emits_bounded_congruence_action_priority():
    out = _run(_building_inputs())

    actions = {row["strategic_action"] for row in out["congruence_action_priority_register"]}
    assert "REQUEST_MINIMUM_EVIDENCE" in actions
    assert "REQUEST_FAIR_PEER_SET" in actions
    assert len(out["congruence_action_priority_register"]) <= 5
