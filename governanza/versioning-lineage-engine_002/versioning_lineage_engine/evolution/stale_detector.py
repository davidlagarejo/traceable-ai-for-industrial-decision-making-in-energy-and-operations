from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib

from ..domain.entities import DependencyEdge
from ..domain.records import StaleStateRecord
from ..domain.value_objects import StaleStateRecordId
from .change_classifier import stale_state_for_classification
from .models import ChangeTrigger


class BasicStaleDetector:
    def __init__(self, *, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def detect_from_trigger(
        self,
        *,
        downstream_edge: DependencyEdge,
        trigger: ChangeTrigger,
    ) -> StaleStateRecord | None:
        if not downstream_edge.required:
            return None

        stale_state = stale_state_for_classification(trigger.classification)
        if stale_state is None:
            return None

        reasons = _unique_ordered(
            [
                f"{downstream_edge.input_role.value} depends on {trigger.trigger_ref.identifier} "
                f"and upstream change is classified as {trigger.classification.value}.",
                *trigger.reasons,
            ]
        )
        record_id = StaleStateRecordId(
            _stable_digest(
                "stale_state",
                str(downstream_edge.from_object_version_id),
                str(trigger.trigger_ref.identifier),
                trigger.classification.value,
                *reasons,
            )
        )
        return StaleStateRecord(
            stale_state_record_id=record_id,
            object_version_id=downstream_edge.from_object_version_id,
            stale_state=stale_state,
            reasons=tuple(reasons),
            upstream_trigger_refs=(trigger.trigger_ref,),
            detected_at=self._clock(),
            cleared_at=None,
        )


def _stable_digest(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _unique_ordered(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
