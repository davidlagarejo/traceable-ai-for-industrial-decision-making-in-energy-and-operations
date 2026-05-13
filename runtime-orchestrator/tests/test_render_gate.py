"""V6 P9 — CLIENT_SAFE_MODE render gate tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.claim_synchronization_auditor import (
    audit_claim_synchronization,
)
from runtime_orchestrator.fallback_policy import (
    FallbackEvent,
    assess,
)
from runtime_orchestrator.qa_score import build_qa_score_card
from runtime_orchestrator.render_gate import (
    RenderGateRefusal,
    RenderGateVerdict,
    enforce_render_gate,
    evaluate_render_gate,
    strict_mode_active,
)
from runtime_orchestrator.source_execution_auditor import (
    audit_source_execution,
)


# ── strict_mode_active resolution ──────────────────────────────────


def test_strict_mode_default_is_on(monkeypatch):
    monkeypatch.delenv("ZLAB_RENDER_STRICT_DEFAULT", raising=False)
    assert strict_mode_active() is True


def test_strict_mode_env_can_disable(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "0")
    assert strict_mode_active() is False


def test_strict_mode_pipeline_override_wins(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    assert strict_mode_active({"__render_strict_default__": False}) is False
    assert strict_mode_active({"__render_soft_mode__": True}) is False


# ── happy path: every gate green ───────────────────────────────────


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


def test_strict_mode_allows_render_when_everything_green(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    card = _clean_qa_card()
    assert card.client_safe is True
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=card,
        fallback_verdict={"prohibited_count": 0},
        source_audit=audit_source_execution(routing_plan_compliance={}),
        claim_sync=audit_claim_synchronization(),
        isolation_violations=[],
    )
    assert verdict.allowed is True
    assert verdict.strict_mode is True
    assert verdict.reasons == ()


# ── strict mode refuses when QA score not client_safe ──────────────


def test_strict_mode_refuses_when_qa_not_client_safe(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    bad_card = build_qa_score_card(
        motor_061_summary={"contamination_count": 9, "cross_family_violations": 5,
                           "blocking_violations": 6},
        motor_063_summary={"blocking_violations": 4},
        fallback_verdict={"prohibited_count": 3},
        motor_019_lint={"orphan_claim_findings": ["x", "y"]},
    )
    assert bad_card.client_safe is False
    verdict = evaluate_render_gate(state="client_safe", qa_card=bad_card)
    assert verdict.allowed is False
    assert any("client_safe=False" in r for r in verdict.reasons)


# ── strict mode refuses publishable but not "client_safe" state ────


def test_strict_mode_refuses_publish_bounded_state(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    card = _clean_qa_card()
    verdict = evaluate_render_gate(state="publish_bounded", qa_card=card)
    assert verdict.allowed is False
    assert any("publish_bounded" in r for r in verdict.reasons)


def test_soft_mode_allows_publish_bounded_state(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "0")
    card = _clean_qa_card()
    verdict = evaluate_render_gate(
        state="publish_bounded",
        qa_card=card,
        fallback_verdict={"prohibited_count": 0},
        claim_sync=audit_claim_synchronization(),
    )
    assert verdict.allowed is True
    assert verdict.strict_mode is False


# ── individual gate refusals ───────────────────────────────────────


def test_prohibited_fallback_refuses_render_in_strict(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    card = _clean_qa_card()
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=card,
        fallback_verdict={"prohibited_count": 2},
    )
    assert verdict.allowed is False
    assert verdict.no_prohibited_fallback is False


def test_unjustified_source_refuses_render(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    card = _clean_qa_card()
    source = audit_source_execution(
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
        state="client_safe", qa_card=card, source_audit=source,
    )
    assert verdict.allowed is False
    assert verdict.no_unjustified_sources is False


def test_claim_sync_divergence_refuses_render(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    card = _clean_qa_card()
    sync = audit_claim_synchronization(
        motor_014_output={"inference_records": [{"case_id": "CL-1"}, {"case_id": "CL-2"}]},
        motor_034_output={"claim_permission_register": [{"claim_name": "CL-1"}]},
    )
    verdict = evaluate_render_gate(
        state="client_safe", qa_card=card, claim_sync=sync,
    )
    assert verdict.allowed is False
    assert verdict.claims_in_sync is False


def test_isolation_violations_refuse_render(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    card = _clean_qa_card()
    verdict = evaluate_render_gate(
        state="client_safe", qa_card=card,
        isolation_violations=[{"pattern_id": "refrigeration_duty",
                                "target_family": "datacenter",
                                "reason": "forbidden_family"}],
    )
    assert verdict.allowed is False
    assert verdict.no_isolation_violations is False


# ── enforce_render_gate raises ─────────────────────────────────────


def test_enforce_render_gate_raises_when_refused(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    with pytest.raises(RenderGateRefusal):
        enforce_render_gate(
            state="publish_bounded",
            qa_card=_clean_qa_card(),
        )


def test_enforce_render_gate_returns_verdict_on_pass(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    verdict = enforce_render_gate(
        state="client_safe", qa_card=_clean_qa_card(),
    )
    assert isinstance(verdict, RenderGateVerdict)
    assert verdict.allowed is True


# ── verdict as_dict for downstream telemetry ───────────────────────


def test_verdict_as_dict_includes_all_diagnostic_flags(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(state="client_safe", qa_card=_clean_qa_card())
    d = v.as_dict()
    for key in (
        "allowed", "strict_mode", "state", "reasons",
        "qa_client_safe", "state_in_allowed",
        "no_prohibited_fallback", "no_unjustified_sources",
        "claims_in_sync", "no_isolation_violations",
    ):
        assert key in d
