"""Output models for motor_007."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FitnessScore:
    score_id: str
    total_score: float
    dimension_scores: Dict[str, float]
    threshold_applied: float
    dimension_thresholds: Dict[str, float]
    scoring_rule_version: str
    blocking_flag_present: bool
    score_basis: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QualityFlag:
    flag_id: str
    code: str
    severity: str
    dimension: str
    message: str
    affected_field: Optional[str]
    contract_rule_ref: Optional[str]
    blocking: bool
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DisqualificationReason:
    reason_id: str
    code: str
    severity: str
    threshold_failed: str
    explanation: str
    supporting_flags: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QualityRecord:
    quality_record_id: str
    subject_ref: str
    subject_version_ref: str
    phase_contract_ref: str
    phase_contract_version: str
    evaluation_run_id: str
    evaluation_status: str
    fitness_score: FitnessScore
    quality_flags: List[QualityFlag]
    disqualification_reason: Optional[DisqualificationReason]
    evaluated_dimensions: List[str]
    evaluation_errors: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data
