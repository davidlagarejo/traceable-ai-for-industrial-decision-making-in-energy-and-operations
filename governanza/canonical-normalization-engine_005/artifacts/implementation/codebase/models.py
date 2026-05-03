"""Data contracts for motor_005 Canonical Normalization Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class NormalizedRecord:
    record_id: str
    source_id: str
    taxonomy_id: str
    taxonomy_version: str
    normalized_fields: Mapping[str, Any]
    unmapped_fields: tuple[Mapping[str, Any], ...]
    normalization_trace_ref: str
    normalization_rule_log_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class NormalizationRule:
    rule_id: str
    taxonomy_id: str
    taxonomy_version: str
    source_pattern: str
    canonical_field: str
    normalization_type: str
    allowed_value_type: str
    rule_priority: int
    conflict_policy: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class FieldMapping:
    mapping_id: str
    record_id: str
    source_field: str
    canonical_field: Optional[str]
    original_value: Any
    normalized_value: Any
    mapping_status: str
    rule_id: Optional[str]
    taxonomy_version: str
    provenance_ref: str
    error_code: Optional[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class NormalizationRejection:
    error_code: str
    error_message: str
    record_id: Optional[str]
    taxonomy_id: Optional[str]
    produced_by_motor: str


@dataclass(frozen=True)
class NormalizationResult:
    normalized_record: Optional[NormalizedRecord]
    normalization_rule_log: tuple[Mapping[str, Any], ...]
    field_mapping_trace: tuple[FieldMapping, ...]
    rejection: Optional[NormalizationRejection]

    def to_dict(self) -> dict[str, Any]:
        return {
            "normalized_record": _to_plain_data(self.normalized_record),
            "normalization_rule_log": _to_plain_data(self.normalization_rule_log),
            "field_mapping_trace": _to_plain_data(self.field_mapping_trace),
            "rejection": _to_plain_data(self.rejection),
        }


def _to_plain_data(value: Any) -> Any:
    if value is None:
        return None
    if is_dataclass(value):
        return _to_plain_data(asdict(value))
    if isinstance(value, tuple):
        return [_to_plain_data(item) for item in value]
    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_plain_data(item) for key, item in value.items()}
    return value
