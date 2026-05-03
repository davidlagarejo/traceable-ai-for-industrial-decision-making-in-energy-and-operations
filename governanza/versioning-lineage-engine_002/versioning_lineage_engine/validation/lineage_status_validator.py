from __future__ import annotations

from ..domain.enums import LineageIntegrityStatus
from ..domain.records import LineageIntegrityRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_lineage_integrity_record(
    record: LineageIntegrityRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is not None and record.object_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.LINEAGE_OBJECT_VERSION_INVALID,
            "Lineage integrity records must point to a known ObjectVersion.",
            field_ref="object_version_id",
        )

    if not isinstance(record.integrity_status, LineageIntegrityStatus):
        collector.add(
            RuleCode.LINEAGE_STATUS_INVALID,
            "integrity_status must be a supported LineageIntegrityStatus enum value.",
            field_ref="integrity_status",
        )
        return

    if context is not None:
        for edge_id in record.broken_dependency_edge_ids:
            if edge_id not in context.edges_by_id:
                collector.add(
                    RuleCode.LINEAGE_BROKEN_EDGE_UNRESOLVED,
                    "broken_dependency_edge_ids must reference known dependency edges.",
                    field_ref="broken_dependency_edge_ids",
                )

        if record.integrity_status is LineageIntegrityStatus.COMPLETE:
            for snapshot in context.snapshots_for_object_version(record.object_version_id):
                for edge_id in snapshot.dependency_edge_ids:
                    edge = context.edges_by_id.get(edge_id)
                    if edge is None or not edge.required:
                        continue
                    if not context.contains_locator(edge.target_ref):
                        collector.add(
                            RuleCode.LINEAGE_COMPLETE_BUT_MISSING_REQUIRED_REF,
                            "Complete lineage integrity cannot be declared while required upstream refs are unresolved.",
                            field_ref="integrity_status",
                        )

    if record.integrity_status is LineageIntegrityStatus.INCOMPLETE:
        collector.add(
            RuleCode.LINEAGE_INCOMPLETE_DECLARED,
            "The lineage integrity record is structurally valid but declares incomplete lineage.",
            field_ref="integrity_status",
        )
    elif record.integrity_status is LineageIntegrityStatus.BROKEN:
        collector.add(
            RuleCode.LINEAGE_BROKEN_DECLARED,
            "The lineage integrity record is structurally valid but declares broken lineage.",
            field_ref="integrity_status",
        )
