from __future__ import annotations

from ..domain.enums import AmbiguityStatus, CandidateMatchStatus, ResolutionStatus
from ..domain.records import (
    AmbiguousResolutionRecord,
    ConfirmedMatchRecord,
    NoMatchRecord,
    RelatedButNotEquivalentRecord,
    ResolutionDecisionRecord,
)
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_resolution_decision_record(
    resolution_decision_record: ResolutionDecisionRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    candidate_set = None
    if resolution_decision_record.candidate_match_set_id is not None:
        candidate_set = context.candidate_sets_by_id.get(resolution_decision_record.candidate_match_set_id)
        if candidate_set is None:
            collector.add(
                RuleCode.DECISION_CANDIDATE_SET_REFERENCE_INVALID,
                "ResolutionDecisionRecord candidate_match_set_id is not resolvable in the validation context.",
                field_ref="candidate_match_set_id",
            )
    for observed_record_id in resolution_decision_record.decision_scope_observed_record_ids:
        if observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.DECISION_SCOPE_REFERENCE_INVALID,
                "ResolutionDecisionRecord scope contains an observed record that is not resolvable in the validation context.",
                field_ref="decision_scope_observed_record_ids",
            )
    for evidence_record_id in resolution_decision_record.evidence_record_ids:
        if evidence_record_id not in context.evidences_by_id:
            collector.add(
                RuleCode.DECISION_EVIDENCE_REFERENCE_INVALID,
                "ResolutionDecisionRecord evidence_record_ids contains an unresolved evidence record.",
                field_ref="evidence_record_ids",
            )
    if (
        resolution_decision_record.confidence_record_id is not None
        and resolution_decision_record.confidence_record_id not in context.confidences_by_id
    ):
        collector.add(
            RuleCode.DECISION_CONFIDENCE_REFERENCE_INVALID,
            "ResolutionDecisionRecord confidence_record_id is not resolvable in the validation context.",
            field_ref="confidence_record_id",
        )
    if candidate_set is not None:
        _validate_decision_status_against_set(resolution_decision_record, candidate_set, collector)


def validate_confirmed_match_record(
    confirmed_match_record: ConfirmedMatchRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    decision = context.decisions_by_id.get(confirmed_match_record.resolution_decision_record_id)
    if decision is None:
        collector.add(
            RuleCode.CONFIRMED_MATCH_DECISION_REFERENCE_INVALID,
            "ConfirmedMatchRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    elif decision.resolution_status is not ResolutionStatus.CONFIRMED:
        collector.add(
            RuleCode.CONFIRMED_MATCH_DECISION_STATUS_MISMATCH,
            "ConfirmedMatchRecord must point to a ResolutionDecisionRecord with CONFIRMED status.",
            field_ref="resolution_decision_record_id",
        )
    if confirmed_match_record.entity_id not in context.entities_by_id:
        collector.add(
            RuleCode.CONFIRMED_MATCH_ENTITY_REFERENCE_INVALID,
            "ConfirmedMatchRecord entity_id is not resolvable in the validation context.",
            field_ref="entity_id",
        )
    for observed_record_id in confirmed_match_record.observed_record_ids:
        if observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.CONFIRMED_MATCH_OBSERVED_REFERENCE_INVALID,
                "ConfirmedMatchRecord observed_record_ids contains an unresolved observed record.",
                field_ref="observed_record_ids",
            )
    if (
        decision is not None
        and decision.decision_scope_observed_record_ids
        and not set(confirmed_match_record.observed_record_ids).issubset(
            set(decision.decision_scope_observed_record_ids)
        )
    ):
        collector.add(
            RuleCode.CONFIRMED_MATCH_SCOPE_MISMATCH,
            "ConfirmedMatchRecord observed records must remain within the explicit scope of the confirming decision.",
            field_ref="observed_record_ids",
        )


def validate_no_match_record(
    no_match_record: NoMatchRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    decision = context.decisions_by_id.get(no_match_record.resolution_decision_record_id)
    if decision is None:
        collector.add(
            RuleCode.NO_MATCH_DECISION_REFERENCE_INVALID,
            "NoMatchRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    elif decision.resolution_status is not ResolutionStatus.NO_MATCH:
        collector.add(
            RuleCode.NO_MATCH_DECISION_STATUS_MISMATCH,
            "NoMatchRecord must point to a ResolutionDecisionRecord with NO_MATCH status.",
            field_ref="resolution_decision_record_id",
        )
    if no_match_record.subject_observed_record_id not in context.observed_records_by_id:
        collector.add(
            RuleCode.NO_MATCH_SUBJECT_REFERENCE_INVALID,
            "NoMatchRecord subject_observed_record_id is not resolvable in the validation context.",
            field_ref="subject_observed_record_id",
        )
    for rejected_observed_record_id in no_match_record.rejected_observed_record_ids:
        if rejected_observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.NO_MATCH_REJECTED_REFERENCE_INVALID,
                "NoMatchRecord rejected_observed_record_ids contains an unresolved observed record.",
                field_ref="rejected_observed_record_ids",
            )
    if (
        no_match_record.rejected_entity_id is not None
        and no_match_record.rejected_entity_id not in context.entities_by_id
    ):
        collector.add(
            RuleCode.NO_MATCH_ENTITY_REFERENCE_INVALID,
            "NoMatchRecord rejected_entity_id is not resolvable in the validation context.",
            field_ref="rejected_entity_id",
        )
    collector.add(
        RuleCode.NO_MATCH_DECLARED,
        "NoMatchRecord declares an explicit identity rejection and should be handled as a governed non-merge outcome.",
        field_ref="resolution_decision_record_id",
    )


def validate_ambiguous_resolution_record(
    ambiguous_resolution_record: AmbiguousResolutionRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    decision = context.decisions_by_id.get(ambiguous_resolution_record.resolution_decision_record_id)
    if decision is None:
        collector.add(
            RuleCode.AMBIGUOUS_DECISION_REFERENCE_INVALID,
            "AmbiguousResolutionRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    elif decision.resolution_status is not ResolutionStatus.AMBIGUOUS:
        collector.add(
            RuleCode.AMBIGUOUS_DECISION_STATUS_MISMATCH,
            "AmbiguousResolutionRecord must point to a ResolutionDecisionRecord with AMBIGUOUS status.",
            field_ref="resolution_decision_record_id",
        )
    if ambiguous_resolution_record.candidate_match_set_id is not None and (
        ambiguous_resolution_record.candidate_match_set_id not in context.candidate_sets_by_id
    ):
        collector.add(
            RuleCode.AMBIGUOUS_CANDIDATE_SET_REFERENCE_INVALID,
            "AmbiguousResolutionRecord candidate_match_set_id is not resolvable in the validation context.",
            field_ref="candidate_match_set_id",
        )
    for observed_record_id in ambiguous_resolution_record.observed_record_ids:
        if observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.AMBIGUOUS_OBSERVED_REFERENCE_INVALID,
                "AmbiguousResolutionRecord observed_record_ids contains an unresolved observed record.",
                field_ref="observed_record_ids",
            )
    for entity_id in ambiguous_resolution_record.plausible_entity_ids:
        if entity_id not in context.entities_by_id:
            collector.add(
                RuleCode.AMBIGUOUS_ENTITY_REFERENCE_INVALID,
                "AmbiguousResolutionRecord plausible_entity_ids contains an unresolved entity reference.",
                field_ref="plausible_entity_ids",
            )
    if ambiguous_resolution_record.ambiguity_status is AmbiguityStatus.RESOLVED:
        collector.add(
            RuleCode.AMBIGUOUS_STATUS_INCOHERENT,
            "AmbiguousResolutionRecord must not declare RESOLVED while still being represented as ambiguous.",
            field_ref="ambiguity_status",
        )
    collector.add(
        RuleCode.AMBIGUOUS_DECLARED,
        "AmbiguousResolutionRecord declares unresolved identity ambiguity that must not be collapsed into a final entity join.",
        field_ref="ambiguity_status",
    )


def validate_related_but_not_equivalent_record(
    related_record: RelatedButNotEquivalentRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    decision = context.decisions_by_id.get(related_record.resolution_decision_record_id)
    if decision is None:
        collector.add(
            RuleCode.RELATED_DECISION_REFERENCE_INVALID,
            "RelatedButNotEquivalentRecord resolution_decision_record_id is not resolvable in the validation context.",
            field_ref="resolution_decision_record_id",
        )
    elif decision.resolution_status is not ResolutionStatus.RELATED_NOT_EQUIVALENT:
        collector.add(
            RuleCode.RELATED_DECISION_STATUS_MISMATCH,
            "RelatedButNotEquivalentRecord must point to a ResolutionDecisionRecord with RELATED_NOT_EQUIVALENT status.",
            field_ref="resolution_decision_record_id",
        )
    if related_record.source_observed_record_id not in context.observed_records_by_id:
        collector.add(
            RuleCode.RELATED_SOURCE_REFERENCE_INVALID,
            "RelatedButNotEquivalentRecord source_observed_record_id is not resolvable in the validation context.",
            field_ref="source_observed_record_id",
        )
    for observed_record_id in related_record.related_observed_record_ids:
        if observed_record_id not in context.observed_records_by_id:
            collector.add(
                RuleCode.RELATED_OBSERVED_REFERENCE_INVALID,
                "RelatedButNotEquivalentRecord related_observed_record_ids contains an unresolved observed record.",
                field_ref="related_observed_record_ids",
            )
    if related_record.related_entity_id is not None and related_record.related_entity_id not in context.entities_by_id:
        collector.add(
            RuleCode.RELATED_ENTITY_REFERENCE_INVALID,
            "RelatedButNotEquivalentRecord related_entity_id is not resolvable in the validation context.",
            field_ref="related_entity_id",
        )
    collector.add(
        RuleCode.RELATED_DECLARED,
        "RelatedButNotEquivalentRecord declares a governed relation that must not be mistaken for shared identity.",
        field_ref="relationship_type",
    )


def _validate_decision_status_against_set(
    resolution_decision_record: ResolutionDecisionRecord,
    candidate_match_set,
    collector: ViolationCollector,
) -> None:
    if (
        resolution_decision_record.resolution_status is ResolutionStatus.CONFIRMED
        and candidate_match_set.candidate_match_status is not CandidateMatchStatus.CONFIRMED
    ):
        collector.add(
            RuleCode.DECISION_SET_STATUS_MISMATCH,
            "Confirmed decisions require a CandidateMatchSet with CONFIRMED status.",
            field_ref="candidate_match_set_id",
        )
    if (
        resolution_decision_record.resolution_status is ResolutionStatus.NO_MATCH
        and candidate_match_set.candidate_match_status is not CandidateMatchStatus.REJECTED
    ):
        collector.add(
            RuleCode.DECISION_SET_STATUS_MISMATCH,
            "No-match decisions require a CandidateMatchSet with REJECTED status.",
            field_ref="candidate_match_set_id",
        )
    if (
        resolution_decision_record.resolution_status is ResolutionStatus.AMBIGUOUS
        and candidate_match_set.candidate_match_status is not CandidateMatchStatus.OPEN
    ):
        collector.add(
            RuleCode.DECISION_SET_STATUS_MISMATCH,
            "Ambiguous decisions require a CandidateMatchSet with OPEN status.",
            field_ref="candidate_match_set_id",
        )
