from __future__ import annotations

from ..domain.enums import IssueType, SeverityLevel
from ..domain.records import (
    EvaluationEvidenceRecord,
    EvaluationIssueRecord,
    EvaluationRationaleRecord,
    EvaluationSeverityRecord,
)
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_evaluation_severity_record(
    evaluation_severity: EvaluationSeverityRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    del evaluation_severity, collector, context



def validate_evaluation_rationale_record(
    evaluation_rationale: EvaluationRationaleRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    del evaluation_rationale, collector, context



def validate_evaluation_evidence_record(
    evaluation_evidence: EvaluationEvidenceRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    del evaluation_evidence, collector, context



def validate_evaluation_issue_record(
    evaluation_issue: EvaluationIssueRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    severity = context.severities_by_id.get(evaluation_issue.evaluation_severity_record_id)
    if severity is None:
        collector.add(
            RuleCode.ISSUE_SEVERITY_REFERENCE_INVALID,
            "Evaluation issue references an unknown severity record.",
            field_ref=str(evaluation_issue.field_path_ref) if evaluation_issue.field_path_ref else None,
        )
    if evaluation_issue.evaluation_rationale_record_id not in context.rationales_by_id:
        collector.add(
            RuleCode.ISSUE_RATIONALE_REFERENCE_INVALID,
            "Evaluation issue references an unknown rationale record.",
            field_ref=str(evaluation_issue.field_path_ref) if evaluation_issue.field_path_ref else None,
        )
    for evidence_id in evaluation_issue.evidence_record_ids:
        if evidence_id not in context.evidence_by_id:
            collector.add(
                RuleCode.ISSUE_EVIDENCE_REFERENCE_INVALID,
                f"Evaluation issue references an unknown evidence record: {evidence_id}.",
                field_ref=str(evaluation_issue.field_path_ref) if evaluation_issue.field_path_ref else None,
            )
    if (
        evaluation_issue.issue_type is IssueType.WARNING
        and severity is not None
        and severity.severity_level is not SeverityLevel.WARNING
    ):
        collector.add(
            RuleCode.ISSUE_WARNING_SEVERITY_MISMATCH,
            "IssueType.WARNING must reference a warning severity record.",
            field_ref=str(evaluation_issue.field_path_ref) if evaluation_issue.field_path_ref else None,
        )
