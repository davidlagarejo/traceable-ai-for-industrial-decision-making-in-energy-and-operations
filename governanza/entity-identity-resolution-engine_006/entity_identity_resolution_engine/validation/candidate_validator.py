from __future__ import annotations

from ..domain.entities import CandidateMatchRecord, CandidateMatchSet
from ..domain.enums import CandidateMatchStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_candidate_match_record(
    candidate_match_record: CandidateMatchRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    match_set = context.candidate_sets_by_id.get(candidate_match_record.candidate_match_set_id)
    if match_set is None:
        collector.add(
            RuleCode.CANDIDATE_MATCH_SET_REFERENCE_INVALID,
            "CandidateMatchRecord candidate_match_set_id is not resolvable in the validation context.",
            field_ref="candidate_match_set_id",
        )
    if candidate_match_record.source_observed_record_id not in context.observed_records_by_id:
        collector.add(
            RuleCode.CANDIDATE_MATCH_SOURCE_REFERENCE_INVALID,
            "CandidateMatchRecord source_observed_record_id is not resolvable in the validation context.",
            field_ref="source_observed_record_id",
        )
    for candidate_observed_record_id in candidate_match_record.candidate_observed_record_ids:
        if candidate_observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.CANDIDATE_MATCH_CANDIDATE_REFERENCE_INVALID,
                "CandidateMatchRecord candidate_observed_record_ids contains an unresolved observed record.",
                field_ref="candidate_observed_record_ids",
            )
    if (
        candidate_match_record.candidate_entity_id is not None
        and candidate_match_record.candidate_entity_id not in context.entities_by_id
    ):
        collector.add(
            RuleCode.CANDIDATE_MATCH_ENTITY_REFERENCE_INVALID,
            "CandidateMatchRecord candidate_entity_id is not resolvable in the validation context.",
            field_ref="candidate_entity_id",
        )
    for evidence_record_id in candidate_match_record.evidence_record_ids:
        if evidence_record_id not in context.evidences_by_id:
            collector.add(
                RuleCode.CANDIDATE_MATCH_EVIDENCE_REFERENCE_INVALID,
                "CandidateMatchRecord references evidence that is not present in the validation context.",
                field_ref="evidence_record_ids",
            )
    if (
        candidate_match_record.confidence_record_id is not None
        and candidate_match_record.confidence_record_id not in context.confidences_by_id
    ):
        collector.add(
            RuleCode.CANDIDATE_MATCH_CONFIDENCE_REFERENCE_INVALID,
            "CandidateMatchRecord confidence_record_id is not resolvable in the validation context.",
            field_ref="confidence_record_id",
        )
    if (
        match_set is not None
        and candidate_match_record.source_observed_record_id not in match_set.anchor_observed_record_ids
    ):
        collector.add(
            RuleCode.CANDIDATE_MATCH_SOURCE_NOT_ANCHORED,
            "CandidateMatchRecord source_observed_record_id is not part of the anchor observed records of its CandidateMatchSet.",
            field_ref="source_observed_record_id",
        )
    if candidate_match_record.candidate_match_status is CandidateMatchStatus.OPEN:
        collector.add(
            RuleCode.CANDIDATE_MATCH_OPEN_DECLARED,
            "CandidateMatchRecord remains open and must not be treated as a confirmed identity resolution.",
            field_ref="candidate_match_status",
        )


def validate_candidate_match_set(
    candidate_match_set: CandidateMatchSet,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    for anchor_observed_record_id in candidate_match_set.anchor_observed_record_ids:
        if anchor_observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.CANDIDATE_SET_ANCHOR_REFERENCE_INVALID,
                "CandidateMatchSet references an anchor observed record that is not present in the validation context.",
                field_ref="anchor_observed_record_ids",
            )
    source_ids: set = set()
    for candidate_match_record_id in candidate_match_set.candidate_match_record_ids:
        candidate_match_record = context.candidate_matches_by_id.get(candidate_match_record_id)
        if candidate_match_record is None:
            collector.add(
                RuleCode.CANDIDATE_SET_MATCH_REFERENCE_INVALID,
                "CandidateMatchSet references a candidate match record that is not present in the validation context.",
                field_ref="candidate_match_record_ids",
            )
            continue
        if candidate_match_record.candidate_match_set_id != candidate_match_set.candidate_match_set_id:
            collector.add(
                RuleCode.CANDIDATE_SET_MATCH_SET_MISMATCH,
                "CandidateMatchRecord points to a different CandidateMatchSet than the one that references it.",
                field_ref="candidate_match_record_ids",
            )
        source_ids.add(candidate_match_record.source_observed_record_id)
    if source_ids and not source_ids.issubset(set(candidate_match_set.anchor_observed_record_ids)):
        collector.add(
            RuleCode.CANDIDATE_SET_ANCHOR_COVERAGE_INVALID,
            "CandidateMatchSet anchor observed records do not cover the source observed records of their candidate matches.",
            field_ref="anchor_observed_record_ids",
        )
