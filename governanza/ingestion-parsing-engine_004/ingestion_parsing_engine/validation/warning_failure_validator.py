from __future__ import annotations

from ..domain.records import ParsingFailureRecord, ParsingWarningRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_parsing_warning_record(
    warning: ParsingWarningRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is not None and not context.contains_scope_ref(warning.scope_ref):
        collector.add(
            RuleCode.WARNING_SCOPE_UNRESOLVED,
            "ParsingWarningRecord.scope_ref does not resolve to a known object.",
            field_ref="scope_ref",
        )
    collector.add(
        RuleCode.WARNING_DECLARED,
        f"Parsing warning declared: {warning.warning_code.value}.",
        field_ref="warning_code",
    )


def validate_parsing_failure_record(
    failure: ParsingFailureRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is not None and not context.contains_scope_ref(failure.scope_ref):
        collector.add(
            RuleCode.FAILURE_SCOPE_UNRESOLVED,
            "ParsingFailureRecord.scope_ref does not resolve to a known object.",
            field_ref="scope_ref",
        )
    collector.add(
        RuleCode.FAILURE_DECLARED,
        f"Parsing failure declared: {failure.failure_code.value}.",
        field_ref="failure_code",
    )
