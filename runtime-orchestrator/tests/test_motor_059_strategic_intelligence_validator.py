"""Tests for motor_059 — Strategic Intelligence Validator."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_059 import Motor059Adapter


def _run(motor_033=None, motor_038=None, motor_054=None):
    adapter = Motor059Adapter()
    return adapter.run(
        {
            "motor_033": motor_033 or {},
            "motor_038": motor_038 or {},
            "motor_054": motor_054 or {},
        }
    )


def test_no_inputs_returns_empty_warnings():
    out = _run()
    assert out["warning_count"] == 0
    assert out["strategic_intelligence_warnings"] == []
    assert "R1_missing_falsification" in out["rules_evaluated"]


def test_r1_flags_allowed_claim_without_falsification():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "claim_x",
                    "permission": "allowed",
                    "falsification_condition": "",
                }
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R1_missing_falsification" in rule_ids


def test_r1_does_not_flag_prohibited_claims():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "claim_x",
                    "permission": "prohibited",
                    "falsification_condition": "",
                }
            ]
        }
    )
    assert out["warning_count"] == 0


def test_r1_does_not_flag_when_falsification_present():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "claim_x",
                    "permission": "allowed",
                    "falsification_condition": "Asset evidence proves frame is wrong.",
                }
            ]
        }
    )
    assert out["warning_count"] == 0


def test_r2_flags_act_now_with_prohibited_claim():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {
                    "action": "Request discriminating evidence pack",
                    "status": "ACT NOW",
                    "linked_claim": "claim_y",
                }
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "claim_y", "permission": "prohibited"}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R2_act_now_with_prohibited_claim" in rule_ids


def test_r2_does_not_flag_act_now_with_allowed_claim():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {
                    "action": "Request discriminating evidence pack",
                    "status": "ACT NOW",
                    "linked_claim": "claim_y",
                }
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "claim_y",
                    "permission": "allowed",
                    "falsification_condition": "test",
                }
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R2_act_now_with_prohibited_claim" not in rule_ids


def test_r3_flags_do_not_model_with_concurrent_redesign_act_now():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {
                    "action": "Build detailed system model / digital twin",
                    "status": "DO NOT MODEL YET",
                },
                {
                    "action": "Advance bounded redesign hypothesis",
                    "status": "ACT NOW",
                },
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R3_do_not_model_with_active_redesign" in rule_ids
    info_warning = next(
        w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R3_do_not_model_with_active_redesign"
    )
    assert info_warning["severity"] == "info"
    assert "Advance bounded redesign hypothesis" in info_warning["concurrent_act_now_actions"]


def test_r3_silent_when_only_do_not_model():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {
                    "action": "Build detailed system model / digital twin",
                    "status": "DO NOT MODEL YET",
                }
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R3_do_not_model_with_active_redesign" not in rule_ids


def test_r4_flags_observed_fact_without_evidence():
    out = _run(
        motor_038={
            "dominant_variable_register": [
                {"variable": "owner_control_boundary", "evidence_state": "OBSERVED_FACT"}
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R4_observed_fact_without_evidence" in rule_ids


def test_r4_does_not_flag_when_evidence_attached():
    out = _run(
        motor_038={
            "dominant_variable_register": [
                {
                    "variable": "owner_control_boundary",
                    "evidence_state": "OBSERVED_FACT",
                    "supporting_evidence": ["lease_agreement_2024"],
                }
            ]
        }
    )
    assert out["warning_count"] == 0


def test_r4_does_not_flag_conditional_hypothesis_without_evidence():
    out = _run(
        motor_038={
            "dominant_variable_register": [
                {
                    "variable": "throughput",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ]
        }
    )
    assert out["warning_count"] == 0


def test_severity_breakdown_in_output():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "falsification_condition": ""}
            ]
        },
        motor_033={
            "expanded_structural_tad_action_register": [
                {
                    "action": "Build detailed system model / digital twin",
                    "status": "DO NOT MODEL YET",
                },
                {"action": "Advance bounded redesign hypothesis", "status": "ACT NOW"},
            ]
        },
    )
    assert out["warning_count_by_severity"]["warning"] >= 1  # R1
    assert out["warning_count_by_severity"]["info"] >= 1  # R3


def test_rules_evaluated_is_stable_list():
    out = _run()
    assert out["rules_evaluated"] == [
        "R1_missing_falsification",
        "R2_act_now_with_prohibited_claim",
        "R3_do_not_model_with_active_redesign",
        "R4_observed_fact_without_evidence",
    ]
