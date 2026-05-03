from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .entities import TaxonomyVersion
from .enums import (
    AmbiguityStatus,
    BoundaryStatus,
    ComparabilityStatus,
    ConflictSeverity,
    DeprecationStatus,
    EquivalenceStatus,
    JoinSafetyLevel,
    MatchStatus,
    SemanticIntegrityStatus,
    SemanticRelationType,
    TaxonomyChangeKind,
)
from .errors import DomainInvariantError
from .value_objects import (
    AliasRecordId,
    BoundaryRecordId,
    CandidateMatchRecordId,
    ConfidenceScore,
    DeprecationRecordId,
    EquivalenceRecordId,
    JoinKeyName,
    JoinKeySemanticRecordId,
    MatchRationale,
    SemanticIntegrityRecordId,
    SemanticScope,
    SemanticText,
    TaxonomyChangeRecordId,
    TaxonomyLocator,
    TaxonomyNodeId,
    TaxonomyVersionId,
    _ensure_unique,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class EquivalenceRecord:
    equivalence_record_id: EquivalenceRecordId
    left_ref: TaxonomyLocator
    right_ref: TaxonomyLocator
    equivalence_status: EquivalenceStatus
    ambiguity_status: AmbiguityStatus
    rationale: MatchRationale
    semantic_scope: SemanticScope
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.left_ref == self.right_ref:
            raise DomainInvariantError("EquivalenceRecord must compare two distinct refs.")
        if self.left_ref.target_kind != self.right_ref.target_kind:
            raise DomainInvariantError(
                "EquivalenceRecord may only compare refs of the same semantic kind."
            )
        if self.left_ref.target_kind not in {
            self.left_ref.target_kind.TAXONOMY_NODE,
            self.left_ref.target_kind.CANONICAL_TERM,
            self.left_ref.target_kind.CANONICAL_ENTITY,
        }:
            raise DomainInvariantError(
                "EquivalenceRecord supports taxonomy_node, canonical_term or canonical_entity refs only."
            )
        if self.equivalence_status is EquivalenceStatus.CONFIRMED and self.ambiguity_status is not AmbiguityStatus.CLEAR:
            raise DomainInvariantError(
                "Confirmed equivalence requires clear ambiguity status."
            )


@dataclass(frozen=True, slots=True)
class CandidateMatchRecord:
    candidate_match_record_id: CandidateMatchRecordId
    source_label: str
    candidate_ref: TaxonomyLocator
    match_status: MatchStatus
    ambiguity_status: AmbiguityStatus
    semantic_scope: SemanticScope
    confidence: ConfidenceScore
    rationale: MatchRationale
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_label", self.source_label.strip())
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.source_label:
            raise DomainInvariantError("CandidateMatchRecord.source_label must be non-empty.")
        if self.candidate_ref.target_kind not in {
            self.candidate_ref.target_kind.TAXONOMY_NODE,
            self.candidate_ref.target_kind.CANONICAL_TERM,
            self.candidate_ref.target_kind.CANONICAL_ENTITY,
        }:
            raise DomainInvariantError(
                "CandidateMatchRecord.candidate_ref must point to a taxonomy_node, canonical_term or canonical_entity."
            )
        if self.match_status is MatchStatus.CONFIRMED and self.ambiguity_status is not AmbiguityStatus.CLEAR:
            raise DomainInvariantError("Confirmed candidate matches require clear ambiguity status.")


@dataclass(frozen=True, slots=True)
class BoundaryRecord:
    boundary_record_id: BoundaryRecordId
    taxonomy_node_id: TaxonomyNodeId
    boundary_status: BoundaryStatus
    semantic_scope: SemanticScope
    inclusion_rule: SemanticText | None
    exclusion_rule: SemanticText | None
    positive_examples: tuple[str, ...]
    negative_examples: tuple[str, ...]
    nearest_valid_ref: TaxonomyLocator | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        object.__setattr__(self, "positive_examples", tuple(item.strip() for item in self.positive_examples if item.strip()))
        object.__setattr__(self, "negative_examples", tuple(item.strip() for item in self.negative_examples if item.strip()))
        _ensure_unique(self.positive_examples, "positive_examples")
        _ensure_unique(self.negative_examples, "negative_examples")
        if not any(
            (
                self.inclusion_rule is not None,
                self.exclusion_rule is not None,
                self.positive_examples,
                self.negative_examples,
                self.nearest_valid_ref is not None,
            )
        ):
            raise DomainInvariantError("BoundaryRecord must carry semantic boundary content.")


@dataclass(frozen=True, slots=True)
class JoinKeySemanticRecord:
    join_key_semantic_record_id: JoinKeySemanticRecordId
    join_key: JoinKeyName
    target_ref: TaxonomyLocator
    semantic_scope: SemanticScope
    join_safety_level: JoinSafetyLevel
    rationale: MatchRationale
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.target_ref.target_kind not in {
            self.target_ref.target_kind.TAXONOMY_NODE,
            self.target_ref.target_kind.CANONICAL_ENTITY,
            self.target_ref.target_kind.CANONICAL_TERM,
        }:
            raise DomainInvariantError(
                "JoinKeySemanticRecord.target_ref must point to a taxonomy_node, canonical_term or canonical_entity."
            )


@dataclass(frozen=True, slots=True)
class DeprecationRecord:
    deprecation_record_id: DeprecationRecordId
    deprecated_ref: TaxonomyLocator
    replacement_ref: TaxonomyLocator | None
    deprecation_status: DeprecationStatus
    rationale: MatchRationale
    effective_from: datetime
    deprecated_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "effective_from", _require_timezone(self.effective_from, "effective_from"))
        object.__setattr__(self, "deprecated_at", _require_timezone(self.deprecated_at, "deprecated_at"))
        if self.replacement_ref is not None and self.replacement_ref == self.deprecated_ref:
            raise DomainInvariantError("replacement_ref must not point to deprecated_ref.")
        if self.deprecation_status is DeprecationStatus.REPLACED and self.replacement_ref is None:
            raise DomainInvariantError("Replaced deprecations must declare replacement_ref.")


@dataclass(frozen=True, slots=True)
class TaxonomyChangeRecord:
    taxonomy_change_record_id: TaxonomyChangeRecordId
    source_taxonomy_version_id: TaxonomyVersionId | None
    target_taxonomy_version_id: TaxonomyVersionId
    change_kind: TaxonomyChangeKind
    affected_refs: tuple[TaxonomyLocator, ...]
    comparability_status: ComparabilityStatus
    severity: ConflictSeverity
    summary: SemanticText
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.affected_refs, "affected_refs")
        if self.source_taxonomy_version_id == self.target_taxonomy_version_id:
            raise DomainInvariantError(
                "TaxonomyChangeRecord source and target versions must differ when both are present."
            )
        if not self.affected_refs and self.source_taxonomy_version_id is None:
            raise DomainInvariantError(
                "TaxonomyChangeRecord must reference affected refs or a source version."
            )

    @classmethod
    def for_versions(
        cls,
        *,
        taxonomy_change_record_id: TaxonomyChangeRecordId,
        source_version: TaxonomyVersion | None,
        target_version: TaxonomyVersion,
        change_kind: TaxonomyChangeKind,
        affected_refs: tuple[TaxonomyLocator, ...],
        comparability_status: ComparabilityStatus,
        severity: ConflictSeverity,
        summary: SemanticText,
        created_at: datetime,
    ) -> "TaxonomyChangeRecord":
        if source_version is not None and source_version.taxonomy_registry_id != target_version.taxonomy_registry_id:
            raise DomainInvariantError(
                "TaxonomyChangeRecord can only compare versions from the same taxonomy registry."
            )
        return cls(
            taxonomy_change_record_id=taxonomy_change_record_id,
            source_taxonomy_version_id=(
                None if source_version is None else source_version.taxonomy_version_id
            ),
            target_taxonomy_version_id=target_version.taxonomy_version_id,
            change_kind=change_kind,
            affected_refs=affected_refs,
            comparability_status=comparability_status,
            severity=severity,
            summary=summary,
            created_at=created_at,
        )


@dataclass(frozen=True, slots=True)
class SemanticIntegrityRecord:
    semantic_integrity_record_id: SemanticIntegrityRecordId
    taxonomy_version_id: TaxonomyVersionId
    integrity_status: SemanticIntegrityStatus
    ambiguous_alias_ids: tuple[AliasRecordId, ...]
    unresolved_candidate_match_ids: tuple[CandidateMatchRecordId, ...]
    conflicting_refs: tuple[TaxonomyLocator, ...]
    details: tuple[str, ...]
    checked_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "checked_at", _require_timezone(self.checked_at, "checked_at"))
        object.__setattr__(self, "details", tuple(item.strip() for item in self.details if item.strip()))
        _ensure_unique(self.ambiguous_alias_ids, "ambiguous_alias_ids")
        _ensure_unique(self.unresolved_candidate_match_ids, "unresolved_candidate_match_ids")
        _ensure_unique(self.conflicting_refs, "conflicting_refs")
        _ensure_unique(self.details, "details")
        if self.integrity_status is SemanticIntegrityStatus.OK:
            if self.ambiguous_alias_ids or self.unresolved_candidate_match_ids or self.conflicting_refs:
                raise DomainInvariantError(
                    "SemanticIntegrityRecord cannot be OK while critical issues are present."
                )
        elif not (
            self.ambiguous_alias_ids
            or self.unresolved_candidate_match_ids
            or self.conflicting_refs
            or self.details
        ):
            raise DomainInvariantError(
                "Non-OK SemanticIntegrityRecord must explain what is wrong."
            )


__all__ = [
    "BoundaryRecord",
    "CandidateMatchRecord",
    "DeprecationRecord",
    "EquivalenceRecord",
    "JoinKeySemanticRecord",
    "SemanticIntegrityRecord",
    "TaxonomyChangeRecord",
]

