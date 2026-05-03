from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from ...domain.entities import ParsedBlockObject
from ...domain.enums import (
    FailureSeverity,
    FailureStage,
    LocationKind,
    ParserStrategyType,
    ParsingStatus,
    PartialParseStatus,
    ReplayabilityStatus,
    SourceFormatFamily,
)
from ...domain.records import StructuralLocationRecord
from ...domain.value_objects import (
    BlockOffsets,
    ParsedBlockObjectId,
    StructuralLocationRecordId,
)
from .results import (
    ParseExecutionResult,
    build_extraction_metadata_record,
    build_parser_strategy_record,
    build_parsed_document_object,
    build_replay_manifest_record,
    expected_output_refs_for_parse,
    failed_parse_result,
)


def _stable_id(prefix: str, *parts: str) -> str:
    from hashlib import sha256

    return f"{prefix}:{sha256('|'.join(parts).encode('utf-8')).hexdigest()[:24]}"


class PlainTextParserStrategy:
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
            parser_strategy_type=ParserStrategyType.TEXT_BLOCK,
            strategy_name="plain-text-basic-strategy",
            strategy_version=self._strategy_version,
            applicable_formats=(SourceFormatFamily.TEXT_DOCUMENT,),
            parameter_fingerprint_value="params:text-basic:default",
            clock=self._clock,
        )
        if captured_raw_asset.raw_asset_version_record.detected_format.value != "text_document":
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="parser.incompatible_format",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="Plain-text strategy can only parse raw assets detected as text_document.",
                recoverable=False,
                clock=self._clock,
            )

        text = captured_raw_asset.decode_text()
        if not text.strip():
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="text.empty_payload",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.BLOCK_PARSE,
                cause="Text payload is empty.",
                recoverable=False,
                clock=self._clock,
            )

        blocks_data = _split_text_blocks(text)
        extraction_metadata_record = build_extraction_metadata_record(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            parsing_status=ParsingStatus.COMPLETE,
            partial_parse_status=PartialParseStatus.NOT_PARTIAL,
            heuristic_notes=(),
            clock=self._clock,
        )
        document = build_parsed_document_object(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            document_title=blocks_data[0][0].splitlines()[0][:80] if blocks_data else None,
            clock=self._clock,
        )
        locations = []
        blocks = []
        for index, (block_text, start_offset, end_offset) in enumerate(blocks_data, start=1):
            location = StructuralLocationRecord(
                structural_location_record_id=StructuralLocationRecordId(
                    _stable_id("location_text_block", document.parsed_document_object_id.value, str(index))
                ),
                location_kind=LocationKind.TEXT_BLOCK,
                page_number=None,
                table_number=None,
                cell_coordinates=None,
                sheet_name=None,
                sheet_index=None,
                block_index=index,
                block_offsets=BlockOffsets(start_offset, end_offset),
                selector=None,
                endpoint_reference=None,
                payload_path=None,
                uri_fragment=None,
            )
            locations.append(location)
            blocks.append(
                ParsedBlockObject(
                    parsed_block_object_id=ParsedBlockObjectId(
                        _stable_id("parsed_block_text", document.parsed_document_object_id.value, str(index))
                    ),
                    parsed_document_object_id=document.parsed_document_object_id,
                    raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
                    extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
                    structural_location_record_id=location.structural_location_record_id,
                    parent_table_object_id=None,
                    raw_text=block_text,
                    parsing_status=ParsingStatus.COMPLETE,
                    partial_parse_status=PartialParseStatus.NOT_PARTIAL,
                    created_at=self._clock(),
                )
            )

        replay_manifest = build_replay_manifest_record(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            replayability_status=ReplayabilityStatus.REPLAYABLE,
            expected_output_refs=expected_output_refs_for_parse(
                extraction_metadata_record=extraction_metadata_record,
                parsed_document_object=document,
                parsed_block_objects=tuple(blocks),
            ),
            clock=self._clock,
        )
        return ParseExecutionResult(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            parsed_document_object=document,
            parsed_table_objects=(),
            parsed_field_objects=(),
            parsed_block_objects=tuple(blocks),
            structural_location_records=tuple(locations),
            parsing_warning_records=(),
            parsing_failure_records=(),
            parsing_confidence_records=(),
            replay_manifest_record=replay_manifest,
        )


def _split_text_blocks(text: str) -> tuple[tuple[str, int, int], ...]:
    blocks: list[tuple[str, int, int]] = []
    block_start: int | None = None
    cursor = 0
    length = len(text)

    while cursor < length:
        while cursor < length and text[cursor].isspace():
            cursor += 1
        if cursor >= length:
            break
        block_start = cursor
        while cursor < length:
            if text[cursor] == "\n" and _next_non_newline_is_newline(text, cursor):
                break
            cursor += 1
        block_end = cursor
        block_text = text[block_start:block_end].strip()
        if block_text:
            blocks.append((block_text, block_start, block_end))
        while cursor < length and text[cursor].isspace():
            cursor += 1
    return tuple(blocks)


def _next_non_newline_is_newline(text: str, index: int) -> bool:
    cursor = index
    newline_count = 0
    while cursor < len(text) and text[cursor].isspace():
        if text[cursor] == "\n":
            newline_count += 1
        cursor += 1
    return newline_count >= 2
