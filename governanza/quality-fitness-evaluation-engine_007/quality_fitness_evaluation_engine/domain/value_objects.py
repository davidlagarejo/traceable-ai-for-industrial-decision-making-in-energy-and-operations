from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable

from .._compat import dataclass
from .errors import DomainInvariantError


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainInvariantError(f"{field_name} must be non-empty.")
    return normalized


def _require_timezone(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise DomainInvariantError(f"{field_name} must be timezone-aware.")
    return value


def _ensure_unique(values: Iterable[object], field_name: str) -> None:
    materialized = tuple(values)
    if len(materialized) != len(set(materialized)):
        raise DomainInvariantError(f"{field_name} must not contain duplicates.")


def _require_non_negative_int(value: int, field_name: str) -> int:
    if value < 0:
        raise DomainInvariantError(f"{field_name} must be >= 0.")
    return value


def _require_score(value: Decimal | str | int | float, field_name: str) -> Decimal:
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DomainInvariantError(f"{field_name} must be a valid decimal.") from exc
    if decimal_value < Decimal("0") or decimal_value > Decimal("100"):
        raise DomainInvariantError(f"{field_name} must be between 0 and 100.")
    return decimal_value


@dataclass(frozen=True, slots=True)
class EvaluationRequestRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationRequestRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationRunRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationRunRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationScopeRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationScopeRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class QualityDimensionRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "QualityDimensionRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FitnessDimensionRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "FitnessDimensionRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ValidationRuleRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ValidationRuleRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObjectCheckResultRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ObjectCheckResultRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FieldCheckResultRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "FieldCheckResultRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TraceabilityCheckRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TraceabilityCheckRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContractConformanceCheckRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ContractConformanceCheckRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FitnessCheckRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "FitnessCheckRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationIssueRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationIssueRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationSeverityRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationSeverityRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationRationaleRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationRationaleRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationEvidenceRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationEvidenceRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationScorecardRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationScorecardRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationDecisionRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationDecisionRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluationReplayManifestId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluationReplayManifestId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluatedObjectRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluatedObjectRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluatedObjectVersionRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluatedObjectVersionRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObjectTypeName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ObjectTypeName.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PhaseContext:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "PhaseContext.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class IntendedUse:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "IntendedUse.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TransitionRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TransitionRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RuleCriterion:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RuleCriterion.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ApplicabilityTarget:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ApplicabilityTarget.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FieldPathRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "FieldPathRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TraceabilityAspect:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TraceabilityAspect.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContractRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ContractRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContractVersionRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ContractVersionRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class FitnessTarget:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "FitnessTarget.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RationaleText:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RationaleText.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvidenceRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvidenceSummary:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvidenceSummary.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class DimensionDescription:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "DimensionDescription.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ScoreFormulaVersion:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ScoreFormulaVersion.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EvaluatorVersion:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvaluatorVersion.value"))

    def __str__(self) -> str:
        return self.value
