from __future__ import annotations

from ..domain.enums import ChangeKind
from ..domain.value_objects import ChangeDescriptor
from .models import ChangeImpact, ClassifiedChange


def classify_changes(changes: tuple[ChangeDescriptor, ...]) -> tuple[ClassifiedChange, ...]:
    return tuple(classify_change(change) for change in changes)


def classify_change(change: ChangeDescriptor) -> ClassifiedChange:
    path = change.path
    kind = change.change_kind

    if kind is ChangeKind.ADDITIVE:
        return ClassifiedChange(
            descriptor=change,
            impact=ChangeImpact.ADDITIVE,
            migration_required=False,
            rationale="Additive change that does not tighten the accepted contract shape.",
        )

    if kind is ChangeKind.RESTRICTIVE:
        return ClassifiedChange(
            descriptor=change,
            impact=ChangeImpact.RESTRICTIVE,
            migration_required=True,
            rationale="Restrictive change that may require payload adjustment before direct reuse.",
        )

    if kind is ChangeKind.REMOVAL:
        return ClassifiedChange(
            descriptor=change,
            impact=ChangeImpact.BREAKING,
            migration_required=False,
            rationale="Removal of previously supported contract surface is treated as breaking.",
        )

    if kind is ChangeKind.RENAME:
        return ClassifiedChange(
            descriptor=change,
            impact=ChangeImpact.BREAKING,
            migration_required=False,
            rationale="Rename changes are treated conservatively as breaking.",
        )

    if kind is ChangeKind.SEMANTIC_CHANGE:
        if path in {"source_phase_contract_id", "target_phase_contract_id", "transition_name"} or path.startswith(
            ("source_object_refs.", "target_object_refs.")
        ):
            return ClassifiedChange(
                descriptor=change,
                impact=ChangeImpact.BREAKING,
                migration_required=False,
                rationale="Transition topology or semantic identity changed in a breaking way.",
            )
        return ClassifiedChange(
            descriptor=change,
            impact=ChangeImpact.UNKNOWN,
            migration_required=False,
            rationale="Semantic change cannot yet be classified safely and is treated conservatively later.",
        )

    if kind is ChangeKind.METADATA_CHANGE:
        if path.startswith(("required_metadata_keys.", "metadata_preservation_policy.required_keys.")):
            if change.description.startswith("Added"):
                return ClassifiedChange(
                    descriptor=change,
                    impact=ChangeImpact.RESTRICTIVE,
                    migration_required=True,
                    rationale="New required metadata introduces migration pressure for existing payloads.",
                )
            return ClassifiedChange(
                descriptor=change,
                impact=ChangeImpact.BREAKING,
                migration_required=False,
                rationale="Removing required metadata is treated conservatively as breaking.",
            )

        if path.startswith("metadata_preservation_policy.immutable_keys."):
            if change.description.startswith("Added"):
                return ClassifiedChange(
                    descriptor=change,
                    impact=ChangeImpact.RESTRICTIVE,
                    migration_required=True,
                    rationale="New immutable metadata constraints may require payload or producer adjustment.",
                )
            return ClassifiedChange(
                descriptor=change,
                impact=ChangeImpact.ADDITIVE,
                migration_required=False,
                rationale="Relaxing immutable metadata constraints is additive.",
            )

        if path.startswith("metadata_preservation_policy.passthrough_keys."):
            if change.description.startswith("Added"):
                return ClassifiedChange(
                    descriptor=change,
                    impact=ChangeImpact.ADDITIVE,
                    migration_required=False,
                    rationale="Preserving additional passthrough metadata is additive.",
                )
            return ClassifiedChange(
                descriptor=change,
                impact=ChangeImpact.RESTRICTIVE,
                migration_required=True,
                rationale="Dropping passthrough metadata can require migration or producer changes.",
            )

        return ClassifiedChange(
            descriptor=change,
            impact=ChangeImpact.UNKNOWN,
            migration_required=False,
            rationale="Metadata policy change needs conservative treatment until more rules exist.",
        )

    return ClassifiedChange(
        descriptor=change,
        impact=ChangeImpact.UNKNOWN,
        migration_required=False,
        rationale="Unknown change classification fallback.",
    )
