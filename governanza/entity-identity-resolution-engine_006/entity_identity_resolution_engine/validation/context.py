from __future__ import annotations

from collections.abc import Iterable

from .._compat import dataclass
from ..domain.entities import (
    CandidateMatchRecord,
    CandidateMatchSet,
    CanonicalEntity,
    EntityAliasRecord,
    ObservedNameRecord,
    ObservedRecord,
)
from ..domain.records import (
    AmbiguousResolutionRecord,
    ConfirmedMatchRecord,
    EntityHistoryRecord,
    MergeEventRecord,
    NoMatchRecord,
    RelatedButNotEquivalentRecord,
    ResolutionConfidenceRecord,
    ResolutionDecisionRecord,
    ResolutionEvidenceRecord,
    SplitEventRecord,
)
from ..domain.value_objects import (
    CandidateMatchRecordId,
    CandidateMatchSetId,
    EntityAliasRecordId,
    EntityHistoryRecordId,
    EntityId,
    MergeEventRecordId,
    ObservedNameRecordId,
    ObservedRecordId,
    ResolutionConfidenceRecordId,
    ResolutionDecisionRecordId,
    ResolutionEvidenceRecordId,
    SplitEventRecordId,
)


@dataclass(frozen=True, slots=True)
class ValidationContext:
    observed_records: tuple[ObservedRecord, ...] = ()
    observed_name_records: tuple[ObservedNameRecord, ...] = ()
    canonical_entities: tuple[CanonicalEntity, ...] = ()
    entity_alias_records: tuple[EntityAliasRecord, ...] = ()
    candidate_match_records: tuple[CandidateMatchRecord, ...] = ()
    candidate_match_sets: tuple[CandidateMatchSet, ...] = ()
    resolution_decision_records: tuple[ResolutionDecisionRecord, ...] = ()
    confirmed_match_records: tuple[ConfirmedMatchRecord, ...] = ()
    no_match_records: tuple[NoMatchRecord, ...] = ()
    ambiguous_resolution_records: tuple[AmbiguousResolutionRecord, ...] = ()
    related_records: tuple[RelatedButNotEquivalentRecord, ...] = ()
    resolution_evidence_records: tuple[ResolutionEvidenceRecord, ...] = ()
    resolution_confidence_records: tuple[ResolutionConfidenceRecord, ...] = ()
    merge_event_records: tuple[MergeEventRecord, ...] = ()
    split_event_records: tuple[SplitEventRecord, ...] = ()
    entity_history_records: tuple[EntityHistoryRecord, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        observed_records: Iterable[ObservedRecord] = (),
        observed_name_records: Iterable[ObservedNameRecord] = (),
        canonical_entities: Iterable[CanonicalEntity] = (),
        entity_alias_records: Iterable[EntityAliasRecord] = (),
        candidate_match_records: Iterable[CandidateMatchRecord] = (),
        candidate_match_sets: Iterable[CandidateMatchSet] = (),
        resolution_decision_records: Iterable[ResolutionDecisionRecord] = (),
        confirmed_match_records: Iterable[ConfirmedMatchRecord] = (),
        no_match_records: Iterable[NoMatchRecord] = (),
        ambiguous_resolution_records: Iterable[AmbiguousResolutionRecord] = (),
        related_records: Iterable[RelatedButNotEquivalentRecord] = (),
        resolution_evidence_records: Iterable[ResolutionEvidenceRecord] = (),
        resolution_confidence_records: Iterable[ResolutionConfidenceRecord] = (),
        merge_event_records: Iterable[MergeEventRecord] = (),
        split_event_records: Iterable[SplitEventRecord] = (),
        entity_history_records: Iterable[EntityHistoryRecord] = (),
    ) -> "ValidationContext":
        return cls(
            observed_records=tuple(observed_records),
            observed_name_records=tuple(observed_name_records),
            canonical_entities=tuple(canonical_entities),
            entity_alias_records=tuple(entity_alias_records),
            candidate_match_records=tuple(candidate_match_records),
            candidate_match_sets=tuple(candidate_match_sets),
            resolution_decision_records=tuple(resolution_decision_records),
            confirmed_match_records=tuple(confirmed_match_records),
            no_match_records=tuple(no_match_records),
            ambiguous_resolution_records=tuple(ambiguous_resolution_records),
            related_records=tuple(related_records),
            resolution_evidence_records=tuple(resolution_evidence_records),
            resolution_confidence_records=tuple(resolution_confidence_records),
            merge_event_records=tuple(merge_event_records),
            split_event_records=tuple(split_event_records),
            entity_history_records=tuple(entity_history_records),
        )

    @property
    def observed_records_by_id(self) -> dict[ObservedRecordId, ObservedRecord]:
        return {item.observed_record_id: item for item in self.observed_records}

    @property
    def observed_names_by_id(self) -> dict[ObservedNameRecordId, ObservedNameRecord]:
        return {item.observed_name_record_id: item for item in self.observed_name_records}

    @property
    def entities_by_id(self) -> dict[EntityId, CanonicalEntity]:
        return {item.entity_id: item for item in self.canonical_entities}

    @property
    def aliases_by_id(self) -> dict[EntityAliasRecordId, EntityAliasRecord]:
        return {item.entity_alias_record_id: item for item in self.entity_alias_records}

    @property
    def candidate_matches_by_id(self) -> dict[CandidateMatchRecordId, CandidateMatchRecord]:
        return {item.candidate_match_record_id: item for item in self.candidate_match_records}

    @property
    def candidate_sets_by_id(self) -> dict[CandidateMatchSetId, CandidateMatchSet]:
        return {item.candidate_match_set_id: item for item in self.candidate_match_sets}

    @property
    def decisions_by_id(self) -> dict[ResolutionDecisionRecordId, ResolutionDecisionRecord]:
        return {item.resolution_decision_record_id: item for item in self.resolution_decision_records}

    @property
    def evidences_by_id(self) -> dict[ResolutionEvidenceRecordId, ResolutionEvidenceRecord]:
        return {item.resolution_evidence_record_id: item for item in self.resolution_evidence_records}

    @property
    def confidences_by_id(self) -> dict[ResolutionConfidenceRecordId, ResolutionConfidenceRecord]:
        return {
            item.resolution_confidence_record_id: item
            for item in self.resolution_confidence_records
        }

    @property
    def merge_events_by_id(self) -> dict[MergeEventRecordId, MergeEventRecord]:
        return {item.merge_event_record_id: item for item in self.merge_event_records}

    @property
    def split_events_by_id(self) -> dict[SplitEventRecordId, SplitEventRecord]:
        return {item.split_event_record_id: item for item in self.split_event_records}

    @property
    def histories_by_id(self) -> dict[EntityHistoryRecordId, EntityHistoryRecord]:
        return {item.entity_history_record_id: item for item in self.entity_history_records}

    def observed_names_for_record(
        self,
        observed_record_id: ObservedRecordId,
    ) -> tuple[ObservedNameRecord, ...]:
        return tuple(
            item
            for item in self.observed_name_records
            if item.observed_record_id == observed_record_id
        )

    def observed_ids_for_candidate_set(
        self,
        candidate_match_set_id: CandidateMatchSetId,
    ) -> set[ObservedRecordId]:
        match_set = self.candidate_sets_by_id.get(candidate_match_set_id)
        if match_set is None:
            return set()
        observed_ids = set(match_set.anchor_observed_record_ids)
        for match_id in match_set.candidate_match_record_ids:
            match = self.candidate_matches_by_id.get(match_id)
            if match is None:
                continue
            observed_ids.add(match.source_observed_record_id)
            observed_ids.update(match.candidate_observed_record_ids)
        return observed_ids
