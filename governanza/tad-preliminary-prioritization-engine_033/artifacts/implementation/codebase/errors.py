"""Structured rejection errors for motor_033."""

from __future__ import annotations

from typing import Any


class Motor033Error(Exception):
    """Base error for governed motor_033 rejections."""

    error_code = "ERR_MOTOR_033"

    def __init__(
        self,
        message: str,
        *,
        field_paths: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.field_paths = field_paths or []
        self.details = details or {}


class InvalidSupportRegisterShapeError(Motor033Error):
    error_code = "ERR_INVALID_SUPPORT_REGISTER_SHAPE"


class MissingRequiredFieldError(Motor033Error):
    error_code = "ERR_MISSING_REQUIRED_FIELD"


class InvalidFieldTypeError(Motor033Error):
    error_code = "ERR_INVALID_FIELD_TYPE"


class MissingEpistemicFlagsError(Motor033Error):
    error_code = "ERR_MISSING_EPISTEMIC_FLAGS"


class FinalDecisionRequestedError(Motor033Error):
    error_code = "ERR_FINAL_DECISION_REQUESTED"


class UnresolvedProvenanceError(Motor033Error):
    error_code = "ERR_UNRESOLVED_PROVENANCE"


class CaseNotActiveError(Motor033Error):
    error_code = "ERR_CASE_NOT_ACTIVE"


class PhaseContractBlocksPriorityError(Motor033Error):
    error_code = "ERR_PHASE_CONTRACT_BLOCKS_PRIORITY"


class NoRankableCasesError(Motor033Error):
    error_code = "ERR_NO_RANKABLE_CASES"


class OutputInvariantError(Motor033Error):
    error_code = "ERR_OUTPUT_INVARIANT"
