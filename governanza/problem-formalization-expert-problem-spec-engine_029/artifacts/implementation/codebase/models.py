"""Data models for motor_029 outputs.

The models are intentionally plain dataclasses so the core motor can run
without framework, database, network, or AI dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MOTOR_ID = "motor_029"
INTENDED_USE = "exploration"
NON_EVIDENTIARY_FLAG = True

ALLOWED_PROBLEM_CLASSES = {
    "classification_binary",
    "classification_multiclass",
    "regression_continuous",
    "regression_interval",
    "ranking",
    "clustering_exploratory",
    "anomaly_detection",
    "survival_hazard",
    "sensitivity_analysis",
}

TARGETLESS_PROBLEM_CLASSES = {
    "clustering_exploratory",
    "sensitivity_analysis",
}

ACTIVE_STATUSES = {
    "activated",
    "active",
    "ready_for_formalization",
    "synthetic_formalization_allowed",
}

IMPACT_ORDER = {
    "none": 0,
    "minor": 1,
    "material": 2,
    "critical": 3,
}

FORBIDDEN_OUTPUT_FIELDS = {
    "synthetic_dataset",
    "generation_manifest",
    "training_run_record",
    "selected_model",
    "metric_auc",
    "ranking_basis",
    "field_validation_result",
    "synthetic_rows",
    "model_metrics",
    "trained_model_ref",
}


@dataclass(frozen=True)
class CanonicalTerm:
    canonical_term_ref: str
    name: str
    aliases: tuple[str, ...] = ()
    value_type: str | None = None
    allowed_domain: dict[str, Any] | None = None
    unit: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AmbiguityItem:
    ambiguity_id: str
    register_id: str
    spec_id: str
    source_problem_ref: str
    field_ref: str
    source_input_ref: str
    description: str
    severity: str
    resolution_status: str
    impact_if_unresolved: str
    resolution_note: str | None
    owner_ref: str | None
    blocks_handoff: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AmbiguityRegister:
    register_id: str
    record_id: str
    spec_id: str
    source_problem_ref: str
    items: list[AmbiguityItem]
    has_unresolved_critical: bool
    highest_unresolved_impact: str
    handoff_allowed: bool
    blocking_item_refs: list[str]
    non_evidentiary_flag: bool
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["items"] = [item.to_dict() for item in self.items]
        return payload


@dataclass
class ParameterConstraint:
    constraint_id: str
    record_id: str
    spec_id: str
    source_problem_ref: str
    parameter_name: str
    canonical_term_ref: str
    value_type: str
    allowed_domain: dict[str, Any]
    unit: str | None
    constraint_kind: str
    required: bool
    compatibility_refs: list[str]
    constraint_rationale: str
    uncertainty_treatment: str
    ambiguity_item_refs: list[str]
    non_evidentiary_flag: bool
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExpertProblemSpec:
    spec_id: str
    record_id: str
    source_problem_ref: str
    phase_contract_ref: str
    taxonomy_snapshot_ref: str
    version_record_refs: list[str]
    spec_version: str
    problem_statement: str
    problem_class: str
    target_variable_ref: str | None
    expert_assumptions: list[str]
    domain_constraints_ref: list[str]
    parameter_constraints_ref: list[str]
    ambiguity_register_ref: str
    handoff_allowed: bool
    handoff_block_reason: str | None
    lineage_refs: list[str]
    provenance_refs: list[str]
    non_evidentiary_flag: bool
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FormalizationResult:
    expert_problem_spec: ExpertProblemSpec
    ambiguity_register: AmbiguityRegister
    parameter_constraints: list[ParameterConstraint]

    def to_dict(self) -> dict[str, Any]:
        return {
            "expert_problem_spec": self.expert_problem_spec.to_dict(),
            "ambiguity_register": self.ambiguity_register.to_dict(),
            "parameter_constraints": [
                constraint.to_dict() for constraint in self.parameter_constraints
            ],
        }
