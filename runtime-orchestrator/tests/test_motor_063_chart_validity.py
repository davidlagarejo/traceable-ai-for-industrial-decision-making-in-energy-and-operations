"""Tests for motor_063 — Chart Validity Engine."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_063 import Motor063Adapter


def _run(motor_018=None, motor_047=None):
    adapter = Motor063Adapter()
    return adapter.run({"motor_018": motor_018 or {}, "motor_047": motor_047 or {}})


def test_no_inputs_returns_no_warnings():
    out = _run()
    assert out["warning_count"] == 0
    assert out["chart_contamination_detected"] is False


def test_cv1_flags_decorative_risk_chart():
    out = _run(
        motor_018={
            "chart_assets": [
                {
                    "chart_id": "decoration_xyz",
                    "strategic_value_tier": "decorative_risk",
                }
            ],
            "chart_strategic_value_summary": {"decorative_risk_count": 1},
        }
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV1_decorative_risk_chart" in rule_ids


def test_cv1_silent_for_thesis_critical():
    out = _run(
        motor_018={
            "chart_assets": [
                {
                    "chart_id": "good_chart",
                    "strategic_value_tier": "thesis_critical",
                    "intelligence_binding": {"thesis_anchor": "dominant_contradiction_01"},
                }
            ],
            "chart_strategic_value_summary": {"decorative_risk_count": 0},
        }
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV1_decorative_risk_chart" not in rule_ids


def test_cv2_flags_chart_without_binding():
    out = _run(
        motor_018={
            "chart_assets": [
                {"chart_id": "unbound_chart", "strategic_value_tier": "supportive_context"}
            ],
            "chart_strategic_value_summary": {"decorative_risk_count": 0},
        }
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV2_chart_without_intelligence_binding" in rule_ids


def test_cv2_silent_when_binding_present():
    out = _run(
        motor_018={
            "chart_assets": [
                {
                    "chart_id": "bound_chart",
                    "strategic_value_tier": "supportive_context",
                    "intelligence_binding": {"combination_id": "warehouse_tariff_combo"},
                }
            ],
        }
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV2_chart_without_intelligence_binding" not in rule_ids


def test_cv3_flags_high_decorative_ratio_critical():
    out = _run(
        motor_018={
            "chart_assets": [
                {"chart_id": "c1", "strategic_value_tier": "decorative_risk"},
                {"chart_id": "c2", "strategic_value_tier": "decorative_risk"},
                {"chart_id": "c3", "strategic_value_tier": "thesis_critical",
                 "intelligence_binding": {"thesis_anchor": "x"}},
                {"chart_id": "c4", "strategic_value_tier": "thesis_critical",
                 "intelligence_binding": {"thesis_anchor": "y"}},
            ],
            "chart_strategic_value_summary": {"decorative_risk_count": 2},
        }
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    # 2/4 = 0.5 > 0.30 threshold
    assert "CV3_decorative_ratio_critical" in rule_ids
    assert out["chart_contamination_detected"] is True


def test_cv3_silent_when_ratio_below_threshold():
    out = _run(
        motor_018={
            "chart_assets": [
                {"chart_id": "c1", "strategic_value_tier": "decorative_risk"},
                {"chart_id": "c2", "strategic_value_tier": "thesis_critical",
                 "intelligence_binding": {"thesis_anchor": "x"}},
                {"chart_id": "c3", "strategic_value_tier": "thesis_critical",
                 "intelligence_binding": {"thesis_anchor": "y"}},
                {"chart_id": "c4", "strategic_value_tier": "thesis_critical",
                 "intelligence_binding": {"thesis_anchor": "z"}},
                {"chart_id": "c5", "strategic_value_tier": "strategic_support",
                 "intelligence_binding": {"thesis_anchor": "w"}},
            ],
            "chart_strategic_value_summary": {"decorative_risk_count": 1},
        }
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    # 1/5 = 0.2 < 0.30
    assert "CV3_decorative_ratio_critical" not in rule_ids


def test_cv4_flags_no_charts_with_admissible_thesis():
    out = _run(
        motor_018={"chart_assets": []},
        motor_047={"executive_thesis": {"thesis_state": "admissible_structural_thesis"}},
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV4_no_charts_with_admissible_thesis" in rule_ids


def test_cv4_silent_when_thesis_inadmissible():
    out = _run(
        motor_018={"chart_assets": []},
        motor_047={"executive_thesis": {"thesis_state": "inadmissible_thesis"}},
    )
    rule_ids = [w["rule_id"] for w in out["chart_validity_warnings"]]
    assert "CV4_no_charts_with_admissible_thesis" not in rule_ids


def test_total_charts_evaluated_reported():
    out = _run(
        motor_018={
            "chart_assets": [
                {"chart_id": f"c{i}", "strategic_value_tier": "thesis_critical",
                 "intelligence_binding": {"thesis_anchor": "x"}}
                for i in range(5)
            ]
        }
    )
    assert out["total_charts_evaluated"] == 5


def test_rules_evaluated_stable():
    out = _run()
    assert out["rules_evaluated"] == [
        "CV1_decorative_risk_chart",
        "CV2_chart_without_intelligence_binding",
        "CV3_decorative_ratio_critical",
        "CV4_no_charts_with_admissible_thesis",
        "CV5_chart_cross_asset_family",  # V7 P7
        "CV6_chart_wrong_source_case_id",  # V8 P2
    ]
