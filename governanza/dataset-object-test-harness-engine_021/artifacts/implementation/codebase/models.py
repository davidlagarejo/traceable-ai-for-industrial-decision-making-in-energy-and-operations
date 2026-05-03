"""Output models for motor_021."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TestResult:
    test_id: str
    harness_run_id: str
    case_name: str
    case_version: str
    status: str
    input_refs: List[str]
    expected_condition: str
    observed_condition: str
    failure_ids: List[str]
    severity: str
    error_code: Optional[str]
    harness_version: str
    executed_at: str
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
class IntegrationFailure:
    failure_id: str
    harness_run_id: str
    test_id: str
    failure_type: str
    affected_object_ref: str
    expected_ref: str
    observed_value: str
    source_input_refs: List[str]
    severity: str
    owner_motor_ref: str
    recommended_action: str
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
class HarnessReport:
    harness_run_id: str
    harness_version: str
    test_result_ids: List[str]
    tested_contract_refs: List[str]
    tested_object_refs: List[str]
    result_counts: Dict[str, int]
    coverage_summary: Dict[str, Any]
    failure_ids: List[str]
    failure_log_ref: Optional[str]
    status: str
    decision_reason: str
    generated_at: str
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
