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


class Motor059Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_059"

    @property
    def input_motor_ids(self) -> list[str]:
        # V3 G2: also read motor_016 (governance_summary), motor_018 (chart
        # assets), motor_051 (fair comparison state).
        return ["motor_016", "motor_018", "motor_033", "motor_038", "motor_051", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m016 = inputs.get("motor_016", {}) if isinstance(inputs.get("motor_016", {}), dict) else {}
        m018 = inputs.get("motor_018", {}) if isinstance(inputs.get("motor_018", {}), dict) else {}
        m033 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m038 = inputs.get("motor_038", {}) if isinstance(inputs.get("motor_038", {}), dict) else {}
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
