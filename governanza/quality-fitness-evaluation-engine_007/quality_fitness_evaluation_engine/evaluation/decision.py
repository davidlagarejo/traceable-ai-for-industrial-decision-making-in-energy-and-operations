from __future__ import annotations

from collections import Counter
from datetime import datetime
from decimal import Decimal

from .._compat import dataclass
from ..domain.enums import CheckResultClass, DecisionStatus, IssueType, SeverityLevel
from ..domain.records import (
    ContractConformanceCheckRecord,
    EvaluationDecisionRecord,
    EvaluationIssueRecord,
    EvaluationRationaleRecord,
    EvaluationScorecardRecord,
    EvaluationSeverityRecord,
    FieldCheckResultRecord,
    FitnessCheckRecord,
    ObjectCheckResultRecord,
    TraceabilityCheckRecord,
)
from ..domain.value_objects import (
    EvaluationDecisionRecordId,
    EvaluationRationaleRecordId,
    EvaluationScorecardRecordId,
    ScoreFormulaVersion,
)
from .results import score_for_result_class, stable_id


@dataclass(frozen=True, slots=True)
class IssueSummary:
    warning_issue_count: int
    error_issue_count: int
    blocking_issue_count: int
    issue_type_counts: tuple[tuple[IssueType, int], ...]



def classify_issues(
    *,
    evaluation_issue_records: tuple[EvaluationIssueRecord, ...],
    evaluation_severity_records: tuple[EvaluationSeverityRecord, ...],
) -> IssueSummary:
    severity_lookup = {
        item.evaluation_severity_record_id: item.severity_level
        for item in evaluation_severity_records
    }
    issue_type_counter: Counter[IssueType] = Counter()
    warning_issue_count = 0
    error_issue_count = 0
    blocking_issue_count = 0
    for issue_record in evaluation_issue_records:
        issue_type_counter[issue_record.issue_type] += 1
        severity_level = severity_lookup[issue_record.evaluation_severity_record_id]
        if severity_level is SeverityLevel.WARNING:
            warning_issue_count += 1
        elif severity_level is SeverityLevel.ERROR:
            error_issue_count += 1
        else:
            blocking_issue_count += 1
    return IssueSummary(
        warning_issue_count=warning_issue_count,
        error_issue_count=error_issue_count,
        blocking_issue_count=blocking_issue_count,
        issue_type_counts=tuple(sorted(issue_type_counter.items(), key=lambda item: item[0].value)),
    )



def build_decision(
    *,
    evaluation_run_record_id,
    evaluation_issue_records: tuple[EvaluationIssueRecord, ...],
    evaluation_severity_records: tuple[EvaluationSeverityRecord, ...],
    created_at: datetime,
) -> tuple[IssueSummary, EvaluationRationaleRecord, EvaluationDecisionRecord]:
    issue_summary = classify_issues(
        evaluation_issue_records=evaluation_issue_records,
        evaluation_severity_records=evaluation_severity_records,
    )
    decision_status = _derive_decision_status(issue_summary)
    rationale_text = _build_rationale_text(decision_status, issue_summary)
    rationale_record = EvaluationRationaleRecord(
        evaluation_rationale_record_id=EvaluationRationaleRecordId(
            stable_id(
                "evaluation_decision_rationale",
                evaluation_run_record_id.value,
                decision_status.value,
                rationale_text,
            )
        ),
        rationale_text=rationale_text,
        created_at=created_at,
    )
    decision_record = EvaluationDecisionRecord(
        evaluation_decision_record_id=EvaluationDecisionRecordId(
            stable_id(
                "evaluation_decision",
                evaluation_run_record_id.value,
                decision_status.value,
                *(item.evaluation_issue_record_id.value for item in evaluation_issue_records),
            )
        ),
        evaluation_run_record_id=evaluation_run_record_id,
        decision_status=decision_status,
        issue_record_ids=tuple(item.evaluation_issue_record_id for item in evaluation_issue_records),
        warning_issue_count=issue_summary.warning_issue_count,
        error_issue_count=issue_summary.error_issue_count,
        blocking_issue_count=issue_summary.blocking_issue_count,
        evaluation_rationale_record_id=rationale_record.evaluation_rationale_record_id,
        created_at=created_at,
    )
    return issue_summary, rationale_record, decision_record



def build_scorecard(
    *,
    evaluation_run_record_id,
    evaluation_scope_record_id,
    evaluated_object_ref,
    object_check_result_records: tuple[ObjectCheckResultRecord, ...],
    field_check_result_records: tuple[FieldCheckResultRecord, ...],
    traceability_check_records: tuple[TraceabilityCheckRecord, ...],
    contract_conformance_check_records: tuple[ContractConformanceCheckRecord, ...],
    fitness_check_records: tuple[FitnessCheckRecord, ...],
    score_formula_version: str,
    created_at: datetime,
) -> EvaluationScorecardRecord:
    structural_score = _score_average(
        [
            *(item.result_class for item in object_check_result_records),
            *(item.result_class for item in field_check_result_records),
        ]
    )
    traceability_score = _score_average(item.result_class for item in traceability_check_records)
    contract_score = _score_average(item.result_class for item in contract_conformance_check_records)
    fitness_score = _score_average(item.result_class for item in fitness_check_records)
    dimension_scores = [
        score
        for score in (
            structural_score,
            traceability_score,
            contract_score,
            fitness_score,
        )
        if score is not None
    ]
    overall_score = min(dimension_scores) if dimension_scores else None
    return EvaluationScorecardRecord(
        evaluation_scorecard_record_id=EvaluationScorecardRecordId(
            stable_id(
                "evaluation_scorecard",
                evaluation_run_record_id.value,
                evaluated_object_ref.value,
                score_formula_version,
                *(str(score) for score in dimension_scores),
            )
        ),
        evaluation_run_record_id=evaluation_run_record_id,
        evaluation_scope_record_id=evaluation_scope_record_id,
        evaluated_object_ref=evaluated_object_ref,
        structural_score=structural_score,
        traceability_score=traceability_score,
        contract_score=contract_score,
        fitness_score=fitness_score,
        overall_score=overall_score,
        score_formula_version=ScoreFormulaVersion(score_formula_version),
        created_at=created_at,
    )



def _derive_decision_status(issue_summary: IssueSummary) -> DecisionStatus:
    if issue_summary.blocking_issue_count > 0:
        return DecisionStatus.BLOCKED
    if issue_summary.error_issue_count > 0:
        return DecisionStatus.FAIL
    if issue_summary.warning_issue_count > 0:
        return DecisionStatus.PASS_WITH_WARNINGS
    return DecisionStatus.PASS



def _build_rationale_text(decision_status: DecisionStatus, issue_summary: IssueSummary) -> str:
    if decision_status is DecisionStatus.PASS:
        return "All applied evaluation rules passed without warnings, errors or blocking issues."
    counts = (
        f"warnings={issue_summary.warning_issue_count}; "
        f"errors={issue_summary.error_issue_count}; "
        f"blocks={issue_summary.blocking_issue_count}"
    )
    issue_types = ",".join(f"{item.value}:{count}" for item, count in issue_summary.issue_type_counts)
    if decision_status is DecisionStatus.PASS_WITH_WARNINGS:
        prefix = "Evaluation passed with warnings."
    elif decision_status is DecisionStatus.FAIL:
        prefix = "Evaluation failed due to material issues."
    else:
        prefix = "Evaluation is blocked for progression."
    return f"{prefix} {counts}; issue_types={issue_types}."



def _score_average(result_classes) -> Decimal | None:
    values = [score_for_result_class(item) for item in result_classes]
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))
