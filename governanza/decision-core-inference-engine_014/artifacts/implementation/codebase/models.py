"""Serializable output models for the Decision Core / Inference Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    source_class: str
    evidence_level: str
    provenance_ref: str
    lineage_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InferenceRecord:
    inference_id: str
    motor_id: str
    case_id: str
    activation_record_ref: str
    trigger_log_ref: str
    phase_id: str
    phase_contract_ref: str
    contract_version: str
    analysis_question: str
    inference_state: str
    inference_basis: list[str]
    evidence_refs: list[EvidenceRef]
    lineage_refs: list[str]
    rule_version: str
    decision_trace: list[str]
    synthetic_support_present: bool
    created_at: str
    updated_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Tension:
    tension_id: str
    motor_id: str
    inference_id: str
    case_id: str
    phase_contract_ref: str
    contract_version: str
    tension_type: str
    severity: str
    source_refs: list[str]
    description: str
    requires_validation: bool
    related_gap_item_ids: list[str]
    lineage_refs: list[str]
    rule_version: str
    created_at: str
    updated_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GapItem:
    gap_item_id: str
    gap_type: str
    affected_ref: str
    missing_condition: str
    required_downstream_action: str
    priority: str
    source_refs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GapAgenda:
    gap_agenda_id: str
    motor_id: str
    inference_id: str
    case_id: str
    phase_contract_ref: str
    contract_version: str
    gap_items: list[GapItem]
    priority_order: list[str]
    validation_dependency_refs: list[str]
    lineage_refs: list[str]
    rule_version: str
    created_at: str
    updated_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationItem:
    validation_item_id: str
    gap_item_id: str
    required_evidence_level: str
    reason: str
    handoff_target: str
    priority: str
    source_refs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationAgenda:
    validation_agenda_id: str
    motor_id: str
    inference_id: str
    case_id: str
    gap_agenda_id: str
    phase_contract_ref: str
    contract_version: str
    validation_items: list[ValidationItem]
    required_evidence_level: str
    handoff_target: str
    lineage_refs: list[str]
    rule_version: str
    created_at: str
    updated_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionCoreOutput:
    inference_record: InferenceRecord
    tension_record: list[Tension]
    gap_agenda: GapAgenda
    validation_agenda: ValidationAgenda

    def to_dict(self) -> dict[str, Any]:
        return {
            "inference_record": self.inference_record.to_dict(),
            "tension_record": [item.to_dict() for item in self.tension_record],
            "gap_agenda": self.gap_agenda.to_dict(),
            "validation_agenda": self.validation_agenda.to_dict(),
        }
