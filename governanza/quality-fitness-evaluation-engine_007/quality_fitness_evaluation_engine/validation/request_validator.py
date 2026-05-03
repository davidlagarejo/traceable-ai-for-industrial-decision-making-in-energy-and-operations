from __future__ import annotations

from ..domain.entities import EvaluationRequestRecord, EvaluationScopeRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_evaluation_scope_record(
    evaluation_scope: EvaluationScopeRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    del evaluation_scope, collector, context


def validate_evaluation_request_record(
    evaluation_request: EvaluationRequestRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if evaluation_request.evaluation_scope_record_id not in context.scopes_by_id:
        collector.add(
            RuleCode.REQUEST_SCOPE_REFERENCE_INVALID,
            "Evaluation request references an unknown evaluation scope.",
        )
