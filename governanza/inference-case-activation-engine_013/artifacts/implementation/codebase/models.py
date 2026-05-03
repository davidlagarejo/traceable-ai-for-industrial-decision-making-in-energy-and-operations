"""Output models for the Inference Case Activation Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TriggerCondition:
    trigger_condition_id: str
    record_id: str
    library_object_ref: str
    library_object_version: str
    condition_type: str
    scope: str
    required_fields: list[str]
    activation_case_type: str
    condition_expression_ref: str
    allowed_result_values: list[str]
    trigger_priority: int
    version: str
    provenance_refs: list[str]
    lineage_refs: list[str]
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
class InferenceCase:
    case_id: str
    record_id: str
    facility_id: str
    source_prior_ref: str
    source_prior_version: str
    contextual_bundle_refs: list[str]
    library_object_refs: list[str]
    trigger_condition_ref: str
    supporting_trigger_refs: list[str]
    activation_record_ref: str
    activation_case_type: str
    case_status: str
    activation_rule_version: str
    quality_record_refs: list[str]
    conditional_quality_notes: list[str]
    activation_rationale_code: str
    provenance_refs: list[str]
    lineage_id: str
    lineage_refs: list[str]
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
class ActivationRecord:
    activation_id: str
    record_id: str
    case_id: str | None
    facility_id: str
    source_prior_ref: str
    evaluated_input_refs: list[str]
    trigger_condition_ref: str
    trigger_version: str
    activation_case_type: str
    result: str
    reason_code: str
    decision_detail_refs: list[str]
    activation_rule_version: str
    provenance_refs: list[str]
    lineage_id: str
    lineage_refs: list[str]
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
class TriggerLogEntry:
    trigger_log_id: str
    record_id: str
    trigger_condition_ref: str
    facility_prior_ref: str
    facility_id: str
    library_object_ref: str
    evaluated_field_refs: list[str]
    evaluation_result: str
    reason_code: str
    activation_record_ref: str
    case_ref: str | None
    evaluated_at: str
    activation_rule_version: str
    provenance_refs: list[str]
    lineage_id: str
    lineage_refs: list[str]
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
class ActivationResult:
    inference_case: list[InferenceCase]
    activation_record: list[ActivationRecord]
    trigger_log: list[TriggerLogEntry]

    @property
    def status(self) -> str:
        if self.inference_case:
            return "activated"
        if any(record.result == "rejected" for record in self.activation_record):
            return "rejected"
        return "not_activated"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "inference_case": [item.to_dict() for item in self.inference_case],
            "activation_record": [
                item.to_dict() for item in self.activation_record
            ],
            "trigger_log": [item.to_dict() for item in self.trigger_log],
        }
