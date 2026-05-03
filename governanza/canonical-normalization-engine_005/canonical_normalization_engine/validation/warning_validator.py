from __future__ import annotations

from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode
from ..domain.records import (
    NonNormalizableFieldRecord,
    NormalizationWarningRecord,
    PartialNormalizationRecord,
)


def validate_normalization_warning_record(
    warning: NormalizationWarningRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        collector.add(
            RuleCode.WARNING_DECLARED,
            "Normalization warning record is declared.",
            field_ref="warning_code",
        )
        return
    if warning.normalization_run_record_id not in context.runs_by_id:
        collector.add(
            RuleCode.WARNING_RUN_REFERENCE_INVALID,
            "Normalization warning record references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    if not context.contains_scope_ref(warning.scope_ref):
        collector.add(
            RuleCode.WARNING_SCOPE_UNRESOLVED,
            "Normalization warning record scope does not resolve to an object present in validation context.",
            field_ref="scope_ref",
        )
    else:
        scope_run_id = context.run_id_for_scope(warning.scope_ref)
        if (
            scope_run_id is not None
            and scope_run_id != warning.normalization_run_record_id
        ):
            collector.add(
                RuleCode.WARNING_SCOPE_RUN_MISMATCH,
                "Normalization warning record scope belongs to a different normalization run.",
                field_ref="scope_ref",
            )
    collector.add(
        RuleCode.WARNING_DECLARED,
        "Normalization warning record is declared.",
        field_ref="warning_code",
    )


def validate_non_normalizable_field_record(
    non_normalizable_field: NonNormalizableFieldRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        collector.add(
            RuleCode.NON_NORMALIZABLE_DECLARED,
            "Non-normalizable field is explicitly declared.",
            field_ref="reason",
        )
        return
    run = context.runs_by_id.get(non_normalizable_field.normalization_run_record_id)
    if run is None:
        collector.add(
            RuleCode.NON_NORMALIZABLE_RUN_REFERENCE_INVALID,
            "Non-normalizable field references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    candidate_field = None
    if non_normalizable_field.candidate_canonical_field_definition_id is not None:
        candidate_field = context.fields_by_id.get(
            non_normalizable_field.candidate_canonical_field_definition_id
        )
        if candidate_field is None:
            collector.add(
                RuleCode.NON_NORMALIZABLE_CANDIDATE_FIELD_REFERENCE_INVALID,
                "Non-normalizable field candidate canonical field definition is not present in validation context.",
                field_ref="candidate_canonical_field_definition_id",
            )
        elif run is not None and candidate_field.canonical_schema_version_id != run.canonical_schema_version_id:
            collector.add(
                RuleCode.NON_NORMALIZABLE_CANDIDATE_FIELD_SCHEMA_MISMATCH,
                "Non-normalizable field candidate canonical field definition belongs to a different schema version than the normalization run.",
                field_ref="candidate_canonical_field_definition_id",
            )
    if non_normalizable_field.field_mapping_rule_id is not None:
        mapping_rule = context.mapping_rules_by_id.get(non_normalizable_field.field_mapping_rule_id)
        if mapping_rule is None:
            collector.add(
                RuleCode.NON_NORMALIZABLE_MAPPING_REFERENCE_INVALID,
                "Non-normalizable field references a field mapping rule that is not present in validation context.",
                field_ref="field_mapping_rule_id",
            )
        else:
            if (
                candidate_field is not None
                and mapping_rule.canonical_field_definition_id
                != non_normalizable_field.candidate_canonical_field_definition_id
            ):
                collector.add(
                    RuleCode.NON_NORMALIZABLE_MAPPING_FIELD_MISMATCH,
                    "Non-normalizable field mapping rule targets a different canonical field definition than the candidate field.",
                    field_ref="field_mapping_rule_id",
                )
            if run is not None and mapping_rule.canonical_schema_version_id != run.canonical_schema_version_id:
                collector.add(
                    RuleCode.NON_NORMALIZABLE_MAPPING_SCHEMA_MISMATCH,
                    "Non-normalizable field mapping rule belongs to a different schema version than the normalization run.",
                    field_ref="field_mapping_rule_id",
                )
    collector.add(
        RuleCode.NON_NORMALIZABLE_DECLARED,
        "Non-normalizable field is explicitly declared.",
        field_ref="reason",
    )


def validate_partial_normalization_record(
    partial_record: PartialNormalizationRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        collector.add(
            RuleCode.PARTIAL_DECLARED,
            "Partial normalization record is explicitly declared.",
            field_ref="partial_normalization_status",
        )
        return
    if partial_record.normalization_run_record_id not in context.runs_by_id:
        collector.add(
            RuleCode.PARTIAL_RUN_REFERENCE_INVALID,
            "Partial normalization record references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    for field_id in partial_record.normalized_field_record_ids:
        normalized_field = context.normalized_fields_by_id.get(field_id)
        if normalized_field is None:
            collector.add(
                RuleCode.PARTIAL_NORMALIZED_FIELD_REFERENCE_INVALID,
                "Partial normalization record references a normalized field that is not present in validation context.",
                field_ref="normalized_field_record_ids",
            )
            continue
        if normalized_field.normalization_run_record_id != partial_record.normalization_run_record_id:
            collector.add(
                RuleCode.PARTIAL_FIELD_RUN_MISMATCH,
                "Partial normalization record references a normalized field from a different normalization run.",
                field_ref="normalized_field_record_ids",
            )
    for record_id in partial_record.non_normalizable_field_record_ids:
        non_normalizable_field = context.non_normalizable_by_id.get(record_id)
        if non_normalizable_field is None:
            collector.add(
                RuleCode.PARTIAL_NON_NORMALIZABLE_REFERENCE_INVALID,
                "Partial normalization record references a non-normalizable field that is not present in validation context.",
                field_ref="non_normalizable_field_record_ids",
            )
            continue
        if non_normalizable_field.normalization_run_record_id != partial_record.normalization_run_record_id:
            collector.add(
                RuleCode.PARTIAL_FIELD_RUN_MISMATCH,
                "Partial normalization record references a non-normalizable field from a different normalization run.",
                field_ref="non_normalizable_field_record_ids",
            )
    collector.add(
        RuleCode.PARTIAL_DECLARED,
        "Partial normalization record is explicitly declared.",
        field_ref="partial_normalization_status",
    )
