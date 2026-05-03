from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import (
    CompatibilityStatus,
    MigrationKind,
    ScopeKind,
    ServingStatus,
    ValidationStatus,
    ViolationSeverity,
)
from .errors import DomainInvariantError
from .value_objects import (
    ChangeDescriptor,
    ContractVersion,
    EntityId,
    ScopedContractRef,
    _ensure_unique,
    _require_text,
    _require_timezone,
)


@dataclass(frozen=True, slots=True)
class ValidationRunRecord:
    validation_run_id: EntityId
    scope_kind: ScopeKind
    target_refs: tuple[ScopedContractRef, ...]
    validator_version: ContractVersion
    executed_at: datetime
    validation_status: ValidationStatus
    violation_ids: tuple[EntityId, ...]
    input_checksum_set: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.target_refs:
            raise DomainInvariantError("target_refs must not be empty.")
        object.__setattr__(self, "executed_at", _require_timezone(self.executed_at, "executed_at"))
        object.__setattr__(
            self,
            "input_checksum_set",
            tuple(_require_text(checksum, "input_checksum") for checksum in self.input_checksum_set),
        )
        _ensure_unique(self.target_refs, "target_refs")
        _ensure_unique(self.violation_ids, "violation_ids")
        _ensure_unique(self.input_checksum_set, "input_checksum_set")
        if self.validation_status is ValidationStatus.FAILED and not self.violation_ids:
            raise DomainInvariantError("Failed validation runs must reference at least one violation.")
        for ref in self.target_refs:
            if ref.scope_kind != self.scope_kind:
                raise DomainInvariantError("Every target_ref.scope_kind must match validation scope_kind.")


@dataclass(frozen=True, slots=True)
class ViolationRecord:
    violation_record_id: EntityId
    validation_run_id: EntityId
    scope_kind: ScopeKind
    scope_ref: ScopedContractRef
    rule_code: str
    violation_severity: ViolationSeverity
    message: str
    blocking: bool
    evidence_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_code", _require_text(self.rule_code, "rule_code"))
        object.__setattr__(self, "message", _require_text(self.message, "message"))
        object.__setattr__(self, "evidence_ref", _require_text(self.evidence_ref, "evidence_ref"))
        if self.scope_ref.scope_kind != self.scope_kind:
            raise DomainInvariantError("scope_ref.scope_kind must match scope_kind.")
        if self.blocking and self.violation_severity is not ViolationSeverity.ERROR:
            raise DomainInvariantError("Only error violations may be blocking.")


@dataclass(frozen=True, slots=True)
class ContractDiffRecord:
    contract_diff_record_id: EntityId
    scope_kind: ScopeKind
    source_ref: ScopedContractRef
    target_ref: ScopedContractRef
    change_set: tuple[ChangeDescriptor, ...]
    breaking_change_detected: bool
    generated_at: datetime

    def __post_init__(self) -> None:
        if self.source_ref.scope_kind != self.scope_kind or self.target_ref.scope_kind != self.scope_kind:
            raise DomainInvariantError("source_ref and target_ref must match scope_kind.")
        if not self.change_set:
            raise DomainInvariantError("change_set must not be empty.")
        object.__setattr__(self, "generated_at", _require_timezone(self.generated_at, "generated_at"))
        inferred_breaking = any(change.is_breaking_by_default for change in self.change_set)
        if inferred_breaking and not self.breaking_change_detected:
            raise DomainInvariantError(
                "breaking_change_detected must be true when change_set contains breaking changes by default."
            )


@dataclass(frozen=True, slots=True)
class CompatibilityRecord:
    compatibility_record_id: EntityId
    scope_kind: ScopeKind
    source_ref: ScopedContractRef
    target_ref: ScopedContractRef
    compatibility_status: CompatibilityStatus
    breaking_reasons: tuple[str, ...]
    migration_required: bool
    generated_at: datetime

    def __post_init__(self) -> None:
        if self.source_ref.scope_kind != self.scope_kind or self.target_ref.scope_kind != self.scope_kind:
            raise DomainInvariantError("source_ref and target_ref must match scope_kind.")
        object.__setattr__(
            self,
            "breaking_reasons",
            tuple(_require_text(reason, "breaking_reason") for reason in self.breaking_reasons),
        )
        _ensure_unique(self.breaking_reasons, "breaking_reasons")
        object.__setattr__(self, "generated_at", _require_timezone(self.generated_at, "generated_at"))

        if self.compatibility_status is CompatibilityStatus.COMPATIBLE:
            if self.breaking_reasons:
                raise DomainInvariantError("Compatible records must not include breaking_reasons.")
            if self.migration_required:
                raise DomainInvariantError("Compatible records must not require migration.")
        elif self.compatibility_status is CompatibilityStatus.CONDITIONALLY_COMPATIBLE:
            if not self.breaking_reasons:
                raise DomainInvariantError(
                    "Conditionally compatible records must include explicit compatibility reasons."
                )
            if not self.migration_required:
                raise DomainInvariantError(
                    "Conditionally compatible records must require migration."
                )
        elif self.compatibility_status is CompatibilityStatus.INCOMPATIBLE:
            if not self.breaking_reasons:
                raise DomainInvariantError("Incompatible records must include breaking_reasons.")


@dataclass(frozen=True, slots=True)
class MigrationSpec:
    migration_spec_id: EntityId
    source_ref: ScopedContractRef
    target_ref: ScopedContractRef
    migration_kind: MigrationKind
    required_steps: tuple[str, ...]
    manual_steps: tuple[str, ...]
    data_loss_risk: bool
    approval_required: bool
    created_at: datetime

    def __post_init__(self) -> None:
        if self.source_ref.scope_kind != self.target_ref.scope_kind:
            raise DomainInvariantError("source_ref and target_ref must have the same scope_kind.")
        object.__setattr__(
            self, "required_steps", tuple(_require_text(step, "required_step") for step in self.required_steps)
        )
        object.__setattr__(
            self, "manual_steps", tuple(_require_text(step, "manual_step") for step in self.manual_steps)
        )
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

        if not self.required_steps and not self.manual_steps:
            raise DomainInvariantError("MigrationSpec must define required_steps or manual_steps.")
        if self.data_loss_risk and not self.approval_required:
            raise DomainInvariantError("data_loss_risk migrations must require approval.")


@dataclass(frozen=True, slots=True)
class ContractServingSnapshot:
    contract_serving_snapshot_id: EntityId
    snapshot_version: ContractVersion
    included_phase_contract_refs: tuple[ScopedContractRef, ...]
    included_object_contract_refs: tuple[ScopedContractRef, ...]
    included_transition_contract_refs: tuple[ScopedContractRef, ...]
    source_validation_run_id: EntityId
    serving_status: ServingStatus
    created_at: datetime
    checksum: str

    @property
    def reference(self) -> ScopedContractRef:
        return ScopedContractRef(
            scope_kind=ScopeKind.SNAPSHOT,
            identifier=self.contract_serving_snapshot_id,
            version=self.snapshot_version,
        )

    def __post_init__(self) -> None:
        if not self.included_phase_contract_refs:
            raise DomainInvariantError("included_phase_contract_refs must not be empty.")
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        object.__setattr__(self, "checksum", _require_text(self.checksum, "checksum"))

        for refs, expected_scope, field_name in (
            (self.included_phase_contract_refs, ScopeKind.PHASE_CONTRACT, "included_phase_contract_refs"),
            (self.included_object_contract_refs, ScopeKind.OBJECT_CONTRACT, "included_object_contract_refs"),
            (
                self.included_transition_contract_refs,
                ScopeKind.TRANSITION_CONTRACT,
                "included_transition_contract_refs",
            ),
        ):
            _ensure_unique(refs, field_name)
            for ref in refs:
                if ref.scope_kind != expected_scope:
                    raise DomainInvariantError(f"{field_name} must only contain {expected_scope.value} refs.")
                if ref.version is None:
                    raise DomainInvariantError(f"{field_name} must point to stable versioned refs.")
