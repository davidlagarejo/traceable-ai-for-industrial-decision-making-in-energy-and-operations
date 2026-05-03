from __future__ import annotations

from ..domain.entities import IngestionRequestRecord
from ..domain.enums import RawAssetKind, SourceFormatFamily
from .collector import ViolationCollector
from .rules import RuleCode


ALLOWED_FORMATS_BY_RAW_ASSET_KIND: dict[RawAssetKind, frozenset[SourceFormatFamily]] = {
    RawAssetKind.PDF_DOCUMENT: frozenset({SourceFormatFamily.PDF}),
    RawAssetKind.CSV_FILE: frozenset({SourceFormatFamily.CSV}),
    RawAssetKind.XLSX_WORKBOOK: frozenset({SourceFormatFamily.XLSX}),
    RawAssetKind.JSON_PAYLOAD: frozenset({SourceFormatFamily.JSON, SourceFormatFamily.API_JSON}),
    RawAssetKind.HTML_PAGE: frozenset({SourceFormatFamily.HTML}),
    RawAssetKind.API_RESPONSE: frozenset(
        {
            SourceFormatFamily.API_JSON,
            SourceFormatFamily.API_TABULAR,
            SourceFormatFamily.JSON,
        }
    ),
    RawAssetKind.TEXT_DOCUMENT: frozenset({SourceFormatFamily.TEXT_DOCUMENT}),
    RawAssetKind.BINARY_BLOB: frozenset(
        {
            SourceFormatFamily.BINARY_DOCUMENT,
            SourceFormatFamily.UNKNOWN,
        }
    ),
}


def validate_ingestion_request_record(
    request: IngestionRequestRecord,
    collector: ViolationCollector,
) -> None:
    if request.declared_format is SourceFormatFamily.UNKNOWN:
        collector.add(
            RuleCode.REQUEST_FORMAT_UNKNOWN,
            "Ingestion request declares UNKNOWN format; downstream parsing may need manual routing.",
            field_ref="declared_format",
        )
        return

    allowed_formats = ALLOWED_FORMATS_BY_RAW_ASSET_KIND[request.raw_asset_kind]
    if request.declared_format not in allowed_formats:
        collector.add(
            RuleCode.REQUEST_FORMAT_INCOHERENT,
            (
                "Ingestion request declared_format is incompatible with raw_asset_kind: "
                f"{request.raw_asset_kind.value} -> {request.declared_format.value}."
            ),
            field_ref="declared_format",
        )
