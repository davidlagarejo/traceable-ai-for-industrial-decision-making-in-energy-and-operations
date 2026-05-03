from __future__ import annotations

from datetime import datetime, timezone
import unittest

from canonical_normalization_engine.domain import (
    CanonicalFieldDefinition,
    CanonicalFieldDefinitionId,
    CanonicalFieldName,
    CanonicalFieldType,
    CanonicalSchemaRegistry,
    CanonicalSchemaRegistryId,
    CanonicalSchemaRegistryStatus,
    CanonicalSchemaVersion,
    CanonicalSchemaVersionId,
    CanonicalSchemaVersionStatus,
    CoercionSafetyLevel,
    ConversionFactor,
    ConversionRuleType,
    CurrencyCode,
    CurrencyConversionRule,
    CurrencyConversionRuleId,
    CurrencyYear,
    ExtractionMetadataRef,
    FieldLifecycleStatus,
    FieldMappingRule,
    FieldMappingRuleId,
    MappingContext,
    MeasurementFamily,
    MissingnessStatus,
    MixedValueStatus,
    NonNormalizableFieldRecord,
    NonNormalizableFieldRecordId,
    NonNormalizableReason,
    NormalizationReplayManifest,
    NormalizationReplayManifestId,
    NormalizationRunRecord,
    NormalizationRunRecordId,
    NormalizationScopeRef,
    NormalizationStatus,
    NormalizationWarningRecord,
    NormalizationWarningRecordId,
    NormalizedFieldRecord,
    NormalizedFieldRecordId,
    NormalizedRecord,
    NormalizedRecordId,
    NormalizedRecordSet,
    NormalizedRecordSetId,
    NormalizedValue,
    ObservedValueType,
    OriginalLabel,
    ParsedDocumentObjectRef,
    ParsedFieldObjectRef,
    ParsedSourceProvenance,
    ParsedTableObjectRef,
    ParsedValue,
    PartialNormalizationRecord,
    PartialNormalizationRecordId,
    PartialNormalizationStatus,
    ParserStrategyRef,
    PrecisionDescriptor,
    PrecisionKind,
    RangeCheckResult,
    RawAssetVersionRef,
    RawValue,
    RecordKey,
    ReplayabilityStatus,
    RuleDescription,
    RuleFingerprint,
    RuleLifecycleStatus,
    SchemaName,
    SchemaProfileKind,
    SourceFormatHint,
    SourcePathHint,
    TypeCoercionRule,
    TypeCoercionRuleId,
    UnitConversionRule,
    UnitConversionRuleId,
    UnitRef,
    ValueTriplet,
    VersionFingerprint,
    VersionLabel,
    WarningCode,
    WarningSeverity,
)
from canonical_normalization_engine.validation import (
    BasicNormalizationIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 10, 20, 0, tzinfo=UTC)


class BasicNormalizationValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicNormalizationIntegrityValidator(clock=fixed_now)

    def test_complete_normalization_graph_passes(self) -> None:
        graph = self._build_complete_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertFalse(report.violations)

    def test_partial_but_coherent_graph_returns_pass_with_warnings(self) -> None:
        graph = self._build_partial_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        codes = {item.code for item in report.violations}
        self.assertIn("run.non_complete_declared", codes)
        self.assertIn("normalized_field.partial_declared", codes)
        self.assertIn("warning.declared", codes)
        self.assertIn("non_normalizable.declared", codes)
        self.assertIn("partial.declared", codes)
        self.assertIn("replay.not_fully_replayable", codes)

    def test_multiple_reference_breaks_fail_in_single_run(self) -> None:
        missing_version_id = CanonicalSchemaVersionId("schema-version:missing")
        broken_version = CanonicalSchemaVersion(
            canonical_schema_version_id=CanonicalSchemaVersionId("schema-version:broken"),
            canonical_schema_registry_id=CanonicalSchemaRegistryId("schema-registry:missing"),
            version_label=VersionLabel("broken"),
            version_status=CanonicalSchemaVersionStatus.ACTIVE,
            version_fingerprint=VersionFingerprint("schema:broken"),
            created_at=fixed_now(),
            effective_from=fixed_now(),
            supersedes_canonical_schema_version_id=None,
        )
        broken_field = CanonicalFieldDefinition(
            canonical_field_definition_id=CanonicalFieldDefinitionId("field:broken"),
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            canonical_field_name=CanonicalFieldName("broken_field"),
            canonical_field_type=CanonicalFieldType.STRING_DISCIPLINED,
            field_status=FieldLifecycleStatus.ACTIVE,
            description="Broken field",
            measurement_family=None,
            canonical_unit=None,
            allowed_units=(),
            canonical_currency=None,
            allowed_currencies=(),
            allowed_enum_values=(),
            required=False,
            allows_multiple=False,
            created_at=fixed_now(),
        )
        orphan_field = CanonicalFieldDefinition(
            canonical_field_definition_id=CanonicalFieldDefinitionId("field:orphan"),
            canonical_schema_version_id=missing_version_id,
            canonical_field_name=CanonicalFieldName("orphan_field"),
            canonical_field_type=CanonicalFieldType.STRING_DISCIPLINED,
            field_status=FieldLifecycleStatus.ACTIVE,
            description="Orphan field",
            measurement_family=None,
            canonical_unit=None,
            allowed_units=(),
            canonical_currency=None,
            allowed_currencies=(),
            allowed_enum_values=(),
            required=False,
            allows_multiple=False,
            created_at=fixed_now(),
        )
        broken_mapping = FieldMappingRule(
            field_mapping_rule_id=FieldMappingRuleId("mapping:broken"),
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            canonical_field_definition_id=broken_field.canonical_field_definition_id,
            rule_status=RuleLifecycleStatus.ACTIVE,
            original_label=OriginalLabel("Broken"),
            source_path_hint=None,
            source_format_hint=None,
            required_unit_hint=None,
            mapping_context=None,
            rule_description=RuleDescription("Broken mapping"),
            created_at=fixed_now(),
        )
        orphan_mapping = FieldMappingRule(
            field_mapping_rule_id=FieldMappingRuleId("mapping:orphan"),
            canonical_schema_version_id=missing_version_id,
            canonical_field_definition_id=CanonicalFieldDefinitionId("field:missing"),
            rule_status=RuleLifecycleStatus.ACTIVE,
            original_label=OriginalLabel("Orphan"),
            source_path_hint=None,
            source_format_hint=None,
            required_unit_hint=None,
            mapping_context=None,
            rule_description=RuleDescription("Orphan mapping"),
            created_at=fixed_now(),
        )
        broken_coercion = TypeCoercionRule(
            type_coercion_rule_id=TypeCoercionRuleId("coercion:broken"),
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            target_canonical_field_type=CanonicalFieldType.INTEGER,
            coercion_safety_level=CoercionSafetyLevel.CONDITIONAL,
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Broken coercion"),
            rule_fingerprint=RuleFingerprint("coercion:broken"),
            allowed_input_types=(ObservedValueType.STRING,),
            accepted_formats=("integer",),
            null_markers=(),
            true_markers=(),
            false_markers=(),
            created_at=fixed_now(),
        )
        orphan_coercion = TypeCoercionRule(
            type_coercion_rule_id=TypeCoercionRuleId("coercion:orphan"),
            canonical_schema_version_id=missing_version_id,
            target_canonical_field_type=CanonicalFieldType.INTEGER,
            coercion_safety_level=CoercionSafetyLevel.CONDITIONAL,
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Orphan coercion"),
            rule_fingerprint=RuleFingerprint("coercion:orphan"),
            allowed_input_types=(ObservedValueType.STRING,),
            accepted_formats=("integer",),
            null_markers=(),
            true_markers=(),
            false_markers=(),
            created_at=fixed_now(),
        )
        broken_unit_rule = UnitConversionRule(
            unit_conversion_rule_id=UnitConversionRuleId("unit-rule:broken"),
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            measurement_family=MeasurementFamily.ENERGY,
            source_unit=UnitRef("kWh"),
            target_unit=UnitRef("MWh"),
            conversion_rule_type=ConversionRuleType.FACTOR,
            conversion_factor=ConversionFactor("0.001"),
            conversion_offset=None,
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Broken unit rule"),
            rule_fingerprint=RuleFingerprint("unit-rule:broken"),
            created_at=fixed_now(),
        )
        orphan_unit_rule = UnitConversionRule(
            unit_conversion_rule_id=UnitConversionRuleId("unit-rule:orphan"),
            canonical_schema_version_id=missing_version_id,
            measurement_family=MeasurementFamily.ENERGY,
            source_unit=UnitRef("kWh"),
            target_unit=UnitRef("MWh"),
            conversion_rule_type=ConversionRuleType.FACTOR,
            conversion_factor=ConversionFactor("0.001"),
            conversion_offset=None,
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Orphan unit rule"),
            rule_fingerprint=RuleFingerprint("unit-rule:orphan"),
            created_at=fixed_now(),
        )
        broken_currency_rule = CurrencyConversionRule(
            currency_conversion_rule_id=CurrencyConversionRuleId("currency-rule:broken"),
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            source_currency=CurrencyCode("USD"),
            target_currency=CurrencyCode("EUR"),
            conversion_rule_type=ConversionRuleType.DECLARED_RATE,
            conversion_factor=ConversionFactor("0.9"),
            basis_currency_year=CurrencyYear(2024),
            basis_reference="policy://currency/2024",
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Broken currency rule"),
            rule_fingerprint=RuleFingerprint("currency-rule:broken"),
            created_at=fixed_now(),
        )
        orphan_currency_rule = CurrencyConversionRule(
            currency_conversion_rule_id=CurrencyConversionRuleId("currency-rule:orphan"),
            canonical_schema_version_id=missing_version_id,
            source_currency=CurrencyCode("USD"),
            target_currency=CurrencyCode("EUR"),
            conversion_rule_type=ConversionRuleType.DECLARED_RATE,
            conversion_factor=ConversionFactor("0.9"),
            basis_currency_year=CurrencyYear(2024),
            basis_reference="policy://currency/orphan",
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Orphan currency rule"),
            rule_fingerprint=RuleFingerprint("currency-rule:orphan"),
            created_at=fixed_now(),
        )
        broken_run = NormalizationRunRecord(
            normalization_run_record_id=NormalizationRunRecordId("run:broken"),
            canonical_schema_registry_id=CanonicalSchemaRegistryId("schema-registry:missing"),
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            source_provenance=self._run_provenance("broken"),
            normalization_status=NormalizationStatus.COMPLETE,
            replayability_status=ReplayabilityStatus.REPLAYABLE,
            created_at=fixed_now(),
        )
        broken_field_record = NormalizedFieldRecord(
            normalized_field_record_id=NormalizedFieldRecordId("normalized-field:broken"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            normalized_record_id=NormalizedRecordId("normalized-record:missing"),
            canonical_field_definition_id=broken_field.canonical_field_definition_id,
            source_provenance=self._field_provenance("broken"),
            original_label=OriginalLabel("Broken"),
            value_triplet=ValueTriplet(
                raw_value=RawValue(""),
                parsed_value=ParsedValue(""),
                normalized_value=NormalizedValue("100"),
            ),
            normalized_field_type=CanonicalFieldType.DECIMAL,
            original_unit=UnitRef("GJ"),
            normalized_unit=UnitRef("MWh"),
            original_currency=CurrencyCode("USD"),
            normalized_currency=CurrencyCode("EUR"),
            precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
            missingness_status=MissingnessStatus.NOT_MISSING,
            mixed_value_status=MixedValueStatus.NOT_MIXED,
            range_check_result=RangeCheckResult.IN_RANGE,
            normalization_status=NormalizationStatus.COMPLETE,
            field_mapping_rule_id=broken_mapping.field_mapping_rule_id,
            type_coercion_rule_id=broken_coercion.type_coercion_rule_id,
            unit_conversion_rule_id=broken_unit_rule.unit_conversion_rule_id,
            currency_conversion_rule_id=broken_currency_rule.currency_conversion_rule_id,
            created_at=fixed_now(),
        )
        broken_record = NormalizedRecord(
            normalized_record_id=NormalizedRecordId("normalized-record:broken"),
            normalized_record_set_id=NormalizedRecordSetId("record-set:missing"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            source_provenance=self._record_provenance("broken"),
            record_key=RecordKey("broken-row"),
            normalization_status=NormalizationStatus.COMPLETE,
            normalized_field_record_ids=(broken_field_record.normalized_field_record_id,),
            created_at=fixed_now(),
        )
        broken_set = NormalizedRecordSet(
            normalized_record_set_id=NormalizedRecordSetId("record-set:broken"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            normalization_status=NormalizationStatus.COMPLETE,
            normalized_record_ids=(broken_record.normalized_record_id,),
            created_at=fixed_now(),
        )
        broken_warning = NormalizationWarningRecord(
            normalization_warning_record_id=NormalizationWarningRecordId("warning:broken"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            scope_ref=NormalizationScopeRef.for_normalized_field(
                NormalizedFieldRecordId("normalized-field:missing")
            ),
            warning_code=WarningCode("normalization.warning"),
            warning_severity=WarningSeverity.MODERATE,
            message="Broken warning",
            created_at=fixed_now(),
        )
        broken_non_normalizable = NonNormalizableFieldRecord(
            non_normalizable_field_record_id=NonNormalizableFieldRecordId("non-normalizable:broken"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            source_provenance=self._field_provenance("broken-nn"),
            original_label=OriginalLabel("Unknown"),
            value_triplet=ValueTriplet(
                raw_value=RawValue("unknown"),
                parsed_value=ParsedValue("unknown"),
                normalized_value=None,
            ),
            candidate_canonical_field_definition_id=broken_field.canonical_field_definition_id,
            field_mapping_rule_id=broken_mapping.field_mapping_rule_id,
            original_unit=None,
            original_currency=None,
            missingness_status=MissingnessStatus.NOT_NORMALIZABLE,
            mixed_value_status=MixedValueStatus.NOT_MIXED,
            reason=NonNormalizableReason("Missing meaning"),
            created_at=fixed_now(),
        )
        broken_partial = PartialNormalizationRecord(
            partial_normalization_record_id=PartialNormalizationRecordId("partial:broken"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            normalization_status=NormalizationStatus.PARTIAL,
            partial_normalization_status=PartialNormalizationStatus.PARTIAL_USEFUL,
            normalized_field_record_ids=(broken_field_record.normalized_field_record_id,),
            non_normalizable_field_record_ids=(
                broken_non_normalizable.non_normalizable_field_record_id,
            ),
            rationale=NonNormalizableReason("Broken partial"),
            created_at=fixed_now(),
        )
        broken_replay = NormalizationReplayManifest(
            normalization_replay_manifest_id=NormalizationReplayManifestId("replay:broken"),
            normalization_run_record_id=broken_run.normalization_run_record_id,
            canonical_schema_version_id=broken_version.canonical_schema_version_id,
            source_provenance=self._run_provenance("broken-other"),
            field_mapping_rule_ids=(broken_mapping.field_mapping_rule_id,),
            type_coercion_rule_ids=(broken_coercion.type_coercion_rule_id,),
            unit_conversion_rule_ids=(broken_unit_rule.unit_conversion_rule_id,),
            currency_conversion_rule_ids=(broken_currency_rule.currency_conversion_rule_id,),
            normalized_record_set_id=broken_set.normalized_record_set_id,
            replayability_status=ReplayabilityStatus.REPLAYABLE,
            created_at=fixed_now(),
        )

        report = self.validator.validate_graph(
            canonical_schema_versions=(broken_version,),
            field_mapping_rules=(broken_mapping, orphan_mapping),
            type_coercion_rules=(broken_coercion, orphan_coercion),
            unit_conversion_rules=(broken_unit_rule, orphan_unit_rule),
            currency_conversion_rules=(broken_currency_rule, orphan_currency_rule),
            canonical_field_definitions=(broken_field, orphan_field),
            normalized_field_records=(broken_field_record,),
            normalized_records=(broken_record,),
            normalized_record_sets=(broken_set,),
            normalization_warning_records=(broken_warning,),
            non_normalizable_field_records=(broken_non_normalizable,),
            partial_normalization_records=(broken_partial,),
            normalization_run_records=(broken_run,),
            normalization_replay_manifests=(broken_replay,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("schema_version.registry_reference_invalid", codes)
        self.assertIn("field.schema_version_reference_invalid", codes)
        self.assertIn("mapping.schema_version_reference_invalid", codes)
        self.assertIn("coercion.schema_version_reference_invalid", codes)
        self.assertIn("unit_conversion.schema_version_reference_invalid", codes)
        self.assertIn("currency_conversion.schema_version_reference_invalid", codes)
        self.assertIn("run.schema_registry_reference_invalid", codes)
        self.assertIn("normalized_field.record_reference_invalid", codes)
        self.assertIn("warning.scope_unresolved", codes)

    def test_complete_record_with_partial_field_fails(self) -> None:
        graph = self._build_partial_graph()
        partial_field = graph["normalized_field_records"][1]
        record = graph["normalized_records"][0]
        invalid_record = NormalizedRecord(
            normalized_record_id=record.normalized_record_id,
            normalized_record_set_id=record.normalized_record_set_id,
            normalization_run_record_id=record.normalization_run_record_id,
            source_provenance=record.source_provenance,
            record_key=record.record_key,
            normalization_status=NormalizationStatus.COMPLETE,
            normalized_field_record_ids=record.normalized_field_record_ids,
            created_at=record.created_at,
        )
        invalid_set = NormalizedRecordSet(
            normalized_record_set_id=graph["normalized_record_sets"][0].normalized_record_set_id,
            normalization_run_record_id=graph["normalized_record_sets"][0].normalization_run_record_id,
            canonical_schema_version_id=graph["normalized_record_sets"][0].canonical_schema_version_id,
            normalization_status=NormalizationStatus.COMPLETE,
            normalized_record_ids=(invalid_record.normalized_record_id,),
            created_at=graph["normalized_record_sets"][0].created_at,
        )
        patched_fields = []
        for item in graph["normalized_field_records"]:
            if item.normalized_field_record_id == partial_field.normalized_field_record_id:
                patched_fields.append(
                    NormalizedFieldRecord(
                        normalized_field_record_id=item.normalized_field_record_id,
                        normalization_run_record_id=item.normalization_run_record_id,
                        normalized_record_id=invalid_record.normalized_record_id,
                        canonical_field_definition_id=item.canonical_field_definition_id,
                        source_provenance=item.source_provenance,
                        original_label=item.original_label,
                        value_triplet=item.value_triplet,
                        normalized_field_type=item.normalized_field_type,
                        original_unit=item.original_unit,
                        normalized_unit=item.normalized_unit,
                        original_currency=item.original_currency,
                        normalized_currency=item.normalized_currency,
                        precision_descriptor=item.precision_descriptor,
                        missingness_status=item.missingness_status,
                        mixed_value_status=item.mixed_value_status,
                        range_check_result=item.range_check_result,
                        normalization_status=item.normalization_status,
                        field_mapping_rule_id=item.field_mapping_rule_id,
                        type_coercion_rule_id=item.type_coercion_rule_id,
                        unit_conversion_rule_id=item.unit_conversion_rule_id,
                        currency_conversion_rule_id=item.currency_conversion_rule_id,
                        created_at=item.created_at,
                    )
                )
            else:
                patched_fields.append(item)

        graph["normalized_records"] = (invalid_record,)
        graph["normalized_record_sets"] = (invalid_set,)
        graph["normalized_field_records"] = tuple(patched_fields)

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("normalized_record.complete_incoherent", codes)

    def test_warning_scope_run_mismatch_fails(self) -> None:
        complete_graph = self._build_complete_graph()
        other_graph = self._build_complete_graph(suffix="other")
        mismatched_warning = NormalizationWarningRecord(
            normalization_warning_record_id=NormalizationWarningRecordId("warning:mismatch"),
            normalization_run_record_id=complete_graph["normalization_run_records"][0].normalization_run_record_id,
            scope_ref=NormalizationScopeRef.for_normalized_field(
                other_graph["normalized_field_records"][0].normalized_field_record_id
            ),
            warning_code=WarningCode("normalization.warning"),
            warning_severity=WarningSeverity.MODERATE,
            message="Cross-run mismatch",
            created_at=fixed_now(),
        )

        merged_graph = dict(complete_graph)
        merged_graph["canonical_schema_registries"] = (
            *complete_graph["canonical_schema_registries"],
            *other_graph["canonical_schema_registries"],
        )
        merged_graph["canonical_schema_versions"] = (
            *complete_graph["canonical_schema_versions"],
            *other_graph["canonical_schema_versions"],
        )
        merged_graph["canonical_field_definitions"] = (
            *complete_graph["canonical_field_definitions"],
            *other_graph["canonical_field_definitions"],
        )
        merged_graph["field_mapping_rules"] = (
            *complete_graph["field_mapping_rules"],
            *other_graph["field_mapping_rules"],
        )
        merged_graph["type_coercion_rules"] = (
            *complete_graph["type_coercion_rules"],
            *other_graph["type_coercion_rules"],
        )
        merged_graph["unit_conversion_rules"] = (
            *complete_graph["unit_conversion_rules"],
            *other_graph["unit_conversion_rules"],
        )
        merged_graph["currency_conversion_rules"] = (
            *complete_graph["currency_conversion_rules"],
            *other_graph["currency_conversion_rules"],
        )
        merged_graph["normalized_field_records"] = (
            *complete_graph["normalized_field_records"],
            *other_graph["normalized_field_records"],
        )
        merged_graph["normalized_records"] = (
            *complete_graph["normalized_records"],
            *other_graph["normalized_records"],
        )
        merged_graph["normalized_record_sets"] = (
            *complete_graph["normalized_record_sets"],
            *other_graph["normalized_record_sets"],
        )
        merged_graph["normalization_run_records"] = (
            *complete_graph["normalization_run_records"],
            *other_graph["normalization_run_records"],
        )
        merged_graph["normalization_replay_manifests"] = (
            *complete_graph["normalization_replay_manifests"],
            *other_graph["normalization_replay_manifests"],
        )
        merged_graph["normalization_warning_records"] = (mismatched_warning,)

        report = self.validator.validate_graph(**merged_graph)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("warning.scope_run_mismatch", codes)

    def test_incoherent_unit_rule_fails(self) -> None:
        graph = self._build_complete_graph()
        energy_field = graph["normalized_field_records"][0]
        invalid_field = NormalizedFieldRecord(
            normalized_field_record_id=energy_field.normalized_field_record_id,
            normalization_run_record_id=energy_field.normalization_run_record_id,
            normalized_record_id=energy_field.normalized_record_id,
            canonical_field_definition_id=energy_field.canonical_field_definition_id,
            source_provenance=energy_field.source_provenance,
            original_label=energy_field.original_label,
            value_triplet=energy_field.value_triplet,
            normalized_field_type=energy_field.normalized_field_type,
            original_unit=UnitRef("GJ"),
            normalized_unit=energy_field.normalized_unit,
            original_currency=energy_field.original_currency,
            normalized_currency=energy_field.normalized_currency,
            precision_descriptor=energy_field.precision_descriptor,
            missingness_status=energy_field.missingness_status,
            mixed_value_status=energy_field.mixed_value_status,
            range_check_result=energy_field.range_check_result,
            normalization_status=energy_field.normalization_status,
            field_mapping_rule_id=energy_field.field_mapping_rule_id,
            type_coercion_rule_id=energy_field.type_coercion_rule_id,
            unit_conversion_rule_id=energy_field.unit_conversion_rule_id,
            currency_conversion_rule_id=energy_field.currency_conversion_rule_id,
            created_at=energy_field.created_at,
        )
        graph["normalized_field_records"] = (invalid_field, graph["normalized_field_records"][1])

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("normalized_field.unit_rule_incoherent", codes)

    def _build_complete_graph(self, suffix: str = "base") -> dict[str, object]:
        registry = CanonicalSchemaRegistry(
            canonical_schema_registry_id=CanonicalSchemaRegistryId(f"schema-registry:{suffix}"),
            schema_profile_kind=SchemaProfileKind.PHASE_1_BUNDLE,
            schema_name=SchemaName(f"Energy benchmark {suffix}"),
            registry_status=CanonicalSchemaRegistryStatus.ACTIVE,
            created_at=fixed_now(),
        )
        schema_version = CanonicalSchemaVersion(
            canonical_schema_version_id=CanonicalSchemaVersionId(f"schema-version:{suffix}:v1"),
            canonical_schema_registry_id=registry.canonical_schema_registry_id,
            version_label=VersionLabel("v1"),
            version_status=CanonicalSchemaVersionStatus.ACTIVE,
            version_fingerprint=VersionFingerprint(f"schema:{suffix}:v1"),
            created_at=fixed_now(),
            effective_from=fixed_now(),
            supersedes_canonical_schema_version_id=None,
        )
        energy_field_definition = CanonicalFieldDefinition(
            canonical_field_definition_id=CanonicalFieldDefinitionId(f"field:{suffix}:energy_use"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            canonical_field_name=CanonicalFieldName("energy_use"),
            canonical_field_type=CanonicalFieldType.MEASURE_WITH_UNIT,
            field_status=FieldLifecycleStatus.ACTIVE,
            description="Energy use",
            measurement_family=MeasurementFamily.ENERGY,
            canonical_unit=UnitRef("MWh"),
            allowed_units=(UnitRef("kWh"), UnitRef("MWh"), UnitRef("GJ")),
            canonical_currency=None,
            allowed_currencies=(),
            allowed_enum_values=(),
            required=False,
            allows_multiple=False,
            created_at=fixed_now(),
        )
        year_field_definition = CanonicalFieldDefinition(
            canonical_field_definition_id=CanonicalFieldDefinitionId(f"field:{suffix}:measurement_year"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            canonical_field_name=CanonicalFieldName("measurement_year"),
            canonical_field_type=CanonicalFieldType.YEAR,
            field_status=FieldLifecycleStatus.ACTIVE,
            description="Measurement year",
            measurement_family=None,
            canonical_unit=None,
            allowed_units=(),
            canonical_currency=None,
            allowed_currencies=(),
            allowed_enum_values=(),
            required=False,
            allows_multiple=False,
            created_at=fixed_now(),
        )
        mapping_energy = FieldMappingRule(
            field_mapping_rule_id=FieldMappingRuleId(f"mapping:{suffix}:energy_use"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            canonical_field_definition_id=energy_field_definition.canonical_field_definition_id,
            rule_status=RuleLifecycleStatus.ACTIVE,
            original_label=OriginalLabel("Energy Use"),
            source_path_hint=SourcePathHint("$.energy_use"),
            source_format_hint=SourceFormatHint("pdf_table"),
            required_unit_hint=UnitRef("kWh"),
            mapping_context=MappingContext("benchmarking"),
            rule_description=RuleDescription("Map Energy Use to energy_use."),
            created_at=fixed_now(),
        )
        mapping_year = FieldMappingRule(
            field_mapping_rule_id=FieldMappingRuleId(f"mapping:{suffix}:measurement_year"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            canonical_field_definition_id=year_field_definition.canonical_field_definition_id,
            rule_status=RuleLifecycleStatus.ACTIVE,
            original_label=OriginalLabel("Year"),
            source_path_hint=SourcePathHint("$.year"),
            source_format_hint=SourceFormatHint("pdf_table"),
            required_unit_hint=None,
            mapping_context=MappingContext("benchmarking"),
            rule_description=RuleDescription("Map Year to measurement_year."),
            created_at=fixed_now(),
        )
        decimal_coercion = TypeCoercionRule(
            type_coercion_rule_id=TypeCoercionRuleId(f"coercion:{suffix}:decimal"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            target_canonical_field_type=CanonicalFieldType.DECIMAL,
            coercion_safety_level=CoercionSafetyLevel.SAFE,
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Parse decimal values."),
            rule_fingerprint=RuleFingerprint(f"coercion:{suffix}:decimal"),
            allowed_input_types=(ObservedValueType.STRING, ObservedValueType.DECIMAL),
            accepted_formats=("decimal",),
            null_markers=(),
            true_markers=(),
            false_markers=(),
            created_at=fixed_now(),
        )
        unit_rule = UnitConversionRule(
            unit_conversion_rule_id=UnitConversionRuleId(f"unit-rule:{suffix}:kwh_to_mwh"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            measurement_family=MeasurementFamily.ENERGY,
            source_unit=UnitRef("kWh"),
            target_unit=UnitRef("MWh"),
            conversion_rule_type=ConversionRuleType.FACTOR,
            conversion_factor=ConversionFactor("0.001"),
            conversion_offset=None,
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Convert kWh to MWh."),
            rule_fingerprint=RuleFingerprint(f"unit-rule:{suffix}:kwh_to_mwh"),
            created_at=fixed_now(),
        )
        currency_rule = CurrencyConversionRule(
            currency_conversion_rule_id=CurrencyConversionRuleId(f"currency-rule:{suffix}:usd_to_eur"),
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            source_currency=CurrencyCode("USD"),
            target_currency=CurrencyCode("EUR"),
            conversion_rule_type=ConversionRuleType.DECLARED_RATE,
            conversion_factor=ConversionFactor("0.9200"),
            basis_currency_year=CurrencyYear(2024),
            basis_reference="policy://fx/2024-mean",
            rule_status=RuleLifecycleStatus.ACTIVE,
            rule_description=RuleDescription("Convert USD to EUR with declared benchmark rate."),
            rule_fingerprint=RuleFingerprint(f"currency-rule:{suffix}:usd_to_eur"),
            created_at=fixed_now(),
        )
        run = NormalizationRunRecord.for_schema_version(
            normalization_run_record_id=NormalizationRunRecordId(f"run:{suffix}"),
            schema_version=schema_version,
            source_provenance=self._run_provenance(suffix),
            normalization_status=NormalizationStatus.COMPLETE,
            replayability_status=ReplayabilityStatus.REPLAYABLE,
            created_at=fixed_now(),
        )
        record_set = NormalizedRecordSet(
            normalized_record_set_id=NormalizedRecordSetId(f"record-set:{suffix}"),
            normalization_run_record_id=run.normalization_run_record_id,
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            normalization_status=NormalizationStatus.COMPLETE,
            normalized_record_ids=(NormalizedRecordId(f"record:{suffix}:row1"),),
            created_at=fixed_now(),
        )
        record = NormalizedRecord(
            normalized_record_id=NormalizedRecordId(f"record:{suffix}:row1"),
            normalized_record_set_id=record_set.normalized_record_set_id,
            normalization_run_record_id=run.normalization_run_record_id,
            source_provenance=self._record_provenance(suffix),
            record_key=RecordKey(f"{suffix}:row1"),
            normalization_status=NormalizationStatus.COMPLETE,
            normalized_field_record_ids=(
                NormalizedFieldRecordId(f"normalized-field:{suffix}:energy_use"),
                NormalizedFieldRecordId(f"normalized-field:{suffix}:measurement_year"),
            ),
            created_at=fixed_now(),
        )
        normalized_energy = NormalizedFieldRecord(
            normalized_field_record_id=NormalizedFieldRecordId(f"normalized-field:{suffix}:energy_use"),
            normalization_run_record_id=run.normalization_run_record_id,
            normalized_record_id=record.normalized_record_id,
            canonical_field_definition_id=energy_field_definition.canonical_field_definition_id,
            source_provenance=self._field_provenance(f"{suffix}:energy"),
            original_label=OriginalLabel("Energy Use"),
            value_triplet=ValueTriplet(
                raw_value=RawValue("123400 kWh"),
                parsed_value=ParsedValue("123400"),
                normalized_value=NormalizedValue("123.4"),
            ),
            normalized_field_type=energy_field_definition.canonical_field_type,
            original_unit=UnitRef("kWh"),
            normalized_unit=UnitRef("MWh"),
            original_currency=None,
            normalized_currency=None,
            precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
            missingness_status=MissingnessStatus.NOT_MISSING,
            mixed_value_status=MixedValueStatus.NOT_MIXED,
            range_check_result=RangeCheckResult.IN_RANGE,
            normalization_status=NormalizationStatus.COMPLETE,
            field_mapping_rule_id=mapping_energy.field_mapping_rule_id,
            type_coercion_rule_id=decimal_coercion.type_coercion_rule_id,
            unit_conversion_rule_id=unit_rule.unit_conversion_rule_id,
            currency_conversion_rule_id=None,
            created_at=fixed_now(),
        )
        normalized_year = NormalizedFieldRecord(
            normalized_field_record_id=NormalizedFieldRecordId(f"normalized-field:{suffix}:measurement_year"),
            normalization_run_record_id=run.normalization_run_record_id,
            normalized_record_id=record.normalized_record_id,
            canonical_field_definition_id=year_field_definition.canonical_field_definition_id,
            source_provenance=self._field_provenance(f"{suffix}:year"),
            original_label=OriginalLabel("Year"),
            value_triplet=ValueTriplet(
                raw_value=RawValue("2024"),
                parsed_value=ParsedValue("2024"),
                normalized_value=NormalizedValue("2024"),
            ),
            normalized_field_type=year_field_definition.canonical_field_type,
            original_unit=None,
            normalized_unit=None,
            original_currency=None,
            normalized_currency=None,
            precision_descriptor=PrecisionDescriptor(PrecisionKind.YEAR),
            missingness_status=MissingnessStatus.NOT_MISSING,
            mixed_value_status=MixedValueStatus.NOT_MIXED,
            range_check_result=RangeCheckResult.IN_RANGE,
            normalization_status=NormalizationStatus.COMPLETE,
            field_mapping_rule_id=mapping_year.field_mapping_rule_id,
            type_coercion_rule_id=None,
            unit_conversion_rule_id=None,
            currency_conversion_rule_id=None,
            created_at=fixed_now(),
        )
        replay_manifest = NormalizationReplayManifest(
            normalization_replay_manifest_id=NormalizationReplayManifestId(f"replay:{suffix}"),
            normalization_run_record_id=run.normalization_run_record_id,
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            source_provenance=run.source_provenance,
            field_mapping_rule_ids=(
                mapping_energy.field_mapping_rule_id,
                mapping_year.field_mapping_rule_id,
            ),
            type_coercion_rule_ids=(decimal_coercion.type_coercion_rule_id,),
            unit_conversion_rule_ids=(unit_rule.unit_conversion_rule_id,),
            currency_conversion_rule_ids=(currency_rule.currency_conversion_rule_id,),
            normalized_record_set_id=record_set.normalized_record_set_id,
            replayability_status=ReplayabilityStatus.REPLAYABLE,
            created_at=fixed_now(),
        )
        return {
            "canonical_schema_registries": (registry,),
            "canonical_schema_versions": (schema_version,),
            "canonical_field_definitions": (
                energy_field_definition,
                year_field_definition,
            ),
            "field_mapping_rules": (mapping_energy, mapping_year),
            "type_coercion_rules": (decimal_coercion,),
            "unit_conversion_rules": (unit_rule,),
            "currency_conversion_rules": (currency_rule,),
            "normalized_field_records": (normalized_energy, normalized_year),
            "normalized_records": (record,),
            "normalized_record_sets": (record_set,),
            "normalization_warning_records": (),
            "non_normalizable_field_records": (),
            "partial_normalization_records": (),
            "normalization_run_records": (run,),
            "normalization_replay_manifests": (replay_manifest,),
        }

    def _build_partial_graph(self) -> dict[str, object]:
        graph = self._build_complete_graph("partial")
        run = graph["normalization_run_records"][0]
        schema_version = graph["canonical_schema_versions"][0]
        energy_field_definition = graph["canonical_field_definitions"][0]
        mapping_energy = graph["field_mapping_rules"][0]
        record_set = graph["normalized_record_sets"][0]
        record = graph["normalized_records"][0]
        complete_energy = graph["normalized_field_records"][0]
        partial_run = NormalizationRunRecord(
            normalization_run_record_id=run.normalization_run_record_id,
            canonical_schema_registry_id=run.canonical_schema_registry_id,
            canonical_schema_version_id=run.canonical_schema_version_id,
            source_provenance=run.source_provenance,
            normalization_status=NormalizationStatus.PARTIAL,
            replayability_status=ReplayabilityStatus.PARTIALLY_REPLAYABLE,
            created_at=run.created_at,
        )
        partial_record_set = NormalizedRecordSet(
            normalized_record_set_id=record_set.normalized_record_set_id,
            normalization_run_record_id=record_set.normalization_run_record_id,
            canonical_schema_version_id=record_set.canonical_schema_version_id,
            normalization_status=NormalizationStatus.PARTIAL,
            normalized_record_ids=record_set.normalized_record_ids,
            created_at=record_set.created_at,
        )
        partial_record = NormalizedRecord(
            normalized_record_id=record.normalized_record_id,
            normalized_record_set_id=record.normalized_record_set_id,
            normalization_run_record_id=record.normalization_run_record_id,
            source_provenance=record.source_provenance,
            record_key=record.record_key,
            normalization_status=NormalizationStatus.PARTIAL,
            normalized_field_record_ids=(
                complete_energy.normalized_field_record_id,
                NormalizedFieldRecordId("normalized-field:partial:limited"),
            ),
            created_at=record.created_at,
        )
        partial_field = NormalizedFieldRecord(
            normalized_field_record_id=NormalizedFieldRecordId("normalized-field:partial:limited"),
            normalization_run_record_id=partial_run.normalization_run_record_id,
            normalized_record_id=partial_record.normalized_record_id,
            canonical_field_definition_id=energy_field_definition.canonical_field_definition_id,
            source_provenance=self._field_provenance("partial:limited"),
            original_label=OriginalLabel("Annual kWh"),
            value_triplet=ValueTriplet(
                raw_value=RawValue("range 100-200"),
                parsed_value=ParsedValue("100-200"),
                normalized_value=None,
            ),
            normalized_field_type=energy_field_definition.canonical_field_type,
            original_unit=UnitRef("kWh"),
            normalized_unit=None,
            original_currency=None,
            normalized_currency=None,
            precision_descriptor=PrecisionDescriptor(PrecisionKind.APPROXIMATE, "range literal"),
            missingness_status=MissingnessStatus.NOT_PARSEABLE,
            mixed_value_status=MixedValueStatus.RANGE_EXPRESSION,
            range_check_result=RangeCheckResult.SUSPICIOUS,
            normalization_status=NormalizationStatus.PARTIAL,
            field_mapping_rule_id=mapping_energy.field_mapping_rule_id,
            type_coercion_rule_id=None,
            unit_conversion_rule_id=None,
            currency_conversion_rule_id=None,
            created_at=fixed_now(),
        )
        non_normalizable = NonNormalizableFieldRecord(
            non_normalizable_field_record_id=NonNormalizableFieldRecordId("non-normalizable:partial:fuel"),
            normalization_run_record_id=partial_run.normalization_run_record_id,
            source_provenance=self._field_provenance("partial:fuel"),
            original_label=OriginalLabel("Fuel"),
            value_triplet=ValueTriplet(
                raw_value=RawValue("fuel"),
                parsed_value=ParsedValue("fuel"),
                normalized_value=None,
            ),
            candidate_canonical_field_definition_id=None,
            field_mapping_rule_id=None,
            original_unit=None,
            original_currency=None,
            missingness_status=MissingnessStatus.NOT_NORMALIZABLE,
            mixed_value_status=MixedValueStatus.NOT_MIXED,
            reason=NonNormalizableReason("Meaning remains ambiguous at normalization time."),
            created_at=fixed_now(),
        )
        warning = NormalizationWarningRecord(
            normalization_warning_record_id=NormalizationWarningRecordId("warning:partial:range"),
            normalization_run_record_id=partial_run.normalization_run_record_id,
            scope_ref=NormalizationScopeRef.for_normalized_field(partial_field.normalized_field_record_id),
            warning_code=WarningCode("normalization.range_suspicious"),
            warning_severity=WarningSeverity.MODERATE,
            message="Range-like energy expression remains only partially normalized.",
            created_at=fixed_now(),
        )
        partial = PartialNormalizationRecord(
            partial_normalization_record_id=PartialNormalizationRecordId("partial:energy"),
            normalization_run_record_id=partial_run.normalization_run_record_id,
            normalization_status=NormalizationStatus.PARTIAL,
            partial_normalization_status=PartialNormalizationStatus.PARTIAL_USEFUL,
            normalized_field_record_ids=(partial_field.normalized_field_record_id,),
            non_normalizable_field_record_ids=(non_normalizable.non_normalizable_field_record_id,),
            rationale=NonNormalizableReason("One field normalized only partially and another stayed unresolved."),
            created_at=fixed_now(),
        )
        partial_replay = NormalizationReplayManifest(
            normalization_replay_manifest_id=NormalizationReplayManifestId("replay:partial"),
            normalization_run_record_id=partial_run.normalization_run_record_id,
            canonical_schema_version_id=schema_version.canonical_schema_version_id,
            source_provenance=partial_run.source_provenance,
            field_mapping_rule_ids=(mapping_energy.field_mapping_rule_id,),
            type_coercion_rule_ids=(),
            unit_conversion_rule_ids=(),
            currency_conversion_rule_ids=(),
            normalized_record_set_id=partial_record_set.normalized_record_set_id,
            replayability_status=ReplayabilityStatus.PARTIALLY_REPLAYABLE,
            created_at=fixed_now(),
        )
        graph["normalized_field_records"] = (complete_energy, partial_field)
        graph["normalized_records"] = (partial_record,)
        graph["normalized_record_sets"] = (partial_record_set,)
        graph["normalization_warning_records"] = (warning,)
        graph["non_normalizable_field_records"] = (non_normalizable,)
        graph["partial_normalization_records"] = (partial,)
        graph["normalization_run_records"] = (partial_run,)
        graph["normalization_replay_manifests"] = (partial_replay,)
        return graph

    def _run_provenance(self, suffix: str) -> ParsedSourceProvenance:
        return ParsedSourceProvenance(
            raw_asset_version_ref=RawAssetVersionRef(f"raw-asset-version:{suffix}"),
            extraction_metadata_ref=ExtractionMetadataRef(f"extraction-metadata:{suffix}"),
            parsed_document_object_ref=ParsedDocumentObjectRef(f"parsed-document:{suffix}"),
            parser_strategy_ref=ParserStrategyRef(f"parser-strategy:{suffix}"),
            parsed_table_object_ref=None,
            parsed_field_object_ref=None,
        )

    def _record_provenance(self, suffix: str) -> ParsedSourceProvenance:
        return ParsedSourceProvenance(
            raw_asset_version_ref=RawAssetVersionRef(f"raw-asset-version:{suffix}"),
            extraction_metadata_ref=ExtractionMetadataRef(f"extraction-metadata:{suffix}"),
            parsed_document_object_ref=ParsedDocumentObjectRef(f"parsed-document:{suffix}"),
            parser_strategy_ref=ParserStrategyRef(f"parser-strategy:{suffix}"),
            parsed_table_object_ref=ParsedTableObjectRef(f"parsed-table:{suffix}"),
            parsed_field_object_ref=None,
        )

    def _field_provenance(self, suffix: str) -> ParsedSourceProvenance:
        return ParsedSourceProvenance(
            raw_asset_version_ref=RawAssetVersionRef(f"raw-asset-version:{suffix}"),
            extraction_metadata_ref=ExtractionMetadataRef(f"extraction-metadata:{suffix}"),
            parsed_document_object_ref=ParsedDocumentObjectRef(f"parsed-document:{suffix}"),
            parser_strategy_ref=ParserStrategyRef(f"parser-strategy:{suffix}"),
            parsed_table_object_ref=ParsedTableObjectRef(f"parsed-table:{suffix}"),
            parsed_field_object_ref=ParsedFieldObjectRef(f"parsed-field:{suffix}"),
        )


if __name__ == "__main__":
    unittest.main()
