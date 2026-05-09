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
            "facility_prior": {"target_definition": {"target_type": "warehouse_distribution", "jurisdiction_scope": ["US-TX"]}},
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


def test_gold_nugget_generator_emits_five_to_eight_case_specific_warehouse_nuggets():
    out = _run(_warehouse_inputs())

    nuggets = out["gold_nugget_register"]
    skill_nuggets = out["skill_gold_nugget_register"]
    assert 5 <= len(nuggets) <= 8
    assert len(out["gold_nugget_strength_register"]) == len(nuggets)
    assert any("wrong denominator" in row["gold_nugget"].lower() for row in nuggets)
    assert any("tariff design problem" in row["gold_nugget"].lower() for row in nuggets)
    assert any("leak across the boundary" in row["gold_nugget"].lower() for row in nuggets)

    for row in nuggets:
        assert row["evidence_state"]
        assert row["what_to_do_next"]
        assert row["minimum_evidence"]
        assert row["tad_action"]
    assert 3 <= len(skill_nuggets) <= 5
    assert out["gold_nugget_authority_state"] == "skill_primary"
    assert out["authoritative_gold_nugget_register"] == skill_nuggets
    assert any("wrong denominator" in row["gold_nugget"].lower() for row in skill_nuggets)
    assert any("tariff orchestration problem" in row["gold_nugget"].lower() for row in skill_nuggets)
    assert any("value may leak" in row["gold_nugget"].lower() for row in skill_nuggets)
    skill_nugget_ids = {row["nugget_id"] for row in skill_nuggets}
    assert "pattern_fair_comparison_invalid_area_metric" in skill_nugget_ids
    assert "pattern_warehouse_mhe_charging_demand_peak" in skill_nugget_ids
    assert "pattern_value_boundary_leakage_owner_operator" in skill_nugget_ids


def test_gold_nugget_strength_register_marks_strong_nuggets_when_multiple_lanes_align():
    out = _run(_warehouse_inputs())

    strength_by_id = {row["nugget_id"]: row for row in out["gold_nugget_strength_register"]}
    candidate_rows = [row for row in out["gold_nugget_register"] if row["nugget_id"].startswith("candidate_")]
    assert candidate_rows
    assert any(
        strength_by_id[row["nugget_id"]]["strength_label"] in {"strong", "deep_strategic"}
        for row in candidate_rows
    )
    assert any(
        row["validator_state"] == "passed"
        for row in out["skill_gold_nugget_register"]
    )
    assert any(
        row["nugget_theme"] == "model_prematurity"
        for row in out["skill_gold_nugget_register"]
    )
