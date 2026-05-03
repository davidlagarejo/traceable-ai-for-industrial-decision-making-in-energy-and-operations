"""Structured errors for the Output Block Composition Engine."""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any


@dataclass(frozen=True)
class OutputBlockCompositionError(ValueError):
    """Raised when the batch envelope cannot be processed deterministically."""

    code: str
    message: str
    field: str | None = None
    details: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def __str__(self) -> str:
        location = f" [{self.field}]" if self.field else ""
        return f"{self.code}{location}: {self.message}"
