from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_competitive_comparison_register
from .base import BaseMotorAdapter


def _allowed_verbs_for_state(evidence_state: str) -> list[str]:
    """Map evidence_state to the verbs the composer is allowed to use.

    Conservative defaults aligned with the four-state epistemic model:
      - OBSERVED_FACT: 'is', 'shows'
      - CONDITIONAL_HYPOTHESIS: 'may', 'is consistent with'
      - ARCHETYPAL_PRIOR: 'structurally suggests', 'archetypally implies'
      - WEAK_SIGNAL: 'might', 'is loosely consistent with'
      - default: ['may'] (most conservative non-prohibited verb)
    """
    state = (evidence_state or "").strip().upper()
    if state == "OBSERVED_FACT":
        return ["is", "shows"]
    if state == "CONDITIONAL_HYPOTHESIS":
        return ["may", "is consistent with"]
    if state == "ARCHETYPAL_PRIOR":
        return ["structurally suggests", "archetypally implies"]
    if state == "WEAK_SIGNAL":
        return ["might", "is loosely consistent with"]
    return ["may"]


class Motor043Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_043"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_039", "motor_042", "motor_051"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        target_definition = (
            inputs.get("motor_012", {}).get("facility_prior", {}).get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )
        register = build_competitive_comparison_register(
            target_definition=target_definition,
            archetype_resolution=dict(inputs.get("motor_039", {}).get("archetype_resolution", {}) or {}),
            structural_benchmark_register=list(inputs.get("motor_042", {}).get("structural_benchmark_register", []) or []),
        )
        # R-59: enrich each comparison row with allowed_verbs derived from
        # its evidence_state. The composer can then render the peer
        # comparison section with bounded language instead of leaving
        # cap. 8 of the PDF empty when benchmark availability is low.
        m51 = inputs.get("motor_051", {}) if isinstance(inputs.get("motor_051", {}), dict) else {}
        archetypal_peer_admissibility_register = list(
            m51.get("archetypal_peer_admissibility_register", []) or []
        )
        enriched_register: list[dict[str, Any]] = []
        for row in register:
            if not isinstance(row, dict):
                enriched_register.append(row)
                continue
            evidence_state = str(row.get("evidence_state", "")).strip()
            allowed_verbs = _allowed_verbs_for_state(evidence_state)
            enriched_register.append({
                **row,
                "allowed_verbs": allowed_verbs,
            })
        return {
            "competitive_comparison_register": enriched_register,
            "competitive_comparison_count": len(enriched_register),
            "archetypal_peer_fallback_register": archetypal_peer_admissibility_register,
            "archetypal_peer_fallback_available": bool(archetypal_peer_admissibility_register),
        }
