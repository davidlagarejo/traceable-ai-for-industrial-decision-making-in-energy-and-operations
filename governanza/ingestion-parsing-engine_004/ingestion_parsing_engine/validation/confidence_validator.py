from __future__ import annotations

from ..domain.records import ParsingConfidenceRecord
from ..domain.enums import ConfidenceStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_parsing_confidence_record(
    confidence: ParsingConfidenceRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is not None and not context.contains_scope_ref(confidence.scope_ref):
        collector.add(
            RuleCode.CONFIDENCE_SCOPE_UNRESOLVED,
            "ParsingConfidenceRecord.scope_ref does not resolve to a known object.",
            field_ref="scope_ref",
        )
    if confidence.confidence_status is ConfidenceStatus.HEURISTIC:
        collector.add(
            RuleCode.CONFIDENCE_HEURISTIC_DECLARED,
            "Parsing confidence is heuristic and should remain visible downstream.",
            field_ref="confidence_status",
        )
