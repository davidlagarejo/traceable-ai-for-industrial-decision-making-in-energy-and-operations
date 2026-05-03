"""Data models for motor_032 synthetic support integration outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


MOTOR_ID = "motor_032"
SYNTHETIC_SUPPORT_FLAG = True
NON_EVIDENTIARY_FLAG = True
DEFAULT_INTENDED_USE = "preliminary_support"

SUPPORT_LEVELS = {"exploratory", "preliminary_signal", "capability_demo"}
PERMITTED_EFFECTS = {"exploration", "preliminary_prioritization"}

CANNOT_SUBSTITUTE = [
    "Validation Data Bridge",
    "Verification Bridge",
    "field_evidence",
    "validation_data",
    "claim_closure",
    "final_TAD_output",
]

REJECTION_BOUNDARIES = [
    "decision_grade_promotion",
    "claim_closure",
    "field_validation",
    "Validation Data Bridge replacement",
    "Verification Bridge replacement",
    "field_evidence replacement",
    "validation_data replacement",
    "final_TAD_output",
]

HANDOFF_LABELS = [
    "synthetic_support",
    "non_evidentiary",
    "subordinate_signal",
    "preliminary_support",
]

DESTINATION_CONSUMERS = [
    "Decision Core handoff",
    "audit trail",
    "motor_033 preliminary prioritization",
]


@dataclass(frozen=True)
class SyntheticMLSupportRegister:
    support_register_id: str
    source_report_id: str
    source_ref: str
    source_problem_ref: str
    expert_spec_ref: str
    target_inference_record_id: str
    phase_contract_ref: str
    version_refs: dict[str, str]
    generator_version: str
    support_level: str
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    gap_to_real_validation: str
    gap_to_deployment: str
    known_failure_modes: list[str]
    cannot_substitute: list[str]
    lineage_id: str
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
class HypothesisSignal:
    hypothesis_signal_id: str
    support_register_id: str
    source_report_id: str
    source_ref: str
    source_problem_ref: str
    expert_spec_ref: str
    target_inference_record_id: str
    signal_role: str
    evidence_level: str
    intended_use: str
    permitted_effect: str
    decision_grade_change_allowed: bool
    domain_validity_limits: str
    limitations_note: str
    version_refs: dict[str, str]
    lineage_id: str
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
class LabeledSupportRecord:
    labeled_support_record_id: str
    support_register_id: str
    hypothesis_signal_id: str
    source_report_id: str
    source_ref: str
    source_problem_ref: str
    expert_spec_ref: str
    target_inference_record_id: str
    labels: list[str]
    support_level: str
    intended_use: str
    destination_consumers: list[str]
    rejection_boundaries: list[str]
    cannot_substitute: list[str]
    upstream_version_refs: list[str]
    version_refs: dict[str, str]
    generator_version: str
    domain_validity_limits: str
    limitations_note: str
    lineage_id: str
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
class IntegrationResult:
    synthetic_ml_support_register: SyntheticMLSupportRegister
    hypothesis_signal: HypothesisSignal
    labeled_support_record: LabeledSupportRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "accepted",
            "synthetic_ml_support_register": (
                self.synthetic_ml_support_register.to_dict()
            ),
            "hypothesis_signal": self.hypothesis_signal.to_dict(),
            "labeled_support_record": self.labeled_support_record.to_dict(),
        }
