from __future__ import annotations

from ..domain.entities import ObjectIdentity
from ..domain.enums import IdentityStatus, ObjectKind, PhaseId
from ..domain.value_objects import ObjectIdentityId
from .collector import ViolationCollector
from .rules import RuleCode


def validate_object_identity(identity: ObjectIdentity, collector: ViolationCollector) -> None:
    if not isinstance(identity.object_identity_id, ObjectIdentityId):
        collector.add(RuleCode.IDENTITY_ID_INVALID, "object_identity_id must be an ObjectIdentityId.")
    if not isinstance(identity.object_kind, ObjectKind):
        collector.add(
            RuleCode.IDENTITY_KIND_INVALID,
            "object_kind must be a supported ObjectKind enum value.",
            field_ref="object_kind",
        )
    if identity.phase_scope is not None and not isinstance(identity.phase_scope, PhaseId):
        collector.add(
            RuleCode.IDENTITY_PHASE_SCOPE_INVALID,
            "phase_scope must be a supported PhaseId or None.",
            field_ref="phase_scope",
        )
    if not isinstance(identity.identity_status, IdentityStatus):
        collector.add(
            RuleCode.IDENTITY_STATUS_INVALID,
            "identity_status must be a supported IdentityStatus enum value.",
            field_ref="identity_status",
        )
        return

    if identity.identity_status is IdentityStatus.REPLACEMENT:
        if identity.replacement_of_identity_id is None:
            collector.add(
                RuleCode.IDENTITY_REPLACEMENT_STATE_INCOHERENT,
                "Replacement identities must declare replacement_of_identity_id.",
                field_ref="replacement_of_identity_id",
            )
    elif identity.replacement_of_identity_id is not None:
        collector.add(
            RuleCode.IDENTITY_REPLACEMENT_STATE_INCOHERENT,
            "Only replacement identities may declare replacement_of_identity_id.",
            field_ref="replacement_of_identity_id",
        )

    if identity.identity_status is IdentityStatus.REPLACED:
        if identity.replaced_by_identity_id is None:
            collector.add(
                RuleCode.IDENTITY_REPLACEMENT_STATE_INCOHERENT,
                "Replaced identities must declare replaced_by_identity_id.",
                field_ref="replaced_by_identity_id",
            )
    elif identity.replaced_by_identity_id is not None:
        collector.add(
            RuleCode.IDENTITY_REPLACEMENT_STATE_INCOHERENT,
            "Only replaced identities may declare replaced_by_identity_id.",
            field_ref="replaced_by_identity_id",
        )
