"""Domain models for motor_024 — Governance Event & Exception Registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class GovernanceEvent:
    governance_event_id: str
    event_type: str
    source_motor_id: str
    captured_at: str
    phase_contract_ref: str
    lineage_id: str
    raw_event_payload: Mapping[str, Any]
    version_id: str
    version_hash: str
    created_at: str
    updated_at: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class ExceptionRecord:
    exception_record_id: str
    governance_event_id: str
    source_motor_id: str
    exception_code: str
    exception_payload: Mapping[str, Any]
    lineage_id: str
    version_id: str
    version_hash: str
    created_at: str
    produced_by_motor: str
    produced_at: str


@dataclass(frozen=True)
class TensionSignal:
    tension_signal_id: str
    governance_event_id: str
    motor_a_id: str
    motor_b_id: str
    conflict_description: str
    lineage_id: str
    version_id: str
    version_hash: str
    created_at: str
    produced_by_motor: str
    produced_at: str


@dataclass(frozen=True)
class GovernanceRejection:
    error_code: str
    error_message: str
    source_motor_id: str
    captured_at: str


@dataclass(frozen=True)
class GovernanceEventResult:
    governance_event: Optional[GovernanceEvent]
    exception_record: Optional[ExceptionRecord]
    tension_signal: Optional[TensionSignal]
    rejection: Optional[GovernanceRejection]
