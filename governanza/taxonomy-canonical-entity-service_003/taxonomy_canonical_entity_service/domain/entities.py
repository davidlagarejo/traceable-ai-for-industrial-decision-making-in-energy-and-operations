from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    AliasKind,
    AliasStatus,
    CanonicalEntityKind,
    EntityStatus,
    MembershipStatus,
    NodeStatus,
    TaxonomyDomain,
    TaxonomyNodeType,
    TaxonomyRegistryStatus,
    TaxonomyVersionStatus,
    TermLifecycleStatus,
)
from .errors import DomainInvariantError
from .value_objects import (
    AliasRecordId,
    AuthoritySource,
    CanonicalEntityId,
    CanonicalName,
    CanonicalTermId,
    EntityMembershipRecordId,
    Label,
    LegacyTermRecordId,
    PhaseApplicability,
    SemanticScope,
    TaxonomyLocator,
    TaxonomyNodeId,
    TaxonomyRegistryId,
    TaxonomyVersionId,
    VersionFingerprint,
    VersionLabel,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class TaxonomyRegistry:
    taxonomy_registry_id: TaxonomyRegistryId
    taxonomy_domain: TaxonomyDomain
    canonical_name: CanonicalName
    registry_status: TaxonomyRegistryStatus
    phase_applicability: PhaseApplicability
    source_of_authority: AuthoritySource
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_taxonomy_registry(self.taxonomy_registry_id)


@dataclass(frozen=True, slots=True)
class TaxonomyVersion:
    taxonomy_version_id: TaxonomyVersionId
    taxonomy_registry_id: TaxonomyRegistryId
    version_label: VersionLabel
    version_status: TaxonomyVersionStatus
    source_of_authority: AuthoritySource
    version_fingerprint: VersionFingerprint
    created_at: datetime
    effective_from: datetime
    supersedes_taxonomy_version_id: TaxonomyVersionId | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        object.__setattr__(self, "effective_from", _require_timezone(self.effective_from, "effective_from"))
        if self.supersedes_taxonomy_version_id == self.taxonomy_version_id:
            raise DomainInvariantError("supersedes_taxonomy_version_id must not point to self.")

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_taxonomy_version(self.taxonomy_version_id)


@dataclass(frozen=True, slots=True)
class TaxonomyNode:
    taxonomy_node_id: TaxonomyNodeId
    taxonomy_version_id: TaxonomyVersionId
    canonical_term_id: CanonicalTermId
    node_type: TaxonomyNodeType
    node_status: NodeStatus
    semantic_scope: SemanticScope
    parent_taxonomy_node_id: TaxonomyNodeId | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.parent_taxonomy_node_id == self.taxonomy_node_id:
            raise DomainInvariantError("parent_taxonomy_node_id must not point to self.")

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_taxonomy_node(self.taxonomy_node_id)


@dataclass(frozen=True, slots=True)
class CanonicalTerm:
    canonical_term_id: CanonicalTermId
    taxonomy_node_id: TaxonomyNodeId
    label: Label
    lifecycle_status: TermLifecycleStatus
    source_of_authority: AuthoritySource
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_canonical_term(self.canonical_term_id)


@dataclass(frozen=True, slots=True)
class AliasRecord:
    alias_record_id: AliasRecordId
    label: Label
    target_ref: TaxonomyLocator
    alias_kind: AliasKind
    alias_status: AliasStatus
    semantic_scope: SemanticScope
    rationale: str
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "rationale", self.rationale.strip())
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.rationale:
            raise DomainInvariantError("AliasRecord.rationale must be non-empty.")
        if self.target_ref.target_kind not in {
            self.target_ref.target_kind.TAXONOMY_NODE,
            self.target_ref.target_kind.CANONICAL_TERM,
            self.target_ref.target_kind.CANONICAL_ENTITY,
        }:
            raise DomainInvariantError(
                "AliasRecord.target_ref must point to a taxonomy_node, canonical_term or canonical_entity."
            )

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_alias_record(self.alias_record_id)


@dataclass(frozen=True, slots=True)
class LegacyTermRecord:
    legacy_term_record_id: LegacyTermRecordId
    label: Label
    canonical_term_id: CanonicalTermId
    lifecycle_status: TermLifecycleStatus
    semantic_scope: SemanticScope
    rationale: str
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "rationale", self.rationale.strip())
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.rationale:
            raise DomainInvariantError("LegacyTermRecord.rationale must be non-empty.")
        if self.lifecycle_status is TermLifecycleStatus.ACTIVE:
            raise DomainInvariantError("LegacyTermRecord cannot use ACTIVE lifecycle status.")

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_legacy_term_record(self.legacy_term_record_id)


@dataclass(frozen=True, slots=True)
class CanonicalEntity:
    canonical_entity_id: CanonicalEntityId
    entity_kind: CanonicalEntityKind
    canonical_name: CanonicalName
    entity_status: EntityStatus
    source_of_authority: AuthoritySource
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

    @property
    def reference(self) -> TaxonomyLocator:
        return TaxonomyLocator.for_canonical_entity(self.canonical_entity_id)


@dataclass(frozen=True, slots=True)
class EntityMembershipRecord:
    entity_membership_record_id: EntityMembershipRecordId
    canonical_entity_id: CanonicalEntityId
    taxonomy_node_id: TaxonomyNodeId
    membership_status: MembershipStatus
    semantic_scope: SemanticScope
    rationale: str
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "rationale", self.rationale.strip())
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.rationale:
            raise DomainInvariantError("EntityMembershipRecord.rationale must be non-empty.")


__all__ = [
    "AliasRecord",
    "CanonicalEntity",
    "CanonicalTerm",
    "EntityMembershipRecord",
    "LegacyTermRecord",
    "TaxonomyNode",
    "TaxonomyRegistry",
    "TaxonomyVersion",
]

