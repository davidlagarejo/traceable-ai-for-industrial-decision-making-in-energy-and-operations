from __future__ import annotations

from ..domain.entities import ValidationRuleRecord
from ..domain.records import (
    ContractConformanceCheckRecord,
    FieldCheckResultRecord,
    FitnessCheckRecord,
    ObjectCheckResultRecord,
    TraceabilityCheckRecord,
)
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_object_check_result_record(
    object_check: ObjectCheckResultRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    rule = _quality_rule(
        object_check.validation_rule_record_id,
        collector,
        context,
        missing_code=RuleCode.OBJECT_CHECK_RULE_REFERENCE_INVALID,
        kind_code=RuleCode.OBJECT_CHECK_RULE_KIND_INVALID,
    )
    if (
        object_check.quality_dimension_record_id is not None
        and object_check.quality_dimension_record_id not in context.quality_dimensions_by_id
    ):
        collector.add(
            RuleCode.OBJECT_CHECK_DIMENSION_REFERENCE_INVALID,
            "Object check references an unknown quality dimension.",
        )
    if (
        rule is not None
        and object_check.quality_dimension_record_id is not None
        and rule.quality_dimension_record_id != object_check.quality_dimension_record_id
    ):
        collector.add(
            RuleCode.OBJECT_CHECK_RULE_DIMENSION_MISMATCH,
            "Object check dimension does not match the referenced validation rule.",
        )
    _validate_issue_refs(
        object_check.issue_record_ids,
        collector,
        context,
        RuleCode.OBJECT_CHECK_ISSUE_REFERENCE_INVALID,
    )



def validate_field_check_result_record(
    field_check: FieldCheckResultRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    rule = _quality_rule(
        field_check.validation_rule_record_id,
        collector,
        context,
        missing_code=RuleCode.FIELD_CHECK_RULE_REFERENCE_INVALID,
        kind_code=RuleCode.FIELD_CHECK_RULE_KIND_INVALID,
    )
    if (
        field_check.quality_dimension_record_id is not None
        and field_check.quality_dimension_record_id not in context.quality_dimensions_by_id
    ):
        collector.add(
            RuleCode.FIELD_CHECK_DIMENSION_REFERENCE_INVALID,
            "Field check references an unknown quality dimension.",
        )
    if (
        rule is not None
        and field_check.quality_dimension_record_id is not None
        and rule.quality_dimension_record_id != field_check.quality_dimension_record_id
    ):
        collector.add(
            RuleCode.FIELD_CHECK_RULE_DIMENSION_MISMATCH,
            "Field check dimension does not match the referenced validation rule.",
            field_ref=str(field_check.field_path_ref),
        )
    _validate_issue_refs(
        field_check.issue_record_ids,
        collector,
        context,
        RuleCode.FIELD_CHECK_ISSUE_REFERENCE_INVALID,
        field_ref=str(field_check.field_path_ref),
    )



def validate_traceability_check_record(
    traceability_check: TraceabilityCheckRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    _quality_rule(
        traceability_check.validation_rule_record_id,
        collector,
        context,
        missing_code=RuleCode.TRACEABILITY_CHECK_RULE_REFERENCE_INVALID,
        kind_code=RuleCode.TRACEABILITY_CHECK_RULE_KIND_INVALID,
    )
    _validate_issue_refs(
        traceability_check.issue_record_ids,
        collector,
        context,
        RuleCode.TRACEABILITY_CHECK_ISSUE_REFERENCE_INVALID,
    )



def validate_contract_conformance_check_record(
    contract_check: ContractConformanceCheckRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    _quality_rule(
        contract_check.validation_rule_record_id,
        collector,
        context,
        missing_code=RuleCode.CONTRACT_CHECK_RULE_REFERENCE_INVALID,
        kind_code=RuleCode.CONTRACT_CHECK_RULE_KIND_INVALID,
    )
    _validate_issue_refs(
        contract_check.issue_record_ids,
        collector,
        context,
        RuleCode.CONTRACT_CHECK_ISSUE_REFERENCE_INVALID,
    )



def validate_fitness_check_record(
    fitness_check: FitnessCheckRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    rule = _fitness_rule(
        fitness_check.validation_rule_record_id,
        collector,
        context,
        missing_code=RuleCode.FITNESS_CHECK_RULE_REFERENCE_INVALID,
        kind_code=RuleCode.FITNESS_CHECK_RULE_KIND_INVALID,
    )
    if fitness_check.evaluation_scope_record_id not in context.scopes_by_id:
        collector.add(
            RuleCode.FITNESS_CHECK_SCOPE_REFERENCE_INVALID,
            "Fitness check references an unknown evaluation scope.",
        )
    if (
        fitness_check.fitness_dimension_record_id is not None
        and fitness_check.fitness_dimension_record_id not in context.fitness_dimensions_by_id
    ):
        collector.add(
            RuleCode.FITNESS_CHECK_DIMENSION_REFERENCE_INVALID,
            "Fitness check references an unknown fitness dimension.",
        )
    if (
        rule is not None
        and fitness_check.fitness_dimension_record_id is not None
        and rule.fitness_dimension_record_id != fitness_check.fitness_dimension_record_id
    ):
        collector.add(
            RuleCode.FITNESS_CHECK_RULE_DIMENSION_MISMATCH,
            "Fitness check dimension does not match the referenced validation rule.",
        )
    _validate_issue_refs(
        fitness_check.issue_record_ids,
        collector,
        context,
        RuleCode.FITNESS_CHECK_ISSUE_REFERENCE_INVALID,
    )



def _quality_rule(
    rule_id,
    collector: ViolationCollector,
    context: ValidationContext,
    *,
    missing_code: RuleCode,
    kind_code: RuleCode,
) -> ValidationRuleRecord | None:
    if rule_id is None:
        return None
    rule = context.rules_by_id.get(rule_id)
    if rule is None:
        collector.add(missing_code, "Referenced validation rule does not exist.")
        return None
    if rule.quality_dimension_record_id is None:
        collector.add(kind_code, "Referenced validation rule is not a quality rule.")
    return rule



def _fitness_rule(
    rule_id,
    collector: ViolationCollector,
    context: ValidationContext,
    *,
    missing_code: RuleCode,
    kind_code: RuleCode,
) -> ValidationRuleRecord | None:
    if rule_id is None:
        return None
    rule = context.rules_by_id.get(rule_id)
    if rule is None:
        collector.add(missing_code, "Referenced validation rule does not exist.")
        return None
    if rule.fitness_dimension_record_id is None:
        collector.add(kind_code, "Referenced validation rule is not a fitness rule.")
    return rule



def _validate_issue_refs(
    issue_ids,
    collector: ViolationCollector,
    context: ValidationContext,
    code: RuleCode,
    *,
    field_ref: str | None = None,
) -> None:
    for issue_id in issue_ids:
        if issue_id not in context.issues_by_id:
            collector.add(
                code,
                f"Referenced evaluation issue does not exist: {issue_id}.",
                field_ref=field_ref,
            )
