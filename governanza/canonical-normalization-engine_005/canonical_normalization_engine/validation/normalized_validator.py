from __future__ import annotations

from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode
from ..domain.enums import MissingnessStatus, NormalizationStatus, RangeCheckResult
from ..domain.records import NormalizedFieldRecord, NormalizedRecord, NormalizedRecordSet


def validate_normalized_field_record(
    normalized_field: NormalizedFieldRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if normalized_field.missingness_status is MissingnessStatus.NOT_MISSING:
        if not (
            normalized_field.value_triplet.raw_value.value
            or normalized_field.value_triplet.parsed_value.value
        ):
            collector.add(
                RuleCode.NORMALIZED_FIELD_TRIPLE_VALUE_INCOHERENT,
                "Normalized field declares NOT_MISSING but both raw_value and parsed_value are empty.",
                field_ref="value_triplet",
            )
    if context is None:
        _emit_status_warnings(normalized_field, collector)
        return
    run = context.runs_by_id.get(normalized_field.normalization_run_record_id)
    if run is None:
        collector.add(
            RuleCode.NORMALIZED_FIELD_RUN_REFERENCE_INVALID,
            "Normalized field references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    record = None
    if normalized_field.normalized_record_id is not None:
        record = context.normalized_records_by_id.get(normalized_field.normalized_record_id)
        if record is None:
            collector.add(
                RuleCode.NORMALIZED_FIELD_RECORD_REFERENCE_INVALID,
                "Normalized field references a normalized record that is not present in validation context.",
                field_ref="normalized_record_id",
            )
        else:
            if record.normalization_run_record_id != normalized_field.normalization_run_record_id:
                collector.add(
                    RuleCode.NORMALIZED_FIELD_RECORD_RUN_MISMATCH,
                    "Normalized field and parent normalized record belong to different normalization runs.",
                    field_ref="normalized_record_id",
                )
            if normalized_field.normalized_field_record_id not in record.normalized_field_record_ids:
                collector.add(
                    RuleCode.NORMALIZED_FIELD_RECORD_PARENT_MISMATCH,
                    "Parent normalized record does not include the normalized field in its child field list.",
                    field_ref="normalized_record_id",
                )
    field_definition = None
    if normalized_field.canonical_field_definition_id is not None:
        field_definition = context.fields_by_id.get(normalized_field.canonical_field_definition_id)
        if field_definition is None:
            collector.add(
                RuleCode.NORMALIZED_FIELD_FIELD_REFERENCE_INVALID,
                "Normalized field references a canonical field definition that is not present in validation context.",
                field_ref="canonical_field_definition_id",
            )
        else:
            if (
                run is not None
                and field_definition.canonical_schema_version_id != run.canonical_schema_version_id
            ):
                collector.add(
                    RuleCode.NORMALIZED_FIELD_FIELD_SCHEMA_MISMATCH,
                    "Normalized field canonical field definition belongs to a different schema version than the normalization run.",
                    field_ref="canonical_field_definition_id",
                )
            if (
                normalized_field.normalized_field_type is not None
                and normalized_field.normalized_field_type
                is not field_definition.canonical_field_type
            ):
                collector.add(
                    RuleCode.NORMALIZED_FIELD_TRIPLE_VALUE_INCOHERENT,
                    "Normalized field type does not match the canonical field definition type.",
                    field_ref="normalized_field_type",
                )
    if normalized_field.field_mapping_rule_id is not None:
        mapping_rule = context.mapping_rules_by_id.get(normalized_field.field_mapping_rule_id)
        if mapping_rule is None:
            collector.add(
                RuleCode.NORMALIZED_FIELD_MAPPING_REFERENCE_INVALID,
                "Normalized field references a field mapping rule that is not present in validation context.",
                field_ref="field_mapping_rule_id",
            )
        else:
            if (
                normalized_field.canonical_field_definition_id is not None
                and mapping_rule.canonical_field_definition_id
                != normalized_field.canonical_field_definition_id
            ):
                collector.add(
                    RuleCode.NORMALIZED_FIELD_MAPPING_FIELD_MISMATCH,
                    "Normalized field mapping rule targets a different canonical field definition.",
                    field_ref="field_mapping_rule_id",
                )
            if run is not None and mapping_rule.canonical_schema_version_id != run.canonical_schema_version_id:
                collector.add(
                    RuleCode.NORMALIZED_FIELD_MAPPING_SCHEMA_MISMATCH,
                    "Normalized field mapping rule belongs to a different schema version than the normalization run.",
                    field_ref="field_mapping_rule_id",
                )
    elif normalized_field.normalization_status is NormalizationStatus.COMPLETE:
        collector.add(
            RuleCode.NORMALIZED_FIELD_MAPPING_REFERENCE_INVALID,
            "Complete normalized fields must reference an effective field mapping rule.",
            field_ref="field_mapping_rule_id",
        )
    if normalized_field.type_coercion_rule_id is not None:
        coercion_rule = context.coercion_rules_by_id.get(normalized_field.type_coercion_rule_id)
        if coercion_rule is None:
            collector.add(
                RuleCode.NORMALIZED_FIELD_COERCION_REFERENCE_INVALID,
                "Normalized field references a type coercion rule that is not present in validation context.",
                field_ref="type_coercion_rule_id",
            )
        elif run is not None and coercion_rule.canonical_schema_version_id != run.canonical_schema_version_id:
            collector.add(
                RuleCode.NORMALIZED_FIELD_COERCION_SCHEMA_MISMATCH,
                "Normalized field coercion rule belongs to a different schema version than the normalization run.",
                field_ref="type_coercion_rule_id",
            )
    if normalized_field.unit_conversion_rule_id is not None:
        unit_rule = context.unit_rules_by_id.get(normalized_field.unit_conversion_rule_id)
        if unit_rule is None:
            collector.add(
                RuleCode.NORMALIZED_FIELD_UNIT_RULE_REFERENCE_INVALID,
                "Normalized field references a unit conversion rule that is not present in validation context.",
                field_ref="unit_conversion_rule_id",
            )
        else:
            if run is not None and unit_rule.canonical_schema_version_id != run.canonical_schema_version_id:
                collector.add(
                    RuleCode.NORMALIZED_FIELD_UNIT_RULE_SCHEMA_MISMATCH,
                    "Normalized field unit conversion rule belongs to a different schema version than the normalization run.",
                    field_ref="unit_conversion_rule_id",
                )
            if (
                normalized_field.original_unit is None
                or normalized_field.normalized_unit is None
                or unit_rule.source_unit != normalized_field.original_unit
                or unit_rule.target_unit != normalized_field.normalized_unit
            ):
                collector.add(
                    RuleCode.NORMALIZED_FIELD_UNIT_RULE_INCOHERENT,
                    "Normalized field unit conversion rule does not match original_unit and normalized_unit.",
                    field_ref="unit_conversion_rule_id",
                )
    if normalized_field.currency_conversion_rule_id is not None:
        currency_rule = context.currency_rules_by_id.get(normalized_field.currency_conversion_rule_id)
        if currency_rule is None:
            collector.add(
                RuleCode.NORMALIZED_FIELD_CURRENCY_RULE_REFERENCE_INVALID,
                "Normalized field references a currency conversion rule that is not present in validation context.",
                field_ref="currency_conversion_rule_id",
            )
        else:
            if run is not None and currency_rule.canonical_schema_version_id != run.canonical_schema_version_id:
                collector.add(
                    RuleCode.NORMALIZED_FIELD_CURRENCY_RULE_SCHEMA_MISMATCH,
                    "Normalized field currency conversion rule belongs to a different schema version than the normalization run.",
                    field_ref="currency_conversion_rule_id",
                )
            if (
                normalized_field.original_currency is None
                or normalized_field.normalized_currency is None
                or currency_rule.source_currency != normalized_field.original_currency
                or currency_rule.target_currency != normalized_field.normalized_currency
            ):
                collector.add(
                    RuleCode.NORMALIZED_FIELD_CURRENCY_RULE_INCOHERENT,
                    "Normalized field currency conversion rule does not match original_currency and normalized_currency.",
                    field_ref="currency_conversion_rule_id",
                )
    _emit_status_warnings(normalized_field, collector)


def _emit_status_warnings(
    normalized_field: NormalizedFieldRecord,
    collector: ViolationCollector,
) -> None:
    if normalized_field.normalization_status is NormalizationStatus.PARTIAL:
        collector.add(
            RuleCode.NORMALIZED_FIELD_PARTIAL_DECLARED,
            "Normalized field is explicitly marked as partial normalization.",
        )
    if normalized_field.normalization_status is NormalizationStatus.NON_NORMALIZABLE:
        collector.add(
            RuleCode.NORMALIZED_FIELD_NON_NORMALIZABLE_DECLARED,
            "Normalized field is explicitly marked as non-normalizable.",
        )
    if normalized_field.range_check_result in {
        RangeCheckResult.SUSPICIOUS,
        RangeCheckResult.OUT_OF_RANGE,
    }:
        collector.add(
            RuleCode.NORMALIZED_FIELD_RANGE_ATTENTION,
            "Normalized field is flagged as suspicious or out_of_range.",
            field_ref="range_check_result",
        )


def validate_normalized_record(
    normalized_record: NormalizedRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    run = context.runs_by_id.get(normalized_record.normalization_run_record_id)
    if run is None:
        collector.add(
            RuleCode.NORMALIZED_RECORD_RUN_REFERENCE_INVALID,
            "Normalized record references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    record_set = context.normalized_record_sets_by_id.get(normalized_record.normalized_record_set_id)
    if record_set is None:
        collector.add(
            RuleCode.NORMALIZED_RECORD_RECORD_SET_REFERENCE_INVALID,
            "Normalized record references a normalized record set that is not present in validation context.",
            field_ref="normalized_record_set_id",
        )
    else:
        if record_set.normalization_run_record_id != normalized_record.normalization_run_record_id:
            collector.add(
                RuleCode.NORMALIZED_RECORD_FIELD_RUN_MISMATCH,
                "Normalized record and parent record set belong to different normalization runs.",
                field_ref="normalized_record_set_id",
            )
        if normalized_record.normalized_record_id not in record_set.normalized_record_ids:
            collector.add(
                RuleCode.NORMALIZED_RECORD_FIELD_PARENT_MISMATCH,
                "Parent normalized record set does not include the normalized record in its child record list.",
                field_ref="normalized_record_set_id",
            )
    child_statuses: list[NormalizationStatus] = []
    for field_id in normalized_record.normalized_field_record_ids:
        normalized_field = context.normalized_fields_by_id.get(field_id)
        if normalized_field is None:
            collector.add(
                RuleCode.NORMALIZED_RECORD_FIELD_REFERENCE_INVALID,
                "Normalized record references a normalized field that is not present in validation context.",
                field_ref="normalized_field_record_ids",
            )
            continue
        child_statuses.append(normalized_field.normalization_status)
        if normalized_field.normalization_run_record_id != normalized_record.normalization_run_record_id:
            collector.add(
                RuleCode.NORMALIZED_RECORD_FIELD_RUN_MISMATCH,
                "Normalized record contains a normalized field from a different normalization run.",
                field_ref="normalized_field_record_ids",
            )
        if normalized_field.normalized_record_id != normalized_record.normalized_record_id:
            collector.add(
                RuleCode.NORMALIZED_RECORD_FIELD_PARENT_MISMATCH,
                "Normalized field does not point back to the normalized record as its parent.",
                field_ref="normalized_field_record_ids",
            )
    if normalized_record.normalization_status is NormalizationStatus.COMPLETE:
        if any(status is not NormalizationStatus.COMPLETE for status in child_statuses):
            collector.add(
                RuleCode.NORMALIZED_RECORD_COMPLETE_INCOHERENT,
                "Normalized record declares COMPLETE but contains non-complete normalized fields.",
                field_ref="normalization_status",
            )
    if normalized_record.normalization_status is NormalizationStatus.PARTIAL:
        if child_statuses and all(status is NormalizationStatus.COMPLETE for status in child_statuses):
            collector.add(
                RuleCode.NORMALIZED_RECORD_PARTIAL_INCOHERENT,
                "Normalized record declares PARTIAL but all referenced normalized fields are complete.",
                field_ref="normalization_status",
            )


def validate_normalized_record_set(
    record_set: NormalizedRecordSet,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    run = context.runs_by_id.get(record_set.normalization_run_record_id)
    if run is None:
        collector.add(
            RuleCode.RECORD_SET_RUN_REFERENCE_INVALID,
            "Normalized record set references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    if record_set.canonical_schema_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.RECORD_SET_SCHEMA_VERSION_REFERENCE_INVALID,
            "Normalized record set references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )
    elif run is not None and record_set.canonical_schema_version_id != run.canonical_schema_version_id:
        collector.add(
            RuleCode.RECORD_SET_RUN_SCHEMA_MISMATCH,
            "Normalized record set schema version does not match the normalization run schema version.",
            field_ref="canonical_schema_version_id",
        )
    child_statuses: list[NormalizationStatus] = []
    for record_id in record_set.normalized_record_ids:
        normalized_record = context.normalized_records_by_id.get(record_id)
        if normalized_record is None:
            collector.add(
                RuleCode.RECORD_SET_RECORD_REFERENCE_INVALID,
                "Normalized record set references a normalized record that is not present in validation context.",
                field_ref="normalized_record_ids",
            )
            continue
        child_statuses.append(normalized_record.normalization_status)
        if normalized_record.normalization_run_record_id != record_set.normalization_run_record_id:
            collector.add(
                RuleCode.RECORD_SET_RECORD_RUN_MISMATCH,
                "Normalized record set contains a normalized record from a different normalization run.",
                field_ref="normalized_record_ids",
            )
        if normalized_record.normalized_record_set_id != record_set.normalized_record_set_id:
            collector.add(
                RuleCode.RECORD_SET_RECORD_PARENT_MISMATCH,
                "Normalized record does not point back to the normalized record set as its parent.",
                field_ref="normalized_record_ids",
            )
    if record_set.normalization_status is NormalizationStatus.COMPLETE:
        if any(status is not NormalizationStatus.COMPLETE for status in child_statuses):
            collector.add(
                RuleCode.RECORD_SET_COMPLETE_INCOHERENT,
                "Normalized record set declares COMPLETE but contains non-complete normalized records.",
                field_ref="normalization_status",
            )
    if record_set.normalization_status is NormalizationStatus.PARTIAL:
        if child_statuses and all(status is NormalizationStatus.COMPLETE for status in child_statuses):
            collector.add(
                RuleCode.RECORD_SET_PARTIAL_INCOHERENT,
                "Normalized record set declares PARTIAL but all referenced normalized records are complete.",
                field_ref="normalization_status",
            )
