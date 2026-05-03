"""Data models for motor_031 ML experiment outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


MOTOR_ID = "motor_031"
SYNTHETIC_DATA_FLAG = True
SYNTHETIC_SUPPORT_FLAG = True
NON_EVIDENTIARY_FLAG = True
DEFAULT_INTENDED_USE = "capability_demo"

CAPABILITY_LIMITATIONS_NOTE = (
    "Motor_031 output is synthetic, non-evidentiary capability support only; "
    "it is not field validation evidence, verification evidence, causal proof, "
    "decision-grade support, or production readiness."
)

CANNOT_SUBSTITUTE = [
    "field_evidence",
    "Validation Data Bridge",
    "Verification Bridge",
    "production deployment review",
]


@dataclass(frozen=True)
class TrainingRunRecord:
    run_id: str
    source_problem_ref: str
    source_ref: str
    expert_spec_ref: str
    training_data_ref: str
    synthetic_dataset_ref: str
    version_refs: dict[str, str]
    experiment_config: dict[str, Any]
    problem_class: str
    primary_metric: str
    primary_metric_threshold: float
    candidate_models: list[dict[str, Any]]
    baseline_model: str
    baseline_evaluated_first: bool
    deterministic_or_statistical_path: bool
    random_seed: int
    split_strategy: dict[str, Any]
    scenario_bundle_refs: list[str]
    model_parameters: dict[str, dict[str, Any]]
    training_result_refs: list[str]
    generator_version: str
    parameter_set: dict[str, Any]
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    synthetic_data_flag: bool
    synthetic_support_flag: bool
    non_evidentiary_flag: bool
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModelEvalSummary:
    eval_id: str
    source_problem_ref: str
    source_ref: str
    expert_spec_ref: str
    training_run_refs: list[str]
    training_data_ref: str
    version_refs: dict[str, str]
    primary_metric: str
    primary_metric_threshold: float
    metric_results: dict[str, dict[str, Any]]
    baseline_comparison: dict[str, Any]
    scenario_stability: dict[str, Any]
    generator_sensitivity_test: dict[str, Any]
    selection_criteria_results: dict[str, Any]
    selected_model: str | None
    selection_rationale: str
    known_metric_limits: list[str]
    generator_version: str
    parameter_set: dict[str, Any]
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    synthetic_data_flag: bool
    synthetic_support_flag: bool
    non_evidentiary_flag: bool
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityDemonstrationReport:
    report_id: str
    source_problem_ref: str
    source_ref: str
    expert_spec_ref: str
    model_eval_summary_ref: str
    training_run_refs: list[str]
    training_data_ref: str
    version_refs: dict[str, str]
    capability_statement: str
    demonstration_status: str
    selected_model: str | None
    primary_metric: str
    primary_metric_value: float | None
    summary_metric_results: dict[str, Any]
    generator_sensitivity_test: dict[str, Any]
    gap_to_real_validation: str
    gap_to_deployment: str
    known_failure_modes: list[str]
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    cannot_substitute: list[str]
    generator_version: str
    parameter_set: dict[str, Any]
    synthetic_data_flag: bool
    synthetic_support_flag: bool
    non_evidentiary_flag: bool
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentResult:
    training_run_record: TrainingRunRecord
    model_eval_summary: ModelEvalSummary
    capability_demonstration_report: CapabilityDemonstrationReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "accepted",
            "training_run_record": self.training_run_record.to_dict(),
            "model_eval_summary": self.model_eval_summary.to_dict(),
            "capability_demonstration_report": (
                self.capability_demonstration_report.to_dict()
            ),
        }
