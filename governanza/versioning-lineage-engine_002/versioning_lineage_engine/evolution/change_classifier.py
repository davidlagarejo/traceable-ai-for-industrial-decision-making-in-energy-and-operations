from __future__ import annotations

from ..domain.enums import ChangeSeverity, ImpactSeverity, StaleState
from ..domain.value_objects import ChangeDescriptor
from .models import DiffClassification


def classify_change_set(change_set: tuple[ChangeDescriptor, ...]) -> DiffClassification:
    if not change_set:
        return DiffClassification.NON_MATERIAL

    if any(_is_rebuild_required_change(item) for item in change_set):
        return DiffClassification.REBUILD_REQUIRED
    if any(_is_breaking_change(item) for item in change_set):
        return DiffClassification.BREAKING_FOR_DOWNSTREAM
    if any(_is_rebuild_recommended_change(item) for item in change_set):
        return DiffClassification.REBUILD_RECOMMENDED
    if any(_is_material_change(item) for item in change_set):
        return DiffClassification.MATERIAL
    return DiffClassification.NON_MATERIAL


def stale_state_for_classification(classification: DiffClassification) -> StaleState | None:
    if classification in {DiffClassification.MATERIAL, DiffClassification.REBUILD_RECOMMENDED}:
        return StaleState.STALE_REBUILD_RECOMMENDED
    if classification is DiffClassification.REBUILD_REQUIRED:
        return StaleState.STALE_MIGRATION_REQUIRED
    if classification is DiffClassification.BREAKING_FOR_DOWNSTREAM:
        return StaleState.STALE_BLOCKED
    return None


def impact_severity_for_classification(classification: DiffClassification) -> ImpactSeverity | None:
    if classification is DiffClassification.NON_MATERIAL:
        return None
    if classification is DiffClassification.MATERIAL:
        return ImpactSeverity.MODERATE
    if classification is DiffClassification.REBUILD_RECOMMENDED:
        return ImpactSeverity.MODERATE
    if classification is DiffClassification.REBUILD_REQUIRED:
        return ImpactSeverity.HIGH
    return ImpactSeverity.CRITICAL


def requires_rebuild_for_classification(classification: DiffClassification) -> bool:
    return classification in {
        DiffClassification.MATERIAL,
        DiffClassification.REBUILD_RECOMMENDED,
        DiffClassification.REBUILD_REQUIRED,
    }


def migration_required_for_classification(classification: DiffClassification) -> bool:
    return classification in {
        DiffClassification.REBUILD_REQUIRED,
        DiffClassification.BREAKING_FOR_DOWNSTREAM,
    }


def _is_rebuild_required_change(change: ChangeDescriptor) -> bool:
    return change.path.startswith(
        (
            "rebuild_manifest.contract_version_refs",
            "rebuild_manifest.taxonomy_version_refs",
            "rebuild_manifest.rule_pack_version_refs",
        )
    )


def _is_breaking_change(change: ChangeDescriptor) -> bool:
    return change.severity is ChangeSeverity.BREAKING


def _is_rebuild_recommended_change(change: ChangeDescriptor) -> bool:
    return change.path.startswith(
        (
            "dependency_snapshot",
            "rebuild_manifest.required_dependency_refs",
            "rebuild_manifest.library_version_refs",
            "rebuild_manifest.model_version_refs",
        )
    )


def _is_material_change(change: ChangeDescriptor) -> bool:
    if change.path in {"producer_engine_name", "producer_engine_version"}:
        return False
    return change.severity in {ChangeSeverity.ADDITIVE, ChangeSeverity.RESTRICTIVE}
