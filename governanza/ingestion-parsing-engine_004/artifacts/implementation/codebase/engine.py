"""Deterministic implementation of motor_004.

The engine preserves the raw payload before creating any parsed output. Parsing
is intentionally shallow and deterministic; downstream normalization, duplicate
resolution, quality scoring, and evidentiary assessment are outside this motor.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from .models import (
    IngestionEvent,
    IngestionInput,
    IngestionRejection,
    IngestionResult,
    ParsedRecord,
    RawRecord,
)


MOTOR_ID = "motor_004"


class InMemoryRawPayloadStore:
    """Minimal immutable raw payload store used by the standalone motor."""

    def __init__(self) -> None:
        self._payloads: dict[str, bytes] = {}

    def preserve(self, raw_payload_ref: str, payload: bytes) -> None:
        existing = self._payloads.get(raw_payload_ref)
        if existing is not None and existing != payload:
            raise RawPreservationError(
                f"raw_payload_ref already exists with different bytes: {raw_payload_ref}"
            )
        self._payloads[raw_payload_ref] = payload

    def get(self, raw_payload_ref: str) -> bytes:
        return self._payloads[raw_payload_ref]


class RawPreservationError(RuntimeError):
    """Raised only when the internal immutable raw store detects mutation."""


@dataclass(frozen=True)
class _ParseOutcome:
    parser_profile: str
    parse_status: str
    extracted_fields: Mapping[str, Any]
    parse_warnings: tuple[str, ...]


@dataclass(frozen=True)
class _ValidationFailure:
    error_code: str
    error_message: str


class IngestionParsingEngine:
    """Capture raw payloads and emit partial parsed structure with lineage."""

    allowed_rejection_codes = frozenset(
        {
            "INGESTION_MISSING_SOURCE_REF",
            "INGESTION_EMPTY_PAYLOAD",
            "INGESTION_MISSING_CONTENT_TYPE",
            "INGESTION_MISSING_LINEAGE_CONTEXT",
            "INGESTION_PHASE_CONTRACT_DENIED",
        }
    )

    def __init__(self, raw_store: Optional[InMemoryRawPayloadStore] = None) -> None:
        self.raw_store = raw_store if raw_store is not None else InMemoryRawPayloadStore()
        self._attempt_counter = 0

    def ingest(self, capture: IngestionInput | Mapping[str, Any]) -> IngestionResult:
        ingestion_input = self._coerce_input(capture)
        payload_bytes = self._payload_to_bytes(ingestion_input.payload)
        self._attempt_counter += 1

        event_id = self._stable_id(
            "ingestion_event",
            str(self._attempt_counter),
            ingestion_input.source_ref,
            ingestion_input.captured_at,
            ingestion_input.phase_contract_ref,
            ingestion_input.lineage_context_ref,
            self._hash_bytes(payload_bytes),
        )
        occurred_at = ingestion_input.captured_at

        validation_failure = self._validate_preconditions(ingestion_input, payload_bytes)
        if validation_failure is not None:
            return self._build_rejection_result(
                ingestion_input=ingestion_input,
                event_id=event_id,
                occurred_at=occurred_at,
                failure=validation_failure,
            )

        content_hash = self._hash_bytes(payload_bytes)
        parser_profile = self._select_parser_profile(ingestion_input)
        media_type = self._declared_media_type(ingestion_input)
        raw_record_id = self._stable_id(
            "raw_record",
            event_id,
            ingestion_input.source_ref,
            ingestion_input.captured_at,
            content_hash,
        )
        raw_payload_ref = self._raw_payload_ref(
            lineage_context_ref=ingestion_input.lineage_context_ref,
            raw_record_id=raw_record_id,
            content_hash=content_hash,
        )

        self.raw_store.preserve(raw_payload_ref, payload_bytes)
        raw_record = self._build_raw_record(
            ingestion_input=ingestion_input,
            event_id=event_id,
            raw_record_id=raw_record_id,
            raw_payload_ref=raw_payload_ref,
            content_hash=content_hash,
            media_type=media_type,
            payload_size_bytes=len(payload_bytes),
        )

        parse_outcome = self._parse_payload(
            payload=payload_bytes,
            media_type=media_type,
            parser_profile=parser_profile,
        )
        parsed_record = self._build_parsed_record(
            ingestion_input=ingestion_input,
            event_id=event_id,
            raw_record=raw_record,
            parse_outcome=parse_outcome,
        )
        event_status = (
            "accepted"
            if parse_outcome.parse_status == "parsed" and not parse_outcome.parse_warnings
            else "accepted_with_parse_warning"
        )
        event = self._build_event(
            ingestion_input=ingestion_input,
            event_id=event_id,
            occurred_at=occurred_at,
            raw_record_ids=(raw_record.raw_record_id,),
            parsed_record_ids=(parsed_record.parsed_record_id,),
            rejection_ids=(),
            event_status=event_status,
        )

        return IngestionResult(
            raw_record=raw_record,
            parsed_record=parsed_record,
            ingestion_lineage=event,
            ingestion_rejection=None,
        )

    def ingest_api_response(
        self,
        *,
        source_ref: str,
        body: bytes | bytearray | str,
        status_code: int,
        media_type: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
        parser_profile: str = "",
        parser_version: str = "1.0.0",
        headers: Optional[Mapping[str, str]] = None,
        url: Optional[str] = None,
    ) -> IngestionResult:
        return self.ingest(
            IngestionInput(
                source_ref=source_ref,
                payload=body,
                media_type=media_type,
                captured_at=captured_at,
                phase_contract_ref=phase_contract_ref,
                lineage_context_ref=lineage_context_ref,
                parser_profile=parser_profile,
                parser_version=parser_version,
                input_kind="api_response",
                status_code=status_code,
                headers=headers or {},
                url=url,
            )
        )

    def ingest_raw_source_file(
        self,
        *,
        source_ref: str,
        payload: bytes | bytearray | str,
        media_type: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
        parser_profile: str = "",
        parser_version: str = "1.0.0",
        file_extension: Optional[str] = None,
    ) -> IngestionResult:
        return self.ingest(
            IngestionInput(
                source_ref=source_ref,
                payload=payload,
                media_type=media_type,
                captured_at=captured_at,
                phase_contract_ref=phase_contract_ref,
                lineage_context_ref=lineage_context_ref,
                parser_profile=parser_profile,
                parser_version=parser_version,
                input_kind="raw_source_file",
                file_extension=file_extension,
            )
        )

    def ingest_structured_feed(
        self,
        *,
        source_ref: str,
        payload: bytes | bytearray | str,
        media_type: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
        parser_profile: str = "",
        parser_version: str = "1.0.0",
    ) -> IngestionResult:
        return self.ingest(
            IngestionInput(
                source_ref=source_ref,
                payload=payload,
                media_type=media_type,
                captured_at=captured_at,
                phase_contract_ref=phase_contract_ref,
                lineage_context_ref=lineage_context_ref,
                parser_profile=parser_profile,
                parser_version=parser_version,
                input_kind="structured_feed",
            )
        )

    def get_preserved_payload(self, raw_payload_ref: str) -> bytes:
        return self.raw_store.get(raw_payload_ref)

    def _coerce_input(self, capture: IngestionInput | Mapping[str, Any]) -> IngestionInput:
        if isinstance(capture, IngestionInput):
            return capture
        return IngestionInput(
            source_ref=str(capture.get("source_ref", "")),
            payload=capture.get("payload", b""),
            media_type=str(capture.get("media_type", "")),
            captured_at=str(capture.get("captured_at", "")),
            phase_contract_ref=str(capture.get("phase_contract_ref", "")),
            lineage_context_ref=str(capture.get("lineage_context_ref", "")),
            parser_profile=str(capture.get("parser_profile", "")),
            parser_version=str(capture.get("parser_version", "1.0.0")),
            input_kind=str(capture.get("input_kind", "raw_source_file")),
            status_code=capture.get("status_code"),
            headers=capture.get("headers", {}) or {},
            url=capture.get("url"),
            file_extension=capture.get("file_extension"),
        )

    def _validate_preconditions(
        self, ingestion_input: IngestionInput, payload: bytes
    ) -> Optional[_ValidationFailure]:
        if not self._stable_ref(ingestion_input.source_ref):
            return _ValidationFailure(
                "INGESTION_MISSING_SOURCE_REF",
                "stable source_ref is required before raw preservation",
            )
        if len(payload) == 0:
            return _ValidationFailure(
                "INGESTION_EMPTY_PAYLOAD",
                "raw payload bytes are empty",
            )
        if not self._has_content_declaration(ingestion_input):
            return _ValidationFailure(
                "INGESTION_MISSING_CONTENT_TYPE",
                "media_type, file_extension, or parser_profile is required",
            )
        if not self._stable_ref(ingestion_input.lineage_context_ref):
            return _ValidationFailure(
                "INGESTION_MISSING_LINEAGE_CONTEXT",
                "lineage_context_ref is required for motor_002 attachment",
            )
        if not self._stable_ref(ingestion_input.captured_at):
            return _ValidationFailure(
                "INGESTION_MISSING_LINEAGE_CONTEXT",
                "captured_at is required for reconstructible lineage",
            )
        if not self._phase_contract_allows(ingestion_input.phase_contract_ref):
            return _ValidationFailure(
                "INGESTION_PHASE_CONTRACT_DENIED",
                "phase_contract_ref does not authorize this capture",
            )
        return None

    def _build_rejection_result(
        self,
        *,
        ingestion_input: IngestionInput,
        event_id: str,
        occurred_at: str,
        failure: _ValidationFailure,
    ) -> IngestionResult:
        if failure.error_code not in self.allowed_rejection_codes:
            raise ValueError(f"unsupported ingestion rejection code: {failure.error_code}")
        rejection_id = self._stable_id("ingestion_rejection", event_id, failure.error_code)
        produced_at = occurred_at
        rejection_fields = {
            "ingestion_rejection_id": rejection_id,
            "ingestion_event_id": event_id,
            "source_ref": ingestion_input.source_ref,
            "error_code": failure.error_code,
            "error_message": failure.error_message,
            "rejected_at": occurred_at,
            "phase_contract_ref": ingestion_input.phase_contract_ref,
            "lineage_context_ref": ingestion_input.lineage_context_ref,
            "version_id": self._version_id(rejection_id),
            "created_at": occurred_at,
            "updated_at": occurred_at,
            "lineage_id": ingestion_input.lineage_context_ref,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": event_id,
        }
        rejection = IngestionRejection(
            **rejection_fields,
            version_hash=self._version_hash(rejection_fields),
        )
        event = self._build_event(
            ingestion_input=ingestion_input,
            event_id=event_id,
            occurred_at=occurred_at,
            raw_record_ids=(),
            parsed_record_ids=(),
            rejection_ids=(rejection.ingestion_rejection_id,),
            event_status="rejected",
        )
        return IngestionResult(
            raw_record=None,
            parsed_record=None,
            ingestion_lineage=event,
            ingestion_rejection=rejection,
        )

    def _build_raw_record(
        self,
        *,
        ingestion_input: IngestionInput,
        event_id: str,
        raw_record_id: str,
        raw_payload_ref: str,
        content_hash: str,
        media_type: str,
        payload_size_bytes: int,
    ) -> RawRecord:
        fields = {
            "raw_record_id": raw_record_id,
            "source_ref": ingestion_input.source_ref,
            "raw_payload_ref": raw_payload_ref,
            "content_hash": content_hash,
            "media_type": media_type,
            "captured_at": ingestion_input.captured_at,
            "lineage_id": ingestion_input.lineage_context_ref,
            "ingestion_event_id": event_id,
            "payload_size_bytes": payload_size_bytes,
            "raw_preservation_status": "preserved",
            "version_id": self._version_id(raw_record_id),
            "created_at": ingestion_input.captured_at,
            "updated_at": ingestion_input.captured_at,
            "produced_by_motor": MOTOR_ID,
            "produced_at": ingestion_input.captured_at,
            "parent_id": event_id,
        }
        return RawRecord(**fields, version_hash=self._version_hash(fields))

    def _build_parsed_record(
        self,
        *,
        ingestion_input: IngestionInput,
        event_id: str,
        raw_record: RawRecord,
        parse_outcome: _ParseOutcome,
    ) -> ParsedRecord:
        parsed_record_id = self._stable_id(
            "parsed_record",
            raw_record.raw_record_id,
            parse_outcome.parser_profile,
            ingestion_input.parser_version,
        )
        fields = {
            "parsed_record_id": parsed_record_id,
            "raw_record_id": raw_record.raw_record_id,
            "source_ref": ingestion_input.source_ref,
            "parser_profile": parse_outcome.parser_profile,
            "parser_version": ingestion_input.parser_version,
            "parse_status": parse_outcome.parse_status,
            "extracted_fields": parse_outcome.extracted_fields,
            "parse_warnings": parse_outcome.parse_warnings,
            "created_at": ingestion_input.captured_at,
            "ingestion_event_id": event_id,
            "version_id": self._version_id(parsed_record_id),
            "updated_at": ingestion_input.captured_at,
            "lineage_id": ingestion_input.lineage_context_ref,
            "produced_by_motor": MOTOR_ID,
            "produced_at": ingestion_input.captured_at,
            "parent_id": raw_record.raw_record_id,
        }
        return ParsedRecord(**fields, version_hash=self._version_hash(fields))

    def _build_event(
        self,
        *,
        ingestion_input: IngestionInput,
        event_id: str,
        occurred_at: str,
        raw_record_ids: tuple[str, ...],
        parsed_record_ids: tuple[str, ...],
        rejection_ids: tuple[str, ...],
        event_status: str,
    ) -> IngestionEvent:
        fields = {
            "ingestion_event_id": event_id,
            "source_ref": ingestion_input.source_ref,
            "phase_contract_ref": ingestion_input.phase_contract_ref,
            "lineage_context_ref": ingestion_input.lineage_context_ref,
            "raw_record_ids": raw_record_ids,
            "parsed_record_ids": parsed_record_ids,
            "rejection_ids": rejection_ids,
            "event_status": event_status,
            "occurred_at": occurred_at,
            "version_id": self._version_id(event_id),
            "created_at": occurred_at,
            "updated_at": occurred_at,
            "produced_by_motor": MOTOR_ID,
            "produced_at": occurred_at,
            "parent_id": ingestion_input.lineage_context_ref,
        }
        return IngestionEvent(**fields, version_hash=self._version_hash(fields))

    def _parse_payload(
        self, *, payload: bytes, media_type: str, parser_profile: str
    ) -> _ParseOutcome:
        profile = parser_profile or self._select_parser_profile_from_media_type(media_type)
        if profile == "json_flat_v1":
            return self._parse_json_flat(payload, profile)
        if profile == "csv_header_row_v1":
            return self._parse_csv_header_row(payload, profile)
        if profile == "ndjson_line_v1":
            return self._parse_ndjson_lines(payload, profile)
        if profile == "binary_preserve_only_v1":
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="unsupported_format",
                extracted_fields={},
                parse_warnings=("payload preserved without structured parser",),
            )
        return _ParseOutcome(
            parser_profile=profile,
            parse_status="unsupported_format",
            extracted_fields={},
            parse_warnings=(f"unsupported parser_profile: {profile}",),
        )

    def _parse_json_flat(self, payload: bytes, profile: str) -> _ParseOutcome:
        try:
            decoded = payload.decode("utf-8")
            data = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="parse_failed",
                extracted_fields={},
                parse_warnings=(f"json parse failed: {exc.__class__.__name__}",),
            )

        if not isinstance(data, dict):
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="partially_parsed",
                extracted_fields={"root": data},
                parse_warnings=("json root is not an object",),
            )

        extracted: dict[str, Any] = {}
        warnings: list[str] = []
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                extracted[str(key)] = value
            else:
                warnings.append(f"nested field not extracted: {key}")
        status = "parsed" if not warnings else "partially_parsed"
        if not extracted:
            status = "partially_parsed"
            warnings.append("json object contained no flat scalar fields")
        return _ParseOutcome(
            parser_profile=profile,
            parse_status=status,
            extracted_fields=extracted,
            parse_warnings=tuple(warnings),
        )

    def _parse_csv_header_row(self, payload: bytes, profile: str) -> _ParseOutcome:
        try:
            decoded = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="parse_failed",
                extracted_fields={},
                parse_warnings=(f"csv decode failed: {exc.__class__.__name__}",),
            )

        reader = csv.DictReader(io.StringIO(decoded), skipinitialspace=False)
        if not reader.fieldnames:
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="parse_failed",
                extracted_fields={},
                parse_warnings=("csv header row is missing",),
            )

        rows = list(reader)
        if not rows:
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="partially_parsed",
                extracted_fields={},
                parse_warnings=("csv header observed with zero data rows",),
            )

        warnings: list[str] = []
        cleaned_rows: list[dict[str, str]] = []
        for row_index, row in enumerate(rows, start=1):
            cleaned: dict[str, str] = {}
            for key, value in row.items():
                field_name = "" if key is None else str(key)
                if value is None or value == "":
                    warnings.append(f"source-empty field at row {row_index}: {field_name}")
                    continue
                cleaned[field_name] = value
            cleaned_rows.append(cleaned)

        extracted: Mapping[str, Any]
        if len(cleaned_rows) == 1:
            extracted = cleaned_rows[0]
        else:
            extracted = {"rows": cleaned_rows}
        return _ParseOutcome(
            parser_profile=profile,
            parse_status="parsed" if not warnings else "partially_parsed",
            extracted_fields=extracted,
            parse_warnings=tuple(warnings),
        )

    def _parse_ndjson_lines(self, payload: bytes, profile: str) -> _ParseOutcome:
        try:
            decoded = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="parse_failed",
                extracted_fields={},
                parse_warnings=(f"ndjson decode failed: {exc.__class__.__name__}",),
            )

        rows: list[Any] = []
        warnings: list[str] = []
        for line_number, line in enumerate(decoded.splitlines(), start=1):
            if line == "":
                warnings.append(f"empty ndjson line ignored: {line_number}")
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                warnings.append(f"malformed ndjson line not extracted: {line_number}")

        if not rows:
            return _ParseOutcome(
                parser_profile=profile,
                parse_status="parse_failed" if warnings else "partially_parsed",
                extracted_fields={},
                parse_warnings=tuple(warnings or ["ndjson payload had no lines"]),
            )
        return _ParseOutcome(
            parser_profile=profile,
            parse_status="parsed" if not warnings else "partially_parsed",
            extracted_fields={"rows": rows},
            parse_warnings=tuple(warnings),
        )

    def _select_parser_profile(self, ingestion_input: IngestionInput) -> str:
        if ingestion_input.parser_profile:
            return ingestion_input.parser_profile
        return self._select_parser_profile_from_media_type(self._declared_media_type(ingestion_input))

    def _select_parser_profile_from_media_type(self, media_type: str) -> str:
        lower_media_type = media_type.lower()
        if lower_media_type == "application/json" or lower_media_type.endswith("+json"):
            return "json_flat_v1"
        if lower_media_type in {"text/csv", "application/csv"}:
            return "csv_header_row_v1"
        if lower_media_type in {"application/x-ndjson", "application/ndjson"}:
            return "ndjson_line_v1"
        return "binary_preserve_only_v1"

    def _payload_to_bytes(self, payload: bytes | bytearray | str) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, bytearray):
            return bytes(payload)
        if isinstance(payload, str):
            return payload.encode("utf-8")
        raise TypeError(f"unsupported payload type: {type(payload).__name__}")

    def _has_content_declaration(self, ingestion_input: IngestionInput) -> bool:
        return any(
            self._stable_ref(value)
            for value in (
                ingestion_input.media_type,
                ingestion_input.file_extension or "",
                ingestion_input.parser_profile,
            )
        )

    def _declared_media_type(self, ingestion_input: IngestionInput) -> str:
        if ingestion_input.media_type:
            return ingestion_input.media_type
        if ingestion_input.file_extension:
            return f"file_extension:{ingestion_input.file_extension}"
        return f"parser_profile:{ingestion_input.parser_profile}"

    def _phase_contract_allows(self, phase_contract_ref: str) -> bool:
        if not self._stable_ref(phase_contract_ref):
            return False
        lower_ref = phase_contract_ref.lower()
        denied_tokens = (
            ":deny",
            ":denied",
            ":blocked",
            ":disallow",
            ":forbid",
            "not_allowed",
        )
        return not any(token in lower_ref for token in denied_tokens)

    def _stable_ref(self, value: str) -> bool:
        stripped = value.strip() if isinstance(value, str) else ""
        return stripped not in {"", "unknown", "undefined", "null", "none"}

    def _raw_payload_ref(
        self, *, lineage_context_ref: str, raw_record_id: str, content_hash: str
    ) -> str:
        lineage_segment = self._safe_ref_segment(lineage_context_ref)
        return f"raw://{MOTOR_ID}/{lineage_segment}/{raw_record_id}/{content_hash}"

    def _safe_ref_segment(self, value: str) -> str:
        return "".join(char if char.isalnum() or char in "-_." else "_" for char in value)

    def _stable_id(self, prefix: str, *parts: str) -> str:
        digest = self._hash_text("\u001f".join(str(part) for part in parts))[:24]
        return f"{prefix}_{digest}"

    def _version_id(self, object_id: str) -> str:
        return f"{object_id}:v1"

    def _version_hash(self, fields: Mapping[str, Any]) -> str:
        return self._hash_text(self._canonical_json(fields))

    def _hash_bytes(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    def _hash_text(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _canonical_json(self, value: Mapping[str, Any]) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
