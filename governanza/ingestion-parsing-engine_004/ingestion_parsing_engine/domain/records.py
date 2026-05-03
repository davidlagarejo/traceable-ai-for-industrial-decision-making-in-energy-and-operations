from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    ConfidenceStatus,
    FailureSeverity,
    FailureStage,
    LocationKind,
    ParsingStatus,
    PartialParseStatus,
    ReplayabilityStatus,
    WarningSeverity,
)
from .errors import DomainInvariantError
from .value_objects import (
    BlockOffsets,
    CellCoordinates,
    ConfidenceValue,
    ContentChecksum,
    EndpointReference,
    ExtractionMetadataRecordId,
    FailureCode,
    ParameterFingerprint,
    ParserStrategyRecordId,
    ParsingConfidenceRecordId,
    ParsingFailureRecordId,
    ParsingScopeRef,
    ParsingWarningRecordId,
    PayloadPath,
    PreservationPointer,
    RawAssetVersionRecordId,
    ReplayManifestRecordId,
    Selector,
    StructuralLocationRecordId,
    UriReference,
    WarningCode,
    PageNumber,
    TableNumber,
    _ensure_unique,
    _require_text,
    _require_timezone,
)


def _validate_partial_state(
    parsing_status: ParsingStatus,
    partial_parse_status: PartialParseStatus,
    *,
    allow_failed: bool,
) -> None:
    if parsing_status is ParsingStatus.COMPLETE and partial_parse_status is not PartialParseStatus.NOT_PARTIAL:
        raise DomainInvariantError(
            "Complete parsing status must not declare a partial parse status."
        )
    if parsing_status is ParsingStatus.PARTIAL and partial_parse_status is PartialParseStatus.NOT_PARTIAL:
        raise DomainInvariantError(
            "Partial parsing status must declare a partial parse status."
        )
    if parsing_status is ParsingStatus.FAILED:
        if not allow_failed:
            raise DomainInvariantError("This record must not declare FAILED parsing status.")
        if partial_parse_status is not PartialParseStatus.NOT_PARTIAL:
            raise DomainInvariantError(
                "Failed parsing status must not declare a partial parse status."
            )


@dataclass(frozen=True, slots=True)
class StructuralLocationRecord:
    structural_location_record_id: StructuralLocationRecordId
    location_kind: LocationKind
    page_number: PageNumber | None
    table_number: TableNumber | None
    cell_coordinates: CellCoordinates | None
    sheet_name: str | None
    sheet_index: int | None
    block_index: int | None
    block_offsets: BlockOffsets | None
    selector: Selector | None
    endpoint_reference: EndpointReference | None
    payload_path: PayloadPath | None
    uri_fragment: UriReference | None

    def __post_init__(self) -> None:
        if self.sheet_name is not None:
            object.__setattr__(self, "sheet_name", _require_text(self.sheet_name, "sheet_name"))
        if self.sheet_index is not None and self.sheet_index < 0:
            raise DomainInvariantError("sheet_index must be greater than or equal to 0.")
        if self.block_index is not None and self.block_index < 0:
            raise DomainInvariantError("block_index must be greater than or equal to 0.")

        if not any(
            (
                self.page_number is not None,
                self.table_number is not None,
                self.cell_coordinates is not None,
                self.sheet_name is not None,
                self.sheet_index is not None,
                self.block_index is not None,
                self.block_offsets is not None,
                self.selector is not None,
                self.endpoint_reference is not None,
                self.payload_path is not None,
                self.uri_fragment is not None,
            )
        ):
            raise DomainInvariantError("StructuralLocationRecord must not be semantically empty.")

        if self.location_kind is LocationKind.PDF_PAGE and self.page_number is None:
            raise DomainInvariantError("PDF_PAGE locations require page_number.")
        if self.location_kind is LocationKind.PDF_TABLE:
            if self.page_number is None or self.table_number is None:
                raise DomainInvariantError("PDF_TABLE locations require page_number and table_number.")
        if self.location_kind is LocationKind.TABLE_CELL and self.cell_coordinates is None:
            raise DomainInvariantError("TABLE_CELL locations require cell_coordinates.")
        if self.location_kind is LocationKind.XLSX_SHEET:
            if self.sheet_name is None and self.sheet_index is None:
                raise DomainInvariantError("XLSX_SHEET locations require sheet_name or sheet_index.")
        if self.location_kind is LocationKind.TEXT_BLOCK:
            if self.block_index is None and self.block_offsets is None:
                raise DomainInvariantError("TEXT_BLOCK locations require block_index or block_offsets.")
        if self.location_kind is LocationKind.HTML_SELECTOR and self.selector is None:
            raise DomainInvariantError("HTML_SELECTOR locations require selector.")
        if self.location_kind is LocationKind.JSON_PATH and self.payload_path is None:
            raise DomainInvariantError("JSON_PATH locations require payload_path.")
        if self.location_kind is LocationKind.API_ENDPOINT and self.endpoint_reference is None:
            raise DomainInvariantError("API_ENDPOINT locations require endpoint_reference.")
        if self.location_kind is LocationKind.API_PAYLOAD_POINTER:
            if self.endpoint_reference is None or self.payload_path is None:
                raise DomainInvariantError(
                    "API_PAYLOAD_POINTER locations require endpoint_reference and payload_path."
                )
        if self.location_kind is LocationKind.URI_FRAGMENT and self.uri_fragment is None:
            raise DomainInvariantError("URI_FRAGMENT locations require uri_fragment.")


@dataclass(frozen=True, slots=True)
class ExtractionMetadataRecord:
    extraction_metadata_record_id: ExtractionMetadataRecordId
    raw_asset_version_record_id: RawAssetVersionRecordId
    parser_strategy_record_id: ParserStrategyRecordId
    parsing_status: ParsingStatus
    partial_parse_status: PartialParseStatus
    extraction_started_at: datetime
    extraction_completed_at: datetime
    heuristic_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_partial_state(
            self.parsing_status,
            self.partial_parse_status,
            allow_failed=True,
        )
        object.__setattr__(
            self,
            "extraction_started_at",
            _require_timezone(self.extraction_started_at, "extraction_started_at"),
        )
        object.__setattr__(
            self,
            "extraction_completed_at",
            _require_timezone(self.extraction_completed_at, "extraction_completed_at"),
        )
        if self.extraction_completed_at < self.extraction_started_at:
            raise DomainInvariantError(
                "extraction_completed_at must be greater than or equal to extraction_started_at."
            )
        normalized_notes = tuple(_require_text(item, "heuristic_note") for item in self.heuristic_notes)
        object.__setattr__(self, "heuristic_notes", normalized_notes)
        _ensure_unique(normalized_notes, "heuristic_notes")


@dataclass(frozen=True, slots=True)
class ParsingWarningRecord:
    parsing_warning_record_id: ParsingWarningRecordId
    scope_ref: ParsingScopeRef
    warning_code: WarningCode
    warning_severity: WarningSeverity
    message: str
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "message", _require_text(self.message, "message"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class ParsingFailureRecord:
    parsing_failure_record_id: ParsingFailureRecordId
    scope_ref: ParsingScopeRef
    failure_code: FailureCode
    failure_severity: FailureSeverity
    failure_stage: FailureStage
    cause: str
    recoverable: bool
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "cause", _require_text(self.cause, "cause"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.failure_severity is FailureSeverity.RECOVERABLE and not self.recoverable:
            raise DomainInvariantError("Recoverable failures must declare recoverable=True.")
        if self.failure_severity is FailureSeverity.CRITICAL and self.recoverable:
            raise DomainInvariantError("Critical failures must declare recoverable=False.")


@dataclass(frozen=True, slots=True)
class ParsingConfidenceRecord:
    parsing_confidence_record_id: ParsingConfidenceRecordId
    scope_ref: ParsingScopeRef
    confidence_status: ConfidenceStatus
    confidence_value: ConfidenceValue | None
    confidence_method: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.confidence_status is ConfidenceStatus.NOT_AVAILABLE:
            if self.confidence_value is not None or self.confidence_method is not None:
                raise DomainInvariantError(
                    "NOT_AVAILABLE confidence must not declare confidence_value or confidence_method."
                )
            return
        if self.confidence_value is None:
            raise DomainInvariantError("Confidence records must declare confidence_value.")
        if self.confidence_method is None:
            raise DomainInvariantError("Confidence records must declare confidence_method.")
        object.__setattr__(
            self,
            "confidence_method",
            _require_text(self.confidence_method, "confidence_method"),
        )


@dataclass(frozen=True, slots=True)
class ReplayManifestRecord:
    replay_manifest_record_id: ReplayManifestRecordId
    raw_asset_version_record_id: RawAssetVersionRecordId
    parser_strategy_record_id: ParserStrategyRecordId
    extraction_metadata_record_id: ExtractionMetadataRecordId
    replayability_status: ReplayabilityStatus
    raw_content_checksum: ContentChecksum
    parameter_fingerprint: ParameterFingerprint
    expected_output_refs: tuple[ParsingScopeRef, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.expected_output_refs:
            raise DomainInvariantError("ReplayManifestRecord.expected_output_refs must not be empty.")
        _ensure_unique(self.expected_output_refs, "expected_output_refs")


__all__ = [
    "ExtractionMetadataRecord",
    "ParsingConfidenceRecord",
    "ParsingFailureRecord",
    "ParsingWarningRecord",
    "ReplayManifestRecord",
    "StructuralLocationRecord",
]
