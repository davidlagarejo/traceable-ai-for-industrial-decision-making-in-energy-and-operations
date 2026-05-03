from __future__ import annotations

from collections.abc import Mapping

from ..domain.entities import ObjectContract, PhaseContract
from .collector import ViolationCollector
from .metadata_validator import validate_required_metadata
from .rules import RuleCode


def validate_object_contract(
    contract: ObjectContract,
    collector: ViolationCollector,
    *,
    phase_contract: PhaseContract | None = None,
    payload_metadata: Mapping[str, object] | None = None,
) -> None:
    if phase_contract is not None:
        if contract.phase_contract_id != phase_contract.phase_contract_id:
            collector.add(
                RuleCode.OBJECT_PHASE_REFERENCE_MISMATCH,
                message=(
                    f"ObjectContract '{contract.object_contract_id}' points to phase_contract "
                    f"'{contract.phase_contract_id}', expected '{phase_contract.phase_contract_id}'."
                ),
                evidence_ref="object_contract.phase_contract_id",
            )
        elif contract.object_contract_id not in set(phase_contract.object_contract_ids):
            collector.add(
                RuleCode.OBJECT_NOT_DECLARED_BY_PHASE,
                message=(
                    f"ObjectContract '{contract.object_contract_id}' is not declared by phase_contract "
                    f"'{phase_contract.phase_contract_id}'."
                ),
                evidence_ref=f"phase_contract.object_contract_ids.{contract.object_contract_id}",
            )

    if not contract.required_fields and not contract.optional_fields and not contract.forbidden_fields:
        collector.add(
            RuleCode.OBJECT_EMPTY_FIELD_SHAPE,
            message="ObjectContract does not declare required, optional or forbidden fields.",
            evidence_ref="object_contract.fields",
        )

    if not contract.allowed_epistemic_state_tokens and not contract.forbidden_epistemic_state_tokens:
        collector.add(
            RuleCode.OBJECT_EMPTY_EPISTEMIC_TOKEN_SET,
            message="ObjectContract does not declare allowed or forbidden epistemic state tokens.",
            evidence_ref="object_contract.epistemic_state_tokens",
        )

    validate_required_metadata(
        scope_ref=contract.reference,
        required_keys=contract.required_metadata_keys,
        payload_metadata=payload_metadata,
        collector=collector,
        evidence_root="object_contract.metadata",
    )
