"""Data contracts for motor_004 Ingestion + Parsing Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Mapping, Optional


RawValue = Any


@dataclass(frozen=True)
class IngestionInput:
    """Single payload capture attempt accepted by motor_004."""

    source_ref: str
    payload: bytes | bytearray | str
    media_type: str
    captured_at: str
    phase_contract_ref: str
    lineage_context_ref: str
    parser_profile: str = ""
    parser_version: str = "1.0.0"
    input_kind: str = "raw_source_file"
    status_code: Optional[int] = None
    headers: Mapping[str, str] = field(default_factory=dict)
    url: Optional[str] = None
    file_extension: Optional[str] = None


@dataclass(frozen=True)
class RawRecord:
    raw_record_id: str
    source_ref: str
    raw_payload_ref: str
    content_hash: str
    media_type: str
    captured_at: str
    lineage_id: str
    ingestion_event_id: str
    payload_size_bytes: int
    raw_preservation_status: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class ParsedRecord:
    parsed_record_id: str
    raw_record_id: str
    source_ref: str
    parser_profile: str
    parser_version: str
    parse_status: str
    extracted_fields: Mapping[str, RawValue]
    parse_warnings: tuple[str, ...]
    created_at: str
    ingestion_event_id: str
    version_id: str
    updated_at: str
    version_hash: str
    lineage_id: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class IngestionEvent:
    ingestion_event_id: str
    source_ref: str
    phase_contract_ref: str
    lineage_context_ref: str
    raw_record_ids: tuple[str, ...]
    parsed_record_ids: tuple[str, ...]
    rejection_ids: tuple[str, ...]
    event_status: str
    occurred_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class IngestionRejection:
    ingestion_rejection_id: str
    ingestion_event_id: str
    source_ref: str
    error_code: str
    error_message: str
    rejected_at: str
    phase_contract_ref: str
    lineage_context_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    lineage_id: str
    produced_by_motor: str
    produced_at: str
    parent_id: str


@dataclass(frozen=True)
class IngestionResult:
    raw_record: Optional[RawRecord]
    parsed_record: Optional[ParsedRecord]
    ingestion_lineage: IngestionEvent
    ingestion_rejection: Optional[IngestionRejection]

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_record": _to_plain_data(self.raw_record),
            "parsed_record": _to_plain_data(self.parsed_record),
            "ingestion_lineage": _to_plain_data(self.ingestion_lineage),
            "ingestion_rejection": _to_plain_data(self.ingestion_rejection),
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
