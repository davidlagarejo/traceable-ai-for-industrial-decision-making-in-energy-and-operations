"""motor_032 implementation entry point."""

from .engine import (
    SyntheticMLDecisionSupportIntegration,
    integrate_synthetic_ml_support,
)
from .errors import (
    AmbiguousTargetInferenceRecordError,
    InvalidFieldTypeError,
    InvalidInputSchemaError,
    MissingEpistemicFlagsError,
    MissingLineageReferenceError,
    MissingRequiredFieldError,
    Motor032Error,
    NoTargetInferenceRecordError,
    OutputInvariantError,
    PhaseContractDisallowsSyntheticSupportError,
    PromotionRequestForbiddenError,
)
from .models import (
    HypothesisSignal,
    IntegrationResult,
    LabeledSupportRecord,
    SyntheticMLSupportRegister,
)

__all__ = [
    "AmbiguousTargetInferenceRecordError",
    "HypothesisSignal",
    "IntegrationResult",
    "InvalidFieldTypeError",
    "InvalidInputSchemaError",
    "LabeledSupportRecord",
    "MissingEpistemicFlagsError",
    "MissingLineageReferenceError",
    "MissingRequiredFieldError",
    "Motor032Error",
    "NoTargetInferenceRecordError",
    "OutputInvariantError",
    "PhaseContractDisallowsSyntheticSupportError",
    "PromotionRequestForbiddenError",
    "SyntheticMLDecisionSupportIntegration",
    "SyntheticMLSupportRegister",
    "integrate_synthetic_ml_support",
]
