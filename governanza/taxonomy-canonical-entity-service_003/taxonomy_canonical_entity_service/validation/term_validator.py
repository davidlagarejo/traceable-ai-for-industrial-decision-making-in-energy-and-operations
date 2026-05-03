from __future__ import annotations

from ..domain.entities import CanonicalTerm, LegacyTermRecord, TaxonomyNode
from ..domain.enums import TermLifecycleStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_canonical_term(
    term: CanonicalTerm,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
    taxonomy_node: TaxonomyNode | None = None,
) -> None:
    if not term.canonical_term_id.value:
        collector.add(
            RuleCode.TERM_ID_INVALID,
            "canonical_term_id must be present.",
            field_ref="canonical_term_id",
        )
    node = taxonomy_node
    if node is None and context is not None:
        node = context.nodes_by_id.get(term.taxonomy_node_id)
    if node is None:
        collector.add(
            RuleCode.TERM_NODE_REFERENCE_INVALID,
            "canonical_term must reference an existing taxonomy_node.",
            field_ref="taxonomy_node_id",
        )
    if context is not None and node is not None:
        duplicates = [
            item
            for item in context.canonical_terms_in_version(node.taxonomy_version_id)
            if item.canonical_term_id != term.canonical_term_id and item.label.normalized == term.label.normalized
        ]
        if duplicates:
            collector.add(
                RuleCode.TERM_DUPLICATE_LABEL_IN_VERSION,
                "canonical_term label must be unique within its taxonomy_version.",
                field_ref="label",
            )
    if term.lifecycle_status is not TermLifecycleStatus.ACTIVE:
        collector.add(
            RuleCode.TERM_NON_ACTIVE_DECLARED,
            f"canonical term is declared as {term.lifecycle_status.value}.",
            field_ref="lifecycle_status",
        )


def validate_legacy_term_record(
    legacy_term: LegacyTermRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not legacy_term.legacy_term_record_id.value:
        collector.add(
            RuleCode.LEGACY_ID_INVALID,
            "legacy_term_record_id must be present.",
            field_ref="legacy_term_record_id",
        )
    canonical_term = None if context is None else context.terms_by_id.get(legacy_term.canonical_term_id)
    if canonical_term is None:
        collector.add(
            RuleCode.LEGACY_TERM_REFERENCE_INVALID,
            "legacy_term_record must reference an existing canonical_term.",
            field_ref="canonical_term_id",
        )
    elif canonical_term.label.normalized == legacy_term.label.normalized:
        collector.add(
            RuleCode.LEGACY_COLLIDES_WITH_CANONICAL,
            "legacy term must not silently duplicate the canonical term label.",
            field_ref="label",
        )
    collector.add(
        RuleCode.LEGACY_DECLARED,
        f"legacy term is declared as {legacy_term.lifecycle_status.value}.",
        field_ref="lifecycle_status",
    )

