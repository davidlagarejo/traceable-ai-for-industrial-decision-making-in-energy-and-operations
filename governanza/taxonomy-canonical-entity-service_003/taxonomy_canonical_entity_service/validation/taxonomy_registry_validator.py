from __future__ import annotations

from ..domain.entities import TaxonomyRegistry
from ..domain.enums import TaxonomyRegistryStatus
from .collector import ViolationCollector
from .rules import RuleCode


def validate_taxonomy_registry(
    registry: TaxonomyRegistry,
    collector: ViolationCollector,
) -> None:
    if not registry.taxonomy_registry_id.value:
        collector.add(
            RuleCode.REGISTRY_ID_INVALID,
            "taxonomy_registry_id must be present.",
            field_ref="taxonomy_registry_id",
        )
    if registry.registry_status is not TaxonomyRegistryStatus.ACTIVE:
        collector.add(
            RuleCode.REGISTRY_NON_ACTIVE_DECLARED,
            f"taxonomy registry is declared as {registry.registry_status.value}.",
            field_ref="registry_status",
        )

