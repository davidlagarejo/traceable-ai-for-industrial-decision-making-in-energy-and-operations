"""Adapter for motor_059 — Strategic Intelligence Validator (Layer F).

Detects structural-coherence violations in the strategic outputs produced by
upstream motors (TAD, claim governor, dominant variables). Emits non-blocking
warnings today; promotion to hard blocks happens in a later recovery phase.

Rules implemented (RECOVERY_ARCHITECTURE_PLAN.md §10.A):
  R1 — Allowed claim with empty falsification_condition.
  R2 — TAD ACT NOW action whose linked claim is prohibited.
  R3 — DO NOT MODEL YET coexisting with redesign-related ACT NOW (informational).
  R4 — Dominant variable marked OBSERVED_FACT with no supporting evidence.
"""
from __future__ import annotations

from typing import Any

from .base import BaseMotorAdapter
from ..validator_severity_policy import effective_severity


_ACT_NOW_STATUSES = {"ACT NOW"}
_REDESIGN_RELATED_ACTIONS = {
    "Advance bounded redesign hypothesis",
    "Compare against structural peers",
    "Request discriminating evidence pack",
}
_DO_NOT_MODEL_TARGET = "Build detailed system model / digital twin"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _detect_missing_falsification(claim_register: list[dict]) -> list[dict]:
    out: list[dict] = []
    for claim in claim_register:
        if not isinstance(claim, dict):
            continue
        permission = _text(claim.get("permission"))
        if permission != "allowed":
            continue
        if _text(claim.get("falsification_condition")):
            continue
        out.append(
            {
                "rule_id": "R1_missing_falsification",
                "severity": "warning",
                "claim_id": _text(claim.get("claim_id")),
                "description": (
                    "Claim is permitted but lacks an explicit falsification_condition; "
                    "downstream readers cannot test what would unbind the claim."
                ),
            }
        )
    return out


def _detect_act_now_with_prohibited_claim(
    actions: list[dict],
    claim_permissions: dict[str, str],
) -> list[dict]:
    out: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if _text(action.get("status")) not in _ACT_NOW_STATUSES:
            continue
        linked_claim = _text(action.get("linked_claim"))
        if not linked_claim:
            continue
        permission = claim_permissions.get(linked_claim, "")
        if permission == "prohibited":
            out.append(
                {
                    "rule_id": "R2_act_now_with_prohibited_claim",
                    "severity": "warning",
                    "action": _text(action.get("action")),
                    "linked_claim": linked_claim,
                    "description": (
                        "TAD action is ACT NOW yet its linked claim is prohibited. "
                        "Either downgrade the action or upgrade the claim permission."
                    ),
                }
            )
    return out


def _detect_do_not_model_with_active_redesign(actions: list[dict]) -> list[dict]:
    do_not_model = any(
        isinstance(a, dict)
        and _text(a.get("action")) == _DO_NOT_MODEL_TARGET
        and _text(a.get("status")) == "DO NOT MODEL YET"
        for a in actions
    )
    if not do_not_model:
        return []
    redesign_act_now = [
        _text(a.get("action"))
        for a in actions
        if isinstance(a, dict)
        and _text(a.get("action")) in _REDESIGN_RELATED_ACTIONS
        and _text(a.get("status")) in _ACT_NOW_STATUSES
    ]
    if not redesign_act_now:
        return []
    return [
        {
            "rule_id": "R3_do_not_model_with_active_redesign",
            "severity": "info",
            "description": (
                "TAD plan declares DO NOT MODEL YET while another action is ACT NOW. "
                "These are not strictly contradictory but indicate incoherent posture; "
                "verify the report does not narrate them as simultaneous immediate actions."
            ),
            "concurrent_act_now_actions": redesign_act_now,
        }
    ]


def _detect_observed_fact_without_evidence(dominant_variables: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in dominant_variables:
        if not isinstance(row, dict):
            continue
        if _text(row.get("evidence_state")) != "OBSERVED_FACT":
            continue
        evidence = row.get("supporting_evidence") or row.get("evidence")
        if isinstance(evidence, list) and evidence:
            continue
        if isinstance(evidence, str) and _text(evidence):
            continue
        out.append(
            {
                "rule_id": "R4_observed_fact_without_evidence",
                "severity": "warning",
                "variable": _text(row.get("variable")),
                "description": (
                    "Dominant variable is marked OBSERVED_FACT but no supporting "
                    "evidence is attached. Either downgrade to CONDITIONAL_HYPOTHESIS "
                    "or attach the evidence reference."
                ),
            }
        )
    return out


# V3 G2: Governance Sync rules — detect contradictions BETWEEN layers
# (TAD ↔ claims ↔ charts ↔ counts). R5/R6/R7 fire when the framework is
# contradicting itself across layers; they are severity=error so motor_017
# blocks render.


def _detect_chart_implies_prohibited_claim(
    chart_assets: list[dict],
    claim_permissions: dict[str, str],
) -> list[dict]:
    """R5: chart's intelligence_binding references a claim_id whose
    permission is 'prohibited'. Charts must not visually support claims
    the claim governor has blocked from closure."""
    out: list[dict] = []
    prohibited_ids = {cid for cid, perm in claim_permissions.items() if perm == "prohibited"}
    if not prohibited_ids:
        return out
    for asset in chart_assets:
        if not isinstance(asset, dict):
            continue
        binding = asset.get("intelligence_binding") or asset.get("chart_intelligence_binding") or {}
        if not isinstance(binding, dict):
            continue
        for key in ("claim_id", "hypothesis_id", "thesis_anchor"):
            ref = _text(binding.get(key))
            if ref and ref in prohibited_ids:
                out.append(
                    {
                        "rule_id": "R5_chart_implies_prohibited_claim",
                        "severity": "error",
                        "chart_id": _text(asset.get("chart_id") or asset.get("asset_id")),
                        "linked_claim": ref,
                        "description": (
                            f"Chart visually supports a prohibited claim "
                            f"({ref}). The claim governor blocks closure on "
                            "this claim; the chart must not imply admissibility."
                        ),
                    }
                )
                break
    return out


def _detect_nugget_implies_superiority_when_blocked(
    nuggets: list[dict],
    fair_comparison_state: dict,
) -> list[dict]:
    """R6: gold nugget uses superiority language while fair_comparison has
    blocked peer-superiority closure for this case."""
    out: list[dict] = []
    superiority_blocked = bool(
        fair_comparison_state.get("peer_superiority_blocked")
        or fair_comparison_state.get("comparison_blocked")
        or fair_comparison_state.get("invalid_peer_set")
    )
    if not superiority_blocked:
        return out
    superiority_markers = ("outperforms", "best-in-class", "top-quartile", "leading peer", "superior to")
    for n in nuggets:
        if not isinstance(n, dict):
            continue
        text = _text(n.get("gold_nugget") or n.get("nugget")).lower()
        if not text:
            continue
        hit = next((m for m in superiority_markers if m in text), None)
        if hit:
            out.append(
                {
                    "rule_id": "R6_nugget_implies_superiority_when_blocked",
                    "severity": "error",
                    "nugget_id": _text(n.get("nugget_id")),
                    "marker": hit,
                    "description": (
                        f"Gold nugget uses superiority language ('{hit}') "
                        "while fair_comparison has blocked peer-superiority "
                        "closure for this case."
                    ),
                }
            )
    return out


def _detect_claim_count_mismatch(
    claim_register: list[dict],
    actions: list[dict],
    governance_summary: dict,
) -> list[dict]:
    """R7: claim counts diverge across layers (claim_register, TAD-linked,
    governance_summary). Tolerance of 1 to absorb in-flight pending claims."""
    out: list[dict] = []
    claim_layer_count = len(claim_register)
    tad_linked_count = len({
        _text(a.get("linked_claim"))
        for a in actions
        if isinstance(a, dict) and _text(a.get("linked_claim"))
    })
    governance_count = int(governance_summary.get("governed_claim_contract_count", 0) or 0)
    counts = [claim_layer_count, tad_linked_count, governance_count]
    if max(counts) - min(counts) > 1:
        out.append(
            {
                "rule_id": "R7_claim_count_mismatch_across_layers",
                "severity": "error",
                "claim_layer_count": claim_layer_count,
                "tad_linked_count": tad_linked_count,
                "governance_count": governance_count,
                "description": (
                    f"Claim count diverges across layers: "
                    f"claim_register={claim_layer_count}, "
                    f"TAD-linked={tad_linked_count}, "
                    f"governance_summary={governance_count}. "
                    "Layers must agree on how many governed claims exist."
                ),
            }
        )
    return out


# V6 P8 — Hard precedence rules R8-R11.
# These enforce that certain TAD actions / claim types are forbidden
# until specific upstream conditions resolve. Phase 0 anchor: prevent
# epistemic jumps (benchmark → savings verified, etc.).


_DIGITAL_TWIN_TOKENS: frozenset[str] = frozenset({
    "digital twin", "digital_twin", "twin model", "simulation model",
    "build twin", "deploy twin",
})

_ROI_CLAIM_TOKENS: frozenset[str] = frozenset({
    "roi", "payback", "savings", "irr", "npv", "bankable",
    "verified savings",
})

_PEER_SUPERIORITY_TOKENS: frozenset[str] = frozenset({
    "outperform", "better than peer", "superior to peer", "peer superiority",
    "best in class", "top quartile",
})

_VERIFIED_SAVINGS_TOKENS: frozenset[str] = frozenset({
    "verified savings", "guaranteed savings", "savings verified",
    "performance verified", "verified retrofit savings",
})

# V7 P5 — R12 local-truth-from-archetypal-prior detection tokens.
# A claim that states a LOCAL truth ("this facility consumes X kWh/sf",
# "this site is X% inefficient") is forbidden when the only support is
# an archetypal prior (no observed evidence locally).
_LOCAL_TRUTH_TOKENS: frozenset[str] = frozenset({
    "this facility consumes", "this site consumes", "this facility uses",
    "this facility is", "this site is", "this facility's eui",
    "this site's eui", "this asset consumes", "facility-level intensity",
    "site-level intensity", "this building consumes",
})

# V7 P5 — R13 benchmark-as-truth detection tokens.
# A claim that invokes "industry benchmark" as proof of inefficiency or
# savings opportunity is forbidden — benchmarks are reference distributions,
# not local-truth oracles.
_BENCHMARK_AS_TRUTH_TOKENS: frozenset[str] = frozenset({
    "below benchmark", "below industry benchmark", "below the benchmark",
    "underperforms benchmark", "benchmark says", "benchmark proves",
    "benchmark shows inefficiency", "vs industry benchmark", "industry-benchmark gap",
    "benchmark gap means savings", "below median", "below the median benchmark",
    "above benchmark suggests waste",
})


def _action_mentions_any(action: dict, tokens: frozenset[str]) -> bool:
    """True if any action text field contains any of the given tokens."""
    blob = " ".join(
        _text(action.get(f, "")).lower()
        for f in ("action_title", "action_family", "recommended_posture",
                  "decision_unlock", "evidence_needed", "sequencing_note")
    )
    return any(t in blob for t in tokens)


def _detect_R8_digital_twin_when_dominant_unresolved(
    actions: list[dict],
    dominant_variables: list[dict],
) -> list[dict]:
    """R8: forbid digital_twin TAD actions when ≥1 dominant variable
    is unresolved (evidence_state in {ARCHETYPAL_PRIOR, WEAK_SIGNAL,
    CONDITIONAL_HYPOTHESIS} and no supporting evidence)."""
    unresolved = [
        v for v in dominant_variables
        if isinstance(v, dict)
        and _text(v.get("evidence_state")) not in ("OBSERVED_FACT", "")
    ]
    if not unresolved:
        return []
    out: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if _action_mentions_any(action, _DIGITAL_TWIN_TOKENS):
            out.append({
                "rule_id": "R8_digital_twin_with_unresolved_dominant_variable",
                "severity": "warning",
                "action_id": _text(action.get("action_id") or action.get("case_id")),
                "unresolved_variable_count": len(unresolved),
                "description": (
                    f"TAD action proposes digital twin / simulation work but "
                    f"{len(unresolved)} dominant variable(s) are still unresolved. "
                    "Digital twin work is forbidden until dominant variables harden."
                ),
            })
    return out


def _detect_R9_roi_when_control_boundary_unresolved(
    actions: list[dict],
    dominant_variables: list[dict],
) -> list[dict]:
    """R9: forbid ROI/payback/savings claims when control_boundary is
    unresolved. Detection: dominant_variable name contains 'control' or
    'boundary' AND evidence_state != OBSERVED_FACT."""
    control_boundary_resolved = False
    for v in dominant_variables:
        if not isinstance(v, dict):
            continue
        name = _text(v.get("variable")).lower()
        if "control" in name or "boundary" in name or "tenant" in name:
            if _text(v.get("evidence_state")) == "OBSERVED_FACT":
                control_boundary_resolved = True
                break
    if control_boundary_resolved:
        return []
    out: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if _action_mentions_any(action, _ROI_CLAIM_TOKENS):
            out.append({
                "rule_id": "R9_roi_claim_with_unresolved_control_boundary",
                "severity": "warning",
                "action_id": _text(action.get("action_id") or action.get("case_id")),
                "description": (
                    "TAD action references ROI/payback/savings but the asset's "
                    "control boundary (owner vs tenant / metering responsibility) "
                    "is not yet resolved. ROI claims are forbidden until the "
                    "control boundary is observed locally."
                ),
            })
    return out


def _detect_R10_peer_superiority_when_normalization_incomplete(
    actions: list[dict],
    motor_051: dict,
) -> list[dict]:
    """R10: forbid peer_superiority claims when fair comparison
    normalization is incomplete (motor_051 reports invalid comparison
    risks or missing peer-set normalization)."""
    invalid_risks = list(motor_051.get("invalid_comparison_risk_register", []) or [])
    not_yet_valid = list(motor_051.get("comparison_not_yet_valid_register", []) or [])
    normalization_incomplete = bool(invalid_risks) or bool(not_yet_valid)
    if not normalization_incomplete:
        return []
    out: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if _action_mentions_any(action, _PEER_SUPERIORITY_TOKENS):
            out.append({
                "rule_id": "R10_peer_superiority_with_incomplete_normalization",
                "severity": "warning",
                "action_id": _text(action.get("action_id") or action.get("case_id")),
                "invalid_risk_count": len(invalid_risks),
                "not_yet_valid_count": len(not_yet_valid),
                "description": (
                    "TAD action implies peer superiority / best-in-class but the "
                    "fair-comparison normalization is incomplete. Peer superiority "
                    "claims are forbidden until normalization completes."
                ),
            })
    return out


def _detect_R11_verified_savings_when_baseline_soft(
    actions: list[dict],
    financial_exposure_register: list[dict],
) -> list[dict]:
    """R11: forbid verified_savings claims when baseline_dependency_state
    is not 'hardened' (V5 P13 Phase 5 financial_exposure_case). Detection:
    any motor_045 financial_exposure_case has baseline_dependency_state
    != 'hardened' AND a TAD action mentions verified-savings tokens."""
    baseline_hardened = False
    for row in financial_exposure_register or []:
        if not isinstance(row, dict):
            continue
        state = _text(row.get("baseline_dependency_state")).lower()
        if state == "hardened":
            baseline_hardened = True
            break
    if baseline_hardened:
        return []
    out: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if _action_mentions_any(action, _VERIFIED_SAVINGS_TOKENS):
            out.append({
                "rule_id": "R11_verified_savings_with_soft_baseline",
                "severity": "warning",
                "action_id": _text(action.get("action_id") or action.get("case_id")),
                "description": (
                    "TAD action carries verified-savings / guaranteed-savings "
                    "language but no Phase 5 financial_exposure_case reports "
                    "a 'hardened' baseline_dependency_state. Verified savings "
                    "claims are forbidden until baseline is locally hardened."
                ),
            })
    return out


def _detect_R12_local_truth_from_archetypal_prior(
    claims: list[dict],
    actions: list[dict],
) -> list[dict]:
    """R12: forbid local-truth claims (e.g. "this facility consumes X kWh/sf")
    when the supporting evidence state is ARCHETYPAL_PRIOR or WEAK_SIGNAL.

    Detection: any claim or TAD action whose text contains a local-truth
    token AND whose evidence_state (or supporting evidence_state on the
    linked claim) is in the archetypal/weak set.
    """
    archetypal_states = {"ARCHETYPAL_PRIOR", "WEAK_SIGNAL", "UNRESOLVED"}
    out: list[dict] = []
    # Scan claims directly.
    for claim in claims or []:
        if not isinstance(claim, dict):
            continue
        blob = " ".join(
            _text(claim.get(f, "")).lower()
            for f in ("claim_text", "claim_language", "narrative",
                      "description", "permission_rationale")
        )
        if not any(t in blob for t in _LOCAL_TRUTH_TOKENS):
            continue
        ev_state = _text(claim.get("evidence_state")).upper()
        if ev_state in archetypal_states or ev_state == "":
            out.append({
                "rule_id": "R12_local_truth_from_archetypal_prior",
                "severity": "warning",
                "claim_id": _text(claim.get("claim_id") or claim.get("case_id")),
                "evidence_state": ev_state or "UNRESOLVED",
                "description": (
                    "Claim asserts a LOCAL truth about this facility "
                    "without observed evidence — only an archetypal / "
                    "weak prior supports it. Local-truth framings require "
                    "hardened evidence, not archetypal inheritance."
                ),
            })
    # Scan TAD actions too (some local-truth language leaks into TAD posture).
    for action in actions or []:
        if not isinstance(action, dict):
            continue
        if _action_mentions_any(action, _LOCAL_TRUTH_TOKENS):
            ev_state = _text(action.get("evidence_state")).upper()
            if ev_state in archetypal_states or ev_state == "":
                out.append({
                    "rule_id": "R12_local_truth_from_archetypal_prior",
                    "severity": "warning",
                    "action_id": _text(action.get("action_id") or action.get("case_id")),
                    "evidence_state": ev_state or "UNRESOLVED",
                    "description": (
                        "TAD action carries local-truth framing without "
                        "observed evidence to support it."
                    ),
                })
    return out


def _detect_R13_benchmark_as_truth(
    claims: list[dict],
    actions: list[dict],
) -> list[dict]:
    """R13: forbid claims that invoke industry benchmark as proof of
    local inefficiency or savings opportunity. Benchmarks describe
    distributions; they are not local-truth oracles."""
    out: list[dict] = []
    for claim in claims or []:
        if not isinstance(claim, dict):
            continue
        blob = " ".join(
            _text(claim.get(f, "")).lower()
            for f in ("claim_text", "claim_language", "narrative",
                      "description", "permission_rationale")
        )
        if any(t in blob for t in _BENCHMARK_AS_TRUTH_TOKENS):
            out.append({
                "rule_id": "R13_benchmark_as_truth",
                "severity": "warning",
                "claim_id": _text(claim.get("claim_id") or claim.get("case_id")),
                "description": (
                    "Claim invokes industry benchmark as proof of local "
                    "inefficiency or savings. Benchmarks are reference "
                    "distributions — they do NOT establish local truth. "
                    "Rephrase as a fair-comparison hypothesis or remove."
                ),
            })
    for action in actions or []:
        if not isinstance(action, dict):
            continue
        if _action_mentions_any(action, _BENCHMARK_AS_TRUTH_TOKENS):
            out.append({
                "rule_id": "R13_benchmark_as_truth",
                "severity": "warning",
                "action_id": _text(action.get("action_id") or action.get("case_id")),
                "description": (
                    "TAD action treats industry benchmark as truth signal. "
                    "Benchmark gap is not equivalent to a local inefficiency."
                ),
            })
    return out


class Motor059Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_059"

    @property
    def input_motor_ids(self) -> list[str]:
        # V3 G2: also read motor_016 (governance_summary), motor_018 (chart
        # assets), motor_051 (fair comparison state).
        # V6 P8: also read motor_045 for Phase 5 financial_exposure_case_register
        # to enforce R11 (verified_savings_when_baseline_soft).
        return ["motor_016", "motor_018", "motor_033", "motor_038", "motor_045", "motor_051", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m016 = inputs.get("motor_016", {}) if isinstance(inputs.get("motor_016", {}), dict) else {}
        m018 = inputs.get("motor_018", {}) if isinstance(inputs.get("motor_018", {}), dict) else {}
        m033 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m038 = inputs.get("motor_038", {}) if isinstance(inputs.get("motor_038", {}), dict) else {}
        m045 = inputs.get("motor_045", {}) if isinstance(inputs.get("motor_045", {}), dict) else {}
        m051 = inputs.get("motor_051", {}) if isinstance(inputs.get("motor_051", {}), dict) else {}
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        claim_register = list(m054.get("congruence_claim_contract_register", []) or [])
        actions = list(m033.get("expanded_structural_tad_action_register", []) or [])
        dominant_variables = list(m038.get("dominant_variable_register", []) or [])
        chart_assets = list(m018.get("chart_assets", []) or [])
        report_package = m016.get("report_package", {}) if isinstance(m016.get("report_package", {}), dict) else {}
        governance_summary = report_package.get("governance_summary", {}) if isinstance(report_package.get("governance_summary", {}), dict) else {}
        nuggets = list(
            m054.get("strategic_gold_nugget_register")
            or m054.get("gold_nugget_register")
            or []
        )

        claim_permissions: dict[str, str] = {
            _text(c.get("claim_id")): _text(c.get("permission"))
            for c in claim_register
            if isinstance(c, dict) and _text(c.get("claim_id"))
        }

        warnings: list[dict] = []
        warnings.extend(_detect_missing_falsification(claim_register))
        # R2 + R3 promoted to severity=error in V3 G2 (cross-layer contradictions)
        r2_hits = _detect_act_now_with_prohibited_claim(actions, claim_permissions)
        for w in r2_hits:
            w["severity"] = "error"
        warnings.extend(r2_hits)
        r3_hits = _detect_do_not_model_with_active_redesign(actions)
        for w in r3_hits:
            w["severity"] = "error"
        warnings.extend(r3_hits)
        warnings.extend(_detect_observed_fact_without_evidence(dominant_variables))
        # V3 G2: new governance-sync rules
        warnings.extend(_detect_chart_implies_prohibited_claim(chart_assets, claim_permissions))
        warnings.extend(_detect_nugget_implies_superiority_when_blocked(nuggets, m051))
        warnings.extend(_detect_claim_count_mismatch(claim_register, actions, governance_summary))
        # V6 P8: hard precedence rules R8-R11.
        warnings.extend(_detect_R8_digital_twin_when_dominant_unresolved(actions, dominant_variables))
        warnings.extend(_detect_R9_roi_when_control_boundary_unresolved(actions, dominant_variables))
        warnings.extend(_detect_R10_peer_superiority_when_normalization_incomplete(actions, m051))
        warnings.extend(_detect_R11_verified_savings_when_baseline_soft(
            actions, list(m045.get("financial_exposure_case_register", []) or [])
        ))
        # V7 P5: epistemic guardrails — local truth from archetypal prior +
        # benchmark-as-truth.
        warnings.extend(_detect_R12_local_truth_from_archetypal_prior(claim_register, actions))
        warnings.extend(_detect_R13_benchmark_as_truth(claim_register, actions))

        # V6 P4.8: apply validator_severity_policy gate (soft-mode no-op).
        # R2/R3 already promoted to "error" in V3 G2 above; gate respects
        # explicit severity if already non-warning. Hard mode promotes
        # R1, R2, R4 (per V6 blocking set) further to "blocking".
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        for w in warnings:
            rid = str(w.get("rule_id", ""))
            sev = str(w.get("severity", "warning"))
            w["severity"] = effective_severity(
                self.motor_id, rid, sev, pipeline_inputs=pipeline_inputs
            )
        blocking_count = sum(1 for w in warnings if w.get("severity") == "blocking")
        warning_count_pure = sum(1 for w in warnings if w.get("severity") == "warning")

        return {
            "strategic_intelligence_warnings": warnings,
            "warning_count": len(warnings),
            "blocking_violations": blocking_count,
            "warning_violations": warning_count_pure,
            "warning_count_by_severity": {
                "warning": sum(1 for w in warnings if w.get("severity") == "warning"),
                "info": sum(1 for w in warnings if w.get("severity") == "info"),
                "error": sum(1 for w in warnings if w.get("severity") == "error"),
            },
            "rules_evaluated": [
                "R1_missing_falsification",
                "R2_act_now_with_prohibited_claim",
                "R3_do_not_model_with_active_redesign",
                "R4_observed_fact_without_evidence",
                "R5_chart_implies_prohibited_claim",
                "R6_nugget_implies_superiority_when_blocked",
                "R7_claim_count_mismatch_across_layers",
            ],
        }
