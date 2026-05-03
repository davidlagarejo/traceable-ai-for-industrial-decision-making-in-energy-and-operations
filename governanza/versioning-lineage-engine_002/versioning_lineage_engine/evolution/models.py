from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from ..domain.records import ImpactSetRecord, StaleStateRecord, VersionDiffRecord
from ..domain.value_objects import LineageLocator, ObjectVersionId


class DiffClassification(str, Enum):
    NON_MATERIAL = "non_material"
    MATERIAL = "material"
    BREAKING_FOR_DOWNSTREAM = "breaking_for_downstream"
    REBUILD_RECOMMENDED = "rebuild_recommended"
    REBUILD_REQUIRED = "rebuild_required"


@dataclass(frozen=True, slots=True)
class ChangeTrigger:
    trigger_ref: LineageLocator
    replacement_ref: LineageLocator | None
    classification: DiffClassification
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VersionDiffAnalysis:
    version_diff_record: VersionDiffRecord | None
    classification: DiffClassification
    reasons: tuple[str, ...]
    trigger: ChangeTrigger

    @property
    def has_changes(self) -> bool:
        return self.version_diff_record is not None

    @property
    def source_object_version_id(self) -> ObjectVersionId:
        if self.version_diff_record is not None:
            return self.version_diff_record.source_object_version_id
        return self.trigger.trigger_ref.identifier  # type: ignore[return-value]

    @property
    def target_object_version_id(self) -> ObjectVersionId | None:
        if self.version_diff_record is not None:
            return self.version_diff_record.target_object_version_id
        if self.trigger.replacement_ref is None:
            return None
        return self.trigger.replacement_ref.identifier  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ImpactAnalysisResult:
    impact_set_record: ImpactSetRecord | None
    stale_state_records: tuple[StaleStateRecord, ...]

    @property
    def affected_object_version_ids(self) -> tuple[ObjectVersionId, ...]:
        if self.impact_set_record is None:
            return ()
        return self.impact_set_record.affected_object_version_ids
