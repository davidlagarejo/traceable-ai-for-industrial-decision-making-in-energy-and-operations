from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from ..._compat import dataclass
from ...domain.entities import (
    ParsedBlockObject,
    ParsedDocumentObject,
    ParsedFieldObject,
    ParsedTableObject,
    ParserStrategyRecord,
)
from ...domain.enums import (
    FailureSeverity,
    FailureStage,
    ParserStrategyType,
    ParsingStatus,
    PartialParseStatus,
    ReplayabilityStatus,
    SourceFormatFamily,
    WarningSeverity,
)
from ...domain.errors import DomainInvariantError
from ...domain.records import (
    ExtractionMetadataRecord,
    ParsingConfidenceRecord,
    ParsingFailureRecord,
    ParsingWarningRecord,
    ReplayManifestRecord,
    StructuralLocationRecord,
)
from ...domain.value_objects import (
    ConfidenceValue,
    ExtractionMetadataRecordId,
    FailureCode,
    ImplementationFingerprint,
    ParsedBlockObjectId,
    ParsedDocumentObjectId,
    ParsedFieldObjectId,
    ParsedTableObjectId,
    ParserStrategyRecordId,
    ParserStrategyVersion,
    ParsingConfidenceRecordId,
    ParsingFailureRecordId,
    ParsingScopeRef,
    ParsingWarningRecordId,
    ParameterFingerprint,
    ReplayManifestRecordId,
    WarningCode,
)
from ..adapters import CapturedRawAsset


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def default_clock() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class ParseExecutionResult:
    captured_raw_asset: CapturedRawAsset
    parser_strategy_record: ParserStrategyRecord
    extraction_metadata_record: ExtractionMetadataRecord
    parsed_document_object: ParsedDocumentObject | None
    parsed_table_objects: tuple[ParsedTableObject, ...]
    parsed_field_objects: tuple[ParsedFieldObject, ...]
    parsed_block_objects: tuple[ParsedBlockObject, ...]
    structural_location_records: tuple[StructuralLocationRecord, ...]
    parsing_warning_records: tuple[ParsingWarningRecord, ...]
    parsing_failure_records: tuple[ParsingFailureRecord, ...]
    parsing_confidence_records: tuple[ParsingConfidenceRecord, ...]
    replay_manifest_record: ReplayManifestRecord

    def __post_init__(self) -> None:
        if self.extraction_metadata_record.parsing_status is ParsingStatus.FAILED:
            if self.parsed_document_object is not None:
                raise DomainInvariantError(
                    "Failed parse executions must not carry parsed_document_object."
                )
        else:
            if self.parsed_document_object is None:
                raise DomainInvariantError(
                    "Successful or partial parse executions must carry parsed_document_object."
                )

    @property
    def is_failed(self) -> bool:
        return self.extraction_metadata_record.parsing_status is ParsingStatus.FAILED

    @property
    def is_partial(self) -> bool:
        return self.extraction_metadata_record.parsing_status is ParsingStatus.PARTIAL

    @property
    def has_warnings(self) -> bool:
        return bool(self.parsing_warning_records)

    @property
    def has_failures(self) -> bool:
        return bool(self.parsing_failure_records)


def build_parser_strategy_record(
    *,
    parser_strategy_type: ParserStrategyType,
    strategy_name: str,
    strategy_version: str,
    applicable_formats: tuple[SourceFormatFamily, ...],
    parameter_fingerprint_value: str,
    clock: Callable[[], datetime] = default_clock,
) -> ParserStrategyRecord:
    created_at = clock()
    strategy_id = ParserStrategyRecordId(
        _stable_id(
            "parser_strategy",
            parser_strategy_type.value,
            strategy_name,
            strategy_version,
            ",".join(item.value for item in applicable_formats),
        )
    )
    return ParserStrategyRecord(
        parser_strategy_record_id=strategy_id,
        parser_strategy_type=parser_strategy_type,
        strategy_name=strategy_name,
        parser_strategy_version=ParserStrategyVersion(strategy_version),
        implementation_fingerprint=ImplementationFingerprint(
            _stable_id(
                "implementation_fingerprint",
                parser_strategy_type.value,
                strategy_name,
                strategy_version,
            )
        ),
        parameter_fingerprint=ParameterFingerprint(parameter_fingerprint_value),
        applicable_formats=applicable_formats,
        created_at=created_at,
    )


def build_extraction_metadata_record(
    *,
    captured_raw_asset: CapturedRawAsset,
    parser_strategy_record: ParserStrategyRecord,
    parsing_status: ParsingStatus,
    partial_parse_status: PartialParseStatus,
    heuristic_notes: tuple[str, ...],
    clock: Callable[[], datetime] = default_clock,
) -> ExtractionMetadataRecord:
    now = clock()
    extraction_id = ExtractionMetadataRecordId(
        _stable_id(
            "extraction_metadata",
            captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id.value,
            parser_strategy_record.parser_strategy_record_id.value,
            parsing_status.value,
            partial_parse_status.value,
            *heuristic_notes,
        )
    )
    return ExtractionMetadataRecord(
        extraction_metadata_record_id=extraction_id,
        raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
        parser_strategy_record_id=parser_strategy_record.parser_strategy_record_id,
        parsing_status=parsing_status,
        partial_parse_status=partial_parse_status,
        extraction_started_at=now,
        extraction_completed_at=now,
        heuristic_notes=heuristic_notes,
    )


def build_parsed_document_object(
    *,
    captured_raw_asset: CapturedRawAsset,
    parser_strategy_record: ParserStrategyRecord,
    extraction_metadata_record: ExtractionMetadataRecord,
    document_title: str | None,
    clock: Callable[[], datetime] = default_clock,
) -> ParsedDocumentObject:
    return ParsedDocumentObject(
        parsed_document_object_id=ParsedDocumentObjectId(
            _stable_id(
                "parsed_document",
                captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id.value,
                extraction_metadata_record.extraction_metadata_record_id.value,
            )
        ),
        raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
        parser_strategy_record_id=parser_strategy_record.parser_strategy_record_id,
        extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
        parsing_status=extraction_metadata_record.parsing_status,
        partial_parse_status=extraction_metadata_record.partial_parse_status,
        document_title=document_title,
        created_at=clock(),
    )


def build_warning_record(
    *,
    scope_ref: ParsingScopeRef,
    warning_code: str,
    warning_severity: WarningSeverity,
    message: str,
    scope_marker: str,
    clock: Callable[[], datetime] = default_clock,
) -> ParsingWarningRecord:
    return ParsingWarningRecord(
        parsing_warning_record_id=ParsingWarningRecordId(
            _stable_id("parsing_warning", warning_code, scope_marker, scope_ref.scope_kind.value)
        ),
        scope_ref=scope_ref,
        warning_code=WarningCode(warning_code),
        warning_severity=warning_severity,
        message=message,
        created_at=clock(),
    )


def build_failure_record(
    *,
    scope_ref: ParsingScopeRef,
    failure_code: str,
    failure_severity: FailureSeverity,
    failure_stage: FailureStage,
    cause: str,
    recoverable: bool,
    scope_marker: str,
    clock: Callable[[], datetime] = default_clock,
) -> ParsingFailureRecord:
    return ParsingFailureRecord(
        parsing_failure_record_id=ParsingFailureRecordId(
            _stable_id("parsing_failure", failure_code, scope_marker, scope_ref.scope_kind.value)
        ),
        scope_ref=scope_ref,
        failure_code=FailureCode(failure_code),
        failure_severity=failure_severity,
        failure_stage=failure_stage,
        cause=cause,
        recoverable=recoverable,
        created_at=clock(),
    )


def build_heuristic_confidence_record(
    *,
    scope_ref: ParsingScopeRef,
    confidence_value: float,
    confidence_method: str,
    scope_marker: str,
    clock: Callable[[], datetime] = default_clock,
) -> ParsingConfidenceRecord:
    from ...domain.enums import ConfidenceStatus

    return ParsingConfidenceRecord(
        parsing_confidence_record_id=ParsingConfidenceRecordId(
            _stable_id(
                "parsing_confidence",
                scope_marker,
                scope_ref.scope_kind.value,
                confidence_method,
            )
        ),
        scope_ref=scope_ref,
        confidence_status=ConfidenceStatus.HEURISTIC,
        confidence_value=ConfidenceValue(confidence_value),
        confidence_method=confidence_method,
        created_at=clock(),
    )


def build_replay_manifest_record(
    *,
    captured_raw_asset: CapturedRawAsset,
    parser_strategy_record: ParserStrategyRecord,
    extraction_metadata_record: ExtractionMetadataRecord,
    replayability_status: ReplayabilityStatus,
    expected_output_refs: tuple[ParsingScopeRef, ...],
    clock: Callable[[], datetime] = default_clock,
) -> ReplayManifestRecord:
    return ReplayManifestRecord(
        replay_manifest_record_id=ReplayManifestRecordId(
            _stable_id(
                "replay_manifest",
                captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id.value,
                extraction_metadata_record.extraction_metadata_record_id.value,
                replayability_status.value,
                *(item.identifier.value for item in expected_output_refs),
            )
        ),
        raw_asset_version_record_id=captured_raw_asset.raw_asset_version_record.raw_asset_version_record_id,
        parser_strategy_record_id=parser_strategy_record.parser_strategy_record_id,
        extraction_metadata_record_id=extraction_metadata_record.extraction_metadata_record_id,
        replayability_status=replayability_status,
        raw_content_checksum=captured_raw_asset.raw_asset_version_record.content_checksum,
        parameter_fingerprint=parser_strategy_record.parameter_fingerprint,
        expected_output_refs=expected_output_refs,
        created_at=clock(),
    )


def expected_output_refs_for_parse(
    *,
    extraction_metadata_record: ExtractionMetadataRecord,
    parsed_document_object: ParsedDocumentObject | None = None,
    parsed_table_objects: Iterable[ParsedTableObject] = (),
    parsed_field_objects: Iterable[ParsedFieldObject] = (),
    parsed_block_objects: Iterable[ParsedBlockObject] = (),
) -> tuple[ParsingScopeRef, ...]:
    refs: list[ParsingScopeRef] = [
        ParsingScopeRef.for_extraction_metadata(
            extraction_metadata_record.extraction_metadata_record_id
        )
    ]
    if parsed_document_object is not None:
        refs.append(
            ParsingScopeRef.for_parsed_document(parsed_document_object.parsed_document_object_id)
        )
    refs.extend(ParsingScopeRef.for_parsed_table(item.parsed_table_object_id) for item in parsed_table_objects)
    refs.extend(ParsingScopeRef.for_parsed_field(item.parsed_field_object_id) for item in parsed_field_objects)
    refs.extend(ParsingScopeRef.for_parsed_block(item.parsed_block_object_id) for item in parsed_block_objects)
    return tuple(refs)


def failed_parse_result(
    *,
    captured_raw_asset: CapturedRawAsset,
    parser_strategy_record: ParserStrategyRecord,
    heuristic_notes: tuple[str, ...],
    failure_code: str,
    failure_severity: FailureSeverity,
    failure_stage: FailureStage,
    cause: str,
    recoverable: bool,
    replayability_status: ReplayabilityStatus = ReplayabilityStatus.NOT_REPLAYABLE,
    warning_records: tuple[ParsingWarningRecord, ...] = (),
    clock: Callable[[], datetime] = default_clock,
) -> ParseExecutionResult:
    extraction_metadata_record = build_extraction_metadata_record(
        captured_raw_asset=captured_raw_asset,
        parser_strategy_record=parser_strategy_record,
        parsing_status=ParsingStatus.FAILED,
        partial_parse_status=PartialParseStatus.NOT_PARTIAL,
        heuristic_notes=heuristic_notes,
        clock=clock,
    )
    failure_record = build_failure_record(
        scope_ref=ParsingScopeRef.for_extraction_metadata(
            extraction_metadata_record.extraction_metadata_record_id
        ),
        failure_code=failure_code,
        failure_severity=failure_severity,
        failure_stage=failure_stage,
        cause=cause,
        recoverable=recoverable,
        scope_marker=extraction_metadata_record.extraction_metadata_record_id.value,
        clock=clock,
    )
    replay_manifest_record = build_replay_manifest_record(
        captured_raw_asset=captured_raw_asset,
        parser_strategy_record=parser_strategy_record,
        extraction_metadata_record=extraction_metadata_record,
        replayability_status=replayability_status,
        expected_output_refs=expected_output_refs_for_parse(
            extraction_metadata_record=extraction_metadata_record
        ),
        clock=clock,
    )
    return ParseExecutionResult(
        captured_raw_asset=captured_raw_asset,
        parser_strategy_record=parser_strategy_record,
        extraction_metadata_record=extraction_metadata_record,
        parsed_document_object=None,
        parsed_table_objects=(),
        parsed_field_objects=(),
        parsed_block_objects=(),
        structural_location_records=(),
        parsing_warning_records=warning_records,
        parsing_failure_records=(failure_record,),
        parsing_confidence_records=(),
        replay_manifest_record=replay_manifest_record,
    )


__all__ = [
    "CapturedRawAsset",
    "ParseExecutionResult",
    "build_extraction_metadata_record",
    "build_failure_record",
    "build_heuristic_confidence_record",
    "build_parser_strategy_record",
    "build_parsed_document_object",
    "build_replay_manifest_record",
    "build_warning_record",
    "expected_output_refs_for_parse",
    "failed_parse_result",
]
