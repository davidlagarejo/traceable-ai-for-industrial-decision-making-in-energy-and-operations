from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from html.parser import HTMLParser

from ...domain.entities import ParsedBlockObject, ParsedFieldObject, ParsedTableObject
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
    ParsedBlockObjectId,
    ParsedFieldObjectId,
    ParsedTableObjectId,
    ParsingScopeRef,
    Selector,
    StructuralLocationRecordId,
)
from .results import (
    ParseExecutionResult,
    build_extraction_metadata_record,
    build_heuristic_confidence_record,
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


class HtmlParserStrategy:
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
            parser_strategy_type=ParserStrategyType.HTML_DOM,
            strategy_name="html-basic-strategy",
            strategy_version=self._strategy_version,
            applicable_formats=(SourceFormatFamily.HTML,),
            parameter_fingerprint_value="params:html-basic:default",
            clock=self._clock,
        )
        if captured_raw_asset.raw_asset_version_record.detected_format.value != "html":
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="parser.incompatible_format",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="HTML strategy can only parse raw assets detected as html.",
                recoverable=False,
                clock=self._clock,
            )

        text = captured_raw_asset.decode_text()
        if not text.strip():
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=(),
                failure_code="html.empty_payload",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause="HTML payload is empty.",
                recoverable=False,
                clock=self._clock,
            )

        collector = _SimpleHtmlCollector()
        collector.feed(text)
        collector.close()
        if not collector.text_blocks and not collector.tables:
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=("html.no_extractable_structure",),
                failure_code="html.no_extractable_structure",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.BLOCK_PARSE,
                cause="HTML payload did not expose text blocks or simple tables.",
                recoverable=False,
                clock=self._clock,
            )

        partial_tables = [table for table in collector.tables if table.is_partial]
        parsing_status = ParsingStatus.PARTIAL if partial_tables else ParsingStatus.COMPLETE
        partial_parse_status = (
            PartialParseStatus.PARTIAL_USEFUL if partial_tables else PartialParseStatus.NOT_PARTIAL
        )
        heuristic_notes = ("html.partial_table_extraction",) if partial_tables else ()
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
            document_title=collector.title,
            clock=self._clock,
        )

        warnings = []
        confidence_records = []
        if partial_tables:
            warnings.append(
                build_warning_record(
                    scope_ref=ParsingScopeRef.for_parsed_document(document.parsed_document_object_id),
                    warning_code="html.table_partial",
                    warning_severity=WarningSeverity.HIGH,
                    message="HTML table extraction was partial due to inconsistent row structures.",
                    scope_marker=document.parsed_document_object_id.value,
                    clock=self._clock,
                )
            )
            confidence_records.append(
                build_heuristic_confidence_record(
                    scope_ref=ParsingScopeRef.for_parsed_document(document.parsed_document_object_id),
                    confidence_value=0.55,
                    confidence_method="html_partial_table_heuristic",
                    scope_marker=document.parsed_document_object_id.value,
                    clock=self._clock,
                )
            )

        locations: list[StructuralLocationRecord] = []
        blocks: list[ParsedBlockObject] = []
        for index, block in enumerate(collector.text_blocks, start=1):
            location = StructuralLocationRecord(
                structural_location_record_id=StructuralLocationRecordId(
                    _stable_id("location_html_block", document.parsed_document_object_id.value, str(index))
                ),
                location_kind=LocationKind.HTML_SELECTOR,
                page_number=None,
                table_number=None,
                cell_coordinates=None,
                sheet_name=None,
                sheet_index=None,
                block_index=None,
                block_offsets=None,
                selector=Selector(block.selector),
                endpoint_reference=None,
                payload_path=None,
                uri_fragment=None,
            )
            locations.append(location)
            blocks.append(
                ParsedBlockObject(
                    parsed_block_object_id=ParsedBlockObjectId(
                        _stable_id("parsed_block_html", document.parsed_document_object_id.value, str(index))
                    ),
                    parsed_document_object_id=document.parsed_document_object_id,
                    raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
                    extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
                    structural_location_record_id=location.structural_location_record_id,
                    parent_table_object_id=None,
                    raw_text=block.text,
                    parsing_status=parsing_status,
                    partial_parse_status=partial_parse_status,
                    created_at=self._clock(),
                )
            )

        tables: list[ParsedTableObject] = []
        fields: list[ParsedFieldObject] = []
        for table in collector.tables:
            table_location = StructuralLocationRecord(
                structural_location_record_id=StructuralLocationRecordId(
                    _stable_id(
                        "location_html_table",
                        document.parsed_document_object_id.value,
                        str(table.table_index),
                    )
                ),
                location_kind=LocationKind.HTML_SELECTOR,
                page_number=None,
                table_number=None,
                cell_coordinates=None,
                sheet_name=None,
                sheet_index=None,
                block_index=None,
                block_offsets=None,
                selector=Selector(table.selector),
                endpoint_reference=None,
                payload_path=None,
                uri_fragment=None,
            )
            locations.append(table_location)
            parsed_table = ParsedTableObject(
                parsed_table_object_id=ParsedTableObjectId(
                    _stable_id(
                        "parsed_table_html",
                        document.parsed_document_object_id.value,
                        str(table.table_index),
                    )
                ),
                parsed_document_object_id=document.parsed_document_object_id,
                raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
                extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
                structural_location_record_id=table_location.structural_location_record_id,
                parsing_status=(
                    ParsingStatus.PARTIAL if table.is_partial else ParsingStatus.COMPLETE
                ),
                partial_parse_status=(
                    PartialParseStatus.PARTIAL_USEFUL
                    if table.is_partial
                    else PartialParseStatus.NOT_PARTIAL
                ),
                row_count=max(len(table.rows) - 1, 0) if table.header_labels else len(table.rows),
                column_count=table.column_count,
                header_labels=table.header_labels,
                created_at=self._clock(),
            )
            tables.append(parsed_table)

            for row_index, row in enumerate(table.rows):
                for column_index, cell_value in enumerate(row):
                    cell_selector = (
                        f"{table.selector} > tr:nth-of-type({row_index + 1}) > "
                        f"cell:nth-of-type({column_index + 1})"
                    )
                    location = StructuralLocationRecord(
                        structural_location_record_id=StructuralLocationRecordId(
                            _stable_id(
                                "location_html_cell",
                                parsed_table.parsed_table_object_id.value,
                                str(row_index),
                                str(column_index),
                            )
                        ),
                        location_kind=LocationKind.HTML_SELECTOR,
                        page_number=None,
                        table_number=None,
                        cell_coordinates=None,
                        sheet_name=None,
                        sheet_index=None,
                        block_index=None,
                        block_offsets=None,
                        selector=Selector(cell_selector),
                        endpoint_reference=None,
                        payload_path=None,
                        uri_fragment=None,
                    )
                    locations.append(location)
                    field_name = None
                    if parsed_table.header_labels and row_index > 0 and column_index < len(parsed_table.header_labels):
                        field_name = parsed_table.header_labels[column_index]
                    fields.append(
                        ParsedFieldObject(
                            parsed_field_object_id=ParsedFieldObjectId(
                                _stable_id(
                                    "parsed_field_html",
                                    parsed_table.parsed_table_object_id.value,
                                    str(row_index),
                                    str(column_index),
                                )
                            ),
                            parsed_document_object_id=document.parsed_document_object_id,
                            raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
                            extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
                            structural_location_record_id=location.structural_location_record_id,
                            parent_table_object_id=parsed_table.parsed_table_object_id,
                            parent_block_object_id=None,
                            field_name=field_name,
                            raw_value=cell_value,
                            parsing_status=parsed_table.parsing_status,
                            partial_parse_status=parsed_table.partial_parse_status,
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
                parsed_table_objects=tuple(tables),
                parsed_field_objects=tuple(fields),
                parsed_block_objects=tuple(blocks),
            ),
            clock=self._clock,
        )
        return ParseExecutionResult(
            captured_raw_asset=captured_raw_asset,
            parser_strategy_record=strategy_record,
            extraction_metadata_record=extraction_metadata_record,
            parsed_document_object=document,
            parsed_table_objects=tuple(tables),
            parsed_field_objects=tuple(fields),
            parsed_block_objects=tuple(blocks),
            structural_location_records=tuple(locations),
            parsing_warning_records=tuple(warnings),
            parsing_failure_records=(),
            parsing_confidence_records=tuple(confidence_records),
            replay_manifest_record=replay_manifest,
        )


class _HtmlTextBlock:
    def __init__(self, text: str, selector: str) -> None:
        self.text = text
        self.selector = selector


class _HtmlTable:
    def __init__(self, table_index: int, rows: tuple[tuple[str, ...], ...]) -> None:
        self.table_index = table_index
        self.rows = rows
        self.selector = f"table:nth-of-type({table_index})"
        self.column_count = max((len(row) for row in rows), default=0)
        header = rows[0] if rows else ()
        if header and all(cell for cell in header) and len(set(header)) == len(header):
            self.header_labels = header
        else:
            self.header_labels = ()
        self.is_partial = len({len(row) for row in rows if row}) > 1


class _SimpleHtmlCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.text_blocks: list[_HtmlTextBlock] = []
        self.tables: list[_HtmlTable] = []
        self._tag_stack: list[str] = []
        self._table_index = 0
        self._inside_table = False
        self._current_rows: list[tuple[str, ...]] = []
        self._current_row: list[str] = []
        self._current_cell_parts: list[str] = []
        self._current_cell_tag: str | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        self._tag_stack.append(tag)
        if tag == "table":
            self._inside_table = True
            self._table_index += 1
            self._current_rows = []
        elif self._inside_table and tag == "tr":
            self._current_row = []
        elif self._inside_table and tag in {"th", "td"}:
            self._current_cell_tag = tag
            self._current_cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._inside_table and tag in {"th", "td"} and self._current_cell_tag == tag:
            value = " ".join(self._current_cell_parts).strip()
            self._current_row.append(value)
            self._current_cell_tag = None
            self._current_cell_parts = []
        elif self._inside_table and tag == "tr":
            if self._current_row:
                self._current_rows.append(tuple(self._current_row))
            self._current_row = []
        elif tag == "table" and self._inside_table:
            self.tables.append(_HtmlTable(self._table_index, tuple(self._current_rows)))
            self._inside_table = False
            self._current_rows = []

        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        normalized = " ".join(data.split())
        if not normalized:
            return
        if "title" in self._tag_stack and self.title is None:
            self.title = normalized[:120]
        if self._inside_table and self._current_cell_tag is not None:
            self._current_cell_parts.append(normalized)
            return
        selector = " > ".join(self._tag_stack) if self._tag_stack else "document"
        self.text_blocks.append(_HtmlTextBlock(normalized, selector))
