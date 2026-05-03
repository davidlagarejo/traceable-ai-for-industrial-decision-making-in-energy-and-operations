from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib

from ..domain.records import NormalizationWarningRecord
from ..domain.value_objects import (
    NormalizationRunRecordId,
    NormalizationScopeRef,
    NormalizationWarningRecordId,
    WarningCode,
)
from .results import WarningDraft


class NormalizationWarningBuilder:
    def __init__(self, *, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def build(
        self,
        *,
        normalization_run_record_id: NormalizationRunRecordId,
        scope_ref: NormalizationScopeRef,
        warning_draft: WarningDraft,
    ) -> NormalizationWarningRecord:
        warning_id = NormalizationWarningRecordId(
            _stable_id(
                "normalization_warning",
                normalization_run_record_id.value,
                scope_ref.scope_kind.value,
                scope_ref.identifier,
                warning_draft.code,
                warning_draft.message,
            )
        )
        return NormalizationWarningRecord(
            normalization_warning_record_id=warning_id,
            normalization_run_record_id=normalization_run_record_id,
            scope_ref=scope_ref,
            warning_code=WarningCode(warning_draft.code),
            warning_severity=warning_draft.severity,
            message=warning_draft.message,
            created_at=self._clock(),
        )


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"
