from __future__ import annotations

from .context import ResolutionCatalog, normalize_label
from .results import AliasResolutionKind, AliasResolutionResult
from ..domain.value_objects import SemanticScope, TaxonomyLocator
from ..domain.enums import TaxonomyDomain


def _unique_locators(values: list[TaxonomyLocator]) -> tuple[TaxonomyLocator, ...]:
    ordered: list[TaxonomyLocator] = []
    seen: set[TaxonomyLocator] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)


class BasicAliasResolver:
    def __init__(self, catalog: ResolutionCatalog) -> None:
        self._catalog = catalog

    def resolve_label(
        self,
        label: str,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> AliasResolutionResult:
        normalized = normalize_label(label)
        canonical_terms = self._catalog.canonical_term_matches(
            label,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        aliases = self._catalog.confirmed_alias_matches(
            label,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )
        legacy_terms = self._catalog.legacy_term_matches(
            label,
            semantic_scope=semantic_scope,
            taxonomy_domain=taxonomy_domain,
        )

        target_refs = _unique_locators(
            [item.reference for item in canonical_terms]
            + [item.target_ref for item in aliases]
            + [
                self._catalog.terms_by_id[item.canonical_term_id].reference
                for item in legacy_terms
                if item.canonical_term_id in self._catalog.terms_by_id
            ]
        )

        if not target_refs:
            return AliasResolutionResult(
                source_label=label,
                normalized_label=normalized,
                kind=AliasResolutionKind.UNRESOLVED,
                resolved_target_ref=None,
                supporting_ref=None,
                candidate_target_refs=(),
                rationale="No canonical term, confirmed alias or legacy term matched the requested label.",
            )

        if len(target_refs) > 1:
            return AliasResolutionResult(
                source_label=label,
                normalized_label=normalized,
                kind=AliasResolutionKind.AMBIGUOUS,
                resolved_target_ref=None,
                supporting_ref=None,
                candidate_target_refs=target_refs,
                rationale="The requested label maps to multiple semantic targets and ambiguity must be preserved.",
            )

        resolved_target = target_refs[0]
        canonical_hit = next((item for item in canonical_terms if item.reference == resolved_target), None)
        if canonical_hit is not None:
            return AliasResolutionResult(
                source_label=label,
                normalized_label=normalized,
                kind=AliasResolutionKind.RESOLVED_CANONICAL,
                resolved_target_ref=resolved_target,
                supporting_ref=canonical_hit.reference,
                candidate_target_refs=(),
                rationale="The requested label matches a canonical term exactly within the requested semantic context.",
            )

        alias_hit = next((item for item in aliases if item.target_ref == resolved_target), None)
        if alias_hit is not None:
            return AliasResolutionResult(
                source_label=label,
                normalized_label=normalized,
                kind=AliasResolutionKind.RESOLVED_ALIAS,
                resolved_target_ref=resolved_target,
                supporting_ref=alias_hit.reference,
                candidate_target_refs=(),
                rationale="The requested label resolves through a confirmed alias mapped to a controlled semantic target.",
            )

        legacy_hit = next(
            (
                item
                for item in legacy_terms
                if item.canonical_term_id in self._catalog.terms_by_id
                and self._catalog.terms_by_id[item.canonical_term_id].reference == resolved_target
            ),
            None,
        )
        return AliasResolutionResult(
            source_label=label,
            normalized_label=normalized,
            kind=AliasResolutionKind.RESOLVED_LEGACY,
            resolved_target_ref=resolved_target,
            supporting_ref=None if legacy_hit is None else legacy_hit.reference,
            candidate_target_refs=(),
            rationale="The requested label resolves through a legacy term and preserves historical semantics explicitly.",
        )


__all__ = ["BasicAliasResolver"]
