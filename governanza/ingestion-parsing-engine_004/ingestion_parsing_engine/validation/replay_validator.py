from __future__ import annotations

from ..domain.records import ReplayManifestRecord
from ..domain.enums import ParsingScopeKind, ReplayabilityStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_replay_manifest_record(
    manifest: ReplayManifestRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if manifest.replayability_status is not ReplayabilityStatus.REPLAYABLE:
        collector.add(
            RuleCode.REPLAY_NOT_FULLY_REPLAYABLE,
            f"Replay manifest declares {manifest.replayability_status.value}.",
            field_ref="replayability_status",
        )

    if context is None:
        return

    raw_version = context.raw_versions_by_id.get(manifest.raw_asset_version_record_id)
    if raw_version is None:
        collector.add(
            RuleCode.REPLAY_RAW_VERSION_REFERENCE_INVALID,
            "ReplayManifestRecord references an unknown raw_asset_version_record.",
            field_ref="raw_asset_version_record_id",
        )

    strategy = context.strategies_by_id.get(manifest.parser_strategy_record_id)
    if strategy is None:
        collector.add(
            RuleCode.REPLAY_STRATEGY_REFERENCE_INVALID,
            "ReplayManifestRecord references an unknown parser_strategy_record.",
            field_ref="parser_strategy_record_id",
        )

    metadata = context.extractions_by_id.get(manifest.extraction_metadata_record_id)
    if metadata is None:
        collector.add(
            RuleCode.REPLAY_EXTRACTION_REFERENCE_INVALID,
            "ReplayManifestRecord references an unknown extraction_metadata_record.",
            field_ref="extraction_metadata_record_id",
        )
    else:
        mismatch_fields: list[str] = []
        if metadata.raw_asset_version_record_id != manifest.raw_asset_version_record_id:
            mismatch_fields.append("raw_asset_version_record_id")
        if metadata.parser_strategy_record_id != manifest.parser_strategy_record_id:
            mismatch_fields.append("parser_strategy_record_id")
        if mismatch_fields:
            collector.add(
                RuleCode.REPLAY_METADATA_MISMATCH,
                "Replay manifest is inconsistent with extraction metadata on: "
                + ", ".join(mismatch_fields)
                + ".",
            )

    if raw_version is not None and raw_version.content_checksum != manifest.raw_content_checksum:
        collector.add(
            RuleCode.REPLAY_CHECKSUM_MISMATCH,
            "Replay manifest raw_content_checksum does not match the referenced raw asset version.",
            field_ref="raw_content_checksum",
        )

    for output_ref in manifest.expected_output_refs:
        if not context.contains_scope_ref(output_ref):
            collector.add(
                RuleCode.REPLAY_OUTPUT_REFERENCE_INVALID,
                "Replay manifest references an unknown expected output scope.",
                field_ref="expected_output_refs",
            )
            continue

        if output_ref.scope_kind is ParsingScopeKind.EXTRACTION_METADATA:
            if output_ref.identifier != manifest.extraction_metadata_record_id:
                collector.add(
                    RuleCode.REPLAY_OUTPUT_PROVENANCE_MISMATCH,
                    "Replay manifest expected extraction metadata does not match the manifest extraction.",
                    field_ref="expected_output_refs",
                )
            continue

        raw_version_id = context.raw_version_id_for_scope(output_ref)
        if raw_version_id is not None and raw_version_id != manifest.raw_asset_version_record_id:
            collector.add(
                RuleCode.REPLAY_OUTPUT_PROVENANCE_MISMATCH,
                "Replay manifest expected output points to a different raw asset version.",
                field_ref="expected_output_refs",
            )
