"""Structured errors for motor_022."""

from __future__ import annotations

from typing import Any, Dict, Optional


class EvaluationConformanceError(Exception):
    """Base exception carrying a deterministic motor_022 error payload."""

    def __init__(
        self,
        error_code: str,
        message: str,
        *,
        input_ref: Optional[str] = None,
        expected_condition: Optional[str] = None,
        observed_value: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.input_ref = input_ref
        self.expected_condition = expected_condition
        self.observed_value = observed_value
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
            "input_ref": self.input_ref,
            "expected_condition": self.expected_condition,
            "observed_value": self.observed_value,
            "details": dict(self.details),
        }
        return payload


class ConformanceInputError(EvaluationConformanceError):
    """Raised when input evidence cannot be evaluated safely."""


class UnsafeConformanceOutputError(EvaluationConformanceError):
    """Raised when an emitted bundle would violate motor_022 invariants."""
