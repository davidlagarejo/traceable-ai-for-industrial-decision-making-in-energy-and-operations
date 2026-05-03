"""Data objects emitted by motor_019."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TargetRef:
    target_type: str
    claim_id: str | None
    tension_id: str | None
    target_label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequiredEvidenceItem:
    evidence_requirement_id: str
    evidence_type: str
    required_level: str
    satisfied_by_refs: list[str]
    is_satisfied: bool
    gap_ref: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationStep:
    step_id: str
    step_type: str
    depends_on_step_ids: list[str]
    input_refs: list[str]
    expected_output: str
    step_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LinkedEvidenceRef:
    evidence_ref_id: str
    upstream_motor_id: str
    upstream_artifact_ref: str
    evidence_level: str
    quality_status: str
    lineage_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationPath:
    path_id: str
    motor_id: str
    target_ref: TargetRef
    source_inference_ref: str
    source_tension_ref: str | None
    phase_contract_id: str
    contract_version: str
    current_evidence_level: str
    target_evidence_level: str
    required_evidence: list[RequiredEvidenceItem]
    linked_evidence_refs: list[LinkedEvidenceRef]
    verification_steps: list[VerificationStep]
    evidence_gap_refs: list[str]
    agenda_ref: str | None
    status: str
    review_trigger: str | None
    rule_version: str
    lineage_refs: list[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceGap:
    gap_id: str
    motor_id: str
    path_id: str
    target_ref: TargetRef
    source_inference_ref: str
    phase_contract_id: str
    contract_version: str
    missing_evidence_type: str
    gap_severity: str
    blocking_reason: str
    recommended_next_action: str
    related_validation_data_refs: list[str]
    resolved_by_ref: str | None
    status: str
    lineage_refs: list[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HardeningAction:
    action_id: str
    path_ref: str
    gap_ref: str | None
    action_type: str
    priority: str
    depends_on_action_ids: list[str]
    expected_evidence_level: str
    owner_role: str
    action_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HardeningAgenda:
    agenda_id: str
    motor_id: str
    path_refs: list[str]
    prioritized_actions: list[HardeningAction]
    dependency_order: list[str]
    blocking_gaps: list[str]
    owner_role: str
    review_trigger: str
    generated_from_version: str
    phase_contract_id: str
    contract_version: str
    status: str
    lineage_refs: list[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationBridgeResult:
    verification_paths: list[VerificationPath]
    hardening_agenda: HardeningAgenda | None
    evidence_gap_records: list[EvidenceGap]
    errors: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_path": [
                path.to_dict() for path in self.verification_paths
            ],
            "hardening_agenda": (
                self.hardening_agenda.to_dict()
                if self.hardening_agenda is not None
                else None
            ),
            "evidence_gap_record": [
                gap.to_dict() for gap in self.evidence_gap_records
            ],
            "errors": self.errors,
        }
