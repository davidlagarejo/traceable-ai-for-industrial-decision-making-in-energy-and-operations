from __future__ import annotations

from .alias_resolver import BasicAliasResolver
from .context import ResolutionCatalog, normalize_label
from .results import (
    AliasResolutionKind,
    CandidateMatchOutcome,
    CandidateMatchResult,
)
from ..domain.enums import AmbiguityStatus, EquivalenceStatus, MatchStatus, TaxonomyDomain
from ..domain.records import CandidateMatchRecord, EquivalenceRecord
from ..domain.value_objects import ConfidenceScore, SemanticScope, TaxonomyLocator


def _max_confidence(records: tuple[CandidateMatchRecord, ...]) -> ConfidenceScore:
    return max(records, key=lambda item: item.confidence.value).confidence


def _unique_locators(values: list[TaxonomyLocator]) -> tuple[TaxonomyLocator, ...]:
    ordered: list[TaxonomyLocator] = []
    seen: set[TaxonomyLocator] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)


class BasicCandidateMatcher:
    def __init__(
        self,
        catalog: ResolutionCatalog,
        *,
        alias_resolver: BasicAliasResolver | None = None,
    ) -> None:
        self._catalog = catalog
        self._alias_resolver = alias_resolver or BasicAliasResolver(catalog)

    def match_label(
        self,
        label: str,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> CandidateMatchResult:
        resolution = self._alias_resolver.resolve_label(
            label,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        if resolution.kind is AliasResolutionKind.RESOLVED_CANONICAL:
            return CandidateMatchResult(
                source_label=label,
                source_ref=None,
                normalized_label=resolution.normalized_label,
                outcome=CandidateMatchOutcome.CONFIRMED_MATCH,
                target_ref=resolution.resolved_target_ref,
                candidate_refs=(),
                confidence=ConfidenceScore(1.0),
                rationale="Exact canonical term match provides a controlled confirmed match.",
                source_resolution_kind=resolution.kind,
            )
        if resolution.kind is AliasResolutionKind.RESOLVED_ALIAS:
            return CandidateMatchResult(
                source_label=label,
                source_ref=None,
                normalized_label=resolution.normalized_label,
                outcome=CandidateMatchOutcome.CONFIRMED_MATCH,
                target_ref=resolution.resolved_target_ref,
                candidate_refs=(),
                confidence=ConfidenceScore(0.99),
                rationale="Confirmed alias mapping provides a controlled confirmed match.",
                source_resolution_kind=resolution.kind,
            )
        if resolution.kind is AliasResolutionKind.RESOLVED_LEGACY:
            return CandidateMatchResult(
                source_label=label,
                source_ref=None,
                normalized_label=resolution.normalized_label,
                outcome=CandidateMatchOutcome.CANDIDATE_MATCH,
                target_ref=resolution.resolved_target_ref,
                candidate_refs=(),
                confidence=ConfidenceScore(0.85),
                rationale="Legacy term mapping suggests a controlled candidate match but preserves historical caution.",
                source_resolution_kind=resolution.kind,
            )
        if resolution.kind is AliasResolutionKind.AMBIGUOUS:
            return CandidateMatchResult(
                source_label=label,
                source_ref=None,
                normalized_label=resolution.normalized_label,
                outcome=CandidateMatchOutcome.AMBIGUOUS,
                target_ref=None,
                candidate_refs=resolution.candidate_target_refs,
                confidence=None,
                rationale=resolution.rationale,
                source_resolution_kind=resolution.kind,
            )

        candidate_records = self._catalog.candidate_matches_for_label(
            label,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        return self._from_candidate_records(
            source_label=label,
            normalized_label=normalize_label(label),
            candidate_records=candidate_records,
        )

    def match_ref(
        self,
        source_ref: TaxonomyLocator,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> CandidateMatchResult:
        records = self._catalog.equivalence_records_for_ref(
            source_ref,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        if not records:
            return CandidateMatchResult(
                source_label=None,
                source_ref=source_ref,
                normalized_label=None,
                outcome=CandidateMatchOutcome.NO_MATCH,
                target_ref=None,
                candidate_refs=(),
                confidence=None,
                rationale="No explicit equivalence record supports a semantic candidate for the supplied reference.",
                source_resolution_kind=None,
            )

        confirmed = []
        open_candidates = []
        ambiguous_refs = []
        for item in records:
            other_ref = item.right_ref if item.left_ref == source_ref else item.left_ref
            if item.equivalence_status is EquivalenceStatus.REJECTED:
                continue
            if item.equivalence_status is EquivalenceStatus.CONFIRMED and item.ambiguity_status is AmbiguityStatus.CLEAR:
                confirmed.append(other_ref)
                continue
            if item.ambiguity_status is not AmbiguityStatus.CLEAR:
                ambiguous_refs.append(other_ref)
                continue
            if item.equivalence_status in {EquivalenceStatus.CANDIDATE, EquivalenceStatus.CONTEXTUAL}:
                open_candidates.append(other_ref)

        if ambiguous_refs:
            return CandidateMatchResult(
                source_label=None,
                source_ref=source_ref,
                normalized_label=None,
                outcome=CandidateMatchOutcome.AMBIGUOUS,
                target_ref=None,
                candidate_refs=_unique_locators(confirmed + open_candidates + ambiguous_refs),
                confidence=None,
                rationale="Equivalence records preserve ambiguity and do not justify automatic confirmation.",
                source_resolution_kind=None,
            )

        unique_confirmed = _unique_locators(confirmed)
        if len(unique_confirmed) == 1 and not open_candidates:
            return CandidateMatchResult(
                source_label=None,
                source_ref=source_ref,
                normalized_label=None,
                outcome=CandidateMatchOutcome.CONFIRMED_MATCH,
                target_ref=unique_confirmed[0],
                candidate_refs=(),
                confidence=ConfidenceScore(0.9),
                rationale="A confirmed equivalence record provides a controlled confirmed candidate.",
                source_resolution_kind=None,
            )

        unique_open = _unique_locators(open_candidates)
        if len(unique_open) == 1 and not unique_confirmed:
            return CandidateMatchResult(
                source_label=None,
                source_ref=source_ref,
                normalized_label=None,
                outcome=CandidateMatchOutcome.CANDIDATE_MATCH,
                target_ref=unique_open[0],
                candidate_refs=(),
                confidence=ConfidenceScore(0.7),
                rationale="A contextual or candidate equivalence suggests a candidate but not a confirmed match.",
                source_resolution_kind=None,
            )

        all_candidates = _unique_locators(confirmed + open_candidates)
        if all_candidates:
            return CandidateMatchResult(
                source_label=None,
                source_ref=source_ref,
                normalized_label=None,
                outcome=CandidateMatchOutcome.AMBIGUOUS,
                target_ref=None,
                candidate_refs=all_candidates,
                confidence=None,
                rationale="Multiple explicit equivalence candidates exist and ambiguity must be preserved.",
                source_resolution_kind=None,
            )

        return CandidateMatchResult(
            source_label=None,
            source_ref=source_ref,
            normalized_label=None,
            outcome=CandidateMatchOutcome.NO_MATCH,
            target_ref=None,
            candidate_refs=(),
            confidence=None,
            rationale="Explicit semantic relations do not support a usable candidate match.",
            source_resolution_kind=None,
        )

    @staticmethod
    def _from_candidate_records(
        *,
        source_label: str,
        normalized_label: str,
        candidate_records: tuple[CandidateMatchRecord, ...],
    ) -> CandidateMatchResult:
        if not candidate_records:
            return CandidateMatchResult(
                source_label=source_label,
                source_ref=None,
                normalized_label=normalized_label,
                outcome=CandidateMatchOutcome.NO_MATCH,
                target_ref=None,
                candidate_refs=(),
                confidence=None,
                rationale="No explicit candidate match record supports the requested label.",
                source_resolution_kind=None,
            )

        active_records = tuple(
            item for item in candidate_records if item.match_status is not MatchStatus.REJECTED
        )
        if not active_records:
            return CandidateMatchResult(
                source_label=source_label,
                source_ref=None,
                normalized_label=normalized_label,
                outcome=CandidateMatchOutcome.NO_MATCH,
                target_ref=None,
                candidate_refs=(),
                confidence=None,
                rationale="Candidate match records exist but all of them are explicitly rejected.",
                source_resolution_kind=None,
            )

        unique_targets = _unique_locators([item.candidate_ref for item in active_records])
        if (
            len(unique_targets) > 1
            or any(item.match_status is MatchStatus.AMBIGUOUS for item in active_records)
            or any(item.ambiguity_status is not AmbiguityStatus.CLEAR for item in active_records)
        ):
            return CandidateMatchResult(
                source_label=source_label,
                source_ref=None,
                normalized_label=normalized_label,
                outcome=CandidateMatchOutcome.AMBIGUOUS,
                target_ref=None,
                candidate_refs=unique_targets,
                confidence=None,
                rationale="Explicit candidate match records preserve ambiguity and do not justify automatic confirmation.",
                source_resolution_kind=None,
            )

        if any(item.match_status is MatchStatus.CONFIRMED for item in active_records):
            return CandidateMatchResult(
                source_label=source_label,
                source_ref=None,
                normalized_label=normalized_label,
                outcome=CandidateMatchOutcome.CONFIRMED_MATCH,
                target_ref=unique_targets[0],
                candidate_refs=(),
                confidence=_max_confidence(active_records),
                rationale="An explicit confirmed candidate match record supports the requested label.",
                source_resolution_kind=None,
            )

        return CandidateMatchResult(
            source_label=source_label,
            source_ref=None,
            normalized_label=normalized_label,
            outcome=CandidateMatchOutcome.CANDIDATE_MATCH,
            target_ref=unique_targets[0],
            candidate_refs=(),
            confidence=_max_confidence(active_records),
            rationale="An explicit candidate match record exists but remains open.",
            source_resolution_kind=None,
        )


__all__ = ["BasicCandidateMatcher"]
