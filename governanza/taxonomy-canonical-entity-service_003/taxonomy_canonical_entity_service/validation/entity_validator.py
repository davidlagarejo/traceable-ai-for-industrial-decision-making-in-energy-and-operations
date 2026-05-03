from __future__ import annotations

from ..domain.entities import CanonicalEntity, EntityMembershipRecord
from ..domain.enums import EntityStatus, MembershipStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_canonical_entity(
    entity: CanonicalEntity,
    collector: ViolationCollector,
) -> None:
    if not entity.canonical_entity_id.value:
        collector.add(
            RuleCode.ENTITY_ID_INVALID,
            "canonical_entity_id must be present.",
            field_ref="canonical_entity_id",
        )
    if entity.entity_status is not EntityStatus.ACTIVE:
        collector.add(
            RuleCode.ENTITY_NON_ACTIVE_DECLARED,
            f"canonical entity is declared as {entity.entity_status.value}.",
            field_ref="entity_status",
        )


def validate_entity_membership_record(
    membership: EntityMembershipRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if not membership.entity_membership_record_id.value:
        collector.add(
            RuleCode.MEMBERSHIP_ID_INVALID,
            "entity_membership_record_id must be present.",
            field_ref="entity_membership_record_id",
        )
    if context is None or membership.canonical_entity_id not in context.entities_by_id:
        collector.add(
            RuleCode.MEMBERSHIP_ENTITY_REFERENCE_INVALID,
            "entity_membership_record must reference an existing canonical_entity.",
            field_ref="canonical_entity_id",
        )
    if context is None or membership.taxonomy_node_id not in context.nodes_by_id:
        collector.add(
            RuleCode.MEMBERSHIP_NODE_REFERENCE_INVALID,
            "entity_membership_record must reference an existing taxonomy_node.",
            field_ref="taxonomy_node_id",
        )
    if membership.membership_status is not MembershipStatus.ACTIVE:
        collector.add(
            RuleCode.MEMBERSHIP_NON_ACTIVE_DECLARED,
            f"entity membership is declared as {membership.membership_status.value}.",
            field_ref="membership_status",
        )

