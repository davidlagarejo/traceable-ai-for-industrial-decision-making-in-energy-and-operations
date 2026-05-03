"""Errors raised by the deterministic Validation Data Bridge."""

from __future__ import annotations


class ValidationDataBridgeError(ValueError):
    """Structured validation error for malformed bridge inputs."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        field: str | None = None,
        candidate_ref: str | None = None,
    ) -> None:
        details = message
        if field:
            details = f"{details} field={field}"
        if candidate_ref:
            details = f"{details} candidate_ref={candidate_ref}"
        super().__init__(f"{code}: {details}")
        self.code = code
        self.message = message
        self.field = field
        self.candidate_ref = candidate_ref
