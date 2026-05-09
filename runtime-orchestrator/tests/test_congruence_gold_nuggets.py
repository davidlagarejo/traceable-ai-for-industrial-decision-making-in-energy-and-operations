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
        "motor_028": {"source_register": []},
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


def test_building_skill_gold_nuggets_follow_building_patterns_without_warehouse_contamination():
    out = _run(_building_inputs())

    skill_nuggets = out["skill_gold_nugget_register"]
    themes = {row["nugget_theme"] for row in skill_nuggets}
    nugget_text = " ".join(row["gold_nugget"].lower() for row in skill_nuggets)

    assert out["gold_nugget_authority_state"] == "skill_primary"
    assert out["authoritative_gold_nugget_register"] == skill_nuggets
    assert "controls_or_schedule" in themes
    assert "boundary_leakage" in themes
    assert "model_prematurity" in themes
    assert "charging drives peak demand" not in nugget_text
    assert "logistics interface" not in nugget_text
    assert "service-level intensity and charging profile" not in nugget_text


def test_manufacturing_skill_gold_nuggets_follow_process_and_power_quality_patterns():
    out = _run(_manufacturing_inputs())

    skill_nuggets = out["skill_gold_nugget_register"]
    themes = {row["nugget_theme"] for row in skill_nuggets}
    nugget_text = " ".join(row["gold_nugget"].lower() for row in skill_nuggets)

    assert out["gold_nugget_authority_state"] == "skill_primary"
    assert out["authoritative_gold_nugget_register"] == skill_nuggets
    assert "process_dominance" in themes
    assert "tariff_orchestration" in themes
    assert "support_utility_loss" in themes
    assert "model_prematurity" in themes
    assert "maintenance_hidden_value" in themes or "maintenance_reality" in themes
    assert "compressed air" in nugget_text or "power factor" in nugget_text
    assert "digital twin" in nugget_text or "do not model" in nugget_text
    assert "charging drives peak demand" not in nugget_text
    assert "logistics interface" not in nugget_text


def test_building_gold_nuggets_survive_target_not_yet_operationally_bounded():
    inputs = _building_inputs()
    inputs["motor_007"]["target_classification_object"] = {
        "target_type": "REGISTERED_AGENT_OR_MAILING_ADDRESS",
        "classification_confidence": "medium",
    }
    out = _run(inputs)

    nuggets = out["strategic_gold_nugget_register"]
    assert nuggets
    nugget_text = " ".join(row["gold_nugget"].lower() for row in nuggets)
    assert "visible question may be premature" in nugget_text or "wrong measurement instinct" in nugget_text
    assert out["congruence_action_priority_register"]


def test_gold_nugget_strength_register_carries_theme_and_priority_scoring():
    out = _run(_manufacturing_inputs())

    strength_rows = out["gold_nugget_strength_register"]
    assert strength_rows
    assert all(row["nugget_theme"] for row in strength_rows)
    assert all("selection_priority_score" in row for row in strength_rows)
    assert all("cross_layer_breadth_score" in row for row in strength_rows)
    assert strength_rows == sorted(
        strength_rows,
        key=lambda row: (
            -int(row.get("selection_priority_score", 0) or 0),
            -int(row.get("cross_layer_breadth_score", 0) or 0),
            str(row.get("nugget_id", "")),
        ),
    )
    assert any(row["strength_label"] in {"strong", "deep_strategic"} for row in strength_rows)
