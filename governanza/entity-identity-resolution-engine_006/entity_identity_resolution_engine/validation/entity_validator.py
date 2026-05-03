from __future__ import annotations

from ..domain.entities import CanonicalEntity, EntityAliasRecord
from ..domain.enums import CanonicalEntityStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_canonical_entity(
    canonical_entity: CanonicalEntity,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if canonical_entity.entity_status is not CanonicalEntityStatus.ACTIVE:
        collector.add(
            RuleCode.ENTITY_NON_ACTIVE_DECLARED,
            "CanonicalEntity is in a non-active lifecycle state and should be consumed with historical care.",
            field_ref="entity_status",
        )


def validate_entity_alias_record(
    entity_alias_record: EntityAliasRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if entity_alias_record.entity_id not in context.entities_by_id:
        collector.add(
            RuleCode.ALIAS_ENTITY_REFERENCE_INVALID,
            "EntityAliasRecord entity_id is not resolvable in the validation context.",
            field_ref="entity_id",
        )
    if (
        entity_alias_record.source_observed_name_record_id is not None
        and entity_alias_record.source_observed_name_record_id not in context.observed_names_by_id
    ):
        collector.add(
            RuleCode.ALIAS_OBSERVED_NAME_REFERENCE_INVALID,
            "EntityAliasRecord source_observed_name_record_id is not resolvable in the validation context.",
            field_ref="source_observed_name_record_id",
        )
