"""Structured errors for motor_013."""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any


@dataclass(frozen=True)
class InferenceActivationError(Exception):
    """Raised when motor_013 must reject an activation run."""

    code: str
    message: str
    field: str | None = None
    validation_records: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def __str__(self) -> str:
        if self.field:
            return f"{self.code}: {self.field}: {self.message}"
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "validation_records": [dict(item) for item in self.validation_records],
        }
