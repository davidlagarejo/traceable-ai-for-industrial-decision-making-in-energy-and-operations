from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    ChangeSeverity,
    ComparabilityStatus,
    ImpactSeverity,
    LineageIntegrityStatus,
    RebuildabilityStatus,
    RetentionStatus,
    StaleState,
    VersionLifecycleStatus,
)
from .errors import DomainInvariantError
from .value_objects import (
    ChangeDescriptor,
    DependencyEdgeId,
    ImpactSetRecordId,
    LineageIntegrityRecordId,
    LineageLocator,
    ObjectIdentityId,
    ObjectVersionId,
    RetentionMarkerId,
    StaleStateRecordId,
    VersionDiffRecordId,
    VersionStatusRecordId,
    _ensure_unique,
    _require_text,
    _require_timezone,
)
from .entities import ObjectVersion


@dataclass(frozen=True, slots=True)
class VersionDiffRecord:
    version_diff_record_id: VersionDiffRecordId
    object_identity_id: ObjectIdentityId
    source_object_version_id: ObjectVersionId
    target_object_version_id: ObjectVersionId
    change_set: tuple[ChangeDescriptor, ...]
    change_severity: ChangeSeverity
    breaking_detected: bool
    generated_at: datetime

    def __post_init__(self) -> None:
        if not self.change_set:
            raise DomainInvariantError("VersionDiffRecord.change_set must not be empty.")
        object.__setattr__(self, "generated_at", _require_timezone(self.generated_at, "generated_at"))
        if self.source_object_version_id == self.target_object_version_id:
            raise DomainInvariantError("VersionDiffRecord must compare two distinct object versions.")
        inferred_breaking = any(change.severity is ChangeSeverity.BREAKING for change in self.change_set)
        if inferred_breaking and not self.breaking_detected:
            raise DomainInvariantError(
                "breaking_detected must be true when change_set contains breaking changes."
            )

    @classmethod
    def for_versions(
        cls,
        *,
        version_diff_record_id: VersionDiffRecordId,
        source_version: ObjectVersion,
        target_version: ObjectVersion,
        change_set: tuple[ChangeDescriptor, ...],
        change_severity: ChangeSeverity,
        breaking_detected: bool,
        generated_at: datetime,
    ) -> "VersionDiffRecord":
        if source_version.object_identity_id != target_version.object_identity_id:
            raise DomainInvariantError(
                "VersionDiffRecord cannot compare versions from different object identities."
            )
        return cls(
            version_diff_record_id=version_diff_record_id,
            object_identity_id=source_version.object_identity_id,
            source_object_version_id=source_version.object_version_id,
            target_object_version_id=target_version.object_version_id,
            change_set=change_set,
            change_severity=change_severity,
            breaking_detected=breaking_detected,
            generated_at=generated_at,
        )


@dataclass(frozen=True, slots=True)
class StaleStateRecord:
    stale_state_record_id: StaleStateRecordId
    object_version_id: ObjectVersionId
    stale_state: StaleState
    reasons: tuple[str, ...]
    upstream_trigger_refs: tuple[LineageLocator, ...]
    detected_at: datetime
    cleared_at: datetime | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "detected_at", _require_timezone(self.detected_at, "detected_at"))
        if self.cleared_at is not None:
            object.__setattr__(self, "cleared_at", _require_timezone(self.cleared_at, "cleared_at"))
        object.__setattr__(self, "reasons", tuple(_require_text(item, "reason") for item in self.reasons))
        _ensure_unique(self.reasons, "reasons")
        _ensure_unique(self.upstream_trigger_refs, "upstream_trigger_refs")
        if self.stale_state is StaleState.FRESH:
            if self.reasons or self.upstream_trigger_refs:
                raise DomainInvariantError("Fresh stale state records must not carry stale reasons or triggers.")
        else:
            if not self.reasons:
                raise DomainInvariantError("Stale state records must include reasons.")
            if not self.upstream_trigger_refs:
                raise DomainInvariantError("Stale state records must include upstream_trigger_refs.")

    @property
    def is_stale(self) -> bool:
        return self.stale_state is not StaleState.FRESH


@dataclass(frozen=True, slots=True)
class ImpactSetRecord:
    impact_set_record_id: ImpactSetRecordId
    trigger_ref: LineageLocator
    affected_object_version_ids: tuple[ObjectVersionId, ...]
    impact_severity: ImpactSeverity
    requires_rebuild: bool
    migration_required: bool
    reasons: tuple[str, ...]
    detected_at: datetime

    def __post_init__(self) -> None:
        if not self.affected_object_version_ids:
            raise DomainInvariantError("ImpactSetRecord must affect at least one object version.")
        object.__setattr__(self, "detected_at", _require_timezone(self.detected_at, "detected_at"))
        object.__setattr__(self, "reasons", tuple(_require_text(item, "reason") for item in self.reasons))
        _ensure_unique(self.affected_object_version_ids, "affected_object_version_ids")
        _ensure_unique(self.reasons, "reasons")
        if not self.reasons:
            raise DomainInvariantError("ImpactSetRecord must include at least one reason.")


@dataclass(frozen=True, slots=True)
class VersionStatusRecord:
    version_status_record_id: VersionStatusRecordId
    object_version_id: ObjectVersionId
    version_status: VersionLifecycleStatus
    comparability_status: ComparabilityStatus
    rebuildability_status: RebuildabilityStatus
    status_reason: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "status_reason", _require_text(self.status_reason, "status_reason"))
        object.__setattr__(self, "recorded_at", _require_timezone(self.recorded_at, "recorded_at"))


@dataclass(frozen=True, slots=True)
class RetentionMarker:
    retention_marker_id: RetentionMarkerId
    object_version_id: ObjectVersionId
    retention_status: RetentionStatus
    reason: str
    marked_at: datetime
    retain_until: datetime | None
    legal_hold: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason", _require_text(self.reason, "reason"))
        object.__setattr__(self, "marked_at", _require_timezone(self.marked_at, "marked_at"))
        if self.retain_until is not None:
            object.__setattr__(self, "retain_until", _require_timezone(self.retain_until, "retain_until"))


@dataclass(frozen=True, slots=True)
class LineageIntegrityRecord:
    lineage_integrity_record_id: LineageIntegrityRecordId
    object_version_id: ObjectVersionId
    integrity_status: LineageIntegrityStatus
    missing_required_refs: tuple[LineageLocator, ...]
    broken_dependency_edge_ids: tuple[DependencyEdgeId, ...]
    details: tuple[str, ...]
    checked_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "checked_at", _require_timezone(self.checked_at, "checked_at"))
        object.__setattr__(self, "details", tuple(_require_text(item, "detail") for item in self.details))
        _ensure_unique(self.missing_required_refs, "missing_required_refs")
        _ensure_unique(self.broken_dependency_edge_ids, "broken_dependency_edge_ids")
        _ensure_unique(self.details, "details")
        if self.integrity_status is LineageIntegrityStatus.COMPLETE:
            if self.missing_required_refs or self.broken_dependency_edge_ids:
                raise DomainInvariantError(
                    "Complete lineage records must not declare missing refs or broken dependency edges."
                )
        else:
            if not (self.missing_required_refs or self.broken_dependency_edge_ids or self.details):
                raise DomainInvariantError(
                    "Incomplete or broken lineage records must explain what is wrong."
                )


__all__ = [
    "ImpactSetRecord",
    "LineageIntegrityRecord",
    "RetentionMarker",
    "StaleStateRecord",
    "VersionDiffRecord",
    "VersionStatusRecord",
]
