from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
import re

from .inputs import ParsedFieldInput
from .results import TypeCoercionResult, WarningDraft
from ..domain.entities import CanonicalFieldDefinition, TypeCoercionRule
from ..domain.enums import (
    CanonicalFieldType,
    MissingnessStatus,
    MixedValueStatus,
    NormalizationStatus,
    ObservedValueType,
    PartialNormalizationStatus,
    PrecisionKind,
    RangeCheckResult,
    RuleLifecycleStatus,
    WarningSeverity,
)
from ..domain.value_objects import NonNormalizableReason, PrecisionDescriptor


_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SLASH_DATE_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")
_ISO_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
_SLASH_MONTH_RE = re.compile(r"^\d{4}/\d{2}$")
_YEAR_RE = re.compile(r"^\d{4}$")
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?$")
_NUMERIC_RE = re.compile(r"^[+-]?[0-9][0-9,]*(?:\.[0-9]+)?$")
_RANGE_RE = re.compile(r"^\s*[+-]?[0-9][0-9,]*(?:\.[0-9]+)?\s*[-–]\s*[+-]?[0-9][0-9,]*(?:\.[0-9]+)?\s*$")


class BasicTypeCoercer:
    def coerce_value(
        self,
        *,
        field_input: ParsedFieldInput,
        canonical_field_definition: CanonicalFieldDefinition,
        type_coercion_rules: tuple[TypeCoercionRule, ...],
    ) -> TypeCoercionResult:
        rule = _select_rule(
            field_input=field_input,
            canonical_field_definition=canonical_field_definition,
            type_coercion_rules=type_coercion_rules,
        )
        value = field_input.parsed_value.value.strip()

        if not value:
            return TypeCoercionResult(
                normalization_status=NormalizationStatus.COMPLETE,
                partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                normalized_value_text=None,
                numeric_value=None,
                precision_descriptor=PrecisionDescriptor(PrecisionKind.UNKNOWN),
                missingness_status=MissingnessStatus.MISSING_NOT_PRESENT,
                mixed_value_status=MixedValueStatus.NOT_MIXED,
                range_check_result=RangeCheckResult.NOT_CHECKED,
                warning_drafts=(),
                non_normalizable_reason=None,
                type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
            )
        if rule is not None:
            lowered = value.casefold()
            if lowered in {item.casefold() for item in rule.null_markers}:
                return TypeCoercionResult(
                    normalization_status=NormalizationStatus.COMPLETE,
                    partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                    normalized_value_text=None,
                    numeric_value=None,
                    precision_descriptor=PrecisionDescriptor(PrecisionKind.UNKNOWN),
                    missingness_status=MissingnessStatus.EXPLICIT_NULL,
                    mixed_value_status=MixedValueStatus.NOT_MIXED,
                    range_check_result=RangeCheckResult.NOT_CHECKED,
                    warning_drafts=(),
                    non_normalizable_reason=None,
                    type_coercion_rule_id=rule.type_coercion_rule_id,
                )

        target_type = canonical_field_definition.canonical_field_type
        if target_type is CanonicalFieldType.STRING_DISCIPLINED:
            return _disciplined_string(value, rule)
        if target_type is CanonicalFieldType.ENUM_CONTROLLED:
            return _enum_value(value, canonical_field_definition, rule)
        if target_type is CanonicalFieldType.BOOLEAN:
            return _boolean_value(value, rule)
        if target_type is CanonicalFieldType.YEAR:
            return _year_value(value, rule)
        if target_type is CanonicalFieldType.DATE:
            return _date_value(value, rule)
        if target_type is CanonicalFieldType.TIMESTAMP:
            return _timestamp_value(value, rule)
        return _numeric_like_value(value, target_type, rule)


def _disciplined_string(value: str, rule: TypeCoercionRule | None) -> TypeCoercionResult:
    normalized = " ".join(value.split())
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.COMPLETE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=normalized,
        numeric_value=None,
        precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=RangeCheckResult.NOT_CHECKED,
        warning_drafts=(),
        non_normalizable_reason=None,
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _enum_value(
    value: str,
    canonical_field_definition: CanonicalFieldDefinition,
    rule: TypeCoercionRule | None,
) -> TypeCoercionResult:
    normalized = value.casefold().strip()
    for token in canonical_field_definition.allowed_enum_values:
        if token.casefold() == normalized:
            return TypeCoercionResult(
                normalization_status=NormalizationStatus.COMPLETE,
                partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
                normalized_value_text=token,
                numeric_value=None,
                precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
                missingness_status=MissingnessStatus.NOT_MISSING,
                mixed_value_status=MixedValueStatus.NOT_MIXED,
                range_check_result=RangeCheckResult.NOT_CHECKED,
                warning_drafts=(),
                non_normalizable_reason=None,
                type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
            )
    return _not_normalizable(
        rule,
        "Coercion to controlled enum failed because the parsed token is not part of the allowed enum set.",
    )


def _boolean_value(value: str, rule: TypeCoercionRule | None) -> TypeCoercionResult:
    if rule is None:
        return _not_normalizable(
            None,
            "Boolean coercion requires an explicit type coercion rule with true/false markers.",
        )
    lowered = value.casefold()
    if lowered in {item.casefold() for item in rule.true_markers}:
        return _simple_complete("true", rule)
    if lowered in {item.casefold() for item in rule.false_markers}:
        return _simple_complete("false", rule)
    return _not_normalizable(
        rule,
        "Boolean coercion failed because the parsed value does not match the governed true/false markers.",
    )


def _year_value(value: str, rule: TypeCoercionRule | None) -> TypeCoercionResult:
    if not _YEAR_RE.fullmatch(value):
        return _not_normalizable(rule, "Year coercion requires a four-digit year.")
    year = int(value)
    range_check = RangeCheckResult.IN_RANGE if 1900 <= year <= 3000 else RangeCheckResult.OUT_OF_RANGE
    warnings = ()
    if range_check is RangeCheckResult.OUT_OF_RANGE:
        warnings = (
            WarningDraft(
                code="coercion.year_out_of_range",
                severity=WarningSeverity.MODERATE,
                message="Year value is outside the supported canonical range.",
            ),
        )
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.COMPLETE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=value,
        numeric_value=Decimal(str(year)),
        precision_descriptor=PrecisionDescriptor(PrecisionKind.YEAR),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=range_check,
        warning_drafts=warnings,
        non_normalizable_reason=None,
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _date_value(value: str, rule: TypeCoercionRule | None) -> TypeCoercionResult:
    if _ISO_DATE_RE.fullmatch(value):
        return _date_complete(value, PrecisionKind.DAY, rule)
    if _SLASH_DATE_RE.fullmatch(value):
        year, month, day = value.split("/")
        return _date_complete(f"{year}-{month}-{day}", PrecisionKind.DAY, rule)
    if _ISO_MONTH_RE.fullmatch(value):
        return _date_partial(f"{value}", PrecisionKind.MONTH, rule)
    if _SLASH_MONTH_RE.fullmatch(value):
        year, month = value.split("/")
        return _date_partial(f"{year}-{month}", PrecisionKind.MONTH, rule)
    if _YEAR_RE.fullmatch(value):
        return _date_partial(value, PrecisionKind.YEAR, rule)
    return _not_normalizable(rule, "Date coercion requires a supported date literal.")


def _timestamp_value(value: str, rule: TypeCoercionRule | None) -> TypeCoercionResult:
    if not _TIMESTAMP_RE.fullmatch(value):
        return _not_normalizable(rule, "Timestamp coercion requires an ISO-like timestamp literal.")
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.COMPLETE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=value,
        numeric_value=None,
        precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=RangeCheckResult.NOT_CHECKED,
        warning_drafts=(),
        non_normalizable_reason=None,
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _numeric_like_value(
    value: str,
    target_type: CanonicalFieldType,
    rule: TypeCoercionRule | None,
) -> TypeCoercionResult:
    if _RANGE_RE.fullmatch(value):
        return TypeCoercionResult(
            normalization_status=NormalizationStatus.PARTIAL,
            partial_normalization_status=PartialNormalizationStatus.PARTIAL_USEFUL,
            normalized_value_text=None,
            numeric_value=None,
            precision_descriptor=PrecisionDescriptor(PrecisionKind.APPROXIMATE, "range expression"),
            missingness_status=MissingnessStatus.NOT_PARSEABLE,
            mixed_value_status=MixedValueStatus.RANGE_EXPRESSION,
            range_check_result=RangeCheckResult.SUSPICIOUS,
            warning_drafts=(
                WarningDraft(
                    code="coercion.range_expression_detected",
                    severity=WarningSeverity.MODERATE,
                    message="Parsed numeric value is a range expression and cannot be normalized as a single complete value.",
                ),
            ),
            non_normalizable_reason=NonNormalizableReason(
                "Numeric coercion found a range expression instead of a scalar value."
            ),
            type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
        )
    sanitized = _sanitize_numeric(value)
    if sanitized is None:
        return _not_normalizable(rule, "Numeric coercion requires a supported scalar numeric literal.")
    try:
        decimal_value = Decimal(sanitized)
    except InvalidOperation:
        return _not_normalizable(rule, "Numeric coercion requires a valid decimal literal.")

    if target_type is CanonicalFieldType.INTEGER:
        if decimal_value != decimal_value.to_integral_value():
            return _not_normalizable(rule, "Integer coercion cannot accept fractional values.")
        normalized = format(decimal_value.quantize(Decimal("1")), "f")
    else:
        normalized = _format_decimal(decimal_value)

    range_check = _default_range_check(target_type, decimal_value)
    warnings: list[WarningDraft] = []
    if range_check is RangeCheckResult.SUSPICIOUS:
        warnings.append(
            WarningDraft(
                code="coercion.value_suspicious",
                severity=WarningSeverity.MODERATE,
                message="Coerced numeric value is suspicious but still usable.",
            )
        )
    if range_check is RangeCheckResult.OUT_OF_RANGE:
        warnings.append(
            WarningDraft(
                code="coercion.value_out_of_range",
                severity=WarningSeverity.MODERATE,
                message="Coerced numeric value is outside the expected canonical range.",
            )
        )
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.COMPLETE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=normalized,
        numeric_value=decimal_value,
        precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=range_check,
        warning_drafts=tuple(warnings),
        non_normalizable_reason=None,
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _date_complete(
    value: str,
    precision_kind: PrecisionKind,
    rule: TypeCoercionRule | None,
) -> TypeCoercionResult:
    year, month, day = value.split("-")
    date(int(year), int(month), int(day))
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.COMPLETE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=value,
        numeric_value=None,
        precision_descriptor=PrecisionDescriptor(precision_kind),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=RangeCheckResult.NOT_CHECKED,
        warning_drafts=(),
        non_normalizable_reason=None,
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _date_partial(
    value: str,
    precision_kind: PrecisionKind,
    rule: TypeCoercionRule | None,
) -> TypeCoercionResult:
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.PARTIAL,
        partial_normalization_status=PartialNormalizationStatus.PARTIAL_USEFUL,
        normalized_value_text=value,
        numeric_value=None,
        precision_descriptor=PrecisionDescriptor(precision_kind),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=RangeCheckResult.NOT_CHECKED,
        warning_drafts=(
            WarningDraft(
                code="coercion.date_precision_incomplete",
                severity=WarningSeverity.MODERATE,
                message="Date coercion preserved the available precision without inventing a full calendar date.",
            ),
        ),
        non_normalizable_reason=NonNormalizableReason(
            "Date coercion preserved only partial temporal precision."
        ),
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _simple_complete(value: str, rule: TypeCoercionRule | None) -> TypeCoercionResult:
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.COMPLETE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=value,
        numeric_value=None,
        precision_descriptor=PrecisionDescriptor(PrecisionKind.EXACT),
        missingness_status=MissingnessStatus.NOT_MISSING,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=RangeCheckResult.NOT_CHECKED,
        warning_drafts=(),
        non_normalizable_reason=None,
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _not_normalizable(
    rule: TypeCoercionRule | None,
    reason: str,
) -> TypeCoercionResult:
    return TypeCoercionResult(
        normalization_status=NormalizationStatus.NON_NORMALIZABLE,
        partial_normalization_status=PartialNormalizationStatus.NOT_PARTIAL,
        normalized_value_text=None,
        numeric_value=None,
        precision_descriptor=PrecisionDescriptor(PrecisionKind.UNKNOWN),
        missingness_status=MissingnessStatus.NOT_NORMALIZABLE,
        mixed_value_status=MixedValueStatus.NOT_MIXED,
        range_check_result=RangeCheckResult.NOT_CHECKED,
        warning_drafts=(),
        non_normalizable_reason=NonNormalizableReason(reason),
        type_coercion_rule_id=None if rule is None else rule.type_coercion_rule_id,
    )


def _sanitize_numeric(value: str) -> str | None:
    stripped = value.strip()
    if stripped.endswith("%"):
        stripped = stripped[:-1]
    stripped = stripped.lstrip("$€£")
    stripped = stripped.replace(" ", "").replace(",", "")
    return stripped if _NUMERIC_RE.fullmatch(stripped) else None


def _format_decimal(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _default_range_check(
    target_type: CanonicalFieldType,
    decimal_value: Decimal,
) -> RangeCheckResult:
    if target_type is CanonicalFieldType.PERCENTAGE:
        if decimal_value < Decimal("0") or decimal_value > Decimal("100"):
            return RangeCheckResult.OUT_OF_RANGE
        return RangeCheckResult.IN_RANGE
    if target_type is CanonicalFieldType.YEAR:
        if decimal_value < Decimal("1900") or decimal_value > Decimal("3000"):
            return RangeCheckResult.OUT_OF_RANGE
        return RangeCheckResult.IN_RANGE
    if target_type in {
        CanonicalFieldType.MEASURE_WITH_UNIT,
        CanonicalFieldType.CURRENCY_AMOUNT,
        CanonicalFieldType.INTEGER,
        CanonicalFieldType.DECIMAL,
        CanonicalFieldType.RATIO,
    }:
        if decimal_value < 0:
            return RangeCheckResult.SUSPICIOUS
        return RangeCheckResult.IN_RANGE
    return RangeCheckResult.NOT_CHECKED


def _select_rule(
    *,
    field_input: ParsedFieldInput,
    canonical_field_definition: CanonicalFieldDefinition,
    type_coercion_rules: tuple[TypeCoercionRule, ...],
) -> TypeCoercionRule | None:
    observed_types = _observed_types(field_input)
    format_tokens = _format_tokens(field_input)
    for rule in type_coercion_rules:
        if rule.rule_status is not RuleLifecycleStatus.ACTIVE:
            continue
        if (
            rule.canonical_schema_version_id
            != canonical_field_definition.canonical_schema_version_id
        ):
            continue
        if rule.target_canonical_field_type is not canonical_field_definition.canonical_field_type:
            continue
        if rule.allowed_input_types and not set(rule.allowed_input_types).intersection(observed_types):
            continue
        if rule.accepted_formats and not set(rule.accepted_formats).intersection(format_tokens):
            continue
        return rule
    return None


def _observed_types(field_input: ParsedFieldInput) -> set[ObservedValueType]:
    value = field_input.parsed_value.value.strip()
    observed: set[ObservedValueType] = {ObservedValueType.STRING}
    if field_input.original_unit is not None:
        observed.add(ObservedValueType.UNIT_VALUE)
    if field_input.original_currency is not None:
        observed.add(ObservedValueType.CURRENCY_VALUE)
    if not value:
        observed.add(ObservedValueType.NULL_LITERAL)
        return observed
    if _TIMESTAMP_RE.fullmatch(value):
        observed.add(ObservedValueType.TIMESTAMP)
    elif _ISO_DATE_RE.fullmatch(value) or _SLASH_DATE_RE.fullmatch(value):
        observed.add(ObservedValueType.DATE)
    elif _YEAR_RE.fullmatch(value):
        observed.add(ObservedValueType.YEAR)
    elif _sanitize_numeric(value) is not None:
        numeric = _sanitize_numeric(value)
        if numeric is not None and "." in numeric:
            observed.add(ObservedValueType.DECIMAL)
        elif numeric is not None:
            observed.add(ObservedValueType.INTEGER)
    return observed


def _format_tokens(field_input: ParsedFieldInput) -> set[str]:
    value = field_input.parsed_value.value.strip()
    tokens = {"string"}
    if value.endswith("%"):
        tokens.add("percent_text")
    if value.startswith(("$", "€", "£")):
        tokens.add("currency_text")
    if _ISO_DATE_RE.fullmatch(value):
        tokens.add("iso_date")
    if _SLASH_DATE_RE.fullmatch(value):
        tokens.add("slash_date")
    if _ISO_MONTH_RE.fullmatch(value):
        tokens.add("iso_month")
    if _SLASH_MONTH_RE.fullmatch(value):
        tokens.add("slash_month")
    if _YEAR_RE.fullmatch(value):
        tokens.add("year_only")
    if _TIMESTAMP_RE.fullmatch(value):
        tokens.add("iso_timestamp")
    if _sanitize_numeric(value) is not None:
        tokens.add("numeric_text")
    return tokens
