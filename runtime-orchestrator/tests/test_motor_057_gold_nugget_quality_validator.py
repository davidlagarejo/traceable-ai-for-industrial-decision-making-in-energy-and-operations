"""Tests for motor_057 — Gold Nugget Quality Validator."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_057 import Motor057Adapter


def _run(motor_007=None, motor_054=None):
    adapter = Motor057Adapter()
    return adapter.run({"motor_007": motor_007 or {}, "motor_054": motor_054 or {}})


def test_no_inputs_emits_only_gn4_count_violation():
    """V3 G16: GN4 fires when there are 0 nuggets (below the min of 5).
    GN1/GN2/GN3 stay silent. Pre-V3 behavior: warning_count == 0 — now == 1."""
    out = _run()
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert rule_ids == ["GN4_nugget_count_out_of_range"]
    assert out["warning_count"] == 1


def test_gn1_flags_warehouse_nugget_without_family_token():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "warehouse_distribution"}},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "n1", "gold_nugget": "Capital may be misallocated against secondary symptoms instead of the primary economic driver."}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert "GN1_archetype_replay" in rule_ids


def test_gn1_quiet_with_warehouse_specific_token():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "warehouse_distribution"}},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "n1", "gold_nugget": "If charging windows drive peak demand, this is a tariff orchestration problem disguised as energy waste."}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert "GN1_archetype_replay" not in rule_ids


def test_gn2_flags_thin_nugget():
    out = _run(
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "n1", "gold_nugget": "Too short to be useful"}
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert "GN2_thin_nugget" in rule_ids


def test_gn3_flags_template_filled_nuggets():
    out = _run(
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "n1", "gold_nugget": "Area may be the wrong denominator until service level is bounded."},
                {"nugget_id": "n2", "gold_nugget": "Area may be the wrong denominator until charging schedule is bounded."},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert "GN3_template_fill" in rule_ids


def test_unknown_asset_family_skips_gn1():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "unknown_family"}},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "n1", "gold_nugget": "Some nugget without any specific token at all here."}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert "GN1_archetype_replay" not in rule_ids


def test_asset_family_reflected_in_output():
    out = _run(
        motor_007={"target_definition_contract": {"target_type": "manufacturing_facility"}},
        motor_054={"strategic_gold_nugget_register": []},
    )
    assert out["asset_family_evaluated"] == "manufacturing_facility"


def test_rules_evaluated_stable():
    out = _run()
    # V3 G16: GN4 added
    assert out["rules_evaluated"] == [
        "GN1_archetype_replay",
        "GN2_thin_nugget",
        "GN3_template_fill",
        "GN4_nugget_count_out_of_range",
    ]
