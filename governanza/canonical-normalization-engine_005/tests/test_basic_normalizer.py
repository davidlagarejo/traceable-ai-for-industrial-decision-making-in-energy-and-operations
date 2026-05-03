from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
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
    NormalizationRunRecordId,
    NormalizationStatus,
    ObservedValueType,
    OriginalLabel,
    ParsedDocumentObjectRef,
    ParsedFieldObjectRef,
    ParsedSourceProvenance,
    ParsedTableObjectRef,
    ParsedValue,
    ParserStrategyRef,
    RawAssetVersionRef,
    RawValue,
    RecordKey,
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
    VersionFingerprint,
    VersionLabel,
)
from canonical_normalization_engine.normalization import (
    BasicFieldMapper,
    BasicNormalizer,
    BasicTypeCoercer,
    BasicUnitConverter,
    FieldMappingStatus,
    ParsedFieldInput,
)
from canonical_normalization_engine.validation import (
    BasicNormalizationIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 10, 21, 0, tzinfo=UTC)


class BasicNormalizerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mapper = BasicFieldMapper()
        self.coercer = BasicTypeCoercer()
        self.unit_converter = BasicUnitConverter()
        self.normalizer = BasicNormalizer(clock=fixed_now)
        self.validator = BasicNormalizationIntegrityValidator(clock=fixed_now)
        self.registry, self.schema_version = self._build_schema()
        self.field_definitions = self._build_field_definitions()
        self.mapping_rules = self._build_mapping_rules()
        self.coercion_rules = self._build_coercion_rules()
        self.unit_rules = self._build_unit_rules()
        self.currency_rules = self._build_currency_rules()

    def test_explicit_mapping_of_energy_use(self) -> None:
        field_input = self._field_input("energy-use", "Energy Use", "1200", original_unit="MWh")

        result = self.mapper.map_field(
            field_input=field_input,
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            canonical_schema_version_id=self.schema_version.canonical_schema_version_id,
        )

        self.assertEqual(result.status, FieldMappingStatus.MATCHED)
        self.assertEqual(
            result.canonical_field_definition.canonical_field_name.value,
            "energy_use",
        )

    def test_power_cons_does_not_collapse_with_annual_kwh_rule(self) -> None:
        field_input = self._field_input("power-cons", "Power Cons.", "1200", original_unit="kWh")

        result = self.mapper.map_field(
            field_input=field_input,
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            canonical_schema_version_id=self.schema_version.canonical_schema_version_id,
        )

        self.assertEqual(result.status, FieldMappingStatus.NO_MATCH)
        self.assertIsNone(result.canonical_field_definition)

    def test_numeric_coercion_preserves_triple_values(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:numeric"),
            field_inputs=(
                self._field_input("energy-numeric", "Energy Use", "123400", original_unit="MWh"),
            ),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.value_triplet.raw_value.value, "123400")
        self.assertEqual(field.value_triplet.parsed_value.value, "123400")
        self.assertEqual(field.value_triplet.normalized_value.value, "123400")

    def test_percentage_textual_coercion(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:percentage"),
            field_inputs=(self._field_input("eff", "Efficiency", "87.5%"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.normalization_status, NormalizationStatus.COMPLETE)
        self.assertEqual(field.value_triplet.normalized_value.value, "87.5")

    def test_full_date_and_year_only_keep_precision_distinct(self) -> None:
        date_input = self._field_input("report-date", "Report Date", "2024-03-15")
        year_input = self._field_input("report-year", "Report Year", "2024")

        date_result = self.coercer.coerce_value(
            field_input=date_input,
            canonical_field_definition=self._field("report_date"),
            type_coercion_rules=self.coercion_rules,
        )
        year_result = self.coercer.coerce_value(
            field_input=year_input,
            canonical_field_definition=self._field("report_year"),
            type_coercion_rules=self.coercion_rules,
        )

        self.assertEqual(date_result.precision_descriptor.precision_kind.value, "day")
        self.assertEqual(year_result.precision_descriptor.precision_kind.value, "year")
        self.assertEqual(date_result.normalization_status, NormalizationStatus.COMPLETE)
        self.assertEqual(year_result.normalization_status, NormalizationStatus.COMPLETE)

    def test_kwh_to_mwh_conversion_with_explicit_rule(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:kwh_to_mwh"),
            field_inputs=(self._field_input("energy-kwh", "Energy Use", "3200", original_unit="kWh"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.value_triplet.normalized_value.value, "3.2")
        self.assertEqual(field.normalized_unit.value, "MWh")
        self.assertIsNotNone(field.unit_conversion_rule_id)
        self._assert_result_validates(result)

    def test_gj_to_kwh_conversion_with_explicit_rule(self) -> None:
        conversion_result = self.unit_converter.convert_value(
            canonical_field_definition=self._field("energy_use_kwh"),
            original_unit=UnitRef("GJ"),
            numeric_value=Decimal("1"),
            unit_conversion_rules=self.unit_rules,
        )

        self.assertEqual(conversion_result.normalization_status, NormalizationStatus.COMPLETE)
        self.assertEqual(conversion_result.normalized_value_text, "277.777778")
        self.assertEqual(conversion_result.normalized_unit.value, "kWh")

    def test_warning_for_missing_unit(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:missing_unit"),
            field_inputs=(self._field_input("energy-missing-unit", "Energy Use", "100"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.normalization_status, NormalizationStatus.PARTIAL)
        self.assertIn("conversion.unit_missing", self._warning_codes(result))
        self._assert_result_validates(result, expected_outcome=ValidationOutcome.PASS_WITH_WARNINGS)

    def test_warning_for_out_of_range_value_without_correction(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:range"),
            field_inputs=(self._field_input("eff-range", "Efficiency", "150%"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.value_triplet.normalized_value.value, "150")
        self.assertEqual(field.range_check_result.value, "out_of_range")
        self.assertIn("coercion.value_out_of_range", self._warning_codes(result))

    def test_ambiguous_field_becomes_non_normalizable(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:fuel-ambiguous"),
            field_inputs=(self._field_input("fuel", "Fuel", "gas"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        self.assertFalse(result.normalized_field_records)
        self.assertEqual(len(result.non_normalizable_field_records), 1)
        self.assertEqual(
            result.normalization_run_record.normalization_status,
            NormalizationStatus.NON_NORMALIZABLE,
        )
        self.assertIn("mapping.context_ambiguous", self._warning_codes(result))

    def test_currency_without_context_is_not_complete(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:currency-missing-year"),
            field_inputs=(
                self._field_input(
                    "fuel-cost-missing-year",
                    "Fuel Cost",
                    "$100",
                    original_currency="USD",
                    mapping_context="finance",
                ),
            ),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.normalization_status, NormalizationStatus.PARTIAL)
        self.assertIn("conversion.currency_year_missing", self._warning_codes(result))

    def test_normalized_field_preserves_raw_parsed_and_normalized_values_after_conversion(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:triple"),
            field_inputs=(self._field_input("energy-triple", "Energy Use", "3200", original_unit="kWh"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.value_triplet.raw_value.value, "3200")
        self.assertEqual(field.value_triplet.parsed_value.value, "3200")
        self.assertEqual(field.value_triplet.normalized_value.value, "3.2")

    def test_conversion_rule_reference_is_preserved(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:rule-ref"),
            field_inputs=(self._field_input("energy-rule-ref", "Annual kWh", "5000", original_unit="kWh"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertIsNotNone(field.field_mapping_rule_id)
        self.assertIsNotNone(field.unit_conversion_rule_id)
        self.assertIsNotNone(result.normalization_replay_manifest)

    def test_partial_normalization_visible_at_record_level(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:partial"),
            field_inputs=(
                self._field_input("energy-partial", "Energy Use", "3200", original_unit="kWh"),
                self._field_input("fuel-partial", "Fuel", "gas"),
            ),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        self.assertIsNotNone(result.normalized_record)
        self.assertIsNotNone(result.normalized_record_set)
        self.assertIsNotNone(result.partial_normalization_record)
        self.assertEqual(result.normalized_record.normalization_status, NormalizationStatus.COMPLETE)
        self.assertEqual(result.normalization_run_record.normalization_status, NormalizationStatus.PARTIAL)
        self._assert_result_validates(result, expected_outcome=ValidationOutcome.PASS_WITH_WARNINGS)

    def test_non_normalizable_field_has_explicit_reason(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:reason"),
            field_inputs=(self._field_input("fuel-reason", "Fuel", "gas"),),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        record = result.non_normalizable_field_records[0]
        self.assertTrue(record.reason.value)

    def test_currency_conversion_with_explicit_rule(self) -> None:
        result = self.normalizer.normalize_record(
            canonical_schema_version=self.schema_version,
            record_key=RecordKey("record:currency"),
            field_inputs=(
                self._field_input(
                    "fuel-cost-complete",
                    "Fuel Cost",
                    "$100",
                    original_currency="USD",
                    currency_year=2024,
                    mapping_context="finance",
                ),
            ),
            canonical_field_definitions=self.field_definitions,
            field_mapping_rules=self.mapping_rules,
            type_coercion_rules=self.coercion_rules,
            unit_conversion_rules=self.unit_rules,
            currency_conversion_rules=self.currency_rules,
        )

        field = result.normalized_field_records[0]
        self.assertEqual(field.normalization_status, NormalizationStatus.COMPLETE)
        self.assertEqual(field.normalized_currency.value, "EUR")
        self.assertEqual(field.value_triplet.normalized_value.value, "92")
        self.assertIsNotNone(field.currency_conversion_rule_id)

    def _assert_result_validates(
        self,
        result,
        *,
        expected_outcome: ValidationOutcome = ValidationOutcome.PASS,
    ) -> None:
        report = self.validator.validate_graph(
            **result.as_validation_graph(
                canonical_schema_registry=self.registry,
                canonical_field_definitions=self.field_definitions,
                field_mapping_rules=self.mapping_rules,
                type_coercion_rules=self.coercion_rules,
                unit_conversion_rules=self.unit_rules,
                currency_conversion_rules=self.currency_rules,
            )
        )
        self.assertEqual(report.outcome, expected_outcome)

    def _warning_codes(self, result) -> set[str]:
        return {item.warning_code.value for item in result.normalization_warning_records}

    def _build_schema(self):
        registry = CanonicalSchemaRegistry(
            canonical_schema_registry_id=CanonicalSchemaRegistryId("schema-registry:normalization"),
            schema_profile_kind=SchemaProfileKind.PHASE_1_BUNDLE,
            schema_name=SchemaName("Normalization benchmark schema"),
            registry_status=CanonicalSchemaRegistryStatus.ACTIVE,
            created_at=fixed_now(),
        )
        schema_version = CanonicalSchemaVersion(
            canonical_schema_version_id=CanonicalSchemaVersionId("schema-version:normalization:v1"),
            canonical_schema_registry_id=registry.canonical_schema_registry_id,
            version_label=VersionLabel("v1"),
            version_status=CanonicalSchemaVersionStatus.ACTIVE,
            version_fingerprint=VersionFingerprint("schema:normalization:v1"),
            created_at=fixed_now(),
            effective_from=fixed_now(),
            supersedes_canonical_schema_version_id=None,
        )
        return registry, schema_version

    def _build_field_definitions(self):
        schema_version_id = self.schema_version.canonical_schema_version_id
        return (
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:energy_use"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("energy_use"),
                canonical_field_type=CanonicalFieldType.MEASURE_WITH_UNIT,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Energy use in canonical unit.",
                measurement_family=MeasurementFamily.ENERGY,
                canonical_unit=UnitRef("MWh"),
                allowed_units=(UnitRef("kWh"), UnitRef("MWh"), UnitRef("GJ")),
                canonical_currency=None,
                allowed_currencies=(),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:energy_use_kwh"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("energy_use_kwh"),
                canonical_field_type=CanonicalFieldType.MEASURE_WITH_UNIT,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Energy use in canonical kWh.",
                measurement_family=MeasurementFamily.ENERGY,
                canonical_unit=UnitRef("kWh"),
                allowed_units=(UnitRef("kWh"), UnitRef("MWh"), UnitRef("GJ")),
                canonical_currency=None,
                allowed_currencies=(),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:efficiency"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("efficiency"),
                canonical_field_type=CanonicalFieldType.PERCENTAGE,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Efficiency percentage.",
                measurement_family=MeasurementFamily.PERCENTAGE,
                canonical_unit=None,
                allowed_units=(),
                canonical_currency=None,
                allowed_currencies=(),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:report_date"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("report_date"),
                canonical_field_type=CanonicalFieldType.DATE,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Report date.",
                measurement_family=None,
                canonical_unit=None,
                allowed_units=(),
                canonical_currency=None,
                allowed_currencies=(),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:report_year"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("report_year"),
                canonical_field_type=CanonicalFieldType.YEAR,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Report year.",
                measurement_family=None,
                canonical_unit=None,
                allowed_units=(),
                canonical_currency=None,
                allowed_currencies=(),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:fuel_cost"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("fuel_cost"),
                canonical_field_type=CanonicalFieldType.CURRENCY_AMOUNT,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Fuel cost.",
                measurement_family=None,
                canonical_unit=None,
                allowed_units=(),
                canonical_currency=CurrencyCode("EUR"),
                allowed_currencies=(CurrencyCode("USD"), CurrencyCode("EUR")),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
            CanonicalFieldDefinition(
                canonical_field_definition_id=CanonicalFieldDefinitionId("field:fuel_type"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_name=CanonicalFieldName("fuel_type"),
                canonical_field_type=CanonicalFieldType.STRING_DISCIPLINED,
                field_status=FieldLifecycleStatus.ACTIVE,
                description="Fuel type string.",
                measurement_family=None,
                canonical_unit=None,
                allowed_units=(),
                canonical_currency=None,
                allowed_currencies=(),
                allowed_enum_values=(),
                required=False,
                allows_multiple=False,
                created_at=fixed_now(),
            ),
        )

    def _build_mapping_rules(self):
        schema_version_id = self.schema_version.canonical_schema_version_id
        return (
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:energy_use"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("energy_use").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Energy Use"),
                source_path_hint=None,
                source_format_hint=SourceFormatHint("pdf_table"),
                required_unit_hint=None,
                mapping_context=None,
                rule_description=RuleDescription("Map Energy Use."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:annual_kwh"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("energy_use").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Annual kWh"),
                source_path_hint=None,
                source_format_hint=SourceFormatHint("pdf_table"),
                required_unit_hint=UnitRef("kWh"),
                mapping_context=None,
                rule_description=RuleDescription("Map Annual kWh."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:efficiency"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("efficiency").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Efficiency"),
                source_path_hint=None,
                source_format_hint=None,
                required_unit_hint=None,
                mapping_context=None,
                rule_description=RuleDescription("Map Efficiency."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:report_date"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("report_date").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Report Date"),
                source_path_hint=None,
                source_format_hint=None,
                required_unit_hint=None,
                mapping_context=None,
                rule_description=RuleDescription("Map Report Date."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:report_year"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("report_year").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Report Year"),
                source_path_hint=None,
                source_format_hint=None,
                required_unit_hint=None,
                mapping_context=None,
                rule_description=RuleDescription("Map Report Year."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:fuel_cost"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("fuel_cost").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Fuel Cost"),
                source_path_hint=None,
                source_format_hint=None,
                required_unit_hint=None,
                mapping_context=MappingContext("finance"),
                rule_description=RuleDescription("Map Fuel Cost."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:fuel_type"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("fuel_type").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Fuel"),
                source_path_hint=None,
                source_format_hint=None,
                required_unit_hint=None,
                mapping_context=MappingContext("energy_context"),
                rule_description=RuleDescription("Map Fuel to fuel_type in energy context."),
                created_at=fixed_now(),
            ),
            FieldMappingRule(
                field_mapping_rule_id=FieldMappingRuleId("mapping:fuel_cost_context"),
                canonical_schema_version_id=schema_version_id,
                canonical_field_definition_id=self._field("fuel_cost").canonical_field_definition_id,
                rule_status=RuleLifecycleStatus.ACTIVE,
                original_label=OriginalLabel("Fuel"),
                source_path_hint=None,
                source_format_hint=None,
                required_unit_hint=None,
                mapping_context=MappingContext("finance"),
                rule_description=RuleDescription("Map Fuel to fuel_cost in finance context."),
                created_at=fixed_now(),
            ),
        )

    def _build_coercion_rules(self):
        schema_version_id = self.schema_version.canonical_schema_version_id
        return (
            TypeCoercionRule(
                type_coercion_rule_id=TypeCoercionRuleId("coercion:measure"),
                canonical_schema_version_id=schema_version_id,
                target_canonical_field_type=CanonicalFieldType.MEASURE_WITH_UNIT,
                coercion_safety_level=CoercionSafetyLevel.SAFE,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("Coerce scalar measures."),
                rule_fingerprint=RuleFingerprint("coercion:measure"),
                allowed_input_types=(ObservedValueType.STRING, ObservedValueType.INTEGER, ObservedValueType.DECIMAL, ObservedValueType.UNIT_VALUE),
                accepted_formats=("numeric_text",),
                null_markers=("n/a", "na"),
                true_markers=(),
                false_markers=(),
                created_at=fixed_now(),
            ),
            TypeCoercionRule(
                type_coercion_rule_id=TypeCoercionRuleId("coercion:percentage"),
                canonical_schema_version_id=schema_version_id,
                target_canonical_field_type=CanonicalFieldType.PERCENTAGE,
                coercion_safety_level=CoercionSafetyLevel.SAFE,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("Coerce percentage values."),
                rule_fingerprint=RuleFingerprint("coercion:percentage"),
                allowed_input_types=(ObservedValueType.STRING, ObservedValueType.DECIMAL, ObservedValueType.INTEGER),
                accepted_formats=("numeric_text", "percent_text"),
                null_markers=("n/a",),
                true_markers=(),
                false_markers=(),
                created_at=fixed_now(),
            ),
            TypeCoercionRule(
                type_coercion_rule_id=TypeCoercionRuleId("coercion:date"),
                canonical_schema_version_id=schema_version_id,
                target_canonical_field_type=CanonicalFieldType.DATE,
                coercion_safety_level=CoercionSafetyLevel.CONDITIONAL,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("Coerce date values."),
                rule_fingerprint=RuleFingerprint("coercion:date"),
                allowed_input_types=(ObservedValueType.STRING, ObservedValueType.DATE, ObservedValueType.YEAR),
                accepted_formats=("iso_date", "slash_date", "iso_month", "slash_month", "year_only"),
                null_markers=(),
                true_markers=(),
                false_markers=(),
                created_at=fixed_now(),
            ),
            TypeCoercionRule(
                type_coercion_rule_id=TypeCoercionRuleId("coercion:year"),
                canonical_schema_version_id=schema_version_id,
                target_canonical_field_type=CanonicalFieldType.YEAR,
                coercion_safety_level=CoercionSafetyLevel.SAFE,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("Coerce year values."),
                rule_fingerprint=RuleFingerprint("coercion:year"),
                allowed_input_types=(ObservedValueType.STRING, ObservedValueType.YEAR),
                accepted_formats=("year_only",),
                null_markers=(),
                true_markers=(),
                false_markers=(),
                created_at=fixed_now(),
            ),
            TypeCoercionRule(
                type_coercion_rule_id=TypeCoercionRuleId("coercion:currency"),
                canonical_schema_version_id=schema_version_id,
                target_canonical_field_type=CanonicalFieldType.CURRENCY_AMOUNT,
                coercion_safety_level=CoercionSafetyLevel.CONDITIONAL,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("Coerce currency amounts."),
                rule_fingerprint=RuleFingerprint("coercion:currency"),
                allowed_input_types=(ObservedValueType.STRING, ObservedValueType.CURRENCY_VALUE, ObservedValueType.DECIMAL, ObservedValueType.INTEGER),
                accepted_formats=("numeric_text", "currency_text"),
                null_markers=(),
                true_markers=(),
                false_markers=(),
                created_at=fixed_now(),
            ),
        )

    def _build_unit_rules(self):
        schema_version_id = self.schema_version.canonical_schema_version_id
        return (
            UnitConversionRule(
                unit_conversion_rule_id=UnitConversionRuleId("unit:kwh_to_mwh"),
                canonical_schema_version_id=schema_version_id,
                measurement_family=MeasurementFamily.ENERGY,
                source_unit=UnitRef("kWh"),
                target_unit=UnitRef("MWh"),
                conversion_rule_type=ConversionRuleType.FACTOR,
                conversion_factor=ConversionFactor("0.001"),
                conversion_offset=None,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("kWh to MWh."),
                rule_fingerprint=RuleFingerprint("unit:kwh_to_mwh"),
                created_at=fixed_now(),
            ),
            UnitConversionRule(
                unit_conversion_rule_id=UnitConversionRuleId("unit:gj_to_kwh"),
                canonical_schema_version_id=schema_version_id,
                measurement_family=MeasurementFamily.ENERGY,
                source_unit=UnitRef("GJ"),
                target_unit=UnitRef("kWh"),
                conversion_rule_type=ConversionRuleType.FACTOR,
                conversion_factor=ConversionFactor("277.777778"),
                conversion_offset=None,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("GJ to kWh."),
                rule_fingerprint=RuleFingerprint("unit:gj_to_kwh"),
                created_at=fixed_now(),
            ),
            UnitConversionRule(
                unit_conversion_rule_id=UnitConversionRuleId("unit:ft2_to_m2"),
                canonical_schema_version_id=schema_version_id,
                measurement_family=MeasurementFamily.AREA,
                source_unit=UnitRef("ft²"),
                target_unit=UnitRef("m²"),
                conversion_rule_type=ConversionRuleType.FACTOR,
                conversion_factor=ConversionFactor("0.092903"),
                conversion_offset=None,
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("ft² to m²."),
                rule_fingerprint=RuleFingerprint("unit:ft2_to_m2"),
                created_at=fixed_now(),
            ),
            UnitConversionRule(
                unit_conversion_rule_id=UnitConversionRuleId("unit:f_to_c"),
                canonical_schema_version_id=schema_version_id,
                measurement_family=MeasurementFamily.TEMPERATURE,
                source_unit=UnitRef("°F"),
                target_unit=UnitRef("°C"),
                conversion_rule_type=ConversionRuleType.AFFINE,
                conversion_factor=ConversionFactor("0.5555555556"),
                conversion_offset=Decimal("-17.7777777778"),
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("F to C."),
                rule_fingerprint=RuleFingerprint("unit:f_to_c"),
                created_at=fixed_now(),
            ),
        )

    def _build_currency_rules(self):
        schema_version_id = self.schema_version.canonical_schema_version_id
        return (
            CurrencyConversionRule(
                currency_conversion_rule_id=CurrencyConversionRuleId("currency:usd_to_eur_2024"),
                canonical_schema_version_id=schema_version_id,
                source_currency=CurrencyCode("USD"),
                target_currency=CurrencyCode("EUR"),
                conversion_rule_type=ConversionRuleType.DECLARED_RATE,
                conversion_factor=ConversionFactor("0.92"),
                basis_currency_year=CurrencyYear(2024),
                basis_reference="policy://fx/2024",
                rule_status=RuleLifecycleStatus.ACTIVE,
                rule_description=RuleDescription("USD to EUR 2024."),
                rule_fingerprint=RuleFingerprint("currency:usd_to_eur_2024"),
                created_at=fixed_now(),
            ),
        )

    def _field(self, name: str) -> CanonicalFieldDefinition:
        for item in self.field_definitions:
            if item.canonical_field_name.value == name:
                return item
        raise AssertionError(f"Unknown field definition: {name}")

    def _field_input(
        self,
        suffix: str,
        original_label: str,
        value: str,
        *,
        original_unit: str | None = None,
        original_currency: str | None = None,
        currency_year: int | None = None,
        mapping_context: str | None = None,
    ) -> ParsedFieldInput:
        return ParsedFieldInput(
            source_provenance=ParsedSourceProvenance(
                raw_asset_version_ref=RawAssetVersionRef("raw-version:shared"),
                extraction_metadata_ref=ExtractionMetadataRef("extraction:shared"),
                parsed_document_object_ref=ParsedDocumentObjectRef("parsed-document:shared"),
                parser_strategy_ref=ParserStrategyRef("parser:text"),
                parsed_table_object_ref=ParsedTableObjectRef("parsed-table:shared"),
                parsed_field_object_ref=ParsedFieldObjectRef(f"parsed-field:{suffix}"),
            ),
            original_label=OriginalLabel(original_label),
            raw_value=RawValue(value),
            parsed_value=ParsedValue(value),
            source_path_hint=SourcePathHint(f"$.{suffix}"),
            source_format_hint=SourceFormatHint("pdf_table"),
            mapping_context=None if mapping_context is None else MappingContext(mapping_context),
            original_unit=None if original_unit is None else UnitRef(original_unit),
            original_currency=None if original_currency is None else CurrencyCode(original_currency),
            currency_year=None if currency_year is None else CurrencyYear(currency_year),
        )


if __name__ == "__main__":
    unittest.main()
