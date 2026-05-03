from __future__ import annotations

from ..domain.entities import ObjectVersion
from ..domain.enums import RebuildabilityStatus, ReferenceKind
from ..domain.value_objects import ExternalDependencyRef, LineageLocator, RebuildManifest
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_rebuild_manifest(
    manifest: RebuildManifest,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
    object_version: ObjectVersion | None = None,
) -> None:
    if object_version is not None:
        if manifest.target_object_version_id != object_version.object_version_id:
            collector.add(
                RuleCode.REBUILD_TARGET_VERSION_INVALID,
                "RebuildManifest.target_object_version_id must match the validated object version.",
                field_ref="target_object_version_id",
            )
        if manifest.expected_content_checksum != object_version.content_checksum:
            collector.add(
                RuleCode.REBUILD_VERSION_ALIGNMENT_MISMATCH,
                "Rebuild manifest checksum must match ObjectVersion.content_checksum.",
                field_ref="expected_content_checksum",
            )
        if manifest.schema_fingerprint != object_version.schema_fingerprint:
            collector.add(
                RuleCode.REBUILD_VERSION_ALIGNMENT_MISMATCH,
                "Rebuild manifest schema_fingerprint must match ObjectVersion.schema_fingerprint.",
                field_ref="schema_fingerprint",
            )
        if manifest.producer_engine_name != object_version.producer_engine_name:
            collector.add(
                RuleCode.REBUILD_VERSION_ALIGNMENT_MISMATCH,
                "Rebuild manifest producer_engine_name must match ObjectVersion.producer_engine_name.",
                field_ref="producer_engine_name",
            )
        if manifest.producer_engine_version != object_version.producer_engine_version:
            collector.add(
                RuleCode.REBUILD_VERSION_ALIGNMENT_MISMATCH,
                "Rebuild manifest producer_engine_version must match ObjectVersion.producer_engine_version.",
                field_ref="producer_engine_version",
            )

    if context is not None and manifest.target_object_version_id not in context.versions_by_id:
        collector.add(
            RuleCode.REBUILD_TARGET_VERSION_INVALID,
            "Rebuild manifest must point to a known object version.",
            field_ref="target_object_version_id",
        )

    for locator in manifest.required_dependency_refs:
        _validate_required_locator(locator, collector, context)

    for field_name, expected_kind, refs in (
        ("contract_version_refs", ReferenceKind.CONTRACT_VERSION, manifest.contract_version_refs),
        ("taxonomy_version_refs", ReferenceKind.TAXONOMY_VERSION, manifest.taxonomy_version_refs),
        ("rule_pack_version_refs", ReferenceKind.RULE_PACK_VERSION, manifest.rule_pack_version_refs),
        ("library_version_refs", ReferenceKind.LIBRARY_VERSION, manifest.library_version_refs),
        ("model_version_refs", ReferenceKind.MODEL_VERSION, manifest.model_version_refs),
    ):
        for item in refs:
            _validate_external_ref(
                item,
                expected_kind=expected_kind,
                field_name=field_name,
                collector=collector,
                context=context,
            )

    if manifest.rebuildability_status is RebuildabilityStatus.PARTIALLY_REBUILDABLE:
        collector.add(
            RuleCode.REBUILD_PARTIAL,
            "The rebuild manifest is only partially rebuildable.",
            field_ref="rebuildability_status",
        )
    elif manifest.rebuildability_status is RebuildabilityStatus.NOT_REBUILDABLE:
        collector.add(
            RuleCode.REBUILD_NOT_REBUILDABLE,
            "The rebuild manifest is not rebuildable.",
            field_ref="rebuildability_status",
        )


def _validate_required_locator(
    locator: LineageLocator,
    collector: ViolationCollector,
    context: ValidationContext | None,
) -> None:
    if context is not None and not context.contains_locator(locator):
        collector.add(
            RuleCode.REBUILD_REQUIRED_REF_UNRESOLVED,
            "Rebuild manifest required_dependency_refs must resolve to known lineage objects.",
            field_ref="required_dependency_refs",
        )


def _validate_external_ref(
    item: ExternalDependencyRef,
    *,
    expected_kind: ReferenceKind,
    field_name: str,
    collector: ViolationCollector,
    context: ValidationContext | None,
) -> None:
    if item.reference_kind is not expected_kind:
        collector.add(
            RuleCode.REBUILD_EXTERNAL_REF_KIND_MISMATCH,
            f"{field_name} must only contain {expected_kind.value} references.",
            field_ref=field_name,
        )
    if context is not None and item.reference_version_record_id not in context.references_by_id:
        collector.add(
            RuleCode.REBUILD_EXTERNAL_REF_UNRESOLVED,
            f"{field_name} must resolve to known reference version records.",
            field_ref=field_name,
        )
