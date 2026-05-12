"""Tests for V3 G2: motor_059 governance sync rules R5/R6/R7 + R2/R3 promoted to error.

R5 — chart visually supports a prohibited claim
R6 — gold nugget implies peer superiority while fair_comparison blocks it
R7 — claim counts diverge across claim_register / TAD-linked / governance_summary
R2 — TAD ACT NOW + prohibited claim — now severity=error (was warning)
R3 — DO NOT MODEL + active redesign — now severity=error (was informational)
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_059 import Motor059Adapter


def _run(**overrides) -> dict:
    base = {
        "motor_016": {},
        "motor_018": {},
        "motor_033": {},
        "motor_038": {},
        "motor_051": {},
        "motor_054": {},
    }
    base.update(overrides)
    return Motor059Adapter().run(base)


# ── R5: chart implies prohibited claim ──────────────────────────────────


def test_r5_chart_binding_to_prohibited_claim_emits_error():
    out = _run(
        motor_018={
            "chart_assets": [
                {
                    "chart_id": "CHT-001",
                    "intelligence_binding": {"claim_id": "claim_alpha"},
                }
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "claim_alpha", "permission": "prohibited"}
            ]
        },
    )
    r5 = [w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R5_chart_implies_prohibited_claim"]
    assert len(r5) == 1
    assert r5[0]["severity"] == "error"
    assert r5[0]["chart_id"] == "CHT-001"
    assert r5[0]["linked_claim"] == "claim_alpha"


def test_r5_silent_when_chart_binds_to_allowed_claim():
    out = _run(
        motor_018={
            "chart_assets": [
                {"chart_id": "CHT-002", "intelligence_binding": {"claim_id": "claim_beta"}}
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "claim_beta", "permission": "allowed"}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R5_chart_implies_prohibited_claim" not in rule_ids


def test_r5_handles_hypothesis_anchor_binding():
    """Charts can bind to hypothesis_id or thesis_anchor too — all flagged
    if pointing to a prohibited claim_id."""
    out = _run(
        motor_018={
            "chart_assets": [
                {"chart_id": "CHT-003", "intelligence_binding": {"hypothesis_id": "claim_gamma"}}
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "claim_gamma", "permission": "prohibited"}
            ]
        },
    )
    r5 = [w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R5_chart_implies_prohibited_claim"]
    assert len(r5) == 1


# ── R6: nugget superiority when fair_comparison blocked ─────────────────


def test_r6_superiority_language_when_blocked_emits_error():
    out = _run(
        motor_051={"peer_superiority_blocked": True},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "N-001", "gold_nugget": "This site outperforms its peers in energy intensity."}
            ]
        },
    )
    r6 = [w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R6_nugget_implies_superiority_when_blocked"]
    assert len(r6) == 1
    assert r6[0]["severity"] == "error"
    assert r6[0]["marker"] == "outperforms"


def test_r6_silent_when_fair_comparison_not_blocked():
    out = _run(
        motor_051={"peer_superiority_blocked": False},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "N-002", "gold_nugget": "This site outperforms peers."}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R6_nugget_implies_superiority_when_blocked" not in rule_ids


def test_r6_silent_when_nuggets_have_no_superiority_language():
    out = _run(
        motor_051={"peer_superiority_blocked": True},
        motor_054={
            "strategic_gold_nugget_register": [
                {"nugget_id": "N-003", "gold_nugget": "Refrigeration duty composition is the deciding question."}
            ]
        },
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R6_nugget_implies_superiority_when_blocked" not in rule_ids


# ── R7: claim count mismatch ────────────────────────────────────────────


def test_r7_count_divergence_emits_error():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": f"c{i}", "permission": "conditional"} for i in range(5)
            ]
        },
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "X", "linked_claim": "c0"},
                {"action": "Y", "linked_claim": "c1"},
            ]
        },
        motor_016={
            "report_package": {"governance_summary": {"governed_claim_contract_count": 10}}
        },
    )
    # 5 / 2 / 10 — diverge > 1
    r7 = [w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R7_claim_count_mismatch_across_layers"]
    assert len(r7) == 1
    assert r7[0]["severity"] == "error"
    assert r7[0]["claim_layer_count"] == 5
    assert r7[0]["tad_linked_count"] == 2
    assert r7[0]["governance_count"] == 10


def test_r7_silent_when_counts_within_tolerance():
    """Tolerance of 1 — 4 / 4 / 5 should NOT fire."""
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": f"c{i}", "permission": "conditional"} for i in range(4)
            ]
        },
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": f"A{i}", "linked_claim": f"c{i}"} for i in range(4)
            ]
        },
        motor_016={
            "report_package": {"governance_summary": {"governed_claim_contract_count": 5}}
        },
    )
    rule_ids = [w["rule_id"] for w in out["strategic_intelligence_warnings"]]
    assert "R7_claim_count_mismatch_across_layers" not in rule_ids


# ── R2/R3: promoted to error ─────────────────────────────────────────────


def test_r2_act_now_with_prohibited_claim_is_error_in_v3():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "Capital Reallocation", "status": "ACT NOW", "linked_claim": "c1"}
            ]
        },
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "permission": "prohibited"}
            ]
        },
    )
    r2 = [w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R2_act_now_with_prohibited_claim"]
    assert len(r2) == 1
    assert r2[0]["severity"] == "error"


def test_r3_do_not_model_with_active_redesign_is_error_in_v3():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action": "Build detailed system model / digital twin", "status": "DO NOT MODEL YET"},
                {"action": "Advance bounded redesign hypothesis", "status": "ACT NOW"},
            ]
        }
    )
    r3 = [w for w in out["strategic_intelligence_warnings"] if w["rule_id"] == "R3_do_not_model_with_active_redesign"]
    assert len(r3) >= 1
    assert all(w["severity"] == "error" for w in r3)


# ── Output schema ───────────────────────────────────────────────────────


def test_rules_evaluated_lists_all_7_rules():
    out = _run()
    assert out["rules_evaluated"] == [
        "R1_missing_falsification",
        "R2_act_now_with_prohibited_claim",
        "R3_do_not_model_with_active_redesign",
        "R4_observed_fact_without_evidence",
        "R5_chart_implies_prohibited_claim",
        "R6_nugget_implies_superiority_when_blocked",
        "R7_claim_count_mismatch_across_layers",
    ]


def test_severity_counts_aggregated():
    out = _run(
        motor_018={
            "chart_assets": [{"chart_id": "X", "intelligence_binding": {"claim_id": "c1"}}]
        },
        motor_054={
            "congruence_claim_contract_register": [{"claim_id": "c1", "permission": "prohibited"}]
        },
    )
    assert out["warning_count_by_severity"]["error"] >= 1
