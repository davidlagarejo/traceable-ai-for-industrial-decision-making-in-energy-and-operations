from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_competitive_comparison_register
from .base import BaseMotorAdapter


class Motor043Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_043"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_039", "motor_042"]

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
        return {
            "competitive_comparison_register": register,
            "competitive_comparison_count": len(register),
        }

