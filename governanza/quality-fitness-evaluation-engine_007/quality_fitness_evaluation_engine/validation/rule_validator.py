from __future__ import annotations

from ..domain.entities import ValidationRuleRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_validation_rule_record(
    validation_rule: ValidationRuleRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if (
        validation_rule.quality_dimension_record_id is not None
        and validation_rule.quality_dimension_record_id not in context.quality_dimensions_by_id
    ):
        collector.add(
            RuleCode.RULE_QUALITY_DIMENSION_REFERENCE_INVALID,
            "Validation rule references an unknown quality dimension.",
        )
    if (
        validation_rule.fitness_dimension_record_id is not None
        and validation_rule.fitness_dimension_record_id not in context.fitness_dimensions_by_id
    ):
        collector.add(
            RuleCode.RULE_FITNESS_DIMENSION_REFERENCE_INVALID,
            "Validation rule references an unknown fitness dimension.",
        )
