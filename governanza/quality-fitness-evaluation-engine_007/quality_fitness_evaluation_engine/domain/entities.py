from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    FitnessDimensionType,
    QualityDimensionType,
    RuleApplicabilityType,
    SeverityLevel,
)
from .errors import DomainInvariantError
from .value_objects import (
    ApplicabilityTarget,
    DimensionDescription,
    EvaluatedObjectRef,
    EvaluatedObjectVersionRef,
    EvaluationRequestRecordId,
    EvaluationScopeRecordId,
    FitnessDimensionRecordId,
    IntendedUse,
    PhaseContext,
    QualityDimensionRecordId,
    RuleCriterion,
    TransitionRef,
    ValidationRuleRecordId,
    _ensure_unique,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class EvaluationScopeRecord:
    evaluation_scope_record_id: EvaluationScopeRecordId
    phase_context: PhaseContext | None
    intended_use: IntendedUse | None
    transition_ref: TransitionRef | None
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if not any(
            (
                self.phase_context is not None,
                self.intended_use is not None,
                self.transition_ref is not None,
            )
        ):
            raise DomainInvariantError(
                "EvaluationScopeRecord requires phase_context, intended_use or transition_ref."
            )


@dataclass(frozen=True, slots=True)
class EvaluationRequestRecord:
    evaluation_request_record_id: EvaluationRequestRecordId
    evaluation_scope_record_id: EvaluationScopeRecordId
    evaluated_object_refs: tuple[EvaluatedObjectRef, ...]
    evaluated_object_version_refs: tuple[EvaluatedObjectVersionRef, ...]
    requested_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "requested_at", _require_timezone(self.requested_at, "requested_at"))
        if not self.evaluated_object_refs:
            raise DomainInvariantError(
                "EvaluationRequestRecord.evaluated_object_refs must not be empty."
            )
        _ensure_unique(self.evaluated_object_refs, "evaluated_object_refs")
        _ensure_unique(self.evaluated_object_version_refs, "evaluated_object_version_refs")
        if len(self.evaluated_object_version_refs) > len(self.evaluated_object_refs):
            raise DomainInvariantError(
                "EvaluationRequestRecord.evaluated_object_version_refs cannot exceed evaluated_object_refs."
            )


@dataclass(frozen=True, slots=True)
class QualityDimensionRecord:
    quality_dimension_record_id: QualityDimensionRecordId
    quality_dimension_type: QualityDimensionType
    description: DimensionDescription
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class FitnessDimensionRecord:
    fitness_dimension_record_id: FitnessDimensionRecordId
    fitness_dimension_type: FitnessDimensionType
    description: DimensionDescription
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))


@dataclass(frozen=True, slots=True)
class ValidationRuleRecord:
    validation_rule_record_id: ValidationRuleRecordId
    quality_dimension_record_id: QualityDimensionRecordId | None
    fitness_dimension_record_id: FitnessDimensionRecordId | None
    rule_applicability_type: RuleApplicabilityType
    applicability_target: ApplicabilityTarget | None
    criterion: RuleCriterion
    default_severity_level: SeverityLevel
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if (self.quality_dimension_record_id is None) == (self.fitness_dimension_record_id is None):
            raise DomainInvariantError(
                "ValidationRuleRecord requires exactly one dimension reference."
            )
        if self.rule_applicability_type is RuleApplicabilityType.GLOBAL:
            if self.applicability_target is not None:
                raise DomainInvariantError(
                    "GLOBAL validation rules must not declare applicability_target."
                )
        elif self.applicability_target is None:
            raise DomainInvariantError(
                "Non-global validation rules must declare applicability_target."
            )
