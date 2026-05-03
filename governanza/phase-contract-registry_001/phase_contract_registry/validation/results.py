from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from ..domain.enums import ValidationStatus, ViolationSeverity
from ..domain.records import ValidationRunRecord, ViolationRecord


class ValidationOutcome(str, Enum):
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"

    @property
    def validation_status(self) -> ValidationStatus:
        if self is self.FAIL:
            return ValidationStatus.FAILED
        return ValidationStatus.PASSED


@dataclass(frozen=True, slots=True)
class ValidationReport:
    outcome: ValidationOutcome
    validation_run_record: ValidationRunRecord
    violation_records: tuple[ViolationRecord, ...]

    @property
    def has_warnings(self) -> bool:
        return any(
            violation.violation_severity is ViolationSeverity.WARNING
            for violation in self.violation_records
        )

    @property
    def has_errors(self) -> bool:
        return any(
            violation.violation_severity is ViolationSeverity.ERROR
            for violation in self.violation_records
        )
