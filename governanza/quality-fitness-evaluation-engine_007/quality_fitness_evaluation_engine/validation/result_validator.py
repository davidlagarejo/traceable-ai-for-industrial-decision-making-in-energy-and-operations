from __future__ import annotations

from ..domain.enums import DecisionStatus, SeverityLevel
from ..domain.records import EvaluationDecisionRecord, EvaluationScorecardRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_evaluation_scorecard_record(
    evaluation_scorecard: EvaluationScorecardRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    run = context.runs_by_id.get(evaluation_scorecard.evaluation_run_record_id)
    if run is None:
        collector.add(
            RuleCode.SCORECARD_RUN_REFERENCE_INVALID,
            "Evaluation scorecard references an unknown evaluation run.",
        )
    scope = context.scopes_by_id.get(evaluation_scorecard.evaluation_scope_record_id)
    if scope is None:
        collector.add(
            RuleCode.SCORECARD_SCOPE_REFERENCE_INVALID,
            "Evaluation scorecard references an unknown evaluation scope.",
        )
    if run is not None:
        if run.evaluation_scope_record_id != evaluation_scorecard.evaluation_scope_record_id:
            collector.add(
                RuleCode.SCORECARD_SCOPE_MISMATCH,
                "Evaluation scorecard scope does not match the referenced run scope.",
            )
        request = context.requests_by_id.get(run.evaluation_request_record_id)
        if request is not None and evaluation_scorecard.evaluated_object_ref not in request.evaluated_object_refs:
            collector.add(
                RuleCode.SCORECARD_OBJECT_NOT_REQUESTED,
                "Evaluation scorecard target object is not part of the referenced request.",
            )



def validate_evaluation_decision_record(
    evaluation_decision: EvaluationDecisionRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if evaluation_decision.evaluation_rationale_record_id not in context.rationales_by_id:
        collector.add(
            RuleCode.DECISION_RATIONALE_REFERENCE_INVALID,
            "Evaluation decision references an unknown rationale record.",
        )
    warning_count = 0
    error_count = 0
    blocking_count = 0
    for issue_id in evaluation_decision.issue_record_ids:
        issue = context.issues_by_id.get(issue_id)
        if issue is None:
            collector.add(
                RuleCode.DECISION_ISSUE_REFERENCE_INVALID,
                f"Evaluation decision references an unknown issue: {issue_id}.",
            )
            continue
        severity = context.severities_by_id.get(issue.evaluation_severity_record_id)
        if severity is None:
            collector.add(
                RuleCode.DECISION_ISSUE_SEVERITY_REFERENCE_INVALID,
                f"Evaluation decision issue references an unknown severity: {issue.evaluation_severity_record_id}.",
            )
            continue
        if severity.severity_level is SeverityLevel.WARNING:
            warning_count += 1
        elif severity.severity_level is SeverityLevel.ERROR:
            error_count += 1
        else:
            blocking_count += 1
    if warning_count != evaluation_decision.warning_issue_count:
        collector.add(
            RuleCode.DECISION_WARNING_COUNT_MISMATCH,
            "Evaluation decision warning count does not match linked issue severities.",
        )
    if error_count != evaluation_decision.error_issue_count:
        collector.add(
            RuleCode.DECISION_ERROR_COUNT_MISMATCH,
            "Evaluation decision error count does not match linked issue severities.",
        )
    if blocking_count != evaluation_decision.blocking_issue_count:
        collector.add(
            RuleCode.DECISION_BLOCKING_COUNT_MISMATCH,
            "Evaluation decision blocking count does not match linked issue severities.",
        )
    if evaluation_decision.decision_status is DecisionStatus.PASS:
        if warning_count or error_count or blocking_count:
            collector.add(
                RuleCode.DECISION_STATUS_ISSUE_MISMATCH,
                "PASS decision must not carry linked issues.",
            )
    elif evaluation_decision.decision_status is DecisionStatus.PASS_WITH_WARNINGS:
        if warning_count == 0 or error_count != 0 or blocking_count != 0:
            collector.add(
                RuleCode.DECISION_STATUS_ISSUE_MISMATCH,
                "PASS_WITH_WARNINGS requires warning-only linked issues.",
            )
        else:
            collector.add(
                RuleCode.DECISION_PASS_WITH_WARNINGS_DECLARED,
                "Evaluation decision is explicitly pass_with_warnings.",
            )
    elif evaluation_decision.decision_status is DecisionStatus.FAIL:
        if error_count == 0 or blocking_count != 0:
            collector.add(
                RuleCode.DECISION_STATUS_ISSUE_MISMATCH,
                "FAIL requires error issues and must not hide blocking issues.",
            )
    elif evaluation_decision.decision_status is DecisionStatus.BLOCKED:
        if blocking_count == 0:
            collector.add(
                RuleCode.DECISION_STATUS_ISSUE_MISMATCH,
                "BLOCKED requires blocking issues.",
            )
        else:
            collector.add(
                RuleCode.DECISION_BLOCKED_DECLARED,
                "Evaluation decision is explicitly blocked.",
            )
