from __future__ import annotations

from ..domain.enums import EvaluationStatus
from ..domain.records import EvaluationRunRecord
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_evaluation_run_record(
    evaluation_run: EvaluationRunRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    request = context.requests_by_id.get(evaluation_run.evaluation_request_record_id)
    if request is None:
        collector.add(
            RuleCode.RUN_REQUEST_REFERENCE_INVALID,
            "Evaluation run references an unknown evaluation request.",
        )
    scope = context.scopes_by_id.get(evaluation_run.evaluation_scope_record_id)
    if scope is None:
        collector.add(
            RuleCode.RUN_SCOPE_REFERENCE_INVALID,
            "Evaluation run references an unknown evaluation scope.",
        )
    if request is not None and request.evaluation_scope_record_id != evaluation_run.evaluation_scope_record_id:
        collector.add(
            RuleCode.RUN_REQUEST_SCOPE_MISMATCH,
            "Evaluation run scope does not match the referenced request scope.",
        )
    for rule_id in evaluation_run.validation_rule_record_ids:
        if rule_id not in context.rules_by_id:
            collector.add(
                RuleCode.RUN_RULE_REFERENCE_INVALID,
                f"Evaluation run references an unknown validation rule: {rule_id}.",
            )
    for check_id in evaluation_run.object_check_result_record_ids:
        check = context.object_checks_by_id.get(check_id)
        if check is None:
            collector.add(
                RuleCode.RUN_OBJECT_CHECK_REFERENCE_INVALID,
                f"Evaluation run references an unknown object check result: {check_id}.",
            )
            continue
        _validate_registered_issue_ids(
            check.issue_record_ids,
            evaluation_run.evaluation_issue_record_ids,
            collector,
            RuleCode.RUN_CHECK_ISSUE_NOT_REGISTERED,
        )
    for check_id in evaluation_run.field_check_result_record_ids:
        check = context.field_checks_by_id.get(check_id)
        if check is None:
            collector.add(
                RuleCode.RUN_FIELD_CHECK_REFERENCE_INVALID,
                f"Evaluation run references an unknown field check result: {check_id}.",
            )
            continue
        _validate_registered_issue_ids(
            check.issue_record_ids,
            evaluation_run.evaluation_issue_record_ids,
            collector,
            RuleCode.RUN_CHECK_ISSUE_NOT_REGISTERED,
        )
    for check_id in evaluation_run.traceability_check_record_ids:
        check = context.traceability_checks_by_id.get(check_id)
        if check is None:
            collector.add(
                RuleCode.RUN_TRACEABILITY_CHECK_REFERENCE_INVALID,
                f"Evaluation run references an unknown traceability check: {check_id}.",
            )
            continue
        _validate_registered_issue_ids(
            check.issue_record_ids,
            evaluation_run.evaluation_issue_record_ids,
            collector,
            RuleCode.RUN_CHECK_ISSUE_NOT_REGISTERED,
        )
    for check_id in evaluation_run.contract_conformance_check_record_ids:
        check = context.contract_checks_by_id.get(check_id)
        if check is None:
            collector.add(
                RuleCode.RUN_CONTRACT_CHECK_REFERENCE_INVALID,
                f"Evaluation run references an unknown contract conformance check: {check_id}.",
            )
            continue
        _validate_registered_issue_ids(
            check.issue_record_ids,
            evaluation_run.evaluation_issue_record_ids,
            collector,
            RuleCode.RUN_CHECK_ISSUE_NOT_REGISTERED,
        )
    for check_id in evaluation_run.fitness_check_record_ids:
        check = context.fitness_checks_by_id.get(check_id)
        if check is None:
            collector.add(
                RuleCode.RUN_FITNESS_CHECK_REFERENCE_INVALID,
                f"Evaluation run references an unknown fitness check: {check_id}.",
            )
            continue
        _validate_registered_issue_ids(
            check.issue_record_ids,
            evaluation_run.evaluation_issue_record_ids,
            collector,
            RuleCode.RUN_CHECK_ISSUE_NOT_REGISTERED,
        )
    for issue_id in evaluation_run.evaluation_issue_record_ids:
        if issue_id not in context.issues_by_id:
            collector.add(
                RuleCode.RUN_ISSUE_REFERENCE_INVALID,
                f"Evaluation run references an unknown issue: {issue_id}.",
            )
    if evaluation_run.evaluation_decision_record_id is not None:
        decision = context.decisions_by_id.get(evaluation_run.evaluation_decision_record_id)
        if decision is None:
            collector.add(
                RuleCode.RUN_DECISION_REFERENCE_INVALID,
                "Evaluation run references an unknown decision record.",
            )
        else:
            if decision.evaluation_run_record_id != evaluation_run.evaluation_run_record_id:
                collector.add(
                    RuleCode.RUN_DECISION_RUN_MISMATCH,
                    "Evaluation run decision does not point back to the same run.",
                )
            _validate_registered_issue_ids(
                decision.issue_record_ids,
                evaluation_run.evaluation_issue_record_ids,
                collector,
                RuleCode.RUN_DECISION_ISSUE_NOT_REGISTERED,
            )
    if evaluation_run.evaluation_scorecard_record_id is not None:
        scorecard = context.scorecards_by_id.get(evaluation_run.evaluation_scorecard_record_id)
        if scorecard is None:
            collector.add(
                RuleCode.RUN_SCORECARD_REFERENCE_INVALID,
                "Evaluation run references an unknown scorecard.",
            )
        else:
            if scorecard.evaluation_run_record_id != evaluation_run.evaluation_run_record_id:
                collector.add(
                    RuleCode.RUN_SCORECARD_RUN_MISMATCH,
                    "Evaluation run scorecard does not point back to the same run.",
                )
            if scorecard.evaluation_scope_record_id != evaluation_run.evaluation_scope_record_id:
                collector.add(
                    RuleCode.RUN_SCORECARD_SCOPE_MISMATCH,
                    "Evaluation run scorecard scope does not match the run scope.",
                )
    if evaluation_run.evaluation_status is not EvaluationStatus.COMPLETED:
        collector.add(
            RuleCode.RUN_NON_COMPLETED_DECLARED,
            "Evaluation run is not completed yet; integrity is structurally valid but not final.",
        )



def _validate_registered_issue_ids(
    issue_ids,
    registered_issue_ids,
    collector: ViolationCollector,
    code: RuleCode,
) -> None:
    registered = set(registered_issue_ids)
    for issue_id in issue_ids:
        if issue_id not in registered:
            collector.add(
                code,
                f"Referenced issue is not registered at run level: {issue_id}.",
            )
