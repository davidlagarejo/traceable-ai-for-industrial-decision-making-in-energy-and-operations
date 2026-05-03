from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

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
from ..domain.records import (
    BoundaryRecord,
    CandidateMatchRecord,
    DeprecationRecord,
    EquivalenceRecord,
    JoinKeySemanticRecord,
    SemanticIntegrityRecord,
    TaxonomyChangeRecord,
)
from .alias_validator import validate_alias_record
from .boundary_validator import validate_boundary_record
from .change_validator import validate_taxonomy_change_record
from .collector import ViolationCollector, ViolationDraft
from .context import ValidationContext
from .deprecation_validator import validate_deprecation_record
from .entity_validator import validate_canonical_entity, validate_entity_membership_record
from .equivalence_validator import validate_candidate_match_record, validate_equivalence_record
from .join_validator import validate_join_key_semantic_record
from .results import ValidationOutcome, ValidationReport, ValidationRun, ValidationViolation
from .semantic_status_validator import validate_semantic_integrity_record
from .taxonomy_node_validator import validate_taxonomy_node
from .taxonomy_registry_validator import validate_taxonomy_registry
from .taxonomy_version_validator import validate_taxonomy_version
from .term_validator import validate_canonical_term, validate_legacy_term_record


DEFAULT_VALIDATOR_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    target_refs: tuple[str, ...]


class BasicSemanticIntegrityValidator:
    def __init__(
        self,
        *,
        validator_version: str = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_taxonomy_registry(self, registry: TaxonomyRegistry) -> ValidationReport:
        collector = ViolationCollector(_registry_ref(registry))
        validate_taxonomy_registry(registry, collector)
        return self._build_report(ValidationArtifacts((_registry_ref(registry),)), collector)

    def validate_taxonomy_version(
        self,
        version: TaxonomyVersion,
        *,
        context: ValidationContext | None = None,
        taxonomy_registry: TaxonomyRegistry | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_version_ref(version))
        validate_taxonomy_version(version, collector, context=context, taxonomy_registry=taxonomy_registry)
        return self._build_report(ValidationArtifacts((_version_ref(version),)), collector)

    def validate_taxonomy_node(
        self,
        node: TaxonomyNode,
        *,
        context: ValidationContext | None = None,
        canonical_term: CanonicalTerm | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_node_ref(node))
        validate_taxonomy_node(node, collector, context=context, canonical_term=canonical_term)
        return self._build_report(ValidationArtifacts((_node_ref(node),)), collector)

    def validate_canonical_term(
        self,
        term: CanonicalTerm,
        *,
        context: ValidationContext | None = None,
        taxonomy_node: TaxonomyNode | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_term_ref(term))
        validate_canonical_term(term, collector, context=context, taxonomy_node=taxonomy_node)
        return self._build_report(ValidationArtifacts((_term_ref(term),)), collector)

    def validate_alias_record(
        self,
        alias_record: AliasRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_alias_ref(alias_record))
        validate_alias_record(alias_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_alias_ref(alias_record),)), collector)

    def validate_legacy_term_record(
        self,
        legacy_term: LegacyTermRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_legacy_ref(legacy_term))
        validate_legacy_term_record(legacy_term, collector, context=context)
        return self._build_report(ValidationArtifacts((_legacy_ref(legacy_term),)), collector)

    def validate_canonical_entity(self, entity: CanonicalEntity) -> ValidationReport:
        collector = ViolationCollector(_entity_ref(entity))
        validate_canonical_entity(entity, collector)
        return self._build_report(ValidationArtifacts((_entity_ref(entity),)), collector)

    def validate_entity_membership_record(
        self,
        membership: EntityMembershipRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_membership_ref(membership))
        validate_entity_membership_record(membership, collector, context=context)
        return self._build_report(ValidationArtifacts((_membership_ref(membership),)), collector)

    def validate_equivalence_record(
        self,
        equivalence_record: EquivalenceRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_equivalence_ref(equivalence_record))
        validate_equivalence_record(equivalence_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_equivalence_ref(equivalence_record),)), collector)

    def validate_candidate_match_record(
        self,
        candidate_match_record: CandidateMatchRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_candidate_match_ref(candidate_match_record))
        validate_candidate_match_record(candidate_match_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_candidate_match_ref(candidate_match_record),)), collector)

    def validate_boundary_record(
        self,
        boundary_record: BoundaryRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_boundary_ref(boundary_record))
        validate_boundary_record(boundary_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_boundary_ref(boundary_record),)), collector)

    def validate_join_key_semantic_record(
        self,
        join_key_record: JoinKeySemanticRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_join_ref(join_key_record))
        validate_join_key_semantic_record(join_key_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_join_ref(join_key_record),)), collector)

    def validate_deprecation_record(
        self,
        deprecation_record: DeprecationRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_deprecation_ref(deprecation_record))
        validate_deprecation_record(deprecation_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_deprecation_ref(deprecation_record),)), collector)

    def validate_taxonomy_change_record(
        self,
        change_record: TaxonomyChangeRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_change_ref(change_record))
        validate_taxonomy_change_record(change_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_change_ref(change_record),)), collector)

    def validate_semantic_integrity_record(
        self,
        integrity_record: SemanticIntegrityRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_integrity_ref(integrity_record))
        validate_semantic_integrity_record(integrity_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_integrity_ref(integrity_record),)), collector)

    def validate_semantic_graph(
        self,
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
    ) -> ValidationReport:
        taxonomy_registries = tuple(taxonomy_registries)
        taxonomy_versions = tuple(taxonomy_versions)
        taxonomy_nodes = tuple(taxonomy_nodes)
        canonical_terms = tuple(canonical_terms)
        alias_records = tuple(alias_records)
        legacy_term_records = tuple(legacy_term_records)
        canonical_entities = tuple(canonical_entities)
        entity_membership_records = tuple(entity_membership_records)
        equivalence_records = tuple(equivalence_records)
        candidate_match_records = tuple(candidate_match_records)
        boundary_records = tuple(boundary_records)
        join_key_semantic_records = tuple(join_key_semantic_records)
        deprecation_records = tuple(deprecation_records)
        taxonomy_change_records = tuple(taxonomy_change_records)
        semantic_integrity_records = tuple(semantic_integrity_records)

        context = ValidationContext.from_iterables(
            taxonomy_registries=taxonomy_registries,
            taxonomy_versions=taxonomy_versions,
            taxonomy_nodes=taxonomy_nodes,
            canonical_terms=canonical_terms,
            alias_records=alias_records,
            legacy_term_records=legacy_term_records,
            canonical_entities=canonical_entities,
            entity_membership_records=entity_membership_records,
            equivalence_records=equivalence_records,
            candidate_match_records=candidate_match_records,
            boundary_records=boundary_records,
            join_key_semantic_records=join_key_semantic_records,
            deprecation_records=deprecation_records,
            taxonomy_change_records=taxonomy_change_records,
            semantic_integrity_records=semantic_integrity_records,
        )
        collector = ViolationCollector("graph:semantic")

        for item in taxonomy_registries:
            local = ViolationCollector(_registry_ref(item))
            validate_taxonomy_registry(item, local)
            _merge_collector(collector, local)

        for item in taxonomy_versions:
            local = ViolationCollector(_version_ref(item))
            validate_taxonomy_version(item, local, context=context)
            _merge_collector(collector, local)

        for item in taxonomy_nodes:
            local = ViolationCollector(_node_ref(item))
            validate_taxonomy_node(item, local, context=context)
            _merge_collector(collector, local)

        for item in canonical_terms:
            local = ViolationCollector(_term_ref(item))
            validate_canonical_term(item, local, context=context)
            _merge_collector(collector, local)

        for item in alias_records:
            local = ViolationCollector(_alias_ref(item))
            validate_alias_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in legacy_term_records:
            local = ViolationCollector(_legacy_ref(item))
            validate_legacy_term_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in canonical_entities:
            local = ViolationCollector(_entity_ref(item))
            validate_canonical_entity(item, local)
            _merge_collector(collector, local)

        for item in entity_membership_records:
            local = ViolationCollector(_membership_ref(item))
            validate_entity_membership_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in equivalence_records:
            local = ViolationCollector(_equivalence_ref(item))
            validate_equivalence_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in candidate_match_records:
            local = ViolationCollector(_candidate_match_ref(item))
            validate_candidate_match_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in boundary_records:
            local = ViolationCollector(_boundary_ref(item))
            validate_boundary_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in join_key_semantic_records:
            local = ViolationCollector(_join_ref(item))
            validate_join_key_semantic_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in deprecation_records:
            local = ViolationCollector(_deprecation_ref(item))
            validate_deprecation_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in taxonomy_change_records:
            local = ViolationCollector(_change_ref(item))
            validate_taxonomy_change_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in semantic_integrity_records:
            local = ViolationCollector(_integrity_ref(item))
            validate_semantic_integrity_record(item, local, context=context)
            _merge_collector(collector, local)

        target_refs = tuple(
            _unique_ordered(
                [
                    *(_registry_ref(item) for item in taxonomy_registries),
                    *(_version_ref(item) for item in taxonomy_versions),
                    *(_node_ref(item) for item in taxonomy_nodes),
                    *(_term_ref(item) for item in canonical_terms),
                    *(_alias_ref(item) for item in alias_records),
                    *(_legacy_ref(item) for item in legacy_term_records),
                    *(_entity_ref(item) for item in canonical_entities),
                    *(_membership_ref(item) for item in entity_membership_records),
                    *(_equivalence_ref(item) for item in equivalence_records),
                    *(_candidate_match_ref(item) for item in candidate_match_records),
                    *(_boundary_ref(item) for item in boundary_records),
                    *(_join_ref(item) for item in join_key_semantic_records),
                    *(_deprecation_ref(item) for item in deprecation_records),
                    *(_change_ref(item) for item in taxonomy_change_records),
                    *(_integrity_ref(item) for item in semantic_integrity_records),
                ]
            )
        ) or ("graph:semantic",)

        return self._build_report(ValidationArtifacts(target_refs), collector)

    def _build_report(
        self,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        run_id = _stable_id(
            "semantic_validation",
            self._validator_version,
            outcome.value,
            *artifacts.target_refs,
            *(_draft_signature(item) for item in collector.violations),
        )
        violations = tuple(
            ValidationViolation(
                violation_id=_stable_id(
                    "semantic_violation",
                    run_id,
                    str(index),
                    draft.code.value,
                    draft.target_ref,
                    draft.field_ref or "nofield",
                ),
                code=draft.code.value,
                severity=draft.severity,
                message=draft.message,
                target_ref=draft.target_ref,
                field_ref=draft.field_ref,
                blocking=draft.blocking,
            )
            for index, draft in enumerate(collector.violations, start=1)
        )
        return ValidationReport(
            outcome=outcome,
            validation_run=ValidationRun(
                run_id=run_id,
                validator_version=self._validator_version,
                executed_at=self._clock(),
                target_refs=artifacts.target_refs,
            ),
            violations=violations,
        )


def _merge_collector(target: ViolationCollector, source: ViolationCollector) -> None:
    for item in source.violations:
        target.add(
            item.code,
            item.message,
            target_ref=item.target_ref,
            field_ref=item.field_ref,
            severity=item.severity,
            blocking=item.blocking,
        )


def _derive_outcome(collector: ViolationCollector) -> ValidationOutcome:
    if collector.has_errors:
        return ValidationOutcome.FAIL
    if collector.has_warnings:
        return ValidationOutcome.PASS_WITH_WARNINGS
    return ValidationOutcome.PASS


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _draft_signature(draft: ViolationDraft) -> str:
    return "|".join(
        (
            draft.code.value,
            draft.severity.value,
            draft.target_ref,
            draft.field_ref or "nofield",
            draft.message,
        )
    )


def _unique_ordered(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _registry_ref(item: TaxonomyRegistry) -> str:
    return f"taxonomy_registry:{item.taxonomy_registry_id.value}"


def _version_ref(item: TaxonomyVersion) -> str:
    return f"taxonomy_version:{item.taxonomy_version_id.value}"


def _node_ref(item: TaxonomyNode) -> str:
    return f"taxonomy_node:{item.taxonomy_node_id.value}"


def _term_ref(item: CanonicalTerm) -> str:
    return f"canonical_term:{item.canonical_term_id.value}"


def _alias_ref(item: AliasRecord) -> str:
    return f"alias_record:{item.alias_record_id.value}"


def _legacy_ref(item: LegacyTermRecord) -> str:
    return f"legacy_term_record:{item.legacy_term_record_id.value}"


def _entity_ref(item: CanonicalEntity) -> str:
    return f"canonical_entity:{item.canonical_entity_id.value}"


def _membership_ref(item: EntityMembershipRecord) -> str:
    return f"entity_membership_record:{item.entity_membership_record_id.value}"


def _equivalence_ref(item: EquivalenceRecord) -> str:
    return f"equivalence_record:{item.equivalence_record_id.value}"


def _candidate_match_ref(item: CandidateMatchRecord) -> str:
    return f"candidate_match_record:{item.candidate_match_record_id.value}"


def _boundary_ref(item: BoundaryRecord) -> str:
    return f"boundary_record:{item.boundary_record_id.value}"


def _join_ref(item: JoinKeySemanticRecord) -> str:
    return f"join_key_semantic_record:{item.join_key_semantic_record_id.value}"


def _deprecation_ref(item: DeprecationRecord) -> str:
    return f"deprecation_record:{item.deprecation_record_id.value}"


def _change_ref(item: TaxonomyChangeRecord) -> str:
    return f"taxonomy_change_record:{item.taxonomy_change_record_id.value}"


def _integrity_ref(item: SemanticIntegrityRecord) -> str:
    return f"semantic_integrity_record:{item.semantic_integrity_record_id.value}"

