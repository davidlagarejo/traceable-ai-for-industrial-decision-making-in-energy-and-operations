"""Structured input errors for motor_011."""

from __future__ import annotations

from typing import Any, Optional


class CurationInputError(ValueError):
    """Raised when a run-level curation contract cannot be evaluated."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        field: Optional[str] = None,
        candidate_ref: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field
        self.candidate_ref = candidate_ref
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "candidate_ref": self.candidate_ref,
            "details": self.details,
        }
