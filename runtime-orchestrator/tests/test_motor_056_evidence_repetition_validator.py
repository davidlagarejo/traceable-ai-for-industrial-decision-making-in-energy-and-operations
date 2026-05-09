"""Tests for motor_056 — Evidence Repetition Validator."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_056 import Motor056Adapter


def _run(motor_033=None, motor_046=None):
    adapter = Motor056Adapter()
    return adapter.run({"motor_033": motor_033 or {}, "motor_046": motor_046 or {}})


def test_no_inputs_returns_no_warnings():
    out = _run()
    assert out["warning_count"] == 0


def test_er1_flags_pack_used_in_more_than_two_actions():
    pack = "service-level proxy; dock activity profile; charging schedule"
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "A1", "status": "ACT NOW", "evidence_needed": pack},
                {"action": "A2", "status": "VALIDATE FIRST", "evidence_needed": pack},
                {"action": "A3", "status": "REDESIGN HYPOTHESIS", "evidence_needed": pack},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["evidence_repetition_warnings"]]
    assert "ER1_pack_repetition" in rule_ids


def test_er1_quiet_when_pack_appears_at_most_twice():
    pack = "service-level proxy"
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "A1", "status": "ACT NOW", "evidence_needed": pack},
                {"action": "A2", "status": "VALIDATE FIRST", "evidence_needed": pack},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["evidence_repetition_warnings"]]
    assert "ER1_pack_repetition" not in rule_ids


def test_er1_handles_list_evidence_packs():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "A1", "status": "ACT NOW", "evidence_needed": ["service-level proxy", "charging"]},
                {"action": "A2", "status": "ACT NOW", "evidence_needed": ["charging", "service-level proxy"]},
                {"action": "A3", "status": "ACT NOW", "evidence_needed": ["service-level proxy", "charging"]},
            ]
        }
    )
    # Order-insensitive normalization should make these equivalent
    rule_ids = [w["rule_id"] for w in out["evidence_repetition_warnings"]]
    assert "ER1_pack_repetition" in rule_ids


def test_er2_flags_repeated_minimum_measurement():
    out = _run(
        motor_046={
            "minimum_evidence_for_discrimination_register": [
                {"minimum_measurement": "utility bills"},
                {"minimum_measurement": "utility bills"},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["evidence_repetition_warnings"]]
    assert "ER2_minimum_measurement_repetition" in rule_ids


def test_er3_flags_actionable_without_evidence():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "Request data", "status": "ACT NOW", "evidence_needed": ""},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["evidence_repetition_warnings"]]
    assert "ER3_actionable_without_evidence_pack" in rule_ids


def test_er3_silent_for_non_actionable_status():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "Investigate", "status": "INVESTIGATE", "evidence_needed": ""},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["evidence_repetition_warnings"]]
    assert "ER3_actionable_without_evidence_pack" not in rule_ids


def test_rules_evaluated_stable():
    out = _run()
    assert out["rules_evaluated"] == [
        "ER1_pack_repetition",
        "ER2_minimum_measurement_repetition",
        "ER3_actionable_without_evidence_pack",
    ]
