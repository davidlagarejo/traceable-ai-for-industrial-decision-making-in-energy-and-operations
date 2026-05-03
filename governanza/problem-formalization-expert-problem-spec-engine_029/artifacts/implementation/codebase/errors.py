"""Structured errors for motor_029."""

from __future__ import annotations


class Motor029Error(Exception):
    """Base error carrying the governed motor error code."""

    code = "ERR_MOTOR_029"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "details": self.details,
        }


class MissingProvenanceError(Motor029Error):
    code = "ERR_MISSING_PROVENANCE"


class InferenceCaseNotActiveError(Motor029Error):
    code = "ERR_INFERENCE_CASE_NOT_ACTIVE"


class PhaseContractViolationError(Motor029Error):
    code = "ERR_PHASE_CONTRACT_VIOLATION"


class CriticalAmbiguityUnresolvedError(Motor029Error):
    code = "ERR_CRITICAL_AMBIGUITY_UNRESOLVED"


class InvalidInputTypeError(Motor029Error):
    code = "ERR_INVALID_INPUT_TYPE"


class InvalidProblemClassError(Motor029Error):
    code = "ERR_INVALID_PROBLEM_CLASS"


class EpistemicFlagsMissingError(Motor029Error):
    code = "ERR_EPISTEMIC_FLAGS_MISSING"


class ParameterConstraintInvalidError(Motor029Error):
    code = "ERR_PARAMETER_CONSTRAINT_INVALID"
