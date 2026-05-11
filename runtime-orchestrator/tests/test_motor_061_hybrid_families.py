"""Tests for motor_061 hybrid asset-family admission (Gap B).

A justified hybrid combination (cold_chain + food_processing, etc.) must
allow its shared_patterns through without flagging them as contamination,
provided the justification trigger is present in evidence tokens. Without
the trigger, the cross-family activation must remain blocked.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_061 import Motor061Adapter


def _run(motor_007=None, motor_054=None):
    adapter = Motor061Adapter()
    return adapter.run({"motor_007": motor_007 or {}, "motor_054": motor_054 or {}})


# ── Hybrid admission: trigger present → contamination cleared ───────────────


def test_cold_chain_food_processing_trigger_admits_process_patterns():
    out = _run(
        motor_007={
            "target_definition_contract": {
                "target_type": "cold_chain_facility",
                "facility_evidence_tokens": ["cook_chill_present"],
            }
        },
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "hybrid_dairy_combo",
                    "pattern_ids": [
                        "refrigeration_duty",
                        "process_load_vs_waste",  # normally manufacturing-only
                        "steam_trap_failure_plausibility",  # normally manufacturing-only
                    ],
                }
            ]
        },
    )
    assert out["hybrid_admissible"] is True
    assert out["hybrid_id"] == "cold_chain_food_processing"
    assert out["hybrid_secondary"] == "manufacturing_facility"
    assert "process_load_vs_waste" in out["hybrid_shared_patterns"]
    assert out["contamination_detected"] is False


def test_warehouse_mixed_temperature_trigger_admits_cold_chain_patterns():
    out = _run(
        motor_007={
            "target_definition_contract": {
                "target_type": "warehouse_distribution",
                "facility_evidence_tokens": ["frozen_zone_present"],
            }
        },
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "mixed_temp_dc",
                    "pattern_ids": [
                        "warehouse_mhe_charging_demand_peak",
                        "cold_chain_status_unknown",
                    ],
                }
            ]
        },
    )
    # cold_chain_status_unknown is NOT in the warehouse contamination set,
    # so contamination is already absent; the hybrid still admits the case.
    assert out["hybrid_admissible"] is True
    assert out["hybrid_id"] == "warehouse_mixed_temperature"
    assert out["contamination_detected"] is False


def test_office_edge_datacenter_hybrid_recognized():
    out = _run(
        motor_007={
            "target_definition_contract": {
                "target_type": "commercial_building",
                "process_evidence_tokens": ["edge_dc_tenant_present"],
            }
        },
        motor_054={"skill_combination_activation_register": []},
    )
    assert out["hybrid_admissible"] is True
    assert out["hybrid_id"] == "office_with_edge_datacenter"


def test_evidence_token_from_industrial_register_works():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "cold_chain_facility"}},
        motor_054={
            "industrial_evidence_register": [
                {"trigger": "sanitation_steam_present", "source": "site_walkthrough"},
            ],
            "skill_combination_activation_register": [
                {
                    "combination_id": "hybrid_meat_combo",
                    "pattern_ids": ["process_load_vs_waste"],
                }
            ],
        },
    )
    assert out["hybrid_admissible"] is True
    assert out["contamination_detected"] is False


# ── No trigger → contamination still blocks ─────────────────────────────────


def test_no_trigger_keeps_cross_family_blocked():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "cold_chain_facility"}},
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "unjustified_cross",
                    "pattern_ids": [
                        "process_load_vs_waste",
                        "boiler_degradation_plausibility",
                    ],
                }
            ]
        },
    )
    assert out["hybrid_admissible"] is False
    assert out["hybrid_id"] == ""
    assert out["contamination_detected"] is True


def test_unrelated_evidence_token_does_not_admit_hybrid():
    out = _run(
        motor_007={
            "target_definition_contract": {
                "target_type": "cold_chain_facility",
                "facility_evidence_tokens": ["high_ceiling_facility"],
            }
        },
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "unjustified_cross",
                    "pattern_ids": ["process_load_vs_waste"],
                }
            ]
        },
    )
    assert out["hybrid_admissible"] is False
    assert out["contamination_detected"] is True


def test_case_insensitive_trigger_match():
    out = _run(
        motor_007={
            "target_definition_contract": {
                "target_type": "cold_chain_facility",
                "facility_evidence_tokens": ["COOK_CHILL_PRESENT"],
            }
        },
        motor_054={
            "skill_combination_activation_register": [
                {"combination_id": "hybrid_x", "pattern_ids": ["process_load_vs_waste"]},
            ]
        },
    )
    assert out["hybrid_admissible"] is True
