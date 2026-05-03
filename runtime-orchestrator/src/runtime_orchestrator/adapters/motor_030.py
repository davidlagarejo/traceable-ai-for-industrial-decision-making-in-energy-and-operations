"""Adapter for motor_030 — Synthetic Data Generation Engine."""
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter

_GENERATOR_VERSION = "0.1.0"


def _stable_id(prefix: str, raw: str) -> str:
    return f"{prefix}:" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _dataset_rows(spec_id: str, scenario_count: int) -> list[dict[str, Any]]:
    rng = random.Random(int(hashlib.sha256(spec_id.encode()).hexdigest()[:8], 16))
    rows: list[dict[str, Any]] = []
    for idx in range(scenario_count):
        observability_gap = round(0.2 + rng.random() * 0.75, 3)
        decision_sensitivity = round(0.3 + rng.random() * 0.7, 3)
        validation_effort = round(0.2 + rng.random() * 0.6, 3)
        priority_proxy = round((decision_sensitivity * (1 - observability_gap)) + (0.4 * (1 - validation_effort)), 3)
        rows.append(
            {
                "scenario_id": f"scn-{idx + 1:02d}",
                "observability_gap_ratio": observability_gap,
                "decision_sensitivity_weight": decision_sensitivity,
                "validation_effort_proxy": validation_effort,
                "priority_proxy": priority_proxy,
                "priority_band": (
                    "high" if priority_proxy >= 0.7 else "medium" if priority_proxy >= 0.45 else "low"
                ),
            }
        )
    return rows


class Motor030Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_030"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_029", "motor_002"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        specs = inputs.get("motor_029", {}).get("expert_problem_specs", [])

        synthetic_generation_runs: list[dict[str, Any]] = []
        synthetic_datasets: list[dict[str, Any]] = []
        skipped_specs: list[dict[str, Any]] = []

        for spec in specs:
            if spec.get("spec_status") == "draft" or spec.get("critical_ambiguity_count", 0) > 0:
                skipped_specs.append(
                    {
                        "spec_id": spec.get("spec_id", ""),
                        "source_problem_ref": spec.get("source_problem_ref", ""),
                        "reason": "spec_not_eligible_for_generation",
                    }
                )
                continue

            spec_id = str(spec.get("spec_id", "")).strip()
            source_problem_ref = str(spec.get("source_problem_ref", "")).strip()
            parameter_set = spec.get("parameter_set", {}) if isinstance(spec.get("parameter_set", {}), dict) else {}
            scenario_count = int(parameter_set.get("scenario_count", 24) or 24)
            run_id = _stable_id("synrun", spec_id)
            rows = _dataset_rows(spec_id, scenario_count)
            avg_priority = round(sum(row["priority_proxy"] for row in rows) / max(len(rows), 1), 3)

            generation_run = {
                "run_id": run_id,
                "source_problem_ref": source_problem_ref,
                "expert_spec_ref": spec_id,
                "synthetic_data_flag": True,
                "non_evidentiary_flag": True,
                "generator_version": _GENERATOR_VERSION,
                "parameter_set": parameter_set,
                "intended_use": "exploration",
                "domain_validity_limits": spec.get("domain_validity_limits", ""),
                "limitations_note": spec.get("limitations_note", ""),
                "row_count": len(rows),
                "produced_at": produced_at,
            }
            dataset = {
                "dataset_id": _stable_id("synds", spec_id),
                "training_data_ref": run_id,
                "source_problem_ref": source_problem_ref,
                "expert_spec_ref": spec_id,
                "synthetic_data_flag": True,
                "non_evidentiary_flag": True,
                "generator_version": _GENERATOR_VERSION,
                "parameter_set": parameter_set,
                "intended_use": "exploration",
                "domain_validity_limits": spec.get("domain_validity_limits", ""),
                "limitations_note": spec.get("limitations_note", ""),
                "problem_class": spec.get("problem_class", ""),
                "schema": [
                    "observability_gap_ratio",
                    "decision_sensitivity_weight",
                    "validation_effort_proxy",
                    "priority_proxy",
                    "priority_band",
                ],
                "rows": rows,
                "dataset_characteristics": {
                    "sample_count": len(rows),
                    "feature_count": 4,
                    "signal_assumption_strength": avg_priority,
                },
            }
            synthetic_generation_runs.append(generation_run)
            synthetic_datasets.append(dataset)

        generation_manifest = {
            "generated_dataset_count": len(synthetic_datasets),
            "skipped_spec_count": len(skipped_specs),
            "eligible_spec_count": len(synthetic_generation_runs),
            "total_specs_received": len(specs),
            "skipped_specs": skipped_specs,
            "generator_version": _GENERATOR_VERSION,
            "synthetic_data_flag": True,
            "non_evidentiary_flag": True,
            "intended_use": "exploration",
            "limitations_note": "Synthetic datasets remain exploratory and cannot be cited as field evidence.",
        }

        return {
            "produced_at": produced_at,
            "synthetic_generation_run": synthetic_generation_runs[0] if synthetic_generation_runs else {},
            "synthetic_generation_runs": synthetic_generation_runs,
            "synthetic_dataset": synthetic_datasets[0] if synthetic_datasets else {},
            "synthetic_datasets": synthetic_datasets,
            "generation_manifest": generation_manifest,
        }
