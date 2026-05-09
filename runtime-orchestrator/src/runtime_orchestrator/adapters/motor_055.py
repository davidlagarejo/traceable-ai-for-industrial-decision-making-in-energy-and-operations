"""Adapter for motor_055 — Hypothesis Diversity Validator (Layer F).

Detects low-diversity patterns in the activated hypothesis set produced by
upstream Layer-B/C motors. Without cross-run history, this is a within-run
validator: it flags signatures that suggest the report would land on a
single hypothesis even when multiple should compete.

Rules:
  HD1 — Fewer than 2 active claims emitted by the claim governor.
  HD2 — Two or more claims share the same (claim_family, current_evidence_summary)
        signature, i.e. the framework is producing duplicates under different ids.
  HD3 — All actionable TAD priorities point to the same `linked_claim`,
        meaning the action plan converges to one bet.

Hard-block promotion is deferred until the orchestrator gains
structured-error handling.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .base import BaseMotorAdapter


def _text(value: Any) -> str:
    return str(value or "").strip()


def _detect_low_claim_count(claim_register: list[dict]) -> list[dict]:
    allowed = [c for c in claim_register if isinstance(c, dict) and _text(c.get("permission")) == "allowed"]
    if len(allowed) >= 2:
        return []
    return [
        {
            "rule_id": "HD1_low_claim_count",
            "severity": "warning",
            "claim_count": len(allowed),
            "description": (
                "Fewer than 2 allowed claims are active. The report risks converging "
                "on a single bet without rival hypotheses to falsify."
            ),
        }
    ]


def _detect_duplicate_signatures(claim_register: list[dict]) -> list[dict]:
    signatures: Counter = Counter()
    for claim in claim_register:
        if not isinstance(claim, dict):
            continue
        family = _text(claim.get("claim_family"))
        summary = _text(claim.get("current_evidence_summary"))
        if not family or not summary:
            continue
        signatures[(family, summary)] += 1
    out: list[dict] = []
    for (family, summary), count in signatures.items():
        if count >= 2:
            out.append(
                {
                    "rule_id": "HD2_duplicate_claim_signature",
                    "severity": "warning",
                    "claim_family": family,
                    "duplicate_count": count,
                    "description": (
                        "Multiple claims share the same family and current evidence "
                        "summary. They likely represent the same hypothesis under "
                        "different ids; merge or differentiate."
                    ),
                }
            )
    return out


def _detect_tad_action_convergence(actions: list[dict]) -> list[dict]:
    actionable = [
        a for a in actions
        if isinstance(a, dict)
        and _text(a.get("status")) in {"ACT NOW", "VALIDATE FIRST", "REDESIGN HYPOTHESIS"}
    ]
    if len(actionable) < 2:
        return []
    linked = [_text(a.get("linked_claim")) for a in actionable]
    linked = [c for c in linked if c]
    if not linked:
        return []
    distinct = set(linked)
    if len(distinct) == 1:
        return [
            {
                "rule_id": "HD3_tad_action_convergence",
                "severity": "warning",
                "single_linked_claim": next(iter(distinct)),
                "actionable_count": len(actionable),
                "description": (
                    "All actionable TAD priorities point to the same linked claim. "
                    "The report would render as a single-bet action plan even though "
                    "multiple actions are listed."
                ),
            }
        ]
    return []


class Motor055Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_055"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_033", "motor_054"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m033 = inputs.get("motor_033", {}) if isinstance(inputs.get("motor_033", {}), dict) else {}
        m054 = inputs.get("motor_054", {}) if isinstance(inputs.get("motor_054", {}), dict) else {}

        claim_register = list(m054.get("congruence_claim_contract_register", []) or [])
        actions = list(m033.get("expanded_structural_tad_action_register", []) or [])

        warnings: list[dict] = []
        warnings.extend(_detect_low_claim_count(claim_register))
        warnings.extend(_detect_duplicate_signatures(claim_register))
        warnings.extend(_detect_tad_action_convergence(actions))

        return {
            "hypothesis_diversity_warnings": warnings,
            "warning_count": len(warnings),
            "rules_evaluated": [
                "HD1_low_claim_count",
                "HD2_duplicate_claim_signature",
                "HD3_tad_action_convergence",
            ],
        }
