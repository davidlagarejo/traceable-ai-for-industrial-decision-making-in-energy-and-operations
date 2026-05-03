from __future__ import annotations

from .alias_resolver import BasicAliasResolver
from .candidate_matcher import BasicCandidateMatcher
from .context import ResolutionCatalog, normalize_label
from .results import (
    AliasResolutionKind,
    CandidateMatchOutcome,
    SemanticJoinOutcome,
    SemanticJoinResult,
)
from ..domain.enums import JoinSafetyLevel, TaxonomyDomain
from ..domain.value_objects import JoinKeyName, SemanticScope, TaxonomyLocator


class BasicSemanticJoinResolver:
    def __init__(
        self,
        catalog: ResolutionCatalog,
        *,
        alias_resolver: BasicAliasResolver | None = None,
        candidate_matcher: BasicCandidateMatcher | None = None,
    ) -> None:
        self._catalog = catalog
        self._alias_resolver = alias_resolver or BasicAliasResolver(catalog)
        self._candidate_matcher = candidate_matcher or BasicCandidateMatcher(
            catalog,
            alias_resolver=self._alias_resolver,
        )

    def resolve_join(
        self,
        *,
        join_key: JoinKeyName,
        label: str,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> SemanticJoinResult:
        normalized = normalize_label(label)
        alias_resolution = self._alias_resolver.resolve_label(
            label,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        if alias_resolution.kind is AliasResolutionKind.AMBIGUOUS:
            return SemanticJoinResult(
                join_key=join_key,
                source_label=label,
                normalized_label=normalized,
                outcome=SemanticJoinOutcome.UNSAFE_JOIN,
                target_ref=None,
                join_safety_level=None,
                rationale="Join is unsafe because semantic resolution is ambiguous.",
                resolution_kind=alias_resolution.kind,
                match_outcome=None,
            )

        target_ref: TaxonomyLocator | None = alias_resolution.resolved_target_ref
        match_outcome: CandidateMatchOutcome | None = None
        if alias_resolution.kind is AliasResolutionKind.UNRESOLVED:
            match = self._candidate_matcher.match_label(
                label,
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
            match_outcome = match.outcome
            if match.outcome is CandidateMatchOutcome.AMBIGUOUS:
                return SemanticJoinResult(
                    join_key=join_key,
                    source_label=label,
                    normalized_label=normalized,
                    outcome=SemanticJoinOutcome.UNSAFE_JOIN,
                    target_ref=None,
                    join_safety_level=None,
                    rationale="Join is unsafe because candidate matching remains ambiguous.",
                    resolution_kind=None,
                    match_outcome=match.outcome,
                )
            if match.outcome is CandidateMatchOutcome.NO_MATCH:
                return SemanticJoinResult(
                    join_key=join_key,
                    source_label=label,
                    normalized_label=normalized,
                    outcome=SemanticJoinOutcome.UNSAFE_JOIN,
                    target_ref=None,
                    join_safety_level=None,
                    rationale="Join is unsafe because no controlled semantic resolution exists for the label.",
                    resolution_kind=None,
                    match_outcome=match.outcome,
                )
            target_ref = match.target_ref

        if target_ref is None:
            return SemanticJoinResult(
                join_key=join_key,
                source_label=label,
                normalized_label=normalized,
                outcome=SemanticJoinOutcome.UNSAFE_JOIN,
                target_ref=None,
                join_safety_level=None,
                rationale="Join is unsafe because no target semantic object could be resolved.",
                resolution_kind=alias_resolution.kind,
                match_outcome=match_outcome,
            )

        join_records = self._catalog.join_records_for_target(
            join_key,
            target_ref,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        join_safety = self._catalog.collapse_join_safety(join_records)
        if join_safety is None:
            return SemanticJoinResult(
                join_key=join_key,
                source_label=label,
                normalized_label=normalized,
                outcome=SemanticJoinOutcome.UNSAFE_JOIN,
                target_ref=None,
                join_safety_level=None,
                rationale="Join is unsafe because no join_key_semantic_record is registered for the resolved target.",
                resolution_kind=alias_resolution.kind,
                match_outcome=match_outcome,
            )

        if join_safety is JoinSafetyLevel.UNSAFE:
            return SemanticJoinResult(
                join_key=join_key,
                source_label=label,
                normalized_label=normalized,
                outcome=SemanticJoinOutcome.UNSAFE_JOIN,
                target_ref=target_ref,
                join_safety_level=join_safety,
                rationale="Join is explicitly marked unsafe in controlled semantic join metadata.",
                resolution_kind=alias_resolution.kind,
                match_outcome=match_outcome,
            )

        if (
            join_safety is JoinSafetyLevel.CONDITIONAL
            or alias_resolution.kind is AliasResolutionKind.RESOLVED_LEGACY
            or match_outcome is CandidateMatchOutcome.CANDIDATE_MATCH
            or not self._catalog.target_is_active(target_ref)
        ):
            return SemanticJoinResult(
                join_key=join_key,
                source_label=label,
                normalized_label=normalized,
                outcome=SemanticJoinOutcome.CONDITIONAL_JOIN,
                target_ref=target_ref,
                join_safety_level=join_safety,
                rationale="Join is controlled but remains conditional because the mapping is not fully stable or uses historical/open semantics.",
                resolution_kind=alias_resolution.kind,
                match_outcome=match_outcome,
            )

        return SemanticJoinResult(
            join_key=join_key,
            source_label=label,
            normalized_label=normalized,
            outcome=SemanticJoinOutcome.SAFE_JOIN,
            target_ref=target_ref,
            join_safety_level=join_safety,
            rationale="Join is safe because the label resolves cleanly and the declared join semantics are safe.",
            resolution_kind=alias_resolution.kind,
            match_outcome=match_outcome,
        )


__all__ = ["BasicSemanticJoinResolver"]
