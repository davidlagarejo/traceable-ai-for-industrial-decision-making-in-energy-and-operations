from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

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
from .collector import ViolationCollector, ViolationDraft
from .context import ValidationContext
from .normalized_validator import (
    validate_normalized_field_record,
    validate_normalized_record,
    validate_normalized_record_set,
)
from .replay_validator import validate_normalization_replay_manifest
from .results import ValidationOutcome, ValidationReport, ValidationRun, ValidationViolation
from .rule_validator import (
    validate_currency_conversion_rule,
    validate_field_mapping_rule,
    validate_type_coercion_rule,
    validate_unit_conversion_rule,
)
from .run_validator import validate_normalization_run_record
from .schema_validator import (
    validate_canonical_field_definition,
    validate_canonical_schema_registry,
    validate_canonical_schema_version,
)
from .warning_validator import (
    validate_non_normalizable_field_record,
    validate_normalization_warning_record,
    validate_partial_normalization_record,
)


DEFAULT_VALIDATOR_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    target_refs: tuple[str, ...]


class BasicNormalizationIntegrityValidator:
    def __init__(
        self,
        *,
        validator_version: str = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_canonical_schema_registry(
        self,
        registry: CanonicalSchemaRegistry,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_registry_ref(registry))
        validate_canonical_schema_registry(registry, collector)
        return self._build_report(ValidationArtifacts((_registry_ref(registry),)), collector)

    def validate_canonical_schema_version(
        self,
        schema_version: CanonicalSchemaVersion,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_schema_version_ref(schema_version))
        validate_canonical_schema_version(schema_version, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_schema_version_ref(schema_version),)),
            collector,
        )

    def validate_canonical_field_definition(
        self,
        field_definition: CanonicalFieldDefinition,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_field_definition_ref(field_definition))
        validate_canonical_field_definition(field_definition, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_field_definition_ref(field_definition),)),
            collector,
        )

    def validate_field_mapping_rule(
        self,
        mapping_rule: FieldMappingRule,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_mapping_rule_ref(mapping_rule))
        validate_field_mapping_rule(mapping_rule, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_mapping_rule_ref(mapping_rule),)),
            collector,
        )

    def validate_type_coercion_rule(
        self,
        coercion_rule: TypeCoercionRule,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_coercion_rule_ref(coercion_rule))
        validate_type_coercion_rule(coercion_rule, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_coercion_rule_ref(coercion_rule),)),
            collector,
        )

    def validate_unit_conversion_rule(
        self,
        unit_rule: UnitConversionRule,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_unit_rule_ref(unit_rule))
        validate_unit_conversion_rule(unit_rule, collector, context=context)
        return self._build_report(ValidationArtifacts((_unit_rule_ref(unit_rule),)), collector)

    def validate_currency_conversion_rule(
        self,
        currency_rule: CurrencyConversionRule,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_currency_rule_ref(currency_rule))
        validate_currency_conversion_rule(currency_rule, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_currency_rule_ref(currency_rule),)),
            collector,
        )

    def validate_normalized_field_record(
        self,
        normalized_field: NormalizedFieldRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_normalized_field_ref(normalized_field))
        validate_normalized_field_record(normalized_field, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_normalized_field_ref(normalized_field),)),
            collector,
        )

    def validate_normalized_record(
        self,
        normalized_record: NormalizedRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_normalized_record_ref(normalized_record))
        validate_normalized_record(normalized_record, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_normalized_record_ref(normalized_record),)),
            collector,
        )

    def validate_normalized_record_set(
        self,
        record_set: NormalizedRecordSet,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_record_set_ref(record_set))
        validate_normalized_record_set(record_set, collector, context=context)
        return self._build_report(ValidationArtifacts((_record_set_ref(record_set),)), collector)

    def validate_normalization_warning_record(
        self,
        warning: NormalizationWarningRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_warning_ref(warning))
        validate_normalization_warning_record(warning, collector, context=context)
        return self._build_report(ValidationArtifacts((_warning_ref(warning),)), collector)

    def validate_non_normalizable_field_record(
        self,
        non_normalizable_field: NonNormalizableFieldRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_non_normalizable_ref(non_normalizable_field))
        validate_non_normalizable_field_record(non_normalizable_field, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_non_normalizable_ref(non_normalizable_field),)),
            collector,
        )

    def validate_partial_normalization_record(
        self,
        partial_record: PartialNormalizationRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_partial_ref(partial_record))
        validate_partial_normalization_record(partial_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_partial_ref(partial_record),)), collector)

    def validate_normalization_run_record(
        self,
        normalization_run: NormalizationRunRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_run_ref(normalization_run))
        validate_normalization_run_record(normalization_run, collector, context=context)
        return self._build_report(ValidationArtifacts((_run_ref(normalization_run),)), collector)

    def validate_normalization_replay_manifest(
        self,
        replay_manifest: NormalizationReplayManifest,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_replay_ref(replay_manifest))
        validate_normalization_replay_manifest(replay_manifest, collector, context=context)
        return self._build_report(ValidationArtifacts((_replay_ref(replay_manifest),)), collector)

    def validate_graph(
        self,
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
    ) -> ValidationReport:
        canonical_schema_registries = tuple(canonical_schema_registries)
        canonical_schema_versions = tuple(canonical_schema_versions)
        canonical_field_definitions = tuple(canonical_field_definitions)
        field_mapping_rules = tuple(field_mapping_rules)
        type_coercion_rules = tuple(type_coercion_rules)
        unit_conversion_rules = tuple(unit_conversion_rules)
        currency_conversion_rules = tuple(currency_conversion_rules)
        normalized_field_records = tuple(normalized_field_records)
        normalized_records = tuple(normalized_records)
        normalized_record_sets = tuple(normalized_record_sets)
        normalization_warning_records = tuple(normalization_warning_records)
        non_normalizable_field_records = tuple(non_normalizable_field_records)
        partial_normalization_records = tuple(partial_normalization_records)
        normalization_run_records = tuple(normalization_run_records)
        normalization_replay_manifests = tuple(normalization_replay_manifests)

        context = ValidationContext.from_iterables(
            canonical_schema_registries=canonical_schema_registries,
            canonical_schema_versions=canonical_schema_versions,
            canonical_field_definitions=canonical_field_definitions,
            field_mapping_rules=field_mapping_rules,
            type_coercion_rules=type_coercion_rules,
            unit_conversion_rules=unit_conversion_rules,
            currency_conversion_rules=currency_conversion_rules,
            normalized_field_records=normalized_field_records,
            normalized_records=normalized_records,
            normalized_record_sets=normalized_record_sets,
            normalization_warning_records=normalization_warning_records,
            non_normalizable_field_records=non_normalizable_field_records,
            partial_normalization_records=partial_normalization_records,
            normalization_run_records=normalization_run_records,
            normalization_replay_manifests=normalization_replay_manifests,
        )
        collector = ViolationCollector("graph:canonical_normalization")

        for item in canonical_schema_registries:
            local = ViolationCollector(_registry_ref(item))
            validate_canonical_schema_registry(item, local)
            _merge_collector(collector, local)

        for item in canonical_schema_versions:
            local = ViolationCollector(_schema_version_ref(item))
            validate_canonical_schema_version(item, local, context=context)
            _merge_collector(collector, local)

        for item in canonical_field_definitions:
            local = ViolationCollector(_field_definition_ref(item))
            validate_canonical_field_definition(item, local, context=context)
            _merge_collector(collector, local)

        for item in field_mapping_rules:
            local = ViolationCollector(_mapping_rule_ref(item))
            validate_field_mapping_rule(item, local, context=context)
            _merge_collector(collector, local)

        for item in type_coercion_rules:
            local = ViolationCollector(_coercion_rule_ref(item))
            validate_type_coercion_rule(item, local, context=context)
            _merge_collector(collector, local)

        for item in unit_conversion_rules:
            local = ViolationCollector(_unit_rule_ref(item))
            validate_unit_conversion_rule(item, local, context=context)
            _merge_collector(collector, local)

        for item in currency_conversion_rules:
            local = ViolationCollector(_currency_rule_ref(item))
            validate_currency_conversion_rule(item, local, context=context)
            _merge_collector(collector, local)

        for item in normalization_run_records:
            local = ViolationCollector(_run_ref(item))
            validate_normalization_run_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in normalized_field_records:
            local = ViolationCollector(_normalized_field_ref(item))
            validate_normalized_field_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in normalized_records:
            local = ViolationCollector(_normalized_record_ref(item))
            validate_normalized_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in normalized_record_sets:
            local = ViolationCollector(_record_set_ref(item))
            validate_normalized_record_set(item, local, context=context)
            _merge_collector(collector, local)

        for item in normalization_warning_records:
            local = ViolationCollector(_warning_ref(item))
            validate_normalization_warning_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in non_normalizable_field_records:
            local = ViolationCollector(_non_normalizable_ref(item))
            validate_non_normalizable_field_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in partial_normalization_records:
            local = ViolationCollector(_partial_ref(item))
            validate_partial_normalization_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in normalization_replay_manifests:
            local = ViolationCollector(_replay_ref(item))
            validate_normalization_replay_manifest(item, local, context=context)
            _merge_collector(collector, local)

        target_refs = tuple(
            _unique_ordered(
                [
                    *(_registry_ref(item) for item in canonical_schema_registries),
                    *(_schema_version_ref(item) for item in canonical_schema_versions),
                    *(_field_definition_ref(item) for item in canonical_field_definitions),
                    *(_mapping_rule_ref(item) for item in field_mapping_rules),
                    *(_coercion_rule_ref(item) for item in type_coercion_rules),
                    *(_unit_rule_ref(item) for item in unit_conversion_rules),
                    *(_currency_rule_ref(item) for item in currency_conversion_rules),
                    *(_run_ref(item) for item in normalization_run_records),
                    *(_normalized_field_ref(item) for item in normalized_field_records),
                    *(_normalized_record_ref(item) for item in normalized_records),
                    *(_record_set_ref(item) for item in normalized_record_sets),
                    *(_warning_ref(item) for item in normalization_warning_records),
                    *(_non_normalizable_ref(item) for item in non_normalizable_field_records),
                    *(_partial_ref(item) for item in partial_normalization_records),
                    *(_replay_ref(item) for item in normalization_replay_manifests),
                ]
            )
        ) or ("graph:canonical_normalization",)
        return self._build_report(ValidationArtifacts(target_refs), collector)

    def _build_report(
        self,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        run_id = _stable_id(
            "canonical_normalization_validation",
            self._validator_version,
            outcome.value,
            *artifacts.target_refs,
            *(_draft_signature(item) for item in collector.violations),
        )
        violations = tuple(
            ValidationViolation(
                violation_id=_stable_id(
                    "canonical_normalization_violation",
                    run_id,
                    str(index),
                    draft.code.value,
                    draft.target_ref,
                    draft.field_ref or "nofield",
                ),
                code=draft.code.value,
                severity=draft.severity,
                message=draft.message,
                target_ref=draft.target_ref,
                field_ref=draft.field_ref,
                blocking=draft.blocking,
            )
            for index, draft in enumerate(collector.violations, start=1)
        )
        return ValidationReport(
            outcome=outcome,
            validation_run=ValidationRun(
                run_id=run_id,
                validator_version=self._validator_version,
                executed_at=self._clock(),
                target_refs=artifacts.target_refs,
            ),
            violations=violations,
        )


def validate_normalization_graph(**kwargs: object) -> ValidationReport:
    return BasicNormalizationIntegrityValidator().validate_graph(**kwargs)


def _merge_collector(target: ViolationCollector, source: ViolationCollector) -> None:
    for item in source.violations:
        target.add(
            item.code,
            item.message,
            target_ref=item.target_ref,
            field_ref=item.field_ref,
            severity=item.severity,
            blocking=item.blocking,
        )


def _derive_outcome(collector: ViolationCollector) -> ValidationOutcome:
    if collector.has_errors:
        return ValidationOutcome.FAIL
    if collector.has_warnings:
        return ValidationOutcome.PASS_WITH_WARNINGS
    return ValidationOutcome.PASS


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _draft_signature(item: ViolationDraft) -> str:
    return "|".join(
        (
            item.code.value,
            item.severity.value,
            item.message,
            item.target_ref,
            item.field_ref or "nofield",
            "blocking" if item.blocking else "nonblocking",
        )
    )


def _registry_ref(registry: CanonicalSchemaRegistry) -> str:
    return f"canonical_schema_registry:{registry.canonical_schema_registry_id}"


def _schema_version_ref(schema_version: CanonicalSchemaVersion) -> str:
    return f"canonical_schema_version:{schema_version.canonical_schema_version_id}"


def _field_definition_ref(field_definition: CanonicalFieldDefinition) -> str:
    return f"canonical_field_definition:{field_definition.canonical_field_definition_id}"


def _mapping_rule_ref(mapping_rule: FieldMappingRule) -> str:
    return f"field_mapping_rule:{mapping_rule.field_mapping_rule_id}"


def _coercion_rule_ref(coercion_rule: TypeCoercionRule) -> str:
    return f"type_coercion_rule:{coercion_rule.type_coercion_rule_id}"


def _unit_rule_ref(unit_rule: UnitConversionRule) -> str:
    return f"unit_conversion_rule:{unit_rule.unit_conversion_rule_id}"


def _currency_rule_ref(currency_rule: CurrencyConversionRule) -> str:
    return f"currency_conversion_rule:{currency_rule.currency_conversion_rule_id}"


def _run_ref(normalization_run: NormalizationRunRecord) -> str:
    return f"normalization_run:{normalization_run.normalization_run_record_id}"


def _normalized_field_ref(normalized_field: NormalizedFieldRecord) -> str:
    return f"normalized_field:{normalized_field.normalized_field_record_id}"


def _normalized_record_ref(normalized_record: NormalizedRecord) -> str:
    return f"normalized_record:{normalized_record.normalized_record_id}"


def _record_set_ref(record_set: NormalizedRecordSet) -> str:
    return f"normalized_record_set:{record_set.normalized_record_set_id}"


def _warning_ref(warning: NormalizationWarningRecord) -> str:
    return f"normalization_warning:{warning.normalization_warning_record_id}"


def _non_normalizable_ref(non_normalizable_field: NonNormalizableFieldRecord) -> str:
    return f"non_normalizable_field:{non_normalizable_field.non_normalizable_field_record_id}"


def _partial_ref(partial_record: PartialNormalizationRecord) -> str:
    return f"partial_normalization:{partial_record.partial_normalization_record_id}"


def _replay_ref(replay_manifest: NormalizationReplayManifest) -> str:
    return f"normalization_replay_manifest:{replay_manifest.normalization_replay_manifest_id}"


def _unique_ordered(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
