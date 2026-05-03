"""Structured errors for motor_030."""

from __future__ import annotations

from typing import Any


class Motor030Error(Exception):
    """Base error for synthetic generation failures."""

    rejection_code = "MOTOR_030_ERROR"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class Motor030Rejection(Motor030Error):
    """Input or candidate output was rejected with a governed code."""

    rejection_code = "REJECTED"


class SpecNotApprovedError(Motor030Rejection):
    rejection_code = "SPEC_NOT_APPROVED"


class CriticalAmbiguityUnresolvedError(Motor030Rejection):
    rejection_code = "CRITICAL_AMBIGUITY_UNRESOLVED"


class GeneratorVersionUnresolvedError(Motor030Rejection):
    rejection_code = "GENERATOR_VERSION_UNRESOLVED"


class InvalidParameterConstraintError(Motor030Rejection):
    rejection_code = "INVALID_PARAMETER_CONSTRAINT"


class EpistemicFlagMissingError(Motor030Rejection):
    rejection_code = "EPISTEMIC_FLAG_MISSING"


class ConstraintDriftError(Motor030Rejection):
    rejection_code = "CONSTRAINT_DRIFT"


class LineageBreakError(Motor030Rejection):
    rejection_code = "LINEAGE_BREAK"


class EvidentiaryPromotionLeakError(Motor030Rejection):
    rejection_code = "EVIDENTIARY_PROMOTION_LEAK"
