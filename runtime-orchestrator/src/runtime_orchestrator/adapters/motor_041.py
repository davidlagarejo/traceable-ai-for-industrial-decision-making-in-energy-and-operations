from __future__ import annotations

from typing import Any

from ..asset_contracts import derive_target_definition
from ..structural_intelligence import build_problem_framing_register
from .base import BaseMotorAdapter


def _format_problem_label(value: Any) -> str:
    text = str(value or "").strip().replace("_", " ")
    return " ".join(text.split())


def _translated_problem_framing(
    invalid_problem_frame_register: list[dict[str, Any]],
    cross_layer_congruence_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    primary_invalid = dict(invalid_problem_frame_register[0] if invalid_problem_frame_register else {})
    if not primary_invalid:
        return []
    linked_layers = list((cross_layer_congruence_register[0] if cross_layer_congruence_register else {}).get("layers", []) or [])
    return [
        {
            "stated_problem": _format_problem_label(primary_invalid.get("apparent_problem")) or "asset_screening",
            "reframed_problem": str(primary_invalid.get("what_problem_should_be_tested_instead", "")).strip(),
            "why_original_framing_may_be_wrong": str(primary_invalid.get("why_invalid_or_premature", "")).strip(),
            "evidence_needed": list(primary_invalid.get("evidence_needed", []) or []),
            "strategic_risk": str(primary_invalid.get("why_invalid_or_premature", "")).strip(),
            "evidence_state": str(primary_invalid.get("evidence_state", "")).strip() or "CONDITIONAL_HYPOTHESIS",
            "linked_layers": linked_layers,
        }
    ]


class Motor041Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_041"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_037", "motor_038", "motor_040", "motor_051", "motor_060"]

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
        register = build_problem_framing_register(
            target_definition=target_definition,
            system_abstraction=dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {}),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
        )
        translated = _translated_problem_framing(
            list(inputs.get("motor_051", {}).get("invalid_problem_frame_register", []) or []),
            list(inputs.get("motor_051", {}).get("cross_layer_congruence_register", []) or []),
        )
        if translated and (
            not register
            or str(register[0].get("evidence_state", "")).strip() == "INADMISSIBLE_CLAIM"
            or str(register[0].get("stated_problem", "")).strip() == "asset_screening"
        ):
            register = translated
        # R-55: surface the diversity_axis_plan from motor_060 alongside the
        # problem framing register so downstream consumers (composer, validators)
        # can use it to enforce per-asset thematic diversity. We attach it as
        # metadata only; we do not re-rank or filter the existing register here.
        diversity_axis_plan = dict(
            inputs.get("motor_060", {}).get("diversity_axis_plan", {}) or {}
        ) if isinstance(inputs.get("motor_060", {}), dict) else {}
        return {
            "problem_framing_register": register,
            "problem_framing_count": len(register),
            "diversity_axis_plan": diversity_axis_plan,
            "diversity_required_themes": list(diversity_axis_plan.get("required_themes", []) or []),
        }
