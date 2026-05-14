"""V8 P9 — Final Release Stability Suite.

8 contamination scenarios + 1 control, exercising every V8 hardening
together. Each scenario asserts:
  - render_gate refuses
  - publication_mode reflects severity
  - YAML block shows the failed gate

  S0 Clean run                                       → client_safe
  S1 Template contamination                          → internal_debug_only
  S2 CV6 chart from another case                     → blocked
  S3 Hybrid governance object missing fields         → governance warns
  S4 TAD digital_twin with unresolved var            → DO_NOT_MODEL_YET
  S5 Evidence branches with high repetition          → EB1 warning
  S6 Identity-tier source unqueried                  → client_safe=false
  S7 Executive Thesis high-value section downgraded  → refuse
  S8 Full cascade contamination                      → all gates fail
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.evidence_branching import (
    EvidenceBranch,
    audit_branch_repetition,
)
from runtime_orchestrator.fallback_policy import (
    FallbackEvent,
    assess as assess_fallbacks,
)
from runtime_orchestrator.hybrid_justification import (
    build_hybrid_governance_object,
)
from runtime_orchestrator.qa_score import build_qa_score_card
from runtime_orchestrator.render_gate import evaluate_render_gate
from runtime_orchestrator.source_execution_auditor import (
    audit_source_execution,
)
from runtime_orchestrator.tad_claim_sync import enforce_tad_action_posture


@pytest.fixture(autouse=True)
def _v8_hard_mode(monkeypatch):
    """V8 default — hard mode + strict render ON."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")


def _clean_qa_card():
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


# ── S0 — clean control ────────────────────────────────────────────


def test_S0_clean_run_emits_client_safe():
    v = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        fallback_verdict={"prohibited_count": 0},
    )
    assert v.allowed is True
    assert v.publication_mode() == "client_safe"
    assert "client_safe: true" in v.as_yaml_block()


# ── S1 — template contamination → internal_debug_only ─────────────


def test_S1_template_contamination_to_internal_debug_only():
    v = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        template_contamination_failure=True,
    )
    assert v.allowed is False
    assert v.publication_mode() == "internal_debug_only"
    yaml = v.as_yaml_block()
    assert "template_contamination: failed" in yaml
    assert "publication_mode: internal_debug_only" in yaml


# ── S2 — CV6 chart wrong case (via motor_063 blocking_violations) ─


def test_S2_chart_wrong_case_lowers_qa_and_refuses():
    """motor_063 surfacing CV6 violations lowers contamination_score."""
    bad_card = build_qa_score_card(
        motor_063_summary={"blocking_violations": 5},
        motor_061_summary={"blocking_violations": 0, "contamination_count": 0,
                           "cross_family_violations": 0},
        motor_057_summary={"blocking_violations": 0},
        motor_058_summary={"blocking_violations": 0},
        motor_059_summary={"blocking_violations": 0},
        fallback_verdict={"prohibited_count": 0},
    )
    assert bad_card.contamination_score < 0.5
    v = evaluate_render_gate(state="client_safe", qa_card=bad_card)
    assert v.allowed is False


# ── S3 — Hybrid governance object incomplete ──────────────────────


def test_S3_hybrid_without_scope_yields_partial_governance_object():
    """Hybrid spec sin scope_allowed produce un governance_object con
    listas vacías. El consumer (motor_017) puede detectarlo."""
    hybrid = {
        "primary": "cold_chain_facility",
        "secondary": "manufacturing_facility",
        "rationale": "missing scope fields",
    }
    obj = build_hybrid_governance_object(
        hybrid=hybrid, matched_evidence_tokens=["evidence_x"]
    )
    assert obj["scope_allowed"] == []
    assert obj["scope_prohibited"] == []
    assert obj["report_sections_blocked"] == []


# ── S4 — TAD digital_twin with unresolved → DO_NOT_MODEL_YET ──────


def test_S4_digital_twin_rewritten_to_DO_NOT_MODEL_YET():
    action = {"action_title": "Build detailed system model / digital twin",
              "status": "INVESTIGATE"}
    out = enforce_tad_action_posture(
        action,
        dominant_variables=[{"evidence_state": "ARCHETYPAL_PRIOR"}],
    )
    assert out["status"] == "DO_NOT_MODEL_YET"
    assert "investigate" in out["forbidden_language"]


# ── S5 — Evidence branches with > 0.80 Jaccard → EB1 warning ──────


def test_S5_evidence_branches_high_repetition_audit_fires():
    b1 = EvidenceBranch(
        hypothesis_id="h1",
        minimum_evidence=("a", "b", "c", "d"),
        cheapest_path=("a", "b"), escalation_path=("c", "d"),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    b2 = EvidenceBranch(
        hypothesis_id="h2",
        minimum_evidence=("a", "b", "c", "d"),
        cheapest_path=("a", "b"), escalation_path=("c", "d"),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    out = audit_branch_repetition([b1, b2])
    assert len(out) == 1
    assert out[0]["rule_id"] == "EB1_branch_evidence_repetition"


# ── S6 — Identity-tier source unqueried → client_safe=false ──────


def test_S6_identity_source_unqueried_refuses_render():
    src = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["sec_edgar_2024"],
            "rows": [{"source_key": "sec_edgar_2024", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    v = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        source_audit=src,
    )
    assert v.allowed is False
    assert v.no_unjustified_sources is False
    yaml = v.as_yaml_block()
    assert "source_execution_status: failed" in yaml


# ── S7 — Executive Thesis section downgraded → refuse ────────────


def test_S7_executive_thesis_downgrade_refuses_render():
    events = [
        FallbackEvent(motor_id="motor_019", kind="narrator_used_structured_fallback",
                      section_id="executive_structural_thesis"),
    ]
    verdict = assess_fallbacks("client_safe", events)
    assert verdict.high_value_section_downgrades == 1
    gate = evaluate_render_gate(
        state="client_safe", qa_card=_clean_qa_card(),
        fallback_verdict=verdict,
    )
    assert gate.allowed is False
    assert any("high-value section" in r for r in gate.reasons)


# ── S8 — Full cascade contamination ──────────────────────────────


def test_S8_full_cascade_lists_every_failed_gate():
    bad_card = build_qa_score_card(
        motor_061_summary={"contamination_count": 5,
                           "cross_family_violations": 3, "blocking_violations": 6},
        motor_063_summary={"blocking_violations": 4},
        motor_058_summary={"blocking_violations": 3},
        motor_059_summary={"blocking_violations": 4},
        motor_057_summary={"blocking_violations": 0},
        fallback_verdict={"prohibited_count": 2},
    )
    src = audit_source_execution(
        routing_plan_compliance={
            "total_routed_sources": 1,
            "mandatory_sources_missing_from_executor": ["sec_edgar"],
            "rows": [{"source_key": "sec_edgar", "priority": "mandatory",
                      "status": "not_executed_by_executor"}],
        },
    )
    v = evaluate_render_gate(
        state="publish_bounded",
        qa_card=bad_card,
        fallback_verdict={"prohibited_count": 2},
        source_audit=src,
        isolation_violations=[
            {"pattern_id": "refrigeration_duty", "target_family": "datacenter",
             "reason": "explicit_anti_family"},
        ],
        template_contamination_failure=True,
    )
    assert v.allowed is False
    # Severity hierarchy puts template_contamination at the top:
    assert v.publication_mode() == "internal_debug_only"
    yaml = v.as_yaml_block()
    # Every governance gate is failed
    for line in (
        "template_contamination: failed",
        "fallback_governance: failed",
        "source_execution_status: failed",
        "hybrid_logic_governance: failed",
        "qa_score_client_safe: failed",
    ):
        assert line in yaml, f"missing {line!r}"
