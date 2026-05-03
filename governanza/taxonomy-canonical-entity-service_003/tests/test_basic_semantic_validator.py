from __future__ import annotations

from datetime import datetime, timezone

from taxonomy_canonical_entity_service.domain import (
    AliasKind,
    AliasRecord,
    AliasRecordId,
    AliasStatus,
    AmbiguityStatus,
    AuthoritySource,
    BoundaryRecord,
    BoundaryRecordId,
    BoundaryStatus,
    CanonicalEntity,
    CanonicalEntityId,
    CanonicalEntityKind,
    CanonicalName,
    CanonicalTerm,
    CanonicalTermId,
    CandidateMatchRecord,
    CandidateMatchRecordId,
    ComparabilityStatus,
    ConfidenceScore,
    ConflictSeverity,
    DeprecationRecord,
    DeprecationRecordId,
    DeprecationStatus,
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
    SemanticIntegrityRecord,
    SemanticIntegrityRecordId,
    SemanticIntegrityStatus,
    SemanticScope,
    SemanticText,
    TaxonomyChangeKind,
    TaxonomyChangeRecord,
    TaxonomyChangeRecordId,
    TaxonomyDomain,
    TaxonomyNode,
    TaxonomyNodeId,
    TaxonomyNodeType,
    TaxonomyRegistry,
    TaxonomyRegistryId,
    TaxonomyRegistryStatus,
    TaxonomyVersion,
    TaxonomyVersionId,
    TaxonomyVersionStatus,
    TermLifecycleStatus,
    VersionFingerprint,
    VersionLabel,
)
from taxonomy_canonical_entity_service.validation import (
    BasicSemanticIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc
AUTHORITY = AuthoritySource("master_spec")
GLOBAL_SCOPE = SemanticScope(
    scope_key="global.system_family",
    taxonomy_domain=TaxonomyDomain.SYSTEM_FAMILY,
    phase_applicability=PhaseApplicability(()),
)


def _dt(day: int) -> datetime:
    return datetime(2026, 4, day, 12, 0, tzinfo=UTC)


def _registry(
    registry_id: str = "registry:system_family",
    *,
    status: TaxonomyRegistryStatus = TaxonomyRegistryStatus.ACTIVE,
) -> TaxonomyRegistry:
    return TaxonomyRegistry(
        taxonomy_registry_id=TaxonomyRegistryId(registry_id),
        taxonomy_domain=TaxonomyDomain.SYSTEM_FAMILY,
        canonical_name=CanonicalName("System Family"),
        registry_status=status,
        phase_applicability=PhaseApplicability(()),
        source_of_authority=AUTHORITY,
        created_at=_dt(1),
    )


def _version(
    version_id: str = "version:system_family:v1",
    *,
    registry_id: str = "registry:system_family",
    status: TaxonomyVersionStatus = TaxonomyVersionStatus.ACTIVE,
    supersedes: str | None = None,
) -> TaxonomyVersion:
    return TaxonomyVersion(
        taxonomy_version_id=TaxonomyVersionId(version_id),
        taxonomy_registry_id=TaxonomyRegistryId(registry_id),
        version_label=VersionLabel(version_id.rsplit(":", 1)[-1]),
        version_status=status,
        source_of_authority=AUTHORITY,
        version_fingerprint=VersionFingerprint(f"fingerprint:{version_id}"),
        created_at=_dt(2),
        effective_from=_dt(2),
        supersedes_taxonomy_version_id=(
            None if supersedes is None else TaxonomyVersionId(supersedes)
        ),
    )


def _node(
    node_id: str,
    term_id: str,
    *,
    version_id: str = "version:system_family:v1",
    node_type: TaxonomyNodeType = TaxonomyNodeType.LEAF,
    status: NodeStatus = NodeStatus.ACTIVE,
    parent_id: str | None = None,
) -> TaxonomyNode:
    return TaxonomyNode(
        taxonomy_node_id=TaxonomyNodeId(node_id),
        taxonomy_version_id=TaxonomyVersionId(version_id),
        canonical_term_id=CanonicalTermId(term_id),
        node_type=node_type,
        node_status=status,
        semantic_scope=GLOBAL_SCOPE,
        parent_taxonomy_node_id=None if parent_id is None else TaxonomyNodeId(parent_id),
        created_at=_dt(3),
    )


def _term(
    term_id: str,
    node_id: str,
    label: str,
    *,
    lifecycle_status: TermLifecycleStatus = TermLifecycleStatus.ACTIVE,
) -> CanonicalTerm:
    return CanonicalTerm(
        canonical_term_id=CanonicalTermId(term_id),
        taxonomy_node_id=TaxonomyNodeId(node_id),
        label=Label(label),
        lifecycle_status=lifecycle_status,
        source_of_authority=AUTHORITY,
        created_at=_dt(4),
    )


def _alias(
    alias_id: str,
    label: str,
    target,
    *,
    status: AliasStatus = AliasStatus.CONFIRMED,
) -> AliasRecord:
    return AliasRecord(
        alias_record_id=AliasRecordId(alias_id),
        label=Label(label),
        target_ref=target.reference,
        alias_kind=AliasKind.ALIAS,
        alias_status=status,
        semantic_scope=GLOBAL_SCOPE,
        rationale="Alias curated from upstream terminology.",
        created_at=_dt(5),
    )


def _legacy(legacy_id: str, label: str, canonical_term: CanonicalTerm) -> LegacyTermRecord:
    return LegacyTermRecord(
        legacy_term_record_id=LegacyTermRecordId(legacy_id),
        label=Label(label),
        canonical_term_id=canonical_term.canonical_term_id,
        lifecycle_status=TermLifecycleStatus.DEPRECATED,
        semantic_scope=GLOBAL_SCOPE,
        rationale="Legacy label retained for historical comparability.",
        created_at=_dt(6),
    )


def _entity(entity_id: str = "entity:system:chw") -> CanonicalEntity:
    return CanonicalEntity(
        canonical_entity_id=CanonicalEntityId(entity_id),
        entity_kind=CanonicalEntityKind.SYSTEM,
        canonical_name=CanonicalName("North Chilled Water System"),
        entity_status=EntityStatus.ACTIVE,
        source_of_authority=AUTHORITY,
        created_at=_dt(7),
    )


def _membership(
    membership_id: str,
    entity: CanonicalEntity,
    node: TaxonomyNode,
    *,
    status: MembershipStatus = MembershipStatus.ACTIVE,
) -> EntityMembershipRecord:
    return EntityMembershipRecord(
        entity_membership_record_id=EntityMembershipRecordId(membership_id),
        canonical_entity_id=entity.canonical_entity_id,
        taxonomy_node_id=node.taxonomy_node_id,
        membership_status=status,
        semantic_scope=GLOBAL_SCOPE,
        rationale="Entity classified under the controlled system family.",
        created_at=_dt(8),
    )


def _equivalence(
    left: CanonicalTerm,
    right: CanonicalTerm,
    *,
    status: EquivalenceStatus = EquivalenceStatus.CONFIRMED,
    ambiguity: AmbiguityStatus = AmbiguityStatus.CLEAR,
) -> EquivalenceRecord:
    return EquivalenceRecord(
        equivalence_record_id=EquivalenceRecordId("equivalence:term1-term2"),
        left_ref=left.reference,
        right_ref=right.reference,
        equivalence_status=status,
        ambiguity_status=ambiguity,
        rationale=MatchRationale("Controlled equivalence confirmed by taxonomy governance."),
        semantic_scope=GLOBAL_SCOPE,
        created_at=_dt(9),
    )


def _candidate_match(
    candidate: CanonicalTerm,
    *,
    record_id: str = "candidate_match:chw-system",
    match_status: MatchStatus = MatchStatus.CONFIRMED,
    ambiguity: AmbiguityStatus = AmbiguityStatus.CLEAR,
    confidence: float = 0.96,
) -> CandidateMatchRecord:
    return CandidateMatchRecord(
        candidate_match_record_id=CandidateMatchRecordId(record_id),
        source_label="CHW system",
        candidate_ref=candidate.reference,
        match_status=match_status,
        ambiguity_status=ambiguity,
        semantic_scope=GLOBAL_SCOPE,
        confidence=ConfidenceScore(confidence),
        rationale=MatchRationale("Source label reviewed against controlled term inventory."),
        created_at=_dt(10),
    )


def _boundary(node: TaxonomyNode, nearest: TaxonomyNode | None = None, *, status: BoundaryStatus = BoundaryStatus.DEFINED) -> BoundaryRecord:
    return BoundaryRecord(
        boundary_record_id=BoundaryRecordId(f"boundary:{node.taxonomy_node_id.value}"),
        taxonomy_node_id=node.taxonomy_node_id,
        boundary_status=status,
        semantic_scope=GLOBAL_SCOPE,
        inclusion_rule=SemanticText("Includes chilled water generation and primary distribution."),
        exclusion_rule=SemanticText("Excludes cooling towers operating as standalone assets."),
        positive_examples=("central chilled water plant",),
        negative_examples=("cooling tower only",),
        nearest_valid_ref=None if nearest is None else nearest.reference,
        created_at=_dt(11),
    )


def _join(target: CanonicalTerm, *, safety: JoinSafetyLevel = JoinSafetyLevel.SAFE) -> JoinKeySemanticRecord:
    return JoinKeySemanticRecord(
        join_key_semantic_record_id=JoinKeySemanticRecordId("join:system_family:chw"),
        join_key=JoinKeyName("system_family"),
        target_ref=target.reference,
        semantic_scope=GLOBAL_SCOPE,
        join_safety_level=safety,
        rationale=MatchRationale("Join key pinned to the canonical taxonomy term."),
        created_at=_dt(12),
    )


def _deprecation(deprecated: CanonicalTerm, replacement: CanonicalTerm | None = None) -> DeprecationRecord:
    return DeprecationRecord(
        deprecation_record_id=DeprecationRecordId("deprecation:term2"),
        deprecated_ref=deprecated.reference,
        replacement_ref=None if replacement is None else replacement.reference,
        deprecation_status=DeprecationStatus.DEPRECATED if replacement is None else DeprecationStatus.REPLACED,
        rationale=MatchRationale("Controlled taxonomy evolution record."),
        effective_from=_dt(13),
        deprecated_at=_dt(13),
    )


def _change(
    target_version: TaxonomyVersion,
    *,
    record_id: str = "change:additive:v1",
    source_version: TaxonomyVersion | None = None,
    change_kind: TaxonomyChangeKind = TaxonomyChangeKind.ADDITIVE,
    comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
    affected_refs=(),
) -> TaxonomyChangeRecord:
    return TaxonomyChangeRecord(
        taxonomy_change_record_id=TaxonomyChangeRecordId(record_id),
        source_taxonomy_version_id=(
            None if source_version is None else source_version.taxonomy_version_id
        ),
        target_taxonomy_version_id=target_version.taxonomy_version_id,
        change_kind=change_kind,
        affected_refs=tuple(affected_refs),
        comparability_status=comparability_status,
        severity=ConflictSeverity.LOW,
        summary=SemanticText("Taxonomy updated in a controlled and documented way."),
        created_at=_dt(14),
    )


def _integrity(
    version: TaxonomyVersion,
    *,
    status: SemanticIntegrityStatus = SemanticIntegrityStatus.OK,
    ambiguous_alias_ids=(),
    unresolved_match_ids=(),
    details=(),
) -> SemanticIntegrityRecord:
    return SemanticIntegrityRecord(
        semantic_integrity_record_id=SemanticIntegrityRecordId(f"integrity:{version.taxonomy_version_id.value}"),
        taxonomy_version_id=version.taxonomy_version_id,
        integrity_status=status,
        ambiguous_alias_ids=tuple(ambiguous_alias_ids),
        unresolved_candidate_match_ids=tuple(unresolved_match_ids),
        conflicting_refs=(),
        details=tuple(details),
        checked_at=_dt(15),
    )


def _clean_graph():
    registry = _registry()
    version = _version()
    node_root = _node("node:plant", "term:plant", node_type=TaxonomyNodeType.ROOT)
    term_root = _term("term:plant", "node:plant", "Chiller Plant")
    node_alt = _node("node:chw", "term:chw", parent_id="node:plant")
    term_alt = _term("term:chw", "node:chw", "Central Chilled Water")
    alias = _alias("alias:chw-system", "CHW system", term_root)
    entity = _entity()
    membership = _membership("membership:entity-node", entity, node_root)
    equivalence = _equivalence(term_root, term_alt)
    candidate_match = _candidate_match(term_root)
    boundary = _boundary(node_root, node_alt)
    join = _join(term_root)
    deprecation = _deprecation(term_alt)
    change = _change(version, affected_refs=(term_root.reference,))
    integrity = _integrity(version)
    return {
        "registry": registry,
        "version": version,
        "node_root": node_root,
        "term_root": term_root,
        "node_alt": node_alt,
        "term_alt": term_alt,
        "alias": alias,
        "entity": entity,
        "membership": membership,
        "equivalence": equivalence,
        "candidate_match": candidate_match,
        "boundary": boundary,
        "join": join,
        "deprecation": deprecation,
        "change": change,
        "integrity": integrity,
    }


def _validate_graph(validator: BasicSemanticIntegrityValidator, graph: dict):
    return validator.validate_semantic_graph(
        taxonomy_registries=(graph["registry"],),
        taxonomy_versions=(graph["version"],),
        taxonomy_nodes=(graph["node_root"], graph["node_alt"]),
        canonical_terms=(graph["term_root"], graph["term_alt"]),
        alias_records=(graph["alias"],),
        canonical_entities=(graph["entity"],),
        entity_membership_records=(graph["membership"],),
        equivalence_records=(graph["equivalence"],),
        candidate_match_records=(graph["candidate_match"],),
        boundary_records=(graph["boundary"],),
        join_key_semantic_records=(graph["join"],),
        deprecation_records=(graph["deprecation"],),
        taxonomy_change_records=(graph["change"],),
        semantic_integrity_records=(graph["integrity"],),
    )


def test_validate_semantic_graph_pass_for_consistent_semantic_objects() -> None:
    validator = BasicSemanticIntegrityValidator()
    graph = _clean_graph()

    report = _validate_graph(validator, graph)

    assert report.outcome is ValidationOutcome.PASS
    assert report.violations == ()


def test_validate_semantic_graph_pass_with_warnings_for_non_final_semantic_states() -> None:
    validator = BasicSemanticIntegrityValidator()
    graph = _clean_graph()
    graph["alias"] = _alias(
        "alias:chw-system",
        "CHW system",
        graph["term_root"],
        status=AliasStatus.PROPOSED,
    )
    graph["legacy"] = _legacy("legacy:cooling-plant", "Cooling Plant", graph["term_root"])
    graph["membership"] = _membership(
        "membership:entity-node",
        graph["entity"],
        graph["node_root"],
        status=MembershipStatus.CONDITIONAL,
    )
    graph["candidate_match"] = _candidate_match(
        graph["term_root"],
        match_status=MatchStatus.AMBIGUOUS,
        ambiguity=AmbiguityStatus.AMBIGUOUS,
        confidence=0.65,
    )
    graph["boundary"] = _boundary(graph["node_root"], graph["node_alt"], status=BoundaryStatus.PROVISIONAL)
    graph["join"] = _join(graph["term_root"], safety=JoinSafetyLevel.CONDITIONAL)
    graph["integrity"] = _integrity(
        graph["version"],
        status=SemanticIntegrityStatus.ISSUES_PRESENT,
        ambiguous_alias_ids=(graph["alias"].alias_record_id,),
        unresolved_match_ids=(graph["candidate_match"].candidate_match_record_id,),
        details=("Pending semantic curation remains open.",),
    )

    report = validator.validate_semantic_graph(
        taxonomy_registries=(graph["registry"],),
        taxonomy_versions=(graph["version"],),
        taxonomy_nodes=(graph["node_root"], graph["node_alt"]),
        canonical_terms=(graph["term_root"], graph["term_alt"]),
        alias_records=(graph["alias"],),
        legacy_term_records=(graph["legacy"],),
        canonical_entities=(graph["entity"],),
        entity_membership_records=(graph["membership"],),
        equivalence_records=(graph["equivalence"],),
        candidate_match_records=(graph["candidate_match"],),
        boundary_records=(graph["boundary"],),
        join_key_semantic_records=(graph["join"],),
        deprecation_records=(graph["deprecation"],),
        taxonomy_change_records=(graph["change"],),
        semantic_integrity_records=(graph["integrity"],),
    )

    assert report.outcome is ValidationOutcome.PASS_WITH_WARNINGS
    assert any(item.code == "alias.non_confirmed_declared" for item in report.violations)
    assert any(item.code == "legacy.declared" for item in report.violations)
    assert any(item.code == "integrity.issues_declared" for item in report.violations)


def test_validate_semantic_graph_fail_with_multiple_unresolved_references() -> None:
    validator = BasicSemanticIntegrityValidator()
    version = _version()
    node = _node("node:plant", "term:plant")
    alias = AliasRecord(
        alias_record_id=AliasRecordId("alias:unknown"),
        label=Label("Unknown CHW"),
        target_ref=_term("term:plant", "node:plant", "Chiller Plant").reference,
        alias_kind=AliasKind.ALIAS,
        alias_status=AliasStatus.CONFIRMED,
        semantic_scope=GLOBAL_SCOPE,
        rationale="Alias points to a target omitted from context.",
        created_at=_dt(16),
    )
    membership = EntityMembershipRecord(
        entity_membership_record_id=EntityMembershipRecordId("membership:missing"),
        canonical_entity_id=CanonicalEntityId("entity:missing"),
        taxonomy_node_id=node.taxonomy_node_id,
        membership_status=MembershipStatus.ACTIVE,
        semantic_scope=GLOBAL_SCOPE,
        rationale="Membership references a missing entity.",
        created_at=_dt(17),
    )
    boundary = BoundaryRecord(
        boundary_record_id=BoundaryRecordId("boundary:missing-node"),
        taxonomy_node_id=TaxonomyNodeId("node:missing"),
        boundary_status=BoundaryStatus.DEFINED,
        semantic_scope=GLOBAL_SCOPE,
        inclusion_rule=SemanticText("Boundary text exists."),
        exclusion_rule=None,
        positive_examples=(),
        negative_examples=(),
        nearest_valid_ref=None,
        created_at=_dt(18),
    )
    deprecation = DeprecationRecord(
        deprecation_record_id=DeprecationRecordId("deprecation:alias-to-missing-term"),
        deprecated_ref=alias.reference,
        replacement_ref=_term("term:missing", "node:missing", "Replacement").reference,
        deprecation_status=DeprecationStatus.REPLACED,
        rationale=MatchRationale("Replacement target is intentionally unresolved."),
        effective_from=_dt(19),
        deprecated_at=_dt(19),
    )

    report = validator.validate_semantic_graph(
        taxonomy_versions=(version,),
        taxonomy_nodes=(node,),
        alias_records=(alias,),
        entity_membership_records=(membership,),
        boundary_records=(boundary,),
        deprecation_records=(deprecation,),
    )

    assert report.outcome is ValidationOutcome.FAIL
    assert len(report.violations) >= 5
    assert any(item.code == "version.registry_reference_invalid" for item in report.violations)
    assert any(item.code == "node.term_reference_invalid" for item in report.violations)
    assert any(item.code == "alias.target_unresolved" for item in report.violations)
    assert any(item.code == "membership.entity_reference_invalid" for item in report.violations)
    assert any(item.code == "deprecation.replacement_unresolved" for item in report.violations)


def test_confirmed_alias_conflict_in_same_scope_fails() -> None:
    validator = BasicSemanticIntegrityValidator()
    graph = _clean_graph()
    conflicting_alias = _alias(
        "alias:chw-system-alt",
        "chw system",
        graph["term_alt"],
        status=AliasStatus.CONFIRMED,
    )

    report = validator.validate_semantic_graph(
        taxonomy_registries=(graph["registry"],),
        taxonomy_versions=(graph["version"],),
        taxonomy_nodes=(graph["node_root"], graph["node_alt"]),
        canonical_terms=(graph["term_root"], graph["term_alt"]),
        alias_records=(graph["alias"], conflicting_alias),
    )

    assert report.outcome is ValidationOutcome.FAIL
    assert any(item.code == "alias.scope_conflict" for item in report.violations)


def test_split_change_cannot_claim_full_comparability() -> None:
    validator = BasicSemanticIntegrityValidator()
    registry = _registry()
    source_version = _version("version:system_family:v1")
    target_version = _version(
        "version:system_family:v2",
        supersedes="version:system_family:v1",
    )
    node = _node("node:plant", "term:plant", version_id="version:system_family:v2")
    term = _term("term:plant", "node:plant", "Chiller Plant")
    change = TaxonomyChangeRecord(
        taxonomy_change_record_id=TaxonomyChangeRecordId("change:split:v1-v2"),
        source_taxonomy_version_id=source_version.taxonomy_version_id,
        target_taxonomy_version_id=target_version.taxonomy_version_id,
        change_kind=TaxonomyChangeKind.SPLIT,
        affected_refs=(term.reference,),
        comparability_status=ComparabilityStatus.COMPARABLE,
        severity=ConflictSeverity.HIGH,
        summary=SemanticText("Split performed across the taxonomy branch."),
        created_at=_dt(20),
    )

    report = validator.validate_semantic_graph(
        taxonomy_registries=(registry,),
        taxonomy_versions=(source_version, target_version),
        taxonomy_nodes=(node,),
        canonical_terms=(term,),
        taxonomy_change_records=(change,),
    )

    assert report.outcome is ValidationOutcome.FAIL
    assert any(item.code == "change.comparability_incoherent" for item in report.violations)


def test_integrity_record_cannot_be_ok_while_pending_matches_exist() -> None:
    validator = BasicSemanticIntegrityValidator()
    graph = _clean_graph()
    graph["candidate_match"] = _candidate_match(
        graph["term_root"],
        match_status=MatchStatus.CANDIDATE,
        ambiguity=AmbiguityStatus.UNRESOLVED,
        confidence=0.58,
    )
    graph["integrity"] = _integrity(graph["version"], status=SemanticIntegrityStatus.OK)

    report = _validate_graph(validator, graph)

    assert report.outcome is ValidationOutcome.FAIL
    assert any(item.code == "integrity.ok_but_pending_issues" for item in report.violations)
