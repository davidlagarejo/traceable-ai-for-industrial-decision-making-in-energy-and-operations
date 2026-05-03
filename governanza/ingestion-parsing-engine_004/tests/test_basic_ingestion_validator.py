from __future__ import annotations

from datetime import datetime, timezone
import unittest

from ingestion_parsing_engine.domain import (
    BlockOffsets,
    CellCoordinates,
    ConfidenceStatus,
    ConfidenceValue,
    ContentChecksum,
    ContentType,
    EndpointReference,
    ExtractionMetadataRecord,
    ExtractionMetadataRecordId,
    FailureCode,
    FailureSeverity,
    FailureStage,
    ImplementationFingerprint,
    IngestionRequestRecord,
    IngestionRequestRecordId,
    LocationKind,
    PageNumber,
    ParameterFingerprint,
    ParsedBlockObject,
    ParsedBlockObjectId,
    ParsedDocumentObject,
    ParsedDocumentObjectId,
    ParsedFieldObject,
    ParsedFieldObjectId,
    ParsedTableObject,
    ParsedTableObjectId,
    ParserStrategyRecord,
    ParserStrategyRecordId,
    ParserStrategyType,
    ParserStrategyVersion,
    ParsingConfidenceRecord,
    ParsingConfidenceRecordId,
    ParsingFailureRecord,
    ParsingFailureRecordId,
    ParsingScopeRef,
    ParsingStatus,
    ParsingWarningRecord,
    ParsingWarningRecordId,
    PartialParseStatus,
    PreservationPointer,
    RawAssetKind,
    RawAssetRecord,
    RawAssetRecordId,
    RawAssetVersionRecord,
    RawAssetVersionRecordId,
    ReplayManifestRecord,
    ReplayManifestRecordId,
    ReplayabilityStatus,
    RequestFingerprint,
    RetrievalRecord,
    RetrievalRecordId,
    RetrievalStatus,
    RightsRestrictionLevel,
    Selector,
    SourceAccessPolicyRef,
    SourceAdapterRef,
    SourceFormatFamily,
    SourceIdRef,
    StructuralLocationRecord,
    StructuralLocationRecordId,
    TableNumber,
    UriReference,
    WarningCode,
    WarningSeverity,
)
from ingestion_parsing_engine.validation import (
    BasicIngestionIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc


def _dt(day: int, hour: int = 12) -> datetime:
    return datetime(2026, 4, day, hour, 0, tzinfo=UTC)


def _request(
    request_id: str = "request:pdf:v1",
    *,
    raw_asset_kind: RawAssetKind = RawAssetKind.PDF_DOCUMENT,
    declared_format: SourceFormatFamily = SourceFormatFamily.PDF,
    fingerprint: str = "request-fingerprint:v1",
) -> IngestionRequestRecord:
    return IngestionRequestRecord(
        ingestion_request_record_id=IngestionRequestRecordId(request_id),
        source_id_ref=SourceIdRef("source:benchmarking"),
        source_access_policy_ref=SourceAccessPolicyRef("policy:public"),
        raw_asset_kind=raw_asset_kind,
        declared_format=declared_format,
        rights_restriction_level=RightsRestrictionLevel.PUBLIC,
        request_fingerprint=RequestFingerprint(fingerprint),
        original_uri=UriReference("https://example.com/benchmark.pdf"),
        endpoint_reference=None,
        requested_at=_dt(1),
    )


def _raw_asset(
    raw_asset_id: str = "raw:benchmarking",
    *,
    request: IngestionRequestRecord | None = None,
) -> RawAssetRecord:
    request = request or _request()
    return RawAssetRecord(
        raw_asset_record_id=RawAssetRecordId(raw_asset_id),
        source_id_ref=request.source_id_ref,
        source_access_policy_ref=request.source_access_policy_ref,
        raw_asset_kind=request.raw_asset_kind,
        declared_format=request.declared_format,
        rights_restriction_level=request.rights_restriction_level,
        original_uri=request.original_uri,
        endpoint_reference=request.endpoint_reference,
        created_at=_dt(1, 13),
    )


def _retrieval(
    retrieval_id: str = "retrieval:benchmarking:v1",
    *,
    request: IngestionRequestRecord | None = None,
    raw_asset: RawAssetRecord | None = None,
    retrieval_status: RetrievalStatus = RetrievalStatus.SUCCEEDED,
) -> RetrievalRecord:
    request = request or _request()
    raw_asset = raw_asset or _raw_asset(request=request)
    return RetrievalRecord(
        retrieval_record_id=RetrievalRecordId(retrieval_id),
        ingestion_request_record_id=request.ingestion_request_record_id,
        raw_asset_record_id=raw_asset.raw_asset_record_id,
        source_adapter_ref=SourceAdapterRef("adapter:http-download"),
        retrieval_status=retrieval_status,
        request_fingerprint=request.request_fingerprint,
        response_status_code=200,
        retrieval_started_at=_dt(1, 14),
        retrieval_completed_at=_dt(1, 15),
    )


def _raw_asset_version(
    version_id: str = "raw-version:benchmarking:v1",
    *,
    raw_asset: RawAssetRecord | None = None,
    retrieval: RetrievalRecord | None = None,
    detected_format: SourceFormatFamily = SourceFormatFamily.PDF,
    checksum: str = "sha256:raw-v1",
) -> RawAssetVersionRecord:
    raw_asset = raw_asset or _raw_asset()
    retrieval = retrieval or _retrieval(raw_asset=raw_asset)
    return RawAssetVersionRecord(
        raw_asset_version_record_id=RawAssetVersionRecordId(version_id),
        raw_asset_record_id=raw_asset.raw_asset_record_id,
        retrieval_record_id=retrieval.retrieval_record_id,
        content_checksum=ContentChecksum(checksum),
        content_type=ContentType("application/pdf"),
        content_length=1024,
        detected_format=detected_format,
        source_visible_version=None,
        raw_preservation_pointer=PreservationPointer("/raw/benchmarking/v1.pdf"),
        charset=None,
        captured_at=_dt(1, 16),
    )


def _strategy(
    strategy_id: str = "parser:pdf-table:v1",
    *,
    strategy_type: ParserStrategyType = ParserStrategyType.PDF_TABLE,
    applicable_formats: tuple[SourceFormatFamily, ...] = (SourceFormatFamily.PDF,),
) -> ParserStrategyRecord:
    return ParserStrategyRecord(
        parser_strategy_record_id=ParserStrategyRecordId(strategy_id),
        parser_strategy_type=strategy_type,
        strategy_name="pdf-table-baseline",
        parser_strategy_version=ParserStrategyVersion("1.0.0"),
        implementation_fingerprint=ImplementationFingerprint("impl:pdf-table:1.0.0"),
        parameter_fingerprint=ParameterFingerprint("params:default"),
        applicable_formats=applicable_formats,
        created_at=_dt(2),
    )


def _extraction(
    extraction_id: str = "extraction:v1",
    *,
    raw_asset_version: RawAssetVersionRecord | None = None,
    strategy: ParserStrategyRecord | None = None,
    parsing_status: ParsingStatus = ParsingStatus.COMPLETE,
    partial_parse_status: PartialParseStatus = PartialParseStatus.NOT_PARTIAL,
) -> ExtractionMetadataRecord:
    raw_asset_version = raw_asset_version or _raw_asset_version()
    strategy = strategy or _strategy()
    return ExtractionMetadataRecord(
        extraction_metadata_record_id=ExtractionMetadataRecordId(extraction_id),
        raw_asset_version_record_id=raw_asset_version.raw_asset_version_record_id,
        parser_strategy_record_id=strategy.parser_strategy_record_id,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
        extraction_started_at=_dt(2, 13),
        extraction_completed_at=_dt(2, 14),
        heuristic_notes=(),
    )


def _document(
    document_id: str = "document:v1",
    *,
    raw_asset_version: RawAssetVersionRecord | None = None,
    strategy: ParserStrategyRecord | None = None,
    extraction: ExtractionMetadataRecord | None = None,
    parsing_status: ParsingStatus = ParsingStatus.COMPLETE,
    partial_parse_status: PartialParseStatus = PartialParseStatus.NOT_PARTIAL,
) -> ParsedDocumentObject:
    raw_asset_version = raw_asset_version or _raw_asset_version()
    strategy = strategy or _strategy()
    extraction = extraction or _extraction(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    return ParsedDocumentObject(
        parsed_document_object_id=ParsedDocumentObjectId(document_id),
        raw_asset_version_record_id=raw_asset_version.raw_asset_version_record_id,
        parser_strategy_record_id=strategy.parser_strategy_record_id,
        extraction_metadata_record_id=extraction.extraction_metadata_record_id,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
        document_title="Industrial Energy Benchmarking 2026",
        created_at=_dt(2, 15),
    )


def _location(
    location_id: str = "location:table:v1",
    *,
    location_kind: LocationKind = LocationKind.PDF_TABLE,
    page_number: PageNumber | None = None,
    table_number: TableNumber | None = None,
    selector: Selector | None = None,
) -> StructuralLocationRecord:
    resolved_page_number = page_number or PageNumber(4)
    resolved_table_number = table_number
    if resolved_table_number is None and location_kind in {LocationKind.PDF_TABLE, LocationKind.TABLE_CELL}:
        resolved_table_number = TableNumber(1)
    return StructuralLocationRecord(
        structural_location_record_id=StructuralLocationRecordId(location_id),
        location_kind=location_kind,
        page_number=resolved_page_number,
        table_number=resolved_table_number,
        cell_coordinates=None,
        sheet_name=None,
        sheet_index=None,
        block_index=None,
        block_offsets=None,
        selector=selector,
        endpoint_reference=None,
        payload_path=None,
        uri_fragment=None,
    )


def _table(
    table_id: str = "table:v1",
    *,
    document: ParsedDocumentObject | None = None,
    raw_asset_version: RawAssetVersionRecord | None = None,
    extraction: ExtractionMetadataRecord | None = None,
    location: StructuralLocationRecord | None = None,
    parsing_status: ParsingStatus = ParsingStatus.COMPLETE,
    partial_parse_status: PartialParseStatus = PartialParseStatus.NOT_PARTIAL,
) -> ParsedTableObject:
    raw_asset_version = raw_asset_version or _raw_asset_version()
    strategy = _strategy()
    extraction = extraction or _extraction(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    document = document or _document(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        extraction=extraction,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    location = location or _location()
    return ParsedTableObject(
        parsed_table_object_id=ParsedTableObjectId(table_id),
        parsed_document_object_id=document.parsed_document_object_id,
        raw_asset_version_record_id=raw_asset_version.raw_asset_version_record_id,
        extraction_metadata_record_id=extraction.extraction_metadata_record_id,
        structural_location_record_id=location.structural_location_record_id,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
        row_count=12,
        column_count=4,
        header_labels=("metric", "value", "unit", "source_note"),
        created_at=_dt(2, 16),
    )


def _block(
    block_id: str = "block:v1",
    *,
    document: ParsedDocumentObject | None = None,
    raw_asset_version: RawAssetVersionRecord | None = None,
    extraction: ExtractionMetadataRecord | None = None,
    location: StructuralLocationRecord | None = None,
    parent_table: ParsedTableObject | None = None,
    parsing_status: ParsingStatus = ParsingStatus.COMPLETE,
    partial_parse_status: PartialParseStatus = PartialParseStatus.NOT_PARTIAL,
) -> ParsedBlockObject:
    raw_asset_version = raw_asset_version or _raw_asset_version()
    strategy = _strategy()
    extraction = extraction or _extraction(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    document = document or _document(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        extraction=extraction,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    location = location or StructuralLocationRecord(
        structural_location_record_id=StructuralLocationRecordId("location:block:v1"),
        location_kind=LocationKind.TEXT_BLOCK,
        page_number=PageNumber(5),
        table_number=None,
        cell_coordinates=None,
        sheet_name=None,
        sheet_index=None,
        block_index=1,
        block_offsets=BlockOffsets(120, 240),
        selector=None,
        endpoint_reference=None,
        payload_path=None,
        uri_fragment=None,
    )
    return ParsedBlockObject(
        parsed_block_object_id=ParsedBlockObjectId(block_id),
        parsed_document_object_id=document.parsed_document_object_id,
        raw_asset_version_record_id=raw_asset_version.raw_asset_version_record_id,
        extraction_metadata_record_id=extraction.extraction_metadata_record_id,
        structural_location_record_id=location.structural_location_record_id,
        parent_table_object_id=None if parent_table is None else parent_table.parsed_table_object_id,
        raw_text="Boiler efficiency improved after retrofit.",
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
        created_at=_dt(2, 17),
    )


def _field(
    field_id: str = "field:v1",
    *,
    document: ParsedDocumentObject | None = None,
    raw_asset_version: RawAssetVersionRecord | None = None,
    extraction: ExtractionMetadataRecord | None = None,
    location: StructuralLocationRecord | None = None,
    parent_table: ParsedTableObject | None = None,
    parent_block: ParsedBlockObject | None = None,
    parsing_status: ParsingStatus = ParsingStatus.COMPLETE,
    partial_parse_status: PartialParseStatus = PartialParseStatus.NOT_PARTIAL,
) -> ParsedFieldObject:
    raw_asset_version = raw_asset_version or _raw_asset_version()
    strategy = _strategy()
    extraction = extraction or _extraction(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    document = document or _document(
        raw_asset_version=raw_asset_version,
        strategy=strategy,
        extraction=extraction,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
    )
    location = location or StructuralLocationRecord(
        structural_location_record_id=StructuralLocationRecordId("location:field:v1"),
        location_kind=LocationKind.TABLE_CELL,
        page_number=PageNumber(4),
        table_number=TableNumber(1),
        cell_coordinates=CellCoordinates(0, 1),
        sheet_name=None,
        sheet_index=None,
        block_index=None,
        block_offsets=None,
        selector=None,
        endpoint_reference=None,
        payload_path=None,
        uri_fragment=None,
    )
    return ParsedFieldObject(
        parsed_field_object_id=ParsedFieldObjectId(field_id),
        parsed_document_object_id=document.parsed_document_object_id,
        raw_asset_version_record_id=raw_asset_version.raw_asset_version_record_id,
        extraction_metadata_record_id=extraction.extraction_metadata_record_id,
        structural_location_record_id=location.structural_location_record_id,
        parent_table_object_id=None if parent_table is None else parent_table.parsed_table_object_id,
        parent_block_object_id=None if parent_block is None else parent_block.parsed_block_object_id,
        field_name="efficiency",
        raw_value="84.2",
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
        created_at=_dt(2, 18),
    )


def _warning(scope_ref: ParsingScopeRef) -> ParsingWarningRecord:
    return ParsingWarningRecord(
        parsing_warning_record_id=ParsingWarningRecordId("warning:v1"),
        scope_ref=scope_ref,
        warning_code=WarningCode("table.truncated"),
        warning_severity=WarningSeverity.HIGH,
        message="Table extraction was truncated after merged footer rows.",
        created_at=_dt(2, 19),
    )


def _failure(scope_ref: ParsingScopeRef) -> ParsingFailureRecord:
    return ParsingFailureRecord(
        parsing_failure_record_id=ParsingFailureRecordId("failure:v1"),
        scope_ref=scope_ref,
        failure_code=FailureCode("table.footer_ambiguity"),
        failure_severity=FailureSeverity.RECOVERABLE,
        failure_stage=FailureStage.TABLE_PARSE,
        cause="Footer rows could not be assigned to a stable schema.",
        recoverable=True,
        created_at=_dt(2, 20),
    )


def _confidence(scope_ref: ParsingScopeRef) -> ParsingConfidenceRecord:
    return ParsingConfidenceRecord(
        parsing_confidence_record_id=ParsingConfidenceRecordId("confidence:v1"),
        scope_ref=scope_ref,
        confidence_status=ConfidenceStatus.HEURISTIC,
        confidence_value=ConfidenceValue(0.62),
        confidence_method="layout_heuristic",
        created_at=_dt(2, 21),
    )


def _replay_manifest(
    *,
    raw_asset_version: RawAssetVersionRecord,
    strategy: ParserStrategyRecord,
    extraction: ExtractionMetadataRecord,
    expected_output_refs: tuple[ParsingScopeRef, ...],
    replayability_status: ReplayabilityStatus = ReplayabilityStatus.REPLAYABLE,
) -> ReplayManifestRecord:
    return ReplayManifestRecord(
        replay_manifest_record_id=ReplayManifestRecordId("replay:v1"),
        raw_asset_version_record_id=raw_asset_version.raw_asset_version_record_id,
        parser_strategy_record_id=strategy.parser_strategy_record_id,
        extraction_metadata_record_id=extraction.extraction_metadata_record_id,
        replayability_status=replayability_status,
        raw_content_checksum=raw_asset_version.content_checksum,
        parameter_fingerprint=strategy.parameter_fingerprint,
        expected_output_refs=expected_output_refs,
        created_at=_dt(2, 22),
    )


class BasicIngestionIntegrityValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicIngestionIntegrityValidator(
            clock=lambda: datetime(2026, 4, 10, 15, 0, tzinfo=UTC)
        )

    def test_valid_graph_passes(self) -> None:
        request = _request()
        raw_asset = _raw_asset(request=request)
        retrieval = _retrieval(request=request, raw_asset=raw_asset)
        raw_asset_version = _raw_asset_version(raw_asset=raw_asset, retrieval=retrieval)
        strategy = _strategy()
        extraction = _extraction(raw_asset_version=raw_asset_version, strategy=strategy)
        document = _document(
            raw_asset_version=raw_asset_version,
            strategy=strategy,
            extraction=extraction,
        )
        location = _location()
        table = _table(
            document=document,
            raw_asset_version=raw_asset_version,
            extraction=extraction,
            location=location,
        )
        replay = _replay_manifest(
            raw_asset_version=raw_asset_version,
            strategy=strategy,
            extraction=extraction,
            expected_output_refs=(
                ParsingScopeRef.for_parsed_document(document.parsed_document_object_id),
                ParsingScopeRef.for_parsed_table(table.parsed_table_object_id),
            ),
        )

        report = self.validator.validate_graph(
            ingestion_request_records=(request,),
            retrieval_records=(retrieval,),
            raw_asset_records=(raw_asset,),
            raw_asset_version_records=(raw_asset_version,),
            parsed_document_objects=(document,),
            parsed_table_objects=(table,),
            structural_location_records=(location,),
            extraction_metadata_records=(extraction,),
            parser_strategy_records=(strategy,),
            replay_manifest_records=(replay,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertEqual(report.violations, ())

    def test_partial_but_coherent_graph_passes_with_warnings(self) -> None:
        request = _request()
        raw_asset = _raw_asset(request=request)
        retrieval = _retrieval(
            request=request,
            raw_asset=raw_asset,
            retrieval_status=RetrievalStatus.PARTIAL,
        )
        raw_asset_version = _raw_asset_version(raw_asset=raw_asset, retrieval=retrieval)
        strategy = _strategy()
        extraction = _extraction(
            raw_asset_version=raw_asset_version,
            strategy=strategy,
            parsing_status=ParsingStatus.PARTIAL,
            partial_parse_status=PartialParseStatus.PARTIAL_USEFUL,
        )
        document = _document(
            raw_asset_version=raw_asset_version,
            strategy=strategy,
            extraction=extraction,
            parsing_status=ParsingStatus.PARTIAL,
            partial_parse_status=PartialParseStatus.PARTIAL_USEFUL,
        )
        location = _location()
        table = _table(
            document=document,
            raw_asset_version=raw_asset_version,
            extraction=extraction,
            location=location,
            parsing_status=ParsingStatus.PARTIAL,
            partial_parse_status=PartialParseStatus.PARTIAL_USEFUL,
        )
        warning = _warning(ParsingScopeRef.for_parsed_table(table.parsed_table_object_id))
        failure = _failure(ParsingScopeRef.for_parsed_table(table.parsed_table_object_id))
        confidence = _confidence(ParsingScopeRef.for_parsed_table(table.parsed_table_object_id))
        replay = _replay_manifest(
            raw_asset_version=raw_asset_version,
            strategy=strategy,
            extraction=extraction,
            expected_output_refs=(
                ParsingScopeRef.for_parsed_document(document.parsed_document_object_id),
                ParsingScopeRef.for_parsed_table(table.parsed_table_object_id),
            ),
            replayability_status=ReplayabilityStatus.PARTIALLY_REPLAYABLE,
        )

        report = self.validator.validate_graph(
            ingestion_request_records=(request,),
            retrieval_records=(retrieval,),
            raw_asset_records=(raw_asset,),
            raw_asset_version_records=(raw_asset_version,),
            parsed_document_objects=(document,),
            parsed_table_objects=(table,),
            structural_location_records=(location,),
            extraction_metadata_records=(extraction,),
            parsing_warning_records=(warning,),
            parsing_failure_records=(failure,),
            parsing_confidence_records=(confidence,),
            parser_strategy_records=(strategy,),
            replay_manifest_records=(replay,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        self.assertTrue(report.has_warnings)
        self.assertFalse(report.has_errors)

    def test_retrieval_with_unresolved_request_fails(self) -> None:
        request = _request()
        raw_asset = _raw_asset(request=request)
        retrieval = _retrieval(request=request, raw_asset=raw_asset)

        report = self.validator.validate_graph(
            retrieval_records=(retrieval,),
            raw_asset_records=(raw_asset,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "retrieval.request_reference_invalid" for item in report.violations))

    def test_raw_asset_version_linked_to_failed_retrieval_fails(self) -> None:
        request = _request()
        raw_asset = _raw_asset(request=request)
        retrieval = _retrieval(
            request=request,
            raw_asset=raw_asset,
            retrieval_status=RetrievalStatus.FAILED,
        )
        raw_asset_version = _raw_asset_version(raw_asset=raw_asset, retrieval=retrieval)

        report = self.validator.validate_graph(
            ingestion_request_records=(request,),
            retrieval_records=(retrieval,),
            raw_asset_records=(raw_asset,),
            raw_asset_version_records=(raw_asset_version,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "raw_version.capture_from_failed_retrieval" for item in report.violations))

    def test_document_metadata_mismatch_fails(self) -> None:
        request = _request()
        raw_asset = _raw_asset(request=request)
        retrieval = _retrieval(request=request, raw_asset=raw_asset)
        raw_asset_version = _raw_asset_version(raw_asset=raw_asset, retrieval=retrieval)
        strategy = _strategy()
        extraction = _extraction(raw_asset_version=raw_asset_version, strategy=strategy)
        other_strategy = _strategy(strategy_id="parser:pdf-text:v1", strategy_type=ParserStrategyType.PDF_TEXT)
        document = _document(
            raw_asset_version=raw_asset_version,
            strategy=other_strategy,
            extraction=extraction,
        )

        report = self.validator.validate_graph(
            ingestion_request_records=(request,),
            retrieval_records=(retrieval,),
            raw_asset_records=(raw_asset,),
            raw_asset_version_records=(raw_asset_version,),
            parsed_document_objects=(document,),
            extraction_metadata_records=(extraction,),
            parser_strategy_records=(strategy, other_strategy),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "document.metadata_mismatch" for item in report.violations))

    def test_table_with_unresolved_location_fails(self) -> None:
        raw_asset_version = _raw_asset_version()
        strategy = _strategy()
        extraction = _extraction(raw_asset_version=raw_asset_version, strategy=strategy)
        document = _document(raw_asset_version=raw_asset_version, strategy=strategy, extraction=extraction)
        location = _location()
        table = _table(
            document=document,
            raw_asset_version=raw_asset_version,
            extraction=extraction,
            location=location,
        )

        report = self.validator.validate_graph(
            raw_asset_version_records=(raw_asset_version,),
            parsed_document_objects=(document,),
            parsed_table_objects=(table,),
            extraction_metadata_records=(extraction,),
            parser_strategy_records=(strategy,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "table.location_reference_invalid" for item in report.violations))

    def test_field_with_broken_parent_provenance_fails(self) -> None:
        request = _request()
        raw_asset = _raw_asset(request=request)
        retrieval = _retrieval(request=request, raw_asset=raw_asset)
        raw_asset_version = _raw_asset_version(raw_asset=raw_asset, retrieval=retrieval)
        strategy = _strategy()
        extraction = _extraction(raw_asset_version=raw_asset_version, strategy=strategy)
        document = _document(raw_asset_version=raw_asset_version, strategy=strategy, extraction=extraction)
        location = _location()
        table = _table(document=document, raw_asset_version=raw_asset_version, extraction=extraction, location=location)

        other_request = _request(request_id="request:pdf:v2", fingerprint="request-fingerprint:v2")
        other_raw_asset = _raw_asset(raw_asset_id="raw:other", request=other_request)
        other_retrieval = _retrieval(
            retrieval_id="retrieval:other:v1",
            request=other_request,
            raw_asset=other_raw_asset,
        )
        other_raw_asset_version = _raw_asset_version(
            version_id="raw-version:other:v1",
            raw_asset=other_raw_asset,
            retrieval=other_retrieval,
            checksum="sha256:raw-other",
        )
        other_extraction = _extraction(
            extraction_id="extraction:other:v1",
            raw_asset_version=other_raw_asset_version,
            strategy=strategy,
        )
        other_document = _document(
            document_id="document:other:v1",
            raw_asset_version=other_raw_asset_version,
            strategy=strategy,
            extraction=other_extraction,
        )
        other_location = StructuralLocationRecord(
            structural_location_record_id=StructuralLocationRecordId("location:field:other"),
            location_kind=LocationKind.TABLE_CELL,
            page_number=PageNumber(8),
            table_number=TableNumber(2),
            cell_coordinates=CellCoordinates(1, 2),
            sheet_name=None,
            sheet_index=None,
            block_index=None,
            block_offsets=None,
            selector=None,
            endpoint_reference=None,
            payload_path=None,
            uri_fragment=None,
        )
        field = _field(
            document=other_document,
            raw_asset_version=other_raw_asset_version,
            extraction=other_extraction,
            location=other_location,
            parent_table=table,
        )

        report = self.validator.validate_graph(
            ingestion_request_records=(request, other_request),
            retrieval_records=(retrieval, other_retrieval),
            raw_asset_records=(raw_asset, other_raw_asset),
            raw_asset_version_records=(raw_asset_version, other_raw_asset_version),
            parsed_document_objects=(document, other_document),
            parsed_table_objects=(table,),
            parsed_field_objects=(field,),
            structural_location_records=(location, other_location),
            extraction_metadata_records=(extraction, other_extraction),
            parser_strategy_records=(strategy,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "field.parent_provenance_mismatch" for item in report.violations))

    def test_location_with_incompatible_fields_fails(self) -> None:
        location = _location(
            location_id="location:invalid",
            location_kind=LocationKind.PDF_PAGE,
            page_number=PageNumber(2),
            table_number=None,
            selector=Selector("table.benchmark"),
        )

        report = self.validator.validate_structural_location_record(location)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "location.field_combination_invalid" for item in report.violations))

    def test_strategy_with_incompatible_format_scope_fails(self) -> None:
        strategy = _strategy(
            strategy_id="parser:bad:v1",
            strategy_type=ParserStrategyType.PDF_TABLE,
            applicable_formats=(SourceFormatFamily.CSV,),
        )

        report = self.validator.validate_parser_strategy_record(strategy)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "strategy.format_scope_incoherent" for item in report.violations))

    def test_replay_manifest_with_unresolved_output_fails(self) -> None:
        raw_asset_version = _raw_asset_version()
        strategy = _strategy()
        extraction = _extraction(raw_asset_version=raw_asset_version, strategy=strategy)
        manifest = _replay_manifest(
            raw_asset_version=raw_asset_version,
            strategy=strategy,
            extraction=extraction,
            expected_output_refs=(ParsingScopeRef.for_parsed_document(ParsedDocumentObjectId("document:missing")),),
        )

        report = self.validator.validate_graph(
            raw_asset_version_records=(raw_asset_version,),
            extraction_metadata_records=(extraction,),
            parser_strategy_records=(strategy,),
            replay_manifest_records=(manifest,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "replay.output_reference_invalid" for item in report.violations))


if __name__ == "__main__":
    unittest.main()
