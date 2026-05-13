"""V6 P1 — fallback_policy tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.fallback_policy import (
    FallbackEvent,
    FallbackPolicyVerdict,
    FallbackTier,
    FallbackViolation,
    assess,
    classify,
    enforce_for_render,
    is_allowed,
)


# ── tier classification ─────────────────────────────────────────────


def test_safe_fallback_kind_classifies_as_safe():
    assert classify("source_coverage_gap_logged") == FallbackTier.SAFE
    assert classify("uncertainty_marker_added") == FallbackTier.SAFE
    assert classify("evidence_state_downgraded") == FallbackTier.SAFE


def test_degraded_fallback_kind_classifies_as_degraded():
    assert classify("narrator_used_structured_fallback") == FallbackTier.DEGRADED
    assert classify("chart_placeholder_emitted") == FallbackTier.DEGRADED


def test_prohibited_fallback_kind_classifies_as_prohibited():
    assert classify("cross_family_pattern_leak") == FallbackTier.PROHIBITED
    assert classify("narrator_invented_claim") == FallbackTier.PROHIBITED
    assert classify("synthetic_gold_nugget") == FallbackTier.PROHIBITED


def test_unknown_kind_defaults_to_degraded_conservative():
    """Unknown kinds default to DEGRADED — prefer block over silent leak."""
    assert classify("nonexistent_kind") == FallbackTier.DEGRADED
    assert classify("") == FallbackTier.DEGRADED


# ── is_allowed ──────────────────────────────────────────────────────


def test_safe_fallback_allowed_in_all_states():
    for state in (
        "internal_debug_only", "exploratory_prior", "structural_hypothesis",
        "bounded_peer_analysis", "evidence_discrimination", "decision_blocked",
        "publish_bounded", "client_safe",
    ):
        assert is_allowed(state, "source_coverage_gap_logged"), state


def test_degraded_fallback_only_allowed_in_low_strength_states():
    assert is_allowed("internal_debug_only", "narrator_used_structured_fallback")
    assert is_allowed("exploratory_prior", "narrator_used_structured_fallback")
    # NOT allowed in stronger states
    assert not is_allowed("client_safe", "narrator_used_structured_fallback")
    assert not is_allowed("publish_bounded", "narrator_used_structured_fallback")
    assert not is_allowed("bounded_peer_analysis", "narrator_used_structured_fallback")


def test_prohibited_fallback_never_allowed():
    for state in (
        "internal_debug_only", "exploratory_prior", "structural_hypothesis",
        "bounded_peer_analysis", "evidence_discrimination", "decision_blocked",
        "publish_bounded", "client_safe",
    ):
        assert not is_allowed(state, "cross_family_pattern_leak"), state
        assert not is_allowed(state, "narrator_invented_claim"), state


# ── assess: aggregate verdict ───────────────────────────────────────


def test_assess_no_events_passes():
    v = assess("client_safe", [])
    assert v.passed
    assert v.total_events == 0


def test_assess_safe_only_in_client_safe_passes():
    events = [
        FallbackEvent("motor_028", "source_coverage_gap_logged", "404"),
        FallbackEvent("motor_034", "claim_ceiling_capped"),
    ]
    v = assess("client_safe", events)
    assert v.passed
    assert v.safe_count == 2
    assert v.total_events == 2


def test_assess_degraded_in_client_safe_fails():
    events = [
        FallbackEvent("motor_019", "narrator_used_structured_fallback"),
    ]
    v = assess("client_safe", events)
    assert not v.passed
    assert v.degraded_count == 1
    assert len(v.out_of_policy_events) == 1


def test_assess_degraded_in_exploratory_prior_passes():
    events = [
        FallbackEvent("motor_019", "narrator_used_structured_fallback"),
    ]
    v = assess("exploratory_prior", events)
    assert v.passed
    assert v.degraded_count == 1
    assert len(v.out_of_policy_events) == 0


def test_assess_prohibited_blocks_in_every_state():
    events = [
        FallbackEvent("motor_054", "synthetic_gold_nugget"),
    ]
    for state in (
        "internal_debug_only", "exploratory_prior", "client_safe",
    ):
        v = assess(state, events)
        assert not v.passed
        assert v.prohibited_count == 1
        assert len(v.blocking_events) == 1


def test_assess_dict_events_accepted():
    """orchestrator may pass dict-shaped events from motor_024 registry."""
    events = [
        {"motor_id": "motor_028", "kind": "source_coverage_gap_logged"},
        {"motor_id": "motor_019", "kind": "narrator_used_structured_fallback"},
    ]
    v = assess("client_safe", events)
    assert v.total_events == 2
    assert v.safe_count == 1
    assert v.degraded_count == 1


def test_assess_mixed_events_correctly_categorized():
    events = [
        FallbackEvent("m1", "uncertainty_marker_added"),       # SAFE
        FallbackEvent("m2", "uncertainty_marker_added"),       # SAFE
        FallbackEvent("m3", "narrator_codex_timeout"),         # DEGRADED
        FallbackEvent("m4", "cross_family_pattern_leak"),      # PROHIBITED
    ]
    v = assess("client_safe", events)
    assert v.total_events == 4
    assert v.safe_count == 2
    assert v.degraded_count == 1
    assert v.prohibited_count == 1
    # In client_safe: degraded is out-of-policy + prohibited blocks
    assert len(v.out_of_policy_events) == 2


# ── enforce_for_render: raise on violation ──────────────────────────


def test_enforce_passes_silent_when_clean():
    events = [FallbackEvent("m1", "source_coverage_gap_logged")]
    verdict = enforce_for_render("client_safe", events)
    assert verdict.passed


def test_enforce_raises_on_prohibited():
    events = [FallbackEvent("m1", "narrator_invented_claim")]
    with pytest.raises(FallbackViolation) as exc_info:
        enforce_for_render("client_safe", events)
    assert exc_info.value.verdict.prohibited_count == 1


def test_enforce_raises_on_degraded_in_client_safe():
    events = [FallbackEvent("m1", "narrator_codex_timeout")]
    with pytest.raises(FallbackViolation):
        enforce_for_render("client_safe", events)


def test_enforce_passes_degraded_in_exploratory_prior():
    events = [FallbackEvent("m1", "narrator_codex_timeout")]
    verdict = enforce_for_render("exploratory_prior", events)
    assert verdict.passed


def test_violation_message_carries_counts():
    events = [
        FallbackEvent("m1", "narrator_invented_claim"),
        FallbackEvent("m2", "narrator_codex_timeout"),
    ]
    with pytest.raises(FallbackViolation) as exc_info:
        enforce_for_render("client_safe", events)
    msg = str(exc_info.value)
    assert "prohibited=1" in msg
    assert "state='client_safe'" in msg
