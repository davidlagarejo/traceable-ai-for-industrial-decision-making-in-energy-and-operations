from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    ParsedObjectType,
    ParserStrategyType,
    ParsingStatus,
    PartialParseStatus,
    RawAssetKind,
    ReplayabilityStatus,
    RetrievalStatus,
    RightsRestrictionLevel,
    SourceFormatFamily,
)
from .errors import DomainInvariantError
from .value_objects import (
    ContentChecksum,
    ContentType,
    EndpointReference,
    ExtractionMetadataRecordId,
    ImplementationFingerprint,
    IngestionRequestRecordId,
    ParameterFingerprint,
    ParsedBlockObjectId,
    ParsedDocumentObjectId,
    ParsedFieldObjectId,
    ParsedTableObjectId,
    ParserStrategyRecordId,
    ParserStrategyVersion,
    PreservationPointer,
    RawAssetRecordId,
    RawAssetVersionRecordId,
    RequestFingerprint,
    RetrievalRecordId,
    SourceAccessPolicyRef,
    SourceAdapterRef,
    SourceIdRef,
    SourceVisibleVersion,
    StructuralLocationRecordId,
    UriReference,
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
            raise DomainInvariantError("Parsed objects must not declare FAILED parsing status.")
        if partial_parse_status is not PartialParseStatus.NOT_PARTIAL:
            raise DomainInvariantError(
                "Failed parsing status must not declare a partial parse status."
            )


@dataclass(frozen=True, slots=True)
class IngestionRequestRecord:
    ingestion_request_record_id: IngestionRequestRecordId
    source_id_ref: SourceIdRef
    source_access_policy_ref: SourceAccessPolicyRef
    raw_asset_kind: RawAssetKind
    declared_format: SourceFormatFamily
    rights_restriction_level: RightsRestrictionLevel
    request_fingerprint: RequestFingerprint
    original_uri: UriReference | None
    endpoint_reference: EndpointReference | None
    requested_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "requested_at", _require_timezone(self.requested_at, "requested_at"))
        if self.original_uri is None and self.endpoint_reference is None:
            raise DomainInvariantError(
                "IngestionRequestRecord must declare original_uri or endpoint_reference."
            )


@dataclass(frozen=True, slots=True)
class RetrievalRecord:
    retrieval_record_id: RetrievalRecordId
    ingestion_request_record_id: IngestionRequestRecordId
    raw_asset_record_id: RawAssetRecordId
    source_adapter_ref: SourceAdapterRef
    retrieval_status: RetrievalStatus
    request_fingerprint: RequestFingerprint
    response_status_code: int | None
    retrieval_started_at: datetime
    retrieval_completed_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "retrieval_started_at",
            _require_timezone(self.retrieval_started_at, "retrieval_started_at"),
        )
        object.__setattr__(
            self,
            "retrieval_completed_at",
            _require_timezone(self.retrieval_completed_at, "retrieval_completed_at"),
        )
        if self.retrieval_completed_at < self.retrieval_started_at:
            raise DomainInvariantError(
                "retrieval_completed_at must be greater than or equal to retrieval_started_at."
            )
        if self.response_status_code is not None:
            if self.response_status_code < 100 or self.response_status_code > 599:
                raise DomainInvariantError("response_status_code must be between 100 and 599.")


@dataclass(frozen=True, slots=True)
class RawAssetRecord:
    raw_asset_record_id: RawAssetRecordId
    source_id_ref: SourceIdRef
    source_access_policy_ref: SourceAccessPolicyRef
    raw_asset_kind: RawAssetKind
    declared_format: SourceFormatFamily
    rights_restriction_level: RightsRestrictionLevel
    original_uri: UriReference | None
    endpoint_reference: EndpointReference | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.original_uri is None and self.endpoint_reference is None:
            raise DomainInvariantError(
                "RawAssetRecord must declare original_uri or endpoint_reference."
            )


@dataclass(frozen=True, slots=True)
class RawAssetVersionRecord:
    raw_asset_version_record_id: RawAssetVersionRecordId
    raw_asset_record_id: RawAssetRecordId
    retrieval_record_id: RetrievalRecordId
    content_checksum: ContentChecksum
    content_type: ContentType
    content_length: int
    detected_format: SourceFormatFamily
    source_visible_version: SourceVisibleVersion | None
    raw_preservation_pointer: PreservationPointer
    charset: str | None
    captured_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "captured_at", _require_timezone(self.captured_at, "captured_at"))
        if self.content_length < 0:
            raise DomainInvariantError("content_length must be greater than or equal to 0.")
        if self.charset is not None:
            object.__setattr__(self, "charset", _require_text(self.charset, "charset"))


@dataclass(frozen=True, slots=True)
class ParserStrategyRecord:
    parser_strategy_record_id: ParserStrategyRecordId
    parser_strategy_type: ParserStrategyType
    strategy_name: str
    parser_strategy_version: ParserStrategyVersion
    implementation_fingerprint: ImplementationFingerprint
    parameter_fingerprint: ParameterFingerprint
    applicable_formats: tuple[SourceFormatFamily, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "strategy_name", _require_text(self.strategy_name, "strategy_name"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.applicable_formats:
            raise DomainInvariantError("applicable_formats must not be empty.")
        _ensure_unique(self.applicable_formats, "applicable_formats")


@dataclass(frozen=True, slots=True)
class ParsedDocumentObject:
    parsed_document_object_id: ParsedDocumentObjectId
    raw_asset_version_record_id: RawAssetVersionRecordId
    parser_strategy_record_id: ParserStrategyRecordId
    extraction_metadata_record_id: ExtractionMetadataRecordId
    parsing_status: ParsingStatus
    partial_parse_status: PartialParseStatus
    document_title: str | None
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_partial_state(
            self.parsing_status,
            self.partial_parse_status,
            allow_failed=False,
        )
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.document_title is not None:
            object.__setattr__(self, "document_title", _require_text(self.document_title, "document_title"))

    @property
    def parsed_object_type(self) -> ParsedObjectType:
        return ParsedObjectType.DOCUMENT


@dataclass(frozen=True, slots=True)
class ParsedTableObject:
    parsed_table_object_id: ParsedTableObjectId
    parsed_document_object_id: ParsedDocumentObjectId
    raw_asset_version_record_id: RawAssetVersionRecordId
    extraction_metadata_record_id: ExtractionMetadataRecordId
    structural_location_record_id: StructuralLocationRecordId
    parsing_status: ParsingStatus
    partial_parse_status: PartialParseStatus
    row_count: int
    column_count: int
    header_labels: tuple[str, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_partial_state(
            self.parsing_status,
            self.partial_parse_status,
            allow_failed=False,
        )
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.row_count < 0:
            raise DomainInvariantError("row_count must be greater than or equal to 0.")
        if self.column_count < 0:
            raise DomainInvariantError("column_count must be greater than or equal to 0.")
        normalized_headers = tuple(_require_text(item, "header_label") for item in self.header_labels)
        object.__setattr__(self, "header_labels", normalized_headers)
        if self.column_count == 0 and normalized_headers:
            raise DomainInvariantError("header_labels require column_count greater than 0.")
        if self.column_count > 0 and len(normalized_headers) > self.column_count:
            raise DomainInvariantError("header_labels must not exceed column_count.")

    @property
    def parsed_object_type(self) -> ParsedObjectType:
        return ParsedObjectType.TABLE


@dataclass(frozen=True, slots=True)
class ParsedFieldObject:
    parsed_field_object_id: ParsedFieldObjectId
    parsed_document_object_id: ParsedDocumentObjectId
    raw_asset_version_record_id: RawAssetVersionRecordId
    extraction_metadata_record_id: ExtractionMetadataRecordId
    structural_location_record_id: StructuralLocationRecordId
    parent_table_object_id: ParsedTableObjectId | None
    parent_block_object_id: ParsedBlockObjectId | None
    field_name: str | None
    raw_value: str
    parsing_status: ParsingStatus
    partial_parse_status: PartialParseStatus
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_partial_state(
            self.parsing_status,
            self.partial_parse_status,
            allow_failed=False,
        )
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.field_name is not None:
            object.__setattr__(self, "field_name", _require_text(self.field_name, "field_name"))
        if self.parent_table_object_id is not None and self.parent_block_object_id is not None:
            raise DomainInvariantError(
                "ParsedFieldObject must not declare both parent_table_object_id and parent_block_object_id."
            )
        if self.field_name is None and not self.raw_value:
            raise DomainInvariantError(
                "ParsedFieldObject must carry a field_name or a non-empty raw_value."
            )

    @property
    def parsed_object_type(self) -> ParsedObjectType:
        return ParsedObjectType.FIELD


@dataclass(frozen=True, slots=True)
class ParsedBlockObject:
    parsed_block_object_id: ParsedBlockObjectId
    parsed_document_object_id: ParsedDocumentObjectId
    raw_asset_version_record_id: RawAssetVersionRecordId
    extraction_metadata_record_id: ExtractionMetadataRecordId
    structural_location_record_id: StructuralLocationRecordId
    parent_table_object_id: ParsedTableObjectId | None
    raw_text: str
    parsing_status: ParsingStatus
    partial_parse_status: PartialParseStatus
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_partial_state(
            self.parsing_status,
            self.partial_parse_status,
            allow_failed=False,
        )
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.raw_text.strip():
            raise DomainInvariantError("ParsedBlockObject.raw_text must be non-empty.")

    @property
    def parsed_object_type(self) -> ParsedObjectType:
        return ParsedObjectType.BLOCK


__all__ = [
    "IngestionRequestRecord",
    "ParsedBlockObject",
    "ParsedDocumentObject",
    "ParsedFieldObject",
    "ParsedTableObject",
    "ParserStrategyRecord",
    "RawAssetRecord",
    "RawAssetVersionRecord",
    "RetrievalRecord",
]
