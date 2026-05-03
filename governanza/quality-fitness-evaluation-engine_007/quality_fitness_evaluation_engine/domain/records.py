from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from .._compat import dataclass
from .enums import (
    CheckResultClass,
    DecisionStatus,
    EvaluationStatus,
    IssueType,
    ReplayabilityStatus,
    SeverityLevel,
)
from .errors import DomainInvariantError
from .value_objects import (
    ContractConformanceCheckRecordId,
    ContractRef,
    ContractVersionRef,
    EvaluatedObjectRef,
    EvaluatedObjectVersionRef,
    EvaluationDecisionRecordId,
    EvaluationEvidenceRecordId,
    EvaluationIssueRecordId,
    EvaluationRationaleRecordId,
    EvaluationReplayManifestId,
    EvaluationRequestRecordId,
    EvaluationRunRecordId,
    EvaluationScopeRecordId,
    EvaluationScorecardRecordId,
    EvaluationSeverityRecordId,
    EvaluatorVersion,
    EvidenceRef,
    EvidenceSummary,
    FieldCheckResultRecordId,
    FieldPathRef,
    FitnessCheckRecordId,
    FitnessDimensionRecordId,
    FitnessTarget,
    ObjectCheckResultRecordId,
    QualityDimensionRecordId,
    RationaleText,
    ScoreFormulaVersion,
    TraceabilityAspect,
    TraceabilityCheckRecordId,
    ValidationRuleRecordId,
    _ensure_unique,
    _require_non_negative_int,
    _require_score,
    _require_text,
    _require_timezone,
)


def _validate_issue_links(
    result_class: CheckResultClass,
    issue_record_ids: tuple[EvaluationIssueRecordId, ...],
    field_name: str,
) -> None:
    _ensure_unique(issue_record_ids, field_name)
    if result_class is CheckResultClass.PASS and issue_record_ids:
        raise DomainInvariantError(f"{field_name} must be empty when result_class is PASS.")
    if result_class is not CheckResultClass.PASS and not issue_record_ids:
        raise DomainInvariantError(f"{field_name} must not be empty when result_class is not PASS.")


@dataclass(frozen=True, slots=True)
class EvaluationSeverityRecord:
    evaluation_severity_record_id: EvaluationSeverityRecordId
    severity_level: SeverityLevel
    blocks_progression: bool
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        expected_blocking = self.severity_level is SeverityLevel.BLOCK
        if self.blocks_progression != expected_blocking:
            raise DomainInvariantError(
                "EvaluationSeverityRecord.blocks_progression must match severity_level semantics."
            )


@dataclass(frozen=True, slots=True)
class EvaluationRationaleRecord:
    evaluation_rationale_record_id: EvaluationRationaleRecordId
    rationale_text: RationaleText
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class EvaluationEvidenceRecord:
    evaluation_evidence_record_id: EvaluationEvidenceRecordId
    evidence_ref: EvidenceRef
    evidence_summary: EvidenceSummary
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class ObjectCheckResultRecord:
    object_check_result_record_id: ObjectCheckResultRecordId
    evaluated_object_ref: EvaluatedObjectRef
    evaluated_object_version_ref: EvaluatedObjectVersionRef | None
    validation_rule_record_id: ValidationRuleRecordId | None
    quality_dimension_record_id: QualityDimensionRecordId | None
    result_class: CheckResultClass
    issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.validation_rule_record_id is None and self.quality_dimension_record_id is None:
            raise DomainInvariantError(
                "ObjectCheckResultRecord requires validation_rule_record_id or quality_dimension_record_id."
            )
        _validate_issue_links(
            self.result_class,
            self.issue_record_ids,
            "ObjectCheckResultRecord.issue_record_ids",
        )


@dataclass(frozen=True, slots=True)
class FieldCheckResultRecord:
    field_check_result_record_id: FieldCheckResultRecordId
    evaluated_object_ref: EvaluatedObjectRef
    field_path_ref: FieldPathRef
    validation_rule_record_id: ValidationRuleRecordId | None
    quality_dimension_record_id: QualityDimensionRecordId | None
    result_class: CheckResultClass
    issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.validation_rule_record_id is None and self.quality_dimension_record_id is None:
            raise DomainInvariantError(
                "FieldCheckResultRecord requires validation_rule_record_id or quality_dimension_record_id."
            )
        _validate_issue_links(
            self.result_class,
            self.issue_record_ids,
            "FieldCheckResultRecord.issue_record_ids",
        )


@dataclass(frozen=True, slots=True)
class TraceabilityCheckRecord:
    traceability_check_record_id: TraceabilityCheckRecordId
    evaluated_object_ref: EvaluatedObjectRef
    validation_rule_record_id: ValidationRuleRecordId | None
    traceability_aspect: TraceabilityAspect
    result_class: CheckResultClass
    issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _validate_issue_links(
            self.result_class,
            self.issue_record_ids,
            "TraceabilityCheckRecord.issue_record_ids",
        )


@dataclass(frozen=True, slots=True)
class ContractConformanceCheckRecord:
    contract_conformance_check_record_id: ContractConformanceCheckRecordId
    evaluated_object_ref: EvaluatedObjectRef
    validation_rule_record_id: ValidationRuleRecordId | None
    contract_ref: ContractRef
    contract_version_ref: ContractVersionRef | None
    result_class: CheckResultClass
    issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _validate_issue_links(
            self.result_class,
            self.issue_record_ids,
            "ContractConformanceCheckRecord.issue_record_ids",
        )


@dataclass(frozen=True, slots=True)
class FitnessCheckRecord:
    fitness_check_record_id: FitnessCheckRecordId
    evaluated_object_ref: EvaluatedObjectRef
    validation_rule_record_id: ValidationRuleRecordId | None
    evaluation_scope_record_id: EvaluationScopeRecordId
    fitness_dimension_record_id: FitnessDimensionRecordId | None
    fitness_target: FitnessTarget
    result_class: CheckResultClass
    issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.validation_rule_record_id is None and self.fitness_dimension_record_id is None:
            raise DomainInvariantError(
                "FitnessCheckRecord requires validation_rule_record_id or fitness_dimension_record_id."
            )
        _validate_issue_links(
            self.result_class,
            self.issue_record_ids,
            "FitnessCheckRecord.issue_record_ids",
        )


@dataclass(frozen=True, slots=True)
class EvaluationIssueRecord:
    evaluation_issue_record_id: EvaluationIssueRecordId
    issue_type: IssueType
    evaluation_severity_record_id: EvaluationSeverityRecordId
    evaluation_rationale_record_id: EvaluationRationaleRecordId
    evidence_record_ids: tuple[EvaluationEvidenceRecordId, ...]
    evaluated_object_ref: EvaluatedObjectRef
    field_path_ref: FieldPathRef | None
    message: str
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "message", _require_text(self.message, "EvaluationIssueRecord.message"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.evidence_record_ids, "EvaluationIssueRecord.evidence_record_ids")


@dataclass(frozen=True, slots=True)
class EvaluationScorecardRecord:
    evaluation_scorecard_record_id: EvaluationScorecardRecordId
    evaluation_run_record_id: EvaluationRunRecordId
    evaluation_scope_record_id: EvaluationScopeRecordId
    evaluated_object_ref: EvaluatedObjectRef
    structural_score: Decimal | None
    traceability_score: Decimal | None
    contract_score: Decimal | None
    fitness_score: Decimal | None
    overall_score: Decimal | None
    score_formula_version: ScoreFormulaVersion
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        score_fields = (
            "structural_score",
            "traceability_score",
            "contract_score",
            "fitness_score",
            "overall_score",
        )
        values = []
        for field_name in score_fields:
            value = getattr(self, field_name)
            if value is not None:
                normalized = _require_score(value, f"EvaluationScorecardRecord.{field_name}")
                object.__setattr__(self, field_name, normalized)
                values.append(normalized)
        if not values:
            raise DomainInvariantError(
                "EvaluationScorecardRecord requires at least one explicit score."
            )


@dataclass(frozen=True, slots=True)
class EvaluationDecisionRecord:
    evaluation_decision_record_id: EvaluationDecisionRecordId
    evaluation_run_record_id: EvaluationRunRecordId
    decision_status: DecisionStatus
    issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    warning_issue_count: int
    error_issue_count: int
    blocking_issue_count: int
    evaluation_rationale_record_id: EvaluationRationaleRecordId
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        _ensure_unique(self.issue_record_ids, "EvaluationDecisionRecord.issue_record_ids")
        warning_count = _require_non_negative_int(
            self.warning_issue_count,
            "EvaluationDecisionRecord.warning_issue_count",
        )
        error_count = _require_non_negative_int(
            self.error_issue_count,
            "EvaluationDecisionRecord.error_issue_count",
        )
        blocking_count = _require_non_negative_int(
            self.blocking_issue_count,
            "EvaluationDecisionRecord.blocking_issue_count",
        )
        object.__setattr__(self, "warning_issue_count", warning_count)
        object.__setattr__(self, "error_issue_count", error_count)
        object.__setattr__(self, "blocking_issue_count", blocking_count)
        total = warning_count + error_count + blocking_count
        if len(self.issue_record_ids) != total:
            raise DomainInvariantError(
                "EvaluationDecisionRecord issue counts must match issue_record_ids length."
            )
        if self.decision_status is DecisionStatus.PASS:
            if total != 0:
                raise DomainInvariantError("PASS decisions must not declare issues.")
        elif self.decision_status is DecisionStatus.PASS_WITH_WARNINGS:
            if warning_count == 0 or error_count != 0 or blocking_count != 0:
                raise DomainInvariantError(
                    "PASS_WITH_WARNINGS requires warnings and no errors or blocks."
                )
        elif self.decision_status is DecisionStatus.FAIL:
            if error_count == 0 or blocking_count != 0:
                raise DomainInvariantError(
                    "FAIL requires errors and must not hide blocking issues."
                )
        elif self.decision_status is DecisionStatus.BLOCKED:
            if blocking_count == 0:
                raise DomainInvariantError(
                    "BLOCKED requires at least one blocking issue."
                )


@dataclass(frozen=True, slots=True)
class EvaluationRunRecord:
    evaluation_run_record_id: EvaluationRunRecordId
    evaluation_request_record_id: EvaluationRequestRecordId
    evaluation_scope_record_id: EvaluationScopeRecordId
    evaluation_status: EvaluationStatus
    validation_rule_record_ids: tuple[ValidationRuleRecordId, ...]
    object_check_result_record_ids: tuple[ObjectCheckResultRecordId, ...]
    field_check_result_record_ids: tuple[FieldCheckResultRecordId, ...]
    traceability_check_record_ids: tuple[TraceabilityCheckRecordId, ...]
    contract_conformance_check_record_ids: tuple[ContractConformanceCheckRecordId, ...]
    fitness_check_record_ids: tuple[FitnessCheckRecordId, ...]
    evaluation_issue_record_ids: tuple[EvaluationIssueRecordId, ...]
    evaluation_decision_record_id: EvaluationDecisionRecordId | None
    evaluation_scorecard_record_id: EvaluationScorecardRecordId | None
    evaluator_version: EvaluatorVersion
    started_at: datetime
    completed_at: datetime | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "started_at", _require_timezone(self.started_at, "started_at"))
        if self.completed_at is not None:
            object.__setattr__(self, "completed_at", _require_timezone(self.completed_at, "completed_at"))
            if self.completed_at < self.started_at:
                raise DomainInvariantError(
                    "EvaluationRunRecord.completed_at must not be earlier than started_at."
                )
        _ensure_unique(self.validation_rule_record_ids, "validation_rule_record_ids")
        _ensure_unique(self.object_check_result_record_ids, "object_check_result_record_ids")
        _ensure_unique(self.field_check_result_record_ids, "field_check_result_record_ids")
        _ensure_unique(self.traceability_check_record_ids, "traceability_check_record_ids")
        _ensure_unique(
            self.contract_conformance_check_record_ids,
            "contract_conformance_check_record_ids",
        )
        _ensure_unique(self.fitness_check_record_ids, "fitness_check_record_ids")
        _ensure_unique(self.evaluation_issue_record_ids, "evaluation_issue_record_ids")
        if self.evaluation_status is EvaluationStatus.COMPLETED:
            if self.completed_at is None:
                raise DomainInvariantError("Completed evaluation runs require completed_at.")
            if self.evaluation_decision_record_id is None:
                raise DomainInvariantError(
                    "Completed evaluation runs require evaluation_decision_record_id."
                )
            if not self.validation_rule_record_ids:
                raise DomainInvariantError(
                    "Completed evaluation runs require validation_rule_record_ids."
                )
            if not any(
                (
                    self.object_check_result_record_ids,
                    self.field_check_result_record_ids,
                    self.traceability_check_record_ids,
                    self.contract_conformance_check_record_ids,
                    self.fitness_check_record_ids,
                    self.evaluation_issue_record_ids,
                )
            ):
                raise DomainInvariantError(
                    "Completed evaluation runs require checks or issues as evidence of evaluation."
                )
        else:
            if self.evaluation_decision_record_id is not None:
                raise DomainInvariantError(
                    "Only completed evaluation runs may declare evaluation_decision_record_id."
                )
            if self.evaluation_scorecard_record_id is not None:
                raise DomainInvariantError(
                    "Only completed evaluation runs may declare evaluation_scorecard_record_id."
                )
            if self.completed_at is not None and self.evaluation_status is not EvaluationStatus.ABORTED:
                raise DomainInvariantError(
                    "Non-completed evaluation runs must not declare completed_at unless aborted."
                )


@dataclass(frozen=True, slots=True)
class EvaluationReplayManifest:
    evaluation_replay_manifest_id: EvaluationReplayManifestId
    evaluation_run_record_id: EvaluationRunRecordId
    evaluation_request_record_id: EvaluationRequestRecordId
    evaluation_scope_record_id: EvaluationScopeRecordId
    evaluated_object_refs: tuple[EvaluatedObjectRef, ...]
    evaluated_object_version_refs: tuple[EvaluatedObjectVersionRef, ...]
    validation_rule_record_ids: tuple[ValidationRuleRecordId, ...]
    contract_version_ref: ContractVersionRef | None
    evaluator_version: EvaluatorVersion
    replayability_status: ReplayabilityStatus
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not self.evaluated_object_refs:
            raise DomainInvariantError(
                "EvaluationReplayManifest.evaluated_object_refs must not be empty."
            )
        if not self.validation_rule_record_ids:
            raise DomainInvariantError(
                "EvaluationReplayManifest.validation_rule_record_ids must not be empty."
            )
        _ensure_unique(self.evaluated_object_refs, "evaluated_object_refs")
        _ensure_unique(self.evaluated_object_version_refs, "evaluated_object_version_refs")
        _ensure_unique(self.validation_rule_record_ids, "validation_rule_record_ids")
        if len(self.evaluated_object_version_refs) > len(self.evaluated_object_refs):
            raise DomainInvariantError(
                "EvaluationReplayManifest.evaluated_object_version_refs cannot exceed evaluated_object_refs."
            )
        if (
            self.replayability_status is ReplayabilityStatus.REPLAYABLE
            and not self.evaluated_object_version_refs
        ):
            raise DomainInvariantError(
                "Replayable manifests require explicit evaluated_object_version_refs."
            )
