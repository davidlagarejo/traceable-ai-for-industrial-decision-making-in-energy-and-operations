"""Structured errors for the Verification Bridge Engine."""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any


@dataclass(frozen=True)
class VerificationBridgeError(ValueError):
    """Structured validation error returned by motor_019."""

    code: str
    message: str
    field: str | None = None
    details: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "details": self.details,
        }

    def __str__(self) -> str:
        location = f" [{self.field}]" if self.field else ""
        return f"{self.code}{location}: {self.message}"
