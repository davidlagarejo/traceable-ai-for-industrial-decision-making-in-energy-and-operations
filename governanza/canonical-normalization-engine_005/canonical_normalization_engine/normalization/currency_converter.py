from __future__ import annotations

from decimal import Decimal

from .results import CurrencyConversionResult, WarningDraft
from ..domain.entities import CanonicalFieldDefinition, CurrencyConversionRule
from ..domain.enums import (
    CanonicalFieldType,
    ConversionRuleType,
    NormalizationStatus,
    PartialNormalizationStatus,
    RuleLifecycleStatus,
    WarningSeverity,
)
from ..domain.value_objects import CurrencyCode, CurrencyYear, NonNormalizableReason


class BasicCurrencyConverter:
    def convert_value(
        self,
        *,
        canonical_field_definition: CanonicalFieldDefinition,
        original_currency: CurrencyCode | None,
        currency_year: CurrencyYear | None,
        numeric_value: Decimal | None,
        currency_conversion_rules: tuple[CurrencyConversionRule, ...],
    ) -> CurrencyConversionResult:
        if canonical_field_definition.canonical_field_type is not CanonicalFieldType.CURRENCY_AMOUNT:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.COMPLETE,
                partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                normalized_value_text=None if numeric_value is None else _format_decimal(numeric_value),
                normalized_currency=None,
                currency_conversion_rule_id=None,
                warning_drafts=(),
                non_normalizable_reason=None,
            )
        if numeric_value is None:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_currency=None,
                currency_conversion_rule_id=None,
                warning_drafts=(),
                non_normalizable_reason=NonNormalizableReason(
                    "Currency conversion cannot proceed without a scalar numeric value."
                ),
            )
        target_currency = canonical_field_definition.canonical_currency
        if original_currency is None:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_currency=None,
                currency_conversion_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="conversion.currency_missing",
                        severity=WarningSeverity.MODERATE,
                        message="Original currency is missing, so canonical currency conversion cannot be completed.",
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Original currency is missing for a currency-bearing canonical field."
                ),
            )
        if target_currency is None or original_currency == target_currency:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.COMPLETE,
                partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                normalized_value_text=_format_decimal(numeric_value),
                normalized_currency=original_currency if target_currency is None else target_currency,
                currency_conversion_rule_id=None,
                warning_drafts=(),
                non_normalizable_reason=None,
            )
        if currency_year is None:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_currency=None,
                currency_conversion_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="conversion.currency_year_missing",
                        severity=WarningSeverity.MODERATE,
                        message="Currency conversion requires a currency year or equivalent basis context.",
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Currency conversion requires a currency year or equivalent basis context."
                ),
            )
        rule = _select_rule(
            canonical_field_definition=canonical_field_definition,
            source_currency=original_currency,
            target_currency=target_currency,
            currency_year=currency_year,
            currency_conversion_rules=currency_conversion_rules,
        )
        if rule is None:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_currency=None,
                currency_conversion_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="conversion.currency_rule_missing",
                        severity=WarningSeverity.MODERATE,
                        message="No explicit currency conversion rule can convert the original currency to the canonical currency with the available basis context.",
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "No explicit currency conversion rule matched the original currency, canonical currency and basis context."
                ),
            )
        if rule.conversion_rule_type is not ConversionRuleType.DECLARED_RATE or rule.conversion_factor is None:
            return CurrencyConversionResult(
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_value_text=None,
                normalized_currency=None,
                currency_conversion_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="conversion.currency_rule_not_executable",
                        severity=WarningSeverity.MODERATE,
                        message="The available currency conversion rule is registered but not executable in this MVP without an external rate table.",
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Currency conversion rule exists but is not executable without an external rate table."
                ),
            )
        converted_value = numeric_value * rule.conversion_factor.value
        return CurrencyConversionResult(
            normalization_status=NormalizationStatus.COMPLETE,
            partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
            normalized_value_text=_format_decimal(converted_value),
            normalized_currency=rule.target_currency,
            currency_conversion_rule_id=rule.currency_conversion_rule_id,
            warning_drafts=(),
            non_normalizable_reason=None,
        )


def _select_rule(
    *,
    canonical_field_definition: CanonicalFieldDefinition,
    source_currency: CurrencyCode,
    target_currency: CurrencyCode,
    currency_year: CurrencyYear,
    currency_conversion_rules: tuple[CurrencyConversionRule, ...],
) -> CurrencyConversionRule | None:
    for rule in currency_conversion_rules:
        if rule.rule_status is not RuleLifecycleStatus.ACTIVE:
            continue
        if rule.canonical_schema_version_id != canonical_field_definition.canonical_schema_version_id:
            continue
        if rule.source_currency != source_currency or rule.target_currency != target_currency:
            continue
        if rule.basis_currency_year is not None and rule.basis_currency_year != currency_year:
            continue
        return rule
    return None


def _format_decimal(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"
