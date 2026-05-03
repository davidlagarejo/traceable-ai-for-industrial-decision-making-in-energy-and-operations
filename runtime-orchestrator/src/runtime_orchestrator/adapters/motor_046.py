from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_minimum_evidence_for_discrimination_register
from .base import BaseMotorAdapter


class Motor046Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_046"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_038", "motor_040", "motor_041", "motor_044"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        target_definition = (
            inputs.get("motor_012", {}).get("facility_prior", {}).get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )
        register = build_minimum_evidence_for_discrimination_register(
            target_definition=target_definition,
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
        )
        return {
            "minimum_evidence_for_discrimination_register": register,
            "minimum_evidence_for_discrimination_count": len(register),
        }

