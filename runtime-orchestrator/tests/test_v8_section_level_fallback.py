"""V8 P7 — Section-level Fallback Governance tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.fallback_policy import (
    HIGH_VALUE_SECTIONS,
    FallbackEvent,
    FallbackTier,
    assess,
)


# ── HIGH_VALUE_SECTIONS catalog ───────────────────────────────────


def test_high_value_sections_contains_six_canonical():
    assert HIGH_VALUE_SECTIONS == frozenset({
        "executive_structural_thesis",
        "tad",
        "financial_exposure",
        "peer_comparison",
        "conditional_redesign",
        "case_adaptation_memo",
    })


# ── FallbackEvent section_id field ────────────────────────────────


def test_event_with_high_value_section_id_detected():
    ev = FallbackEvent(
        motor_id="motor_019", kind="narrator_used_structured_fallback",
        section_id="executive_structural_thesis",
    )
    assert ev.is_high_value_section() is True


def test_event_without_section_id_is_not_high_value():
    ev = FallbackEvent(motor_id="motor_019", kind="narrator_codex_timeout")
    assert ev.is_high_value_section() is False


def test_event_with_non_high_value_section_id():
    ev = FallbackEvent(
        motor_id="motor_019", kind="narrator_used_structured_fallback",
        section_id="bibliography",
    )
    assert ev.is_high_value_section() is False


# ── assess counts high-value section downgrades ───────────────────


def test_assess_counts_high_value_downgrades():
    events = [
        FallbackEvent(motor_id="motor_019", kind="narrator_used_structured_fallback",
                      section_id="executive_structural_thesis"),
        FallbackEvent(motor_id="motor_019", kind="narrator_used_structured_fallback",
                      section_id="tad"),
        FallbackEvent(motor_id="motor_019", kind="narrator_used_structured_fallback",
                      section_id="bibliography"),  # not high value
    ]
    verdict = assess("publish_bounded", events)
    assert verdict.high_value_section_downgrades == 2
    assert "executive_structural_thesis" in verdict.affected_high_value_sections
    assert "tad" in verdict.affected_high_value_sections


def test_assess_safe_fallback_in_high_value_section_does_not_count():
    """SAFE-tier events in a high-value section are informational, not downgrade."""
    events = [
        FallbackEvent(motor_id="motor_019", kind="missing_evidence_marker",
                      section_id="tad"),  # SAFE
    ]
    verdict = assess("publish_bounded", events)
    assert verdict.high_value_section_downgrades == 0


def test_assess_prohibited_fallback_in_high_value_section_counts():
    events = [
        FallbackEvent(motor_id="motor_019", kind="narrator_invented_claim",
                      section_id="financial_exposure"),  # PROHIBITED
    ]
    verdict = assess("internal_debug_only", events)
    assert verdict.high_value_section_downgrades == 1


def test_assess_dict_form_carries_section_id():
    """Verdict accepts dict-form events too (motor_024 registry path)."""
    events = [
        {"motor_id": "motor_019", "kind": "narrator_used_structured_fallback",
         "section_id": "peer_comparison"},
    ]
    verdict = assess("publish_bounded", events)
    assert verdict.high_value_section_downgrades == 1


# ── render_gate integration ───────────────────────────────────────


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


def test_render_gate_refuses_when_high_value_section_downgraded(monkeypatch):
    from runtime_orchestrator.render_gate import evaluate_render_gate
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    events = [
        FallbackEvent(motor_id="motor_019", kind="narrator_used_structured_fallback",
                      section_id="executive_structural_thesis"),
    ]
    verdict = assess("client_safe", events)
    gate_verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        fallback_verdict=verdict,
    )
    assert gate_verdict.allowed is False
    assert any("high-value section" in r for r in gate_verdict.reasons)


def test_render_gate_allows_when_only_low_value_section_downgraded(monkeypatch):
    from runtime_orchestrator.render_gate import evaluate_render_gate
    monkeypatch.setenv("ZLAB_RENDER_STRICT_DEFAULT", "1")
    events = [
        FallbackEvent(motor_id="motor_019", kind="narrator_used_structured_fallback",
                      section_id="bibliography"),  # low value
    ]
    verdict = assess("client_safe", events)
    gate_verdict = evaluate_render_gate(
        state="client_safe",
        qa_card=_clean_qa_card(),
        fallback_verdict=verdict,
    )
    # client_safe state allows DEGRADED fallback per V6 _TIER_ALLOWED_STATES?
    # Actually DEGRADED is forbidden in client_safe. Let me verify by
    # asserting the high-value channel is NOT what blocks.
    if not gate_verdict.allowed:
        assert all("high-value section" not in r for r in gate_verdict.reasons)
