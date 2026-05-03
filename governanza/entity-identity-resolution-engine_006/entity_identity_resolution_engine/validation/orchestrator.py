from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from .._compat import dataclass
from ..domain.entities import (
    CandidateMatchRecord,
    CandidateMatchSet,
    CanonicalEntity,
    EntityAliasRecord,
    ObservedNameRecord,
    ObservedRecord,
)
from ..domain.records import (
    AmbiguousResolutionRecord,
    ConfirmedMatchRecord,
    EntityHistoryRecord,
    MergeEventRecord,
    NoMatchRecord,
    RelatedButNotEquivalentRecord,
    ResolutionConfidenceRecord,
    ResolutionDecisionRecord,
    ResolutionEvidenceRecord,
    SplitEventRecord,
)
from .candidate_validator import validate_candidate_match_record, validate_candidate_match_set
from .collector import ViolationCollector, ViolationDraft
from .context import ValidationContext
from .decision_validator import (
    validate_ambiguous_resolution_record,
    validate_confirmed_match_record,
    validate_no_match_record,
    validate_related_but_not_equivalent_record,
    validate_resolution_decision_record,
)
from .entity_validator import validate_canonical_entity, validate_entity_alias_record
from .evidence_validator import (
    validate_resolution_confidence_record,
    validate_resolution_evidence_record,
)
from .event_validator import validate_merge_event_record, validate_split_event_record
from .history_validator import validate_entity_history_record
from .observed_validator import validate_observed_name_record, validate_observed_record
from .results import ValidationOutcome, ValidationReport, ValidationRun, ValidationViolation


DEFAULT_VALIDATOR_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    target_refs: tuple[str, ...]


class BasicIdentityIntegrityValidator:
    def __init__(
        self,
        *,
        validator_version: str = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_observed_record(
        self,
        observed_record: ObservedRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_observed_record_ref(observed_record))
        validate_observed_record(observed_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_observed_record_ref(observed_record),)), collector)

    def validate_observed_name_record(
        self,
        observed_name_record: ObservedNameRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_observed_name_ref(observed_name_record))
        validate_observed_name_record(observed_name_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_observed_name_ref(observed_name_record),)), collector)

    def validate_canonical_entity(
        self,
        canonical_entity: CanonicalEntity,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_entity_ref(canonical_entity))
        validate_canonical_entity(canonical_entity, collector, context=context)
        return self._build_report(ValidationArtifacts((_entity_ref(canonical_entity),)), collector)

    def validate_entity_alias_record(
        self,
        entity_alias_record: EntityAliasRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_alias_ref(entity_alias_record))
        validate_entity_alias_record(entity_alias_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_alias_ref(entity_alias_record),)), collector)

    def validate_candidate_match_record(
        self,
        candidate_match_record: CandidateMatchRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_candidate_match_ref(candidate_match_record))
        validate_candidate_match_record(candidate_match_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_candidate_match_ref(candidate_match_record),)), collector)

    def validate_candidate_match_set(
        self,
        candidate_match_set: CandidateMatchSet,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_candidate_match_set_ref(candidate_match_set))
        validate_candidate_match_set(candidate_match_set, collector, context=context)
        return self._build_report(ValidationArtifacts((_candidate_match_set_ref(candidate_match_set),)), collector)

    def validate_resolution_decision_record(
        self,
        resolution_decision_record: ResolutionDecisionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_decision_ref(resolution_decision_record))
        validate_resolution_decision_record(resolution_decision_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_decision_ref(resolution_decision_record),)), collector)

    def validate_confirmed_match_record(
        self,
        confirmed_match_record: ConfirmedMatchRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_confirmed_match_ref(confirmed_match_record))
        validate_confirmed_match_record(confirmed_match_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_confirmed_match_ref(confirmed_match_record),)), collector)

    def validate_no_match_record(
        self,
        no_match_record: NoMatchRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_no_match_ref(no_match_record))
        validate_no_match_record(no_match_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_no_match_ref(no_match_record),)), collector)

    def validate_ambiguous_resolution_record(
        self,
        ambiguous_resolution_record: AmbiguousResolutionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_ambiguous_ref(ambiguous_resolution_record))
        validate_ambiguous_resolution_record(ambiguous_resolution_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_ambiguous_ref(ambiguous_resolution_record),)), collector)

    def validate_related_but_not_equivalent_record(
        self,
        related_record: RelatedButNotEquivalentRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_related_ref(related_record))
        validate_related_but_not_equivalent_record(related_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_related_ref(related_record),)), collector)

    def validate_resolution_evidence_record(
        self,
        resolution_evidence_record: ResolutionEvidenceRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_evidence_ref(resolution_evidence_record))
        validate_resolution_evidence_record(resolution_evidence_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_evidence_ref(resolution_evidence_record),)), collector)

    def validate_resolution_confidence_record(
        self,
        resolution_confidence_record: ResolutionConfidenceRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_confidence_ref(resolution_confidence_record))
        validate_resolution_confidence_record(resolution_confidence_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_confidence_ref(resolution_confidence_record),)), collector)

    def validate_merge_event_record(
        self,
        merge_event_record: MergeEventRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_merge_ref(merge_event_record))
        validate_merge_event_record(merge_event_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_merge_ref(merge_event_record),)), collector)

    def validate_split_event_record(
        self,
        split_event_record: SplitEventRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_split_ref(split_event_record))
        validate_split_event_record(split_event_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_split_ref(split_event_record),)), collector)

    def validate_entity_history_record(
        self,
        entity_history_record: EntityHistoryRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_history_ref(entity_history_record))
        validate_entity_history_record(entity_history_record, collector, context=context)
        return self._build_report(ValidationArtifacts((_history_ref(entity_history_record),)), collector)

    def validate_graph(
        self,
        *,
        observed_records: Iterable[ObservedRecord] = (),
        observed_name_records: Iterable[ObservedNameRecord] = (),
        canonical_entities: Iterable[CanonicalEntity] = (),
        entity_alias_records: Iterable[EntityAliasRecord] = (),
        candidate_match_records: Iterable[CandidateMatchRecord] = (),
        candidate_match_sets: Iterable[CandidateMatchSet] = (),
        resolution_decision_records: Iterable[ResolutionDecisionRecord] = (),
        confirmed_match_records: Iterable[ConfirmedMatchRecord] = (),
        no_match_records: Iterable[NoMatchRecord] = (),
        ambiguous_resolution_records: Iterable[AmbiguousResolutionRecord] = (),
        related_records: Iterable[RelatedButNotEquivalentRecord] = (),
        resolution_evidence_records: Iterable[ResolutionEvidenceRecord] = (),
        resolution_confidence_records: Iterable[ResolutionConfidenceRecord] = (),
        merge_event_records: Iterable[MergeEventRecord] = (),
        split_event_records: Iterable[SplitEventRecord] = (),
        entity_history_records: Iterable[EntityHistoryRecord] = (),
    ) -> ValidationReport:
        observed_records = tuple(observed_records)
        observed_name_records = tuple(observed_name_records)
        canonical_entities = tuple(canonical_entities)
        entity_alias_records = tuple(entity_alias_records)
        candidate_match_records = tuple(candidate_match_records)
        candidate_match_sets = tuple(candidate_match_sets)
        resolution_decision_records = tuple(resolution_decision_records)
        confirmed_match_records = tuple(confirmed_match_records)
        no_match_records = tuple(no_match_records)
        ambiguous_resolution_records = tuple(ambiguous_resolution_records)
        related_records = tuple(related_records)
        resolution_evidence_records = tuple(resolution_evidence_records)
        resolution_confidence_records = tuple(resolution_confidence_records)
        merge_event_records = tuple(merge_event_records)
        split_event_records = tuple(split_event_records)
        entity_history_records = tuple(entity_history_records)

        context = ValidationContext.from_iterables(
            observed_records=observed_records,
            observed_name_records=observed_name_records,
            canonical_entities=canonical_entities,
            entity_alias_records=entity_alias_records,
            candidate_match_records=candidate_match_records,
            candidate_match_sets=candidate_match_sets,
            resolution_decision_records=resolution_decision_records,
            confirmed_match_records=confirmed_match_records,
            no_match_records=no_match_records,
            ambiguous_resolution_records=ambiguous_resolution_records,
            related_records=related_records,
            resolution_evidence_records=resolution_evidence_records,
            resolution_confidence_records=resolution_confidence_records,
            merge_event_records=merge_event_records,
            split_event_records=split_event_records,
            entity_history_records=entity_history_records,
        )
        collector = ViolationCollector("graph:entity_identity_resolution")

        for item in observed_records:
            local = ViolationCollector(_observed_record_ref(item))
            validate_observed_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in observed_name_records:
            local = ViolationCollector(_observed_name_ref(item))
            validate_observed_name_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in canonical_entities:
            local = ViolationCollector(_entity_ref(item))
            validate_canonical_entity(item, local, context=context)
            _merge_collector(collector, local)

        for item in entity_alias_records:
            local = ViolationCollector(_alias_ref(item))
            validate_entity_alias_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in resolution_evidence_records:
            local = ViolationCollector(_evidence_ref(item))
            validate_resolution_evidence_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in resolution_confidence_records:
            local = ViolationCollector(_confidence_ref(item))
            validate_resolution_confidence_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in candidate_match_sets:
            local = ViolationCollector(_candidate_match_set_ref(item))
            validate_candidate_match_set(item, local, context=context)
            _merge_collector(collector, local)

        for item in candidate_match_records:
            local = ViolationCollector(_candidate_match_ref(item))
            validate_candidate_match_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in resolution_decision_records:
            local = ViolationCollector(_decision_ref(item))
            validate_resolution_decision_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in confirmed_match_records:
            local = ViolationCollector(_confirmed_match_ref(item))
            validate_confirmed_match_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in no_match_records:
            local = ViolationCollector(_no_match_ref(item))
            validate_no_match_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in ambiguous_resolution_records:
            local = ViolationCollector(_ambiguous_ref(item))
            validate_ambiguous_resolution_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in related_records:
            local = ViolationCollector(_related_ref(item))
            validate_related_but_not_equivalent_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in merge_event_records:
            local = ViolationCollector(_merge_ref(item))
            validate_merge_event_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in split_event_records:
            local = ViolationCollector(_split_ref(item))
            validate_split_event_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in entity_history_records:
            local = ViolationCollector(_history_ref(item))
            validate_entity_history_record(item, local, context=context)
            _merge_collector(collector, local)

        target_refs = tuple(
            _unique_ordered(
                [
                    *(_observed_record_ref(item) for item in observed_records),
                    *(_observed_name_ref(item) for item in observed_name_records),
                    *(_entity_ref(item) for item in canonical_entities),
                    *(_alias_ref(item) for item in entity_alias_records),
                    *(_candidate_match_ref(item) for item in candidate_match_records),
                    *(_candidate_match_set_ref(item) for item in candidate_match_sets),
                    *(_decision_ref(item) for item in resolution_decision_records),
                    *(_confirmed_match_ref(item) for item in confirmed_match_records),
                    *(_no_match_ref(item) for item in no_match_records),
                    *(_ambiguous_ref(item) for item in ambiguous_resolution_records),
                    *(_related_ref(item) for item in related_records),
                    *(_evidence_ref(item) for item in resolution_evidence_records),
                    *(_confidence_ref(item) for item in resolution_confidence_records),
                    *(_merge_ref(item) for item in merge_event_records),
                    *(_split_ref(item) for item in split_event_records),
                    *(_history_ref(item) for item in entity_history_records),
                ]
            )
        ) or ("graph:entity_identity_resolution",)
        return self._build_report(ValidationArtifacts(target_refs), collector)

    def _build_report(
        self,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        run_id = _stable_id(
            "entity_identity_validation",
            self._validator_version,
            outcome.value,
            *artifacts.target_refs,
            *(_draft_signature(item) for item in collector.violations),
        )
        violations = tuple(
            ValidationViolation(
                violation_id=_stable_id(
                    "entity_identity_violation",
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


def validate_identity_resolution_graph(**kwargs: object) -> ValidationReport:
    return BasicIdentityIntegrityValidator().validate_graph(**kwargs)


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


def _draft_signature(item: ViolationDraft) -> str:
    return "|".join(
        (
            item.code.value,
            item.severity.value,
            item.message,
            item.target_ref,
            item.field_ref or "nofield",
            "blocking" if item.blocking else "nonblocking",
        )
    )


def _unique_ordered(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _observed_record_ref(observed_record: ObservedRecord) -> str:
    return f"observed_record:{observed_record.observed_record_id}"


def _observed_name_ref(observed_name_record: ObservedNameRecord) -> str:
    return f"observed_name_record:{observed_name_record.observed_name_record_id}"


def _entity_ref(canonical_entity: CanonicalEntity) -> str:
    return f"canonical_entity:{canonical_entity.entity_id}"


def _alias_ref(entity_alias_record: EntityAliasRecord) -> str:
    return f"entity_alias_record:{entity_alias_record.entity_alias_record_id}"


def _candidate_match_ref(candidate_match_record: CandidateMatchRecord) -> str:
    return f"candidate_match_record:{candidate_match_record.candidate_match_record_id}"


def _candidate_match_set_ref(candidate_match_set: CandidateMatchSet) -> str:
    return f"candidate_match_set:{candidate_match_set.candidate_match_set_id}"


def _decision_ref(resolution_decision_record: ResolutionDecisionRecord) -> str:
    return f"resolution_decision_record:{resolution_decision_record.resolution_decision_record_id}"


def _confirmed_match_ref(confirmed_match_record: ConfirmedMatchRecord) -> str:
    return f"confirmed_match_record:{confirmed_match_record.resolution_decision_record_id}"


def _no_match_ref(no_match_record: NoMatchRecord) -> str:
    return f"no_match_record:{no_match_record.resolution_decision_record_id}"


def _ambiguous_ref(ambiguous_resolution_record: AmbiguousResolutionRecord) -> str:
    return f"ambiguous_resolution_record:{ambiguous_resolution_record.resolution_decision_record_id}"


def _related_ref(related_record: RelatedButNotEquivalentRecord) -> str:
    return f"related_record:{related_record.resolution_decision_record_id}"


def _evidence_ref(resolution_evidence_record: ResolutionEvidenceRecord) -> str:
    return f"resolution_evidence_record:{resolution_evidence_record.resolution_evidence_record_id}"


def _confidence_ref(resolution_confidence_record: ResolutionConfidenceRecord) -> str:
    return f"resolution_confidence_record:{resolution_confidence_record.resolution_confidence_record_id}"


def _merge_ref(merge_event_record: MergeEventRecord) -> str:
    return f"merge_event_record:{merge_event_record.merge_event_record_id}"


def _split_ref(split_event_record: SplitEventRecord) -> str:
    return f"split_event_record:{split_event_record.split_event_record_id}"


def _history_ref(entity_history_record: EntityHistoryRecord) -> str:
    return f"entity_history_record:{entity_history_record.entity_history_record_id}"
