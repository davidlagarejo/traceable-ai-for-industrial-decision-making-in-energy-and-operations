from __future__ import annotations

from ..domain.records import JoinKeySemanticRecord
from ..domain.enums import JoinSafetyLevel
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_join_key_semantic_record(
    join_key_record: JoinKeySemanticRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not join_key_record.join_key_semantic_record_id.value:
        collector.add(
            RuleCode.JOIN_ID_INVALID,
            "join_key_semantic_record_id must be present.",
            field_ref="join_key_semantic_record_id",
        )
    if context is None or not context.contains_locator(join_key_record.target_ref):
        collector.add(
            RuleCode.JOIN_TARGET_UNRESOLVED,
            "join_key_semantic_record must reference an existing semantic target.",
            field_ref="target_ref",
        )
    if join_key_record.join_safety_level is not JoinSafetyLevel.SAFE:
        collector.add(
            RuleCode.JOIN_NOT_SAFE_DECLARED,
            f"join key is declared as {join_key_record.join_safety_level.value}.",
            field_ref="join_safety_level",
        )

