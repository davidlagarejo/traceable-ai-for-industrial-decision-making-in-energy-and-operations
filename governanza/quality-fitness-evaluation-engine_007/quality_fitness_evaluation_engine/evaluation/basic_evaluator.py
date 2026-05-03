from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone

from .decision import build_decision, build_scorecard
from .inputs import (
    ContractRuleSpec,
    EvaluableObjectSnapshot,
    FitnessRuleSpec,
    StructuralRuleSpec,
    TraceabilityRuleSpec,
)
from .replay import build_replay_manifest
from .results import (
    BasicEvaluationResult,
    IssueDraft,
    RuleExecutionDraft,
    RuleExecutionKind,
    stable_id,
)
from .rules import (
    apply_contract_rules,
    apply_fitness_rules,
    apply_structural_rules,
    apply_traceability_rules,
)
from ..domain.entities import (
    EvaluationRequestRecord,
    EvaluationScopeRecord,
    FitnessDimensionRecord,
    QualityDimensionRecord,
    ValidationRuleRecord,
)
from ..domain.enums import EvaluationStatus, SeverityLevel
from ..domain.records import (
    ContractConformanceCheckRecord,
    EvaluationEvidenceRecord,
    EvaluationIssueRecord,
    EvaluationRationaleRecord,
    EvaluationRunRecord,
    EvaluationSeverityRecord,
    FieldCheckResultRecord,
    FitnessCheckRecord,
    ObjectCheckResultRecord,
    TraceabilityCheckRecord,
)
from ..domain.value_objects import (
    ContractConformanceCheckRecordId,
    EvaluationEvidenceRecordId,
    EvaluationIssueRecordId,
    EvaluationRationaleRecordId,
    EvaluationRunRecordId,
    EvaluationSeverityRecordId,
    EvidenceRef,
    EvidenceSummary,
    EvaluatorVersion,
    FieldCheckResultRecordId,
    FitnessCheckRecordId,
    ObjectCheckResultRecordId,
    RationaleText,
    TraceabilityCheckRecordId,
)


DEFAULT_EVALUATOR_VERSION = "0.1.0"
DEFAULT_SCORE_FORMULA_VERSION = "basic-scorecard:min-dimension-v1"


class BasicEvaluator:
    def __init__(
        self,
        *,
        evaluator_version: str = DEFAULT_EVALUATOR_VERSION,
        score_formula_version: str = DEFAULT_SCORE_FORMULA_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._evaluator_version = evaluator_version.strip()
        self._score_formula_version = score_formula_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def evaluate(
        self,
        *,
        evaluation_scope_record: EvaluationScopeRecord,
        evaluation_request_record: EvaluationRequestRecord,
        subject: EvaluableObjectSnapshot,
        quality_dimension_records: Iterable[QualityDimensionRecord],
        fitness_dimension_records: Iterable[FitnessDimensionRecord],
        validation_rule_records: Iterable[ValidationRuleRecord],
        structural_rule_specs: Iterable[StructuralRuleSpec] = (),
        traceability_rule_specs: Iterable[TraceabilityRuleSpec] = (),
        contract_rule_specs: Iterable[ContractRuleSpec] = (),
        fitness_rule_specs: Iterable[FitnessRuleSpec] = (),
    ) -> BasicEvaluationResult:
        quality_dimension_records = tuple(quality_dimension_records)
        fitness_dimension_records = tuple(fitness_dimension_records)
        validation_rule_records = tuple(validation_rule_records)
        structural_rule_specs = tuple(structural_rule_specs)
        traceability_rule_specs = tuple(traceability_rule_specs)
        contract_rule_specs = tuple(contract_rule_specs)
        fitness_rule_specs = tuple(fitness_rule_specs)

        _validate_request_scope_subject(
            evaluation_scope_record=evaluation_scope_record,
            evaluation_request_record=evaluation_request_record,
            subject=subject,
        )
        rule_lookup = {item.validation_rule_record_id: item for item in validation_rule_records}
        quality_lookup = {item.quality_dimension_record_id: item for item in quality_dimension_records}
        fitness_lookup = {item.fitness_dimension_record_id: item for item in fitness_dimension_records}
        _validate_rule_specs(
            structural_rule_specs=structural_rule_specs,
            traceability_rule_specs=traceability_rule_specs,
            contract_rule_specs=contract_rule_specs,
            fitness_rule_specs=fitness_rule_specs,
            rule_lookup=rule_lookup,
            quality_lookup=quality_lookup,
            fitness_lookup=fitness_lookup,
        )

        applied_rule_ids = _collect_applied_rule_ids(
            structural_rule_specs=structural_rule_specs,
            traceability_rule_specs=traceability_rule_specs,
            contract_rule_specs=contract_rule_specs,
            fitness_rule_specs=fitness_rule_specs,
        )
        executed_at = self._clock()
        evaluation_run_record_id = EvaluationRunRecordId(
            stable_id(
                "evaluation_run",
                evaluation_request_record.evaluation_request_record_id.value,
                evaluation_scope_record.evaluation_scope_record_id.value,
                subject.evaluated_object_ref.value,
                subject.evaluated_object_version_ref.value if subject.evaluated_object_version_ref is not None else "noversion",
                *(item.value for item in applied_rule_ids),
            )
        )

        execution_drafts = (
            *apply_structural_rules(
                subject=subject,
                rule_specs=structural_rule_specs,
                rule_lookup=rule_lookup,
            ),
            *apply_traceability_rules(
                subject=subject,
                rule_specs=traceability_rule_specs,
                rule_lookup=rule_lookup,
            ),
            *apply_contract_rules(
                subject=subject,
                rule_specs=contract_rule_specs,
                rule_lookup=rule_lookup,
            ),
            *apply_fitness_rules(
                subject=subject,
                rule_specs=fitness_rule_specs,
                rule_lookup=rule_lookup,
            ),
        )

        severity_records = _build_severity_records(created_at=executed_at)
        severity_lookup = {
            item.severity_level: item
            for item in severity_records
        }
        rationale_records: dict[str, EvaluationRationaleRecord] = {}
        evidence_records: dict[str, EvaluationEvidenceRecord] = {}
        issue_records: list[EvaluationIssueRecord] = []
        execution_issue_ids: dict[int, tuple[EvaluationIssueRecordId, ...]] = {}

        for execution_index, execution_draft in enumerate(execution_drafts, start=1):
            issue_ids: list[EvaluationIssueRecordId] = []
            for issue_index, issue_draft in enumerate(execution_draft.issue_drafts, start=1):
                rationale_record = _build_issue_rationale_record(
                    evaluation_run_record_id=evaluation_run_record_id,
                    execution_index=execution_index,
                    issue_index=issue_index,
                    issue_draft=issue_draft,
                    created_at=executed_at,
                )
                rationale_records[rationale_record.evaluation_rationale_record_id.value] = rationale_record
                evidence_record = _build_issue_evidence_record(
                    evaluation_run_record_id=evaluation_run_record_id,
                    execution_index=execution_index,
                    issue_index=issue_index,
                    issue_draft=issue_draft,
                    created_at=executed_at,
                )
                evidence_records[evidence_record.evaluation_evidence_record_id.value] = evidence_record
                severity_record = severity_lookup[issue_draft.severity_level]
                issue_record = EvaluationIssueRecord(
                    evaluation_issue_record_id=EvaluationIssueRecordId(
                        stable_id(
                            "evaluation_issue",
                            evaluation_run_record_id.value,
                            str(execution_index),
                            str(issue_index),
                            execution_draft.validation_rule_record_id.value,
                            issue_draft.issue_type.value,
                            issue_draft.message,
                            issue_draft.field_path_ref.value if issue_draft.field_path_ref is not None else "nofield",
                        )
                    ),
                    issue_type=issue_draft.issue_type,
                    evaluation_severity_record_id=severity_record.evaluation_severity_record_id,
                    evaluation_rationale_record_id=rationale_record.evaluation_rationale_record_id,
                    evidence_record_ids=(evidence_record.evaluation_evidence_record_id,),
                    evaluated_object_ref=subject.evaluated_object_ref,
                    field_path_ref=issue_draft.field_path_ref,
                    message=issue_draft.message,
                    created_at=executed_at,
                )
                issue_records.append(issue_record)
                issue_ids.append(issue_record.evaluation_issue_record_id)
            execution_issue_ids[execution_index] = tuple(issue_ids)

        object_checks: list[ObjectCheckResultRecord] = []
        field_checks: list[FieldCheckResultRecord] = []
        traceability_checks: list[TraceabilityCheckRecord] = []
        contract_checks: list[ContractConformanceCheckRecord] = []
        fitness_checks: list[FitnessCheckRecord] = []

        for execution_index, execution_draft in enumerate(execution_drafts, start=1):
            rule = rule_lookup[execution_draft.validation_rule_record_id]
            issue_record_ids = execution_issue_ids[execution_index]
            if execution_draft.execution_kind is RuleExecutionKind.OBJECT:
                object_checks.append(
                    ObjectCheckResultRecord(
                        object_check_result_record_id=ObjectCheckResultRecordId(
                            stable_id(
                                "object_check",
                                evaluation_run_record_id.value,
                                execution_draft.validation_rule_record_id.value,
                                str(execution_index),
                            )
                        ),
                        evaluated_object_ref=subject.evaluated_object_ref,
                        evaluated_object_version_ref=subject.evaluated_object_version_ref,
                        validation_rule_record_id=rule.validation_rule_record_id,
                        quality_dimension_record_id=rule.quality_dimension_record_id,
                        result_class=execution_draft.result_class,
                        issue_record_ids=issue_record_ids,
                        created_at=executed_at,
                    )
                )
            elif execution_draft.execution_kind is RuleExecutionKind.FIELD:
                field_checks.append(
                    FieldCheckResultRecord(
                        field_check_result_record_id=FieldCheckResultRecordId(
                            stable_id(
                                "field_check",
                                evaluation_run_record_id.value,
                                execution_draft.validation_rule_record_id.value,
                                execution_draft.field_path_ref.value,
                            )
                        ),
                        evaluated_object_ref=subject.evaluated_object_ref,
                        field_path_ref=execution_draft.field_path_ref,
                        validation_rule_record_id=rule.validation_rule_record_id,
                        quality_dimension_record_id=rule.quality_dimension_record_id,
                        result_class=execution_draft.result_class,
                        issue_record_ids=issue_record_ids,
                        created_at=executed_at,
                    )
                )
            elif execution_draft.execution_kind is RuleExecutionKind.TRACEABILITY:
                traceability_checks.append(
                    TraceabilityCheckRecord(
                        traceability_check_record_id=TraceabilityCheckRecordId(
                            stable_id(
                                "traceability_check",
                                evaluation_run_record_id.value,
                                execution_draft.validation_rule_record_id.value,
                                execution_draft.traceability_aspect.value,
                            )
                        ),
                        evaluated_object_ref=subject.evaluated_object_ref,
                        validation_rule_record_id=rule.validation_rule_record_id,
                        traceability_aspect=execution_draft.traceability_aspect,
                        result_class=execution_draft.result_class,
                        issue_record_ids=issue_record_ids,
                        created_at=executed_at,
                    )
                )
            elif execution_draft.execution_kind is RuleExecutionKind.CONTRACT:
                contract_checks.append(
                    ContractConformanceCheckRecord(
                        contract_conformance_check_record_id=ContractConformanceCheckRecordId(
                            stable_id(
                                "contract_check",
                                evaluation_run_record_id.value,
                                execution_draft.validation_rule_record_id.value,
                                execution_draft.contract_ref.value,
                            )
                        ),
                        evaluated_object_ref=subject.evaluated_object_ref,
                        validation_rule_record_id=rule.validation_rule_record_id,
                        contract_ref=execution_draft.contract_ref,
                        contract_version_ref=execution_draft.contract_version_ref,
                        result_class=execution_draft.result_class,
                        issue_record_ids=issue_record_ids,
                        created_at=executed_at,
                    )
                )
            else:
                fitness_checks.append(
                    FitnessCheckRecord(
                        fitness_check_record_id=FitnessCheckRecordId(
                            stable_id(
                                "fitness_check",
                                evaluation_run_record_id.value,
                                execution_draft.validation_rule_record_id.value,
                                execution_draft.fitness_target.value,
                            )
                        ),
                        evaluated_object_ref=subject.evaluated_object_ref,
                        validation_rule_record_id=rule.validation_rule_record_id,
                        evaluation_scope_record_id=evaluation_scope_record.evaluation_scope_record_id,
                        fitness_dimension_record_id=rule.fitness_dimension_record_id,
                        fitness_target=execution_draft.fitness_target,
                        result_class=execution_draft.result_class,
                        issue_record_ids=issue_record_ids,
                        created_at=executed_at,
                    )
                )

        issue_summary, decision_rationale_record, decision_record = build_decision(
            evaluation_run_record_id=evaluation_run_record_id,
            evaluation_issue_records=tuple(issue_records),
            evaluation_severity_records=severity_records,
            created_at=executed_at,
        )
        rationale_records[decision_rationale_record.evaluation_rationale_record_id.value] = decision_rationale_record

        scorecard_record = build_scorecard(
            evaluation_run_record_id=evaluation_run_record_id,
            evaluation_scope_record_id=evaluation_scope_record.evaluation_scope_record_id,
            evaluated_object_ref=subject.evaluated_object_ref,
            object_check_result_records=tuple(object_checks),
            field_check_result_records=tuple(field_checks),
            traceability_check_records=tuple(traceability_checks),
            contract_conformance_check_records=tuple(contract_checks),
            fitness_check_records=tuple(fitness_checks),
            score_formula_version=self._score_formula_version,
            created_at=executed_at,
        )

        run_record = EvaluationRunRecord(
            evaluation_run_record_id=evaluation_run_record_id,
            evaluation_request_record_id=evaluation_request_record.evaluation_request_record_id,
            evaluation_scope_record_id=evaluation_scope_record.evaluation_scope_record_id,
            evaluation_status=EvaluationStatus.COMPLETED,
            validation_rule_record_ids=applied_rule_ids,
            object_check_result_record_ids=tuple(item.object_check_result_record_id for item in object_checks),
            field_check_result_record_ids=tuple(item.field_check_result_record_id for item in field_checks),
            traceability_check_record_ids=tuple(item.traceability_check_record_id for item in traceability_checks),
            contract_conformance_check_record_ids=tuple(
                item.contract_conformance_check_record_id for item in contract_checks
            ),
            fitness_check_record_ids=tuple(item.fitness_check_record_id for item in fitness_checks),
            evaluation_issue_record_ids=tuple(item.evaluation_issue_record_id for item in issue_records),
            evaluation_decision_record_id=decision_record.evaluation_decision_record_id,
            evaluation_scorecard_record_id=scorecard_record.evaluation_scorecard_record_id,
            evaluator_version=EvaluatorVersion(self._evaluator_version),
            started_at=executed_at,
            completed_at=executed_at,
        )
        replay_manifest = build_replay_manifest(
            evaluation_run_record_id=evaluation_run_record_id,
            evaluation_request_record=evaluation_request_record,
            evaluation_scope_record=evaluation_scope_record,
            subject=subject,
            validation_rule_record_ids=applied_rule_ids,
            evaluator_version=self._evaluator_version,
            contract_version_ref=_first_contract_version_ref(contract_checks),
            created_at=executed_at,
        )

        return BasicEvaluationResult(
            evaluation_scope_record=evaluation_scope_record,
            evaluation_request_record=evaluation_request_record,
            quality_dimension_records=quality_dimension_records,
            fitness_dimension_records=fitness_dimension_records,
            validation_rule_records=tuple(rule_lookup[item] for item in applied_rule_ids),
            object_check_result_records=tuple(object_checks),
            field_check_result_records=tuple(field_checks),
            traceability_check_records=tuple(traceability_checks),
            contract_conformance_check_records=tuple(contract_checks),
            fitness_check_records=tuple(fitness_checks),
            evaluation_issue_records=tuple(issue_records),
            evaluation_severity_records=severity_records,
            evaluation_rationale_records=tuple(rationale_records.values()),
            evaluation_evidence_records=tuple(evidence_records.values()),
            evaluation_scorecard_record=scorecard_record,
            evaluation_decision_record=decision_record,
            evaluation_run_record=run_record,
            evaluation_replay_manifest=replay_manifest,
            executed_at=executed_at,
        )

    def re_evaluate(
        self,
        *,
        replay_manifest,
        evaluation_scope_record: EvaluationScopeRecord,
        evaluation_request_record: EvaluationRequestRecord,
        subject: EvaluableObjectSnapshot,
        quality_dimension_records: Iterable[QualityDimensionRecord],
        fitness_dimension_records: Iterable[FitnessDimensionRecord],
        validation_rule_records: Iterable[ValidationRuleRecord],
        structural_rule_specs: Iterable[StructuralRuleSpec] = (),
        traceability_rule_specs: Iterable[TraceabilityRuleSpec] = (),
        contract_rule_specs: Iterable[ContractRuleSpec] = (),
        fitness_rule_specs: Iterable[FitnessRuleSpec] = (),
    ) -> BasicEvaluationResult:
        if replay_manifest.evaluation_request_record_id != evaluation_request_record.evaluation_request_record_id:
            raise ValueError("Replay manifest request reference does not match the provided request.")
        if replay_manifest.evaluation_scope_record_id != evaluation_scope_record.evaluation_scope_record_id:
            raise ValueError("Replay manifest scope reference does not match the provided scope.")
        if subject.evaluated_object_ref not in replay_manifest.evaluated_object_refs:
            raise ValueError("Replay manifest does not include the provided object reference.")
        if replay_manifest.evaluated_object_version_refs:
            if subject.evaluated_object_version_ref not in replay_manifest.evaluated_object_version_refs:
                raise ValueError("Replay manifest does not include the provided object version reference.")
        applied_rule_ids = _collect_applied_rule_ids(
            structural_rule_specs=tuple(structural_rule_specs),
            traceability_rule_specs=tuple(traceability_rule_specs),
            contract_rule_specs=tuple(contract_rule_specs),
            fitness_rule_specs=tuple(fitness_rule_specs),
        )
        if tuple(replay_manifest.validation_rule_record_ids) != applied_rule_ids:
            raise ValueError("Replay manifest rule ids do not match the provided evaluation rules.")
        return self.evaluate(
            evaluation_scope_record=evaluation_scope_record,
            evaluation_request_record=evaluation_request_record,
            subject=subject,
            quality_dimension_records=quality_dimension_records,
            fitness_dimension_records=fitness_dimension_records,
            validation_rule_records=validation_rule_records,
            structural_rule_specs=structural_rule_specs,
            traceability_rule_specs=traceability_rule_specs,
            contract_rule_specs=contract_rule_specs,
            fitness_rule_specs=fitness_rule_specs,
        )



def _validate_request_scope_subject(
    *,
    evaluation_scope_record: EvaluationScopeRecord,
    evaluation_request_record: EvaluationRequestRecord,
    subject: EvaluableObjectSnapshot,
) -> None:
    if evaluation_request_record.evaluation_scope_record_id != evaluation_scope_record.evaluation_scope_record_id:
        raise ValueError("Evaluation request scope does not match the provided evaluation scope.")
    if subject.evaluated_object_ref not in evaluation_request_record.evaluated_object_refs:
        raise ValueError("Evaluated object is not registered in the evaluation request.")
    if (
        evaluation_request_record.evaluated_object_version_refs
        and subject.evaluated_object_version_ref not in evaluation_request_record.evaluated_object_version_refs
    ):
        raise ValueError("Evaluated object version is not registered in the evaluation request.")



def _validate_rule_specs(
    *,
    structural_rule_specs: tuple[StructuralRuleSpec, ...],
    traceability_rule_specs: tuple[TraceabilityRuleSpec, ...],
    contract_rule_specs: tuple[ContractRuleSpec, ...],
    fitness_rule_specs: tuple[FitnessRuleSpec, ...],
    rule_lookup: dict,
    quality_lookup: dict,
    fitness_lookup: dict,
) -> None:
    for spec in (*structural_rule_specs, *traceability_rule_specs, *contract_rule_specs):
        rule = rule_lookup.get(spec.validation_rule_record_id)
        if rule is None:
            raise ValueError(f"Unknown quality rule: {spec.validation_rule_record_id}.")
        if rule.quality_dimension_record_id is None:
            raise ValueError(f"Rule is not a quality rule: {spec.validation_rule_record_id}.")
        if rule.quality_dimension_record_id not in quality_lookup:
            raise ValueError(
                f"Missing quality dimension for rule {spec.validation_rule_record_id}."
            )
    for spec in fitness_rule_specs:
        rule = rule_lookup.get(spec.validation_rule_record_id)
        if rule is None:
            raise ValueError(f"Unknown fitness rule: {spec.validation_rule_record_id}.")
        if rule.fitness_dimension_record_id is None:
            raise ValueError(f"Rule is not a fitness rule: {spec.validation_rule_record_id}.")
        if rule.fitness_dimension_record_id not in fitness_lookup:
            raise ValueError(
                f"Missing fitness dimension for rule {spec.validation_rule_record_id}."
            )



def _collect_applied_rule_ids(
    *,
    structural_rule_specs: tuple[StructuralRuleSpec, ...],
    traceability_rule_specs: tuple[TraceabilityRuleSpec, ...],
    contract_rule_specs: tuple[ContractRuleSpec, ...],
    fitness_rule_specs: tuple[FitnessRuleSpec, ...],
):
    ordered = []
    seen = set()
    for spec in (
        *structural_rule_specs,
        *traceability_rule_specs,
        *contract_rule_specs,
        *fitness_rule_specs,
    ):
        if spec.validation_rule_record_id in seen:
            continue
        seen.add(spec.validation_rule_record_id)
        ordered.append(spec.validation_rule_record_id)
    if not ordered:
        raise ValueError("BasicEvaluator requires at least one explicit evaluation rule.")
    return tuple(ordered)



def _build_severity_records(*, created_at: datetime) -> tuple[EvaluationSeverityRecord, ...]:
    return (
        EvaluationSeverityRecord(
            evaluation_severity_record_id=EvaluationSeverityRecordId("evaluation_severity:warning"),
            severity_level=SeverityLevel.WARNING,
            blocks_progression=False,
            created_at=created_at,
        ),
        EvaluationSeverityRecord(
            evaluation_severity_record_id=EvaluationSeverityRecordId("evaluation_severity:error"),
            severity_level=SeverityLevel.ERROR,
            blocks_progression=False,
            created_at=created_at,
        ),
        EvaluationSeverityRecord(
            evaluation_severity_record_id=EvaluationSeverityRecordId("evaluation_severity:block"),
            severity_level=SeverityLevel.BLOCK,
            blocks_progression=True,
            created_at=created_at,
        ),
    )



def _build_issue_rationale_record(
    *,
    evaluation_run_record_id,
    execution_index: int,
    issue_index: int,
    issue_draft: IssueDraft,
    created_at: datetime,
) -> EvaluationRationaleRecord:
    return EvaluationRationaleRecord(
        evaluation_rationale_record_id=EvaluationRationaleRecordId(
            stable_id(
                "evaluation_issue_rationale",
                evaluation_run_record_id.value,
                str(execution_index),
                str(issue_index),
                issue_draft.rationale_text,
            )
        ),
        rationale_text=RationaleText(issue_draft.rationale_text),
        created_at=created_at,
    )



def _build_issue_evidence_record(
    *,
    evaluation_run_record_id,
    execution_index: int,
    issue_index: int,
    issue_draft: IssueDraft,
    created_at: datetime,
) -> EvaluationEvidenceRecord:
    return EvaluationEvidenceRecord(
        evaluation_evidence_record_id=EvaluationEvidenceRecordId(
            stable_id(
                "evaluation_issue_evidence",
                evaluation_run_record_id.value,
                str(execution_index),
                str(issue_index),
                issue_draft.evidence_ref,
            )
        ),
        evidence_ref=EvidenceRef(issue_draft.evidence_ref),
        evidence_summary=EvidenceSummary(issue_draft.evidence_summary),
        created_at=created_at,
    )



def _first_contract_version_ref(
    contract_checks: list[ContractConformanceCheckRecord],
):
    for item in contract_checks:
        if item.contract_version_ref is not None:
            return item.contract_version_ref
    return None
