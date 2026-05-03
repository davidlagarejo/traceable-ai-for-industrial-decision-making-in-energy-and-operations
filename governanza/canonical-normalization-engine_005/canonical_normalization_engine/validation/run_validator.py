from __future__ import annotations

from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode
from ..domain.enums import NormalizationStatus
from ..domain.records import NormalizationRunRecord


def validate_normalization_run_record(
    normalization_run: NormalizationRunRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        if normalization_run.normalization_status is not NormalizationStatus.COMPLETE:
            collector.add(
                RuleCode.RUN_NON_COMPLETE_DECLARED,
                "Normalization run is not complete.",
                field_ref="normalization_status",
            )
        return
    registry = context.registries_by_id.get(normalization_run.canonical_schema_registry_id)
    if registry is None:
        collector.add(
            RuleCode.RUN_SCHEMA_REGISTRY_REFERENCE_INVALID,
            "Normalization run references a schema registry that is not present in validation context.",
            field_ref="canonical_schema_registry_id",
        )
    schema_version = context.versions_by_id.get(normalization_run.canonical_schema_version_id)
    if schema_version is None:
        collector.add(
            RuleCode.RUN_SCHEMA_VERSION_REFERENCE_INVALID,
            "Normalization run references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )
    elif schema_version.canonical_schema_registry_id != normalization_run.canonical_schema_registry_id:
        collector.add(
            RuleCode.RUN_SCHEMA_REGISTRY_MISMATCH,
            "Normalization run schema version belongs to a different schema registry.",
            field_ref="canonical_schema_version_id",
        )
    if normalization_run.normalization_status is not NormalizationStatus.COMPLETE:
        collector.add(
            RuleCode.RUN_NON_COMPLETE_DECLARED,
            "Normalization run is not complete.",
            field_ref="normalization_status",
        )
