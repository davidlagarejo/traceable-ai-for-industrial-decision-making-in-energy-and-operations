from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from .._compat import dataclass
from ..domain.entities import (
    EvaluationRequestRecord,
    EvaluationScopeRecord,
    FitnessDimensionRecord,
    QualityDimensionRecord,
    ValidationRuleRecord,
)
from ..domain.records import (
    ContractConformanceCheckRecord,
    EvaluationDecisionRecord,
    EvaluationEvidenceRecord,
    EvaluationIssueRecord,
    EvaluationRationaleRecord,
    EvaluationReplayManifest,
    EvaluationRunRecord,
    EvaluationScorecardRecord,
    EvaluationSeverityRecord,
    FieldCheckResultRecord,
    FitnessCheckRecord,
    ObjectCheckResultRecord,
    TraceabilityCheckRecord,
)
from .check_validator import (
    validate_contract_conformance_check_record,
    validate_field_check_result_record,
    validate_fitness_check_record,
    validate_object_check_result_record,
    validate_traceability_check_record,
)
from .collector import ViolationCollector, ViolationDraft
from .context import ValidationContext
from .dimension_validator import (
    validate_fitness_dimension_record,
    validate_quality_dimension_record,
)
from .issue_validator import (
    validate_evaluation_evidence_record,
    validate_evaluation_issue_record,
    validate_evaluation_rationale_record,
    validate_evaluation_severity_record,
)
from .replay_validator import validate_evaluation_replay_manifest
from .request_validator import (
    validate_evaluation_request_record,
    validate_evaluation_scope_record,
)
from .result_validator import (
    validate_evaluation_decision_record,
    validate_evaluation_scorecard_record,
)
from .results import ValidationOutcome, ValidationReport, ValidationRun, ValidationViolation
from .rule_validator import validate_validation_rule_record
from .run_validator import validate_evaluation_run_record


DEFAULT_VALIDATOR_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    target_refs: tuple[str, ...]


class BasicQualityFitnessIntegrityValidator:
    def __init__(
        self,
        *,
        validator_version: str = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_evaluation_scope_record(
        self,
        evaluation_scope: EvaluationScopeRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_scope_ref(evaluation_scope))
        validate_evaluation_scope_record(evaluation_scope, collector, context=context)
        return self._build_report(ValidationArtifacts((_scope_ref(evaluation_scope),)), collector)

    def validate_evaluation_request_record(
        self,
        evaluation_request: EvaluationRequestRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_request_ref(evaluation_request))
        validate_evaluation_request_record(evaluation_request, collector, context=context)
        return self._build_report(ValidationArtifacts((_request_ref(evaluation_request),)), collector)

    def validate_quality_dimension_record(
        self,
        quality_dimension: QualityDimensionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_quality_dimension_ref(quality_dimension))
        validate_quality_dimension_record(quality_dimension, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_quality_dimension_ref(quality_dimension),)),
            collector,
        )

    def validate_fitness_dimension_record(
        self,
        fitness_dimension: FitnessDimensionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_fitness_dimension_ref(fitness_dimension))
        validate_fitness_dimension_record(fitness_dimension, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_fitness_dimension_ref(fitness_dimension),)),
            collector,
        )

    def validate_validation_rule_record(
        self,
        validation_rule: ValidationRuleRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_rule_ref(validation_rule))
        validate_validation_rule_record(validation_rule, collector, context=context)
        return self._build_report(ValidationArtifacts((_rule_ref(validation_rule),)), collector)

    def validate_object_check_result_record(
        self,
        object_check: ObjectCheckResultRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_object_check_ref(object_check))
        validate_object_check_result_record(object_check, collector, context=context)
        return self._build_report(ValidationArtifacts((_object_check_ref(object_check),)), collector)

    def validate_field_check_result_record(
        self,
        field_check: FieldCheckResultRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_field_check_ref(field_check))
        validate_field_check_result_record(field_check, collector, context=context)
        return self._build_report(ValidationArtifacts((_field_check_ref(field_check),)), collector)

    def validate_traceability_check_record(
        self,
        traceability_check: TraceabilityCheckRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_traceability_check_ref(traceability_check))
        validate_traceability_check_record(traceability_check, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_traceability_check_ref(traceability_check),)),
            collector,
        )

    def validate_contract_conformance_check_record(
        self,
        contract_check: ContractConformanceCheckRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_contract_check_ref(contract_check))
        validate_contract_conformance_check_record(contract_check, collector, context=context)
        return self._build_report(ValidationArtifacts((_contract_check_ref(contract_check),)), collector)

    def validate_fitness_check_record(
        self,
        fitness_check: FitnessCheckRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_fitness_check_ref(fitness_check))
        validate_fitness_check_record(fitness_check, collector, context=context)
        return self._build_report(ValidationArtifacts((_fitness_check_ref(fitness_check),)), collector)

    def validate_evaluation_issue_record(
        self,
        evaluation_issue: EvaluationIssueRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_issue_ref(evaluation_issue))
        validate_evaluation_issue_record(evaluation_issue, collector, context=context)
        return self._build_report(ValidationArtifacts((_issue_ref(evaluation_issue),)), collector)

    def validate_evaluation_severity_record(
        self,
        evaluation_severity: EvaluationSeverityRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_severity_ref(evaluation_severity))
        validate_evaluation_severity_record(evaluation_severity, collector, context=context)
        return self._build_report(ValidationArtifacts((_severity_ref(evaluation_severity),)), collector)

    def validate_evaluation_rationale_record(
        self,
        evaluation_rationale: EvaluationRationaleRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_rationale_ref(evaluation_rationale))
        validate_evaluation_rationale_record(evaluation_rationale, collector, context=context)
        return self._build_report(ValidationArtifacts((_rationale_ref(evaluation_rationale),)), collector)

    def validate_evaluation_evidence_record(
        self,
        evaluation_evidence: EvaluationEvidenceRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_evidence_ref(evaluation_evidence))
        validate_evaluation_evidence_record(evaluation_evidence, collector, context=context)
        return self._build_report(ValidationArtifacts((_evidence_ref(evaluation_evidence),)), collector)

    def validate_evaluation_scorecard_record(
        self,
        evaluation_scorecard: EvaluationScorecardRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_scorecard_ref(evaluation_scorecard))
        validate_evaluation_scorecard_record(evaluation_scorecard, collector, context=context)
        return self._build_report(ValidationArtifacts((_scorecard_ref(evaluation_scorecard),)), collector)

    def validate_evaluation_decision_record(
        self,
        evaluation_decision: EvaluationDecisionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_decision_ref(evaluation_decision))
        validate_evaluation_decision_record(evaluation_decision, collector, context=context)
        return self._build_report(ValidationArtifacts((_decision_ref(evaluation_decision),)), collector)

    def validate_evaluation_run_record(
        self,
        evaluation_run: EvaluationRunRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_run_ref(evaluation_run))
        validate_evaluation_run_record(evaluation_run, collector, context=context)
        return self._build_report(ValidationArtifacts((_run_ref(evaluation_run),)), collector)

    def validate_evaluation_replay_manifest(
        self,
        replay_manifest: EvaluationReplayManifest,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_replay_ref(replay_manifest))
        validate_evaluation_replay_manifest(replay_manifest, collector, context=context)
        return self._build_report(ValidationArtifacts((_replay_ref(replay_manifest),)), collector)

    def validate_graph(
        self,
        *,
        evaluation_scope_records: Iterable[EvaluationScopeRecord] = (),
        evaluation_request_records: Iterable[EvaluationRequestRecord] = (),
        quality_dimension_records: Iterable[QualityDimensionRecord] = (),
        fitness_dimension_records: Iterable[FitnessDimensionRecord] = (),
        validation_rule_records: Iterable[ValidationRuleRecord] = (),
        object_check_result_records: Iterable[ObjectCheckResultRecord] = (),
        field_check_result_records: Iterable[FieldCheckResultRecord] = (),
        traceability_check_records: Iterable[TraceabilityCheckRecord] = (),
        contract_conformance_check_records: Iterable[ContractConformanceCheckRecord] = (),
        fitness_check_records: Iterable[FitnessCheckRecord] = (),
        evaluation_issue_records: Iterable[EvaluationIssueRecord] = (),
        evaluation_severity_records: Iterable[EvaluationSeverityRecord] = (),
        evaluation_rationale_records: Iterable[EvaluationRationaleRecord] = (),
        evaluation_evidence_records: Iterable[EvaluationEvidenceRecord] = (),
        evaluation_scorecard_records: Iterable[EvaluationScorecardRecord] = (),
        evaluation_decision_records: Iterable[EvaluationDecisionRecord] = (),
        evaluation_run_records: Iterable[EvaluationRunRecord] = (),
        evaluation_replay_manifests: Iterable[EvaluationReplayManifest] = (),
    ) -> ValidationReport:
        evaluation_scope_records = tuple(evaluation_scope_records)
        evaluation_request_records = tuple(evaluation_request_records)
        quality_dimension_records = tuple(quality_dimension_records)
        fitness_dimension_records = tuple(fitness_dimension_records)
        validation_rule_records = tuple(validation_rule_records)
        object_check_result_records = tuple(object_check_result_records)
        field_check_result_records = tuple(field_check_result_records)
        traceability_check_records = tuple(traceability_check_records)
        contract_conformance_check_records = tuple(contract_conformance_check_records)
        fitness_check_records = tuple(fitness_check_records)
        evaluation_issue_records = tuple(evaluation_issue_records)
        evaluation_severity_records = tuple(evaluation_severity_records)
        evaluation_rationale_records = tuple(evaluation_rationale_records)
        evaluation_evidence_records = tuple(evaluation_evidence_records)
        evaluation_scorecard_records = tuple(evaluation_scorecard_records)
        evaluation_decision_records = tuple(evaluation_decision_records)
        evaluation_run_records = tuple(evaluation_run_records)
        evaluation_replay_manifests = tuple(evaluation_replay_manifests)

        context = ValidationContext.from_iterables(
            evaluation_scope_records=evaluation_scope_records,
            evaluation_request_records=evaluation_request_records,
            quality_dimension_records=quality_dimension_records,
            fitness_dimension_records=fitness_dimension_records,
            validation_rule_records=validation_rule_records,
            object_check_result_records=object_check_result_records,
            field_check_result_records=field_check_result_records,
            traceability_check_records=traceability_check_records,
            contract_conformance_check_records=contract_conformance_check_records,
            fitness_check_records=fitness_check_records,
            evaluation_issue_records=evaluation_issue_records,
            evaluation_severity_records=evaluation_severity_records,
            evaluation_rationale_records=evaluation_rationale_records,
            evaluation_evidence_records=evaluation_evidence_records,
            evaluation_scorecard_records=evaluation_scorecard_records,
            evaluation_decision_records=evaluation_decision_records,
            evaluation_run_records=evaluation_run_records,
            evaluation_replay_manifests=evaluation_replay_manifests,
        )
        collector = ViolationCollector("graph:quality_fitness_evaluation")

        for item in evaluation_scope_records:
            local = ViolationCollector(_scope_ref(item))
            validate_evaluation_scope_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_request_records:
            local = ViolationCollector(_request_ref(item))
            validate_evaluation_request_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in quality_dimension_records:
            local = ViolationCollector(_quality_dimension_ref(item))
            validate_quality_dimension_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in fitness_dimension_records:
            local = ViolationCollector(_fitness_dimension_ref(item))
            validate_fitness_dimension_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in validation_rule_records:
            local = ViolationCollector(_rule_ref(item))
            validate_validation_rule_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in object_check_result_records:
            local = ViolationCollector(_object_check_ref(item))
            validate_object_check_result_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in field_check_result_records:
            local = ViolationCollector(_field_check_ref(item))
            validate_field_check_result_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in traceability_check_records:
            local = ViolationCollector(_traceability_check_ref(item))
            validate_traceability_check_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in contract_conformance_check_records:
            local = ViolationCollector(_contract_check_ref(item))
            validate_contract_conformance_check_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in fitness_check_records:
            local = ViolationCollector(_fitness_check_ref(item))
            validate_fitness_check_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_severity_records:
            local = ViolationCollector(_severity_ref(item))
            validate_evaluation_severity_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_rationale_records:
            local = ViolationCollector(_rationale_ref(item))
            validate_evaluation_rationale_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_evidence_records:
            local = ViolationCollector(_evidence_ref(item))
            validate_evaluation_evidence_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_issue_records:
            local = ViolationCollector(_issue_ref(item))
            validate_evaluation_issue_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_scorecard_records:
            local = ViolationCollector(_scorecard_ref(item))
            validate_evaluation_scorecard_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_decision_records:
            local = ViolationCollector(_decision_ref(item))
            validate_evaluation_decision_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_run_records:
            local = ViolationCollector(_run_ref(item))
            validate_evaluation_run_record(item, local, context=context)
            _merge_collector(collector, local)
        for item in evaluation_replay_manifests:
            local = ViolationCollector(_replay_ref(item))
            validate_evaluation_replay_manifest(item, local, context=context)
            _merge_collector(collector, local)

        target_refs = tuple(
            _unique_ordered(
                [
                    *(_scope_ref(item) for item in evaluation_scope_records),
                    *(_request_ref(item) for item in evaluation_request_records),
                    *(_quality_dimension_ref(item) for item in quality_dimension_records),
                    *(_fitness_dimension_ref(item) for item in fitness_dimension_records),
                    *(_rule_ref(item) for item in validation_rule_records),
                    *(_object_check_ref(item) for item in object_check_result_records),
                    *(_field_check_ref(item) for item in field_check_result_records),
                    *(_traceability_check_ref(item) for item in traceability_check_records),
                    *(_contract_check_ref(item) for item in contract_conformance_check_records),
                    *(_fitness_check_ref(item) for item in fitness_check_records),
                    *(_severity_ref(item) for item in evaluation_severity_records),
                    *(_rationale_ref(item) for item in evaluation_rationale_records),
                    *(_evidence_ref(item) for item in evaluation_evidence_records),
                    *(_issue_ref(item) for item in evaluation_issue_records),
                    *(_scorecard_ref(item) for item in evaluation_scorecard_records),
                    *(_decision_ref(item) for item in evaluation_decision_records),
                    *(_run_ref(item) for item in evaluation_run_records),
                    *(_replay_ref(item) for item in evaluation_replay_manifests),
                ]
            )
        ) or ("graph:quality_fitness_evaluation",)
        return self._build_report(ValidationArtifacts(target_refs), collector)

    def _build_report(
        self,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        run_id = _stable_id(
            "quality_fitness_validation",
            self._validator_version,
            outcome.value,
            *artifacts.target_refs,
            *(_draft_signature(item) for item in collector.violations),
        )
        violations = tuple(
            ValidationViolation(
                violation_id=_stable_id(
                    "quality_fitness_violation",
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



def validate_quality_fitness_graph(**kwargs: object) -> ValidationReport:
    return BasicQualityFitnessIntegrityValidator().validate_graph(**kwargs)



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



def _scope_ref(evaluation_scope: EvaluationScopeRecord) -> str:
    return f"evaluation_scope:{evaluation_scope.evaluation_scope_record_id}"



def _request_ref(evaluation_request: EvaluationRequestRecord) -> str:
    return f"evaluation_request:{evaluation_request.evaluation_request_record_id}"



def _quality_dimension_ref(quality_dimension: QualityDimensionRecord) -> str:
    return f"quality_dimension:{quality_dimension.quality_dimension_record_id}"



def _fitness_dimension_ref(fitness_dimension: FitnessDimensionRecord) -> str:
    return f"fitness_dimension:{fitness_dimension.fitness_dimension_record_id}"



def _rule_ref(validation_rule: ValidationRuleRecord) -> str:
    return f"validation_rule:{validation_rule.validation_rule_record_id}"



def _object_check_ref(object_check: ObjectCheckResultRecord) -> str:
    return f"object_check:{object_check.object_check_result_record_id}"



def _field_check_ref(field_check: FieldCheckResultRecord) -> str:
    return f"field_check:{field_check.field_check_result_record_id}"



def _traceability_check_ref(traceability_check: TraceabilityCheckRecord) -> str:
    return f"traceability_check:{traceability_check.traceability_check_record_id}"



def _contract_check_ref(contract_check: ContractConformanceCheckRecord) -> str:
    return f"contract_check:{contract_check.contract_conformance_check_record_id}"



def _fitness_check_ref(fitness_check: FitnessCheckRecord) -> str:
    return f"fitness_check:{fitness_check.fitness_check_record_id}"



def _severity_ref(evaluation_severity: EvaluationSeverityRecord) -> str:
    return f"evaluation_severity:{evaluation_severity.evaluation_severity_record_id}"



def _rationale_ref(evaluation_rationale: EvaluationRationaleRecord) -> str:
    return f"evaluation_rationale:{evaluation_rationale.evaluation_rationale_record_id}"



def _evidence_ref(evaluation_evidence: EvaluationEvidenceRecord) -> str:
    return f"evaluation_evidence:{evaluation_evidence.evaluation_evidence_record_id}"



def _issue_ref(evaluation_issue: EvaluationIssueRecord) -> str:
    return f"evaluation_issue:{evaluation_issue.evaluation_issue_record_id}"



def _scorecard_ref(evaluation_scorecard: EvaluationScorecardRecord) -> str:
    return f"evaluation_scorecard:{evaluation_scorecard.evaluation_scorecard_record_id}"



def _decision_ref(evaluation_decision: EvaluationDecisionRecord) -> str:
    return f"evaluation_decision:{evaluation_decision.evaluation_decision_record_id}"



def _run_ref(evaluation_run: EvaluationRunRecord) -> str:
    return f"evaluation_run:{evaluation_run.evaluation_run_record_id}"



def _replay_ref(replay_manifest: EvaluationReplayManifest) -> str:
    return f"evaluation_replay_manifest:{replay_manifest.evaluation_replay_manifest_id}"



def _unique_ordered(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
