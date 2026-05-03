from __future__ import annotations

from ..domain.entities import DependencySnapshot
from ..domain.value_objects import DependencySnapshotId, Fingerprint, ObjectVersionId
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_dependency_snapshot(
    snapshot: DependencySnapshot,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not isinstance(snapshot.dependency_snapshot_id, DependencySnapshotId):
        collector.add(
            RuleCode.SNAPSHOT_ID_INVALID,
            "dependency_snapshot_id must be a DependencySnapshotId.",
        )
    if not isinstance(snapshot.object_version_id, ObjectVersionId):
        collector.add(
            RuleCode.SNAPSHOT_OBJECT_VERSION_INVALID,
            "object_version_id must be an ObjectVersionId.",
            field_ref="object_version_id",
        )
    elif context is not None and snapshot.object_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.SNAPSHOT_OBJECT_VERSION_INVALID,
            "Dependency snapshots must freeze a known ObjectVersion.",
            field_ref="object_version_id",
        )
    if not isinstance(snapshot.snapshot_fingerprint, Fingerprint):
        collector.add(
            RuleCode.SNAPSHOT_ID_INVALID,
            "snapshot_fingerprint must be a Fingerprint value object.",
            field_ref="snapshot_fingerprint",
        )

    if context is None:
        return

    edges_by_id = context.edges_by_id
    for edge_id in snapshot.dependency_edge_ids:
        edge = edges_by_id.get(edge_id)
        if edge is None:
            collector.add(
                RuleCode.SNAPSHOT_EDGE_MISSING,
                "Dependency snapshots must only reference known dependency edges.",
                field_ref="dependency_edge_ids",
            )
            continue
        if edge.from_object_version_id != snapshot.object_version_id:
            collector.add(
                RuleCode.SNAPSHOT_EDGE_ORIGIN_MISMATCH,
                "Dependency snapshot edge origin must match snapshot.object_version_id.",
                field_ref="dependency_edge_ids",
            )
