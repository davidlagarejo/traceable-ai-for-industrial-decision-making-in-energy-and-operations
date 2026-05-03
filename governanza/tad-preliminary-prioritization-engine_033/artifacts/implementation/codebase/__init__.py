"""motor_033 implementation entry point."""

from .engine import (
    TADPreliminaryPrioritizationEngine,
    prioritize_inference_cases,
)
from .errors import (
    CaseNotActiveError,
    FinalDecisionRequestedError,
    InvalidFieldTypeError,
    InvalidSupportRegisterShapeError,
    MissingEpistemicFlagsError,
    MissingRequiredFieldError,
    Motor033Error,
    NoRankableCasesError,
    OutputInvariantError,
    PhaseContractBlocksPriorityError,
    UnresolvedProvenanceError,
)
from .models import (
    PreliminaryPriorityRegister,
    PrioritizationResult,
    RankingBasis,
    RankUncertaintyRecord,
)

__all__ = [
    "CaseNotActiveError",
    "FinalDecisionRequestedError",
    "InvalidFieldTypeError",
    "InvalidSupportRegisterShapeError",
    "MissingEpistemicFlagsError",
    "MissingRequiredFieldError",
    "Motor033Error",
    "NoRankableCasesError",
    "OutputInvariantError",
    "PhaseContractBlocksPriorityError",
    "PreliminaryPriorityRegister",
    "PrioritizationResult",
    "RankingBasis",
    "RankUncertaintyRecord",
    "TADPreliminaryPrioritizationEngine",
    "UnresolvedProvenanceError",
    "prioritize_inference_cases",
]
