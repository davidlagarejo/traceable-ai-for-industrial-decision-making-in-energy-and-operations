"""Structured errors for motor_025."""

from __future__ import annotations

from typing import Any, Dict, Optional


class EpistemicGovernanceError(Exception):
    """Base exception carrying a deterministic motor_025 error payload."""

    def __init__(
        self,
        error_code: str,
        message: str,
        *,
        field_path: Optional[str] = None,
        source_ref: Optional[str] = None,
        observed_value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.field_path = field_path
        self.source_ref = source_ref
        self.observed_value = observed_value
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "field_path": self.field_path,
            "source_ref": self.source_ref,
            "observed_value": self.observed_value,
            "details": dict(self.details),
        }


class EpistemicGovernanceInputError(EpistemicGovernanceError):
    """Raised when upstream evidence cannot be evaluated safely."""


class UnsafeEpistemicGovernanceOutputError(EpistemicGovernanceError):
    """Raised when an output would violate the motor_025 contract."""
