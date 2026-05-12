"""Report State Machine (V3 G6 — RECOVERY_V3_BACKLOG.md).

Formalizes the 8 report states the V3 prompt declares mandatory. motor_017
consumes this to decide whether to render the PDF.

Lifecycle (terminal states are exclusive):

    exploratory_prior          ──┐
    structural_hypothesis       │
    bounded_peer_analysis       ├─ "in progress" — pipeline still working
    evidence_discrimination     │
                              ──┘
    decision_blocked           ── pipeline has unresolvable consistency issues
    internal_debug_only        ── contamination detected; client cannot see this
    publish_bounded            ── ready to render but with bounded caveats
    client_safe                ── strictest green: nothing blocking, all validators clean

Render gate (motor_017):
  PDF renders when state ∈ allowed_render_states (default: {"client_safe"}).
  Pipeline can widen via __pipeline__.allowed_render_states.

State derivation is a PURE function — feed it the validator outputs and
the scenario_review readiness, get back (state, reason, signals). No I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── State definitions ──────────────────────────────────────────────────


STATES = (
    "exploratory_prior",
    "structural_hypothesis",
    "bounded_peer_analysis",
    "evidence_discrimination",
    "decision_blocked",
    "publish_bounded",
    "client_safe",
    "internal_debug_only",
)

# V3 Day 4 default: allow anything that V2 already permitted. V2 blocked
# only when validators / contamination / scenario_review failed; the state
# machine maps those to `internal_debug_only` and `decision_blocked`. By
# defaulting allowed_render_states to "everything else", we preserve V2
# behavior. Strict mode (client_safe only) is opt-in via
# __pipeline__.allowed_render_states = ("client_safe",) — recommended for
# production client-facing deliverables.
DEFAULT_ALLOWED_RENDER_STATES: tuple[str, ...] = (
    "exploratory_prior",
    "structural_hypothesis",
    "bounded_peer_analysis",
    "evidence_discrimination",
    "publish_bounded",
    "client_safe",
)

# Strict mode constant for production use.
STRICT_CLIENT_SAFE_RENDER_STATES: tuple[str, ...] = ("client_safe",)


@dataclass
class ReportStateDiagnosis:
    """Inputs the state machine consumes to derive a state.

    Every field is optional with a safe default; if a validator hasn't run
    the machine assumes it didn't fail (consistent with motor_017's gate
    semantics today).
    """
    # consistency / structural blocks
    can_render_pdf: bool = True
    consistency_critical_failures: int = 0

    # asset family + scenario justification + chart contamination
    contamination_detected: bool = False
    chart_contamination_detected: bool = False
    scenario_justification_failed: bool = False

    # quality validators (V3 G1 hard blocks)
    duplicate_claim_signature: bool = False
    pack_repetition_count: int = 0
    archetype_replay: bool = False
    verbatim_nugget_reuse: bool = False
    strategic_intelligence_error_count: int = 0

    # scenario review readiness (dashboard gate)
    scenario_review_ready: bool = True
    scenario_review_pending_count: int = 0

    # evidence richness signals
    cluster_count: int = 0
    minimum_cluster_count_for_peer_analysis: int = 3
    minimum_cluster_count_for_discrimination: int = 5
    peer_set_valid: bool = False
    minimum_evidence_pack_ready: bool = False

    # nugget richness (V3 G16)
    nugget_count: int = 0
    nugget_count_min: int = 5
    nugget_count_max: int = 12

    # additional warning aggregate (for publish_bounded vs client_safe split)
    total_warning_count: int = 0


@dataclass
class ReportStateResult:
    state: str
    reason: str
    signals: list[str] = field(default_factory=list)
    can_render: bool = False
    allowed_render_states: tuple[str, ...] = DEFAULT_ALLOWED_RENDER_STATES


def derive_state(
    diag: ReportStateDiagnosis,
    *,
    allowed_render_states: tuple[str, ...] | None = None,
) -> ReportStateResult:
    """Deterministic state derivation.

    Order matters — checks are evaluated top-down. The first matching guard
    wins. `signals` accumulates a trace of what the diagnosis triggered.
    """
    allowed = allowed_render_states or DEFAULT_ALLOWED_RENDER_STATES
    signals: list[str] = []

    # ── Terminal failure states (override any green) ────────────────────

    # CONTAMINATION → internal_debug_only.
    # Per V3 prompt §1: "Si contamination=true → internal_debug_only."
    # This is the highest-priority override — overrides even client_safe.
    if diag.contamination_detected:
        signals.append("asset_family_contamination_detected")
        return ReportStateResult(
            state="internal_debug_only",
            reason="Asset-family contamination detected (motor_061). Report is not client-eligible.",
            signals=signals,
            can_render=("internal_debug_only" in allowed),
            allowed_render_states=allowed,
        )
    if diag.chart_contamination_detected:
        signals.append("chart_contamination_detected")
        return ReportStateResult(
            state="internal_debug_only",
            reason="Chart-validity contamination detected (motor_063). Report is not client-eligible.",
            signals=signals,
            can_render=("internal_debug_only" in allowed),
            allowed_render_states=allowed,
        )

    # Consistency failures → decision_blocked
    if not diag.can_render_pdf or diag.consistency_critical_failures > 0:
        signals.append("consistency_critical_failures")
        return ReportStateResult(
            state="decision_blocked",
            reason="System consistency validator (motor_036) reports critical failures.",
            signals=signals,
            can_render=("decision_blocked" in allowed),
            allowed_render_states=allowed,
        )

    # Strategic-intelligence errors (R2/R3/R5/R6/R7 in V3 G2) → decision_blocked
    if diag.strategic_intelligence_error_count > 0:
        signals.append("strategic_intelligence_errors")
        return ReportStateResult(
            state="decision_blocked",
            reason=(
                f"Strategic intelligence governance failures (motor_059): "
                f"{diag.strategic_intelligence_error_count} cross-layer errors."
            ),
            signals=signals,
            can_render=("decision_blocked" in allowed),
            allowed_render_states=allowed,
        )

    # Scenario review still pending in dashboard → decision_blocked
    if not diag.scenario_review_ready:
        signals.append("scenario_review_pending")
        return ReportStateResult(
            state="decision_blocked",
            reason=(
                f"Scenario review pending in dashboard "
                f"({diag.scenario_review_pending_count} scenarios awaiting approval)."
            ),
            signals=signals,
            can_render=("decision_blocked" in allowed),
            allowed_render_states=allowed,
        )

    # ── Quality-blocking conditions (V3 G1 hard blocks) ────────────────

    quality_blocks: list[str] = []
    if diag.duplicate_claim_signature:
        quality_blocks.append("duplicate_claim_signature (motor_055.HD2)")
    if diag.pack_repetition_count >= 2:
        quality_blocks.append(f"evidence_pack_repetition≥2 (motor_056.ER1)")
    if diag.archetype_replay:
        quality_blocks.append("archetype_replay (motor_057.GN1)")
    if diag.verbatim_nugget_reuse:
        quality_blocks.append("verbatim_nugget_reuse (motor_058.RU2)")
    if diag.scenario_justification_failed:
        quality_blocks.append("scenario_justification_failed (motor_062)")
    if quality_blocks:
        signals.extend(quality_blocks)
        return ReportStateResult(
            state="decision_blocked",
            reason="Quality validators detected blocking issues: " + "; ".join(quality_blocks),
            signals=signals,
            can_render=("decision_blocked" in allowed),
            allowed_render_states=allowed,
        )

    # ── In-progress states (cases without enough evidence for closure) ─

    if diag.cluster_count < diag.minimum_cluster_count_for_peer_analysis:
        signals.append("evidence_below_peer_analysis_threshold")
        return ReportStateResult(
            state="exploratory_prior",
            reason=(
                f"Insufficient evidence for peer analysis "
                f"({diag.cluster_count} clusters < "
                f"{diag.minimum_cluster_count_for_peer_analysis} required). "
                "Structural reasoning permitted; closure not."
            ),
            signals=signals,
            can_render=("exploratory_prior" in allowed),
            allowed_render_states=allowed,
        )
    if not diag.peer_set_valid:
        signals.append("peer_set_not_valid")
        return ReportStateResult(
            state="structural_hypothesis",
            reason="Evidence supports structural hypotheses but peer set not yet validated.",
            signals=signals,
            can_render=("structural_hypothesis" in allowed),
            allowed_render_states=allowed,
        )
    if not diag.minimum_evidence_pack_ready:
        signals.append("evidence_pack_not_ready")
        return ReportStateResult(
            state="bounded_peer_analysis",
            reason="Peer set valid; minimum evidence pack still incomplete for evidence discrimination.",
            signals=signals,
            can_render=("bounded_peer_analysis" in allowed),
            allowed_render_states=allowed,
        )
    if diag.cluster_count < diag.minimum_cluster_count_for_discrimination:
        signals.append("evidence_below_discrimination_threshold")
        return ReportStateResult(
            state="evidence_discrimination",
            reason=(
                f"Evidence pack ready; reaching {diag.minimum_cluster_count_for_discrimination} "
                f"clusters for full discrimination (currently {diag.cluster_count})."
            ),
            signals=signals,
            can_render=("evidence_discrimination" in allowed),
            allowed_render_states=allowed,
        )

    # ── Green states: client_safe vs publish_bounded ───────────────────

    # Nugget count must be in valid range (5-12 by default per V3 G16)
    nugget_ok = diag.nugget_count_min <= diag.nugget_count <= diag.nugget_count_max
    # Total warning count zero = client_safe; else publish_bounded
    if nugget_ok and diag.total_warning_count == 0:
        signals.append("all_validators_clean")
        signals.append(f"nugget_count={diag.nugget_count}_in_range")
        return ReportStateResult(
            state="client_safe",
            reason="All validators clean; nugget count in range; no warnings. Client-eligible.",
            signals=signals,
            can_render=("client_safe" in allowed),
            allowed_render_states=allowed,
        )

    bound_signals = []
    if not nugget_ok:
        bound_signals.append(
            f"nugget_count={diag.nugget_count}_outside_[{diag.nugget_count_min},{diag.nugget_count_max}]"
        )
    if diag.total_warning_count > 0:
        bound_signals.append(f"total_warnings={diag.total_warning_count}")
    signals.extend(bound_signals)
    return ReportStateResult(
        state="publish_bounded",
        reason=(
            "Validators non-blocking but bounded caveats present: "
            + "; ".join(bound_signals)
        ),
        signals=signals,
        can_render=("publish_bounded" in allowed),
        allowed_render_states=allowed,
    )


def diagnosis_from_motor_outputs(motor_outputs: dict[str, Any]) -> ReportStateDiagnosis:
    """Convenience builder — extract the diagnosis from motor outputs.

    motor_outputs is the dict typically passed to motor_017 (keys like
    'motor_036', 'motor_054', 'motor_055', ..., 'motor_063', plus the
    scenario_review summary).
    """
    def _d(key: str) -> dict:
        v = motor_outputs.get(key, {})
        return v if isinstance(v, dict) else {}

    m036 = _d("motor_036")
    m054 = _d("motor_054")
    m055 = _d("motor_055")
    m056 = _d("motor_056")
    m057 = _d("motor_057")
    m058 = _d("motor_058")
    m059 = _d("motor_059")
    m061 = _d("motor_061")
    m062 = _d("motor_062")
    m063 = _d("motor_063")
    sr = _d("scenario_review_summary")

    def _has_rule(motor_warnings: list, rule_id: str) -> bool:
        return any(
            isinstance(w, dict) and w.get("rule_id") == rule_id
            for w in motor_warnings
        )

    def _count_rule(motor_warnings: list, rule_id: str) -> int:
        return sum(
            1 for w in motor_warnings
            if isinstance(w, dict) and w.get("rule_id") == rule_id
        )

    m055_w = list(m055.get("hypothesis_diversity_warnings", []) or [])
    m056_w = list(m056.get("evidence_repetition_warnings", []) or [])
    m057_w = list(m057.get("gold_nugget_quality_warnings", []) or [])
    m058_w = list(m058.get("report_uniqueness_warnings", []) or [])
    m059_w = list(m059.get("strategic_intelligence_warnings", []) or [])

    total_warnings = sum([
        int(m055.get("warning_count", 0) or 0),
        int(m056.get("warning_count", 0) or 0),
        int(m057.get("warning_count", 0) or 0),
        int(m058.get("warning_count", 0) or 0),
        int(m059.get("warning_count", 0) or 0),
        int(m061.get("warning_count", 0) or 0),
        int(m062.get("warning_count", 0) or 0),
        int(m063.get("warning_count", 0) or 0),
    ])

    claim_register = m054.get("congruence_claim_contract_register") or []
    cluster_count = len(claim_register) if isinstance(claim_register, list) else 0

    return ReportStateDiagnosis(
        can_render_pdf=bool(m036.get("can_render_pdf", True)),
        consistency_critical_failures=len(m036.get("critical_failures", []) or []),
        contamination_detected=bool(m061.get("contamination_detected", False)),
        chart_contamination_detected=bool(m063.get("chart_contamination_detected", False)),
        scenario_justification_failed=bool(m062.get("scenario_justification_failed", False)),
        duplicate_claim_signature=_has_rule(m055_w, "HD2_duplicate_claim_signature"),
        pack_repetition_count=_count_rule(m056_w, "ER1_pack_repetition"),
        archetype_replay=_has_rule(m057_w, "GN1_archetype_replay"),
        verbatim_nugget_reuse=_has_rule(m058_w, "RU2_verbatim_nugget_reuse"),
        strategic_intelligence_error_count=int(
            (m059.get("warning_count_by_severity", {}) or {}).get("error", 0) or 0
        ),
        scenario_review_ready=bool(sr.get("ready_to_render", True)),
        scenario_review_pending_count=int(sr.get("pending_count", 0) or 0),
        cluster_count=cluster_count,
        peer_set_valid=bool(motor_outputs.get("peer_set_valid", True)),
        minimum_evidence_pack_ready=bool(motor_outputs.get("minimum_evidence_pack_ready", True)),
        nugget_count=int(m057.get("nugget_count_evaluated", 0) or 0),
        total_warning_count=total_warnings,
    )
