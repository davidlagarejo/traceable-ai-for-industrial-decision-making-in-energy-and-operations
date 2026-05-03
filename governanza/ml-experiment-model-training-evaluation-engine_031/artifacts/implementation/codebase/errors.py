"""Structured errors for motor_031."""

from __future__ import annotations

from typing import Any


class Motor031Error(Exception):
    """Base error for governed motor_031 rejections."""

    error_code = "ERROR_MOTOR_031"

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


class InvalidInputSchemaError(Motor031Error):
    error_code = "ERROR_INVALID_INPUT_SCHEMA"


class InputLineageMismatchError(Motor031Error):
    error_code = "ERROR_INPUT_LINEAGE_MISMATCH"


class MissingEpistemicFlagsError(Motor031Error):
    error_code = "ERROR_MISSING_EPISTEMIC_FLAGS"


class UnsupportedProblemClassError(Motor031Error):
    error_code = "ERROR_UNSUPPORTED_PROBLEM_CLASS"


class CriticalAmbiguityError(Motor031Error):
    error_code = "ERROR_CRITICAL_AMBIGUITY"


class InsufficientSyntheticSampleError(Motor031Error):
    error_code = "ERROR_INSUFFICIENT_SYNTHETIC_SAMPLE"


class BaselinePolicyError(Motor031Error):
    error_code = "ERROR_BASELINE_NOT_EVALUATED"


class ProductionModelRequestedError(Motor031Error):
    error_code = "ERROR_PRODUCTION_MODEL_REQUESTED"
