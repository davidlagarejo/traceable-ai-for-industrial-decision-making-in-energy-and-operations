from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    CandidateMatchStatus,
    CanonicalEntityStatus,
    EntityType,
)
from .errors import DomainInvariantError
from .value_objects import (
    AliasLabel,
    CandidateMatchRecordId,
    CandidateMatchSetId,
    CanonicalName,
    EntityAliasRecordId,
    EntityId,
    NormalizedFieldRef,
    ObservedLabel,
    ObservedNameRecordId,
    ObservedRecordId,
    ResolutionConfidenceRecordId,
    ResolutionEvidenceRecordId,
    Rationale,
    SourceProvenanceRefs,
    _ensure_unique,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class ObservedRecord:
    observed_record_id: ObservedRecordId
    entity_type: EntityType
    source_provenance: SourceProvenanceRefs
    primary_observed_name_record_id: ObservedNameRecordId
    observed_name_record_ids: tuple[ObservedNameRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.observed_name_record_ids:
            raise DomainInvariantError("ObservedRecord.observed_name_record_ids must not be empty.")
        _ensure_unique(self.observed_name_record_ids, "ObservedRecord.observed_name_record_ids")
        if self.primary_observed_name_record_id not in self.observed_name_record_ids:
            raise DomainInvariantError(
                "ObservedRecord.primary_observed_name_record_id must be part of observed_name_record_ids."
            )


@dataclass(frozen=True, slots=True)
class ObservedNameRecord:
    observed_name_record_id: ObservedNameRecordId
    observed_record_id: ObservedRecordId
    observed_label: ObservedLabel
    is_primary: bool
    source_normalized_field_ref: NormalizedFieldRef | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class CanonicalEntity:
    entity_id: EntityId
    entity_type: EntityType
    canonical_name: CanonicalName
    entity_status: CanonicalEntityStatus
    created_at: datetime
    effective_from: datetime
    retired_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        object.__setattr__(
            self,
            "effective_from",
            _require_timezone(self.effective_from, "effective_from"),
        )
        if self.retired_at is not None:
            object.__setattr__(self, "retired_at", _require_timezone(self.retired_at, "retired_at"))
            if self.entity_status is CanonicalEntityStatus.ACTIVE:
                raise DomainInvariantError(
                    "CanonicalEntity with retired_at must not remain ACTIVE."
                )


@dataclass(frozen=True, slots=True)
class EntityAliasRecord:
    entity_alias_record_id: EntityAliasRecordId
    entity_id: EntityId
    alias_label: AliasLabel
    source_observed_name_record_id: ObservedNameRecordId | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class CandidateMatchRecord:
    candidate_match_record_id: CandidateMatchRecordId
    candidate_match_set_id: CandidateMatchSetId
    source_observed_record_id: ObservedRecordId
    candidate_observed_record_ids: tuple[ObservedRecordId, ...]
    candidate_entity_id: EntityId | None
    candidate_match_status: CandidateMatchStatus
    rationale: Rationale
    evidence_record_ids: tuple[ResolutionEvidenceRecordId, ...]
    confidence_record_id: ResolutionConfidenceRecordId | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(
            self.candidate_observed_record_ids,
            "CandidateMatchRecord.candidate_observed_record_ids",
        )
        _ensure_unique(self.evidence_record_ids, "CandidateMatchRecord.evidence_record_ids")
        if self.source_observed_record_id in self.candidate_observed_record_ids:
            raise DomainInvariantError(
                "CandidateMatchRecord candidate_observed_record_ids must not include source_observed_record_id."
            )
        if self.candidate_entity_id is None and not self.candidate_observed_record_ids:
            raise DomainInvariantError(
                "CandidateMatchRecord requires candidate_entity_id or candidate_observed_record_ids."
            )


@dataclass(frozen=True, slots=True)
class CandidateMatchSet:
    candidate_match_set_id: CandidateMatchSetId
    anchor_observed_record_ids: tuple[ObservedRecordId, ...]
    candidate_match_record_ids: tuple[CandidateMatchRecordId, ...]
    candidate_match_status: CandidateMatchStatus
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.anchor_observed_record_ids:
            raise DomainInvariantError(
                "CandidateMatchSet.anchor_observed_record_ids must not be empty."
            )
        if not self.candidate_match_record_ids:
            raise DomainInvariantError(
                "CandidateMatchSet.candidate_match_record_ids must not be empty."
            )
        _ensure_unique(
            self.anchor_observed_record_ids,
            "CandidateMatchSet.anchor_observed_record_ids",
        )
        _ensure_unique(
            self.candidate_match_record_ids,
            "CandidateMatchSet.candidate_match_record_ids",
        )
