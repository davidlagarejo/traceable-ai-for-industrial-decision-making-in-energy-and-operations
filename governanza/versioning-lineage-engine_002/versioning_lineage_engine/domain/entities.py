from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    ComparabilityStatus,
    DependencyTargetKind,
    DependencyType,
    IdentityStatus,
    ObjectKind,
    PhaseId,
    RebuildabilityStatus,
    ReferenceKind,
    VersionLifecycleStatus,
)
from .errors import DomainInvariantError
from .value_objects import (
    ContentChecksum,
    DependencyEdgeId,
    DependencyRole,
    DependencySnapshotId,
    EngineName,
    EngineVersion,
    Fingerprint,
    LineageLocator,
    ObjectIdentityId,
    ObjectVersionId,
    ReferenceVersionRecordId,
    RebuildManifest,
    StableKey,
    VersionIndex,
    VersionLineageNodeId,
    _ensure_unique,
    _require_text,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class ObjectIdentity:
    object_identity_id: ObjectIdentityId
    object_kind: ObjectKind
    phase_scope: PhaseId | None
    stable_key: StableKey
    canonical_name: str
    identity_status: IdentityStatus
    replacement_of_identity_id: ObjectIdentityId | None
    replaced_by_identity_id: ObjectIdentityId | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.replacement_of_identity_id == self.object_identity_id:
            raise DomainInvariantError("replacement_of_identity_id must not point to self.")
        if self.replaced_by_identity_id == self.object_identity_id:
            raise DomainInvariantError("replaced_by_identity_id must not point to self.")
        if self.identity_status is IdentityStatus.REPLACEMENT and self.replacement_of_identity_id is None:
            raise DomainInvariantError(
                "Replacement identities must declare replacement_of_identity_id."
            )
        if self.identity_status is IdentityStatus.REPLACED and self.replaced_by_identity_id is None:
            raise DomainInvariantError("Replaced identities must declare replaced_by_identity_id.")

    @property
    def is_deprecated_object(self) -> bool:
        return self.identity_status is IdentityStatus.DEPRECATED

    @property
    def is_replacement_object(self) -> bool:
        return self.identity_status is IdentityStatus.REPLACEMENT

    @property
    def is_replaced_object(self) -> bool:
        return self.identity_status is IdentityStatus.REPLACED

    @property
    def reference(self) -> LineageLocator:
        return LineageLocator.for_object_identity(self.object_identity_id)


@dataclass(frozen=True, slots=True)
class ObjectVersion:
    object_version_id: ObjectVersionId
    object_identity_id: ObjectIdentityId
    version_index: VersionIndex
    content_checksum: ContentChecksum
    schema_fingerprint: Fingerprint
    version_status: VersionLifecycleStatus
    created_at: datetime
    producer_engine_name: EngineName
    producer_engine_version: EngineVersion
    rebuild_manifest: RebuildManifest

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.rebuild_manifest.target_object_version_id != self.object_version_id:
            raise DomainInvariantError(
                "RebuildManifest.target_object_version_id must match ObjectVersion.object_version_id."
            )
        if self.rebuild_manifest.expected_content_checksum != self.content_checksum:
            raise DomainInvariantError(
                "RebuildManifest.expected_content_checksum must match ObjectVersion.content_checksum."
            )

    @property
    def reference(self) -> LineageLocator:
        return LineageLocator.for_object_version(self.object_version_id)


@dataclass(frozen=True, slots=True)
class ReferenceVersionRecord:
    reference_version_record_id: ReferenceVersionRecordId
    reference_kind: ReferenceKind
    reference_key: StableKey
    reference_name: str
    version_label: str
    content_fingerprint: Fingerprint
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_name", _require_text(self.reference_name, "reference_name"))
        object.__setattr__(self, "version_label", _require_text(self.version_label, "version_label"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

    @property
    def reference(self) -> LineageLocator:
        return LineageLocator.for_reference_version(self.reference_version_record_id)


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    dependency_edge_id: DependencyEdgeId
    from_object_version_id: ObjectVersionId
    target_kind: DependencyTargetKind
    target_ref: LineageLocator
    dependency_type: DependencyType
    required: bool
    contributes_to_rebuild: bool
    input_role: DependencyRole
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.target_ref.target_kind != self.target_kind:
            raise DomainInvariantError("target_ref.target_kind must match target_kind.")

        if self.dependency_type is DependencyType.REPLACES:
            if self.target_kind is not DependencyTargetKind.OBJECT_IDENTITY:
                raise DomainInvariantError("REPLACES dependencies must target object_identity.")
        elif self.dependency_type in {
            DependencyType.USES_CONTRACT,
            DependencyType.USES_TAXONOMY,
            DependencyType.USES_RULE_PACK,
            DependencyType.USES_LIBRARY,
            DependencyType.USES_MODEL,
        }:
            if self.target_kind is not DependencyTargetKind.REFERENCE_VERSION:
                raise DomainInvariantError("Policy or external dependencies must target reference_version.")
        else:
            if self.target_kind is not DependencyTargetKind.OBJECT_VERSION:
                raise DomainInvariantError("Object dependencies must target object_version.")


@dataclass(frozen=True, slots=True)
class DependencySnapshot:
    dependency_snapshot_id: DependencySnapshotId
    object_version_id: ObjectVersionId
    dependency_edge_ids: tuple[DependencyEdgeId, ...]
    snapshot_fingerprint: Fingerprint
    captured_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "captured_at", _require_timezone(self.captured_at, "captured_at"))
        _ensure_unique(self.dependency_edge_ids, "dependency_edge_ids")


@dataclass(frozen=True, slots=True)
class VersionLineageNode:
    version_lineage_node_id: VersionLineageNodeId
    object_version_id: ObjectVersionId
    dependency_snapshot_id: DependencySnapshotId
    upstream_object_version_ids: tuple[ObjectVersionId, ...]
    reference_version_ids: tuple[ReferenceVersionRecordId, ...]
    comparability_status: ComparabilityStatus
    rebuildability_status: RebuildabilityStatus
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.upstream_object_version_ids, "upstream_object_version_ids")
        _ensure_unique(self.reference_version_ids, "reference_version_ids")

    @property
    def is_derived_object(self) -> bool:
        return bool(self.upstream_object_version_ids or self.reference_version_ids)


__all__ = [
    "DependencyEdge",
    "DependencySnapshot",
    "ObjectIdentity",
    "ObjectVersion",
    "ReferenceVersionRecord",
    "VersionLineageNode",
]
