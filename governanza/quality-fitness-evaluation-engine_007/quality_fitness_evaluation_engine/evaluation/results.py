from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
import hashlib

from .._compat import dataclass
from ..domain.entities import (
    EvaluationRequestRecord,
    EvaluationScopeRecord,
    FitnessDimensionRecord,
    QualityDimensionRecord,
    ValidationRuleRecord,
)
from ..domain.enums import CheckResultClass, DecisionStatus, IssueType, SeverityLevel
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
from ..domain.value_objects import (
    ContractRef,
    ContractVersionRef,
    FieldPathRef,
    FitnessTarget,
    TraceabilityAspect,
    ValidationRuleRecordId,
)


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty.")
    return normalized


class RuleExecutionKind(str, Enum):
    OBJECT = "object"
    FIELD = "field"
    TRACEABILITY = "traceability"
    CONTRACT = "contract"
    FITNESS = "fitness"


@dataclass(frozen=True, slots=True)
class IssueDraft:
    issue_type: IssueType
    severity_level: SeverityLevel
    message: str
    rationale_text: str
    evidence_ref: str
    evidence_summary: str
    field_path_ref: FieldPathRef | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "message", _require_text(self.message, "message"))
        object.__setattr__(
            self,
            "rationale_text",
            _require_text(self.rationale_text, "rationale_text"),
        )
        object.__setattr__(self, "evidence_ref", _require_text(self.evidence_ref, "evidence_ref"))
        object.__setattr__(
            self,
            "evidence_summary",
            _require_text(self.evidence_summary, "evidence_summary"),
        )


@dataclass(frozen=True, slots=True)
class RuleExecutionDraft:
    execution_kind: RuleExecutionKind
    validation_rule_record_id: ValidationRuleRecordId
    result_class: CheckResultClass
    issue_drafts: tuple[IssueDraft, ...]
    field_path_ref: FieldPathRef | None = None
    traceability_aspect: TraceabilityAspect | None = None
    contract_ref: ContractRef | None = None
    contract_version_ref: ContractVersionRef | None = None
    fitness_target: FitnessTarget | None = None

    def __post_init__(self) -> None:
        if self.execution_kind is RuleExecutionKind.FIELD and self.field_path_ref is None:
            raise ValueError("Field rule executions require field_path_ref.")
        if (
            self.execution_kind is RuleExecutionKind.TRACEABILITY
            and self.traceability_aspect is None
        ):
            raise ValueError("Traceability rule executions require traceability_aspect.")
        if self.execution_kind is RuleExecutionKind.CONTRACT and self.contract_ref is None:
            raise ValueError("Contract rule executions require contract_ref.")
        if self.execution_kind is RuleExecutionKind.FITNESS and self.fitness_target is None:
            raise ValueError("Fitness rule executions require fitness_target.")


@dataclass(frozen=True, slots=True)
class BasicEvaluationResult:
    evaluation_scope_record: EvaluationScopeRecord
    evaluation_request_record: EvaluationRequestRecord
    quality_dimension_records: tuple[QualityDimensionRecord, ...]
    fitness_dimension_records: tuple[FitnessDimensionRecord, ...]
    validation_rule_records: tuple[ValidationRuleRecord, ...]
    object_check_result_records: tuple[ObjectCheckResultRecord, ...]
    field_check_result_records: tuple[FieldCheckResultRecord, ...]
    traceability_check_records: tuple[TraceabilityCheckRecord, ...]
    contract_conformance_check_records: tuple[ContractConformanceCheckRecord, ...]
    fitness_check_records: tuple[FitnessCheckRecord, ...]
    evaluation_issue_records: tuple[EvaluationIssueRecord, ...]
    evaluation_severity_records: tuple[EvaluationSeverityRecord, ...]
    evaluation_rationale_records: tuple[EvaluationRationaleRecord, ...]
    evaluation_evidence_records: tuple[EvaluationEvidenceRecord, ...]
    evaluation_scorecard_record: EvaluationScorecardRecord
    evaluation_decision_record: EvaluationDecisionRecord
    evaluation_run_record: EvaluationRunRecord
    evaluation_replay_manifest: EvaluationReplayManifest
    executed_at: datetime

    @property
    def decision_status(self) -> DecisionStatus:
        return self.evaluation_decision_record.decision_status

    @property
    def applied_rule_ids(self) -> tuple[ValidationRuleRecordId, ...]:
        return self.evaluation_run_record.validation_rule_record_ids


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def derive_result_class(issue_drafts: tuple[IssueDraft, ...]) -> CheckResultClass:
    if any(item.severity_level is SeverityLevel.BLOCK for item in issue_drafts):
        return CheckResultClass.BLOCK
    if any(item.severity_level is SeverityLevel.ERROR for item in issue_drafts):
        return CheckResultClass.FAIL
    if any(item.severity_level is SeverityLevel.WARNING for item in issue_drafts):
        return CheckResultClass.WARNING
    return CheckResultClass.PASS


def score_for_result_class(result_class: CheckResultClass) -> Decimal:
    if result_class is CheckResultClass.PASS:
        return Decimal("100")
    if result_class is CheckResultClass.WARNING:
        return Decimal("75")
    if result_class is CheckResultClass.FAIL:
        return Decimal("25")
    return Decimal("0")
