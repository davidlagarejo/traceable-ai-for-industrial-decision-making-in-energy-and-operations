from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from .._compat import dataclass
from .enums import (
    CanonicalFieldType,
    CanonicalSchemaRegistryStatus,
    CanonicalSchemaVersionStatus,
    CoercionSafetyLevel,
    ConversionRuleType,
    FieldLifecycleStatus,
    MeasurementFamily,
    ObservedValueType,
    RuleLifecycleStatus,
    SchemaProfileKind,
)
from .errors import DomainInvariantError
from .value_objects import (
    CanonicalFieldDefinitionId,
    CanonicalFieldName,
    CanonicalSchemaRegistryId,
    CanonicalSchemaVersionId,
    ConversionFactor,
    CurrencyCode,
    CurrencyConversionRuleId,
    CurrencyYear,
    FieldMappingRuleId,
    MappingContext,
    OriginalLabel,
    RuleDescription,
    RuleFingerprint,
    SchemaName,
    SourceFormatHint,
    SourcePathHint,
    TypeCoercionRuleId,
    UnitConversionRuleId,
    UnitRef,
    VersionFingerprint,
    VersionLabel,
    _ensure_unique,
    _require_text,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class CanonicalSchemaRegistry:
    canonical_schema_registry_id: CanonicalSchemaRegistryId
    schema_profile_kind: SchemaProfileKind
    schema_name: SchemaName
    registry_status: CanonicalSchemaRegistryStatus
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class CanonicalSchemaVersion:
    canonical_schema_version_id: CanonicalSchemaVersionId
    canonical_schema_registry_id: CanonicalSchemaRegistryId
    version_label: VersionLabel
    version_status: CanonicalSchemaVersionStatus
    version_fingerprint: VersionFingerprint
    created_at: datetime
    effective_from: datetime
    supersedes_canonical_schema_version_id: CanonicalSchemaVersionId | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        object.__setattr__(self, "effective_from", _require_timezone(self.effective_from, "effective_from"))
        if self.supersedes_canonical_schema_version_id == self.canonical_schema_version_id:
            raise DomainInvariantError(
                "supersedes_canonical_schema_version_id must not point to self."
            )


@dataclass(frozen=True, slots=True)
class CanonicalFieldDefinition:
    canonical_field_definition_id: CanonicalFieldDefinitionId
    canonical_schema_version_id: CanonicalSchemaVersionId
    canonical_field_name: CanonicalFieldName
    canonical_field_type: CanonicalFieldType
    field_status: FieldLifecycleStatus
    description: str
    measurement_family: MeasurementFamily | None
    canonical_unit: UnitRef | None
    allowed_units: tuple[UnitRef, ...]
    canonical_currency: CurrencyCode | None
    allowed_currencies: tuple[CurrencyCode, ...]
    allowed_enum_values: tuple[str, ...]
    required: bool
    allows_multiple: bool
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "description", _require_text(self.description, "description"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        normalized_enum_values = tuple(
            _require_text(item, "allowed_enum_value") for item in self.allowed_enum_values
        )
        object.__setattr__(self, "allowed_enum_values", normalized_enum_values)
        _ensure_unique(self.allowed_units, "allowed_units")
        _ensure_unique(self.allowed_currencies, "allowed_currencies")
        _ensure_unique(normalized_enum_values, "allowed_enum_values")
        if self.canonical_unit is not None:
            if self.measurement_family is None:
                raise DomainInvariantError(
                    "canonical_unit requires measurement_family to be declared."
                )
            if self.allowed_units and self.canonical_unit not in self.allowed_units:
                raise DomainInvariantError(
                    "canonical_unit must appear in allowed_units when allowed_units are declared."
                )
        if self.allowed_units and self.measurement_family is None:
            raise DomainInvariantError("allowed_units require measurement_family to be declared.")
        if self.canonical_field_type is CanonicalFieldType.ENUM_CONTROLLED and not normalized_enum_values:
            raise DomainInvariantError(
                "ENUM_CONTROLLED fields must declare allowed_enum_values."
            )
        if self.canonical_field_type is not CanonicalFieldType.ENUM_CONTROLLED and normalized_enum_values:
            raise DomainInvariantError(
                "allowed_enum_values are only valid for ENUM_CONTROLLED fields."
            )
        if self.canonical_field_type is CanonicalFieldType.MEASURE_WITH_UNIT:
            if self.measurement_family is None:
                raise DomainInvariantError(
                    "MEASURE_WITH_UNIT fields must declare measurement_family."
                )
        elif self.measurement_family is not None and self.canonical_field_type is not CanonicalFieldType.PERCENTAGE and self.canonical_field_type is not CanonicalFieldType.RATIO:
            if self.canonical_field_type is not CanonicalFieldType.MEASURE_WITH_UNIT:
                raise DomainInvariantError(
                    "measurement_family is only valid for MEASURE_WITH_UNIT, PERCENTAGE or RATIO fields."
                )
        if self.canonical_currency is not None:
            if self.canonical_field_type is not CanonicalFieldType.CURRENCY_AMOUNT:
                raise DomainInvariantError(
                    "canonical_currency is only valid for CURRENCY_AMOUNT fields."
                )
            if self.allowed_currencies and self.canonical_currency not in self.allowed_currencies:
                raise DomainInvariantError(
                    "canonical_currency must appear in allowed_currencies when allowed_currencies are declared."
                )
        if self.allowed_currencies and self.canonical_field_type is not CanonicalFieldType.CURRENCY_AMOUNT:
            raise DomainInvariantError(
                "allowed_currencies are only valid for CURRENCY_AMOUNT fields."
            )


@dataclass(frozen=True, slots=True)
class FieldMappingRule:
    field_mapping_rule_id: FieldMappingRuleId
    canonical_schema_version_id: CanonicalSchemaVersionId
    canonical_field_definition_id: CanonicalFieldDefinitionId
    rule_status: RuleLifecycleStatus
    original_label: OriginalLabel | None
    source_path_hint: SourcePathHint | None
    source_format_hint: SourceFormatHint | None
    required_unit_hint: UnitRef | None
    mapping_context: MappingContext | None
    rule_description: RuleDescription
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not any(
            (
                self.original_label is not None,
                self.source_path_hint is not None,
                self.source_format_hint is not None,
                self.required_unit_hint is not None,
                self.mapping_context is not None,
            )
        ):
            raise DomainInvariantError(
                "FieldMappingRule must declare at least one explicit mapping condition."
            )


@dataclass(frozen=True, slots=True)
class TypeCoercionRule:
    type_coercion_rule_id: TypeCoercionRuleId
    canonical_schema_version_id: CanonicalSchemaVersionId
    target_canonical_field_type: CanonicalFieldType
    coercion_safety_level: CoercionSafetyLevel
    rule_status: RuleLifecycleStatus
    rule_description: RuleDescription
    rule_fingerprint: RuleFingerprint
    allowed_input_types: tuple[ObservedValueType, ...]
    accepted_formats: tuple[str, ...]
    null_markers: tuple[str, ...]
    true_markers: tuple[str, ...]
    false_markers: tuple[str, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        normalized_formats = tuple(_require_text(item, "accepted_format") for item in self.accepted_formats)
        normalized_null_markers = tuple(item for item in self.null_markers)
        normalized_true_markers = tuple(item for item in self.true_markers)
        normalized_false_markers = tuple(item for item in self.false_markers)
        object.__setattr__(self, "accepted_formats", normalized_formats)
        object.__setattr__(self, "null_markers", normalized_null_markers)
        object.__setattr__(self, "true_markers", normalized_true_markers)
        object.__setattr__(self, "false_markers", normalized_false_markers)
        _ensure_unique(self.allowed_input_types, "allowed_input_types")
        _ensure_unique(normalized_formats, "accepted_formats")
        _ensure_unique(normalized_null_markers, "null_markers")
        _ensure_unique(normalized_true_markers, "true_markers")
        _ensure_unique(normalized_false_markers, "false_markers")
        if not any(
            (
                self.allowed_input_types,
                normalized_formats,
                normalized_null_markers,
                normalized_true_markers,
                normalized_false_markers,
            )
        ):
            raise DomainInvariantError(
                "TypeCoercionRule must declare at least one coercion constraint."
            )
        if self.target_canonical_field_type is CanonicalFieldType.BOOLEAN:
            if not normalized_true_markers or not normalized_false_markers:
                raise DomainInvariantError(
                    "Boolean coercion rules must declare true_markers and false_markers."
                )


@dataclass(frozen=True, slots=True)
class UnitConversionRule:
    unit_conversion_rule_id: UnitConversionRuleId
    canonical_schema_version_id: CanonicalSchemaVersionId
    measurement_family: MeasurementFamily
    source_unit: UnitRef
    target_unit: UnitRef
    conversion_rule_type: ConversionRuleType
    conversion_factor: ConversionFactor
    conversion_offset: Decimal | None
    rule_status: RuleLifecycleStatus
    rule_description: RuleDescription
    rule_fingerprint: RuleFingerprint
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.source_unit == self.target_unit:
            raise DomainInvariantError("UnitConversionRule must change units explicitly.")
        if self.conversion_rule_type not in {
            ConversionRuleType.FACTOR,
            ConversionRuleType.AFFINE,
        }:
            raise DomainInvariantError(
                "UnitConversionRule must use FACTOR or AFFINE conversion_rule_type."
            )
        if self.conversion_rule_type is ConversionRuleType.FACTOR and self.conversion_offset is not None:
            raise DomainInvariantError(
                "FACTOR unit conversion rules must not declare conversion_offset."
            )
        if self.conversion_rule_type is ConversionRuleType.AFFINE and self.conversion_offset is None:
            raise DomainInvariantError(
                "AFFINE unit conversion rules must declare conversion_offset."
            )


@dataclass(frozen=True, slots=True)
class CurrencyConversionRule:
    currency_conversion_rule_id: CurrencyConversionRuleId
    canonical_schema_version_id: CanonicalSchemaVersionId
    source_currency: CurrencyCode
    target_currency: CurrencyCode
    conversion_rule_type: ConversionRuleType
    conversion_factor: ConversionFactor | None
    basis_currency_year: CurrencyYear | None
    basis_reference: str | None
    rule_status: RuleLifecycleStatus
    rule_description: RuleDescription
    rule_fingerprint: RuleFingerprint
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.source_currency == self.target_currency:
            raise DomainInvariantError(
                "CurrencyConversionRule must change source_currency to target_currency."
            )
        if self.basis_reference is not None:
            object.__setattr__(
                self,
                "basis_reference",
                _require_text(self.basis_reference, "basis_reference"),
            )
        if self.conversion_rule_type not in {
            ConversionRuleType.DECLARED_RATE,
            ConversionRuleType.OFFICIAL_TABLE,
            ConversionRuleType.FIXED_POLICY_TABLE,
        }:
            raise DomainInvariantError(
                "CurrencyConversionRule must use a currency-compatible conversion_rule_type."
            )
        if not any(
            (
                self.conversion_factor is not None,
                self.basis_currency_year is not None,
                self.basis_reference is not None,
            )
        ):
            raise DomainInvariantError(
                "CurrencyConversionRule must declare explicit basis information."
            )
        if self.conversion_rule_type is ConversionRuleType.DECLARED_RATE and self.conversion_factor is None:
            raise DomainInvariantError(
                "DECLARED_RATE currency rules must declare conversion_factor."
            )
        if self.conversion_rule_type in {
            ConversionRuleType.OFFICIAL_TABLE,
            ConversionRuleType.FIXED_POLICY_TABLE,
        } and self.basis_reference is None:
            raise DomainInvariantError(
                "Table-based currency rules must declare basis_reference."
            )
