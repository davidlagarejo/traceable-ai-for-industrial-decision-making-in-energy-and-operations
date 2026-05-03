from __future__ import annotations

from ..domain.records import TaxonomyChangeRecord
from ..domain.enums import ComparabilityStatus, TaxonomyChangeKind
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_taxonomy_change_record(
    change_record: TaxonomyChangeRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not change_record.taxonomy_change_record_id.value:
        collector.add(
            RuleCode.CHANGE_ID_INVALID,
            "taxonomy_change_record_id must be present.",
            field_ref="taxonomy_change_record_id",
        )
    if change_record.source_taxonomy_version_id is not None and (
        context is None or change_record.source_taxonomy_version_id not in context.versions_by_id
    ):
        collector.add(
            RuleCode.CHANGE_SOURCE_VERSION_UNRESOLVED,
            "taxonomy_change_record.source_taxonomy_version_id must resolve when present.",
            field_ref="source_taxonomy_version_id",
        )
    if context is None or change_record.target_taxonomy_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.CHANGE_TARGET_VERSION_UNRESOLVED,
            "taxonomy_change_record.target_taxonomy_version_id must resolve.",
            field_ref="target_taxonomy_version_id",
        )
    if context is not None:
        for ref in change_record.affected_refs:
            if not context.contains_locator(ref):
                collector.add(
                    RuleCode.CHANGE_AFFECTED_REF_UNRESOLVED,
                    "taxonomy_change_record contains an affected_ref that does not resolve.",
                    field_ref="affected_refs",
                )
                break
    if change_record.change_kind in {
        TaxonomyChangeKind.SPLIT,
        TaxonomyChangeKind.MERGE,
        TaxonomyChangeKind.BOUNDARY_REDEFINITION,
    } and change_record.comparability_status is ComparabilityStatus.COMPARABLE:
        collector.add(
            RuleCode.CHANGE_COMPARABILITY_INCOHERENT,
            "split, merge and boundary redefinition changes must not declare full comparability.",
            field_ref="comparability_status",
        )

