"""motor_030 implementation entry point."""

from .engine import SyntheticDataGenerationEngine, generate_synthetic_data
from .errors import (
    ConstraintDriftError,
    CriticalAmbiguityUnresolvedError,
    EpistemicFlagMissingError,
    EvidentiaryPromotionLeakError,
    GeneratorVersionUnresolvedError,
    InvalidParameterConstraintError,
    LineageBreakError,
    Motor030Error,
    Motor030Rejection,
    SpecNotApprovedError,
)
from .models import (
    GenerationManifest,
    GenerationResult,
    SyntheticDataset,
    SyntheticGenerationRun,
)

__all__ = [
    "ConstraintDriftError",
    "CriticalAmbiguityUnresolvedError",
    "EpistemicFlagMissingError",
    "EvidentiaryPromotionLeakError",
    "GenerationManifest",
    "GenerationResult",
    "GeneratorVersionUnresolvedError",
    "InvalidParameterConstraintError",
    "LineageBreakError",
    "Motor030Error",
    "Motor030Rejection",
    "SpecNotApprovedError",
    "SyntheticDataGenerationEngine",
    "SyntheticDataset",
    "SyntheticGenerationRun",
    "generate_synthetic_data",
]
