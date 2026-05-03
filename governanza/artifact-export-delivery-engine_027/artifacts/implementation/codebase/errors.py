"""Structured errors for motor_027."""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any


@dataclass(frozen=True)
class ArtifactExportDeliveryError(Exception):
    """Raised when an export request cannot be prepared deterministically."""

    code: str
    message: str
    field: str | None = None
    diagnostics: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def __str__(self) -> str:
        if self.field:
            return f"{self.code}: {self.field}: {self.message}"
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "diagnostics": [dict(item) for item in self.diagnostics],
        }
