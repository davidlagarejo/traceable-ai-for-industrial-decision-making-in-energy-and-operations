"""Tests for V3 G16: motor_057 enforces nugget count 5-12.

Adds GN4_nugget_count_out_of_range. Below 5 or above 12 (defaults) →
severity=critical. Thresholds configurable via
__pipeline__.nugget_count_thresholds.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_057 import Motor057Adapter


def _run(motor_054=None, pipeline=None):
    return Motor057Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "manufacturing_facility"}},
        "motor_054": motor_054 or {},
        "__pipeline__": pipeline or {},
    })


def _nuggets(count: int) -> list[dict]:
    return [
        {"nugget_id": f"n{i}", "gold_nugget": f"Nugget {i} text that is sufficiently descriptive to pass thin-nugget threshold and provide value."}
        for i in range(count)
    ]


# ── below minimum ───────────────────────────────────────────────────────


def test_below_minimum_5_fires_gn4_critical():
    out = _run(motor_054={"strategic_gold_nugget_register": _nuggets(3)})
    gn4 = [w for w in out["gold_nugget_quality_warnings"] if w["rule_id"] == "GN4_nugget_count_out_of_range"]
    assert len(gn4) == 1
    assert gn4[0]["severity"] == "critical"
    assert gn4[0]["nugget_count"] == 3
    assert gn4[0]["min_required"] == 5
    assert "below the minimum" in gn4[0]["description"]


def test_zero_nuggets_fires_gn4_critical():
    out = _run(motor_054={"strategic_gold_nugget_register": []})
    gn4 = [w for w in out["gold_nugget_quality_warnings"] if w["rule_id"] == "GN4_nugget_count_out_of_range"]
    assert len(gn4) == 1


# ── above maximum ───────────────────────────────────────────────────────


def test_above_maximum_12_fires_gn4_critical():
    out = _run(motor_054={"strategic_gold_nugget_register": _nuggets(15)})
    gn4 = [w for w in out["gold_nugget_quality_warnings"] if w["rule_id"] == "GN4_nugget_count_out_of_range"]
    assert len(gn4) == 1
    assert gn4[0]["nugget_count"] == 15
    assert gn4[0]["max_allowed"] == 12
    assert "above the maximum" in gn4[0]["description"]


# ── in-range ─────────────────────────────────────────────────────────────


def test_in_range_5_to_12_silent():
    for count in (5, 6, 8, 10, 12):
        out = _run(motor_054={"strategic_gold_nugget_register": _nuggets(count)})
        rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
        assert "GN4_nugget_count_out_of_range" not in rule_ids, f"GN4 should be silent at count={count}"


# ── configurable thresholds ─────────────────────────────────────────────


def test_pipeline_can_widen_max_threshold():
    out = _run(
        motor_054={"strategic_gold_nugget_register": _nuggets(20)},
        pipeline={"nugget_count_thresholds": {"min": 5, "max": 30}},
    )
    rule_ids = [w["rule_id"] for w in out["gold_nugget_quality_warnings"]]
    assert "GN4_nugget_count_out_of_range" not in rule_ids


def test_pipeline_can_tighten_min_threshold():
    out = _run(
        motor_054={"strategic_gold_nugget_register": _nuggets(7)},
        pipeline={"nugget_count_thresholds": {"min": 10, "max": 12}},
    )
    gn4 = [w for w in out["gold_nugget_quality_warnings"] if w["rule_id"] == "GN4_nugget_count_out_of_range"]
    assert len(gn4) == 1
    assert gn4[0]["min_required"] == 10


# ── Output schema ───────────────────────────────────────────────────────


def test_output_surfaces_thresholds():
    out = _run(
        motor_054={"strategic_gold_nugget_register": _nuggets(7)},
        pipeline={"nugget_count_thresholds": {"min": 5, "max": 12}},
    )
    assert out["nugget_count_evaluated"] == 7
    assert out["nugget_count_min"] == 5
    assert out["nugget_count_max"] == 12
    assert "GN4_nugget_count_out_of_range" in out["rules_evaluated"]
