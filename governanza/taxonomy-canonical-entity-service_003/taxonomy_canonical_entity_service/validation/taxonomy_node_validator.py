from __future__ import annotations

from ..domain.entities import CanonicalTerm, TaxonomyNode
from ..domain.enums import NodeStatus, TaxonomyNodeType
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_taxonomy_node(
    node: TaxonomyNode,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
    canonical_term: CanonicalTerm | None = None,
) -> None:
    if not node.taxonomy_node_id.value:
        collector.add(
            RuleCode.NODE_ID_INVALID,
            "taxonomy_node_id must be present.",
            field_ref="taxonomy_node_id",
        )
    if context is None or node.taxonomy_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.NODE_VERSION_REFERENCE_INVALID,
            "taxonomy_node must reference an existing taxonomy_version.",
            field_ref="taxonomy_version_id",
        )
    term = canonical_term
    if term is None and context is not None:
        term = context.terms_by_id.get(node.canonical_term_id)
    if term is None:
        collector.add(
            RuleCode.NODE_TERM_REFERENCE_INVALID,
            "taxonomy_node must reference an existing canonical_term.",
            field_ref="canonical_term_id",
        )
    elif term.taxonomy_node_id != node.taxonomy_node_id:
        collector.add(
            RuleCode.NODE_TERM_REFERENCE_INVALID,
            "canonical_term must point back to the same taxonomy_node.",
            field_ref="canonical_term_id",
        )
    if node.node_type is TaxonomyNodeType.ROOT and node.parent_taxonomy_node_id is not None:
        collector.add(
            RuleCode.NODE_PARENT_INVALID,
            "root taxonomy nodes must not declare a parent.",
            field_ref="parent_taxonomy_node_id",
        )
    if node.parent_taxonomy_node_id is not None:
        if context is None or node.parent_taxonomy_node_id not in context.nodes_by_id:
            collector.add(
                RuleCode.NODE_PARENT_INVALID,
                "taxonomy_node parent must reference an existing taxonomy_node.",
                field_ref="parent_taxonomy_node_id",
            )
        else:
            parent = context.nodes_by_id[node.parent_taxonomy_node_id]
            if parent.taxonomy_version_id != node.taxonomy_version_id:
                collector.add(
                    RuleCode.NODE_PARENT_VERSION_MISMATCH,
                    "taxonomy_node parent must belong to the same taxonomy_version.",
                    field_ref="parent_taxonomy_node_id",
                )
    if node.node_status is not NodeStatus.ACTIVE:
        collector.add(
            RuleCode.NODE_PROVISIONAL_DECLARED,
            f"taxonomy node is declared as {node.node_status.value}.",
            field_ref="node_status",
        )

