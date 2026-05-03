from __future__ import annotations

from ..domain.entities import RawAssetRecord, RawAssetVersionRecord
from ..domain.enums import RetrievalStatus, SourceFormatFamily
from .collector import ViolationCollector
from .context import ValidationContext
from .request_validator import ALLOWED_FORMATS_BY_RAW_ASSET_KIND
from .rules import RuleCode


def validate_raw_asset_record(
    raw_asset: RawAssetRecord,
    collector: ViolationCollector,
) -> None:
    allowed_formats = ALLOWED_FORMATS_BY_RAW_ASSET_KIND[raw_asset.raw_asset_kind]
    if raw_asset.declared_format not in allowed_formats:
        collector.add(
            RuleCode.RAW_ASSET_FORMAT_INCOHERENT,
            (
                "RawAssetRecord.declared_format is incompatible with raw_asset_kind: "
                f"{raw_asset.raw_asset_kind.value} -> {raw_asset.declared_format.value}."
            ),
            field_ref="declared_format",
        )


def validate_raw_asset_version_record(
    raw_asset_version: RawAssetVersionRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return

    raw_asset = context.raw_assets_by_id.get(raw_asset_version.raw_asset_record_id)
    if raw_asset is None:
        collector.add(
            RuleCode.RAW_VERSION_RAW_ASSET_REFERENCE_INVALID,
            "RawAssetVersionRecord references an unknown raw_asset_record.",
            field_ref="raw_asset_record_id",
        )

    retrieval = context.retrievals_by_id.get(raw_asset_version.retrieval_record_id)
    if retrieval is None:
        collector.add(
            RuleCode.RAW_VERSION_RETRIEVAL_REFERENCE_INVALID,
            "RawAssetVersionRecord references an unknown retrieval_record.",
            field_ref="retrieval_record_id",
        )
        return

    if retrieval.raw_asset_record_id != raw_asset_version.raw_asset_record_id:
        collector.add(
            RuleCode.RAW_VERSION_RETRIEVAL_RAW_MISMATCH,
            "RawAssetVersionRecord.raw_asset_record_id does not match its retrieval raw asset.",
            field_ref="raw_asset_record_id",
        )

    if retrieval.retrieval_status is RetrievalStatus.FAILED:
        collector.add(
            RuleCode.RAW_VERSION_CAPTURE_FROM_FAILED_RETRIEVAL,
            "RawAssetVersionRecord must not be anchored to a FAILED retrieval.",
            field_ref="retrieval_record_id",
        )

    if raw_asset is not None:
        if (
            raw_asset.declared_format is not SourceFormatFamily.UNKNOWN
            and raw_asset.declared_format != raw_asset_version.detected_format
        ):
            collector.add(
                RuleCode.RAW_VERSION_FORMAT_DIVERGENCE,
                (
                    "RawAssetVersionRecord.detected_format diverges from raw asset declared_format: "
                    f"{raw_asset.declared_format.value} -> {raw_asset_version.detected_format.value}."
                ),
                field_ref="detected_format",
            )
