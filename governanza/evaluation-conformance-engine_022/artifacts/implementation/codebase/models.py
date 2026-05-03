"""Output models for motor_022."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ConformanceRecord:
    record_id: str
    evaluated_object_id: str
    evaluated_object_type: str
    evaluated_version_id: str
    contract_id: str
    contract_version_id: str
    lineage_id: str
    quality_record_ids: List[str]
    harness_result_ids: List[str]
    status: str
    status_reason: str
    violation_ids: List[str]
    drift_signal_ids: List[str]
    evidence_refs: List[str]
    evaluated_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ViolationRecord:
    violation_id: str
    conformance_record_id: str
    evaluated_object_id: str
    evaluated_version_id: str
    violation_type: str
    rule_ref: str
    severity: str
    input_ref: str
    expected_condition: str
    observed_value: str
    material: bool
    evidence_refs: List[str]
    detected_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DriftSignal:
    signal_id: str
    scope: str
    scope_ref: str
    basis: str
    severity: str
    related_violation_ids: List[str]
    related_conformance_record_ids: List[str]
    evidence_refs: List[str]
    emitted_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
