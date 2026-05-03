from __future__ import annotations

from ..domain.records import ExtractionMetadataRecord
from ..domain.enums import ParsingStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_extraction_metadata_record(
    metadata: ExtractionMetadataRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if metadata.parsing_status is ParsingStatus.PARTIAL:
        collector.add(
            RuleCode.EXTRACTION_PARTIAL_DECLARED,
            "Extraction metadata declares PARTIAL parsing status.",
            field_ref="parsing_status",
        )
    if metadata.parsing_status is ParsingStatus.FAILED:
        collector.add(
            RuleCode.EXTRACTION_FAILED_DECLARED,
            "Extraction metadata declares FAILED parsing status.",
            field_ref="parsing_status",
        )

    if context is None:
        return

    raw_version = context.raw_versions_by_id.get(metadata.raw_asset_version_record_id)
    if raw_version is None:
        collector.add(
            RuleCode.EXTRACTION_RAW_VERSION_REFERENCE_INVALID,
            "ExtractionMetadataRecord references an unknown raw_asset_version_record.",
            field_ref="raw_asset_version_record_id",
        )

    strategy = context.strategies_by_id.get(metadata.parser_strategy_record_id)
    if strategy is None:
        collector.add(
            RuleCode.EXTRACTION_STRATEGY_REFERENCE_INVALID,
            "ExtractionMetadataRecord references an unknown parser_strategy_record.",
            field_ref="parser_strategy_record_id",
        )
        return

    if raw_version is not None and raw_version.detected_format not in strategy.applicable_formats:
        collector.add(
            RuleCode.EXTRACTION_FORMAT_SCOPE_INCOHERENT,
            (
                "ExtractionMetadataRecord uses a parser strategy that does not declare support for "
                f"{raw_version.detected_format.value}."
            ),
            field_ref="parser_strategy_record_id",
        )
