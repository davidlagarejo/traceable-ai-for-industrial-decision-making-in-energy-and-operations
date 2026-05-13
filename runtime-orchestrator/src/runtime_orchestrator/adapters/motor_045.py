from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..phase_units import to_financial_exposure_case_register
from ..structural_intelligence import (
    build_evidence_state_by_layer_register,
    build_structural_financial_exposure_register,
)
from .base import BaseMotorAdapter


class Motor045Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_045"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_037", "motor_038", "motor_040", "motor_041", "motor_043", "motor_044"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        target_definition = (
            inputs.get("motor_012", {}).get("facility_prior", {}).get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )
        register = build_structural_financial_exposure_register(
            target_definition=target_definition,
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
        )
        evidence_by_layer = build_evidence_state_by_layer_register(
            target_definition=target_definition,
            system_abstraction=dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {}),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
            competitive_comparison_register=list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or []),
            structural_financial_exposure_register=register,
        )
        # V5 P2 + V5 P13: canonical Phase 5 unit (Master Doc §4 + §7).
        # V5 P13 enriches by passing target_asset_family and by structurally
        # computing baseline_dependency_state, tariff_basis_state,
        # cost_basis_state, benefit_driver_family, regulatory_dependency_state,
        # and publication_ceiling from the row's own evidence_state +
        # evidence_needed + allowed_financial_output (instead of empty
        # placeholders).
        financial_exposure_case_register = to_financial_exposure_case_register(
            register,
            target_asset_family=str(target_definition.get("target_type", "")),
        )
        return {
            "structural_financial_exposure_register": register,
            "structural_financial_exposure_count": len(register),
            "evidence_state_by_layer_register": evidence_by_layer,
            "evidence_state_by_layer_count": len(evidence_by_layer),
            "financial_exposure_case_register": financial_exposure_case_register,
        }
