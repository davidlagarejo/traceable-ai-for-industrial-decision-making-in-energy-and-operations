from __future__ import annotations

from collections.abc import Iterable

from .._compat import dataclass
from ..domain.entities import (
    AliasRecord,
    CanonicalEntity,
    CanonicalTerm,
    EntityMembershipRecord,
    LegacyTermRecord,
    TaxonomyNode,
    TaxonomyVersion,
)
from ..domain.enums import AliasStatus, EntityStatus, JoinSafetyLevel, NodeStatus, TaxonomyDomain, TaxonomyLocatorKind, TermLifecycleStatus
from ..domain.records import CandidateMatchRecord, EquivalenceRecord, JoinKeySemanticRecord
from ..domain.value_objects import (
    CanonicalEntityId,
    CanonicalTermId,
    JoinKeyName,
    SemanticScope,
    TaxonomyLocator,
    TaxonomyNodeId,
    TaxonomyVersionId,
)


def normalize_label(label: str) -> str:
    return " ".join(label.casefold().split())


def normalize_key(value: str) -> str:
    return " ".join(value.casefold().split())


@dataclass(frozen=True, slots=True)
class ResolutionCatalog:
    taxonomy_versions: tuple[TaxonomyVersion, ...] = ()
    taxonomy_nodes: tuple[TaxonomyNode, ...] = ()
    canonical_terms: tuple[CanonicalTerm, ...] = ()
    alias_records: tuple[AliasRecord, ...] = ()
    legacy_term_records: tuple[LegacyTermRecord, ...] = ()
    canonical_entities: tuple[CanonicalEntity, ...] = ()
    entity_membership_records: tuple[EntityMembershipRecord, ...] = ()
    equivalence_records: tuple[EquivalenceRecord, ...] = ()
    candidate_match_records: tuple[CandidateMatchRecord, ...] = ()
    join_key_semantic_records: tuple[JoinKeySemanticRecord, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        taxonomy_versions: Iterable[TaxonomyVersion] = (),
        taxonomy_nodes: Iterable[TaxonomyNode] = (),
        canonical_terms: Iterable[CanonicalTerm] = (),
        alias_records: Iterable[AliasRecord] = (),
        legacy_term_records: Iterable[LegacyTermRecord] = (),
        canonical_entities: Iterable[CanonicalEntity] = (),
        entity_membership_records: Iterable[EntityMembershipRecord] = (),
        equivalence_records: Iterable[EquivalenceRecord] = (),
        candidate_match_records: Iterable[CandidateMatchRecord] = (),
        join_key_semantic_records: Iterable[JoinKeySemanticRecord] = (),
    ) -> "ResolutionCatalog":
        return cls(
            taxonomy_versions=tuple(taxonomy_versions),
            taxonomy_nodes=tuple(taxonomy_nodes),
            canonical_terms=tuple(canonical_terms),
            alias_records=tuple(alias_records),
            legacy_term_records=tuple(legacy_term_records),
            canonical_entities=tuple(canonical_entities),
            entity_membership_records=tuple(entity_membership_records),
            equivalence_records=tuple(equivalence_records),
            candidate_match_records=tuple(candidate_match_records),
            join_key_semantic_records=tuple(join_key_semantic_records),
        )

    @property
    def versions_by_id(self) -> dict[TaxonomyVersionId, TaxonomyVersion]:
        return {item.taxonomy_version_id: item for item in self.taxonomy_versions}

    @property
    def nodes_by_id(self) -> dict[TaxonomyNodeId, TaxonomyNode]:
        return {item.taxonomy_node_id: item for item in self.taxonomy_nodes}

    @property
    def terms_by_id(self) -> dict[CanonicalTermId, CanonicalTerm]:
        return {item.canonical_term_id: item for item in self.canonical_terms}

    @property
    def entities_by_id(self) -> dict[CanonicalEntityId, CanonicalEntity]:
        return {item.canonical_entity_id: item for item in self.canonical_entities}

    def contains_locator(self, locator: TaxonomyLocator) -> bool:
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_VERSION:
            return locator.identifier in self.versions_by_id
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_NODE:
            return locator.identifier in self.nodes_by_id
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_TERM:
            return locator.identifier in self.terms_by_id
        if locator.target_kind is TaxonomyLocatorKind.ALIAS_RECORD:
            return any(item.alias_record_id == locator.identifier for item in self.alias_records)
        if locator.target_kind is TaxonomyLocatorKind.LEGACY_TERM_RECORD:
            return any(item.legacy_term_record_id == locator.identifier for item in self.legacy_term_records)
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_ENTITY:
            return locator.identifier in self.entities_by_id
        return False

    def node_for_term(self, canonical_term_id: CanonicalTermId) -> TaxonomyNode | None:
        term = self.terms_by_id.get(canonical_term_id)
        if term is None:
            return None
        return self.nodes_by_id.get(term.taxonomy_node_id)

    def term_for_node(self, taxonomy_node_id: TaxonomyNodeId) -> CanonicalTerm | None:
        for item in self.canonical_terms:
            if item.taxonomy_node_id == taxonomy_node_id:
                return item
        return None

    def scope_for_locator(self, locator: TaxonomyLocator) -> SemanticScope | None:
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_NODE:
            node = self.nodes_by_id.get(locator.identifier)
            return None if node is None else node.semantic_scope
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_TERM:
            node = self.node_for_term(locator.identifier)
            return None if node is None else node.semantic_scope
        if locator.target_kind is TaxonomyLocatorKind.ALIAS_RECORD:
            for item in self.alias_records:
                if item.alias_record_id == locator.identifier:
                    return item.semantic_scope
            return None
        if locator.target_kind is TaxonomyLocatorKind.LEGACY_TERM_RECORD:
            for item in self.legacy_term_records:
                if item.legacy_term_record_id == locator.identifier:
                    return item.semantic_scope
            return None
        return None

    def canonical_term_ref_for_target(self, locator: TaxonomyLocator) -> TaxonomyLocator | None:
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_TERM:
            return locator
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_NODE:
            term = self.term_for_node(locator.identifier)
            return None if term is None else term.reference
        return None

    def target_is_active(self, locator: TaxonomyLocator) -> bool:
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_TERM:
            term = self.terms_by_id.get(locator.identifier)
            return term is not None and term.lifecycle_status is TermLifecycleStatus.ACTIVE
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_NODE:
            node = self.nodes_by_id.get(locator.identifier)
            return node is not None and node.node_status is NodeStatus.ACTIVE
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_ENTITY:
            entity = self.entities_by_id.get(locator.identifier)
            return entity is not None and entity.entity_status is EntityStatus.ACTIVE
        return False

    def memberships_for_entity(
        self,
        canonical_entity_id: CanonicalEntityId,
    ) -> tuple[EntityMembershipRecord, ...]:
        return tuple(
            item
            for item in self.entity_membership_records
            if item.canonical_entity_id == canonical_entity_id
        )

    def canonical_term_matches(
        self,
        label: str,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> tuple[CanonicalTerm, ...]:
        normalized = normalize_label(label)
        return tuple(
            item
            for item in self.canonical_terms
            if item.label.normalized == normalized
            and self._scope_matches(
                self.scope_for_locator(item.reference),
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
        )

    def confirmed_alias_matches(
        self,
        label: str,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> tuple[AliasRecord, ...]:
        normalized = normalize_label(label)
        return tuple(
            item
            for item in self.alias_records
            if item.alias_status is AliasStatus.CONFIRMED
            and item.label.normalized == normalized
            and self._scope_matches(
                item.semantic_scope,
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
        )

    def legacy_term_matches(
        self,
        label: str,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> tuple[LegacyTermRecord, ...]:
        normalized = normalize_label(label)
        return tuple(
            item
            for item in self.legacy_term_records
            if item.label.normalized == normalized
            and self._scope_matches(
                item.semantic_scope,
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
        )

    def candidate_matches_for_label(
        self,
        label: str,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> tuple[CandidateMatchRecord, ...]:
        normalized = normalize_label(label)
        return tuple(
            item
            for item in self.candidate_match_records
            if normalize_label(item.source_label) == normalized
            and self._scope_matches(
                item.semantic_scope,
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
        )

    def equivalence_records_for_ref(
        self,
        source_ref: TaxonomyLocator,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> tuple[EquivalenceRecord, ...]:
        return tuple(
            item
            for item in self.equivalence_records
            if (item.left_ref == source_ref or item.right_ref == source_ref)
            and self._scope_matches(
                item.semantic_scope,
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
        )

    def join_records_for_target(
        self,
        join_key: JoinKeyName,
        target_ref: TaxonomyLocator,
        *,
        semantic_scope: SemanticScope | None = None,
        taxonomy_domain: TaxonomyDomain | None = None,
    ) -> tuple[JoinKeySemanticRecord, ...]:
        normalized_key = normalize_key(join_key.value)
        return tuple(
            item
            for item in self.join_key_semantic_records
            if normalize_key(item.join_key.value) == normalized_key
            and item.target_ref == target_ref
            and self._scope_matches(
                item.semantic_scope,
                semantic_scope=semantic_scope,
                taxonomy_domain=taxonomy_domain,
            )
        )

    @staticmethod
    def collapse_join_safety(records: tuple[JoinKeySemanticRecord, ...]) -> JoinSafetyLevel | None:
        if not records:
            return None
        levels = {item.join_safety_level for item in records}
        if JoinSafetyLevel.UNSAFE in levels:
            return JoinSafetyLevel.UNSAFE
        if JoinSafetyLevel.CONDITIONAL in levels:
            return JoinSafetyLevel.CONDITIONAL
        return JoinSafetyLevel.SAFE

    @staticmethod
    def _scope_matches(
        record_scope: SemanticScope | None,
        *,
        semantic_scope: SemanticScope | None,
        taxonomy_domain: TaxonomyDomain | None,
    ) -> bool:
        if semantic_scope is not None:
            return record_scope == semantic_scope
        if taxonomy_domain is not None:
            return record_scope is not None and record_scope.taxonomy_domain == taxonomy_domain
        return True


__all__ = [
    "ResolutionCatalog",
    "normalize_key",
    "normalize_label",
]
