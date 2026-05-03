from __future__ import annotations

from ..domain.entities import AliasRecord
from ..domain.enums import AliasStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_alias_record(
    alias_record: AliasRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not alias_record.alias_record_id.value:
        collector.add(
            RuleCode.ALIAS_ID_INVALID,
            "alias_record_id must be present.",
            field_ref="alias_record_id",
        )
    if context is None or not context.contains_locator(alias_record.target_ref):
        collector.add(
            RuleCode.ALIAS_TARGET_UNRESOLVED,
            "alias_record must target an existing taxonomy node, canonical term or canonical entity.",
            field_ref="target_ref",
        )
    if context is not None:
        conflicting = [
            item
            for item in context.aliases_for_label_scope(
                normalized_label=alias_record.label.normalized,
                semantic_scope=alias_record.semantic_scope,
            )
            if item.alias_record_id != alias_record.alias_record_id and item.target_ref != alias_record.target_ref
        ]
        if conflicting and alias_record.alias_status is AliasStatus.CONFIRMED:
            collector.add(
                RuleCode.ALIAS_SCOPE_CONFLICT,
                "confirmed alias label conflicts with another target in the same semantic scope.",
                field_ref="label",
            )
    if alias_record.alias_status is not AliasStatus.CONFIRMED:
        collector.add(
            RuleCode.ALIAS_NON_CONFIRMED_DECLARED,
            f"alias is declared as {alias_record.alias_status.value}.",
            field_ref="alias_status",
        )

