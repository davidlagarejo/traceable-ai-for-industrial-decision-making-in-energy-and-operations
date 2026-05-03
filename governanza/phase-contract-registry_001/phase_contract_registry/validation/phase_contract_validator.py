from __future__ import annotations

from collections.abc import Iterable, Mapping

from ..domain.entities import ObjectContract, PhaseContract, TransitionContract
from .collector import ViolationCollector
from .metadata_validator import validate_required_metadata
from .rules import RuleCode


def validate_phase_contract(
    contract: PhaseContract,
    collector: ViolationCollector,
    *,
    object_contracts: Iterable[ObjectContract] = (),
    transition_contracts: Iterable[TransitionContract] = (),
    payload_metadata: Mapping[str, object] | None = None,
) -> None:
    validate_required_metadata(
        scope_ref=contract.reference,
        required_keys=contract.required_metadata_keys,
        payload_metadata=payload_metadata,
        collector=collector,
        evidence_root="phase_contract.metadata",
    )

    provided_objects = {item.object_contract_id: item for item in object_contracts}
    for expected_object_id in contract.object_contract_ids:
        if expected_object_id not in provided_objects:
            collector.add(
                RuleCode.PHASE_DECLARED_OBJECT_MISSING,
                message=f"Declared object_contract '{expected_object_id}' was not provided for validation.",
                evidence_ref=f"phase_contract.object_contract_ids.{expected_object_id}",
            )

    for object_contract in provided_objects.values():
        if object_contract.phase_contract_id != contract.phase_contract_id:
            collector.add(
                RuleCode.PHASE_OBJECT_PHASE_MISMATCH,
                message=(
                    f"ObjectContract '{object_contract.object_contract_id}' points to phase_contract "
                    f"'{object_contract.phase_contract_id}', expected '{contract.phase_contract_id}'."
                ),
                evidence_ref=f"object_contract.{object_contract.object_contract_id}.phase_contract_id",
            )
        elif object_contract.object_contract_id not in set(contract.object_contract_ids):
            collector.add(
                RuleCode.PHASE_UNDECLARED_OBJECT_PROVIDED,
                message=(
                    f"ObjectContract '{object_contract.object_contract_id}' was provided but is not declared "
                    "by the phase contract."
                ),
                evidence_ref=f"object_contract.{object_contract.object_contract_id}",
            )

    provided_transitions = {item.transition_contract_id: item for item in transition_contracts}
    for expected_transition_id in contract.transition_contract_ids:
        if expected_transition_id not in provided_transitions:
            collector.add(
                RuleCode.PHASE_DECLARED_TRANSITION_MISSING,
                message=(
                    f"Declared transition_contract '{expected_transition_id}' was not provided for validation."
                ),
                evidence_ref=f"phase_contract.transition_contract_ids.{expected_transition_id}",
            )

    for transition_contract in provided_transitions.values():
        references_phase = (
            transition_contract.source_phase_contract_id == contract.phase_contract_id
            or transition_contract.target_phase_contract_id == contract.phase_contract_id
        )
        if not references_phase:
            collector.add(
                RuleCode.PHASE_TRANSITION_PHASE_MISMATCH,
                message=(
                    f"TransitionContract '{transition_contract.transition_contract_id}' does not reference "
                    f"phase_contract '{contract.phase_contract_id}'."
                ),
                evidence_ref=f"transition_contract.{transition_contract.transition_contract_id}",
            )
        elif transition_contract.transition_contract_id not in set(contract.transition_contract_ids):
            collector.add(
                RuleCode.PHASE_UNDECLARED_TRANSITION_PROVIDED,
                message=(
                    f"TransitionContract '{transition_contract.transition_contract_id}' was provided but is "
                    "not declared by the phase contract."
                ),
                evidence_ref=f"transition_contract.{transition_contract.transition_contract_id}",
            )
