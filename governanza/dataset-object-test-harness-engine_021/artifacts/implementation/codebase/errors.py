"""Structured errors for motor_021."""

from __future__ import annotations

from typing import Any, Dict, Optional


class DatasetObjectHarnessError(Exception):
    """Base exception carrying a deterministic motor_021 error code."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": dict(self.details),
        }


class HarnessInputError(DatasetObjectHarnessError):
    """Raised when the accepted batch cannot be tested safely."""


class UnsafeHarnessReportError(DatasetObjectHarnessError):
    """Raised when report aggregates do not reconcile with emitted records."""
