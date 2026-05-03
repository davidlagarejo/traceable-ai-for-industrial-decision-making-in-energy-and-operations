from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    MissingnessStatus,
    MixedValueStatus,
    NormalizationStatus,
    PartialNormalizationStatus,
    RangeCheckResult,
    ReplayabilityStatus,
    WarningSeverity,
)
from .errors import DomainInvariantError
from .value_objects import (
    CanonicalFieldDefinitionId,
    CanonicalSchemaRegistryId,
    CanonicalSchemaVersionId,
    CurrencyCode,
    CurrencyConversionRuleId,
    FieldMappingRuleId,
    NonNormalizableFieldRecordId,
    NonNormalizableReason,
    NormalizationReplayManifestId,
    NormalizationRunRecordId,
    NormalizationScopeRef,
    NormalizationWarningRecordId,
    NormalizedFieldRecordId,
    NormalizedRecordId,
    NormalizedRecordSetId,
    OriginalLabel,
    ParsedSourceProvenance,
    PartialNormalizationRecordId,
    PrecisionDescriptor,
    RecordKey,
    TypeCoercionRuleId,
    UnitConversionRuleId,
    UnitRef,
    ValueTriplet,
    WarningCode,
    _ensure_unique,
    _require_timezone,
)
from .entities import CanonicalFieldDefinition, CanonicalSchemaVersion
from .enums import CanonicalFieldType


def _validate_partial_state(
    normalization_status: NormalizationStatus,
    partial_normalization_status: PartialNormalizationStatus,
    *,
    allow_failed: bool,
) -> None:
    if normalization_status is NormalizationStatus.COMPLETE and partial_normalization_status is not PartialNormalizationStatus.NOT_PARTIAL:
        raise DomainInvariantError(
            "Complete normalization status must not declare a partial normalization status."
        )
    if normalization_status is NormalizationStatus.PARTIAL and partial_normalization_status is PartialNormalizationStatus.NOT_PARTIAL:
        raise DomainInvariantError(
            "Partial normalization status must declare a partial normalization status."
        )
    if normalization_status is NormalizationStatus.NON_NORMALIZABLE and partial_normalization_status is not PartialNormalizationStatus.NOT_PARTIAL:
        raise DomainInvariantError(
            "Non-normalizable status must not declare a partial normalization status."
        )
    if normalization_status is NormalizationStatus.FAILED:
        if not allow_failed:
            raise DomainInvariantError("This record must not declare FAILED normalization status.")
        if partial_normalization_status is not PartialNormalizationStatus.NOT_PARTIAL:
            raise DomainInvariantError(
                "Failed normalization status must not declare a partial normalization status."
            )


@dataclass(frozen=True, slots=True)
class NormalizationRunRecord:
    normalization_run_record_id: NormalizationRunRecordId
    canonical_schema_registry_id: CanonicalSchemaRegistryId
    canonical_schema_version_id: CanonicalSchemaVersionId
    source_provenance: ParsedSourceProvenance
    normalization_status: NormalizationStatus
    replayability_status: ReplayabilityStatus
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

    @classmethod
    def for_schema_version(
        cls,
        *,
        normalization_run_record_id: NormalizationRunRecordId,
        schema_version: CanonicalSchemaVersion,
        source_provenance: ParsedSourceProvenance,
        normalization_status: NormalizationStatus,
        replayability_status: ReplayabilityStatus,
        created_at: datetime,
    ) -> "NormalizationRunRecord":
        return cls(
            normalization_run_record_id=normalization_run_record_id,
            canonical_schema_registry_id=schema_version.canonical_schema_registry_id,
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            source_provenance=source_provenance,
            normalization_status=normalization_status,
            replayability_status=replayability_status,
            created_at=created_at,
        )


@dataclass(frozen=True, slots=True)
class NormalizedFieldRecord:
    normalized_field_record_id: NormalizedFieldRecordId
    normalization_run_record_id: NormalizationRunRecordId
    normalized_record_id: NormalizedRecordId | None
    canonical_field_definition_id: CanonicalFieldDefinitionId | None
    source_provenance: ParsedSourceProvenance
    original_label: OriginalLabel
    value_triplet: ValueTriplet
    normalized_field_type: CanonicalFieldType | None
    original_unit: UnitRef | None
    normalized_unit: UnitRef | None
    original_currency: CurrencyCode | None
    normalized_currency: CurrencyCode | None
    precision_descriptor: PrecisionDescriptor
    missingness_status: MissingnessStatus
    mixed_value_status: MixedValueStatus
    range_check_result: RangeCheckResult
    normalization_status: NormalizationStatus
    field_mapping_rule_id: FieldMappingRuleId | None
    type_coercion_rule_id: TypeCoercionRuleId | None
    unit_conversion_rule_id: UnitConversionRuleId | None
    currency_conversion_rule_id: CurrencyConversionRuleId | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.source_provenance.parsed_field_object_ref is None:
            raise DomainInvariantError(
                "NormalizedFieldRecord requires parsed_field_object_ref in source_provenance."
            )
        if (
            self.canonical_field_definition_id is None
            and self.normalization_status is not NormalizationStatus.NON_NORMALIZABLE
        ):
            raise DomainInvariantError(
                "NormalizedFieldRecord requires canonical_field_definition_id unless status is NON_NORMALIZABLE."
            )
        if self.normalization_status is NormalizationStatus.COMPLETE:
            if not self.value_triplet.has_normalized_value and self.missingness_status is MissingnessStatus.NOT_MISSING:
                raise DomainInvariantError(
                    "Complete normalized fields must declare normalized_value unless missingness is explicit."
                )
            if self.normalized_field_type is None:
                raise DomainInvariantError(
                    "Complete normalized fields must declare normalized_field_type."
                )
            if self.field_mapping_rule_id is None:
                raise DomainInvariantError(
                    "Complete normalized fields must declare field_mapping_rule_id."
                )
        if self.normalization_status is NormalizationStatus.NON_NORMALIZABLE:
            if self.value_triplet.has_normalized_value:
                raise DomainInvariantError(
                    "Non-normalizable fields must not declare normalized_value."
                )
        if self.original_unit is not None and self.normalized_unit is None and self.normalization_status is NormalizationStatus.COMPLETE:
            raise DomainInvariantError(
                "NormalizedFieldRecord must preserve normalized_unit when original_unit exists on complete normalization."
            )
        if (
            self.original_unit is not None
            and self.normalized_unit is not None
            and self.original_unit != self.normalized_unit
            and self.unit_conversion_rule_id is None
        ):
            raise DomainInvariantError("Unit changes require explicit unit_conversion_rule_id.")
        if self.original_currency is not None and self.normalized_currency is None and self.normalization_status is NormalizationStatus.COMPLETE:
            raise DomainInvariantError(
                "NormalizedFieldRecord must preserve normalized_currency when original_currency exists on complete normalization."
            )
        if (
            self.original_currency is not None
            and self.normalized_currency is not None
            and self.original_currency != self.normalized_currency
            and self.currency_conversion_rule_id is None
        ):
            raise DomainInvariantError(
                "Currency changes require explicit currency_conversion_rule_id."
            )

    @classmethod
    def for_canonical_field(
        cls,
        *,
        normalized_field_record_id: NormalizedFieldRecordId,
        normalization_run_record_id: NormalizationRunRecordId,
        normalized_record_id: NormalizedRecordId | None,
        canonical_field_definition: CanonicalFieldDefinition,
        source_provenance: ParsedSourceProvenance,
        original_label: OriginalLabel,
        value_triplet: ValueTriplet,
        original_unit: UnitRef | None,
        normalized_unit: UnitRef | None,
        original_currency: CurrencyCode | None,
        normalized_currency: CurrencyCode | None,
        precision_descriptor: PrecisionDescriptor,
        missingness_status: MissingnessStatus,
        mixed_value_status: MixedValueStatus,
        range_check_result: RangeCheckResult,
        normalization_status: NormalizationStatus,
        field_mapping_rule_id: FieldMappingRuleId | None,
        type_coercion_rule_id: TypeCoercionRuleId | None,
        unit_conversion_rule_id: UnitConversionRuleId | None,
        currency_conversion_rule_id: CurrencyConversionRuleId | None,
        created_at: datetime,
    ) -> "NormalizedFieldRecord":
        return cls(
            normalized_field_record_id=normalized_field_record_id,
            normalization_run_record_id=normalization_run_record_id,
            normalized_record_id=normalized_record_id,
            canonical_field_definition_id=canonical_field_definition.canonical_field_definition_id,
            source_provenance=source_provenance,
            original_label=original_label,
            value_triplet=value_triplet,
            normalized_field_type=canonical_field_definition.canonical_field_type,
            original_unit=original_unit,
            normalized_unit=normalized_unit,
            original_currency=original_currency,
            normalized_currency=normalized_currency,
            precision_descriptor=precision_descriptor,
            missingness_status=missingness_status,
            mixed_value_status=mixed_value_status,
            range_check_result=range_check_result,
            normalization_status=normalization_status,
            field_mapping_rule_id=field_mapping_rule_id,
            type_coercion_rule_id=type_coercion_rule_id,
            unit_conversion_rule_id=unit_conversion_rule_id,
            currency_conversion_rule_id=currency_conversion_rule_id,
            created_at=created_at,
        )


@dataclass(frozen=True, slots=True)
class NormalizedRecord:
    normalized_record_id: NormalizedRecordId
    normalized_record_set_id: NormalizedRecordSetId
    normalization_run_record_id: NormalizationRunRecordId
    source_provenance: ParsedSourceProvenance
    record_key: RecordKey
    normalization_status: NormalizationStatus
    normalized_field_record_ids: tuple[NormalizedFieldRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.normalized_field_record_ids:
            raise DomainInvariantError(
                "NormalizedRecord.normalized_field_record_ids must not be empty."
            )
        _ensure_unique(self.normalized_field_record_ids, "normalized_field_record_ids")


@dataclass(frozen=True, slots=True)
class NormalizedRecordSet:
    normalized_record_set_id: NormalizedRecordSetId
    normalization_run_record_id: NormalizationRunRecordId
    canonical_schema_version_id: CanonicalSchemaVersionId
    normalization_status: NormalizationStatus
    normalized_record_ids: tuple[NormalizedRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.normalized_record_ids:
            raise DomainInvariantError(
                "NormalizedRecordSet.normalized_record_ids must not be empty."
            )
        _ensure_unique(self.normalized_record_ids, "normalized_record_ids")


@dataclass(frozen=True, slots=True)
class NormalizationWarningRecord:
    normalization_warning_record_id: NormalizationWarningRecordId
    normalization_run_record_id: NormalizationRunRecordId
    scope_ref: NormalizationScopeRef
    warning_code: WarningCode
    warning_severity: WarningSeverity
    message: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise DomainInvariantError(
                "NormalizationWarningRecord.message must be non-empty."
            )
        object.__setattr__(self, "message", self.message.strip())
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class NonNormalizableFieldRecord:
    non_normalizable_field_record_id: NonNormalizableFieldRecordId
    normalization_run_record_id: NormalizationRunRecordId
    source_provenance: ParsedSourceProvenance
    original_label: OriginalLabel
    value_triplet: ValueTriplet
    candidate_canonical_field_definition_id: CanonicalFieldDefinitionId | None
    field_mapping_rule_id: FieldMappingRuleId | None
    original_unit: UnitRef | None
    original_currency: CurrencyCode | None
    missingness_status: MissingnessStatus
    mixed_value_status: MixedValueStatus
    reason: NonNormalizableReason
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.source_provenance.parsed_field_object_ref is None:
            raise DomainInvariantError(
                "NonNormalizableFieldRecord requires parsed_field_object_ref in source_provenance."
            )
        if self.value_triplet.has_normalized_value:
            raise DomainInvariantError(
                "NonNormalizableFieldRecord must not declare normalized_value."
            )


@dataclass(frozen=True, slots=True)
class PartialNormalizationRecord:
    partial_normalization_record_id: PartialNormalizationRecordId
    normalization_run_record_id: NormalizationRunRecordId
    normalization_status: NormalizationStatus
    partial_normalization_status: PartialNormalizationStatus
    normalized_field_record_ids: tuple[NormalizedFieldRecordId, ...]
    non_normalizable_field_record_ids: tuple[NonNormalizableFieldRecordId, ...]
    rationale: NonNormalizableReason
    created_at: datetime

    def __post_init__(self) -> None:
        _validate_partial_state(
            self.normalization_status,
            self.partial_normalization_status,
            allow_failed=False,
        )
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.normalization_status is not NormalizationStatus.PARTIAL:
            raise DomainInvariantError(
                "PartialNormalizationRecord must declare PARTIAL normalization_status."
            )
        if not (self.normalized_field_record_ids or self.non_normalizable_field_record_ids):
            raise DomainInvariantError(
                "PartialNormalizationRecord must reference normalized or non-normalizable fields."
            )
        _ensure_unique(self.normalized_field_record_ids, "normalized_field_record_ids")
        _ensure_unique(
            self.non_normalizable_field_record_ids,
            "non_normalizable_field_record_ids",
        )


@dataclass(frozen=True, slots=True)
class NormalizationReplayManifest:
    normalization_replay_manifest_id: NormalizationReplayManifestId
    normalization_run_record_id: NormalizationRunRecordId
    canonical_schema_version_id: CanonicalSchemaVersionId
    source_provenance: ParsedSourceProvenance
    field_mapping_rule_ids: tuple[FieldMappingRuleId, ...]
    type_coercion_rule_ids: tuple[TypeCoercionRuleId, ...]
    unit_conversion_rule_ids: tuple[UnitConversionRuleId, ...]
    currency_conversion_rule_ids: tuple[CurrencyConversionRuleId, ...]
    normalized_record_set_id: NormalizedRecordSetId | None
    replayability_status: ReplayabilityStatus
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.field_mapping_rule_ids, "field_mapping_rule_ids")
        _ensure_unique(self.type_coercion_rule_ids, "type_coercion_rule_ids")
        _ensure_unique(self.unit_conversion_rule_ids, "unit_conversion_rule_ids")
        _ensure_unique(
            self.currency_conversion_rule_ids,
            "currency_conversion_rule_ids",
        )
        if not any(
            (
                self.field_mapping_rule_ids,
                self.type_coercion_rule_ids,
                self.unit_conversion_rule_ids,
                self.currency_conversion_rule_ids,
            )
        ):
            raise DomainInvariantError(
                "NormalizationReplayManifest must reference the effective rules used."
            )
