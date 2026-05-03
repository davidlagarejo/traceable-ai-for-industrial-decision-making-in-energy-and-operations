from __future__ import annotations

from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode
from ..domain.entities import (
    CanonicalFieldDefinition,
    CanonicalSchemaRegistry,
    CanonicalSchemaVersion,
)


def validate_canonical_schema_registry(
    registry: CanonicalSchemaRegistry,
    collector: ViolationCollector,
) -> None:
    del registry, collector


def validate_canonical_schema_version(
    schema_version: CanonicalSchemaVersion,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    registry = context.registries_by_id.get(schema_version.canonical_schema_registry_id)
    if registry is None:
        collector.add(
            RuleCode.SCHEMA_VERSION_REGISTRY_REFERENCE_INVALID,
            "Canonical schema version references a registry that is not present in validation context.",
            field_ref="canonical_schema_registry_id",
        )
    supersedes_id = schema_version.supersedes_canonical_schema_version_id
    if supersedes_id is None:
        return
    superseded = context.versions_by_id.get(supersedes_id)
    if superseded is None:
        collector.add(
            RuleCode.SCHEMA_VERSION_SUPERSEDES_REFERENCE_INVALID,
            "Canonical schema version supersedes a version that is not present in validation context.",
            field_ref="supersedes_canonical_schema_version_id",
        )
        return
    if superseded.canonical_schema_registry_id != schema_version.canonical_schema_registry_id:
        collector.add(
            RuleCode.SCHEMA_VERSION_SUPERSEDES_REGISTRY_MISMATCH,
            "Superseded schema version belongs to a different schema registry.",
            field_ref="supersedes_canonical_schema_version_id",
        )


def validate_canonical_field_definition(
    field_definition: CanonicalFieldDefinition,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    if field_definition.canonical_schema_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.FIELD_SCHEMA_VERSION_REFERENCE_INVALID,
            "Canonical field definition references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )
