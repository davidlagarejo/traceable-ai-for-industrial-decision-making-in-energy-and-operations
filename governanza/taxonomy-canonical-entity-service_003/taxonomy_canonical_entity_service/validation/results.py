from __future__ import annotations

from datetime import datetime
from enum import Enum

from .._compat import dataclass


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty.")
    return normalized


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class ValidationOutcome(str, Enum):
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class ValidationViolation:
    violation_id: str
    code: str
    severity: ValidationSeverity
    message: str
    target_ref: str
    field_ref: str | None
    blocking: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "violation_id", _require_text(self.violation_id, "violation_id"))
        object.__setattr__(self, "code", _require_text(self.code, "code"))
        object.__setattr__(self, "message", _require_text(self.message, "message"))
        object.__setattr__(self, "target_ref", _require_text(self.target_ref, "target_ref"))
        if self.field_ref is not None:
            object.__setattr__(self, "field_ref", _require_text(self.field_ref, "field_ref"))

    @property
    def rule_ref(self) -> str:
        return self.code


@dataclass(frozen=True, slots=True)
class ValidationRun:
    run_id: str
    validator_version: str
    executed_at: datetime
    target_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "run_id", _require_text(self.run_id, "run_id"))
        object.__setattr__(self, "validator_version", _require_text(self.validator_version, "validator_version"))
        if not self.target_refs:
            raise ValueError("ValidationRun.target_refs must not be empty.")
        object.__setattr__(
            self,
            "target_refs",
            tuple(_require_text(item, "target_ref") for item in self.target_refs),
        )


@dataclass(frozen=True, slots=True)
class ValidationReport:
    outcome: ValidationOutcome
    validation_run: ValidationRun
    violations: tuple[ValidationViolation, ...]

    @property
    def has_errors(self) -> bool:
        return any(item.severity is ValidationSeverity.ERROR for item in self.violations)

    @property
    def has_warnings(self) -> bool:
        return any(item.severity is ValidationSeverity.WARNING for item in self.violations)

