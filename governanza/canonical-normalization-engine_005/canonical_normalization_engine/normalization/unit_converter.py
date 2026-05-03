from __future__ import annotations

from decimal import Decimal

from .results import UnitConversionResult, WarningDraft
from ..domain.entities import CanonicalFieldDefinition, UnitConversionRule
from ..domain.enums import (
    CanonicalFieldType,
    NormalizationStatus,
    PartialNormalizationStatus,
    RuleLifecycleStatus,
    WarningSeverity,
)
from ..domain.value_objects import NonNormalizableReason, UnitRef


class BasicUnitConverter:
    def convert_value(
        self,
        *,
        canonical_field_definition: CanonicalFieldDefinition,
        original_unit: UnitRef | None,
        numeric_value: Decimal | None,
        unit_conversion_rules: tuple[UnitConversionRule, ...],
    ) -> UnitConversionResult:
        if canonical_field_definition.canonical_field_type is not CanonicalFieldType.MEASURE_WITH_UNIT:
            return UnitConversionResult(
                normalization_status=NormalizationStatus.COMPLETE,
                partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                normalized_value_text=None if numeric_value is None else _format_decimal(numeric_value),
                normalized_unit=None,
                unit_conversion_rule_id=None,
                warning_drafts=(),
                non_normalizable_reason=None,
            )
        if numeric_value is None:
            return UnitConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_unit=None,
                unit_conversion_rule_id=None,
                warning_drafts=(),
                non_normalizable_reason=NonNormalizableReason(
                    "Unit conversion cannot proceed without a scalar numeric value."
                ),
            )

        target_unit = canonical_field_definition.canonical_unit
        if original_unit is None:
            return UnitConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_unit=None,
                unit_conversion_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="conversion.unit_missing",
                        severity=WarningSeverity.MODERATE,
                        message="Original unit is missing, so canonical unit conversion cannot be completed.",
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Original unit is missing for a unit-bearing canonical field."
                ),
            )
        if target_unit is None or original_unit == target_unit:
            return UnitConversionResult(
                normalization_status=NormalizationStatus.COMPLETE,
                partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                normalized_value_text=_format_decimal(numeric_value),
                normalized_unit=original_unit if target_unit is None else target_unit,
                unit_conversion_rule_id=None,
                warning_drafts=(),
                non_normalizable_reason=None,
            )
        rule = _select_rule(
            canonical_field_definition=canonical_field_definition,
            source_unit=original_unit,
            target_unit=target_unit,
            unit_conversion_rules=unit_conversion_rules,
        )
        if rule is None:
            return UnitConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_unit=None,
                unit_conversion_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="conversion.unit_rule_missing",
                        severity=WarningSeverity.MODERATE,
                        message="No explicit unit conversion rule can convert the original unit to the canonical unit.",
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "No explicit unit conversion rule matched the original unit and canonical unit."
                ),
            )
        if rule.conversion_offset is None:
            converted_value = numeric_value * rule.conversion_factor.value
        else:
            converted_value = (numeric_value * rule.conversion_factor.value) + rule.conversion_offset
        return UnitConversionResult(
            normalization_status=NormalizationStatus.COMPLETE,
            partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
            normalized_value_text=_format_decimal(converted_value),
            normalized_unit=rule.target_unit,
            unit_conversion_rule_id=rule.unit_conversion_rule_id,
            warning_drafts=(),
            non_normalizable_reason=None,
        )


def _select_rule(
    *,
    canonical_field_definition: CanonicalFieldDefinition,
    source_unit: UnitRef,
    target_unit: UnitRef,
    unit_conversion_rules: tuple[UnitConversionRule, ...],
) -> UnitConversionRule | None:
    for rule in unit_conversion_rules:
        if rule.rule_status is not RuleLifecycleStatus.ACTIVE:
            continue
        if rule.canonical_schema_version_id != canonical_field_definition.canonical_schema_version_id:
            continue
        if rule.measurement_family != canonical_field_definition.measurement_family:
            continue
        if rule.source_unit != source_unit or rule.target_unit != target_unit:
            continue
        return rule
    return None


def _format_decimal(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"
