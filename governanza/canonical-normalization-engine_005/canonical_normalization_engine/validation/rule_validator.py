from __future__ import annotations

from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode
from ..domain.entities import (
    CurrencyConversionRule,
    FieldMappingRule,
    TypeCoercionRule,
    UnitConversionRule,
)


def validate_field_mapping_rule(
    mapping_rule: FieldMappingRule,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    version = context.versions_by_id.get(mapping_rule.canonical_schema_version_id)
    if version is None:
        collector.add(
            RuleCode.MAPPING_SCHEMA_VERSION_REFERENCE_INVALID,
            "Field mapping rule references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )
    field_definition = context.fields_by_id.get(mapping_rule.canonical_field_definition_id)
    if field_definition is None:
        collector.add(
            RuleCode.MAPPING_FIELD_REFERENCE_INVALID,
            "Field mapping rule targets a canonical field definition that is not present in validation context.",
            field_ref="canonical_field_definition_id",
        )
        return
    if field_definition.canonical_schema_version_id != mapping_rule.canonical_schema_version_id:
        collector.add(
            RuleCode.MAPPING_FIELD_SCHEMA_MISMATCH,
            "Field mapping rule and target canonical field definition belong to different schema versions.",
            field_ref="canonical_field_definition_id",
        )


def validate_type_coercion_rule(
    coercion_rule: TypeCoercionRule,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if coercion_rule.canonical_schema_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.COERCION_SCHEMA_VERSION_REFERENCE_INVALID,
            "Type coercion rule references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )


def validate_unit_conversion_rule(
    unit_rule: UnitConversionRule,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if unit_rule.canonical_schema_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.UNIT_CONVERSION_SCHEMA_VERSION_REFERENCE_INVALID,
            "Unit conversion rule references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )


def validate_currency_conversion_rule(
    currency_rule: CurrencyConversionRule,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if currency_rule.canonical_schema_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.CURRENCY_CONVERSION_SCHEMA_VERSION_REFERENCE_INVALID,
            "Currency conversion rule references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )
