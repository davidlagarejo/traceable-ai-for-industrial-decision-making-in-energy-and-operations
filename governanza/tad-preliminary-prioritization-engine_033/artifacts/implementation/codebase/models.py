"""Data models for motor_033 preliminary priority outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


MOTOR_ID = "motor_033"
SYNTHETIC_SUPPORT_FLAG = True
NON_EVIDENTIARY_FLAG = True
RANK_IS_PRELIMINARY = True
DEFAULT_INTENDED_USE = "preliminary_support"

CANNOT_SUBSTITUTE = [
    "TAD_final",
    "inference_case_closure",
    "field_evidence",
    "validation_data",
    "Validation Data Bridge",
    "Verification Bridge",
]

SIGNAL_FIELDS_USED = [
    "priority_signal",
    "support_quality",
    "domain_validity_limits",
    "limitations_note",
]

WEIGHTING_RULE = (
    "For each active case, use valid motor_032 support only. The preliminary "
    "score is the maximum numeric priority_signal for that case after "
    "epistemic flag, phase, provenance, and domain-validity checks. Cases are "
    "ordered by descending preliminary score."
)

PRIORITY_BAND_RULE = (
    "score >= 0.75 -> high_preliminary; score >= 0.50 -> "
    "medium_preliminary; otherwise low_preliminary. Materially conflicting "
    "support signals force limited_confidence regardless of score."
)

TIE_BREAK_RULE = (
    "Exact score ties are retained in rank_uncertainty_record.tie_groups and "
    "ordered deterministically by inference_case_id for a stable register."
)


@dataclass(frozen=True)
class PreliminaryPriorityRegister:
    record_id: str
    motor_033_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    source_problem_ref: str
    expert_spec_ref: str
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    synthetic_support_flag: bool
    non_evidentiary_flag: bool
    rank_is_preliminary: bool
    ranking_basis_ref: str
    rank_uncertainty_ref: str
    ranking_basis: dict[str, Any]
    ranked_cases: list[dict[str, Any]]
    requires_real_evidence: list[str]
    cannot_substitute: list[str]
    active_case_count: int
    ranked_case_count: int
    excluded_case_refs: list[str]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RankingBasis:
    record_id: str
    motor_033_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    source_problem_ref: str
    expert_spec_ref: str
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    synthetic_support_flag: bool
    non_evidentiary_flag: bool
    rank_is_preliminary: bool
    preliminary_priority_register_ref: str
    source_support_refs: list[str]
    source_case_refs: list[str]
    phase_contract_refs: list[str]
    version_record_refs: list[str]
    signal_fields_used: list[str]
    weighting_rule: str
    priority_band_rule: str
    tie_break_rule: str
    excluded_signal_reasons: list[dict[str, str]]
    case_rationales: list[dict[str, Any]]
    rebuild_notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RankUncertaintyRecord:
    record_id: str
    motor_033_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    source_problem_ref: str
    expert_spec_ref: str
    intended_use: str
    domain_validity_limits: str
    limitations_note: str
    synthetic_support_flag: bool
    non_evidentiary_flag: bool
    rank_is_preliminary: bool
    preliminary_priority_register_ref: str
    ranking_basis_ref: str
    affected_case_refs: list[str]
    missing_signal_refs: list[str]
    conflicting_signal_notes: list[dict[str, Any]]
    tie_groups: list[list[str]]
    rank_separation_notes: list[dict[str, Any]]
    generator_sensitivity_notes: list[str]
    insufficient_support_case_refs: list[str]
    requires_real_evidence: list[str]
    uncertainty_level: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PrioritizationResult:
    preliminary_priority_register: PreliminaryPriorityRegister
    ranking_basis: RankingBasis
    rank_uncertainty_record: RankUncertaintyRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "accepted",
            "preliminary_priority_register": (
                self.preliminary_priority_register.to_dict()
            ),
            "ranking_basis": self.ranking_basis.to_dict(),
            "rank_uncertainty_record": self.rank_uncertainty_record.to_dict(),
        }
