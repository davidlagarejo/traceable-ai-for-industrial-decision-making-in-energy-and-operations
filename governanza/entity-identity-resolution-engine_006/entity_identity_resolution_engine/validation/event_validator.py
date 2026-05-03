from __future__ import annotations

from ..domain.enums import ResolutionStatus
from ..domain.records import MergeEventRecord, SplitEventRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_merge_event_record(
    merge_event_record: MergeEventRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    for entity_id in merge_event_record.merged_entity_ids:
        if entity_id not in context.entities_by_id:
            collector.add(
                RuleCode.MERGE_EVENT_ENTITY_REFERENCE_INVALID,
                "MergeEventRecord merged_entity_ids contains an unresolved entity reference.",
                field_ref="merged_entity_ids",
            )
    if merge_event_record.resolution_decision_record_id is None:
        return
    decision = context.decisions_by_id.get(merge_event_record.resolution_decision_record_id)
    if decision is None:
        collector.add(
            RuleCode.MERGE_EVENT_DECISION_REFERENCE_INVALID,
            "MergeEventRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    elif decision.resolution_status is not ResolutionStatus.MERGED:
        collector.add(
            RuleCode.MERGE_EVENT_DECISION_STATUS_MISMATCH,
            "MergeEventRecord must point to a ResolutionDecisionRecord with MERGED status.",
            field_ref="resolution_decision_record_id",
        )


def validate_split_event_record(
    split_event_record: SplitEventRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if split_event_record.source_entity_id not in context.entities_by_id:
        collector.add(
            RuleCode.SPLIT_EVENT_ENTITY_REFERENCE_INVALID,
            "SplitEventRecord source_entity_id is not resolvable in the validation context.",
            field_ref="source_entity_id",
        )
    for entity_id in split_event_record.successor_entity_ids:
        if entity_id not in context.entities_by_id:
            collector.add(
                RuleCode.SPLIT_EVENT_ENTITY_REFERENCE_INVALID,
                "SplitEventRecord successor_entity_ids contains an unresolved entity reference.",
                field_ref="successor_entity_ids",
            )
    if split_event_record.resolution_decision_record_id is None:
        return
    decision = context.decisions_by_id.get(split_event_record.resolution_decision_record_id)
    if decision is None:
        collector.add(
            RuleCode.SPLIT_EVENT_DECISION_REFERENCE_INVALID,
            "SplitEventRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    elif decision.resolution_status is not ResolutionStatus.SPLIT:
        collector.add(
            RuleCode.SPLIT_EVENT_DECISION_STATUS_MISMATCH,
            "SplitEventRecord must point to a ResolutionDecisionRecord with SPLIT status.",
            field_ref="resolution_decision_record_id",
        )
