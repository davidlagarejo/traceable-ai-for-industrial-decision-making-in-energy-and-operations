from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable

from .._compat import dataclass
from .enums import (
    NormalizationScopeKind,
    PrecisionKind,
)
from .errors import DomainInvariantError


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainInvariantError(f"{field_name} must be non-empty.")
    return normalized


def _require_preserved_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise DomainInvariantError(f"{field_name} must be a string.")
    return value


def _require_timezone(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise DomainInvariantError(f"{field_name} must be timezone-aware.")
    return value


def _ensure_unique(values: Iterable[object], field_name: str) -> None:
    materialized = tuple(values)
    if len(materialized) != len(set(materialized)):
        raise DomainInvariantError(f"{field_name} must not contain duplicates.")


def _require_decimal(value: Decimal | str | int | float, field_name: str) -> Decimal:
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DomainInvariantError(f"{field_name} must be a valid decimal.") from exc
    return decimal_value


@dataclass(frozen=True, slots=True)
class CanonicalSchemaRegistryId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CanonicalSchemaRegistryId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalSchemaVersionId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CanonicalSchemaVersionId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalFieldDefinitionId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CanonicalFieldDefinitionId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FieldMappingRuleId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "FieldMappingRuleId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TypeCoercionRuleId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "TypeCoercionRuleId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class UnitConversionRuleId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "UnitConversionRuleId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CurrencyConversionRuleId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CurrencyConversionRuleId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizationRunRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NormalizationRunRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedFieldRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NormalizedFieldRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NormalizedRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedRecordSetId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NormalizedRecordSetId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizationWarningRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NormalizationWarningRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NonNormalizableFieldRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NonNormalizableFieldRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PartialNormalizationRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "PartialNormalizationRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizationReplayManifestId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NormalizationReplayManifestId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SchemaName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SchemaName.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VersionLabel:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "VersionLabel.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VersionFingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "VersionFingerprint.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalFieldName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CanonicalFieldName.value"),
        )

    @property
    def normalized(self) -> str:
        return "_".join(self.value.casefold().split())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class OriginalLabel:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "OriginalLabel.value"))

    @property
    def normalized(self) -> str:
        return " ".join(self.value.casefold().split())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RuleDescription:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "RuleDescription.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RuleFingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "RuleFingerprint.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SourceFormatHint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "SourceFormatHint.value"),
        )


@dataclass(frozen=True, slots=True)
class SourcePathHint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "SourcePathHint.value"),
        )


@dataclass(frozen=True, slots=True)
class MappingContext:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "MappingContext.value"),
        )


@dataclass(frozen=True, slots=True)
class RawValue:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_preserved_text(self.value, "RawValue.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParsedValue:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_preserved_text(self.value, "ParsedValue.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedValue:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_preserved_text(self.value, "NormalizedValue.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class UnitRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "UnitRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CurrencyCode:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value.upper(), "CurrencyCode.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CurrencyYear:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1900 or self.value > 3000:
            raise DomainInvariantError("CurrencyYear.value must be between 1900 and 3000.")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ConversionFactor:
    value: Decimal

    def __init__(self, value: Decimal | str | int | float) -> None:
        decimal_value = _require_decimal(value, "ConversionFactor.value")
        if decimal_value <= 0:
            raise DomainInvariantError("ConversionFactor.value must be greater than 0.")
        object.__setattr__(self, "value", decimal_value)

    def __str__(self) -> str:
        return format(self.value, "f")


@dataclass(frozen=True, slots=True)
class PrecisionDescriptor:
    precision_kind: PrecisionKind
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.detail is not None:
            object.__setattr__(self, "detail", _require_text(self.detail, "PrecisionDescriptor.detail"))


@dataclass(frozen=True, slots=True)
class RecordKey:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RecordKey.value"))


@dataclass(frozen=True, slots=True)
class WarningCode:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "WarningCode.value"))


@dataclass(frozen=True, slots=True)
class NonNormalizableReason:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "NonNormalizableReason.value"),
        )


@dataclass(frozen=True, slots=True)
class ParsedDocumentObjectRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ParsedDocumentObjectRef.value"),
        )


@dataclass(frozen=True, slots=True)
class ParsedTableObjectRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ParsedTableObjectRef.value"),
        )


@dataclass(frozen=True, slots=True)
class ParsedFieldObjectRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ParsedFieldObjectRef.value"),
        )


@dataclass(frozen=True, slots=True)
class RawAssetVersionRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "RawAssetVersionRef.value"),
        )


@dataclass(frozen=True, slots=True)
class ExtractionMetadataRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ExtractionMetadataRef.value"),
        )


@dataclass(frozen=True, slots=True)
class ParserStrategyRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ParserStrategyRef.value"),
        )


@dataclass(frozen=True, slots=True)
class ParsedSourceProvenance:
    raw_asset_version_ref: RawAssetVersionRef
    extraction_metadata_ref: ExtractionMetadataRef
    parsed_document_object_ref: ParsedDocumentObjectRef
    parser_strategy_ref: ParserStrategyRef
    parsed_table_object_ref: ParsedTableObjectRef | None
    parsed_field_object_ref: ParsedFieldObjectRef | None


@dataclass(frozen=True, slots=True)
class ValueTriplet:
    raw_value: RawValue
    parsed_value: ParsedValue
    normalized_value: NormalizedValue | None

    @property
    def has_normalized_value(self) -> bool:
        return self.normalized_value is not None


@dataclass(frozen=True, slots=True)
class NormalizationScopeRef:
    scope_kind: NormalizationScopeKind
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "identifier",
            _require_text(self.identifier, "NormalizationScopeRef.identifier"),
        )

    @classmethod
    def for_normalization_run(
        cls,
        normalization_run_record_id: NormalizationRunRecordId,
    ) -> "NormalizationScopeRef":
        return cls(NormalizationScopeKind.NORMALIZATION_RUN, normalization_run_record_id.value)

    @classmethod
    def for_normalized_record_set(
        cls,
        normalized_record_set_id: NormalizedRecordSetId,
    ) -> "NormalizationScopeRef":
        return cls(
            NormalizationScopeKind.NORMALIZED_RECORD_SET,
            normalized_record_set_id.value,
        )

    @classmethod
    def for_normalized_record(
        cls,
        normalized_record_id: NormalizedRecordId,
    ) -> "NormalizationScopeRef":
        return cls(NormalizationScopeKind.NORMALIZED_RECORD, normalized_record_id.value)

    @classmethod
    def for_normalized_field(
        cls,
        normalized_field_record_id: NormalizedFieldRecordId,
    ) -> "NormalizationScopeRef":
        return cls(NormalizationScopeKind.NORMALIZED_FIELD, normalized_field_record_id.value)

    @classmethod
    def for_non_normalizable_field(
        cls,
        non_normalizable_field_record_id: NonNormalizableFieldRecordId,
    ) -> "NormalizationScopeRef":
        return cls(
            NormalizationScopeKind.NON_NORMALIZABLE_FIELD,
            non_normalizable_field_record_id.value,
        )

    @classmethod
    def for_partial_normalization(
        cls,
        partial_normalization_record_id: PartialNormalizationRecordId,
    ) -> "NormalizationScopeRef":
        return cls(
            NormalizationScopeKind.PARTIAL_NORMALIZATION,
            partial_normalization_record_id.value,
        )
