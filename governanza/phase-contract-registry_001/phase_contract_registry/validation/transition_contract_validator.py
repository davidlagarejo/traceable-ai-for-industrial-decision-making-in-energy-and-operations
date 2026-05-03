from __future__ import annotations

from collections.abc import Iterable, Mapping

from ..domain.entities import ObjectContract, PhaseContract, TransitionContract
from .collector import ViolationCollector
from .metadata_validator import validate_metadata_preservation, validate_required_metadata
from .rules import RuleCode


def validate_transition_contract(
    contract: TransitionContract,
    collector: ViolationCollector,
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
) -> None:
    if contract.source_phase_contract_id == contract.target_phase_contract_id:
        collector.add(
            RuleCode.TRANSITION_SELF_HANDOFF,
            message="TransitionContract cannot use the same phase contract as source and target.",
            evidence_ref="transition_contract.phase_contract_ids",
        )

    if source_phase_contract is not None:
        if contract.source_phase_contract_id != source_phase_contract.phase_contract_id:
            collector.add(
                RuleCode.TRANSITION_SOURCE_PHASE_MISMATCH,
                message=(
                    f"TransitionContract source phase '{contract.source_phase_contract_id}' does not match "
                    f"provided phase_contract '{source_phase_contract.phase_contract_id}'."
                ),
                evidence_ref="transition_contract.source_phase_contract_id",
            )
        if contract.transition_contract_id not in set(source_phase_contract.transition_contract_ids):
            collector.add(
                RuleCode.TRANSITION_NOT_DECLARED_BY_SOURCE_PHASE,
                message=(
                    f"TransitionContract '{contract.transition_contract_id}' is not declared by source "
                    f"phase_contract '{source_phase_contract.phase_contract_id}'."
                ),
                evidence_ref="source_phase_contract.transition_contract_ids",
            )

    if target_phase_contract is not None:
        if contract.target_phase_contract_id != target_phase_contract.phase_contract_id:
            collector.add(
                RuleCode.TRANSITION_TARGET_PHASE_MISMATCH,
                message=(
                    f"TransitionContract target phase '{contract.target_phase_contract_id}' does not match "
                    f"provided phase_contract '{target_phase_contract.phase_contract_id}'."
                ),
                evidence_ref="transition_contract.target_phase_contract_id",
            )
        if contract.transition_contract_id not in set(target_phase_contract.transition_contract_ids):
            collector.add(
                RuleCode.TRANSITION_NOT_DECLARED_BY_TARGET_PHASE,
                message=(
                    f"TransitionContract '{contract.transition_contract_id}' is not declared by target "
                    f"phase_contract '{target_phase_contract.phase_contract_id}'."
                ),
                evidence_ref="target_phase_contract.transition_contract_ids",
            )

    if (
        source_phase_contract is not None
        and target_phase_contract is not None
        and source_phase_contract.phase_id == target_phase_contract.phase_id
    ):
        collector.add(
            RuleCode.TRANSITION_SELF_HANDOFF,
            message="TransitionContract must hand off across distinct phase ids.",
            evidence_ref="transition_contract.phase_ids",
        )

    source_objects_by_id = {item.object_contract_id: item for item in source_object_contracts}
    for source_ref in contract.source_object_refs:
        source_object = source_objects_by_id.get(source_ref.identifier)
        if source_object is None:
            collector.add(
                RuleCode.TRANSITION_SOURCE_OBJECT_MISSING,
                message=f"Source object '{source_ref.identifier}' was not provided for transition validation.",
                evidence_ref=f"transition_contract.source_object_refs.{source_ref.identifier}",
            )
            continue
        if source_object.phase_contract_id != contract.source_phase_contract_id:
            collector.add(
                RuleCode.TRANSITION_SOURCE_OBJECT_PHASE_MISMATCH,
                message=(
                    f"Source object '{source_object.object_contract_id}' belongs to phase_contract "
                    f"'{source_object.phase_contract_id}', expected '{contract.source_phase_contract_id}'."
                ),
                evidence_ref=f"object_contract.{source_object.object_contract_id}.phase_contract_id",
            )

    target_objects_by_id = {item.object_contract_id: item for item in target_object_contracts}
    target_objects_for_preservation: list[ObjectContract] = []
    for target_ref in contract.target_object_refs:
        target_object = target_objects_by_id.get(target_ref.identifier)
        if target_object is None:
            collector.add(
                RuleCode.TRANSITION_TARGET_OBJECT_MISSING,
                message=f"Target object '{target_ref.identifier}' was not provided for transition validation.",
                evidence_ref=f"transition_contract.target_object_refs.{target_ref.identifier}",
            )
            continue
        target_objects_for_preservation.append(target_object)
        if target_object.phase_contract_id != contract.target_phase_contract_id:
            collector.add(
                RuleCode.TRANSITION_TARGET_OBJECT_PHASE_MISMATCH,
                message=(
                    f"Target object '{target_object.object_contract_id}' belongs to phase_contract "
                    f"'{target_object.phase_contract_id}', expected '{contract.target_phase_contract_id}'."
                ),
                evidence_ref=f"object_contract.{target_object.object_contract_id}.phase_contract_id",
            )

    validate_required_metadata(
        scope_ref=contract.reference,
        required_keys=contract.required_metadata_keys,
        payload_metadata=handoff_metadata,
        collector=collector,
        evidence_root="transition_contract.handoff_metadata",
    )

    completed = {item.strip() for item in completed_preconditions if item.strip()}
    for required_precondition in contract.required_preconditions:
        if required_precondition not in completed:
            collector.add(
                RuleCode.TRANSITION_REQUIRED_PRECONDITION_MISSING,
                message=f"Required precondition '{required_precondition}' is missing.",
                evidence_ref=f"transition_contract.required_preconditions.{required_precondition}",
            )

    if requested_status_transform is not None:
        normalized_transform = requested_status_transform.strip()
        if normalized_transform in set(contract.blocked_status_transforms):
            collector.add(
                RuleCode.TRANSITION_STATUS_TRANSFORM_BLOCKED,
                message=f"Status transform '{normalized_transform}' is explicitly blocked.",
                evidence_ref=f"transition_contract.blocked_status_transforms.{normalized_transform}",
            )
        elif (
            contract.allowed_status_transforms
            and normalized_transform not in set(contract.allowed_status_transforms)
        ):
            collector.add(
                RuleCode.TRANSITION_STATUS_TRANSFORM_NOT_ALLOWED,
                message=f"Status transform '{normalized_transform}' is not allowed by the transition contract.",
                evidence_ref=f"transition_contract.allowed_status_transforms.{normalized_transform}",
            )

    for target_object in target_objects_for_preservation:
        validate_metadata_preservation(
            scope_ref=contract.reference,
            policy=target_object.metadata_preservation_policy,
            source_metadata=source_metadata,
            target_metadata=target_metadata,
            collector=collector,
            evidence_root=f"transition_contract.target_object.{target_object.object_contract_id}.metadata",
        )
