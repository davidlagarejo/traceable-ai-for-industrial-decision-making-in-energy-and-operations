"""V8 P8 — Final Delivery Gate YAML block tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.qa_score import build_qa_score_card
from runtime_orchestrator.render_gate import (
    RenderGateVerdict,
    evaluate_render_gate,
)


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


# ── publication_mode ──────────────────────────────────────────────


def test_publication_mode_client_safe_when_allowed_and_state_matches(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(state="client_safe", qa_card=_clean_qa_card())
    assert v.publication_mode() == "client_safe"


def test_publication_mode_publish_with_degradation_when_allowed_softer_state(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "0")
    v = evaluate_render_gate(
        state="publish_bounded",
        qa_card=_clean_qa_card(),
        fallback_verdict={"prohibited_count": 0},
    )
    assert v.allowed is True
    assert v.publication_mode() == "publish_with_degradation"


def test_publication_mode_internal_debug_when_template_contamination(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        template_contamination_failure=True,
    )
    assert v.publication_mode() == "internal_debug_only"


def test_publication_mode_blocked_when_isolation_violations(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        isolation_violations=[
            {"pattern_id": "refrigeration_duty",
             "target_family": "datacenter", "reason": "explicit_anti_family"},
        ],
    )
    assert v.publication_mode() == "blocked"


# ── as_yaml_block format ──────────────────────────────────────────


def test_yaml_block_includes_canonical_header(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(state="client_safe", qa_card=_clean_qa_card())
    y = v.as_yaml_block()
    assert y.startswith("final_delivery_gate:")
    assert "client_safe: true" in y
    assert "publication_mode: client_safe" in y
    assert "strict_mode: true" in y
    assert "state: client_safe" in y
    assert "blocking_failures: []" in y


def test_yaml_block_lists_failures_when_refused(monkeypatch):
    """State mismatch alone → publish_with_degradation (other gates green)."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(
        state="publish_bounded",  # not client_safe in strict
        qa_card=_clean_qa_card(),
    )
    y = v.as_yaml_block()
    assert "client_safe: false" in y
    # State-mismatch-only with all other gates green ⇒ publish_with_degradation
    assert "publication_mode: publish_with_degradation" in y
    assert "blocking_failures:" in y
    # The failure mentions the state restriction
    assert "publish_bounded" in y


def test_yaml_block_publication_mode_blocked_when_isolation_violation(monkeypatch):
    """Real contamination ⇒ blocked."""
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(
        state="publish_bounded",
        qa_card=_clean_qa_card(),
        isolation_violations=[
            {"pattern_id": "X", "target_family": "Y", "reason": "explicit_anti_family"},
        ],
    )
    y = v.as_yaml_block()
    assert "publication_mode: blocked" in y


def test_yaml_block_includes_all_required_gates(monkeypatch):
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    v = evaluate_render_gate(state="client_safe", qa_card=_clean_qa_card())
    y = v.as_yaml_block()
    # Required gates per Chief QA Architect prompt § Required output:
    for required in (
        "chart_validation:",
        "tad_claim_sync:",
        "hybrid_logic_governance:",
        "source_execution_status:",
        "template_contamination:",
        "fallback_governance:",
        "qa_score_client_safe:",
    ):
        assert required in y, f"YAML block missing '{required}'"


def test_yaml_block_escapes_reasons():
    """Verdict reasons with special chars don't break YAML format."""
    v = RenderGateVerdict(
        allowed=False, strict_mode=True, state="client_safe",
        reasons=('reason with "quotes" and \nnewline',),
    )
    y = v.as_yaml_block()
    # No raw double-quotes inside the string literal nor newlines
    assert '"reason with' in y
    assert "\nnewline" not in y  # was stripped to space
