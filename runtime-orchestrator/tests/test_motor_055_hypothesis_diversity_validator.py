"""Tests for motor_055 — Hypothesis Diversity Validator."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_055 import Motor055Adapter


def _run(motor_033=None, motor_054=None):
    adapter = Motor055Adapter()
    return adapter.run({"motor_033": motor_033 or {}, "motor_054": motor_054 or {}})


def test_no_inputs_flags_low_diversity():
    out = _run()
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD1_low_claim_count" in rule_ids


def test_hd1_quiet_with_two_allowed_claims():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "claim_family": "f1", "current_evidence_summary": "a"},
                {"claim_id": "c2", "permission": "allowed", "claim_family": "f2", "current_evidence_summary": "b"},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD1_low_claim_count" not in rule_ids


def test_hd2_flags_duplicate_signatures():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "claim_family": "denominator", "current_evidence_summary": "area_normalized"},
                {"claim_id": "c2", "permission": "allowed", "claim_family": "denominator", "current_evidence_summary": "area_normalized"},
                {"claim_id": "c3", "permission": "allowed", "claim_family": "tariff", "current_evidence_summary": "charging"},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD2_duplicate_claim_signature" in rule_ids


def test_hd2_quiet_with_distinct_signatures():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "claim_family": "f1", "current_evidence_summary": "a"},
                {"claim_id": "c2", "permission": "allowed", "claim_family": "f2", "current_evidence_summary": "b"},
            ]
        }
    )
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD2_duplicate_claim_signature" not in rule_ids


def test_hd3_flags_when_all_actions_target_same_claim():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "A1", "status": "ACT NOW", "linked_claim": "c1"},
                {"action": "A2", "status": "VALIDATE FIRST", "linked_claim": "c1"},
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "claim_family": "f1", "current_evidence_summary": "a"},
                {"claim_id": "c2", "permission": "allowed", "claim_family": "f2", "current_evidence_summary": "b"},
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD3_tad_action_convergence" in rule_ids


def test_hd3_quiet_when_actions_target_different_claims():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "A1", "status": "ACT NOW", "linked_claim": "c1"},
                {"action": "A2", "status": "ACT NOW", "linked_claim": "c2"},
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "claim_family": "f1", "current_evidence_summary": "a"},
                {"claim_id": "c2", "permission": "allowed", "claim_family": "f2", "current_evidence_summary": "b"},
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD3_tad_action_convergence" not in rule_ids


def test_hd3_silent_when_only_one_actionable():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "A1", "status": "ACT NOW", "linked_claim": "c1"},
                {"action": "A2", "status": "INVESTIGATE", "linked_claim": "c1"},  # not actionable
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "allowed", "claim_family": "f1", "current_evidence_summary": "a"},
                {"claim_id": "c2", "permission": "allowed", "claim_family": "f2", "current_evidence_summary": "b"},
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["hypothesis_diversity_warnings"]]
    assert "HD3_tad_action_convergence" not in rule_ids


def test_rules_evaluated_stable():
    out = _run()
    assert out["rules_evaluated"] == [
        "HD1_low_claim_count",
        "HD2_duplicate_claim_signature",
        "HD3_tad_action_convergence",
    ]
