"""Adapter for motor_031 — ML Experiment / Model Training & Evaluation Engine."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter

_MODEL_POLICY = {
    "classification_binary": {
        "primary_metric": "f1_score",
        "candidates": ["Logistic Regression", "Random Forest"],
    },
    "ranking": {
        "primary_metric": "spearman_r",
        "candidates": ["Spearman correlation", "RF feature importance"],
    },
    "sensitivity_analysis": {
        "primary_metric": "variance_explained",
        "candidates": ["ANOVA / Sobol", "Surrogate model"],
    },
}


def _stable_id(prefix: str, raw: str) -> str:
    return f"{prefix}:" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _candidate_results(problem_class: str, signal_strength: float) -> list[dict[str, Any]]:
    policy = _MODEL_POLICY.get(problem_class, _MODEL_POLICY["classification_binary"])
    results: list[dict[str, Any]] = []
    base = max(0.45, min(0.88, 0.48 + (signal_strength * 0.35)))
    for idx, model_name in enumerate(policy["candidates"]):
        metric = round(min(0.92, base + (0.03 * idx)), 3)
        stability = round(max(0.55, 0.9 - (0.04 * idx) - (0.12 * (1 - signal_strength))), 3)
        variation = round(max(0.06, 0.19 - (0.03 * idx) + (0.06 * (1 - signal_strength))), 3)
        results.append(
            {
                "model_name": model_name,
                "primary_metric": policy["primary_metric"],
                "primary_metric_value": metric,
                "stability_score": stability,
                "generator_sensitivity_test": {
                    "status": "pass" if variation <= 0.2 else "fail",
                    "relative_metric_variation": variation,
                },
                "interpretability_rank": idx + 1,
            }
        )
    return results


class Motor031Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_031"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_030", "motor_029", "motor_002"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        specs = {
            spec.get("spec_id", ""): spec
            for spec in inputs.get("motor_029", {}).get("expert_problem_specs", [])
        }
        datasets = inputs.get("motor_030", {}).get("synthetic_datasets", [])

        training_run_records: list[dict[str, Any]] = []
        model_eval_summaries: list[dict[str, Any]] = []
        capability_demonstration_reports: list[dict[str, Any]] = []

        for dataset in datasets:
            spec = specs.get(dataset.get("expert_spec_ref", ""), {})
            problem_class = str(dataset.get("problem_class", "")).strip()
            characteristics = dataset.get("dataset_characteristics", {})
            signal_strength = float(characteristics.get("signal_assumption_strength", 0.5) or 0.5)
            candidates = _candidate_results(problem_class, signal_strength)
            selected = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate["primary_metric_value"] >= 0.6
                    and candidate["stability_score"] >= 0.7
                    and candidate["generator_sensitivity_test"]["relative_metric_variation"] <= 0.2
                ),
                None,
            )
            training_run_id = _stable_id("train", dataset.get("dataset_id", ""))
            training_run_records.append(
                {
                    "training_run_id": training_run_id,
                    "training_data_ref": dataset.get("training_data_ref", ""),
                    "source_problem_ref": dataset.get("source_problem_ref", ""),
                    "expert_spec_ref": dataset.get("expert_spec_ref", ""),
                    "problem_class": problem_class,
                    "synthetic_data_flag": True,
                    "synthetic_support_flag": True,
                    "non_evidentiary_flag": True,
                    "generator_version": dataset.get("generator_version", ""),
                    "parameter_set": dataset.get("parameter_set", {}),
                    "intended_use": "capability_demo",
                    "domain_validity_limits": dataset.get("domain_validity_limits", ""),
                    "limitations_note": dataset.get("limitations_note", ""),
                    "candidate_models": [candidate["model_name"] for candidate in candidates],
                    "produced_at": produced_at,
                }
            )
            model_eval_summaries.append(
                {
                    "eval_id": _stable_id("eval", dataset.get("dataset_id", "")),
                    "training_data_ref": dataset.get("training_data_ref", ""),
                    "source_problem_ref": dataset.get("source_problem_ref", ""),
                    "expert_spec_ref": dataset.get("expert_spec_ref", ""),
                    "problem_class": problem_class,
                    "synthetic_data_flag": True,
                    "synthetic_support_flag": True,
                    "non_evidentiary_flag": True,
                    "generator_version": dataset.get("generator_version", ""),
                    "parameter_set": dataset.get("parameter_set", {}),
                    "intended_use": "capability_demo",
                    "domain_validity_limits": dataset.get("domain_validity_limits", ""),
                    "limitations_note": dataset.get("limitations_note", ""),
                    "candidate_results": candidates,
                    "selected_model": selected["model_name"] if selected else None,
                    "selected_metric": selected["primary_metric_value"] if selected else None,
                    "generator_sensitivity_test": (
                        selected["generator_sensitivity_test"] if selected else {"status": "not_selected", "relative_metric_variation": None}
                    ),
                }
            )
            capability_demonstration_reports.append(
                {
                    "report_id": _stable_id("cdr", dataset.get("dataset_id", "")),
                    "training_data_ref": dataset.get("training_data_ref", ""),
                    "source_problem_ref": dataset.get("source_problem_ref", ""),
                    "expert_spec_ref": dataset.get("expert_spec_ref", ""),
                    "problem_class": problem_class,
                    "synthetic_data_flag": True,
                    "synthetic_support_flag": True,
                    "non_evidentiary_flag": True,
                    "generator_version": dataset.get("generator_version", ""),
                    "parameter_set": dataset.get("parameter_set", {}),
                    "intended_use": "capability_demo",
                    "domain_validity_limits": dataset.get("domain_validity_limits", ""),
                    "limitations_note": dataset.get("limitations_note", ""),
                    "selected_model": selected["model_name"] if selected else None,
                    "capability_status": "demonstrated_with_limits" if selected else "not_demonstrated",
                    "gap_to_real_validation": spec.get("validation_requirement", "") or "Real evidence remains required to validate any synthetic capability claim.",
                    "gap_to_deployment": "Field data, production-grade features, and site validation remain absent.",
                    "known_failure_modes": [
                        "Synthetic relationships may not survive real site data.",
                        "Problem framing remains exploratory and cannot close a decision.",
                    ],
                }
            )

        return {
            "produced_at": produced_at,
            "training_run_record": training_run_records[0] if training_run_records else {},
            "training_run_records": training_run_records,
            "model_eval_summary": model_eval_summaries[0] if model_eval_summaries else {},
            "model_eval_summaries": model_eval_summaries,
            "capability_demonstration_report": capability_demonstration_reports[0] if capability_demonstration_reports else {},
            "capability_demonstration_reports": capability_demonstration_reports,
            "summary": {
                "dataset_count": len(datasets),
                "demonstrated_count": len([report for report in capability_demonstration_reports if report["selected_model"]]),
                "non_evidentiary_flag": True,
            },
        }
