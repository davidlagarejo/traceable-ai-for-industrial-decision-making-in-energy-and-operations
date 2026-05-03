"""Output models for Propagation / Re-evaluation Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ReEvaluationJob:
    job_id: str
    target_object_ref: str
    target_version_ref: str | None
    trigger_ref: str
    trigger_type: str
    reason_code: str
    priority: str
    dependency_path: list[str]
    input_refs: list[str]
    evidence_refs: list[str]
    propagation_record_id: str
    stale_object_id: str | None
    status: str
    blocking_reason: str | None
    propagation_rule_version: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class StaleObject:
    stale_object_id: str
    object_ref: str
    version_ref: str | None
    stale_reason: str
    trigger_ref: str
    trigger_type: str
    lineage_refs: list[str]
    dependency_path: list[str]
    severity: str
    detected_at: str
    propagation_record_id: str
    job_id: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PropagationRecord:
    propagation_record_id: str
    input_refs: list[str]
    trigger_ref: str
    trigger_type: str
    affected_object_refs: list[str]
    emitted_job_ids: list[str]
    stale_object_ids: list[str]
    stale_set_ref: str | None
    rejected_input_refs: list[str]
    dependency_paths: list[list[str]]
    decision: str
    secondary_decisions: list[str]
    error_code: str | None
    rule_version: str
    evaluated_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
