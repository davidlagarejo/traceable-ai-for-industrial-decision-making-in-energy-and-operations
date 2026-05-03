"""Structured rejection errors for motor_032."""

from __future__ import annotations

from typing import Any


class Motor032Error(Exception):
    """Base error for governed motor_032 rejections."""

    error_code = "MOTOR_032_ERROR"

    def __init__(
        self,
        message: str,
        *,
        field_paths: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.field_paths = field_paths or []
        self.details = details or {}


class InvalidInputSchemaError(Motor032Error):
    error_code = "INVALID_INPUT_SCHEMA"


class MissingRequiredFieldError(Motor032Error):
    error_code = "MISSING_REQUIRED_FIELD"


class InvalidFieldTypeError(Motor032Error):
    error_code = "INVALID_FIELD_TYPE"


class MissingEpistemicFlagsError(Motor032Error):
    error_code = "MISSING_EPISTEMIC_FLAGS"


class NoTargetInferenceRecordError(Motor032Error):
    error_code = "NO_TARGET_INFERENCE_RECORD"


class AmbiguousTargetInferenceRecordError(Motor032Error):
    error_code = "AMBIGUOUS_TARGET_INFERENCE_RECORD"


class PhaseContractDisallowsSyntheticSupportError(Motor032Error):
    error_code = "PHASE_CONTRACT_DISALLOWS_SYNTHETIC_SUPPORT"


class MissingLineageReferenceError(Motor032Error):
    error_code = "MISSING_LINEAGE_REFERENCE"


class PromotionRequestForbiddenError(Motor032Error):
    error_code = "PROMOTION_REQUEST_FORBIDDEN"


class OutputInvariantError(Motor032Error):
    error_code = "OUTPUT_INVARIANT_FAILURE"
