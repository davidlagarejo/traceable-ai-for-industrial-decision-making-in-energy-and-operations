"""Structured errors for motor_010 duplicate and similarity control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DuplicateInputError(ValueError):
    """Deterministic rejection raised before any advisory output is emitted."""

    code: str
    message: str
    field: Optional[str] = None
    record_ref: Optional[str] = None

    def __str__(self) -> str:
        parts = [self.code, self.message]
        if self.field:
            parts.append(f"field={self.field}")
        if self.record_ref:
            parts.append(f"record_ref={self.record_ref}")
        return " | ".join(parts)

    def to_dict(self) -> dict[str, Optional[str]]:
        return {
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "record_ref": self.record_ref,
        }
