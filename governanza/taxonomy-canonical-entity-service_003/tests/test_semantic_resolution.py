from __future__ import annotations

from datetime import datetime, timezone

from taxonomy_canonical_entity_service.domain import (
    AliasKind,
    AliasRecord,
    AliasRecordId,
    AliasStatus,
    AmbiguityStatus,
    AuthoritySource,
    CanonicalEntity,
    CanonicalEntityId,
    CanonicalEntityKind,
    CanonicalName,
    CanonicalTerm,
    CanonicalTermId,
    CandidateMatchRecord,
    CandidateMatchRecordId,
    ConfidenceScore,
    EntityMembershipRecord,
    EntityMembershipRecordId,
    EntityStatus,
    EquivalenceRecord,
    EquivalenceRecordId,
    EquivalenceStatus,
    JoinKeyName,
    JoinKeySemanticRecord,
    JoinKeySemanticRecordId,
    JoinSafetyLevel,
    Label,
    LegacyTermRecord,
    LegacyTermRecordId,
    MatchRationale,
    MatchStatus,
    MembershipStatus,
    NodeStatus,
    PhaseApplicability,
    SemanticScope,
    TaxonomyDomain,
    TaxonomyNode,
    TaxonomyNodeId,
    TaxonomyNodeType,
    TaxonomyVersion,
    TaxonomyVersionId,
    TaxonomyVersionStatus,
    TaxonomyRegistryId,
    TermLifecycleStatus,
    VersionFingerprint,
    VersionLabel,
)
from taxonomy_canonical_entity_service.resolution import (
    AliasResolutionKind,
    BasicAliasResolver,
    BasicCandidateMatcher,
    BasicSemanticJoinResolver,
    CandidateMatchOutcome,
    ResolutionCatalog,
    SemanticJoinOutcome,
)


UTC = timezone.utc
AUTHORITY = AuthoritySource("master_spec")
SYSTEM_SCOPE = SemanticScope(
    scope_key="global.system_family",
    taxonomy_domain=TaxonomyDomain.SYSTEM_FAMILY,
    phase_applicability=PhaseApplicability(()),
)
BENCHMARK_SCOPE = SemanticScope(
    scope_key="global.benchmark_family",
    taxonomy_domain=TaxonomyDomain.BENCHMARK_FAMILY,
    phase_applicability=PhaseApplicability(()),
)


def _dt(day: int) -> datetime:
    return datetime(2026, 4, day, 11, 0, tzinfo=UTC)


def _version(version_id: str, *, domain: TaxonomyDomain) -> TaxonomyVersion:
    return TaxonomyVersion(
        taxonomy_version_id=TaxonomyVersionId(version_id),
        taxonomy_registry_id=TaxonomyRegistryId(f"registry:{domain.value}"),
        version_label=VersionLabel(version_id.rsplit(":", 1)[-1]),
        version_status=TaxonomyVersionStatus.ACTIVE,
        source_of_authority=AUTHORITY,
        version_fingerprint=VersionFingerprint(f"fingerprint:{version_id}"),
        created_at=_dt(1),
        effective_from=_dt(1),
        supersedes_taxonomy_version_id=None,
    )


def _node(
    node_id: str,
    term_id: str,
    *,
    version_id: str,
    scope: SemanticScope,
) -> TaxonomyNode:
    return TaxonomyNode(
        taxonomy_node_id=TaxonomyNodeId(node_id),
        taxonomy_version_id=TaxonomyVersionId(version_id),
        canonical_term_id=CanonicalTermId(term_id),
        node_type=TaxonomyNodeType.LEAF,
        node_status=NodeStatus.ACTIVE,
        semantic_scope=scope,
        parent_taxonomy_node_id=None,
        created_at=_dt(2),
    )


def _term(term_id: str, node_id: str, label: str) -> CanonicalTerm:
    return CanonicalTerm(
        canonical_term_id=CanonicalTermId(term_id),
        taxonomy_node_id=TaxonomyNodeId(node_id),
        label=Label(label),
        lifecycle_status=TermLifecycleStatus.ACTIVE,
        source_of_authority=AUTHORITY,
        created_at=_dt(3),
    )


def _alias(alias_id: str, label: str, target, *, scope: SemanticScope = SYSTEM_SCOPE) -> AliasRecord:
    return AliasRecord(
        alias_record_id=AliasRecordId(alias_id),
        label=Label(label),
        target_ref=target.reference,
        alias_kind=AliasKind.ALIAS,
        alias_status=AliasStatus.CONFIRMED,
        semantic_scope=scope,
        rationale="Controlled alias mapping.",
        created_at=_dt(4),
    )


def _legacy(legacy_id: str, label: str, target: CanonicalTerm, *, scope: SemanticScope = SYSTEM_SCOPE) -> LegacyTermRecord:
    return LegacyTermRecord(
        legacy_term_record_id=LegacyTermRecordId(legacy_id),
        label=Label(label),
        canonical_term_id=target.canonical_term_id,
        lifecycle_status=TermLifecycleStatus.LEGACY_ONLY,
        semantic_scope=scope,
        rationale="Historical label retained.",
        created_at=_dt(5),
    )


def _candidate_record(
    record_id: str,
    source_label: str,
    target: CanonicalTerm,
    *,
    status: MatchStatus = MatchStatus.CANDIDATE,
    ambiguity: AmbiguityStatus = AmbiguityStatus.CLEAR,
    confidence: float = 0.72,
    scope: SemanticScope = SYSTEM_SCOPE,
) -> CandidateMatchRecord:
    return CandidateMatchRecord(
        candidate_match_record_id=CandidateMatchRecordId(record_id),
        source_label=source_label,
        candidate_ref=target.reference,
        match_status=status,
        ambiguity_status=ambiguity,
        semantic_scope=scope,
        confidence=ConfidenceScore(confidence),
        rationale=MatchRationale("Explicit candidate match curated by semantic governance."),
        created_at=_dt(6),
    )


def _equivalence(
    record_id: str,
    left: CanonicalTerm,
    right: CanonicalTerm,
    *,
    status: EquivalenceStatus,
    ambiguity: AmbiguityStatus = AmbiguityStatus.CLEAR,
    scope: SemanticScope = SYSTEM_SCOPE,
) -> EquivalenceRecord:
    return EquivalenceRecord(
        equivalence_record_id=EquivalenceRecordId(record_id),
        left_ref=left.reference,
        right_ref=right.reference,
        equivalence_status=status,
        ambiguity_status=ambiguity,
        rationale=MatchRationale("Explicit semantic relation."),
        semantic_scope=scope,
        created_at=_dt(7),
    )


def _join(join_id: str, join_key: str, target, *, safety: JoinSafetyLevel, scope: SemanticScope = SYSTEM_SCOPE) -> JoinKeySemanticRecord:
    return JoinKeySemanticRecord(
        join_key_semantic_record_id=JoinKeySemanticRecordId(join_id),
        join_key=JoinKeyName(join_key),
        target_ref=target.reference,
        semantic_scope=scope,
        join_safety_level=safety,
        rationale=MatchRationale("Controlled semantic join key."),
        created_at=_dt(8),
    )


def _entity(entity_id: str, name: str) -> CanonicalEntity:
    return CanonicalEntity(
        canonical_entity_id=CanonicalEntityId(entity_id),
        entity_kind=CanonicalEntityKind.SYSTEM,
        canonical_name=CanonicalName(name),
        entity_status=EntityStatus.ACTIVE,
        source_of_authority=AUTHORITY,
        created_at=_dt(9),
    )


def _membership(record_id: str, entity: CanonicalEntity, node: TaxonomyNode) -> EntityMembershipRecord:
    return EntityMembershipRecord(
        entity_membership_record_id=EntityMembershipRecordId(record_id),
        canonical_entity_id=entity.canonical_entity_id,
        taxonomy_node_id=node.taxonomy_node_id,
        membership_status=MembershipStatus.ACTIVE,
        semantic_scope=node.semantic_scope,
        rationale="Controlled entity classification.",
        created_at=_dt(10),
    )


def _catalog():
    version_system = _version("version:system_family:v1", domain=TaxonomyDomain.SYSTEM_FAMILY)
    version_benchmark = _version("version:benchmark_family:v1", domain=TaxonomyDomain.BENCHMARK_FAMILY)

    node_chiller = _node("node:chiller", "term:chiller", version_id=version_system.taxonomy_version_id.value, scope=SYSTEM_SCOPE)
    node_cooling = _node("node:cooling", "term:cooling", version_id=version_system.taxonomy_version_id.value, scope=SYSTEM_SCOPE)
    node_benchmark_plant = _node("node:benchmark-plant", "term:benchmark-plant", version_id=version_benchmark.taxonomy_version_id.value, scope=BENCHMARK_SCOPE)

    term_chiller = _term("term:chiller", "node:chiller", "Chiller Plant")
    term_cooling = _term("term:cooling", "node:cooling", "Cooling Plant")
    term_benchmark_plant = _term("term:benchmark-plant", "node:benchmark-plant", "Plant")
    term_system_plant = _term("term:system-plant", "node:chiller", "Plant")

    alias_chw = _alias("alias:chw", "CHW system", term_chiller)
    alias_ambiguous = _alias("alias:plant-a", "plant center", term_chiller)
    alias_ambiguous_2 = _alias("alias:plant-b", "plant center", term_cooling)
    legacy_central_chw = _legacy("legacy:central-chw", "Central Chilled Water", term_chiller)
    candidate = _candidate_record("candidate:cool-plant", "cooling line", term_cooling)
    contextual_equivalence = _equivalence(
        "equivalence:contextual",
        term_chiller,
        term_cooling,
        status=EquivalenceStatus.CONTEXTUAL,
    )
    join_safe = _join("join:safe", "system_family", term_chiller, safety=JoinSafetyLevel.SAFE)
    join_conditional = _join("join:conditional", "legacy_system_family", term_chiller, safety=JoinSafetyLevel.SAFE)
    join_unsafe = _join("join:unsafe", "unsafe_system_family", term_cooling, safety=JoinSafetyLevel.UNSAFE)

    entity = _entity("entity:utility-plant", "North Utility Plant")
    entity_alias = _alias("alias:entity-plant", "north utility plant", entity)
    join_entity = _join("join:entity", "system_entity", entity, safety=JoinSafetyLevel.SAFE)
    membership_1 = _membership("membership:entity-1", entity, node_chiller)
    membership_2 = _membership("membership:entity-2", entity, node_cooling)

    return ResolutionCatalog.from_iterables(
        taxonomy_versions=(version_system, version_benchmark),
        taxonomy_nodes=(node_chiller, node_cooling, node_benchmark_plant),
        canonical_terms=(term_chiller, term_cooling, term_benchmark_plant, term_system_plant),
        alias_records=(alias_chw, alias_ambiguous, alias_ambiguous_2, entity_alias),
        legacy_term_records=(legacy_central_chw,),
        canonical_entities=(entity,),
        entity_membership_records=(membership_1, membership_2),
        equivalence_records=(contextual_equivalence,),
        candidate_match_records=(candidate,),
        join_key_semantic_records=(join_safe, join_conditional, join_unsafe, join_entity),
    )


def test_resolves_exact_canonical_term() -> None:
    resolver = BasicAliasResolver(_catalog())

    result = resolver.resolve_label("Chiller Plant", semantic_scope=SYSTEM_SCOPE)

    assert result.kind is AliasResolutionKind.RESOLVED_CANONICAL
    assert result.resolved_target_ref is not None
    assert result.resolved_target_ref.identifier.value == "term:chiller"


def test_resolves_confirmed_alias() -> None:
    resolver = BasicAliasResolver(_catalog())

    result = resolver.resolve_label("CHW system", semantic_scope=SYSTEM_SCOPE)

    assert result.kind is AliasResolutionKind.RESOLVED_ALIAS
    assert result.resolved_target_ref is not None
    assert result.resolved_target_ref.identifier.value == "term:chiller"


def test_resolves_legacy_term_without_overwriting_history() -> None:
    resolver = BasicAliasResolver(_catalog())

    result = resolver.resolve_label("Central Chilled Water", semantic_scope=SYSTEM_SCOPE)

    assert result.kind is AliasResolutionKind.RESOLVED_LEGACY
    assert result.resolved_target_ref is not None
    assert result.resolved_target_ref.identifier.value == "term:chiller"
    assert result.supporting_ref is not None
    assert result.supporting_ref.identifier.value == "legacy:central-chw"


def test_preserves_ambiguous_alias_without_auto_resolution() -> None:
    resolver = BasicAliasResolver(_catalog())

    result = resolver.resolve_label("plant center", semantic_scope=SYSTEM_SCOPE)

    assert result.kind is AliasResolutionKind.AMBIGUOUS
    assert len(result.candidate_target_refs) == 2


def test_unknown_term_stays_unresolved() -> None:
    resolver = BasicAliasResolver(_catalog())

    result = resolver.resolve_label("unknown hydronic thing", semantic_scope=SYSTEM_SCOPE)

    assert result.kind is AliasResolutionKind.UNRESOLVED
    assert result.resolved_target_ref is None


def test_candidate_match_open_record_returns_candidate_with_rationale_and_confidence() -> None:
    matcher = BasicCandidateMatcher(_catalog())

    result = matcher.match_label("cooling line", semantic_scope=SYSTEM_SCOPE)

    assert result.outcome is CandidateMatchOutcome.CANDIDATE_MATCH
    assert result.target_ref is not None
    assert result.target_ref.identifier.value == "term:cooling"
    assert result.confidence is not None
    assert result.confidence.value == 0.72
    assert "candidate match record" in result.rationale.lower()


def test_contextual_equivalence_does_not_confirm_related_but_not_equivalent_term() -> None:
    catalog = _catalog()
    matcher = BasicCandidateMatcher(catalog)
    source_ref = next(item.reference for item in catalog.canonical_terms if item.canonical_term_id.value == "term:chiller")

    result = matcher.match_ref(source_ref, semantic_scope=SYSTEM_SCOPE)

    assert result.outcome is CandidateMatchOutcome.CANDIDATE_MATCH
    assert result.target_ref is not None
    assert result.target_ref.identifier.value == "term:cooling"


def test_safe_join_is_allowed_for_clean_resolution() -> None:
    resolver = BasicSemanticJoinResolver(_catalog())

    result = resolver.resolve_join(
        join_key=JoinKeyName("system_family"),
        label="CHW system",
        semantic_scope=SYSTEM_SCOPE,
    )

    assert result.outcome is SemanticJoinOutcome.SAFE_JOIN
    assert result.target_ref is not None
    assert result.target_ref.identifier.value == "term:chiller"


def test_conditional_join_is_returned_for_legacy_resolution() -> None:
    resolver = BasicSemanticJoinResolver(_catalog())

    result = resolver.resolve_join(
        join_key=JoinKeyName("legacy_system_family"),
        label="Central Chilled Water",
        semantic_scope=SYSTEM_SCOPE,
    )

    assert result.outcome is SemanticJoinOutcome.CONDITIONAL_JOIN
    assert result.target_ref is not None
    assert result.target_ref.identifier.value == "term:chiller"


def test_unsafe_join_is_blocked() -> None:
    resolver = BasicSemanticJoinResolver(_catalog())

    result = resolver.resolve_join(
        join_key=JoinKeyName("unsafe_system_family"),
        label="cooling line",
        semantic_scope=SYSTEM_SCOPE,
    )

    assert result.outcome is SemanticJoinOutcome.UNSAFE_JOIN


def test_same_word_in_different_domains_requires_domain_filter() -> None:
    resolver = BasicAliasResolver(_catalog())

    ambiguous = resolver.resolve_label("Plant")
    system = resolver.resolve_label("Plant", taxonomy_domain=TaxonomyDomain.SYSTEM_FAMILY)
    benchmark = resolver.resolve_label("Plant", taxonomy_domain=TaxonomyDomain.BENCHMARK_FAMILY)

    assert ambiguous.kind is AliasResolutionKind.AMBIGUOUS
    assert system.kind is AliasResolutionKind.RESOLVED_CANONICAL
    assert system.resolved_target_ref is not None
    assert system.resolved_target_ref.identifier.value == "term:system-plant"
    assert benchmark.kind is AliasResolutionKind.RESOLVED_CANONICAL
    assert benchmark.resolved_target_ref is not None
    assert benchmark.resolved_target_ref.identifier.value == "term:benchmark-plant"


def test_entity_with_multiple_memberships_keeps_identity_stable() -> None:
    catalog = _catalog()
    resolver = BasicSemanticJoinResolver(catalog)
    entity = next(item for item in catalog.canonical_entities if item.canonical_entity_id.value == "entity:utility-plant")

    result = resolver.resolve_join(
        join_key=JoinKeyName("system_entity"),
        label="north utility plant",
        semantic_scope=SYSTEM_SCOPE,
    )
    memberships = catalog.memberships_for_entity(entity.canonical_entity_id)

    assert result.outcome is SemanticJoinOutcome.SAFE_JOIN
    assert result.target_ref == entity.reference
    assert len(memberships) == 2
    assert memberships[0].canonical_entity_id == memberships[1].canonical_entity_id == entity.canonical_entity_id
