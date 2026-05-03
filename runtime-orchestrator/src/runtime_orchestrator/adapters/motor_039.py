from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import resolve_archetype
from .base import BaseMotorAdapter


class Motor039Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_039"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_007", "motor_012", "motor_028"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        m07 = inputs.get("motor_007", {})
        m12 = inputs.get("motor_012", {})
        m28 = inputs.get("motor_028", {})

        facility_prior = dict(m12.get("facility_prior", {}) or {})
        target_definition = (
            facility_prior.get("target_definition")
            or m07.get("target_definition_contract")
            or derive_target_definition(pipeline)
            or {}
        )
        target_classification_object = dict(m07.get("target_classification_object", {}) or {})
        asset_field_register = list(m12.get("asset_field_register", []) or facility_prior.get("asset_field_register", []) or [])
        dataset_coverage_register = list(m12.get("dataset_coverage_register", []) or facility_prior.get("dataset_coverage_register", []) or [])
        source_register = list(m28.get("source_register", []) or [])

        resolved = resolve_archetype(
            target_definition=target_definition,
            target_classification_object=target_classification_object,
            facility_prior=facility_prior,
            asset_field_register=asset_field_register,
            dataset_coverage_register=dataset_coverage_register,
            source_register=source_register,
        )

        resolution = dict(resolved.get("archetype_resolution", {}) or {})
        return {
            **resolved,
            "selected_archetype_id": resolution.get("selected_archetype_id", ""),
            "selected_archetype_label": resolution.get("label", ""),
            "match_confidence": resolution.get("match_confidence", "low"),
            "resolver_state": resolution.get("resolver_state", "unresolved"),
            "dominant_variable_count": len(resolved.get("dominant_variable_hypotheses", []) or []),
        }

