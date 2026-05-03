from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_system_abstraction
from .base import BaseMotorAdapter


class Motor037Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_037"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_012", "motor_039"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        m12 = inputs.get("motor_012", {})
        m28 = inputs.get("motor_028", {})
        m39 = inputs.get("motor_039", {})

        facility_prior = dict(m12.get("facility_prior", {}) or {})
        target_definition = (
            facility_prior.get("target_definition")
            or inputs.get("motor_007", {}).get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )

        system_abstraction = build_system_abstraction(
            target_definition=target_definition,
            canonical_asset_context_summary=dict(m12.get("canonical_asset_context_summary", {}) or {}),
            archetype_resolution=dict(m39.get("archetype_resolution", {}) or {}),
            archetype_library_register=list(m39.get("archetype_library_register", []) or []),
            asset_field_register=list(m12.get("asset_field_register", []) or facility_prior.get("asset_field_register", []) or []),
            dataset_coverage_register=list(m12.get("dataset_coverage_register", []) or facility_prior.get("dataset_coverage_register", []) or []),
            source_register=list(m28.get("source_register", []) or []),
        )

        return {
            "system_abstraction": system_abstraction,
            "system_abstraction_fields": list(system_abstraction.keys()),
            "system_abstraction_evidence_states": {
                key: value.get("evidence_state", "NOT_OBSERVED")
                for key, value in system_abstraction.items()
                if isinstance(value, dict)
            },
        }

