"""Tests for motor_061 — Asset Family Isolation Validator."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_061 import Motor061Adapter


def _run(motor_007=None, motor_054=None):
    adapter = Motor061Adapter()
    return adapter.run({"motor_007": motor_007 or {}, "motor_054": motor_054 or {}})


def test_no_inputs_returns_no_warnings():
    out = _run()
    assert out["warning_count"] == 0
    assert out["contamination_detected"] is False


def test_warehouse_clean_no_contamination():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "warehouse_distribution"}},
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "warehouse_tariff_boundary_area_combo",
                    "pattern_ids": [
                        "warehouse_mhe_charging_demand_peak",
                        "value_boundary_leakage_owner_operator",
                        "fair_comparison_invalid_area_metric",
                    ],
                }
            ]
        },
    )
    assert out["contamination_detected"] is False
    assert out["warning_count"] == 0


def test_warehouse_with_manufacturing_pattern_flagged():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "warehouse_distribution"}},
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "leaky_combo",
                    "pattern_ids": [
                        "warehouse_mhe_charging_demand_peak",
                        "process_load_vs_waste",  # manufacturing-only
                        "boiler_degradation_plausibility",  # manufacturing-only
                    ],
                }
            ]
        },
    )
    assert out["contamination_detected"] is True
    rule_ids = [w["rule_id"] for w in out["asset_family_isolation_warnings"]]
    assert "AF1_pattern_contamination" in rule_ids


def test_office_with_warehouse_pattern_flagged():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "commercial_building"}},
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "leaky_combo",
                    "pattern_ids": [
                        "hvac_schedule_drift",
                        "warehouse_mhe_charging_demand_peak",  # warehouse-only
                    ],
                }
            ]
        },
    )
    assert out["contamination_detected"] is True


def test_manufacturing_with_cold_chain_pattern_flagged():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "manufacturing_facility"}},
        motor_054={
            "skill_combination_activation_register": [
                {
                    "combination_id": "leaky_combo",
                    "pattern_ids": [
                        "compressed_air_leak_plausibility",
                        "cold_chain_status_unknown",  # cold-chain-only
                    ],
                }
            ]
        },
    )
    assert out["contamination_detected"] is True


def test_warehouse_with_tenant_token_in_nugget_flagged():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "warehouse_distribution"}},
        motor_054={
            "strategic_gold_nugget_register": [
                {
                    "nugget_id": "n1",
                    "gold_nugget": "Tenant boundary in this warehouse leaves owner ROI ambiguous.",
                }
            ]
        },
    )
    assert out["contamination_detected"] is True
    rule_ids = [w["rule_id"] for w in out["asset_family_isolation_warnings"]]
    assert "AF2_nugget_token_contamination" in rule_ids


def test_office_with_dock_token_in_nugget_flagged():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "commercial_building"}},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "n1", "gold_nugget": "Dock cycles drive after-hours load."}
            ]
        },
    )
    assert out["contamination_detected"] is True


def test_unknown_asset_family_skips_validation():
    """No contamination set defined for unknown families → no warnings."""
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "exotic_family"}},
        motor_054={
            "skill_combination_activation_register": [
                {"combination_id": "foo", "pattern_ids": ["whatever"]}
            ]
        },
    )
    assert out["warning_count"] == 0


def test_rules_evaluated_stable():
    out = _run()
    assert out["rules_evaluated"] == [
        "AF1_pattern_contamination",
        "AF2_nugget_token_contamination",
    ]


def test_activated_combinations_count_reported():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "warehouse_distribution"}},
        motor_054={
            "skill_combination_activation_register": [
                {"combination_id": "c1", "pattern_ids": ["warehouse_mhe_charging_demand_peak"]},
                {"combination_id": "c2", "pattern_ids": ["fair_comparison_invalid_area_metric"]},
            ]
        },
    )
    assert out["activated_combinations_count"] == 2
