from __future__ import annotations

from decimal import Decimal
from enum import Enum

from .._compat import dataclass
from ..domain.entities import CanonicalFieldDefinition, CanonicalSchemaRegistry, CanonicalSchemaVersion
from ..domain.enums import (
    MissingnessStatus,
    MixedValueStatus,
    NormalizationStatus,
    PartialNormalizationStatus,
    RangeCheckResult,
    WarningSeverity,
)
from ..domain.records import (
    NonNormalizableFieldRecord,
    NormalizationReplayManifest,
    NormalizationRunRecord,
    NormalizationWarningRecord,
    NormalizedFieldRecord,
    NormalizedRecord,
    NormalizedRecordSet,
    PartialNormalizationRecord,
)
from ..domain.value_objects import (
    NonNormalizableReason,
    PrecisionDescriptor,
    TypeCoercionRuleId,
)


class FieldMappingStatus(str, Enum):
    MATCHED = "matched"
    NO_MATCH = "no_match"
    CONTEXT_INSUFFICIENT = "context_insufficient"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class WarningDraft:
    code: str
    severity: WarningSeverity
    message: str


@dataclass(frozen=True, slots=True)
class FieldMappingResult:
    status: FieldMappingStatus
    canonical_field_definition: CanonicalFieldDefinition | None
    field_mapping_rule_id: object | None
    warning_drafts: tuple[WarningDraft, ...]
    non_normalizable_reason: NonNormalizableReason | None


@dataclass(frozen=True, slots=True)
class TypeCoercionResult:
    normalization_status: NormalizationStatus
    partial_normalization_status: PartialNormalizationStatus
    normalized_value_text: str | None
    numeric_value: Decimal | None
    precision_descriptor: PrecisionDescriptor
    missingness_status: MissingnessStatus
    mixed_value_status: MixedValueStatus
    range_check_result: RangeCheckResult
    warning_drafts: tuple[WarningDraft, ...]
    non_normalizable_reason: NonNormalizableReason | None
    type_coercion_rule_id: TypeCoercionRuleId | None


@dataclass(frozen=True, slots=True)
class UnitConversionResult:
    normalization_status: NormalizationStatus
    partial_normalization_status: PartialNormalizationStatus
    normalized_value_text: str | None
    normalized_unit: object | None
    unit_conversion_rule_id: object | None
    warning_drafts: tuple[WarningDraft, ...]
    non_normalizable_reason: NonNormalizableReason | None


@dataclass(frozen=True, slots=True)
class CurrencyConversionResult:
    normalization_status: NormalizationStatus
    partial_normalization_status: PartialNormalizationStatus
    normalized_value_text: str | None
    normalized_currency: object | None
    currency_conversion_rule_id: object | None
    warning_drafts: tuple[WarningDraft, ...]
    non_normalizable_reason: NonNormalizableReason | None


@dataclass(frozen=True, slots=True)
class NormalizationExecutionResult:
    canonical_schema_version: CanonicalSchemaVersion
    normalization_run_record: NormalizationRunRecord
    normalized_record_set: NormalizedRecordSet | None
    normalized_record: NormalizedRecord | None
    normalized_field_records: tuple[NormalizedFieldRecord, ...]
    normalization_warning_records: tuple[NormalizationWarningRecord, ...]
    non_normalizable_field_records: tuple[NonNormalizableFieldRecord, ...]
    partial_normalization_record: PartialNormalizationRecord | None
    normalization_replay_manifest: NormalizationReplayManifest | None

    @property
    def has_warnings(self) -> bool:
        return bool(self.normalization_warning_records)

    @property
    def is_partial(self) -> bool:
        return self.partial_normalization_record is not None

    @property
    def is_non_normalizable(self) -> bool:
        return (
            self.normalization_run_record.normalization_status
            is NormalizationStatus.NON_NORMALIZABLE
        )

    def as_validation_graph(
        self,
        *,
        canonical_schema_registry: CanonicalSchemaRegistry,
        canonical_field_definitions: tuple[CanonicalFieldDefinition, ...],
        field_mapping_rules: tuple[object, ...] = (),
        type_coercion_rules: tuple[object, ...] = (),
        unit_conversion_rules: tuple[object, ...] = (),
        currency_conversion_rules: tuple[object, ...] = (),
    ) -> dict[str, object]:
        return {
            "canonical_schema_registries": (canonical_schema_registry,),
            "canonical_schema_versions": (self.canonical_schema_version,),
            "canonical_field_definitions": canonical_field_definitions,
            "field_mapping_rules": field_mapping_rules,
            "type_coercion_rules": type_coercion_rules,
            "unit_conversion_rules": unit_conversion_rules,
            "currency_conversion_rules": currency_conversion_rules,
            "normalized_field_records": self.normalized_field_records,
            "normalized_records": ()
            if self.normalized_record is None
            else (self.normalized_record,),
            "normalized_record_sets": ()
            if self.normalized_record_set is None
            else (self.normalized_record_set,),
            "normalization_warning_records": self.normalization_warning_records,
            "non_normalizable_field_records": self.non_normalizable_field_records,
            "partial_normalization_records": ()
            if self.partial_normalization_record is None
            else (self.partial_normalization_record,),
            "normalization_run_records": (self.normalization_run_record,),
            "normalization_replay_manifests": ()
            if self.normalization_replay_manifest is None
            else (self.normalization_replay_manifest,),
        }
