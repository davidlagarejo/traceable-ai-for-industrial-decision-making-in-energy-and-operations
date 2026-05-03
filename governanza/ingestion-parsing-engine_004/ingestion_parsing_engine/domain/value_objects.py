from __future__ import annotations

from datetime import datetime
from typing import Union

from .._compat import dataclass
from .enums import ParsingScopeKind
from .errors import DomainInvariantError


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainInvariantError(f"{field_name} must be non-empty.")
    return normalized


def _require_timezone(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise DomainInvariantError(f"{field_name} must be timezone-aware.")
    return value


def _ensure_unique(values: tuple[object, ...], field_name: str) -> None:
    if len(values) != len(set(values)):
        raise DomainInvariantError(f"{field_name} must not contain duplicates.")


@dataclass(frozen=True, slots=True)
class SourceIdRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SourceIdRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SourceAccessPolicyRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SourceAccessPolicyRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class IngestionRequestRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "IngestionRequestRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RetrievalRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RetrievalRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RawAssetRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RawAssetRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RawAssetVersionRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RawAssetVersionRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsedDocumentObjectId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsedDocumentObjectId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsedTableObjectId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsedTableObjectId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsedFieldObjectId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsedFieldObjectId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsedBlockObjectId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsedBlockObjectId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class StructuralLocationRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "StructuralLocationRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ExtractionMetadataRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ExtractionMetadataRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsingWarningRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsingWarningRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsingFailureRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsingFailureRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsingConfidenceRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParsingConfidenceRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParserStrategyRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParserStrategyRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ReplayManifestRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ReplayManifestRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SourceAdapterRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SourceAdapterRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParserStrategyVersion:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParserStrategyVersion.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContentChecksum:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ContentChecksum.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContentType:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ContentType.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SourceVisibleVersion:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SourceVisibleVersion.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RequestFingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RequestFingerprint.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ImplementationFingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ImplementationFingerprint.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParameterFingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ParameterFingerprint.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PreservationPointer:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "PreservationPointer.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class UriReference:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "UriReference.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EndpointReference:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EndpointReference.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PayloadPath:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "PayloadPath.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Selector:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "Selector.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class WarningCode:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "WarningCode.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FailureCode:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "FailureCode.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ConfidenceValue:
    value: float

    def __post_init__(self) -> None:
        if self.value < 0.0 or self.value > 1.0:
            raise DomainInvariantError("ConfidenceValue.value must be between 0.0 and 1.0.")

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True, slots=True)
class PageNumber:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise DomainInvariantError("PageNumber.value must be greater than or equal to 1.")

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, slots=True)
class TableNumber:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise DomainInvariantError("TableNumber.value must be greater than or equal to 1.")

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, slots=True)
class CellCoordinates:
    row_index: int
    column_index: int

    def __post_init__(self) -> None:
        if self.row_index < 0:
            raise DomainInvariantError("CellCoordinates.row_index must be greater than or equal to 0.")
        if self.column_index < 0:
            raise DomainInvariantError("CellCoordinates.column_index must be greater than or equal to 0.")


@dataclass(frozen=True, slots=True)
class BlockOffsets:
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        if self.start_offset < 0:
            raise DomainInvariantError("BlockOffsets.start_offset must be greater than or equal to 0.")
        if self.end_offset < self.start_offset:
            raise DomainInvariantError("BlockOffsets.end_offset must be greater than or equal to start_offset.")


ParsingScopeIdentifier = Union[
    RawAssetVersionRecordId,
    ParsedDocumentObjectId,
    ParsedTableObjectId,
    ParsedFieldObjectId,
    ParsedBlockObjectId,
    StructuralLocationRecordId,
    ExtractionMetadataRecordId,
]


@dataclass(frozen=True, slots=True)
class ParsingScopeRef:
    scope_kind: ParsingScopeKind
    identifier: ParsingScopeIdentifier

    def __post_init__(self) -> None:
        expected_type = {
            ParsingScopeKind.RAW_ASSET_VERSION: RawAssetVersionRecordId,
            ParsingScopeKind.PARSED_DOCUMENT: ParsedDocumentObjectId,
            ParsingScopeKind.PARSED_TABLE: ParsedTableObjectId,
            ParsingScopeKind.PARSED_FIELD: ParsedFieldObjectId,
            ParsingScopeKind.PARSED_BLOCK: ParsedBlockObjectId,
            ParsingScopeKind.STRUCTURAL_LOCATION: StructuralLocationRecordId,
            ParsingScopeKind.EXTRACTION_METADATA: ExtractionMetadataRecordId,
        }[self.scope_kind]
        if not isinstance(self.identifier, expected_type):
            raise DomainInvariantError("ParsingScopeRef.identifier does not match scope_kind.")

    @classmethod
    def for_raw_asset_version(cls, identifier: RawAssetVersionRecordId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.RAW_ASSET_VERSION, identifier)

    @classmethod
    def for_parsed_document(cls, identifier: ParsedDocumentObjectId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.PARSED_DOCUMENT, identifier)

    @classmethod
    def for_parsed_table(cls, identifier: ParsedTableObjectId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.PARSED_TABLE, identifier)

    @classmethod
    def for_parsed_field(cls, identifier: ParsedFieldObjectId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.PARSED_FIELD, identifier)

    @classmethod
    def for_parsed_block(cls, identifier: ParsedBlockObjectId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.PARSED_BLOCK, identifier)

    @classmethod
    def for_structural_location(cls, identifier: StructuralLocationRecordId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.STRUCTURAL_LOCATION, identifier)

    @classmethod
    def for_extraction_metadata(cls, identifier: ExtractionMetadataRecordId) -> "ParsingScopeRef":
        return cls(ParsingScopeKind.EXTRACTION_METADATA, identifier)


__all__ = [
    "BlockOffsets",
    "CellCoordinates",
    "ConfidenceValue",
    "ContentChecksum",
    "ContentType",
    "EndpointReference",
    "ExtractionMetadataRecordId",
    "FailureCode",
    "ImplementationFingerprint",
    "IngestionRequestRecordId",
    "PageNumber",
    "ParameterFingerprint",
    "ParsedBlockObjectId",
    "ParsedDocumentObjectId",
    "ParsedFieldObjectId",
    "ParsedTableObjectId",
    "ParserStrategyRecordId",
    "ParserStrategyVersion",
    "ParsingConfidenceRecordId",
    "ParsingFailureRecordId",
    "ParsingScopeRef",
    "ParsingWarningRecordId",
    "PayloadPath",
    "PreservationPointer",
    "RawAssetRecordId",
    "RawAssetVersionRecordId",
    "ReplayManifestRecordId",
    "RequestFingerprint",
    "RetrievalRecordId",
    "Selector",
    "SourceAccessPolicyRef",
    "SourceAdapterRef",
    "SourceIdRef",
    "SourceVisibleVersion",
    "StructuralLocationRecordId",
    "TableNumber",
    "UriReference",
    "WarningCode",
    "_ensure_unique",
    "_require_text",
    "_require_timezone",
]
