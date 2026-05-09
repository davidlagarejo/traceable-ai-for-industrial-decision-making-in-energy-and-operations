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


class Motor059Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_059"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_033", "motor_038", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m033 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m038 = inputs.get("motor_038", {}) if isinstance(inputs.get("motor_038", {}), dict) else {}
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        claim_register = list(m054.get("congruence_claim_contract_register", []) or [])
        actions = list(m033.get("expanded_structural_tad_action_register", []) or [])
        dominant_variables = list(m038.get("dominant_variable_register", []) or [])

        claim_permissions: dict[str, str] = {
            _text(c.get("claim_id")): _text(c.get("permission"))
            for c in claim_register
            if isinstance(c, dict) and _text(c.get("claim_id"))
        }

        warnings: list[dict] = []
        warnings.extend(_detect_missing_falsification(claim_register))
        warnings.extend(_detect_act_now_with_prohibited_claim(actions, claim_permissions))
        warnings.extend(_detect_do_not_model_with_active_redesign(actions))
        warnings.extend(_detect_observed_fact_without_evidence(dominant_variables))

        return {
            "strategic_intelligence_warnings": warnings,
            "warning_count": len(warnings),
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
            ],
        }
