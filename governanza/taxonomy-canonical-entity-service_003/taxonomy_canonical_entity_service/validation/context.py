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
    TaxonomyRegistry,
    TaxonomyVersion,
)
from ..domain.enums import TaxonomyLocatorKind
from ..domain.records import (
    BoundaryRecord,
    CandidateMatchRecord,
    DeprecationRecord,
    EquivalenceRecord,
    JoinKeySemanticRecord,
    SemanticIntegrityRecord,
    TaxonomyChangeRecord,
)
from ..domain.value_objects import (
    AliasRecordId,
    CanonicalEntityId,
    CanonicalTermId,
    CandidateMatchRecordId,
    LegacyTermRecordId,
    SemanticScope,
    TaxonomyLocator,
    TaxonomyNodeId,
    TaxonomyRegistryId,
    TaxonomyVersionId,
)


@dataclass(frozen=True, slots=True)
class ValidationContext:
    taxonomy_registries: tuple[TaxonomyRegistry, ...] = ()
    taxonomy_versions: tuple[TaxonomyVersion, ...] = ()
    taxonomy_nodes: tuple[TaxonomyNode, ...] = ()
    canonical_terms: tuple[CanonicalTerm, ...] = ()
    alias_records: tuple[AliasRecord, ...] = ()
    legacy_term_records: tuple[LegacyTermRecord, ...] = ()
    canonical_entities: tuple[CanonicalEntity, ...] = ()
    entity_membership_records: tuple[EntityMembershipRecord, ...] = ()
    equivalence_records: tuple[EquivalenceRecord, ...] = ()
    candidate_match_records: tuple[CandidateMatchRecord, ...] = ()
    boundary_records: tuple[BoundaryRecord, ...] = ()
    join_key_semantic_records: tuple[JoinKeySemanticRecord, ...] = ()
    deprecation_records: tuple[DeprecationRecord, ...] = ()
    taxonomy_change_records: tuple[TaxonomyChangeRecord, ...] = ()
    semantic_integrity_records: tuple[SemanticIntegrityRecord, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        taxonomy_registries: Iterable[TaxonomyRegistry] = (),
        taxonomy_versions: Iterable[TaxonomyVersion] = (),
        taxonomy_nodes: Iterable[TaxonomyNode] = (),
        canonical_terms: Iterable[CanonicalTerm] = (),
        alias_records: Iterable[AliasRecord] = (),
        legacy_term_records: Iterable[LegacyTermRecord] = (),
        canonical_entities: Iterable[CanonicalEntity] = (),
        entity_membership_records: Iterable[EntityMembershipRecord] = (),
        equivalence_records: Iterable[EquivalenceRecord] = (),
        candidate_match_records: Iterable[CandidateMatchRecord] = (),
        boundary_records: Iterable[BoundaryRecord] = (),
        join_key_semantic_records: Iterable[JoinKeySemanticRecord] = (),
        deprecation_records: Iterable[DeprecationRecord] = (),
        taxonomy_change_records: Iterable[TaxonomyChangeRecord] = (),
        semantic_integrity_records: Iterable[SemanticIntegrityRecord] = (),
    ) -> "ValidationContext":
        return cls(
            taxonomy_registries=tuple(taxonomy_registries),
            taxonomy_versions=tuple(taxonomy_versions),
            taxonomy_nodes=tuple(taxonomy_nodes),
            canonical_terms=tuple(canonical_terms),
            alias_records=tuple(alias_records),
            legacy_term_records=tuple(legacy_term_records),
            canonical_entities=tuple(canonical_entities),
            entity_membership_records=tuple(entity_membership_records),
            equivalence_records=tuple(equivalence_records),
            candidate_match_records=tuple(candidate_match_records),
            boundary_records=tuple(boundary_records),
            join_key_semantic_records=tuple(join_key_semantic_records),
            deprecation_records=tuple(deprecation_records),
            taxonomy_change_records=tuple(taxonomy_change_records),
            semantic_integrity_records=tuple(semantic_integrity_records),
        )

    @property
    def registries_by_id(self) -> dict[TaxonomyRegistryId, TaxonomyRegistry]:
        return {item.taxonomy_registry_id: item for item in self.taxonomy_registries}

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
    def aliases_by_id(self) -> dict[AliasRecordId, AliasRecord]:
        return {item.alias_record_id: item for item in self.alias_records}

    @property
    def legacy_terms_by_id(self) -> dict[LegacyTermRecordId, LegacyTermRecord]:
        return {item.legacy_term_record_id: item for item in self.legacy_term_records}

    @property
    def entities_by_id(self) -> dict[CanonicalEntityId, CanonicalEntity]:
        return {item.canonical_entity_id: item for item in self.canonical_entities}

    @property
    def candidate_matches_by_id(self) -> dict[CandidateMatchRecordId, CandidateMatchRecord]:
        return {item.candidate_match_record_id: item for item in self.candidate_match_records}

    def registry_for_version(self, taxonomy_version_id: TaxonomyVersionId) -> TaxonomyRegistry | None:
        version = self.versions_by_id.get(taxonomy_version_id)
        if version is None:
            return None
        return self.registries_by_id.get(version.taxonomy_registry_id)

    def version_for_node(self, taxonomy_node_id: TaxonomyNodeId) -> TaxonomyVersion | None:
        node = self.nodes_by_id.get(taxonomy_node_id)
        if node is None:
            return None
        return self.versions_by_id.get(node.taxonomy_version_id)

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

    def taxonomy_version_id_for_locator(self, locator: TaxonomyLocator) -> TaxonomyVersionId | None:
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_VERSION:
            return locator.identifier
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_NODE:
            node = self.nodes_by_id.get(locator.identifier)
            return None if node is None else node.taxonomy_version_id
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_TERM:
            node = self.node_for_term(locator.identifier)
            return None if node is None else node.taxonomy_version_id
        if locator.target_kind is TaxonomyLocatorKind.ALIAS_RECORD:
            alias = self.aliases_by_id.get(locator.identifier)
            return None if alias is None else self.taxonomy_version_id_for_locator(alias.target_ref)
        if locator.target_kind is TaxonomyLocatorKind.LEGACY_TERM_RECORD:
            legacy = self.legacy_terms_by_id.get(locator.identifier)
            if legacy is None:
                return None
            node = self.node_for_term(legacy.canonical_term_id)
            return None if node is None else node.taxonomy_version_id
        return None

    def contains_locator(self, locator: TaxonomyLocator) -> bool:
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_REGISTRY:
            return locator.identifier in self.registries_by_id
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_VERSION:
            return locator.identifier in self.versions_by_id
        if locator.target_kind is TaxonomyLocatorKind.TAXONOMY_NODE:
            return locator.identifier in self.nodes_by_id
        if locator.target_kind is TaxonomyLocatorKind.CANONICAL_TERM:
            return locator.identifier in self.terms_by_id
        if locator.target_kind is TaxonomyLocatorKind.ALIAS_RECORD:
            return locator.identifier in self.aliases_by_id
        if locator.target_kind is TaxonomyLocatorKind.LEGACY_TERM_RECORD:
            return locator.identifier in self.legacy_terms_by_id
        return locator.identifier in self.entities_by_id

    def canonical_terms_in_version(self, taxonomy_version_id: TaxonomyVersionId) -> tuple[CanonicalTerm, ...]:
        return tuple(
            item
            for item in self.canonical_terms
            if self.taxonomy_version_id_for_locator(item.reference) == taxonomy_version_id
        )

    def aliases_for_label_scope(self, *, normalized_label: str, semantic_scope: SemanticScope) -> tuple[AliasRecord, ...]:
        return tuple(
            item
            for item in self.alias_records
            if item.label.normalized == normalized_label and item.semantic_scope == semantic_scope
        )

    def unresolved_candidate_matches_for_taxonomy_version(
        self,
        taxonomy_version_id: TaxonomyVersionId,
    ) -> tuple[CandidateMatchRecord, ...]:
        return tuple(
            item
            for item in self.candidate_match_records
            if item.match_status.value in {"candidate", "ambiguous"}
            and self.taxonomy_version_id_for_locator(item.candidate_ref) == taxonomy_version_id
        )

