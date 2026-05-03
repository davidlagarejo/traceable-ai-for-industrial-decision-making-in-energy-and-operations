"""Motor 010 implementation package."""

from .engine import (
    DuplicateSimilarityControlEngine,
    run_duplicate_similarity_control,
)
from .errors import DuplicateInputError
from .models import (
    DeduplicationDecision,
    DuplicateCluster,
    DuplicateSimilarityResult,
    SimilarityRecord,
    ThresholdProfile,
)

__all__ = [
    "DeduplicationDecision",
    "DuplicateCluster",
    "DuplicateInputError",
    "DuplicateSimilarityControlEngine",
    "DuplicateSimilarityResult",
    "SimilarityRecord",
    "ThresholdProfile",
    "run_duplicate_similarity_control",
]
