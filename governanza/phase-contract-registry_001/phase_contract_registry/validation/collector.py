from __future__ import annotations

from .._compat import dataclass
from ..domain.enums import ViolationSeverity
from ..domain.value_objects import ScopedContractRef
from .rules import RuleCode, profile_for


@dataclass(frozen=True, slots=True)
class ViolationDraft:
    scope_ref: ScopedContractRef
    rule_code: RuleCode
    severity: ViolationSeverity
    message: str
    evidence_ref: str
    blocking: bool


class ViolationCollector:
    def __init__(self, default_scope_ref: ScopedContractRef) -> None:
        self._default_scope_ref = default_scope_ref
        self._violations: list[ViolationDraft] = []

    def add(
        self,
        rule_code: RuleCode,
        message: str,
        evidence_ref: str,
        *,
        scope_ref: ScopedContractRef | None = None,
        severity: ViolationSeverity | None = None,
        blocking: bool | None = None,
    ) -> None:
        profile = profile_for(rule_code)
        self._violations.append(
            ViolationDraft(
                scope_ref=scope_ref or self._default_scope_ref,
                rule_code=rule_code,
                severity=severity or profile.severity,
                message=message,
                evidence_ref=evidence_ref,
                blocking=profile.blocking if blocking is None else blocking,
            )
        )

    @property
    def violations(self) -> tuple[ViolationDraft, ...]:
        return tuple(self._violations)

    @property
    def has_errors(self) -> bool:
        return any(item.severity is ViolationSeverity.ERROR for item in self._violations)

    @property
    def has_warnings(self) -> bool:
        return any(item.severity is ViolationSeverity.WARNING for item in self._violations)
