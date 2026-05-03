from __future__ import annotations

from ..domain.entities import (
    ParsedBlockObject,
    ParsedDocumentObject,
    ParsedFieldObject,
    ParsedTableObject,
)
from ..domain.enums import ParsingStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_parsed_document_object(
    document: ParsedDocumentObject,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if document.parsing_status is ParsingStatus.PARTIAL:
        collector.add(
            RuleCode.DOCUMENT_PARTIAL_DECLARED,
            "ParsedDocumentObject declares PARTIAL parsing status.",
            field_ref="parsing_status",
        )

    if context is None:
        return

    raw_version = context.raw_versions_by_id.get(document.raw_asset_version_record_id)
    if raw_version is None:
        collector.add(
            RuleCode.DOCUMENT_RAW_VERSION_REFERENCE_INVALID,
            "ParsedDocumentObject references an unknown raw_asset_version_record.",
            field_ref="raw_asset_version_record_id",
        )

    metadata = context.extractions_by_id.get(document.extraction_metadata_record_id)
    if metadata is None:
        collector.add(
            RuleCode.DOCUMENT_EXTRACTION_REFERENCE_INVALID,
            "ParsedDocumentObject references an unknown extraction_metadata_record.",
            field_ref="extraction_metadata_record_id",
        )

    strategy = context.strategies_by_id.get(document.parser_strategy_record_id)
    if strategy is None:
        collector.add(
            RuleCode.DOCUMENT_STRATEGY_REFERENCE_INVALID,
            "ParsedDocumentObject references an unknown parser_strategy_record.",
            field_ref="parser_strategy_record_id",
        )

    if metadata is not None:
        _validate_document_metadata_alignment(document, metadata, collector)


def validate_parsed_table_object(
    table: ParsedTableObject,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if table.parsing_status is ParsingStatus.PARTIAL:
        collector.add(
            RuleCode.TABLE_PARTIAL_DECLARED,
            "ParsedTableObject declares PARTIAL parsing status.",
            field_ref="parsing_status",
        )

    if context is None:
        return

    document = context.parsed_documents_by_id.get(table.parsed_document_object_id)
    if document is None:
        collector.add(
            RuleCode.TABLE_DOCUMENT_REFERENCE_INVALID,
            "ParsedTableObject references an unknown parsed_document_object.",
            field_ref="parsed_document_object_id",
        )
    else:
        _validate_parent_alignment(
            child_raw_version_id=table.raw_asset_version_record_id,
            child_extraction_id=table.extraction_metadata_record_id,
            parent_raw_version_id=document.raw_asset_version_record_id,
            parent_extraction_id=document.extraction_metadata_record_id,
            collector=collector,
            rule_code=RuleCode.TABLE_PARENT_PROVENANCE_MISMATCH,
        )

    if context.extractions_by_id.get(table.extraction_metadata_record_id) is None:
        collector.add(
            RuleCode.TABLE_EXTRACTION_REFERENCE_INVALID,
            "ParsedTableObject references an unknown extraction_metadata_record.",
            field_ref="extraction_metadata_record_id",
        )

    if context.locations_by_id.get(table.structural_location_record_id) is None:
        collector.add(
            RuleCode.TABLE_LOCATION_REFERENCE_INVALID,
            "ParsedTableObject references an unknown structural_location_record.",
            field_ref="structural_location_record_id",
        )


def validate_parsed_field_object(
    field: ParsedFieldObject,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if field.parsing_status is ParsingStatus.PARTIAL:
        collector.add(
            RuleCode.FIELD_PARTIAL_DECLARED,
            "ParsedFieldObject declares PARTIAL parsing status.",
            field_ref="parsing_status",
        )

    if context is None:
        return

    document = context.parsed_documents_by_id.get(field.parsed_document_object_id)
    if document is None:
        collector.add(
            RuleCode.FIELD_DOCUMENT_REFERENCE_INVALID,
            "ParsedFieldObject references an unknown parsed_document_object.",
            field_ref="parsed_document_object_id",
        )
    else:
        _validate_parent_alignment(
            child_raw_version_id=field.raw_asset_version_record_id,
            child_extraction_id=field.extraction_metadata_record_id,
            parent_raw_version_id=document.raw_asset_version_record_id,
            parent_extraction_id=document.extraction_metadata_record_id,
            collector=collector,
            rule_code=RuleCode.FIELD_PARENT_PROVENANCE_MISMATCH,
        )

    if context.extractions_by_id.get(field.extraction_metadata_record_id) is None:
        collector.add(
            RuleCode.FIELD_EXTRACTION_REFERENCE_INVALID,
            "ParsedFieldObject references an unknown extraction_metadata_record.",
            field_ref="extraction_metadata_record_id",
        )

    if context.locations_by_id.get(field.structural_location_record_id) is None:
        collector.add(
            RuleCode.FIELD_LOCATION_REFERENCE_INVALID,
            "ParsedFieldObject references an unknown structural_location_record.",
            field_ref="structural_location_record_id",
        )

    if field.parent_table_object_id is not None:
        table = context.parsed_tables_by_id.get(field.parent_table_object_id)
        if table is None:
            collector.add(
                RuleCode.FIELD_PARENT_REFERENCE_INVALID,
                "ParsedFieldObject.parent_table_object_id references an unknown parsed_table_object.",
                field_ref="parent_table_object_id",
            )
        else:
            _validate_nested_parent_alignment(
                child_document_id=field.parsed_document_object_id,
                child_raw_version_id=field.raw_asset_version_record_id,
                parent_document_id=table.parsed_document_object_id,
                parent_raw_version_id=table.raw_asset_version_record_id,
                collector=collector,
                rule_code=RuleCode.FIELD_PARENT_PROVENANCE_MISMATCH,
            )

    if field.parent_block_object_id is not None:
        block = context.parsed_blocks_by_id.get(field.parent_block_object_id)
        if block is None:
            collector.add(
                RuleCode.FIELD_PARENT_REFERENCE_INVALID,
                "ParsedFieldObject.parent_block_object_id references an unknown parsed_block_object.",
                field_ref="parent_block_object_id",
            )
        else:
            _validate_nested_parent_alignment(
                child_document_id=field.parsed_document_object_id,
                child_raw_version_id=field.raw_asset_version_record_id,
                parent_document_id=block.parsed_document_object_id,
                parent_raw_version_id=block.raw_asset_version_record_id,
                collector=collector,
                rule_code=RuleCode.FIELD_PARENT_PROVENANCE_MISMATCH,
            )


def validate_parsed_block_object(
    block: ParsedBlockObject,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if block.parsing_status is ParsingStatus.PARTIAL:
        collector.add(
            RuleCode.BLOCK_PARTIAL_DECLARED,
            "ParsedBlockObject declares PARTIAL parsing status.",
            field_ref="parsing_status",
        )

    if context is None:
        return

    document = context.parsed_documents_by_id.get(block.parsed_document_object_id)
    if document is None:
        collector.add(
            RuleCode.BLOCK_DOCUMENT_REFERENCE_INVALID,
            "ParsedBlockObject references an unknown parsed_document_object.",
            field_ref="parsed_document_object_id",
        )
    else:
        _validate_parent_alignment(
            child_raw_version_id=block.raw_asset_version_record_id,
            child_extraction_id=block.extraction_metadata_record_id,
            parent_raw_version_id=document.raw_asset_version_record_id,
            parent_extraction_id=document.extraction_metadata_record_id,
            collector=collector,
            rule_code=RuleCode.BLOCK_PARENT_PROVENANCE_MISMATCH,
        )

    if context.extractions_by_id.get(block.extraction_metadata_record_id) is None:
        collector.add(
            RuleCode.BLOCK_EXTRACTION_REFERENCE_INVALID,
            "ParsedBlockObject references an unknown extraction_metadata_record.",
            field_ref="extraction_metadata_record_id",
        )

    if context.locations_by_id.get(block.structural_location_record_id) is None:
        collector.add(
            RuleCode.BLOCK_LOCATION_REFERENCE_INVALID,
            "ParsedBlockObject references an unknown structural_location_record.",
            field_ref="structural_location_record_id",
        )

    if block.parent_table_object_id is not None:
        table = context.parsed_tables_by_id.get(block.parent_table_object_id)
        if table is None:
            collector.add(
                RuleCode.BLOCK_PARENT_REFERENCE_INVALID,
                "ParsedBlockObject.parent_table_object_id references an unknown parsed_table_object.",
                field_ref="parent_table_object_id",
            )
        else:
            _validate_nested_parent_alignment(
                child_document_id=block.parsed_document_object_id,
                child_raw_version_id=block.raw_asset_version_record_id,
                parent_document_id=table.parsed_document_object_id,
                parent_raw_version_id=table.raw_asset_version_record_id,
                collector=collector,
                rule_code=RuleCode.BLOCK_PARENT_PROVENANCE_MISMATCH,
            )


def _validate_document_metadata_alignment(
    document: ParsedDocumentObject,
    metadata,
    collector: ViolationCollector,
) -> None:
    mismatch_fields: list[str] = []
    if metadata.raw_asset_version_record_id != document.raw_asset_version_record_id:
        mismatch_fields.append("raw_asset_version_record_id")
    if metadata.parser_strategy_record_id != document.parser_strategy_record_id:
        mismatch_fields.append("parser_strategy_record_id")
    if metadata.parsing_status != document.parsing_status:
        mismatch_fields.append("parsing_status")
    if metadata.partial_parse_status != document.partial_parse_status:
        mismatch_fields.append("partial_parse_status")
    if mismatch_fields:
        collector.add(
            RuleCode.DOCUMENT_METADATA_MISMATCH,
            "ParsedDocumentObject is inconsistent with its extraction metadata on: "
            + ", ".join(mismatch_fields)
            + ".",
        )


def _validate_parent_alignment(
    *,
    child_raw_version_id,
    child_extraction_id,
    parent_raw_version_id,
    parent_extraction_id,
    collector: ViolationCollector,
    rule_code: RuleCode,
) -> None:
    mismatch_fields: list[str] = []
    if child_raw_version_id != parent_raw_version_id:
        mismatch_fields.append("raw_asset_version_record_id")
    if child_extraction_id != parent_extraction_id:
        mismatch_fields.append("extraction_metadata_record_id")
    if mismatch_fields:
        collector.add(
            rule_code,
            "Parsed child object is inconsistent with its parent provenance on: "
            + ", ".join(mismatch_fields)
            + ".",
        )


def _validate_nested_parent_alignment(
    *,
    child_document_id,
    child_raw_version_id,
    parent_document_id,
    parent_raw_version_id,
    collector: ViolationCollector,
    rule_code: RuleCode,
) -> None:
    mismatch_fields: list[str] = []
    if child_document_id != parent_document_id:
        mismatch_fields.append("parsed_document_object_id")
    if child_raw_version_id != parent_raw_version_id:
        mismatch_fields.append("raw_asset_version_record_id")
    if mismatch_fields:
        collector.add(
            rule_code,
            "Parsed child object is inconsistent with its nested parent provenance on: "
            + ", ".join(mismatch_fields)
            + ".",
        )
