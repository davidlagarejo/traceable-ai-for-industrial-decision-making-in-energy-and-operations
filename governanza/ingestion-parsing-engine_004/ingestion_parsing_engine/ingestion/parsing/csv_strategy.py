from __future__ import annotations

from collections.abc import Callable
import csv
from datetime import datetime, timezone
from io import StringIO

from ...domain.entities import ParsedFieldObject, ParsedTableObject
from ...domain.enums import (
    FailureSeverity,
    FailureStage,
    LocationKind,
    ParserStrategyType,
    ParsingStatus,
    PartialParseStatus,
    ReplayabilityStatus,
    SourceFormatFamily,
    WarningSeverity,
)
from ...domain.records import StructuralLocationRecord
from ...domain.value_objects import (
    CellCoordinates,
    ParsedFieldObjectId,
    ParsedTableObjectId,
    ParsingScopeRef,
    StructuralLocationRecordId,
    TableNumber,
    UriReference,
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


class CsvParserStrategy:
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
            parser_strategy_type=ParserStrategyType.CSV_TABULAR,
            strategy_name="csv-basic-strategy",
            strategy_version=self._strategy_version,
            applicable_formats=(SourceFormatFamily.CSV,),
            parameter_fingerprint_value="params:csv-basic:default",
            clock=self._clock,
        )
        if captured_raw_asset.raw_asset_version_record.detected_format.value != "csv":
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="parser.incompatible_format",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="CSV strategy can only parse raw assets detected as csv.",
                recoverable=False,
                clock=self._clock,
            )

        text = captured_raw_asset.decode_text()
        if not text.strip():
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="csv.empty_payload",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="CSV payload is empty.",
                recoverable=False,
                clock=self._clock,
            )

        rows = tuple(csv.reader(StringIO(text)))
        if not rows or not any(any(cell.strip() for cell in row) for row in rows):
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="csv.empty_payload",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.TABLE_PARSE,
                cause="CSV payload does not contain any non-empty rows.",
                recoverable=False,
                clock=self._clock,
            )

        first_row = tuple(cell.strip() for cell in rows[0])
        header_clear = bool(first_row) and all(first_row) and len(set(first_row)) == len(first_row)
        row_lengths = tuple(len(row) for row in rows if row)
        inconsistent_rows = len(set(row_lengths)) > 1
        parsing_status = (
            ParsingStatus.PARTIAL if inconsistent_rows else ParsingStatus.COMPLETE
        )
        partial_parse_status = (
            PartialParseStatus.PARTIAL_USEFUL
            if inconsistent_rows
            else PartialParseStatus.NOT_PARTIAL
        )
        heuristic_notes = (
            ("csv.inconsistent_row_lengths",) if inconsistent_rows else ()
        )
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
        table_location = StructuralLocationRecord(
            structural_location_record_id=StructuralLocationRecordId(
                _stable_id("location_csv_table", document.parsed_document_object_id.value)
            ),
            location_kind=LocationKind.URI_FRAGMENT,
            page_number=None,
            table_number=None,
            cell_coordinates=None,
            sheet_name=None,
            sheet_index=None,
            block_index=None,
            block_offsets=None,
            selector=None,
            endpoint_reference=None,
            payload_path=None,
            uri_fragment=UriReference("#csv-table-1"),
        )
        data_rows = rows[1:] if header_clear and len(rows) > 1 else rows
        header_labels = first_row if header_clear else ()
        table = ParsedTableObject(
            parsed_table_object_id=ParsedTableObjectId(
                _stable_id("parsed_table_csv", document.parsed_document_object_id.value)
            ),
            parsed_document_object_id=document.parsed_document_object_id,
            raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
            extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
            structural_location_record_id=table_location.structural_location_record_id,
            parsing_status=parsing_status,
            partial_parse_status=partial_parse_status,
            row_count=len(data_rows),
            column_count=max(row_lengths),
            header_labels=header_labels,
            created_at=self._clock(),
        )

        locations: list[StructuralLocationRecord] = [table_location]
        fields: list[ParsedFieldObject] = []
        warnings = []

        if not header_clear:
            warnings.append(
                build_warning_record(
                    scope_ref=ParsingScopeRef.for_parsed_table(table.parsed_table_object_id),
                    warning_code="csv.headers_ambiguous",
                    warning_severity=WarningSeverity.MODERATE,
                    message="CSV first row could not be treated as a clear header row.",
                    scope_marker=table.parsed_table_object_id.value,
                    clock=self._clock,
                )
            )

        if inconsistent_rows:
            warnings.append(
                build_warning_record(
                    scope_ref=ParsingScopeRef.for_parsed_table(table.parsed_table_object_id),
                    warning_code="csv.row_length_inconsistent",
                    warning_severity=WarningSeverity.HIGH,
                    message="CSV rows have inconsistent lengths; table was materialized as partial.",
                    scope_marker=table.parsed_table_object_id.value,
                    clock=self._clock,
                )
            )

        for row_index, row in enumerate(rows):
            for column_index, cell_value in enumerate(row):
                field_name = None
                if header_clear and row_index > 0 and column_index < len(header_labels):
                    field_name = header_labels[column_index]
                if field_name is None and cell_value == "":
                    continue
                location = StructuralLocationRecord(
                    structural_location_record_id=StructuralLocationRecordId(
                        _stable_id(
                            "location_csv_cell",
                            table.parsed_table_object_id.value,
                            str(row_index),
                            str(column_index),
                        )
                    ),
                    location_kind=LocationKind.TABLE_CELL,
                    page_number=None,
                    table_number=TableNumber(1),
                    cell_coordinates=CellCoordinates(row_index, column_index),
                    sheet_name=None,
                    sheet_index=None,
                    block_index=None,
                    block_offsets=None,
                    selector=None,
                    endpoint_reference=None,
                    payload_path=None,
                    uri_fragment=None,
                )
                locations.append(location)
                fields.append(
                    ParsedFieldObject(
                        parsed_field_object_id=ParsedFieldObjectId(
                            _stable_id(
                                "parsed_field_csv",
                                table.parsed_table_object_id.value,
                                str(row_index),
                                str(column_index),
                            )
                        ),
                        parsed_document_object_id=document.parsed_document_object_id,
                        raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
                        extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
                        structural_location_record_id=location.structural_location_record_id,
                        parent_table_object_id=table.parsed_table_object_id,
                        parent_block_object_id=None,
                        field_name=field_name,
                        raw_value=cell_value,
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
                parsed_table_objects=(table,),
                parsed_field_objects=tuple(fields),
            ),
            clock=self._clock,
        )
        return ParseExecutionResult(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            parsed_document_object=document,
            parsed_table_objects=(table,),
            parsed_field_objects=tuple(fields),
            parsed_block_objects=(),
            structural_location_records=tuple(locations),
            parsing_warning_records=tuple(warnings),
            parsing_failure_records=(),
            parsing_confidence_records=(),
            replay_manifest_record=replay_manifest,
        )
