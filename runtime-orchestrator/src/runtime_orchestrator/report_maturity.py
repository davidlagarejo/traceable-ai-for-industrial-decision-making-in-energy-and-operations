"""V5 P5 — canonical 6-type report maturity classifier.

Phase 0 Master Doc §10 mandates the framework expose a CANONICAL FAMILY
of 6 deliverable types, graduated by evidence maturity:

  1. Integrated Preliminary Report
  2. Decision-Grade Report
  3. Hardened Decision Report
  4. Validation-Oriented Report
  5. Verification-Supported Report
  6. Verified Report

These are ORTHOGONAL to the existing framework taxonomy (which categorizes
reports by topic/shape, e.g. 'Target Classification Brief', 'TAD Action
Priority Brief', etc.). Every report — regardless of topic — has a
maturity grade. This module computes that grade deterministically from
the claim_support_state ladder owned by motor_025 (Phase 0 / Epistemic
Governance Layer).

Mapping (Master Doc §10 + §5.2):

  claim_support_state          →  canonical maturity grade
  ─────────────────────────────────────────────────────────────────
  unsupported                  →  Integrated Preliminary Report
  hypothesis                   →  Integrated Preliminary Report
  indication                   →  Integrated Preliminary Report
  screening_grade              →  Decision-Grade Report
  decision_grade               →  Decision-Grade Report
  partially_hardened           →  Hardened Decision Report
  verification_ready           →  Validation-Oriented Report
  verification_supported       →  Verification-Supported Report
  verified                     →  Verified Report

The classifier accepts EITHER:
  - a single claim_support_state string (per-claim mode), OR
  - the report's `max_claim_support_state` (aggregate mode — recommended
    for the Report Package's overall maturity grade)

Phase 0 anchor: no LLM. Deterministic mapping.
"""
from __future__ import annotations

from typing import Any


# Canonical 6-type family (Phase 0 Master Doc §10)
CANONICAL_REPORT_MATURITY_TYPES: tuple[str, ...] = (
    "Integrated Preliminary Report",
    "Decision-Grade Report",
    "Hardened Decision Report",
    "Validation-Oriented Report",
    "Verification-Supported Report",
    "Verified Report",
)


# Map each of the 9 claim_support_state values (Phase 0 §5.2) to a
# canonical maturity type. Lower-support states map to lower-strength
# reports. Higher-support states unlock stronger report types.
_SUPPORT_STATE_TO_MATURITY: dict[str, str] = {
    # Phase 0 §5.2 ladder
    "unsupported": "Integrated Preliminary Report",
    "hypothesis": "Integrated Preliminary Report",
    "indication": "Integrated Preliminary Report",
    "screening_grade": "Decision-Grade Report",
    "decision_grade": "Decision-Grade Report",
    "partially_hardened": "Hardened Decision Report",
    "verification_ready": "Validation-Oriented Report",
    "verification_supported": "Verification-Supported Report",
    "verified": "Verified Report",
}


# Ordered ladder of support states (for max() aggregation downstream).
SUPPORT_STATE_LADDER: tuple[str, ...] = (
    "unsupported",
    "hypothesis",
    "indication",
    "screening_grade",
    "decision_grade",
    "partially_hardened",
    "verification_ready",
    "verification_supported",
    "verified",
)


# Ordered ladder of maturity types (lower index = weaker).
_MATURITY_TYPE_INDEX: dict[str, int] = {
    name: i for i, name in enumerate(CANONICAL_REPORT_MATURITY_TYPES)
}


def maturity_type_for_support_state(support_state: str) -> str:
    """Map a single claim_support_state to its canonical maturity type.

    Unknown / empty / unrecognised states map to the most conservative
    `Integrated Preliminary Report` (Phase 0's bounded preliminary mode).
    """
    s = (support_state or "").strip().lower()
    return _SUPPORT_STATE_TO_MATURITY.get(s, "Integrated Preliminary Report")


def aggregate_maturity_type(
    claim_support_states: list[str] | tuple[str, ...],
) -> str:
    """Aggregate over many claims' support states → one canonical type.

    Phase 0 §10 makes clear: a report's overall maturity is bounded by
    the LADDER POSITION of its strongest-supported claims, but cannot
    exceed any structural blockers. The conservative aggregation rule:
    use the HIGHEST support state present, then map that.

    This is the "ceiling" view — the report can claim maturity X if AT
    LEAST ONE major claim is at level X. Downstream Phase 0 validators
    (motor_025) catch publication-state overrides if individual claims
    are above the ceiling.
    """
    if not claim_support_states:
        return "Integrated Preliminary Report"
    # Find the highest-ladder state present
    max_index = -1
    max_state = ""
    for s in claim_support_states:
        s_norm = (s or "").strip().lower()
        if s_norm in SUPPORT_STATE_LADDER:
            i = SUPPORT_STATE_LADDER.index(s_norm)
            if i > max_index:
                max_index = i
                max_state = s_norm
    if max_index < 0:
        return "Integrated Preliminary Report"
    return _SUPPORT_STATE_TO_MATURITY[max_state]


def maturity_type_index(maturity_type: str) -> int:
    """Return the ordinal of a maturity type (0..5). -1 if not canonical."""
    return _MATURITY_TYPE_INDEX.get(maturity_type, -1)


def is_stronger_maturity(a: str, b: str) -> bool:
    """True if maturity type a is strictly stronger than b."""
    return maturity_type_index(a) > maturity_type_index(b)


def derive_report_maturity_from_motor_025(
    motor_025_output: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compute the canonical maturity for the current Report Package
    from motor_025's epistemic status tuple.

    motor_025 produces a 3-axis status tuple per material output:
      phase_presence_state · claim_support_state · publication_state

    This function reads claim_support_state across the published rows
    and returns the canonical maturity classification with rationale.
    """
    if not isinstance(motor_025_output, dict):
        return {
            "report_maturity_type": "Integrated Preliminary Report",
            "max_claim_support_state": "",
            "rationale": "motor_025 output unavailable — defaulting to preliminary",
        }

    rows = []
    for key in ("status_register", "epistemic_status_register", "axis_records"):
        candidate = motor_025_output.get(key)
        if isinstance(candidate, list):
            rows = candidate
            break

    states: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        s = row.get("claim_support_state")
        if isinstance(s, str) and s.strip():
            states.append(s.strip().lower())

    maturity = aggregate_maturity_type(states)
    max_state = ""
    if states:
        max_idx = -1
        for s in states:
            if s in SUPPORT_STATE_LADDER:
                i = SUPPORT_STATE_LADDER.index(s)
                if i > max_idx:
                    max_idx = i
                    max_state = s

    return {
        "report_maturity_type": maturity,
        "max_claim_support_state": max_state,
        "rationale": (
            f"max claim_support_state across {len(states)} rows = "
            f"{max_state or 'none'} → mapped to {maturity!r}"
        ),
        "support_states_observed": sorted(set(states)),
    }
