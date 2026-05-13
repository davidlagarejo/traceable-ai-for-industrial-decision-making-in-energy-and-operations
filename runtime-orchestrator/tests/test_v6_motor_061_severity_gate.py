"""V6 P4.1 — motor_061 integration with validator_severity_policy."""
from __future__ import annotations

import os

import pytest

from runtime_orchestrator.adapters.motor_061 import Motor061Adapter


_ENV = "ZLAB_VALIDATORS_HARD_BLOCK"


def _inputs_with_contamination(*, hard_mode: bool = False) -> dict:
    """Build a minimal motor_061 input set that triggers AF1 pattern contamination.

    Scenario: a cold_chain case where a combination activates patterns that
    belong to manufacturing (process_load_vs_waste, etc).
    """
    pipeline_inputs = {}
    if hard_mode:
        pipeline_inputs["__validators_hard_block__"] = True
    return {
        "__pipeline__": pipeline_inputs,
        "motor_007": {
            "target_definition_contract": {"target_type": "cold_chain_facility"},
        },
        "motor_054": {
            "skill_combination_activation_register": [
                {
                    "combination_id": "test_contaminating_combo",
                    "pattern_ids": [
                        "process_load_vs_waste",        # manufacturing pattern
                        "boiler_degradation_plausibility",  # also manufacturing
                    ],
                },
            ],
            "strategic_gold_nugget_register": [],
        },
    }


def _inputs_clean() -> dict:
    """Build a minimal motor_061 input set with NO contamination."""
    return {
        "motor_007": {
            "target_definition_contract": {"target_type": "cold_chain_facility"},
        },
        "motor_054": {
            "skill_combination_activation_register": [],
            "strategic_gold_nugget_register": [],
        },
    }


# ── soft mode (regression default) — severity unchanged ─────────────


def test_soft_mode_keeps_severity_critical(monkeypatch):
    """In soft mode, motor_061 must emit severity='critical' exactly as before."""
    monkeypatch.delenv(_ENV, raising=False)
    out = Motor061Adapter().run(_inputs_with_contamination())
    warnings = out["asset_family_isolation_warnings"]
    assert len(warnings) > 0
    # ALL contamination findings should retain critical severity
    assert all(w["severity"] == "critical" for w in warnings), [
        (w["rule_id"], w["severity"]) for w in warnings
    ]
    assert out["critical_count"] > 0
    assert out["blocking_violations"] == 0  # not promoted in soft mode


# ── hard mode (V6) — AF1 promoted to blocking ──────────────────────


def test_hard_mode_env_promotes_to_blocking(monkeypatch):
    """When ZLAB_VALIDATORS_HARD_BLOCK=1, AF1 contamination becomes blocking."""
    monkeypatch.setenv(_ENV, "1")
    out = Motor061Adapter().run(_inputs_with_contamination())
    warnings = out["asset_family_isolation_warnings"]
    assert len(warnings) > 0
    af1 = [w for w in warnings if w["rule_id"] == "AF1_pattern_contamination"]
    assert af1, "AF1 contamination should be detected"
    assert all(w["severity"] == "blocking" for w in af1)
    assert out["blocking_violations"] > 0
    # critical_count drops because the AF1 findings flipped to blocking
    assert out["critical_count"] == 0


def test_hard_mode_pipeline_override_promotes(monkeypatch):
    """Pipeline-level __validators_hard_block__=True activates the gate."""
    monkeypatch.delenv(_ENV, raising=False)
    out = Motor061Adapter().run(_inputs_with_contamination(hard_mode=True))
    af1 = [w for w in out["asset_family_isolation_warnings"]
           if w["rule_id"] == "AF1_pattern_contamination"]
    assert af1
    assert all(w["severity"] == "blocking" for w in af1)


# ── clean case — no contamination either mode ──────────────────────


def test_clean_case_soft_mode_zero_contamination(monkeypatch):
    monkeypatch.delenv(_ENV, raising=False)
    out = Motor061Adapter().run(_inputs_clean())
    assert out["contamination_detected"] is False
    assert out["blocking_violations"] == 0
    assert out["critical_count"] == 0


def test_clean_case_hard_mode_zero_contamination(monkeypatch):
    monkeypatch.setenv(_ENV, "1")
    out = Motor061Adapter().run(_inputs_clean())
    assert out["contamination_detected"] is False
    assert out["blocking_violations"] == 0


# ── V6 QA-score consumer fields ────────────────────────────────────


def test_motor_061_exposes_v6_fields_for_qa_score():
    """motor_061 output must expose blocking_violations, warning_violations,
    cross_family_violations, contamination_count for qa_score consumer."""
    out = Motor061Adapter().run(_inputs_clean())
    for field in ("blocking_violations", "warning_violations",
                   "cross_family_violations", "contamination_count"):
        assert field in out, f"motor_061 missing V6 field: {field}"


def test_motor_061_v6_field_values_match_warnings():
    """V6 counts must reconcile with the actual warnings list."""
    out = Motor061Adapter().run(_inputs_with_contamination())
    warnings = out["asset_family_isolation_warnings"]
    expected_cross_family = sum(
        1 for w in warnings if w["rule_id"] == "AF1_pattern_contamination"
    )
    expected_contamination = sum(
        1 for w in warnings if w["rule_id"] == "AF2_nugget_token_contamination"
    )
    assert out["cross_family_violations"] == expected_cross_family
    assert out["contamination_count"] == expected_contamination
