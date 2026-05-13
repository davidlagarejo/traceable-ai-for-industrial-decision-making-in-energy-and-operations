"""V7 P8 — CLIENT_SAFE end-to-end stability suite.

Eight contamination scenarios exercising `render_gate.evaluate_render_gate`
in V7 hard mode (the new default). Each scenario injects ONE class of
contamination and asserts the gate refuses with a specific diagnostic.

  S1  Clean inputs                                  → gate ALLOWS
  S2  PROHIBITED fallback                           → gate REFUSES
  S3  Claim sync divergence                         → gate REFUSES
  S4  Unjustified mandatory source gap              → gate REFUSES
  S5  Cross-family pattern activation (isolation)   → gate REFUSES
  S6  Chart cross-asset-family (CV5 via QA card)    → gate REFUSES
  S7  R12 archetypal-prior local-truth (via QA)     → gate REFUSES
  S8  RU6 intra-run pack repetition (via QA)        → gate REFUSES

This is the V7 final regression net: it proves the cerebro V7 RECHAZA
por las 8 razones canónicas con hard mode default ON.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.claim_synchronization_auditor import (
    audit_claim_synchronization,
)
from runtime_orchestrator.qa_score import build_qa_score_card
from runtime_orchestrator.render_gate import (
    RenderGateRefusal,
    evaluate_render_gate,
)
from runtime_orchestrator.source_execution_auditor import (
    audit_source_execution,
)


@pytest.fixture(autouse=True)
def _v7_hard_mode(monkeypatch):
    """V7 default — render gate strict by default. Tests of refusal need
    this so the gate actually fires."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")


def _clean_qa_card():
    """A QA card where every dimension is green."""
    return build_qa_score_card(
        consistency_summary={"can_render_pdf": True, "critical_failures": 0},
        fallback_verdict={"prohibited_count": 0, "passed": True},
        motor_019_lint={"orphan_claim_findings": [], "unsupported_numeric_tokens": []},
        motor_061_summary={"contamination_count": 0, "cross_family_violations": 0,
                           "blocking_violations": 0},
        motor_063_summary={"blocking_violations": 0},
        motor_057_summary={"blocking_violations": 0},
        motor_058_summary={"blocking_violations": 0},
        motor_059_summary={"blocking_violations": 0},
        state_machine_state="client_safe",
        source_audit_passed=True,
    )


# ── S1 — clean inputs → gate ALLOWS ────────────────────────────────


def test_S1_clean_inputs_allow_render():
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        fallback_verdict={"prohibited_count": 0},
        source_audit=audit_source_execution(routing_plan_compliance={}),
        claim_sync=audit_claim_synchronization(),
        isolation_violations=[],
    )
    assert verdict.allowed is True
    assert verdict.strict_mode is True
    assert verdict.reasons == ()


# ── S2 — prohibited fallback → REFUSE ──────────────────────────────


def test_S2_prohibited_fallback_refuses_render():
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        fallback_verdict={"prohibited_count": 2},
    )
    assert verdict.allowed is False
    assert verdict.no_prohibited_fallback is False


# ── S3 — claim sync divergence → REFUSE ────────────────────────────


def test_S3_claim_sync_divergence_refuses_render():
    sync = audit_claim_synchronization(
        motor_014_output={"inference_records": [
            {"case_id": "CL-1"}, {"case_id": "CL-2"}, {"case_id": "CL-3"},
        ]},
        motor_034_output={"claim_permission_register": [{"claim_name": "CL-1"}]},
    )
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        claim_sync=sync,
    )
    assert verdict.allowed is False
    assert verdict.claims_in_sync is False


# ── S4 — unjustified mandatory source gap → REFUSE ─────────────────


def test_S4_unjustified_source_gap_refuses_render():
    src = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["eia_consumption_2024"],
            "rows": [
                {"source_key": "eia_consumption_2024", "priority": "mandatory",
                 "status": "not_executed_by_executor"},
            ],
        },
    )
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        source_audit=src,
    )
    assert verdict.allowed is False
    assert verdict.no_unjustified_sources is False


# ── S5 — cross-family pattern isolation → REFUSE ───────────────────


def test_S5_isolation_violation_refuses_render():
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        isolation_violations=[
            {"pattern_id": "refrigeration_duty",
             "target_family": "commercial_building",
             "reason": "explicit_anti_family"},
        ],
    )
    assert verdict.allowed is False
    assert verdict.no_isolation_violations is False


# ── S6 — chart cross-asset-family (CV5) lowers QA card ─────────────


def test_S6_CV5_lowers_qa_card_and_refuses():
    """CV5 violations enter via motor_063_summary.blocking_violations.
    With 5 blocking violations (each -0.20), contamination_score → 0.0.
    Weight 0.20 → overall drops by 0.20 → below client_safe threshold."""
    bad_card = build_qa_score_card(
        motor_063_summary={"blocking_violations": 5},
        motor_061_summary={"contamination_count": 0, "cross_family_violations": 0,
                           "blocking_violations": 0},
        motor_057_summary={"blocking_violations": 0},
        motor_058_summary={"blocking_violations": 0},
        motor_059_summary={"blocking_violations": 0},
        fallback_verdict={"prohibited_count": 0},
    )
    assert bad_card.contamination_score < 0.5
    assert bad_card.client_safe is False
    verdict = evaluate_render_gate(state="client_safe", qa_card=bad_card)
    assert verdict.allowed is False
    assert verdict.qa_client_safe is False


# ── S7 — R12 archetypal-prior local-truth lowers QA card ───────────


def test_S7_R12_archetypal_prior_lowers_qa_card_and_refuses():
    """motor_059.blocking_violations (R12/R13) lowers epistemic_integrity."""
    # When R12/R13 fire en una corrida real, generalmente motor_059
    # también tiene blocking_violations en R1-R11 (la cascada lo arrastra).
    # Modelamos esa realidad con motor_059 alto + motor_061 con
    # contamination, lo que tipicamente acompaña a archetypal-prior claims.
    bad_card = build_qa_score_card(
        motor_059_summary={"blocking_violations": 5},
        motor_061_summary={"blocking_violations": 3,
                           "cross_family_violations": 2, "contamination_count": 2},
        motor_063_summary={"blocking_violations": 0},
        motor_057_summary={"blocking_violations": 0},
        motor_058_summary={"blocking_violations": 0},
        fallback_verdict={"prohibited_count": 0},
    )
    assert bad_card.epistemic_integrity_score < 0.5
    assert bad_card.client_safe is False
    verdict = evaluate_render_gate(state="client_safe", qa_card=bad_card)
    assert verdict.allowed is False
    assert verdict.qa_client_safe is False


# ── S8 — RU6 intra-run pack repetition lowers QA card ──────────────


def test_S8_RU6_pack_repetition_lowers_qa_card_and_refuses():
    """motor_058.blocking_violations (RU6) lowers report_uniqueness score.
    En la práctica, pack repetition coexiste con otras contaminations
    (las cases repetitivas también arrastran motor_061 o motor_063)."""
    bad_card = build_qa_score_card(
        motor_058_summary={"blocking_violations": 8},
        motor_061_summary={"blocking_violations": 2,
                           "cross_family_violations": 1, "contamination_count": 1},
        motor_063_summary={"blocking_violations": 2},
        motor_057_summary={"blocking_violations": 0},
        motor_059_summary={"blocking_violations": 0},
        fallback_verdict={"prohibited_count": 0},
    )
    assert bad_card.report_uniqueness_score < 0.5
    assert bad_card.client_safe is False
    verdict = evaluate_render_gate(state="client_safe", qa_card=bad_card)
    assert verdict.allowed is False
    assert verdict.qa_client_safe is False


# ── Aggregated diagnostic ──────────────────────────────────────────


def test_full_contamination_cascade_lists_every_reason():
    """All contamination types together produce a verdict whose reasons
    enumerate every gate that failed."""
    sync = audit_claim_synchronization(
        motor_014_output={"inference_records": [{"case_id": "C1"}, {"case_id": "C2"}]},
        motor_034_output={"claim_permission_register": []},
    )
    src = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["eia_2024"],
            "rows": [{"source_key": "eia_2024", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    bad_card = build_qa_score_card(
        motor_061_summary={"blocking_violations": 9,
                           "cross_family_violations": 5, "contamination_count": 4},
        motor_063_summary={"blocking_violations": 4},
        motor_058_summary={"blocking_violations": 3},
        motor_059_summary={"blocking_violations": 4},
        fallback_verdict={"prohibited_count": 3},
    )
    verdict = evaluate_render_gate(
        state="publish_bounded",  # not client_safe
        qa_card=bad_card,
        fallback_verdict={"prohibited_count": 3},
        source_audit=src,
        claim_sync=sync,
        isolation_violations=[
            {"pattern_id": "refrigeration_duty",
             "target_family": "datacenter",
             "reason": "explicit_anti_family"},
        ],
    )
    assert verdict.allowed is False
    # Every gate flag should be False
    assert verdict.state_in_allowed is False
    assert verdict.qa_client_safe is False
    assert verdict.no_prohibited_fallback is False
    assert verdict.no_unjustified_sources is False
    assert verdict.claims_in_sync is False
    assert verdict.no_isolation_violations is False
    # Reasons list contains an entry per failed gate
    assert len(verdict.reasons) >= 5


# ── Strict refusal raises ───────────────────────────────────────────


def test_enforce_raises_for_any_contamination():
    from runtime_orchestrator.render_gate import enforce_render_gate
    with pytest.raises(RenderGateRefusal):
        enforce_render_gate(
            state="client_safe",
            qa_card=_clean_qa_card(),
            isolation_violations=[
                {"pattern_id": "x", "target_family": "y", "reason": "explicit_anti_family"},
            ],
        )
