"""Public entry point for motor_005 Canonical Normalization Engine."""

from .engine import (
    CanonicalNormalizationEngine,
    ConversionError,
    ERROR_CONVERSION_FAILED,
    ERROR_INVALID_NORMALIZATION_RULE,
    ERROR_INVALID_PARSED_RECORD,
    ERROR_INVALID_TAXONOMY,
    ERROR_MISSING_PROVENANCE,
    ERROR_NO_CANONICAL_MAPPING,
    ERROR_RULE_CONFLICT,
)
from .models import (
    FieldMapping,
    NormalizationRejection,
    NormalizationResult,
    NormalizationRule,
    NormalizedRecord,
)

__all__ = [
    "CanonicalNormalizationEngine",
    "ConversionError",
    "ERROR_CONVERSION_FAILED",
    "ERROR_INVALID_NORMALIZATION_RULE",
    "ERROR_INVALID_PARSED_RECORD",
    "ERROR_INVALID_TAXONOMY",
    "ERROR_MISSING_PROVENANCE",
    "ERROR_NO_CANONICAL_MAPPING",
    "ERROR_RULE_CONFLICT",
    "FieldMapping",
    "NormalizationRejection",
    "NormalizationResult",
    "NormalizationRule",
    "NormalizedRecord",
]
