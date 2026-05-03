from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import json

from ...domain.entities import ParsedFieldObject
from ...domain.enums import (
    FailureSeverity,
    FailureStage,
    LocationKind,
    ParserStrategyType,
    ParsingStatus,
    PartialParseStatus,
    ReplayabilityStatus,
    WarningSeverity,
    SourceFormatFamily,
)
from ...domain.records import StructuralLocationRecord
from ...domain.value_objects import (
    ParsedFieldObjectId,
    PayloadPath,
    ParsingScopeRef,
    StructuralLocationRecordId,
)
from .results import (
    ParseExecutionResult,
    build_extraction_metadata_record,
    build_parser_strategy_record,
    build_parsed_document_object,
    build_replay_manifest_record,
    build_warning_record,
    expected_output_refs_for_parse,
    failed_parse_result,
)


def _stable_id(prefix: str, *parts: str) -> str:
    from hashlib import sha256

    return f"{prefix}:{sha256('|'.join(parts).encode('utf-8')).hexdigest()[:24]}"


class JsonParserStrategy:
    def __init__(
        self,
        *,
        strategy_version: str = "0.1.0",
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._strategy_version = strategy_version
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def parse(self, captured_raw_asset) -> ParseExecutionResult:
        strategy_record = build_parser_strategy_record(
            parser_strategy_type=ParserStrategyType.JSON_TREE,
            strategy_name="json-basic-strategy",
            strategy_version=self._strategy_version,
            applicable_formats=(SourceFormatFamily.JSON, SourceFormatFamily.API_JSON),
            parameter_fingerprint_value="params:json-basic:default",
            clock=self._clock,
        )
        if captured_raw_asset.raw_asset_version_record.detected_format.value not in {"json", "api_json"}:
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="parser.incompatible_format",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="JSON strategy can only parse raw assets detected as json/api_json.",
                recoverable=False,
                clock=self._clock,
            )

        text = captured_raw_asset.decode_text()
        if not text.strip():
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="json.empty_payload",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="JSON payload is empty.",
                recoverable=False,
                clock=self._clock,
            )

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="json.invalid_payload",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause=f"JSON payload could not be decoded: {exc.msg}.",
                recoverable=False,
                clock=self._clock,
            )

        scalar_entries: list[tuple[str, str, str | None]] = []
        _collect_json_scalars(payload, "$", None, scalar_entries)

        parsing_status = ParsingStatus.COMPLETE
        partial_parse_status = PartialParseStatus.NOT_PARTIAL
        heuristic_notes: tuple[str, ...] = ()
        warnings = []
        if not scalar_entries:
            parsing_status = ParsingStatus.PARTIAL
            partial_parse_status = PartialParseStatus.PARTIAL_LIMITED
            heuristic_notes = ("json.no_scalar_leaf_values",)

        extraction_metadata_record = build_extraction_metadata_record(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            parsing_status=parsing_status,
            partial_parse_status=partial_parse_status,
            heuristic_notes=heuristic_notes,
            clock=self._clock,
        )
        document = build_parsed_document_object(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            document_title=None,
            clock=self._clock,
        )

        if parsing_status is ParsingStatus.PARTIAL:
            warnings.append(
                build_warning_record(
                    scope_ref=ParsingScopeRef.for_parsed_document(document.parsed_document_object_id),
                    warning_code="json.no_scalar_leaf_values",
                    warning_severity=WarningSeverity.MODERATE,
                    message="JSON payload did not expose scalar leaf values; document was materialized as partial.",
                    scope_marker=document.parsed_document_object_id.value,
                    clock=self._clock,
                )
            )

        locations = []
        fields = []
        for index, (payload_path, raw_value, field_name) in enumerate(scalar_entries):
            location = StructuralLocationRecord(
                structural_location_record_id=StructuralLocationRecordId(
                    _stable_id("location_json_path", document.parsed_document_object_id.value, payload_path)
                ),
                location_kind=LocationKind.JSON_PATH,
                page_number=None,
                table_number=None,
                cell_coordinates=None,
                sheet_name=None,
                sheet_index=None,
                block_index=None,
                block_offsets=None,
                selector=None,
                endpoint_reference=None,
                payload_path=PayloadPath(payload_path),
                uri_fragment=None,
            )
            locations.append(location)
            fields.append(
                ParsedFieldObject(
                    parsed_field_object_id=ParsedFieldObjectId(
                        _stable_id("parsed_field_json", document.parsed_document_object_id.value, str(index))
                    ),
                    parsed_document_object_id=document.parsed_document_object_id,
                    raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
                    extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
                    structural_location_record_id=location.structural_location_record_id,
                    parent_table_object_id=None,
                    parent_block_object_id=None,
                    field_name=field_name,
                    raw_value=raw_value,
                    parsing_status=parsing_status,
                    partial_parse_status=partial_parse_status,
                    created_at=self._clock(),
                )
            )

        replay_manifest = build_replay_manifest_record(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            replayability_status=(
                ReplayabilityStatus.PARTIALLY_REPLAYABLE
                if parsing_status is ParsingStatus.PARTIAL
                else ReplayabilityStatus.REPLAYABLE
            ),
            expected_output_refs=expected_output_refs_for_parse(
                extraction_metadata_record=extraction_metadata_record,
                parsed_document_object=document,
                parsed_field_objects=tuple(fields),
            ),
            clock=self._clock,
        )
        return ParseExecutionResult(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            parsed_document_object=document,
            parsed_table_objects=(),
            parsed_field_objects=tuple(fields),
            parsed_block_objects=(),
            structural_location_records=tuple(locations),
            parsing_warning_records=tuple(warnings),
            parsing_failure_records=(),
            parsing_confidence_records=(),
            replay_manifest_record=replay_manifest,
        )


def _collect_json_scalars(
    value,
    path: str,
    field_name: str | None,
    sink: list[tuple[str, str, str | None]],
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            _collect_json_scalars(child, child_path, key, sink)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            _collect_json_scalars(child, child_path, str(index), sink)
        return
    if value is None:
        sink.append((path, "null", field_name))
        return
    if isinstance(value, bool):
        sink.append((path, "true" if value else "false", field_name))
        return
    sink.append((path, str(value), field_name))
