from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timezone
import hashlib
import json

from .._compat import dataclass
from ..domain.entities import ObjectContract, PhaseContract, TransitionContract
from ..domain.enums import ScopeKind
from ..domain.records import ValidationRunRecord, ViolationRecord
from ..domain.value_objects import ContractVersion, EntityId, ScopedContractRef
from .collector import ViolationCollector, ViolationDraft
from .object_contract_validator import validate_object_contract
from .phase_contract_validator import validate_phase_contract
from .results import ValidationOutcome, ValidationReport
from .transition_contract_validator import validate_transition_contract


DEFAULT_VALIDATOR_VERSION = ContractVersion(0, 1, 0)


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    input_checksums: tuple[str, ...]
    target_refs: tuple[ScopedContractRef, ...]


class BasicContractValidator:
    def __init__(
        self,
        *,
        validator_version: ContractVersion = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_phase_contract(
        self,
        contract: PhaseContract,
        *,
        object_contracts: Iterable[ObjectContract] = (),
        transition_contracts: Iterable[TransitionContract] = (),
        payload_metadata: Mapping[str, object] | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(contract.reference)
        object_contracts = tuple(object_contracts)
        transition_contracts = tuple(transition_contracts)
        validate_phase_contract(
            contract,
            collector,
            object_contracts=object_contracts,
            transition_contracts=transition_contracts,
            payload_metadata=payload_metadata,
        )
        artifacts = ValidationArtifacts(
            target_refs=(contract.reference,),
            input_checksums=_build_input_checksums(
                contract.checksum,
                *(item.checksum for item in object_contracts),
                *(item.checksum for item in transition_contracts),
                _mapping_checksum(payload_metadata, "phase_payload"),
            ),
        )
        return self._build_report(
            scope_kind=ScopeKind.PHASE_CONTRACT,
            artifacts=artifacts,
            collector=collector,
        )

    def validate_object_contract(
        self,
        contract: ObjectContract,
        *,
        phase_contract: PhaseContract | None = None,
        payload_metadata: Mapping[str, object] | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(contract.reference)
        validate_object_contract(
            contract,
            collector,
            phase_contract=phase_contract,
            payload_metadata=payload_metadata,
        )
        artifacts = ValidationArtifacts(
            target_refs=(contract.reference,),
            input_checksums=_build_input_checksums(
                contract.checksum,
                phase_contract.checksum if phase_contract is not None else None,
                _mapping_checksum(payload_metadata, "object_payload"),
            ),
        )
        return self._build_report(
            scope_kind=ScopeKind.OBJECT_CONTRACT,
            artifacts=artifacts,
            collector=collector,
        )

    def validate_transition_contract(
        self,
        contract: TransitionContract,
        *,
        source_phase_contract: PhaseContract | None = None,
        target_phase_contract: PhaseContract | None = None,
        source_object_contracts: Iterable[ObjectContract] = (),
        target_object_contracts: Iterable[ObjectContract] = (),
        handoff_metadata: Mapping[str, object] | None = None,
        source_metadata: Mapping[str, object] | None = None,
        target_metadata: Mapping[str, object] | None = None,
        completed_preconditions: Iterable[str] = (),
        requested_status_transform: str | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(contract.reference)
        source_object_contracts = tuple(source_object_contracts)
        target_object_contracts = tuple(target_object_contracts)
        validate_transition_contract(
            contract,
            collector,
            source_phase_contract=source_phase_contract,
            target_phase_contract=target_phase_contract,
            source_object_contracts=source_object_contracts,
            target_object_contracts=target_object_contracts,
            handoff_metadata=handoff_metadata,
            source_metadata=source_metadata,
            target_metadata=target_metadata,
            completed_preconditions=completed_preconditions,
            requested_status_transform=requested_status_transform,
        )
        artifacts = ValidationArtifacts(
            target_refs=(contract.reference,),
            input_checksums=_build_input_checksums(
                contract.checksum,
                source_phase_contract.checksum if source_phase_contract is not None else None,
                target_phase_contract.checksum if target_phase_contract is not None else None,
                *(item.checksum for item in source_object_contracts),
                *(item.checksum for item in target_object_contracts),
                _mapping_checksum(handoff_metadata, "handoff_metadata"),
                _mapping_checksum(source_metadata, "source_metadata"),
                _mapping_checksum(target_metadata, "target_metadata"),
                _iterable_checksum(completed_preconditions, "completed_preconditions"),
                requested_status_transform.strip() if requested_status_transform else None,
            ),
        )
        return self._build_report(
            scope_kind=ScopeKind.TRANSITION_CONTRACT,
            artifacts=artifacts,
            collector=collector,
        )

    def _build_report(
        self,
        *,
        scope_kind: ScopeKind,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        executed_at = self._clock()
        validation_run_id = _stable_entity_id(
            "validation_run",
            scope_kind.value,
            str(self._validator_version),
            *(ref_signature(item) for item in artifacts.target_refs),
            *(artifacts.input_checksums),
            outcome.value,
            *(draft_signature(item) for item in collector.violations),
        )
        violation_records = tuple(
            ViolationRecord(
                violation_record_id=_stable_entity_id(
                    "violation",
                    str(validation_run_id),
                    str(index),
                    item.rule_code.value,
                    item.scope_ref.identifier.value,
                    item.evidence_ref,
                ),
                validation_run_id=validation_run_id,
                scope_kind=item.scope_ref.scope_kind,
                scope_ref=item.scope_ref,
                rule_code=item.rule_code.value,
                violation_severity=item.severity,
                message=item.message,
                blocking=item.blocking,
                evidence_ref=item.evidence_ref,
            )
            for index, item in enumerate(collector.violations, start=1)
        )
        validation_run_record = ValidationRunRecord(
            validation_run_id=validation_run_id,
            scope_kind=scope_kind,
            target_refs=artifacts.target_refs,
            validator_version=self._validator_version,
            executed_at=executed_at,
            validation_status=outcome.validation_status,
            violation_ids=tuple(item.violation_record_id for item in violation_records),
            input_checksum_set=artifacts.input_checksums,
        )
        return ValidationReport(
            outcome=outcome,
            validation_run_record=validation_run_record,
            violation_records=violation_records,
        )


def _derive_outcome(collector: ViolationCollector) -> ValidationOutcome:
    if collector.has_errors:
        return ValidationOutcome.FAIL
    if collector.has_warnings:
        return ValidationOutcome.PASS_WITH_WARNINGS
    return ValidationOutcome.PASS


def _stable_entity_id(prefix: str, *parts: str) -> EntityId:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return EntityId(f"{prefix}:{digest}")


def _build_input_checksums(*values: str | None) -> tuple[str, ...]:
    ordered_unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None or value in seen:
            continue
        seen.add(value)
        ordered_unique.append(value)
    return tuple(ordered_unique)


def _mapping_checksum(payload: Mapping[str, object] | None, label: str) -> str | None:
    if payload is None:
        return None
    normalized = json.dumps(_normalize_for_checksum(payload), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return f"{label}:{digest}"


def _iterable_checksum(values: Iterable[str], label: str) -> str | None:
    materialized = tuple(value.strip() for value in values if value and value.strip())
    if not materialized:
        return None
    normalized = json.dumps(sorted(materialized), separators=(",", ":"))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return f"{label}:{digest}"


def _normalize_for_checksum(value: object) -> object:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_for_checksum(item)
            for key, item in sorted(value.items(), key=lambda entry: str(entry[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_for_checksum(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_normalize_for_checksum(item) for item in value)
    return {"__repr__": repr(value)}


def ref_signature(reference: ScopedContractRef) -> str:
    version = str(reference.version) if reference.version is not None else "noversion"
    return f"{reference.scope_kind.value}:{reference.identifier.value}:{version}"


def draft_signature(draft: ViolationDraft) -> str:
    item = draft
    return "|".join(
        (
            ref_signature(item.scope_ref),
            item.rule_code.value,
            item.severity.value,
            item.message,
            item.evidence_ref,
            "blocking" if item.blocking else "nonblocking",
        )
    )
