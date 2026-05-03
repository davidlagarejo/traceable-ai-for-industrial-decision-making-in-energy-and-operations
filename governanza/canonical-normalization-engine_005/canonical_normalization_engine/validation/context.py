from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .._compat import dataclass
from ..domain.entities import (
    CanonicalFieldDefinition,
    CanonicalSchemaRegistry,
    CanonicalSchemaVersion,
    CurrencyConversionRule,
    FieldMappingRule,
    TypeCoercionRule,
    UnitConversionRule,
)
from ..domain.enums import NormalizationScopeKind
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
    CanonicalFieldDefinitionId,
    CanonicalSchemaRegistryId,
    CanonicalSchemaVersionId,
    CurrencyConversionRuleId,
    FieldMappingRuleId,
    NonNormalizableFieldRecordId,
    NormalizationScopeRef,
    NormalizationRunRecordId,
    NormalizationWarningRecordId,
    NormalizedFieldRecordId,
    NormalizedRecordId,
    NormalizedRecordSetId,
    PartialNormalizationRecordId,
    TypeCoercionRuleId,
    UnitConversionRuleId,
)


@dataclass(frozen=True, slots=True)
class ValidationContext:
    canonical_schema_registries: tuple[CanonicalSchemaRegistry, ...] = ()
    canonical_schema_versions: tuple[CanonicalSchemaVersion, ...] = ()
    canonical_field_definitions: tuple[CanonicalFieldDefinition, ...] = ()
    field_mapping_rules: tuple[FieldMappingRule, ...] = ()
    type_coercion_rules: tuple[TypeCoercionRule, ...] = ()
    unit_conversion_rules: tuple[UnitConversionRule, ...] = ()
    currency_conversion_rules: tuple[CurrencyConversionRule, ...] = ()
    normalized_field_records: tuple[NormalizedFieldRecord, ...] = ()
    normalized_records: tuple[NormalizedRecord, ...] = ()
    normalized_record_sets: tuple[NormalizedRecordSet, ...] = ()
    normalization_warning_records: tuple[NormalizationWarningRecord, ...] = ()
    non_normalizable_field_records: tuple[NonNormalizableFieldRecord, ...] = ()
    partial_normalization_records: tuple[PartialNormalizationRecord, ...] = ()
    normalization_run_records: tuple[NormalizationRunRecord, ...] = ()
    normalization_replay_manifests: tuple[NormalizationReplayManifest, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        canonical_schema_registries: Iterable[CanonicalSchemaRegistry] = (),
        canonical_schema_versions: Iterable[CanonicalSchemaVersion] = (),
        canonical_field_definitions: Iterable[CanonicalFieldDefinition] = (),
        field_mapping_rules: Iterable[FieldMappingRule] = (),
        type_coercion_rules: Iterable[TypeCoercionRule] = (),
        unit_conversion_rules: Iterable[UnitConversionRule] = (),
        currency_conversion_rules: Iterable[CurrencyConversionRule] = (),
        normalized_field_records: Iterable[NormalizedFieldRecord] = (),
        normalized_records: Iterable[NormalizedRecord] = (),
        normalized_record_sets: Iterable[NormalizedRecordSet] = (),
        normalization_warning_records: Iterable[NormalizationWarningRecord] = (),
        non_normalizable_field_records: Iterable[NonNormalizableFieldRecord] = (),
        partial_normalization_records: Iterable[PartialNormalizationRecord] = (),
        normalization_run_records: Iterable[NormalizationRunRecord] = (),
        normalization_replay_manifests: Iterable[NormalizationReplayManifest] = (),
    ) -> "ValidationContext":
        return cls(
            canonical_schema_registries=tuple(canonical_schema_registries),
            canonical_schema_versions=tuple(canonical_schema_versions),
            canonical_field_definitions=tuple(canonical_field_definitions),
            field_mapping_rules=tuple(field_mapping_rules),
            type_coercion_rules=tuple(type_coercion_rules),
            unit_conversion_rules=tuple(unit_conversion_rules),
            currency_conversion_rules=tuple(currency_conversion_rules),
            normalized_field_records=tuple(normalized_field_records),
            normalized_records=tuple(normalized_records),
            normalized_record_sets=tuple(normalized_record_sets),
            normalization_warning_records=tuple(normalization_warning_records),
            non_normalizable_field_records=tuple(non_normalizable_field_records),
            partial_normalization_records=tuple(partial_normalization_records),
            normalization_run_records=tuple(normalization_run_records),
            normalization_replay_manifests=tuple(normalization_replay_manifests),
        )

    @property
    def registries_by_id(self) -> dict[CanonicalSchemaRegistryId, CanonicalSchemaRegistry]:
        return {
            item.canonical_schema_registry_id: item
            for item in self.canonical_schema_registries
        }

    @property
    def versions_by_id(self) -> dict[CanonicalSchemaVersionId, CanonicalSchemaVersion]:
        return {
            item.canonical_schema_version_id: item
            for item in self.canonical_schema_versions
        }

    @property
    def fields_by_id(self) -> dict[CanonicalFieldDefinitionId, CanonicalFieldDefinition]:
        return {
            item.canonical_field_definition_id: item
            for item in self.canonical_field_definitions
        }

    @property
    def mapping_rules_by_id(self) -> dict[FieldMappingRuleId, FieldMappingRule]:
        return {item.field_mapping_rule_id: item for item in self.field_mapping_rules}

    @property
    def coercion_rules_by_id(self) -> dict[TypeCoercionRuleId, TypeCoercionRule]:
        return {item.type_coercion_rule_id: item for item in self.type_coercion_rules}

    @property
    def unit_rules_by_id(self) -> dict[UnitConversionRuleId, UnitConversionRule]:
        return {item.unit_conversion_rule_id: item for item in self.unit_conversion_rules}

    @property
    def currency_rules_by_id(self) -> dict[CurrencyConversionRuleId, CurrencyConversionRule]:
        return {
            item.currency_conversion_rule_id: item
            for item in self.currency_conversion_rules
        }

    @property
    def runs_by_id(self) -> dict[NormalizationRunRecordId, NormalizationRunRecord]:
        return {item.normalization_run_record_id: item for item in self.normalization_run_records}

    @property
    def normalized_fields_by_id(self) -> dict[NormalizedFieldRecordId, NormalizedFieldRecord]:
        return {
            item.normalized_field_record_id: item
            for item in self.normalized_field_records
        }

    @property
    def normalized_records_by_id(self) -> dict[NormalizedRecordId, NormalizedRecord]:
        return {item.normalized_record_id: item for item in self.normalized_records}

    @property
    def normalized_record_sets_by_id(self) -> dict[NormalizedRecordSetId, NormalizedRecordSet]:
        return {
            item.normalized_record_set_id: item
            for item in self.normalized_record_sets
        }

    @property
    def warnings_by_id(self) -> dict[NormalizationWarningRecordId, NormalizationWarningRecord]:
        return {
            item.normalization_warning_record_id: item
            for item in self.normalization_warning_records
        }

    @property
    def non_normalizable_by_id(self) -> dict[NonNormalizableFieldRecordId, NonNormalizableFieldRecord]:
        return {
            item.non_normalizable_field_record_id: item
            for item in self.non_normalizable_field_records
        }

    @property
    def partials_by_id(self) -> dict[PartialNormalizationRecordId, PartialNormalizationRecord]:
        return {
            item.partial_normalization_record_id: item
            for item in self.partial_normalization_records
        }

    def contains_scope_ref(self, scope_ref: NormalizationScopeRef) -> bool:
        return self.object_for_scope(scope_ref) is not None

    def object_for_scope(self, scope_ref: NormalizationScopeRef) -> Any | None:
        if scope_ref.scope_kind is NormalizationScopeKind.NORMALIZATION_RUN:
            return self._runs_by_scope_id().get(scope_ref.identifier)
        if scope_ref.scope_kind is NormalizationScopeKind.NORMALIZED_RECORD_SET:
            return self._record_sets_by_scope_id().get(scope_ref.identifier)
        if scope_ref.scope_kind is NormalizationScopeKind.NORMALIZED_RECORD:
            return self._records_by_scope_id().get(scope_ref.identifier)
        if scope_ref.scope_kind is NormalizationScopeKind.NORMALIZED_FIELD:
            return self._fields_by_scope_id().get(scope_ref.identifier)
        if scope_ref.scope_kind is NormalizationScopeKind.NON_NORMALIZABLE_FIELD:
            return self._non_normalizable_by_scope_id().get(scope_ref.identifier)
        return self._partials_by_scope_id().get(scope_ref.identifier)

    def run_id_for_scope(self, scope_ref: NormalizationScopeRef) -> NormalizationRunRecordId | None:
        item = self.object_for_scope(scope_ref)
        if item is None:
            return None
        if scope_ref.scope_kind is NormalizationScopeKind.NORMALIZATION_RUN:
            return item.normalization_run_record_id
        return item.normalization_run_record_id

    def _runs_by_scope_id(self) -> dict[str, NormalizationRunRecord]:
        return {
            item.normalization_run_record_id.value: item
            for item in self.normalization_run_records
        }

    def _record_sets_by_scope_id(self) -> dict[str, NormalizedRecordSet]:
        return {
            item.normalized_record_set_id.value: item
            for item in self.normalized_record_sets
        }

    def _records_by_scope_id(self) -> dict[str, NormalizedRecord]:
        return {
            item.normalized_record_id.value: item
            for item in self.normalized_records
        }

    def _fields_by_scope_id(self) -> dict[str, NormalizedFieldRecord]:
        return {
            item.normalized_field_record_id.value: item
            for item in self.normalized_field_records
        }

    def _non_normalizable_by_scope_id(self) -> dict[str, NonNormalizableFieldRecord]:
        return {
            item.non_normalizable_field_record_id.value: item
            for item in self.non_normalizable_field_records
        }

    def _partials_by_scope_id(self) -> dict[str, PartialNormalizationRecord]:
        return {
            item.partial_normalization_record_id.value: item
            for item in self.partial_normalization_records
        }
