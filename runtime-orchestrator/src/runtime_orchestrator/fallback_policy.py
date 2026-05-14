"""V6 P1 — Fallback Policy Engine.

V5 closed the framework's INTELLIGENCE. V6 stabilizes the BRAIN.

Today, when motor logic encounters missing inputs / failed dependencies /
out-of-policy outputs, motors emit "fallback" content — silently.
Examples observed in the wild:
  - motor_054 emits a synthetic gold nugget when no thesis exists
  - motor_018 emits a placeholder chart when chart_intelligence_binding is empty
  - motor_019 falls back to structured-summary prose when Codex CLI times out
  - motor_028 emits a coverage_gap row when an API returns 404

Some of these are LEGITIMATE (graceful degradation under sparse evidence).
Others are CONTAMINATION (the report carries placeholder content the user
will read as real intelligence).

This module classifies fallbacks into three tiers and enforces what
publication states each tier is allowed in.

Phase 0 anchor: "no permitir fallback silencioso". Every fallback is now
either ALLOWED in the current publication state, or BLOCKS the report.

Tri-modal policy:

  safe_fallback       — informational only; allowed everywhere
  degraded_fallback   — content was substituted; ONLY allowed in
                        internal_debug_only OR exploratory_prior
  prohibited_fallback — represents undetected contamination; BLOCKS

Integration:
  pipeline_orchestrator collects fallback events from each motor (via
  motor_024 governance event registry). motor_017 (render gate) calls
  enforce_for_render(state, fallback_events) BEFORE compiling the PDF.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping


class FallbackTier(str, Enum):
    """Tri-modal tier per the V6 policy."""
    SAFE = "safe_fallback"
    DEGRADED = "degraded_fallback"
    PROHIBITED = "prohibited_fallback"


# Allowed states per tier. Keys are publication / report states from
# report_state_machine. Lower-strength states allow more fallback
# permissiveness.
_TIER_ALLOWED_STATES: dict[FallbackTier, frozenset[str]] = {
    FallbackTier.SAFE: frozenset({
        "internal_debug_only",
        "exploratory_prior",
        "structural_hypothesis",
        "bounded_peer_analysis",
        "evidence_discrimination",
        "decision_blocked",
        "publish_bounded",
        "client_safe",
    }),
    FallbackTier.DEGRADED: frozenset({
        "internal_debug_only",
        "exploratory_prior",
    }),
    FallbackTier.PROHIBITED: frozenset(),  # never allowed
}


# Fallback KIND → tier classification.
# Each motor emits fallback events with a `kind` field; this maps to a tier.
# Unmapped kinds default to DEGRADED (conservative — prefer block over leak).
_KIND_TO_TIER: dict[str, FallbackTier] = {
    # SAFE (informational)
    "source_coverage_gap_logged":          FallbackTier.SAFE,
    "missing_evidence_marker":             FallbackTier.SAFE,
    "uncertainty_marker_added":            FallbackTier.SAFE,
    "claim_ceiling_capped":                FallbackTier.SAFE,
    "evidence_state_downgraded":           FallbackTier.SAFE,
    "screening_grade_assigned":            FallbackTier.SAFE,
    "validation_requirement_emitted":      FallbackTier.SAFE,

    # DEGRADED (content was substituted; visible to reader)
    "narrator_used_structured_fallback":   FallbackTier.DEGRADED,
    "narrator_codex_timeout":              FallbackTier.DEGRADED,
    "narrator_codex_unavailable":          FallbackTier.DEGRADED,
    "chart_placeholder_emitted":           FallbackTier.DEGRADED,
    "decorative_chart_kept_no_binding":    FallbackTier.DEGRADED,
    "scenario_justification_partial":      FallbackTier.DEGRADED,
    "claim_governor_default_state":        FallbackTier.DEGRADED,
    "evidence_pack_fallback_to_generic":   FallbackTier.DEGRADED,
    "tad_action_inferred_from_default":    FallbackTier.DEGRADED,

    # PROHIBITED (silent contamination — must block)
    "hardcoded_pattern_injection":         FallbackTier.PROHIBITED,
    "cross_family_pattern_leak":           FallbackTier.PROHIBITED,
    "chart_from_other_asset_family":       FallbackTier.PROHIBITED,
    "verified_claim_without_evidence":     FallbackTier.PROHIBITED,
    "savings_claim_without_baseline":      FallbackTier.PROHIBITED,
    "roi_claim_without_control_boundary":  FallbackTier.PROHIBITED,
    "compliance_closure_by_screening":     FallbackTier.PROHIBITED,
    "narrator_invented_claim":             FallbackTier.PROHIBITED,
    "fallback_combination_unjustified":    FallbackTier.PROHIBITED,
    "synthetic_gold_nugget":               FallbackTier.PROHIBITED,
    "repeated_evidence_pack":              FallbackTier.PROHIBITED,
}


# V8 P7 — high-value sections per Chief QA Architect § G. If ANY of
# these sections is downgraded to a fallback, client_safe is refused
# (the reader treats them as the spine of the deliverable).
HIGH_VALUE_SECTIONS: frozenset[str] = frozenset({
    "executive_structural_thesis",
    "tad",
    "financial_exposure",
    "peer_comparison",
    "conditional_redesign",
    "case_adaptation_memo",
})


@dataclass(frozen=True)
class FallbackEvent:
    """A single fallback event recorded by a motor during pipeline run."""
    motor_id: str
    kind: str          # the lookup key for _KIND_TO_TIER
    reason: str = ""   # human-readable detail
    metadata: dict[str, Any] = field(default_factory=dict)
    # V8 P7 — section_id (optional). When present and the event downgrades
    # a high-value section, render_gate refuses client_safe.
    section_id: str = ""

    def tier(self) -> FallbackTier:
        return _KIND_TO_TIER.get(self.kind, FallbackTier.DEGRADED)

    def is_high_value_section(self) -> bool:
        return (self.section_id or "").strip().lower() in HIGH_VALUE_SECTIONS


@dataclass(frozen=True)
class FallbackPolicyVerdict:
    """Result of applying the policy to a set of events for a given state."""
    state: str
    total_events: int
    safe_count: int
    degraded_count: int
    prohibited_count: int
    blocking_events: tuple[FallbackEvent, ...]   # events that BLOCK in this state
    out_of_policy_events: tuple[FallbackEvent, ...]  # blocking + non-allowed degraded
    # V8 P7 — count of fallback events affecting high-value sections.
    high_value_section_downgrades: int = 0
    affected_high_value_sections: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return len(self.out_of_policy_events) == 0


class FallbackViolation(Exception):
    """Raised by enforce_for_render when prohibited fallbacks present."""

    def __init__(self, verdict: FallbackPolicyVerdict) -> None:
        super().__init__(
            f"FallbackViolation: {len(verdict.out_of_policy_events)} fallback(s) "
            f"out of policy for state={verdict.state!r}. "
            f"prohibited={verdict.prohibited_count}, "
            f"degraded_disallowed={len(verdict.out_of_policy_events) - verdict.prohibited_count}"
        )
        self.verdict = verdict


def classify(kind: str) -> FallbackTier:
    """Return the tier for a fallback `kind` token.

    Unknown kinds default to DEGRADED (conservative: prefer block over
    silent acceptance).
    """
    return _KIND_TO_TIER.get(kind, FallbackTier.DEGRADED)


def is_allowed(state: str, kind: str) -> bool:
    """True if a fallback of this kind is permitted in this state."""
    tier = classify(kind)
    return state in _TIER_ALLOWED_STATES.get(tier, frozenset())


def assess(
    state: str,
    events: Iterable[FallbackEvent | Mapping[str, Any]],
) -> FallbackPolicyVerdict:
    """Apply the policy to a stream of events for a given publication state.

    Accepts either FallbackEvent dataclass instances OR dict-shaped events
    (which the orchestrator may pass through motor_024's registry).
    """
    state_norm = (state or "").strip()
    safe = 0
    degraded = 0
    prohibited = 0
    blocking: list[FallbackEvent] = []
    out_of_policy: list[FallbackEvent] = []
    total = 0

    # V8 P7 — track high-value section downgrades.
    high_value_downgrades = 0
    affected_sections: set[str] = set()

    for raw in events or []:
        if isinstance(raw, FallbackEvent):
            ev = raw
        elif isinstance(raw, Mapping):
            ev = FallbackEvent(
                motor_id=str(raw.get("motor_id", "")),
                kind=str(raw.get("kind", "")),
                reason=str(raw.get("reason", "")),
                metadata=dict(raw.get("metadata", {}) or {}),
                section_id=str(raw.get("section_id", "") or ""),
            )
        else:
            continue
        total += 1
        tier = ev.tier()
        if tier == FallbackTier.SAFE:
            safe += 1
        elif tier == FallbackTier.DEGRADED:
            degraded += 1
        elif tier == FallbackTier.PROHIBITED:
            prohibited += 1
            blocking.append(ev)
        # Out-of-policy = event whose tier is not allowed in this state
        if state_norm not in _TIER_ALLOWED_STATES.get(tier, frozenset()):
            out_of_policy.append(ev)
        # V8 P7 — high-value section impact (only DEGRADED/PROHIBITED count;
        # SAFE markers in a high-value section are informational).
        if ev.is_high_value_section() and tier != FallbackTier.SAFE:
            high_value_downgrades += 1
            affected_sections.add(ev.section_id.strip().lower())

    return FallbackPolicyVerdict(
        state=state_norm,
        total_events=total,
        safe_count=safe,
        degraded_count=degraded,
        prohibited_count=prohibited,
        blocking_events=tuple(blocking),
        out_of_policy_events=tuple(out_of_policy),
        high_value_section_downgrades=high_value_downgrades,
        affected_high_value_sections=tuple(sorted(affected_sections)),
    )


def enforce_for_render(
    state: str,
    events: Iterable[FallbackEvent | Mapping[str, Any]],
) -> FallbackPolicyVerdict:
    """Hard-block enforcement: raise FallbackViolation if any out-of-policy
    fallback would land in the report at `state`.

    motor_017 (LaTeX render) should call this BEFORE compiling the PDF.
    """
    verdict = assess(state, events)
    if not verdict.passed:
        raise FallbackViolation(verdict)
    return verdict
