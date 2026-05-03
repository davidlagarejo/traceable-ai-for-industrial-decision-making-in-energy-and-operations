from __future__ import annotations

from ..domain.entities import ObservedNameRecord, ObservedRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_observed_record(
    observed_record: ObservedRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    primary_name = context.observed_names_by_id.get(observed_record.primary_observed_name_record_id)
    if primary_name is None:
        collector.add(
            RuleCode.OBSERVED_PRIMARY_NAME_REFERENCE_INVALID,
            "ObservedRecord primary_observed_name_record_id is not resolvable in the validation context.",
            field_ref="primary_observed_name_record_id",
        )
    else:
        if primary_name.observed_record_id != observed_record.observed_record_id:
            collector.add(
                RuleCode.OBSERVED_NAME_PARENT_MISMATCH,
                "ObservedRecord primary observed name points to a different observed record.",
                field_ref="primary_observed_name_record_id",
            )
        if not primary_name.is_primary:
            collector.add(
                RuleCode.OBSERVED_NAME_PRIMARY_FLAG_INCOHERENT,
                "ObservedRecord primary observed name is not marked as primary.",
                field_ref="primary_observed_name_record_id",
            )

    for name_id in observed_record.observed_name_record_ids:
        observed_name = context.observed_names_by_id.get(name_id)
        if observed_name is None:
            collector.add(
                RuleCode.OBSERVED_NAME_REFERENCE_INVALID,
                "ObservedRecord references an observed name that is not present in the validation context.",
                field_ref="observed_name_record_ids",
            )
            continue
        if observed_name.observed_record_id != observed_record.observed_record_id:
            collector.add(
                RuleCode.OBSERVED_NAME_PARENT_MISMATCH,
                "ObservedNameRecord parent does not match the ObservedRecord that references it.",
                field_ref="observed_name_record_ids",
            )


def validate_observed_name_record(
    observed_name_record: ObservedNameRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    observed_record = context.observed_records_by_id.get(observed_name_record.observed_record_id)
    if observed_record is None:
        collector.add(
            RuleCode.OBSERVED_NAME_OBSERVED_RECORD_REFERENCE_INVALID,
            "ObservedNameRecord observed_record_id is not resolvable in the validation context.",
            field_ref="observed_record_id",
        )
        return
    if observed_name_record.observed_name_record_id not in observed_record.observed_name_record_ids:
        collector.add(
            RuleCode.OBSERVED_NAME_PARENT_MISMATCH,
            "ObservedNameRecord is not referenced by its parent ObservedRecord.",
            field_ref="observed_record_id",
        )
    if observed_name_record.is_primary and (
        observed_record.primary_observed_name_record_id != observed_name_record.observed_name_record_id
    ):
        collector.add(
            RuleCode.OBSERVED_NAME_PRIMARY_FLAG_INCOHERENT,
            "ObservedNameRecord is marked primary but is not the primary name of its parent ObservedRecord.",
            field_ref="is_primary",
        )
    if (not observed_name_record.is_primary) and (
        observed_record.primary_observed_name_record_id == observed_name_record.observed_name_record_id
    ):
        collector.add(
            RuleCode.OBSERVED_NAME_PRIMARY_FLAG_INCOHERENT,
            "ObservedNameRecord is the primary name of its parent ObservedRecord but is not marked primary.",
            field_ref="is_primary",
        )
