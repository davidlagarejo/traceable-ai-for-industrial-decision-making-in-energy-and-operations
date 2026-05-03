from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from ..domain.enums import JoinSafetyLevel
from ..domain.value_objects import ConfidenceScore, JoinKeyName, TaxonomyLocator


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty.")
    return normalized


class AliasResolutionKind(str, Enum):
    RESOLVED_CANONICAL = "resolved_canonical"
    RESOLVED_ALIAS = "resolved_alias"
    RESOLVED_LEGACY = "resolved_legacy"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class CandidateMatchOutcome(str, Enum):
    CONFIRMED_MATCH = "confirmed_match"
    CANDIDATE_MATCH = "candidate_match"
    AMBIGUOUS = "ambiguous"
    NO_MATCH = "no_match"


class SemanticJoinOutcome(str, Enum):
    SAFE_JOIN = "safe_join"
    CONDITIONAL_JOIN = "conditional_join"
    UNSAFE_JOIN = "unsafe_join"


@dataclass(frozen=True, slots=True)
class AliasResolutionResult:
    source_label: str
    normalized_label: str
    kind: AliasResolutionKind
    resolved_target_ref: TaxonomyLocator | None
    supporting_ref: TaxonomyLocator | None
    candidate_target_refs: tuple[TaxonomyLocator, ...]
    rationale: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_label", _require_text(self.source_label, "source_label"))
        object.__setattr__(self, "normalized_label", _require_text(self.normalized_label, "normalized_label"))
        object.__setattr__(self, "rationale", _require_text(self.rationale, "rationale"))
        if self.kind in {
            AliasResolutionKind.RESOLVED_CANONICAL,
            AliasResolutionKind.RESOLVED_ALIAS,
            AliasResolutionKind.RESOLVED_LEGACY,
        } and self.resolved_target_ref is None:
            raise ValueError("Resolved alias results must carry resolved_target_ref.")
        if self.kind is AliasResolutionKind.AMBIGUOUS and not self.candidate_target_refs:
            raise ValueError("Ambiguous alias results must carry candidate_target_refs.")
        if self.kind is AliasResolutionKind.UNRESOLVED:
            if self.resolved_target_ref is not None or self.candidate_target_refs:
                raise ValueError("Unresolved alias results must not carry resolved targets.")


@dataclass(frozen=True, slots=True)
class CandidateMatchResult:
    source_label: str | None
    source_ref: TaxonomyLocator | None
    normalized_label: str | None
    outcome: CandidateMatchOutcome
    target_ref: TaxonomyLocator | None
    candidate_refs: tuple[TaxonomyLocator, ...]
    confidence: ConfidenceScore | None
    rationale: str
    source_resolution_kind: AliasResolutionKind | None

    def __post_init__(self) -> None:
        if self.source_label is not None:
            object.__setattr__(self, "source_label", _require_text(self.source_label, "source_label"))
        if self.normalized_label is not None:
            object.__setattr__(self, "normalized_label", _require_text(self.normalized_label, "normalized_label"))
        object.__setattr__(self, "rationale", _require_text(self.rationale, "rationale"))
        if self.outcome in {
            CandidateMatchOutcome.CONFIRMED_MATCH,
            CandidateMatchOutcome.CANDIDATE_MATCH,
        }:
            if self.target_ref is None or self.confidence is None:
                raise ValueError("Confirmed and candidate matches require target_ref and confidence.")
        if self.outcome is CandidateMatchOutcome.AMBIGUOUS and not self.candidate_refs:
            raise ValueError("Ambiguous matches must carry candidate_refs.")
        if self.outcome is CandidateMatchOutcome.NO_MATCH:
            if self.target_ref is not None or self.candidate_refs:
                raise ValueError("No-match results must not carry target candidates.")


@dataclass(frozen=True, slots=True)
class SemanticJoinResult:
    join_key: JoinKeyName
    source_label: str
    normalized_label: str
    outcome: SemanticJoinOutcome
    target_ref: TaxonomyLocator | None
    join_safety_level: JoinSafetyLevel | None
    rationale: str
    resolution_kind: AliasResolutionKind | None
    match_outcome: CandidateMatchOutcome | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_label", _require_text(self.source_label, "source_label"))
        object.__setattr__(self, "normalized_label", _require_text(self.normalized_label, "normalized_label"))
        object.__setattr__(self, "rationale", _require_text(self.rationale, "rationale"))
        if self.outcome in {
            SemanticJoinOutcome.SAFE_JOIN,
            SemanticJoinOutcome.CONDITIONAL_JOIN,
        }:
            if self.target_ref is None or self.join_safety_level is None:
                raise ValueError("Resolved joins must carry target_ref and join_safety_level.")


__all__ = [
    "AliasResolutionKind",
    "AliasResolutionResult",
    "CandidateMatchOutcome",
    "CandidateMatchResult",
    "SemanticJoinOutcome",
    "SemanticJoinResult",
]
