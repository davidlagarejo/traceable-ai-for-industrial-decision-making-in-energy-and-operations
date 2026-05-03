"""Output models for Source Change Detection / Refresh Intelligence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ChangeEvent:
    record_id: str
    event_id: str
    source_id: str
    change_type: str
    detected_at: str
    severity: str
    previous_ingestion_ref: str | None
    current_ingestion_ref: str | None
    previous_version_ref: str | None
    current_version_ref: str | None
    comparison_basis: dict[str, Any]
    evidence_refs: list[str]
    lineage_refs: list[str]
    detection_rule_ref: str
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
class RefreshPriority:
    record_id: str
    priority_id: str
    source_id: str
    priority_level: str
    priority_reason: str
    derived_from_event_ids: list[str]
    staleness_id: str | None
    rule_ref: str
    calculated_at: str
    evidence_refs: list[str]
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
class StalenessRecord:
    record_id: str
    staleness_id: str
    source_id: str
    staleness_status: str
    last_observed_at: str | None
    expected_refresh_interval: str | None
    age_days: int | None
    triggering_condition: str
    trigger_event_ids: list[str]
    basis_ingestion_refs: list[str]
    basis_version_refs: list[str]
    calculated_at: str
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
class StructuredError:
    error_code: str
    source_id: str | None
    message: str
    input_refs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
