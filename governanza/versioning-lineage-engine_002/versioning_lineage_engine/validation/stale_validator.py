from __future__ import annotations

from ..domain.enums import StaleState
from ..domain.records import StaleStateRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_stale_state_record(
    record: StaleStateRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is not None and record.object_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.STALE_OBJECT_VERSION_INVALID,
            "Stale state records must point to a known ObjectVersion.",
            field_ref="object_version_id",
        )

    if not isinstance(record.stale_state, StaleState):
        collector.add(
            RuleCode.STALE_STATUS_INVALID,
            "stale_state must be a supported StaleState enum value.",
            field_ref="stale_state",
        )
        return

    if context is not None:
        for locator in record.upstream_trigger_refs:
            if not context.contains_locator(locator):
                collector.add(
                    RuleCode.STALE_TRIGGER_UNRESOLVED,
                    "Stale state upstream_trigger_refs must resolve to known lineage objects or references.",
                    field_ref="upstream_trigger_refs",
                )

    if record.stale_state is not StaleState.FRESH:
        collector.add(
            RuleCode.STALE_DECLARED,
            "The stale state record is structurally valid but declares the object version stale.",
            field_ref="stale_state",
        )
