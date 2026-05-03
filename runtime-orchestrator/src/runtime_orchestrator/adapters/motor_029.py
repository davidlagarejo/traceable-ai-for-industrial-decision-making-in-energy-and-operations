"""Adapter for motor_029 — Problem Formalization / Expert Problem Spec Engine."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _stable_id(prefix: str, raw: str) -> str:
    return f"{prefix}:" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _problem_class(case: dict[str, Any]) -> str:
    family = str(case.get("claim_family", "")).strip().lower()
    case_id = str(case.get("case_id", "")).strip().upper()
    if case_id == "LC-ASSET-01":
        return "classification_binary"
    if family == "conflict":
        return "classification_binary"
    if family == "tension":
        return "ranking"
    if family == "opportunity":
        return "sensitivity_analysis"
    return "classification_binary"


def _domain_limits(target_type: str) -> str:
    return (
        f"Valid only as exploratory synthetic support for target_type={target_type or 'unknown'}. "
        "Cannot substitute for field evidence, validation data, or verification outputs."
    )


def _parameter_constraints(case: dict[str, Any], problem_class: str, target_type: str) -> list[dict[str, Any]]:
    constraints = [
        {
            "parameter_name": "observability_gap_ratio",
            "constraint_type": "range",
            "min_value": 0.2,
            "max_value": 0.95,
            "rationale": "Synthetic scenarios should span sparse to moderately informed asset states.",
        },
        {
            "parameter_name": "decision_sensitivity_weight",
            "constraint_type": "range",
            "min_value": 0.3,
            "max_value": 1.0,
            "rationale": "Synthetic support must preserve the decision relevance ordering of the source case.",
        },
        {
            "parameter_name": "problem_class",
            "constraint_type": "enum",
            "allowed_values": [problem_class],
            "rationale": "Model family selection must stay coherent with the formalized problem class.",
        },
    ]
    if target_type:
        constraints.append(
            {
                "parameter_name": "target_type_scope",
                "constraint_type": "enum",
                "allowed_values": [target_type],
                "rationale": "Synthetic support remains bounded to the declared asset family.",
            }
        )
    return constraints


def _ambiguities(case: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    validation_requirement = str(case.get("validation_requirement", "")).strip()
    activation_basis = case.get("activation_basis", [])
    if not validation_requirement:
        items.append(
            {
                "ambiguity_type": "missing_validation_requirement",
                "impact_if_unresolved": "critical",
                "description": "Inference case lacks a validation requirement, so a synthetic spec cannot be safely generated.",
            }
        )
    if not activation_basis:
        items.append(
            {
                "ambiguity_type": "missing_activation_basis",
                "impact_if_unresolved": "high",
                "description": "Inference case activated without explicit trigger trace.",
            }
        )
    if case.get("case_id") == "LC-ASSET-01":
        items.append(
            {
                "ambiguity_type": "asset_context_underpopulation",
                "impact_if_unresolved": "high",
                "description": "The problem is dominated by asset underpopulation, so any synthetic support must remain purely exploratory.",
            }
        )
    elif "cannot be confirmed" in str(case.get("conditional_statement", "")).lower():
        items.append(
            {
                "ambiguity_type": "public_data_insufficiency",
                "impact_if_unresolved": "medium",
                "description": "Public priors are insufficient to close the case without further evidence.",
            }
        )
    return items


class Motor029Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_029"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_002", "motor_003", "motor_013"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        m01 = inputs.get("motor_001", {})
        m02 = inputs.get("motor_002", {})
        m03 = inputs.get("motor_003", {})
        m13 = inputs.get("motor_013", {})

        inference_cases = m13.get("inference_case_register", [])
        target_contract = m01.get("target_definition_contract", {})
        target_type = str(target_contract.get("target_type", "")).strip()
        taxonomy_version = str(m03.get("taxonomy_version", "")).strip()

        expert_problem_specs: list[dict[str, Any]] = []
        ambiguity_register: list[dict[str, Any]] = []
        parameter_constraints: list[dict[str, Any]] = []

        for ordinal, case in enumerate(inference_cases, 1):
            case_id = str(case.get("case_id", "")).strip()
            problem_class = _problem_class(case)
            spec_id = _stable_id("eps", f"{case_id}:{ordinal}:{target_type}")
            case_ambiguities = _ambiguities(case)
            critical_count = sum(1 for item in case_ambiguities if item["impact_if_unresolved"] == "critical")
            spec_status = "draft" if critical_count else ("approved_with_limits" if case_ambiguities else "approved")
            constraints = _parameter_constraints(case, problem_class, target_type)

            spec = {
                "spec_id": spec_id,
                "source_problem_ref": case_id,
                "case_name": case.get("case_name", ""),
                "problem_class": problem_class,
                "spec_status": spec_status,
                "objective_statement": (
                    "Formalize a bounded exploratory problem around the active inference case "
                    f"{case_id} without promoting synthetic artifacts into evidentiary status."
                ),
                "synthetic_data_flag": False,
                "synthetic_support_flag": False,
                "non_evidentiary_flag": True,
                "intended_use": "exploration",
                "domain_validity_limits": _domain_limits(target_type),
                "limitations_note": (
                    "Expert problem specs are contracts for synthetic exploration only. "
                    "They cannot close validation, compliance, or investment decisions."
                ),
                "expert_spec_ref": spec_id,
                "target_type": target_type,
                "target_id": target_contract.get("target_id", ""),
                "taxonomy_version": taxonomy_version,
                "validation_requirement": case.get("validation_requirement", ""),
                "feature_hypotheses": [
                    "observability_gap_ratio",
                    "decision_sensitivity_weight",
                    "validation_effort_proxy",
                ],
                "label_definition": (
                    "Synthetic target labels are exploratory proxies for prioritization and capability demonstration, "
                    "never real-world truth labels."
                ),
                "assumption_register": case.get("dependency_assumptions", []),
                "parameter_set": {
                    "scenario_count": 24,
                    "problem_class": problem_class,
                    "target_type": target_type,
                },
                "generator_policy": {
                    "dataset_size": 24,
                    "allow_probability_claims": False,
                    "requires_real_evidence_for_upgrade": True,
                },
                "critical_ambiguity_count": critical_count,
            }
            expert_problem_specs.append(spec)

            for idx, ambiguity in enumerate(case_ambiguities, 1):
                ambiguity_register.append(
                    {
                        "ambiguity_id": _stable_id("amb", f"{spec_id}:{idx}"),
                        "spec_id": spec_id,
                        "source_problem_ref": case_id,
                        "description": ambiguity["description"],
                        "impact_if_unresolved": ambiguity["impact_if_unresolved"],
                        "ambiguity_type": ambiguity["ambiguity_type"],
                        "non_evidentiary_flag": True,
                    }
                )

            for constraint in constraints:
                parameter_constraints.append(
                    {
                        "spec_id": spec_id,
                        "source_problem_ref": case_id,
                        "non_evidentiary_flag": True,
                        **constraint,
                    }
                )

        approved_specs = [spec for spec in expert_problem_specs if spec["spec_status"] != "draft"]

        return {
            "produced_at": produced_at,
            "expert_problem_spec": expert_problem_specs[0] if expert_problem_specs else {},
            "expert_problem_specs": expert_problem_specs,
            "ambiguity_register": ambiguity_register,
            "parameter_constraints": parameter_constraints,
            "summary": {
                "total_specs": len(expert_problem_specs),
                "approved_specs": len(approved_specs),
                "draft_specs": len(expert_problem_specs) - len(approved_specs),
                "target_type": target_type,
                "taxonomy_version": taxonomy_version,
            },
            "non_evidentiary_flag": True,
            "intended_use": "exploration",
        }
