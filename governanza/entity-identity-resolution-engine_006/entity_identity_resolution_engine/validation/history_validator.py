from __future__ import annotations

from ..domain.enums import HistoryStatus
from ..domain.records import EntityHistoryRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_entity_history_record(
    entity_history_record: EntityHistoryRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if entity_history_record.entity_id not in context.entities_by_id:
        collector.add(
            RuleCode.HISTORY_ENTITY_REFERENCE_INVALID,
            "EntityHistoryRecord entity_id is not resolvable in the validation context.",
            field_ref="entity_id",
        )
    if (
        entity_history_record.resolution_decision_record_id is not None
        and entity_history_record.resolution_decision_record_id not in context.decisions_by_id
    ):
        collector.add(
            RuleCode.HISTORY_DECISION_REFERENCE_INVALID,
            "EntityHistoryRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    merge_event = None
    if entity_history_record.merge_event_record_id is not None:
        merge_event = context.merge_events_by_id.get(entity_history_record.merge_event_record_id)
        if merge_event is None:
            collector.add(
                RuleCode.HISTORY_MERGE_REFERENCE_INVALID,
                "EntityHistoryRecord merge_event_record_id is not resolvable in the validation context.",
                field_ref="merge_event_record_id",
            )
    split_event = None
    if entity_history_record.split_event_record_id is not None:
        split_event = context.split_events_by_id.get(entity_history_record.split_event_record_id)
        if split_event is None:
            collector.add(
                RuleCode.HISTORY_SPLIT_REFERENCE_INVALID,
                "EntityHistoryRecord split_event_record_id is not resolvable in the validation context.",
                field_ref="split_event_record_id",
            )
    if entity_history_record.history_status is HistoryStatus.MERGED and merge_event is None:
        collector.add(
            RuleCode.HISTORY_STATUS_EVENT_MISMATCH,
            "EntityHistoryRecord with MERGED status must reference a MergeEventRecord.",
            field_ref="history_status",
        )
    if entity_history_record.history_status is HistoryStatus.SPLIT and split_event is None:
        collector.add(
            RuleCode.HISTORY_STATUS_EVENT_MISMATCH,
            "EntityHistoryRecord with SPLIT status must reference a SplitEventRecord.",
            field_ref="history_status",
        )
    if merge_event is not None and entity_history_record.entity_id not in merge_event.merged_entity_ids:
        collector.add(
            RuleCode.HISTORY_EVENT_ENTITY_MISMATCH,
            "EntityHistoryRecord merge event does not actually involve the referenced entity.",
            field_ref="merge_event_record_id",
        )
    if split_event is not None and entity_history_record.entity_id not in {
        split_event.source_entity_id,
        *split_event.successor_entity_ids,
    }:
        collector.add(
            RuleCode.HISTORY_EVENT_ENTITY_MISMATCH,
            "EntityHistoryRecord split event does not actually involve the referenced entity.",
            field_ref="split_event_record_id",
        )
