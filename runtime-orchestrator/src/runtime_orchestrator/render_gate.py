"""V6 P9 — CLIENT_SAFE_MODE render gate (strict default).

V6 Stability prompt item 14: "CLIENT_SAFE_MODE — strict default".

Today the report pipeline renders whatever state the state-machine
permits, with `client_safe` being only one of six green states.
Production deliverables can slip through at `publish_bounded` or
`exploratory_prior` and still reach a client.

This module is the V6 *consolidator*: it reads every V6 hardening
verdict and emits ONE binary decision — render allowed, or refuse.

Strict mode (default):
  - QA card.client_safe == True
  - state ∈ STRICT_CLIENT_SAFE_RENDER_STATES (just "client_safe")
  - no prohibited fallback events
  - no unjustified source gaps
  - claim synchronization consistent
  - no pattern isolation violations

Soft mode (opt-out — env ZLAB_RENDER_STRICT_DEFAULT=0):
  - state ∈ DEFAULT_ALLOWED_RENDER_STATES (V2 behavior)
  - everything else advisory

Integration:
  motor_017 (LaTeX render gate) calls `evaluate_render_gate(...)` before
  invoking pdflatex. If verdict.allowed is False, motor_017 emits a
  decision_blocked stub PDF instead of the full report.

Phase 0 anchor: a client-facing deliverable is ONLY released when EVERY
gate is green. Silence elsewhere is not consent.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping

from .claim_synchronization_auditor import ClaimSyncReport
from .fallback_policy import FallbackPolicyVerdict
from .qa_score import QAScoreCard
from .report_state_machine import (
    DEFAULT_ALLOWED_RENDER_STATES,
    STRICT_CLIENT_SAFE_RENDER_STATES,
)
from .source_execution_auditor import (
    SourceExecutionAuditReport,
    client_safe_compatible,
)


_STRICT_ENV_FLAG = "ZLAB_RENDER_STRICT_DEFAULT"


def strict_mode_active(
    pipeline_inputs: Mapping[str, Any] | None = None,
) -> bool:
    """Resolve whether the strict CLIENT_SAFE_MODE default is active.

    Resolution order:
      1. pipeline_inputs["__render_strict_default__"] (explicit override)
      2. pipeline_inputs["__render_soft_mode__"] (force off)
      3. env ZLAB_RENDER_STRICT_DEFAULT (1/true/yes/on)
      4. default: True (V6 default is strict)
    """
    if pipeline_inputs:
        explicit = pipeline_inputs.get("__render_strict_default__")
        if explicit is not None:
            return bool(explicit)
        if pipeline_inputs.get("__render_soft_mode__"):
            return False
    raw = (os.environ.get(_STRICT_ENV_FLAG, "") or "").lower().strip()
    if raw in ("0", "false", "no", "off"):
        return False
    # Default: strict mode is ON.
    return True


@dataclass(frozen=True)
class RenderGateVerdict:
    allowed: bool
    strict_mode: bool
    state: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    # individual gate booleans for diagnostics:
    qa_client_safe: bool = False
    state_in_allowed: bool = False
    no_prohibited_fallback: bool = True
    no_unjustified_sources: bool = True
    claims_in_sync: bool = True
    no_isolation_violations: bool = True
    # V8 P1 — template contamination hard block
    no_template_contamination: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed":                   self.allowed,
            "strict_mode":               self.strict_mode,
            "state":                     self.state,
            "reasons":                   list(self.reasons),
            "qa_client_safe":            self.qa_client_safe,
            "state_in_allowed":          self.state_in_allowed,
            "no_prohibited_fallback":    self.no_prohibited_fallback,
            "no_unjustified_sources":    self.no_unjustified_sources,
            "claims_in_sync":            self.claims_in_sync,
            "no_isolation_violations":   self.no_isolation_violations,
            "no_template_contamination": self.no_template_contamination,
        }

    def publication_mode(self) -> str:
        """V8 P8 — publication_mode synthesis for the Final Delivery Gate.

        Returns one of:
          - "client_safe"
          - "publish_with_degradation"
          - "internal_debug_only"
          - "blocked"
        """
        if self.allowed and self.state == "client_safe":
            return "client_safe"
        if self.allowed:
            return "publish_with_degradation"
        # Not allowed. Severity hierarchy:
        #   1. template contamination ⇒ internal_debug_only
        if not self.no_template_contamination:
            return "internal_debug_only"
        #   2. contamination / sync / fallback / source ⇒ blocked
        if (
            not self.claims_in_sync
            or not self.no_isolation_violations
            or not self.no_prohibited_fallback
            or not self.no_unjustified_sources
        ):
            return "blocked"
        #   3. only state mismatch (strict refused because state != client_safe
        #      but all other gates green) ⇒ publish_with_degradation
        if not self.state_in_allowed:
            return "publish_with_degradation"
        # Fallback (QA card insufficient etc.)
        return "internal_debug_only"

    def as_yaml_block(self) -> str:
        """V8 P8 — emit the canonical Final Delivery Gate YAML block per
        Chief QA Architect § Required Output Changes.

        Format:

            final_delivery_gate:
              client_safe: true/false
              publication_mode: client_safe / publish_with_degradation / internal_debug_only / blocked
              strict_mode: true/false
              state: <state>
              blocking_failures: [...]
              chart_validation: passed/failed
              tad_claim_sync: passed/failed
              hybrid_logic_governance: passed/failed
              source_execution_status: passed/failed
              template_contamination: passed/failed
        """
        cs = "true" if (self.allowed and self.state == "client_safe") else "false"
        sm = "true" if self.strict_mode else "false"
        pm = self.publication_mode()
        # Top-level gate booleans → passed/failed labels
        def _pf(ok: bool) -> str:
            return "passed" if ok else "failed"
        lines = [
            "final_delivery_gate:",
            f"  client_safe: {cs}",
            f"  publication_mode: {pm}",
            f"  strict_mode: {sm}",
            f"  state: {self.state}",
        ]
        if self.reasons:
            lines.append("  blocking_failures:")
            for r in self.reasons:
                # Escape colons + newlines defensively.
                clean = str(r).replace("\n", " ").replace('"', "'")
                lines.append(f'    - "{clean}"')
        else:
            lines.append("  blocking_failures: []")
        lines.extend([
            f"  chart_validation: {_pf(self.no_isolation_violations)}",
            f"  tad_claim_sync: {_pf(self.claims_in_sync)}",
            f"  hybrid_logic_governance: {_pf(self.no_isolation_violations)}",
            f"  source_execution_status: {_pf(self.no_unjustified_sources)}",
            f"  template_contamination: {_pf(self.no_template_contamination)}",
            f"  fallback_governance: {_pf(self.no_prohibited_fallback)}",
            f"  qa_score_client_safe: {_pf(self.qa_client_safe)}",
        ])
        return "\n".join(lines)


def evaluate_render_gate(
    *,
    state: str,
    qa_card: QAScoreCard | None = None,
    fallback_verdict: FallbackPolicyVerdict | Mapping[str, Any] | None = None,
    source_audit: SourceExecutionAuditReport | None = None,
    claim_sync: ClaimSyncReport | None = None,
    isolation_violations: list[Mapping[str, Any]] | None = None,
    template_contamination_failure: bool = False,
    pipeline_inputs: Mapping[str, Any] | None = None,
) -> RenderGateVerdict:
    """Evaluate ALL V6 gates and return a single allow/refuse verdict.

    Strict mode (V6 default) requires every gate green AND state == client_safe.
    Soft mode reverts to V2-style "any non-blocked green state is fine".
    """
    strict = strict_mode_active(pipeline_inputs)
    reasons: list[str] = []
    state_norm = (state or "").strip()

    # ── 1. State must be allowed in current mode ──────────────────
    allowed_states = (
        STRICT_CLIENT_SAFE_RENDER_STATES if strict else DEFAULT_ALLOWED_RENDER_STATES
    )
    state_in_allowed = state_norm in allowed_states
    if not state_in_allowed:
        reasons.append(
            f"state={state_norm!r} not in allowed_states={list(allowed_states)} "
            f"(strict_mode={strict})"
        )

    # ── 2. QA card.client_safe (only enforced in strict mode) ─────
    qa_client_safe = bool(qa_card and qa_card.client_safe)
    if strict and not qa_client_safe:
        if qa_card is None:
            reasons.append("strict mode requires QAScoreCard; got None")
        else:
            reasons.append(
                f"QA card.client_safe=False "
                f"(overall_score={qa_card.overall_score:.3f}, "
                f"decision_blocked={qa_card.decision_blocked})"
            )

    # ── 3. Fallback verdict — no prohibited events ────────────────
    no_prohibited_fallback = True
    # V8 P7 — high-value section downgrades. Even one downgrade in
    # {Executive Thesis, TAD, Financial Exposure, Peer Comparison,
    # Conditional Redesign, Case Adaptation Memo} refuses client_safe.
    high_value_downgrades = 0
    if isinstance(fallback_verdict, FallbackPolicyVerdict):
        no_prohibited_fallback = fallback_verdict.prohibited_count == 0
        high_value_downgrades = fallback_verdict.high_value_section_downgrades
        if not no_prohibited_fallback:
            reasons.append(
                f"fallback_verdict has {fallback_verdict.prohibited_count} "
                f"prohibited event(s)"
            )
        if strict and high_value_downgrades > 0:
            no_prohibited_fallback = False
            reasons.append(
                f"V8 P7: {high_value_downgrades} high-value section(s) "
                f"downgraded ({list(fallback_verdict.affected_high_value_sections)})"
            )
    elif isinstance(fallback_verdict, Mapping):
        prohibited_n = int(fallback_verdict.get("prohibited_count", 0) or 0)
        high_value_downgrades = int(
            fallback_verdict.get("high_value_section_downgrades", 0) or 0
        )
        no_prohibited_fallback = prohibited_n == 0
        if not no_prohibited_fallback:
            reasons.append(f"fallback verdict reports {prohibited_n} prohibited event(s)")
        if strict and high_value_downgrades > 0:
            no_prohibited_fallback = False
            affected = fallback_verdict.get("affected_high_value_sections", []) or []
            reasons.append(
                f"V8 P7: {high_value_downgrades} high-value section(s) "
                f"downgraded ({list(affected)})"
            )

    # ── 4. Source audit — no unjustified mandatory gaps ───────────
    no_unjustified_sources = True
    if source_audit is not None:
        unjustified_n = len(source_audit.unjustified_gaps)
        # V8 P6 — tier-aware: only IDENTITY / PERMIT_EMISSIONS gaps block
        # client_safe by default. BENCHMARK / REFERENCE / OTHER tolerable.
        cs_compatible, blocking_reasons = client_safe_compatible(source_audit)
        no_unjustified_sources = unjustified_n == 0 if not strict else (
            cs_compatible and unjustified_n == 0
        )
        # In strict mode, blocking-tier gaps refuse render even if total
        # unjustified count is small. In soft mode, only any gap fires.
        if strict and not cs_compatible:
            reasons.extend(blocking_reasons)
            no_unjustified_sources = False
        elif unjustified_n > 0:
            reasons.append(
                f"source_audit has {unjustified_n} unjustified mandatory gap(s)"
            )
            no_unjustified_sources = False

    # ── 5. Claim synchronization across motors ────────────────────
    claims_in_sync = True
    if claim_sync is not None:
        claims_in_sync = bool(claim_sync.consistent)
        if not claims_in_sync:
            reasons.append(
                f"claim_sync inconsistent (baseline={claim_sync.expected_baseline}, "
                f"max_divergence={claim_sync.max_divergence})"
            )

    # ── 6. Pattern isolation violations ───────────────────────────
    no_isolation_violations = True
    if isolation_violations:
        no_isolation_violations = False
        reasons.append(
            f"pattern isolation has {len(isolation_violations)} contamination "
            f"violation(s) (first: {isolation_violations[0].get('pattern_id')})"
        )

    # ── 7. V8 P1 template contamination hard block ────────────────
    # motor_016 / case_adaptation_memo flags this when the report is
    # being assembled from a template heritage that was never specialized
    # for the current case. V8 doctrine: this is ALWAYS a hard block
    # (even in soft mode), unless caller explicitly says
    # __template_contamination_force_render__ = True (debug only).
    no_template_contamination = not bool(template_contamination_failure)
    force_template = bool(
        (pipeline_inputs or {}).get("__template_contamination_force_render__")
    )
    if template_contamination_failure and not force_template:
        reasons.append(
            "template_contamination_failure=True (case_adaptation_memo carries "
            "heritage from another case; render blocked per V8 P1 doctrine)"
        )

    # ── Final verdict ─────────────────────────────────────────────
    template_ok = no_template_contamination or force_template
    if strict:
        allowed = (
            state_in_allowed
            and qa_client_safe
            and no_prohibited_fallback
            and no_unjustified_sources
            and claims_in_sync
            and no_isolation_violations
            and template_ok
        )
    else:
        # Soft mode: allow render if state is in soft allowed states AND no
        # hard contamination (prohibited fallback, claim_sync, isolation,
        # or template). Template contamination is hard-block in BOTH modes.
        allowed = (
            state_in_allowed
            and no_prohibited_fallback
            and claims_in_sync
            and no_isolation_violations
            and template_ok
        )

    return RenderGateVerdict(
        allowed=allowed,
        strict_mode=strict,
        state=state_norm,
        reasons=tuple(reasons),
        qa_client_safe=qa_client_safe,
        state_in_allowed=state_in_allowed,
        no_prohibited_fallback=no_prohibited_fallback,
        no_unjustified_sources=no_unjustified_sources,
        claims_in_sync=claims_in_sync,
        no_isolation_violations=no_isolation_violations,
        no_template_contamination=no_template_contamination,
    )


class RenderGateRefusal(Exception):
    """Raised when callers want exception-style strict enforcement."""

    def __init__(self, verdict: RenderGateVerdict) -> None:
        super().__init__(
            f"RenderGateRefusal (strict_mode={verdict.strict_mode}): "
            f"{'; '.join(verdict.reasons) or 'all gates clean but state not in allowed set'}"
        )
        self.verdict = verdict


def enforce_render_gate(**kwargs: Any) -> RenderGateVerdict:
    """Evaluate the gate and raise RenderGateRefusal if not allowed."""
    verdict = evaluate_render_gate(**kwargs)
    if not verdict.allowed:
        raise RenderGateRefusal(verdict)
    return verdict
