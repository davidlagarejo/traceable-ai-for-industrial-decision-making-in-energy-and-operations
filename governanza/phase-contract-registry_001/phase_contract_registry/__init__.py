"""Phase Contract Registry package."""

from .domain import *  # noqa: F401,F403
from .evolution import (
    ChangeImpact,
    ClassifiedChange,
    CompatibilityDecision,
    CompatibilityEvaluation,
    ContractDiffResult,
    VersionChangeKind,
    VersionDelta,
    compare_versions,
    diff_contracts,
    evaluate_contract_compatibility,
)
from .validation import BasicContractValidator, RuleCode, ValidationOutcome, ValidationReport

__all__ = [
    "BasicContractValidator",
    "ChangeImpact",
    "ClassifiedChange",
    "CompatibilityDecision",
    "CompatibilityEvaluation",
    "ContractDiffResult",
    "RuleCode",
    "ValidationOutcome",
    "ValidationReport",
    "VersionChangeKind",
    "VersionDelta",
    "compare_versions",
    "diff_contracts",
    "evaluate_contract_compatibility",
]
