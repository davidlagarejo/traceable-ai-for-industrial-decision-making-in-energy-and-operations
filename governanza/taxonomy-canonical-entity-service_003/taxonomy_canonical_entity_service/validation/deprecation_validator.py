from __future__ import annotations

from ..domain.records import DeprecationRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_deprecation_record(
    deprecation_record: DeprecationRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not deprecation_record.deprecation_record_id.value:
        collector.add(
            RuleCode.DEPRECATION_ID_INVALID,
            "deprecation_record_id must be present.",
            field_ref="deprecation_record_id",
        )
    if context is None or not context.contains_locator(deprecation_record.deprecated_ref):
        collector.add(
            RuleCode.DEPRECATION_TARGET_UNRESOLVED,
            "deprecation_record must point to an existing deprecated target.",
            field_ref="deprecated_ref",
        )
    if deprecation_record.replacement_ref is not None:
        if context is None or not context.contains_locator(deprecation_record.replacement_ref):
            collector.add(
                RuleCode.DEPRECATION_REPLACEMENT_UNRESOLVED,
                "deprecation_record.replacement_ref must resolve when present.",
                field_ref="replacement_ref",
            )
        elif deprecation_record.replacement_ref.target_kind != deprecation_record.deprecated_ref.target_kind:
            collector.add(
                RuleCode.DEPRECATION_REPLACEMENT_KIND_MISMATCH,
                "deprecation replacement must refer to the same semantic level as the deprecated target.",
                field_ref="replacement_ref",
            )

