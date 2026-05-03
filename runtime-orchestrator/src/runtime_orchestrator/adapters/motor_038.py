from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_dominant_variable_register
from .base import BaseMotorAdapter


class Motor038Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_038"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_012", "motor_037", "motor_039"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        m12 = inputs.get("motor_012", {})
        m37 = inputs.get("motor_037", {})
        m39 = inputs.get("motor_039", {})

        facility_prior = dict(m12.get("facility_prior", {}) or {})
        target_definition = (
            facility_prior.get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )

        register = build_dominant_variable_register(
            target_definition=target_definition,
            system_abstraction=dict(m37.get("system_abstraction", {}) or {}),
            dominant_variable_hypotheses=list(m39.get("dominant_variable_hypotheses", []) or []),
            asset_field_register=list(m12.get("asset_field_register", []) or facility_prior.get("asset_field_register", []) or []),
            dataset_coverage_register=list(m12.get("dataset_coverage_register", []) or facility_prior.get("dataset_coverage_register", []) or []),
        )

        return {
            "dominant_variable_register": register,
            "dominant_variable_count": len(register),
            "observed_or_conditional_variable_count": len(
                [
                    row
                    for row in register
                    if row.get("evidence_state") in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS"}
                ]
            ),
        }

