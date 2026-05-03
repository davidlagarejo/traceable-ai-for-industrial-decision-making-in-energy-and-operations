from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    AmbiguityStatus,
    ConfidenceStatus,
    EvidenceBasisType,
    HistoricalEventType,
    HistoryStatus,
    RelatedEntityRelationshipType,
    ResolutionMode,
    ResolutionStatus,
)
from .errors import DomainInvariantError
from .value_objects import (
    AmbiguityBasis,
    CandidateMatchSetId,
    ConfidenceMethod,
    ConfidenceValue,
    EntityHistoryRecordId,
    EntityHistorySummary,
    EntityId,
    EvidenceSummary,
    MergeEventRecordId,
    ObservedRecordId,
    RelationBasis,
    ResolutionConfidenceRecordId,
    ResolutionDecisionRecordId,
    ResolutionEvidenceRecordId,
    Rationale,
    SourceProvenanceRefs,
    SplitEventRecordId,
    _ensure_unique,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class ResolutionEvidenceRecord:
    resolution_evidence_record_id: ResolutionEvidenceRecordId
    evidence_basis_type: EvidenceBasisType
    source_provenance: SourceProvenanceRefs
    supports_match: bool
    evidence_summary: EvidenceSummary
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class ResolutionConfidenceRecord:
    resolution_confidence_record_id: ResolutionConfidenceRecordId
    confidence_status: ConfidenceStatus
    confidence_method: ConfidenceMethod
    confidence_value: ConfidenceValue | None
    rationale: Rationale
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class ResolutionDecisionRecord:
    resolution_decision_record_id: ResolutionDecisionRecordId
    resolution_status: ResolutionStatus
    resolution_mode: ResolutionMode
    candidate_match_set_id: CandidateMatchSetId | None
    decision_scope_observed_record_ids: tuple[ObservedRecordId, ...]
    rationale: Rationale
    evidence_record_ids: tuple[ResolutionEvidenceRecordId, ...]
    confidence_record_id: ResolutionConfidenceRecordId | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(
            self.decision_scope_observed_record_ids,
            "ResolutionDecisionRecord.decision_scope_observed_record_ids",
        )
        _ensure_unique(
            self.evidence_record_ids,
            "ResolutionDecisionRecord.evidence_record_ids",
        )
        if self.candidate_match_set_id is None and not self.decision_scope_observed_record_ids:
            raise DomainInvariantError(
                "ResolutionDecisionRecord requires candidate_match_set_id or decision scope."
            )


@dataclass(frozen=True, slots=True)
class ConfirmedMatchRecord:
    resolution_decision_record_id: ResolutionDecisionRecordId
    entity_id: EntityId
    observed_record_ids: tuple[ObservedRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.observed_record_ids:
            raise DomainInvariantError("ConfirmedMatchRecord.observed_record_ids must not be empty.")
        _ensure_unique(self.observed_record_ids, "ConfirmedMatchRecord.observed_record_ids")


@dataclass(frozen=True, slots=True)
class NoMatchRecord:
    resolution_decision_record_id: ResolutionDecisionRecordId
    subject_observed_record_id: ObservedRecordId
    rejected_observed_record_ids: tuple[ObservedRecordId, ...]
    rejected_entity_id: EntityId | None
    rationale: Rationale
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.rejected_observed_record_ids, "NoMatchRecord.rejected_observed_record_ids")
        if self.subject_observed_record_id in self.rejected_observed_record_ids:
            raise DomainInvariantError(
                "NoMatchRecord.rejected_observed_record_ids must not include subject_observed_record_id."
            )
        if self.rejected_entity_id is None and not self.rejected_observed_record_ids:
            raise DomainInvariantError(
                "NoMatchRecord requires rejected_entity_id or rejected_observed_record_ids."
            )


@dataclass(frozen=True, slots=True)
class AmbiguousResolutionRecord:
    resolution_decision_record_id: ResolutionDecisionRecordId
    candidate_match_set_id: CandidateMatchSetId | None
    observed_record_ids: tuple[ObservedRecordId, ...]
    plausible_entity_ids: tuple[EntityId, ...]
    ambiguity_status: AmbiguityStatus
    ambiguity_basis: AmbiguityBasis
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.observed_record_ids, "AmbiguousResolutionRecord.observed_record_ids")
        _ensure_unique(self.plausible_entity_ids, "AmbiguousResolutionRecord.plausible_entity_ids")
        if self.candidate_match_set_id is None and not self.observed_record_ids:
            raise DomainInvariantError(
                "AmbiguousResolutionRecord requires candidate_match_set_id or observed_record_ids."
            )
        if not self.plausible_entity_ids and len(self.observed_record_ids) < 2:
            raise DomainInvariantError(
                "AmbiguousResolutionRecord requires multiple observed records or plausible_entity_ids."
            )


@dataclass(frozen=True, slots=True)
class RelatedButNotEquivalentRecord:
    resolution_decision_record_id: ResolutionDecisionRecordId
    source_observed_record_id: ObservedRecordId
    related_observed_record_ids: tuple[ObservedRecordId, ...]
    related_entity_id: EntityId | None
    relationship_type: RelatedEntityRelationshipType
    relation_basis: RelationBasis
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(
            self.related_observed_record_ids,
            "RelatedButNotEquivalentRecord.related_observed_record_ids",
        )
        if self.source_observed_record_id in self.related_observed_record_ids:
            raise DomainInvariantError(
                "RelatedButNotEquivalentRecord.related_observed_record_ids must not include source_observed_record_id."
            )
        if self.related_entity_id is None and not self.related_observed_record_ids:
            raise DomainInvariantError(
                "RelatedButNotEquivalentRecord requires related_entity_id or related_observed_record_ids."
            )


@dataclass(frozen=True, slots=True)
class MergeEventRecord:
    merge_event_record_id: MergeEventRecordId
    merged_entity_ids: tuple[EntityId, ...]
    surviving_entity_id: EntityId
    resolution_decision_record_id: ResolutionDecisionRecordId | None
    rationale: Rationale
    event_type: HistoricalEventType
    effective_from: datetime
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "effective_from", _require_timezone(self.effective_from, "effective_from"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.event_type is not HistoricalEventType.MERGE:
            raise DomainInvariantError("MergeEventRecord.event_type must be MERGE.")
        if len(self.merged_entity_ids) < 2:
            raise DomainInvariantError("MergeEventRecord.merged_entity_ids must contain at least two entities.")
        _ensure_unique(self.merged_entity_ids, "MergeEventRecord.merged_entity_ids")
        if self.surviving_entity_id not in self.merged_entity_ids:
            raise DomainInvariantError(
                "MergeEventRecord.surviving_entity_id must be part of merged_entity_ids."
            )


@dataclass(frozen=True, slots=True)
class SplitEventRecord:
    split_event_record_id: SplitEventRecordId
    source_entity_id: EntityId
    successor_entity_ids: tuple[EntityId, ...]
    resolution_decision_record_id: ResolutionDecisionRecordId | None
    rationale: Rationale
    event_type: HistoricalEventType
    effective_from: datetime
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "effective_from", _require_timezone(self.effective_from, "effective_from"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.event_type is not HistoricalEventType.SPLIT:
            raise DomainInvariantError("SplitEventRecord.event_type must be SPLIT.")
        if len(self.successor_entity_ids) < 2:
            raise DomainInvariantError("SplitEventRecord.successor_entity_ids must contain at least two entities.")
        _ensure_unique(self.successor_entity_ids, "SplitEventRecord.successor_entity_ids")
        if self.source_entity_id in self.successor_entity_ids:
            raise DomainInvariantError(
                "SplitEventRecord.successor_entity_ids must not include source_entity_id."
            )


@dataclass(frozen=True, slots=True)
class EntityHistoryRecord:
    entity_history_record_id: EntityHistoryRecordId
    entity_id: EntityId
    history_status: HistoryStatus
    resolution_decision_record_id: ResolutionDecisionRecordId | None
    merge_event_record_id: MergeEventRecordId | None
    split_event_record_id: SplitEventRecordId | None
    summary: EntityHistorySummary
    effective_from: datetime
    effective_to: datetime | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "effective_from", _require_timezone(self.effective_from, "effective_from"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.effective_to is not None:
            object.__setattr__(self, "effective_to", _require_timezone(self.effective_to, "effective_to"))
            if self.effective_to <= self.effective_from:
                raise DomainInvariantError("EntityHistoryRecord.effective_to must be after effective_from.")
        if (
            self.resolution_decision_record_id is None
            and self.merge_event_record_id is None
            and self.split_event_record_id is None
        ):
            raise DomainInvariantError(
                "EntityHistoryRecord requires a decision or historical event reference."
            )
