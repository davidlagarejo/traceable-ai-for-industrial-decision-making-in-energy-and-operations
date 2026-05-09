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


def test_expanded_strategic_tad_engine_emits_multi_action_warehouse_register():
    out = _run(_warehouse_inputs())

    actions = {row["strategic_action"] for row in out["expanded_tad_action_register"]}
    assert "BUILD_FAIR_PEER_SET" in actions
    assert "VALIDATE_TARIFF_EXPOSURE" in actions
    assert "VALIDATE_CONTROL_BOUNDARY" in actions
    assert "VALIDATE_LOSS_PATTERN" in actions
    assert "DO_NOT_MODEL_YET" in actions
    assert "DO_NOT_SENSOR_YET" in actions
    assert "DO_NOT_INVEST_YET" in actions
    assert "PROHIBIT_CLAIM" in actions
    skill_actions = {row["strategic_action"] for row in out["skill_expanded_tad_action_register"]}
    assert "BUILD_FAIR_PEER_SET" in skill_actions
    assert "VALIDATE_TARIFF_EXPOSURE" in skill_actions
    assert "VALIDATE_CONTROL_BOUNDARY" in skill_actions
    assert "DO_NOT_MODEL_YET" in skill_actions
    assert "DO_NOT_SENSOR_YET" in skill_actions
    assert out["tad_authority_state"] == "skill_primary"

    by_action = {row["strategic_action"]: row for row in out["expanded_tad_action_register"]}
    assert by_action["BUILD_FAIR_PEER_SET"]["evidence_needed"]
    assert "peer superiority" in by_action["BUILD_FAIR_PEER_SET"]["prohibited_action"].lower()
    assert "digital twin" in by_action["DO_NOT_MODEL_YET"]["prohibited_action"].lower()
    assert by_action["VALIDATE_TARIFF_EXPOSURE"]["trigger"]
    assert by_action["VALIDATE_TARIFF_EXPOSURE"]["decision_front"] == "VALIDATE DEMAND / TARIFF EXPOSURE"
    assert by_action["VALIDATE_TARIFF_EXPOSURE"]["trigger_family"] == "tariff_or_demand"
    assert by_action["VALIDATE_CONTROL_BOUNDARY"]["evidence_pack_family"] == "control_boundary_pack"
    assert by_action["DO_NOT_INVEST_YET"]["prohibited_action_class"] == "capex_underwriting_block"


def test_prohibited_action_register_tracks_expanded_actions():
    out = _run(_warehouse_inputs())
    assert out["prohibited_action_count"] == len(out["prohibited_action_register"])
    assert any(row["strategic_action"] == "PROHIBIT_CLAIM" for row in out["prohibited_action_register"])
    assert out["skill_combination_review_count"] >= 1
    assert out["authoritative_tad_action_count"] == len(out["authoritative_tad_action_register"])
