from __future__ import annotations

from enum import Enum


class QualityDimensionType(str, Enum):
    STRUCTURAL_INTEGRITY = "structural_integrity"
    MINIMUM_COMPLETENESS = "minimum_completeness"
    INTERNAL_CONSISTENCY = "internal_consistency"
    TRACEABILITY = "traceability"
    VERSION_DISCIPLINE = "version_discipline"
    CONTRACT_CONFORMANCE = "contract_conformance"
    UNCERTAINTY_PRESERVATION = "uncertainty_preservation"
    STATE_TRANSPARENCY = "state_transparency"


class FitnessDimensionType(str, Enum):
    PHASE_FITNESS = "phase_fitness"
    TRANSITION_FITNESS = "transition_fitness"
    GRANULARITY_FITNESS = "granularity_fitness"
    DEPENDENCY_FITNESS = "dependency_fitness"
    EPISTEMIC_CONTEXT_FITNESS = "epistemic_context_fitness"
    DOWNSTREAM_OPERATIONAL_FITNESS = "downstream_operational_fitness"
    COVERAGE_FITNESS = "coverage_fitness"


class EvaluationStatus(str, Enum):
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABORTED = "aborted"


class DecisionStatus(str, Enum):
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"
    BLOCKED = "blocked"


class SeverityLevel(str, Enum):
    WARNING = "warning"
    ERROR = "error"
    BLOCK = "block"


class IssueType(str, Enum):
    QUALITY_FAILURE = "quality_failure"
    TRACEABILITY_FAILURE = "traceability_failure"
    CONTRACT_VIOLATION = "contract_violation"
    FITNESS_FAILURE = "fitness_failure"
    EPISTEMIC_INSUFFICIENCY = "epistemic_insufficiency"
    WARNING = "warning"


class RuleApplicabilityType(str, Enum):
    GLOBAL = "global"
    OBJECT_TYPE = "object_type"
    PHASE_CONTEXT = "phase_context"
    INTENDED_USE = "intended_use"
    TRANSITION = "transition"
    HANDOFF = "handoff"


class ReplayabilityStatus(str, Enum):
    REPLAYABLE = "replayable"
    PARTIALLY_REPLAYABLE = "partially_replayable"
    NOT_REPLAYABLE = "not_replayable"


class CheckResultClass(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    BLOCK = "block"
