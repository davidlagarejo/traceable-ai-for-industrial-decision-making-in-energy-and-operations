from __future__ import annotations

from ..domain.entities import DependencyEdge
from ..domain.enums import DependencyTargetKind, DependencyType
from ..domain.value_objects import DependencyEdgeId, DependencyRole, LineageLocator, ObjectVersionId
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


_REFERENCE_DEPENDENCY_TYPES = {
    DependencyType.USES_CONTRACT,
    DependencyType.USES_TAXONOMY,
    DependencyType.USES_RULE_PACK,
    DependencyType.USES_LIBRARY,
    DependencyType.USES_MODEL,
}


def validate_dependency_edge(
    edge: DependencyEdge,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not isinstance(edge.dependency_edge_id, DependencyEdgeId):
        collector.add(RuleCode.EDGE_ID_INVALID, "dependency_edge_id must be a DependencyEdgeId.")
    if not isinstance(edge.from_object_version_id, ObjectVersionId):
        collector.add(
            RuleCode.EDGE_ORIGIN_INVALID,
            "from_object_version_id must be an ObjectVersionId.",
            field_ref="from_object_version_id",
        )
    elif context is not None and edge.from_object_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.EDGE_ORIGIN_INVALID,
            "Dependency edges must originate from a known ObjectVersion.",
            field_ref="from_object_version_id",
        )

    if not isinstance(edge.target_kind, DependencyTargetKind):
        collector.add(
            RuleCode.EDGE_TARGET_INVALID,
            "target_kind must be a supported DependencyTargetKind enum value.",
            field_ref="target_kind",
        )
    if not isinstance(edge.target_ref, LineageLocator):
        collector.add(
            RuleCode.EDGE_TARGET_INVALID,
            "target_ref must be a LineageLocator.",
            field_ref="target_ref",
        )
        return
    if not isinstance(edge.dependency_type, DependencyType):
        collector.add(
            RuleCode.EDGE_SEMANTIC_MISMATCH,
            "dependency_type must be a supported DependencyType enum value.",
            field_ref="dependency_type",
        )
        return
    if not isinstance(edge.input_role, DependencyRole):
        collector.add(
            RuleCode.EDGE_SEMANTIC_MISMATCH,
            "input_role must be a DependencyRole value object.",
            field_ref="input_role",
        )

    if edge.target_ref.target_kind != edge.target_kind:
        collector.add(
            RuleCode.EDGE_TARGET_INVALID,
            "target_ref.target_kind must match target_kind.",
            field_ref="target_ref",
        )

    if (
        edge.target_kind is DependencyTargetKind.OBJECT_VERSION
        and edge.target_ref.identifier == edge.from_object_version_id
    ):
        collector.add(
            RuleCode.EDGE_SELF_REFERENCE_FORBIDDEN,
            "Dependency edges must not point to their own origin object version.",
            field_ref="target_ref",
        )

    if context is not None and not context.contains_locator(edge.target_ref):
        collector.add(
            RuleCode.EDGE_TARGET_UNRESOLVED,
            "Dependency edge target_ref must resolve to a known lineage object or reference.",
            field_ref="target_ref",
        )

    if edge.dependency_type is DependencyType.REPLACES:
        expected_kind = DependencyTargetKind.OBJECT_IDENTITY
    elif edge.dependency_type in _REFERENCE_DEPENDENCY_TYPES:
        expected_kind = DependencyTargetKind.REFERENCE_VERSION
    else:
        expected_kind = DependencyTargetKind.OBJECT_VERSION

    if edge.target_kind is not expected_kind:
        collector.add(
            RuleCode.EDGE_SEMANTIC_MISMATCH,
            f"{edge.dependency_type.value} dependencies must target {expected_kind.value}.",
            field_ref="target_kind",
        )
