from __future__ import annotations

from .._compat import dataclass
from .results import ValidationSeverity
from .rules import RuleCode, profile_for


@dataclass(frozen=True, slots=True)
class ViolationDraft:
    code: RuleCode
    severity: ValidationSeverity
    message: str
    target_ref: str
    field_ref: str | None
    blocking: bool


class ViolationCollector:
    def __init__(self, default_target_ref: str) -> None:
        self._default_target_ref = default_target_ref
        self._violations: list[ViolationDraft] = []

    def add(
        self,
        code: RuleCode,
        message: str,
        *,
        target_ref: str | None = None,
        field_ref: str | None = None,
        severity: ValidationSeverity | None = None,
        blocking: bool | None = None,
    ) -> None:
        profile = profile_for(code)
        self._violations.append(
            ViolationDraft(
                code=code,
                severity=severity or profile.severity,
                message=message,
                target_ref=target_ref or self._default_target_ref,
                field_ref=field_ref,
                blocking=profile.blocking if blocking is None else blocking,
            )
        )

    @property
    def violations(self) -> tuple[ViolationDraft, ...]:
        return tuple(self._violations)

    @property
    def has_errors(self) -> bool:
        return any(item.severity is ValidationSeverity.ERROR for item in self._violations)

    @property
    def has_warnings(self) -> bool:
        return any(item.severity is ValidationSeverity.WARNING for item in self._violations)

