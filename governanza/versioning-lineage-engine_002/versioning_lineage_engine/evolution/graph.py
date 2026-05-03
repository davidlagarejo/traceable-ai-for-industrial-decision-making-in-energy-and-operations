from __future__ import annotations

from collections.abc import Iterable

from .._compat import dataclass
from ..domain.entities import DependencyEdge, DependencySnapshot, ObjectVersion, ReferenceVersionRecord
from ..domain.value_objects import (
    DependencyEdgeId,
    DependencySnapshotId,
    LineageLocator,
    ObjectVersionId,
    ReferenceVersionRecordId,
)


@dataclass(frozen=True, slots=True)
class LineageGraphIndex:
    object_versions: tuple[ObjectVersion, ...] = ()
    dependency_edges: tuple[DependencyEdge, ...] = ()
    dependency_snapshots: tuple[DependencySnapshot, ...] = ()
    reference_versions: tuple[ReferenceVersionRecord, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        object_versions: Iterable[ObjectVersion] = (),
        dependency_edges: Iterable[DependencyEdge] = (),
        dependency_snapshots: Iterable[DependencySnapshot] = (),
        reference_versions: Iterable[ReferenceVersionRecord] = (),
    ) -> "LineageGraphIndex":
        return cls(
            object_versions=tuple(object_versions),
            dependency_edges=tuple(dependency_edges),
            dependency_snapshots=tuple(dependency_snapshots),
            reference_versions=tuple(reference_versions),
        )

    @property
    def object_versions_by_id(self) -> dict[ObjectVersionId, ObjectVersion]:
        return {item.object_version_id: item for item in self.object_versions}

    @property
    def dependency_edges_by_id(self) -> dict[DependencyEdgeId, DependencyEdge]:
        return {item.dependency_edge_id: item for item in self.dependency_edges}

    @property
    def dependency_snapshots_by_id(self) -> dict[DependencySnapshotId, DependencySnapshot]:
        return {item.dependency_snapshot_id: item for item in self.dependency_snapshots}

    @property
    def reference_versions_by_id(self) -> dict[ReferenceVersionRecordId, ReferenceVersionRecord]:
        return {item.reference_version_record_id: item for item in self.reference_versions}

    def downstream_edges_for_trigger(self, trigger_ref: LineageLocator) -> tuple[DependencyEdge, ...]:
        return tuple(item for item in self.dependency_edges if item.target_ref == trigger_ref)

    def dependency_snapshot_for_version(
        self,
        object_version_id: ObjectVersionId,
    ) -> DependencySnapshot | None:
        for item in self.dependency_snapshots:
            if item.object_version_id == object_version_id:
                return item
        return None
