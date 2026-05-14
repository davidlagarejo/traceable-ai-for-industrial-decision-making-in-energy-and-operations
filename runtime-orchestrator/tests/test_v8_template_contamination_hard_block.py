"""V8 P1 — template_contamination_failure hard block via render_gate.

V8 Chief QA Architect § Error 1: el flag se detecta en motor_016
case_adaptation_memo pero el render gate no lo bloquea. Hoy llega a
'publish_with_degradation' cuando debería ser internal_debug_only.

V8 P1 doctrine: template contamination es hard block en AMBOS modos
(soft + strict). Bypass sólo vía
pipeline_inputs.__template_contamination_force_render__ = True (debug).
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.render_gate import (
    RenderGateRefusal,
    enforce_render_gate,
    evaluate_render_gate,
)


def _clean_qa_card():
    from runtime_orchestrator.qa_score import build_qa_score_card
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


# ── strict mode + template contamination ──────────────────────────


def test_template_contamination_refuses_in_strict_mode(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        template_contamination_failure=True,
    )
    assert verdict.allowed is False
    assert verdict.no_template_contamination is False
    assert any("template_contamination_failure" in r for r in verdict.reasons)


# ── soft mode + template contamination ────────────────────────────


def test_template_contamination_refuses_in_soft_mode_too(monkeypatch):
    """V8 P1: template contamination es hard block en AMBOS modos."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "0")
    verdict = evaluate_render_gate(
        state="publish_bounded",  # soft mode tolera estados no-client_safe
        template_contamination_failure=True,
    )
    assert verdict.allowed is False
    assert verdict.strict_mode is False
    assert verdict.no_template_contamination is False


# ── no contamination → clean run ─────────────────────────────────


def test_no_template_contamination_allows_render(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        template_contamination_failure=False,
    )
    assert verdict.allowed is True
    assert verdict.no_template_contamination is True


def test_default_argument_is_no_contamination(monkeypatch):
    """Backward compat: callers que no pasan el arg new no rompen."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        # template_contamination_failure omitted → defaults to False
    )
    assert verdict.no_template_contamination is True
    assert verdict.allowed is True


# ── force-render bypass (debug only) ──────────────────────────────


def test_force_template_render_bypasses_block(monkeypatch):
    """Operators can opt out by passing the explicit force flag."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "0")
    verdict = evaluate_render_gate(
        state="exploratory_prior",  # in soft DEFAULT_ALLOWED_RENDER_STATES
        template_contamination_failure=True,
        pipeline_inputs={"__template_contamination_force_render__": True},
    )
    # The verdict no_template_contamination still reflects the raw signal
    # but the gate allows render because the bypass was explicit.
    assert verdict.no_template_contamination is False
    # With bypass and no other contamination, gate allows in soft mode.
    assert verdict.allowed is True


# ── enforce_render_gate raises ───────────────────────────────────


def test_enforce_raises_on_template_contamination(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    with pytest.raises(RenderGateRefusal):
        enforce_render_gate(
            state="client_safe",
            qa_card=_clean_qa_card(),
            template_contamination_failure=True,
        )


# ── as_dict includes new diagnostic flag ─────────────────────────


def test_verdict_dict_includes_template_flag(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(state="client_safe", qa_card=_clean_qa_card())
    d = v.as_dict()
    assert "no_template_contamination" in d
    assert d["no_template_contamination"] is True
