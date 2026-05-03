from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_structural_benchmark_register
from .base import BaseMotorAdapter


class Motor042Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_042"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_037", "motor_038", "motor_039", "motor_012"]

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
        register = build_structural_benchmark_register(
            target_definition=target_definition,
            archetype_resolution=dict(inputs.get("motor_039", {}).get("archetype_resolution", {}) or {}),
            system_abstraction=dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {}),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            dataset_coverage_register=list(m12.get("dataset_coverage_register", []) or facility_prior.get("dataset_coverage_register", []) or []),
        )
        return {
            "structural_benchmark_register": register,
            "structural_benchmark_count": len(register),
        }

