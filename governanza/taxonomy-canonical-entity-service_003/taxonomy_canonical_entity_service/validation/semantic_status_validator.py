from __future__ import annotations

from ..domain.records import SemanticIntegrityRecord
from ..domain.enums import SemanticIntegrityStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_semantic_integrity_record(
    integrity_record: SemanticIntegrityRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not integrity_record.semantic_integrity_record_id.value:
        collector.add(
            RuleCode.INTEGRITY_ID_INVALID,
            "semantic_integrity_record_id must be present.",
            field_ref="semantic_integrity_record_id",
        )
    if context is None or integrity_record.taxonomy_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.INTEGRITY_VERSION_UNRESOLVED,
            "semantic_integrity_record must reference an existing taxonomy_version.",
            field_ref="taxonomy_version_id",
        )
    if context is not None:
        for alias_id in integrity_record.ambiguous_alias_ids:
            if alias_id not in context.aliases_by_id:
                collector.add(
                    RuleCode.INTEGRITY_ALIAS_UNRESOLVED,
                    "semantic_integrity_record references an unknown alias id.",
                    field_ref="ambiguous_alias_ids",
                )
                break
        for match_id in integrity_record.unresolved_candidate_match_ids:
            if match_id not in context.candidate_matches_by_id:
                collector.add(
                    RuleCode.INTEGRITY_MATCH_UNRESOLVED,
                    "semantic_integrity_record references an unknown candidate match id.",
                    field_ref="unresolved_candidate_match_ids",
                )
                break
        for ref in integrity_record.conflicting_refs:
            if not context.contains_locator(ref):
                collector.add(
                    RuleCode.INTEGRITY_CONFLICT_REF_UNRESOLVED,
                    "semantic_integrity_record references an unknown conflicting ref.",
                    field_ref="conflicting_refs",
                )
                break
        pending_matches = context.unresolved_candidate_matches_for_taxonomy_version(
            integrity_record.taxonomy_version_id
        )
        if integrity_record.integrity_status is SemanticIntegrityStatus.OK and pending_matches:
            collector.add(
                RuleCode.INTEGRITY_OK_BUT_PENDING_ISSUES,
                "semantic_integrity_record cannot be OK while unresolved candidate matches still exist for the same taxonomy_version.",
                field_ref="integrity_status",
            )
    if integrity_record.integrity_status is not SemanticIntegrityStatus.OK:
        collector.add(
            RuleCode.INTEGRITY_ISSUES_DECLARED,
            f"semantic integrity is declared as {integrity_record.integrity_status.value}.",
            field_ref="integrity_status",
        )

