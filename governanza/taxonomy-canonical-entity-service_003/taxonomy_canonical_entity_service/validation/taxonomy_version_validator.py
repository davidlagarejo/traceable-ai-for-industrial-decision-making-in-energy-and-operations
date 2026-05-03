from __future__ import annotations

from ..domain.entities import TaxonomyRegistry, TaxonomyVersion
from ..domain.enums import TaxonomyVersionStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_taxonomy_version(
    version: TaxonomyVersion,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
    taxonomy_registry: TaxonomyRegistry | None = None,
) -> None:
    if not version.taxonomy_version_id.value:
        collector.add(
            RuleCode.VERSION_ID_INVALID,
            "taxonomy_version_id must be present.",
            field_ref="taxonomy_version_id",
        )
    registry = taxonomy_registry
    if registry is None and context is not None:
        registry = context.registries_by_id.get(version.taxonomy_registry_id)
    if registry is None:
        collector.add(
            RuleCode.VERSION_REGISTRY_REFERENCE_INVALID,
            "taxonomy_version must reference an existing taxonomy_registry.",
            field_ref="taxonomy_registry_id",
        )
    if version.version_status is not TaxonomyVersionStatus.ACTIVE:
        collector.add(
            RuleCode.VERSION_NON_ACTIVE_DECLARED,
            f"taxonomy version is declared as {version.version_status.value}.",
            field_ref="version_status",
        )

