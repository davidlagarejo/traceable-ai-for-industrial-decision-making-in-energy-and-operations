from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_cross_layer_conflict_register
from .base import BaseMotorAdapter


def _translated_congruence_conflicts(cross_layer_congruence_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in cross_layer_congruence_register:
        conflict = str(row.get("contradiction", "")).strip()
        if not conflict:
            continue
        rows.append(
            {
                "conflict": conflict,
                "layers_involved": list(row.get("layers", []) or []),
                "why_it_matters": str(row.get("strategic_risk", "")).strip(),
                "evidence_state": str(row.get("evidence_state", "")).strip() or "CONDITIONAL_HYPOTHESIS",
                "potential_redesign_direction": str(row.get("possible_redesign", "")).strip(),
            }
        )
    return rows


class Motor040Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_040"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_037", "motor_038", "motor_051"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        m12 = inputs.get("motor_012", {})
        facility_prior = dict(m12.get("facility_prior", {}) or {})
        target_definition = (
            facility_prior.get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )

        register = build_cross_layer_conflict_register(
            target_definition=target_definition,
            system_abstraction=dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {}),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            financial_exposure_register=list(inputs.get("motor_014", {}).get("financial_exposure_register", []) or []),
            claim_permission_register=list(inputs.get("motor_034", {}).get("claim_permission_register", []) or []),
            decision_front_actions=list(inputs.get("motor_033", {}).get("decision_front_actions", []) or []),
        )
        if not register:
            register = _translated_congruence_conflicts(
                list(inputs.get("motor_051", {}).get("cross_layer_congruence_register", []) or [])
            )
        return {
            "cross_layer_conflict_register": register,
            "cross_layer_conflict_count": len(register),
        }
