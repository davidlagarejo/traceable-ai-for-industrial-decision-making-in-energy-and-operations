from __future__ import annotations

from ..domain.records import BoundaryRecord
from ..domain.enums import BoundaryStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_boundary_record(
    boundary_record: BoundaryRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not boundary_record.boundary_record_id.value:
        collector.add(
            RuleCode.BOUNDARY_ID_INVALID,
            "boundary_record_id must be present.",
            field_ref="boundary_record_id",
        )
    if context is None or boundary_record.taxonomy_node_id not in context.nodes_by_id:
        collector.add(
            RuleCode.BOUNDARY_NODE_REFERENCE_INVALID,
            "boundary_record must reference an existing taxonomy_node.",
            field_ref="taxonomy_node_id",
        )
    if boundary_record.nearest_valid_ref is not None and (context is None or not context.contains_locator(boundary_record.nearest_valid_ref)):
        collector.add(
            RuleCode.BOUNDARY_NEAREST_REF_UNRESOLVED,
            "boundary_record.nearest_valid_ref must resolve when present.",
            field_ref="nearest_valid_ref",
        )
    if boundary_record.boundary_status is not BoundaryStatus.DEFINED:
        collector.add(
            RuleCode.BOUNDARY_NON_FINAL_DECLARED,
            f"boundary is declared as {boundary_record.boundary_status.value}.",
            field_ref="boundary_status",
        )

