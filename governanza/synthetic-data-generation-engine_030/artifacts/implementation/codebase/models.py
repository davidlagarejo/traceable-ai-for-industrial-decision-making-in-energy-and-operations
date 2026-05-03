"""Data models for motor_030 synthetic data generation outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


MOTOR_ID = "motor_030"
INTENDED_USE = "exploration"
SYNTHETIC_DATA_FLAG = True
NON_EVIDENTIARY_FLAG = True

FORBIDDEN_USES = [
    "field_evidence",
    "validation_data_bridge",
    "verification_bridge",
    "decision_closure",
]


@dataclass(frozen=True)
class SyntheticGenerationRun:
    run_id: str
    record_id: str
    expert_spec_ref: str
    source_problem_ref: str
    generator_version: str | None
    version_record_refs: list[str]
    parameter_set: dict[str, Any]
    generation_seed: int | None
    scenario_refs: list[str]
    status: str
    rejection_code: str | None
    constraint_summary: dict[str, Any]
    synthetic_data_flag: bool
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


@dataclass(frozen=True)
class SyntheticDataset:
    dataset_id: str
    record_id: str
    run_id: str
    manifest_id: str
    expert_spec_ref: str
    source_problem_ref: str
    generator_version: str
    version_record_refs: list[str]
    parameter_set: dict[str, Any]
    schema: dict[str, Any]
    records: list[dict[str, Any]]
    record_count: int
    partition_refs: list[str]
    scenario_column: str | None
    dataset_hash: str
    quality_checks: dict[str, Any]
    synthetic_data_flag: bool
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


@dataclass(frozen=True)
class GenerationManifest:
    manifest_id: str
    record_id: str
    run_id: str
    dataset_refs: list[str]
    expert_spec_ref: str
    source_problem_ref: str
    generator_version: str
    version_record_refs: list[str]
    parameter_set: dict[str, Any]
    constraints_applied: list[dict[str, Any]]
    scenario_summary: dict[str, Any]
    quality_checks: dict[str, Any]
    reproducibility_fingerprint: str
    forbidden_uses: list[str]
    synthetic_data_flag: bool
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


@dataclass(frozen=True)
class GenerationResult:
    synthetic_generation_run: SyntheticGenerationRun
    synthetic_dataset: SyntheticDataset | None
    generation_manifest: GenerationManifest | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "synthetic_generation_run": self.synthetic_generation_run.to_dict(),
            "synthetic_dataset": (
                self.synthetic_dataset.to_dict()
                if self.synthetic_dataset is not None
                else None
            ),
            "generation_manifest": (
                self.generation_manifest.to_dict()
                if self.generation_manifest is not None
                else None
            ),
        }
