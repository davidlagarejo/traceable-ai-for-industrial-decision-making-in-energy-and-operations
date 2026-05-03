from __future__ import annotations

from collections.abc import Iterable

from .._compat import dataclass
from ..domain.entities import (
    DependencyEdge,
    DependencySnapshot,
    ObjectIdentity,
    ObjectVersion,
    ReferenceVersionRecord,
    VersionLineageNode,
)
from ..domain.value_objects import (
    DependencyEdgeId,
    DependencySnapshotId,
    LineageLocator,
    ObjectIdentityId,
    ObjectVersionId,
    ReferenceVersionRecordId,
    VersionLineageNodeId,
)


@dataclass(frozen=True, slots=True)
class ValidationContext:
    object_identities: tuple[ObjectIdentity, ...] = ()
    object_versions: tuple[ObjectVersion, ...] = ()
    dependency_edges: tuple[DependencyEdge, ...] = ()
    dependency_snapshots: tuple[DependencySnapshot, ...] = ()
    reference_versions: tuple[ReferenceVersionRecord, ...] = ()
    version_lineage_nodes: tuple[VersionLineageNode, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        object_identities: Iterable[ObjectIdentity] = (),
        object_versions: Iterable[ObjectVersion] = (),
        dependency_edges: Iterable[DependencyEdge] = (),
        dependency_snapshots: Iterable[DependencySnapshot] = (),
        reference_versions: Iterable[ReferenceVersionRecord] = (),
        version_lineage_nodes: Iterable[VersionLineageNode] = (),
    ) -> "ValidationContext":
        return cls(
            object_identities=tuple(object_identities),
            object_versions=tuple(object_versions),
            dependency_edges=tuple(dependency_edges),
            dependency_snapshots=tuple(dependency_snapshots),
            reference_versions=tuple(reference_versions),
            version_lineage_nodes=tuple(version_lineage_nodes),
        )

    @property
    def identities_by_id(self) -> dict[ObjectIdentityId, ObjectIdentity]:
        return {item.object_identity_id: item for item in self.object_identities}

    @property
    def versions_by_id(self) -> dict[ObjectVersionId, ObjectVersion]:
        return {item.object_version_id: item for item in self.object_versions}

    @property
    def edges_by_id(self) -> dict[DependencyEdgeId, DependencyEdge]:
        return {item.dependency_edge_id: item for item in self.dependency_edges}

    @property
    def snapshots_by_id(self) -> dict[DependencySnapshotId, DependencySnapshot]:
        return {item.dependency_snapshot_id: item for item in self.dependency_snapshots}

    @property
    def references_by_id(self) -> dict[ReferenceVersionRecordId, ReferenceVersionRecord]:
        return {item.reference_version_record_id: item for item in self.reference_versions}

    @property
    def nodes_by_id(self) -> dict[VersionLineageNodeId, VersionLineageNode]:
        return {item.version_lineage_node_id: item for item in self.version_lineage_nodes}

    def contains_locator(self, locator: LineageLocator) -> bool:
        if locator.target_kind.value == "object_identity":
            return locator.identifier in self.identities_by_id
        if locator.target_kind.value == "object_version":
            return locator.identifier in self.versions_by_id
        return locator.identifier in self.references_by_id

    def snapshots_for_object_version(self, object_version_id: ObjectVersionId) -> tuple[DependencySnapshot, ...]:
        return tuple(
            item for item in self.dependency_snapshots if item.object_version_id == object_version_id
        )
