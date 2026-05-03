from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib

from ..domain.records import ImpactSetRecord
from ..domain.value_objects import ImpactSetRecordId, LineageLocator
from .change_classifier import (
    impact_severity_for_classification,
    migration_required_for_classification,
    requires_rebuild_for_classification,
)
from .graph import LineageGraphIndex
from .models import ChangeTrigger, DiffClassification, ImpactAnalysisResult, VersionDiffAnalysis
from .stale_detector import BasicStaleDetector


class BasicImpactAnalyzer:
    def __init__(
        self,
        *,
        stale_detector: BasicStaleDetector | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._stale_detector = stale_detector or BasicStaleDetector(clock=clock)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def analyze_diff(
        self,
        diff_analysis: VersionDiffAnalysis,
        *,
        graph_index: LineageGraphIndex,
    ) -> ImpactAnalysisResult:
        return self.analyze_trigger(diff_analysis.trigger, graph_index=graph_index)

    def analyze_trigger(
        self,
        trigger: ChangeTrigger,
        *,
        graph_index: LineageGraphIndex,
    ) -> ImpactAnalysisResult:
        if trigger.classification is DiffClassification.NON_MATERIAL:
            return ImpactAnalysisResult(impact_set_record=None, stale_state_records=())

        downstream_edges = graph_index.downstream_edges_for_trigger(trigger.trigger_ref)
        stale_records = tuple(
            item
            for item in (
                self._stale_detector.detect_from_trigger(
                    downstream_edge=edge,
                    trigger=trigger,
                )
                for edge in downstream_edges
            )
            if item is not None
        )
        if not stale_records:
            return ImpactAnalysisResult(impact_set_record=None, stale_state_records=())

        impact_severity = impact_severity_for_classification(trigger.classification)
        assert impact_severity is not None
        affected_object_version_ids = tuple(
            _unique_ordered_ids(item.object_version_id for item in stale_records)
        )
        reasons = tuple(_unique_ordered_text(
            [
                *trigger.reasons,
                f"Direct downstream impact from {trigger.trigger_ref.identifier}.",
            ]
        ))
        impact_record = ImpactSetRecord(
            impact_set_record_id=ImpactSetRecordId(
                _stable_digest(
                    "impact_set",
                    trigger.classification.value,
                    str(trigger.trigger_ref.identifier),
                    *(str(item) for item in affected_object_version_ids),
                    *reasons,
                )
            ),
            trigger_ref=trigger.trigger_ref,
            affected_object_version_ids=affected_object_version_ids,
            impact_severity=impact_severity,
            requires_rebuild=requires_rebuild_for_classification(trigger.classification),
            migration_required=migration_required_for_classification(trigger.classification),
            reasons=reasons,
            detected_at=self._clock(),
        )
        return ImpactAnalysisResult(
            impact_set_record=impact_record,
            stale_state_records=stale_records,
        )

    def analyze_reference_change(
        self,
        *,
        source_ref: LineageLocator,
        replacement_ref: LineageLocator,
        classification: DiffClassification,
        reasons: tuple[str, ...],
        graph_index: LineageGraphIndex,
    ) -> ImpactAnalysisResult:
        trigger = ChangeTrigger(
            trigger_ref=source_ref,
            replacement_ref=replacement_ref,
            classification=classification,
            reasons=reasons,
        )
        return self.analyze_trigger(trigger, graph_index=graph_index)


def _stable_digest(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _unique_ordered_ids(values):
    ordered = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _unique_ordered_text(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
