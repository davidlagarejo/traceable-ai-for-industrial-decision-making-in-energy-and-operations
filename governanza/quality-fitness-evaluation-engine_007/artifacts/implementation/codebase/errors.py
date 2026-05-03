"""Structured errors for the Quality / Fitness Evaluation Engine."""

from __future__ import annotations

from typing import Any, Dict, Optional


class QualityFitnessEvaluationError(ValueError):
    """Contract-level rejection with a stable machine-readable code."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
            "quality_record": [],
        }
