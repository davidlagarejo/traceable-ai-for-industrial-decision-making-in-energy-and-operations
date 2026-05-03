from __future__ import annotations

from datetime import datetime, timezone
import hashlib

from ..domain.enums import CompatibilityStatus
from ..domain.records import CompatibilityRecord
from ..domain.value_objects import EntityId
from .differ import diff_contracts
from .models import (
    ChangeImpact,
    CompatibilityDecision,
    CompatibilityEvaluation,
    ContractDiffResult,
)


def evaluate_contract_compatibility(
    source,
    target,
    *,
    generated_at: datetime | None = None,
) -> CompatibilityEvaluation:
    diff_result = diff_contracts(source, target, generated_at=generated_at)
    decision, reasons = _derive_decision(diff_result)
    compatibility_record = CompatibilityRecord(
        compatibility_record_id=_stable_entity_id(
            "compatibility",
            diff_result.source_contract_type,
            diff_result.target_contract_type,
            _decision_signature(decision, reasons),
            *(
                item.descriptor.path + ":" + item.impact.value
                for item in diff_result.classified_changes
            ),
        ),
        scope_kind=(diff_result.diff_record.scope_kind if diff_result.diff_record is not None else source.reference.scope_kind),
        source_ref=source.reference,
        target_ref=target.reference,
        compatibility_status=_to_domain_status(decision),
        breaking_reasons=reasons,
        migration_required=decision is CompatibilityDecision.MIGRATION_REQUIRED,
        generated_at=generated_at or datetime.now(timezone.utc),
    )
    return CompatibilityEvaluation(
        decision=decision,
        migration_required=decision is CompatibilityDecision.MIGRATION_REQUIRED,
        reasons=reasons,
        diff_result=diff_result,
        compatibility_record=compatibility_record,
    )


def _derive_decision(diff_result: ContractDiffResult) -> tuple[CompatibilityDecision, tuple[str, ...]]:
    if not diff_result.has_changes:
        return CompatibilityDecision.COMPATIBLE, ()

    breaking = tuple(
        _reason_for(change) for change in diff_result.classified_changes if change.impact is ChangeImpact.BREAKING
    )
    if breaking:
        return CompatibilityDecision.INCOMPATIBLE, breaking

    unknown = tuple(
        _reason_for(change) for change in diff_result.classified_changes if change.impact is ChangeImpact.UNKNOWN
    )
    if unknown:
        return CompatibilityDecision.INCOMPATIBLE, unknown

    restrictive = tuple(
        _reason_for(change) for change in diff_result.classified_changes if change.impact is ChangeImpact.RESTRICTIVE
    )
    if restrictive:
        return CompatibilityDecision.MIGRATION_REQUIRED, restrictive

    return CompatibilityDecision.COMPATIBLE, ()


def _reason_for(change) -> str:
    return f"{change.descriptor.path}: {change.rationale}"


def _to_domain_status(decision: CompatibilityDecision) -> CompatibilityStatus:
    if decision is CompatibilityDecision.COMPATIBLE:
        return CompatibilityStatus.COMPATIBLE
    if decision is CompatibilityDecision.MIGRATION_REQUIRED:
        return CompatibilityStatus.CONDITIONALLY_COMPATIBLE
    return CompatibilityStatus.INCOMPATIBLE


def _stable_entity_id(prefix: str, *parts: str) -> EntityId:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return EntityId(f"{prefix}:{digest}")


def _decision_signature(decision: CompatibilityDecision, reasons: tuple[str, ...]) -> str:
    return "|".join((decision.value, *reasons))
