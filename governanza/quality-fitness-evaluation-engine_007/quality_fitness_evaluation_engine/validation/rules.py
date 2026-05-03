from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from .results import ValidationSeverity


class RuleCode(str, Enum):
    REQUEST_SCOPE_REFERENCE_INVALID = "request.scope_reference_invalid"
    RULE_QUALITY_DIMENSION_REFERENCE_INVALID = "rule.quality_dimension_reference_invalid"
    RULE_FITNESS_DIMENSION_REFERENCE_INVALID = "rule.fitness_dimension_reference_invalid"
    OBJECT_CHECK_RULE_REFERENCE_INVALID = "object_check.rule_reference_invalid"
    OBJECT_CHECK_DIMENSION_REFERENCE_INVALID = "object_check.dimension_reference_invalid"
    OBJECT_CHECK_RULE_DIMENSION_MISMATCH = "object_check.rule_dimension_mismatch"
    OBJECT_CHECK_RULE_KIND_INVALID = "object_check.rule_kind_invalid"
    OBJECT_CHECK_ISSUE_REFERENCE_INVALID = "object_check.issue_reference_invalid"
    FIELD_CHECK_RULE_REFERENCE_INVALID = "field_check.rule_reference_invalid"
    FIELD_CHECK_DIMENSION_REFERENCE_INVALID = "field_check.dimension_reference_invalid"
    FIELD_CHECK_RULE_DIMENSION_MISMATCH = "field_check.rule_dimension_mismatch"
    FIELD_CHECK_RULE_KIND_INVALID = "field_check.rule_kind_invalid"
    FIELD_CHECK_ISSUE_REFERENCE_INVALID = "field_check.issue_reference_invalid"
    TRACEABILITY_CHECK_RULE_REFERENCE_INVALID = "traceability_check.rule_reference_invalid"
    TRACEABILITY_CHECK_RULE_KIND_INVALID = "traceability_check.rule_kind_invalid"
    TRACEABILITY_CHECK_ISSUE_REFERENCE_INVALID = "traceability_check.issue_reference_invalid"
    CONTRACT_CHECK_RULE_REFERENCE_INVALID = "contract_check.rule_reference_invalid"
    CONTRACT_CHECK_RULE_KIND_INVALID = "contract_check.rule_kind_invalid"
    CONTRACT_CHECK_ISSUE_REFERENCE_INVALID = "contract_check.issue_reference_invalid"
    FITNESS_CHECK_RULE_REFERENCE_INVALID = "fitness_check.rule_reference_invalid"
    FITNESS_CHECK_DIMENSION_REFERENCE_INVALID = "fitness_check.dimension_reference_invalid"
    FITNESS_CHECK_SCOPE_REFERENCE_INVALID = "fitness_check.scope_reference_invalid"
    FITNESS_CHECK_RULE_DIMENSION_MISMATCH = "fitness_check.rule_dimension_mismatch"
    FITNESS_CHECK_RULE_KIND_INVALID = "fitness_check.rule_kind_invalid"
    FITNESS_CHECK_ISSUE_REFERENCE_INVALID = "fitness_check.issue_reference_invalid"
    ISSUE_SEVERITY_REFERENCE_INVALID = "issue.severity_reference_invalid"
    ISSUE_RATIONALE_REFERENCE_INVALID = "issue.rationale_reference_invalid"
    ISSUE_EVIDENCE_REFERENCE_INVALID = "issue.evidence_reference_invalid"
    ISSUE_WARNING_SEVERITY_MISMATCH = "issue.warning_severity_mismatch"
    SCORECARD_RUN_REFERENCE_INVALID = "scorecard.run_reference_invalid"
    SCORECARD_SCOPE_REFERENCE_INVALID = "scorecard.scope_reference_invalid"
    SCORECARD_SCOPE_MISMATCH = "scorecard.scope_mismatch"
    SCORECARD_OBJECT_NOT_REQUESTED = "scorecard.object_not_requested"
    DECISION_RATIONALE_REFERENCE_INVALID = "decision.rationale_reference_invalid"
    DECISION_ISSUE_REFERENCE_INVALID = "decision.issue_reference_invalid"
    DECISION_ISSUE_SEVERITY_REFERENCE_INVALID = "decision.issue_severity_reference_invalid"
    DECISION_WARNING_COUNT_MISMATCH = "decision.warning_count_mismatch"
    DECISION_ERROR_COUNT_MISMATCH = "decision.error_count_mismatch"
    DECISION_BLOCKING_COUNT_MISMATCH = "decision.blocking_count_mismatch"
    DECISION_STATUS_ISSUE_MISMATCH = "decision.status_issue_mismatch"
    DECISION_PASS_WITH_WARNINGS_DECLARED = "decision.pass_with_warnings_declared"
    DECISION_BLOCKED_DECLARED = "decision.blocked_declared"
    RUN_REQUEST_REFERENCE_INVALID = "run.request_reference_invalid"
    RUN_SCOPE_REFERENCE_INVALID = "run.scope_reference_invalid"
    RUN_REQUEST_SCOPE_MISMATCH = "run.request_scope_mismatch"
    RUN_RULE_REFERENCE_INVALID = "run.rule_reference_invalid"
    RUN_OBJECT_CHECK_REFERENCE_INVALID = "run.object_check_reference_invalid"
    RUN_FIELD_CHECK_REFERENCE_INVALID = "run.field_check_reference_invalid"
    RUN_TRACEABILITY_CHECK_REFERENCE_INVALID = "run.traceability_check_reference_invalid"
    RUN_CONTRACT_CHECK_REFERENCE_INVALID = "run.contract_check_reference_invalid"
    RUN_FITNESS_CHECK_REFERENCE_INVALID = "run.fitness_check_reference_invalid"
    RUN_ISSUE_REFERENCE_INVALID = "run.issue_reference_invalid"
    RUN_DECISION_REFERENCE_INVALID = "run.decision_reference_invalid"
    RUN_DECISION_RUN_MISMATCH = "run.decision_run_mismatch"
    RUN_DECISION_ISSUE_NOT_REGISTERED = "run.decision_issue_not_registered"
    RUN_SCORECARD_REFERENCE_INVALID = "run.scorecard_reference_invalid"
    RUN_SCORECARD_RUN_MISMATCH = "run.scorecard_run_mismatch"
    RUN_SCORECARD_SCOPE_MISMATCH = "run.scorecard_scope_mismatch"
    RUN_CHECK_ISSUE_NOT_REGISTERED = "run.check_issue_not_registered"
    RUN_NON_COMPLETED_DECLARED = "run.non_completed_declared"
    REPLAY_RUN_REFERENCE_INVALID = "replay.run_reference_invalid"
    REPLAY_REQUEST_REFERENCE_INVALID = "replay.request_reference_invalid"
    REPLAY_SCOPE_REFERENCE_INVALID = "replay.scope_reference_invalid"
    REPLAY_RUN_REQUEST_MISMATCH = "replay.run_request_mismatch"
    REPLAY_RUN_SCOPE_MISMATCH = "replay.run_scope_mismatch"
    REPLAY_REQUEST_SCOPE_MISMATCH = "replay.request_scope_mismatch"
    REPLAY_RULE_REFERENCE_INVALID = "replay.rule_reference_invalid"
    REPLAY_RULE_NOT_REGISTERED_IN_RUN = "replay.rule_not_registered_in_run"
    REPLAY_OBJECT_NOT_REQUESTED = "replay.object_not_requested"
    REPLAY_OBJECT_VERSION_NOT_REQUESTED = "replay.object_version_not_requested"
    REPLAY_RUN_NOT_COMPLETED = "replay.run_not_completed"
    REPLAY_PARTIALLY_REPLAYABLE_DECLARED = "replay.partially_replayable_declared"
    REPLAY_NOT_REPLAYABLE_DECLARED = "replay.not_replayable_declared"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ValidationSeverity
    blocking: bool


_ERROR = RuleProfile(severity=ValidationSeverity.ERROR, blocking=True)
_WARNING = RuleProfile(severity=ValidationSeverity.WARNING, blocking=False)


_WARNING_CODES = {
    RuleCode.DECISION_PASS_WITH_WARNINGS_DECLARED,
    RuleCode.DECISION_BLOCKED_DECLARED,
    RuleCode.RUN_NON_COMPLETED_DECLARED,
    RuleCode.REPLAY_PARTIALLY_REPLAYABLE_DECLARED,
    RuleCode.REPLAY_NOT_REPLAYABLE_DECLARED,
}


def profile_for(code: RuleCode) -> RuleProfile:
    if code in _WARNING_CODES:
        return _WARNING
    return _ERROR
