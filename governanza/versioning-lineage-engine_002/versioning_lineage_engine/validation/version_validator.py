from __future__ import annotations

from ..domain.entities import ObjectIdentity, ObjectVersion
from ..domain.enums import VersionLifecycleStatus
from ..domain.value_objects import ObjectIdentityId, ObjectVersionId
from .collector import ViolationCollector
from .context import ValidationContext
from .rebuild_validator import validate_rebuild_manifest
from .rules import RuleCode


def validate_object_version(
    version: ObjectVersion,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
    object_identity: ObjectIdentity | None = None,
) -> None:
    if not isinstance(version.object_version_id, ObjectVersionId):
        collector.add(RuleCode.VERSION_ID_INVALID, "object_version_id must be an ObjectVersionId.")
    if not isinstance(version.object_identity_id, ObjectIdentityId):
        collector.add(
            RuleCode.VERSION_IDENTITY_REFERENCE_INVALID,
            "object_identity_id must be an ObjectIdentityId.",
            field_ref="object_identity_id",
        )
    if not isinstance(version.version_status, VersionLifecycleStatus):
        collector.add(
            RuleCode.VERSION_STATUS_INVALID,
            "version_status must be a supported VersionLifecycleStatus enum value.",
            field_ref="version_status",
        )

    if object_identity is not None and version.object_identity_id != object_identity.object_identity_id:
        collector.add(
            RuleCode.VERSION_IDENTITY_REFERENCE_INVALID,
            "ObjectVersion must reference exactly the validated ObjectIdentity.",
            field_ref="object_identity_id",
        )

    if context is not None and version.object_identity_id not in context.identities_by_id:
        collector.add(
            RuleCode.VERSION_IDENTITY_REFERENCE_INVALID,
            "ObjectVersion must reference a known ObjectIdentity.",
            field_ref="object_identity_id",
        )

    validate_rebuild_manifest(
        version.rebuild_manifest,
        collector,
        context=context,
        object_version=version,
    )
