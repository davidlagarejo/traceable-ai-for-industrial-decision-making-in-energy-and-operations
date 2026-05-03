from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Iterable, TypeVar

from ..domain.entities import ObjectContract, PhaseContract, TransitionContract
from ..domain.enums import ChangeKind, ScopeKind
from ..domain.errors import DomainInvariantError
from ..domain.records import ContractDiffRecord
from ..domain.value_objects import ChangeDescriptor, EntityId, ScopedContractRef
from .classifier import classify_changes
from .models import ContractDiffResult
from .versioning import compare_versions


ContractEntity = TypeVar("ContractEntity", PhaseContract, ObjectContract, TransitionContract)


def diff_contracts(
    source: ContractEntity,
    target: ContractEntity,
    *,
    generated_at: datetime | None = None,
) -> ContractDiffResult:
    _ensure_same_contract_type(source, target)
    change_set = _diff_by_type(source, target)
    classified_changes = classify_changes(change_set)
    version_delta = _extract_version_delta(source, target)

    diff_record = None
    if change_set:
        diff_record = ContractDiffRecord(
            contract_diff_record_id=_stable_entity_id(
                "contract_diff",
                _ref_signature(_contract_ref(source)),
                _ref_signature(_contract_ref(target)),
                *(item.path for item in change_set),
                *(item.change_kind.value for item in change_set),
            ),
            scope_kind=_scope_kind_for(source),
            source_ref=_contract_ref(source),
            target_ref=_contract_ref(target),
            change_set=change_set,
            breaking_change_detected=any(
                item.change_kind.is_breaking_by_default for item in change_set
            ),
            generated_at=generated_at or datetime.now(timezone.utc),
        )

    return ContractDiffResult(
        source_contract_type=type(source).__name__,
        target_contract_type=type(target).__name__,
        version_delta=version_delta,
        changes=change_set,
        classified_changes=classified_changes,
        diff_record=diff_record,
    )


def _ensure_same_contract_type(source: object, target: object) -> None:
    if type(source) is not type(target):
        raise DomainInvariantError("Contracts can only be diffed against the same contract type.")


def _scope_kind_for(contract: ContractEntity) -> ScopeKind:
    if isinstance(contract, PhaseContract):
        return ScopeKind.PHASE_CONTRACT
    if isinstance(contract, ObjectContract):
        return ScopeKind.OBJECT_CONTRACT
    if isinstance(contract, TransitionContract):
        return ScopeKind.TRANSITION_CONTRACT
    raise DomainInvariantError("Unsupported contract type for diff.")


def _contract_ref(contract: ContractEntity) -> ScopedContractRef:
    return contract.reference


def _extract_version_delta(
    source: ContractEntity,
    target: ContractEntity,
):
    if isinstance(source, PhaseContract) and isinstance(target, PhaseContract):
        return compare_versions(source.contract_version, target.contract_version)
    return None


def _diff_by_type(source: ContractEntity, target: ContractEntity) -> tuple[ChangeDescriptor, ...]:
    if isinstance(source, PhaseContract):
        return _diff_phase_contracts(source, target)
    if isinstance(source, ObjectContract):
        return _diff_object_contracts(source, target)
    if isinstance(source, TransitionContract):
        return _diff_transition_contracts(source, target)
    raise DomainInvariantError("Unsupported contract type for diff.")


def _diff_phase_contracts(
    source: PhaseContract,
    target: PhaseContract,
) -> tuple[ChangeDescriptor, ...]:
    changes: list[ChangeDescriptor] = []
    changes.extend(
        _set_changes(
            path="allowed_output_names",
            source_values=source.allowed_output_names,
            target_values=target.allowed_output_names,
            add_kind=ChangeKind.ADDITIVE,
            remove_kind=ChangeKind.REMOVAL,
            label="allowed output",
        )
    )
    changes.extend(
        _set_changes(
            path="forbidden_output_names",
            source_values=source.forbidden_output_names,
            target_values=target.forbidden_output_names,
            add_kind=ChangeKind.RESTRICTIVE,
            remove_kind=ChangeKind.ADDITIVE,
            label="forbidden output",
        )
    )
    changes.extend(
        _set_changes(
            path="required_metadata_keys",
            source_values=_metadata_names(source.required_metadata_keys),
            target_values=_metadata_names(target.required_metadata_keys),
            add_kind=ChangeKind.METADATA_CHANGE,
            remove_kind=ChangeKind.METADATA_CHANGE,
            label="required metadata key",
        )
    )
    changes.extend(
        _set_changes(
            path="object_contract_ids",
            source_values=_entity_names(source.object_contract_ids),
            target_values=_entity_names(target.object_contract_ids),
            add_kind=ChangeKind.ADDITIVE,
            remove_kind=ChangeKind.RESTRICTIVE,
            label="object contract reference",
        )
    )
    changes.extend(
        _set_changes(
            path="transition_contract_ids",
            source_values=_entity_names(source.transition_contract_ids),
            target_values=_entity_names(target.transition_contract_ids),
            add_kind=ChangeKind.ADDITIVE,
            remove_kind=ChangeKind.RESTRICTIVE,
            label="transition contract reference",
        )
    )
    changes.extend(
        _scalar_change(
            path="contract_status",
            source_value=source.contract_status.value,
            target_value=target.contract_status.value,
            kind=ChangeKind.SEMANTIC_CHANGE,
            label="contract status",
        )
    )
    changes.extend(
        _scalar_change(
            path="canonical_name",
            source_value=source.canonical_name,
            target_value=target.canonical_name,
            kind=ChangeKind.RENAME,
            label="canonical name",
        )
    )
    return tuple(changes)


def _diff_object_contracts(
    source: ObjectContract,
    target: ObjectContract,
) -> tuple[ChangeDescriptor, ...]:
    changes: list[ChangeDescriptor] = []
    changes.extend(
        _field_shape_changes(
            source_required=source.required_fields,
            source_optional=source.optional_fields,
            source_forbidden=source.forbidden_fields,
            target_required=target.required_fields,
            target_optional=target.optional_fields,
            target_forbidden=target.forbidden_fields,
        )
    )
    changes.extend(
        _set_changes(
            path="required_metadata_keys",
            source_values=_metadata_names(source.required_metadata_keys),
            target_values=_metadata_names(target.required_metadata_keys),
            add_kind=ChangeKind.METADATA_CHANGE,
            remove_kind=ChangeKind.METADATA_CHANGE,
            label="required metadata key",
        )
    )
    changes.extend(
        _metadata_policy_changes(source, target)
    )
    changes.extend(
        _set_changes(
            path="allowed_epistemic_state_tokens",
            source_values=source.allowed_epistemic_state_tokens,
            target_values=target.allowed_epistemic_state_tokens,
            add_kind=ChangeKind.ADDITIVE,
            remove_kind=ChangeKind.RESTRICTIVE,
            label="allowed epistemic token",
        )
    )
    changes.extend(
        _set_changes(
            path="forbidden_epistemic_state_tokens",
            source_values=source.forbidden_epistemic_state_tokens,
            target_values=target.forbidden_epistemic_state_tokens,
            add_kind=ChangeKind.RESTRICTIVE,
            remove_kind=ChangeKind.ADDITIVE,
            label="forbidden epistemic token",
        )
    )
    changes.extend(
        _scalar_change(
            path="object_name",
            source_value=source.object_name,
            target_value=target.object_name,
            kind=ChangeKind.RENAME,
            label="object name",
        )
    )
    changes.extend(
        _scalar_change(
            path="object_role",
            source_value=source.object_role,
            target_value=target.object_role,
            kind=ChangeKind.SEMANTIC_CHANGE,
            label="object role",
        )
    )
    return tuple(changes)


def _diff_transition_contracts(
    source: TransitionContract,
    target: TransitionContract,
) -> tuple[ChangeDescriptor, ...]:
    changes: list[ChangeDescriptor] = []
    changes.extend(
        _scalar_change(
            path="source_phase_contract_id",
            source_value=source.source_phase_contract_id.value,
            target_value=target.source_phase_contract_id.value,
            kind=ChangeKind.SEMANTIC_CHANGE,
            label="source phase contract id",
        )
    )
    changes.extend(
        _scalar_change(
            path="target_phase_contract_id",
            source_value=source.target_phase_contract_id.value,
            target_value=target.target_phase_contract_id.value,
            kind=ChangeKind.SEMANTIC_CHANGE,
            label="target phase contract id",
        )
    )
    changes.extend(
        _set_changes(
            path="source_object_refs",
            source_values=_scoped_ref_names(source.source_object_refs),
            target_values=_scoped_ref_names(target.source_object_refs),
            add_kind=ChangeKind.SEMANTIC_CHANGE,
            remove_kind=ChangeKind.SEMANTIC_CHANGE,
            label="source object ref",
        )
    )
    changes.extend(
        _set_changes(
            path="target_object_refs",
            source_values=_scoped_ref_names(source.target_object_refs),
            target_values=_scoped_ref_names(target.target_object_refs),
            add_kind=ChangeKind.SEMANTIC_CHANGE,
            remove_kind=ChangeKind.SEMANTIC_CHANGE,
            label="target object ref",
        )
    )
    changes.extend(
        _set_changes(
            path="required_preconditions",
            source_values=source.required_preconditions,
            target_values=target.required_preconditions,
            add_kind=ChangeKind.RESTRICTIVE,
            remove_kind=ChangeKind.ADDITIVE,
            label="required precondition",
        )
    )
    changes.extend(
        _set_changes(
            path="required_metadata_keys",
            source_values=_metadata_names(source.required_metadata_keys),
            target_values=_metadata_names(target.required_metadata_keys),
            add_kind=ChangeKind.METADATA_CHANGE,
            remove_kind=ChangeKind.METADATA_CHANGE,
            label="required metadata key",
        )
    )
    changes.extend(
        _set_changes(
            path="allowed_status_transforms",
            source_values=source.allowed_status_transforms,
            target_values=target.allowed_status_transforms,
            add_kind=ChangeKind.ADDITIVE,
            remove_kind=ChangeKind.REMOVAL,
            label="allowed status transform",
        )
    )
    changes.extend(
        _set_changes(
            path="blocked_status_transforms",
            source_values=source.blocked_status_transforms,
            target_values=target.blocked_status_transforms,
            add_kind=ChangeKind.RESTRICTIVE,
            remove_kind=ChangeKind.ADDITIVE,
            label="blocked status transform",
        )
    )
    changes.extend(
        _set_changes(
            path="prohibited_transforms",
            source_values=source.prohibited_transforms,
            target_values=target.prohibited_transforms,
            add_kind=ChangeKind.RESTRICTIVE,
            remove_kind=ChangeKind.ADDITIVE,
            label="prohibited transform",
        )
    )
    changes.extend(
        _scalar_change(
            path="transition_name",
            source_value=source.transition_name,
            target_value=target.transition_name,
            kind=ChangeKind.RENAME,
            label="transition name",
        )
    )
    return tuple(changes)


def _field_shape_changes(
    *,
    source_required: tuple[str, ...],
    source_optional: tuple[str, ...],
    source_forbidden: tuple[str, ...],
    target_required: tuple[str, ...],
    target_optional: tuple[str, ...],
    target_forbidden: tuple[str, ...],
) -> tuple[ChangeDescriptor, ...]:
    changes: list[ChangeDescriptor] = []
    source_required_set = set(source_required)
    source_optional_set = set(source_optional)
    source_forbidden_set = set(source_forbidden)
    target_required_set = set(target_required)
    target_optional_set = set(target_optional)
    target_forbidden_set = set(target_forbidden)

    for field_name in sorted(target_optional_set - source_optional_set - source_required_set - source_forbidden_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.ADDITIVE,
                path=f"optional_fields.{field_name}",
                description=f"Added optional field '{field_name}'.",
            )
        )
    for field_name in sorted(source_optional_set - target_optional_set - target_required_set - target_forbidden_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.RESTRICTIVE,
                path=f"optional_fields.{field_name}",
                description=f"Removed optional field '{field_name}'.",
            )
        )
    for field_name in sorted(target_required_set - source_required_set - source_optional_set - source_forbidden_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.RESTRICTIVE,
                path=f"required_fields.{field_name}",
                description=f"Added required field '{field_name}'.",
            )
        )
    for field_name in sorted(source_required_set - target_required_set - target_optional_set - target_forbidden_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.REMOVAL,
                path=f"required_fields.{field_name}",
                description=f"Removed required field '{field_name}'.",
            )
        )
    for field_name in sorted(source_optional_set & target_required_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.RESTRICTIVE,
                path=f"fields.{field_name}",
                description=f"Changed field '{field_name}' from optional to required.",
            )
        )
    for field_name in sorted(source_required_set & target_optional_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.ADDITIVE,
                path=f"fields.{field_name}",
                description=f"Changed field '{field_name}' from required to optional.",
            )
        )
    for field_name in sorted(target_forbidden_set - source_forbidden_set - source_required_set - source_optional_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.RESTRICTIVE,
                path=f"forbidden_fields.{field_name}",
                description=f"Added forbidden field '{field_name}'.",
            )
        )
    for field_name in sorted(source_forbidden_set - target_forbidden_set - target_required_set - target_optional_set):
        changes.append(
            ChangeDescriptor(
                change_kind=ChangeKind.ADDITIVE,
                path=f"forbidden_fields.{field_name}",
                description=f"Removed forbidden field '{field_name}'.",
            )
        )
    return tuple(changes)


def _metadata_policy_changes(
    source: ObjectContract,
    target: ObjectContract,
) -> tuple[ChangeDescriptor, ...]:
    changes: list[ChangeDescriptor] = []
    source_policy = source.metadata_preservation_policy
    target_policy = target.metadata_preservation_policy
    changes.extend(
        _set_changes(
            path="metadata_preservation_policy.required_keys",
            source_values=_metadata_names(source_policy.required_keys),
            target_values=_metadata_names(target_policy.required_keys),
            add_kind=ChangeKind.METADATA_CHANGE,
            remove_kind=ChangeKind.METADATA_CHANGE,
            label="metadata policy required key",
        )
    )
    changes.extend(
        _set_changes(
            path="metadata_preservation_policy.immutable_keys",
            source_values=_metadata_names(source_policy.immutable_keys),
            target_values=_metadata_names(target_policy.immutable_keys),
            add_kind=ChangeKind.METADATA_CHANGE,
            remove_kind=ChangeKind.METADATA_CHANGE,
            label="immutable metadata key",
        )
    )
    changes.extend(
        _set_changes(
            path="metadata_preservation_policy.passthrough_keys",
            source_values=_metadata_names(source_policy.passthrough_keys),
            target_values=_metadata_names(target_policy.passthrough_keys),
            add_kind=ChangeKind.METADATA_CHANGE,
            remove_kind=ChangeKind.METADATA_CHANGE,
            label="passthrough metadata key",
        )
    )
    changes.extend(
        _scalar_change(
            path="metadata_preservation_policy.missing_key_behavior",
            source_value=source_policy.missing_key_behavior,
            target_value=target_policy.missing_key_behavior,
            kind=ChangeKind.METADATA_CHANGE,
            label="missing key behavior",
        )
    )
    changes.extend(
        _scalar_change(
            path="metadata_preservation_policy.unknown_key_behavior",
            source_value=source_policy.unknown_key_behavior,
            target_value=target_policy.unknown_key_behavior,
            kind=ChangeKind.METADATA_CHANGE,
            label="unknown key behavior",
        )
    )
    return tuple(changes)


def _set_changes(
    *,
    path: str,
    source_values: Iterable[str],
    target_values: Iterable[str],
    add_kind: ChangeKind,
    remove_kind: ChangeKind,
    label: str,
) -> tuple[ChangeDescriptor, ...]:
    source_set = set(source_values)
    target_set = set(target_values)
    changes: list[ChangeDescriptor] = []
    for value in sorted(target_set - source_set):
        changes.append(
            ChangeDescriptor(
                change_kind=add_kind,
                path=f"{path}.{value}",
                description=f"Added {label} '{value}'.",
            )
        )
    for value in sorted(source_set - target_set):
        changes.append(
            ChangeDescriptor(
                change_kind=remove_kind,
                path=f"{path}.{value}",
                description=f"Removed {label} '{value}'.",
            )
        )
    return tuple(changes)


def _scalar_change(
    *,
    path: str,
    source_value: str,
    target_value: str,
    kind: ChangeKind,
    label: str,
) -> tuple[ChangeDescriptor, ...]:
    if source_value == target_value:
        return ()
    return (
        ChangeDescriptor(
            change_kind=kind,
            path=path,
            description=f"Changed {label} from '{source_value}' to '{target_value}'.",
        ),
    )


def _metadata_names(values: Iterable[object]) -> tuple[str, ...]:
    return tuple(item.value for item in values)


def _entity_names(values: Iterable[EntityId]) -> tuple[str, ...]:
    return tuple(item.value for item in values)


def _scoped_ref_names(values: Iterable[ScopedContractRef]) -> tuple[str, ...]:
    return tuple(item.identifier.value for item in values)


def _stable_entity_id(prefix: str, *parts: str) -> EntityId:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return EntityId(f"{prefix}:{digest}")


def _ref_signature(reference: ScopedContractRef) -> str:
    version = str(reference.version) if reference.version is not None else "noversion"
    return f"{reference.scope_kind.value}:{reference.identifier.value}:{version}"
