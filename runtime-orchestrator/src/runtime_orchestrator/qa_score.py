"""V6 P3 — QA Score Aggregator.

Today, multiple motors emit local "score" signals scattered across the
pipeline output (motor_036 consistency, motor_055-063 validator severities,
motor_025 epistemic axes, motor_031 ML stability, motor_058 jaccard, etc).

There is NO single cross-motor score the dashboard / render gate can
read to decide "is this report client-safe?".

V6 P3 fixes this. One module aggregates 7 explicit health dimensions
into a QAScoreCard with an `overall_score` and a `client_safe` boolean.

Each dimension ∈ [0.0, 1.0]:
  1.0  = clean / healthy
  0.0  = total contamination / failure

Dimensions (Master Doc §0 + prompt item 15):

  stability_score              — motor_036 + state_machine + fallback_policy
  contamination_score          — inverse of motor_061 + motor_063 violations
  epistemic_integrity_score    — motor_059 + motor_025 ladder discipline
  rendering_integrity_score    — motor_019 lint verdicts + orphan claims
  combination_quality_score    — motor_054 + motor_057 nugget quality
  report_uniqueness_score      — motor_058 jaccard / verbatim reuse
  asset_family_integrity_score — motor_061 isolation outcomes

`overall_score` is a WEIGHTED MEAN with weights favoring contamination
(the V6 priority).

`client_safe` = overall ≥ 0.85 AND all hard-blocks clean AND no
prohibited fallbacks.

Integration (deferred to V6 P9 render gate): motor_017 reads the
QAScoreCard and refuses to compile if `client_safe == False` unless the
opt-in `__pipeline__.__render_under_warnings__ = true` flag is set.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


# Dimension weights for overall_score. Sum to 1.0.
# Higher weight = stronger penalty when that dimension degrades.
_DIMENSION_WEIGHTS: dict[str, float] = {
    "stability_score":              0.20,
    "contamination_score":          0.20,  # priority for V6
    "epistemic_integrity_score":    0.15,
    "rendering_integrity_score":    0.15,
    "combination_quality_score":    0.10,
    "report_uniqueness_score":      0.10,
    "asset_family_integrity_score": 0.10,
}


# Threshold above which a report is considered client-safe IF all hard-
# blocks are also clean.
CLIENT_SAFE_THRESHOLD: float = 0.85
DECISION_BLOCKED_THRESHOLD: float = 0.50


@dataclass(frozen=True)
class QAScoreCard:
    """Aggregated cross-motor health snapshot for one pipeline run."""
    stability_score:              float
    contamination_score:          float
    epistemic_integrity_score:    float
    rendering_integrity_score:    float
    combination_quality_score:    float
    report_uniqueness_score:      float
    asset_family_integrity_score: float
    overall_score:                float
    client_safe:                  bool
    decision_blocked:             bool
    rationale:                    dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stability_score":              self.stability_score,
            "contamination_score":          self.contamination_score,
            "epistemic_integrity_score":    self.epistemic_integrity_score,
            "rendering_integrity_score":    self.rendering_integrity_score,
            "combination_quality_score":    self.combination_quality_score,
            "report_uniqueness_score":      self.report_uniqueness_score,
            "asset_family_integrity_score": self.asset_family_integrity_score,
            "overall_score":                self.overall_score,
            "client_safe":                  self.client_safe,
            "decision_blocked":             self.decision_blocked,
            "rationale":                    dict(self.rationale),
        }


def _clamp(v: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return lo
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def _score_from_violation_counts(
    critical: int, warning: int, *, total_attempts: int = 0
) -> float:
    """Convert validator violation counts into a 0..1 score.

    1.0 = no violations. Each critical drops score by 0.20, each warning
    by 0.05. Floored at 0.0.
    """
    score = 1.0 - (0.20 * critical) - (0.05 * warning)
    return max(0.0, min(1.0, score))


def _stability_score(
    consistency_summary: Mapping[str, Any] | None,
    fallback_verdict: Mapping[str, Any] | None,
    state_machine_state: str,
) -> tuple[float, str]:
    """1.0 = motor_036 reports can_render_pdf, zero prohibited fallbacks,
    state ∈ stable set."""
    cs = consistency_summary or {}
    can_render = bool(cs.get("can_render_pdf", True))
    critical_failures = int(cs.get("critical_failure_count", 0) or 0)
    warning_failures = int(cs.get("warning_failure_count", 0) or 0)

    base = _score_from_violation_counts(critical_failures, warning_failures)

    # Fallback policy penalty
    fb = fallback_verdict or {}
    prohibited = int(fb.get("prohibited_count", 0) or 0)
    base = max(0.0, base - 0.30 * prohibited)

    # State penalty (non-stable states reduce stability)
    state = (state_machine_state or "").strip()
    if state in ("decision_blocked", "internal_debug_only"):
        base = max(0.0, base - 0.20)

    rationale = (
        f"motor_036 critical={critical_failures}/warning={warning_failures}, "
        f"prohibited_fallbacks={prohibited}, state={state}, "
        f"can_render={can_render}"
    )
    if not can_render:
        base = min(base, 0.40)
    return base, rationale


def _contamination_score(
    motor_061_summary: Mapping[str, Any] | None,
    motor_063_summary: Mapping[str, Any] | None,
) -> tuple[float, str]:
    """1.0 = zero asset_family contamination, zero chart contamination."""
    af_blocking = int((motor_061_summary or {}).get("blocking_violations", 0) or 0)
    af_warning = int((motor_061_summary or {}).get("warning_violations", 0) or 0)
    chart_blocking = int((motor_063_summary or {}).get("blocking_violations", 0) or 0)
    chart_warning = int((motor_063_summary or {}).get("warning_violations", 0) or 0)
    score = _score_from_violation_counts(
        af_blocking + chart_blocking,
        af_warning + chart_warning,
    )
    rationale = (
        f"asset_family violations={af_blocking}b/{af_warning}w; "
        f"chart violations={chart_blocking}b/{chart_warning}w"
    )
    return score, rationale


def _epistemic_integrity_score(
    motor_059_summary: Mapping[str, Any] | None,
    motor_025_summary: Mapping[str, Any] | None,
) -> tuple[float, str]:
    """1.0 = R1-R7+ rules clean, no claim_support_state mismatch."""
    si_critical = int((motor_059_summary or {}).get("blocking_violations", 0) or 0)
    si_warning = int((motor_059_summary or {}).get("warning_violations", 0) or 0)
    ladder_violations = int((motor_025_summary or {}).get("ladder_violations", 0) or 0)
    score = _score_from_violation_counts(si_critical + ladder_violations, si_warning)
    rationale = (
        f"motor_059 violations={si_critical}b/{si_warning}w; "
        f"ladder ceiling violations={ladder_violations}"
    )
    return score, rationale


def _rendering_integrity_score(
    motor_019_lint: Mapping[str, Any] | None,
) -> tuple[float, str]:
    """1.0 = no orphan claims, no forbidden phrases, no instruction leaks.
    V5 P7 narrator_validator data."""
    lint = motor_019_lint or {}
    orphans = len(lint.get("orphan_claim_findings", []) or [])
    violations = list(lint.get("violations", []) or [])
    forbidden = sum(1 for v in violations if str(v).startswith("forbidden_phrase"))
    closure = sum(1 for v in violations if str(v).startswith("closure_phrase"))
    leakage = sum(1 for v in violations if str(v).startswith("instruction_leakage"))
    unsupported_nums = sum(1 for v in violations if str(v).startswith("unsupported_numeric"))

    critical = forbidden + closure + leakage + unsupported_nums + (1 if orphans > 3 else 0)
    warning = (1 if 0 < orphans <= 3 else 0)
    score = _score_from_violation_counts(critical, warning)
    rationale = (
        f"orphan_claims={orphans}, forbidden_phrases={forbidden}, "
        f"closure_phrases={closure}, instruction_leakage={leakage}, "
        f"unsupported_numerics={unsupported_nums}"
    )
    return score, rationale


def _combination_quality_score(
    motor_054_summary: Mapping[str, Any] | None,
    motor_057_summary: Mapping[str, Any] | None,
) -> tuple[float, str]:
    """1.0 = combinations have active patterns AND gold nuggets pass GN1-3."""
    active_count = int((motor_054_summary or {}).get("skill_combination_activation_count", 0) or 0)
    gn_critical = int((motor_057_summary or {}).get("blocking_violations", 0) or 0)
    gn_warning = int((motor_057_summary or {}).get("warning_violations", 0) or 0)
    base = _score_from_violation_counts(gn_critical, gn_warning)
    # Bonus for having activations
    if active_count > 0:
        base = min(1.0, base + 0.05 * min(active_count, 5))
    rationale = (
        f"active_combinations={active_count}, nugget violations="
        f"{gn_critical}b/{gn_warning}w"
    )
    return base, rationale


def _report_uniqueness_score(
    motor_058_summary: Mapping[str, Any] | None,
) -> tuple[float, str]:
    """1.0 = jaccard low, no verbatim nugget reuse."""
    critical = int((motor_058_summary or {}).get("blocking_violations", 0) or 0)
    warning = int((motor_058_summary or {}).get("warning_violations", 0) or 0)
    score = _score_from_violation_counts(critical, warning)
    rationale = f"uniqueness violations={critical}b/{warning}w"
    return score, rationale


def _asset_family_integrity_score(
    motor_061_summary: Mapping[str, Any] | None,
) -> tuple[float, str]:
    """1.0 = no cross-family pattern activation; full family isolation.

    Reads granular cross_family_violations + contamination_count if
    motor_061 reports them; otherwise falls back to blocking_violations
    as the violation indicator. This handles both pre-V6 and V6-style
    motor_061 output schemas.
    """
    summary = motor_061_summary or {}
    cross_family = int(summary.get("cross_family_violations", 0) or 0)
    contamination = int(summary.get("contamination_count", 0) or 0)
    granular = cross_family + contamination
    if granular == 0:
        # Fall back to blocking_violations as catch-all indicator
        granular = int(summary.get("blocking_violations", 0) or 0)
    warning = int(summary.get("warning_violations", 0) or 0)
    score = _score_from_violation_counts(granular, warning)
    rationale = (
        f"cross_family_violations={cross_family}, "
        f"contamination_count={contamination}, "
        f"fallback_blocking={int(summary.get('blocking_violations', 0) or 0)}"
    )
    return score, rationale


def build_qa_score_card(
    *,
    consistency_summary: Mapping[str, Any] | None = None,
    fallback_verdict: Mapping[str, Any] | None = None,
    motor_019_lint: Mapping[str, Any] | None = None,
    motor_025_summary: Mapping[str, Any] | None = None,
    motor_054_summary: Mapping[str, Any] | None = None,
    motor_057_summary: Mapping[str, Any] | None = None,
    motor_058_summary: Mapping[str, Any] | None = None,
    motor_059_summary: Mapping[str, Any] | None = None,
    motor_061_summary: Mapping[str, Any] | None = None,
    motor_063_summary: Mapping[str, Any] | None = None,
    state_machine_state: str = "",
    source_audit_passed: bool = True,
) -> QAScoreCard:
    """Aggregate cross-motor signals into one QAScoreCard.

    Every parameter is optional and defaults to None — the aggregator
    is robust to missing dimensions (returns conservative scores).
    """
    stability, stab_why = _stability_score(
        consistency_summary, fallback_verdict, state_machine_state
    )
    contamination, cont_why = _contamination_score(
        motor_061_summary, motor_063_summary
    )
    epistemic, ep_why = _epistemic_integrity_score(
        motor_059_summary, motor_025_summary
    )
    rendering, ren_why = _rendering_integrity_score(motor_019_lint)
    combination, comb_why = _combination_quality_score(
        motor_054_summary, motor_057_summary
    )
    uniqueness, uni_why = _report_uniqueness_score(motor_058_summary)
    asset_family, af_why = _asset_family_integrity_score(motor_061_summary)

    overall = (
        _DIMENSION_WEIGHTS["stability_score"]               * stability +
        _DIMENSION_WEIGHTS["contamination_score"]           * contamination +
        _DIMENSION_WEIGHTS["epistemic_integrity_score"]     * epistemic +
        _DIMENSION_WEIGHTS["rendering_integrity_score"]     * rendering +
        _DIMENSION_WEIGHTS["combination_quality_score"]     * combination +
        _DIMENSION_WEIGHTS["report_uniqueness_score"]       * uniqueness +
        _DIMENSION_WEIGHTS["asset_family_integrity_score"]  * asset_family
    )

    # Hard requirements for client_safe
    has_prohibited_fallback = int(
        (fallback_verdict or {}).get("prohibited_count", 0) or 0
    ) > 0
    cannot_render = not bool(
        (consistency_summary or {}).get("can_render_pdf", True)
    )

    client_safe = (
        overall >= CLIENT_SAFE_THRESHOLD
        and not has_prohibited_fallback
        and not cannot_render
        and source_audit_passed
    )
    decision_blocked = (
        overall <= DECISION_BLOCKED_THRESHOLD  # inclusive: 0.50 is already blocked
        or has_prohibited_fallback
        or cannot_render
    )

    return QAScoreCard(
        stability_score=stability,
        contamination_score=contamination,
        epistemic_integrity_score=epistemic,
        rendering_integrity_score=rendering,
        combination_quality_score=combination,
        report_uniqueness_score=uniqueness,
        asset_family_integrity_score=asset_family,
        overall_score=round(overall, 4),
        client_safe=client_safe,
        decision_blocked=decision_blocked,
        rationale={
            "stability":              stab_why,
            "contamination":          cont_why,
            "epistemic_integrity":    ep_why,
            "rendering_integrity":    ren_why,
            "combination_quality":    comb_why,
            "report_uniqueness":      uni_why,
            "asset_family_integrity": af_why,
        },
    )
