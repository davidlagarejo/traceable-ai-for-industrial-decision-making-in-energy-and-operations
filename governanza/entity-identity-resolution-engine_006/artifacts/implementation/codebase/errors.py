"""Structured errors for the entity identity resolution motor."""

from __future__ import annotations

from typing import Any, Dict, Optional


class IdentityResolutionError(ValueError):
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
            "identity_resolution_record": [],
            "entity_cluster": [],
            "ambiguity_flag": [],
            "resolution_conflict": [],
            "candidate_match": [],
        }
