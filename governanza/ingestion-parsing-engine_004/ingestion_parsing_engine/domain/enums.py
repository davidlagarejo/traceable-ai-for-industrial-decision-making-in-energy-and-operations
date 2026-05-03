from __future__ import annotations

from enum import Enum


class SourceFormatFamily(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    HTML = "html"
    API_JSON = "api_json"
    API_TABULAR = "api_tabular"
    TEXT_DOCUMENT = "text_document"
    BINARY_DOCUMENT = "binary_document"
    UNKNOWN = "unknown"


class RawAssetKind(str, Enum):
    PDF_DOCUMENT = "pdf_document"
    CSV_FILE = "csv_file"
    XLSX_WORKBOOK = "xlsx_workbook"
    JSON_PAYLOAD = "json_payload"
    HTML_PAGE = "html_page"
    API_RESPONSE = "api_response"
    TEXT_DOCUMENT = "text_document"
    BINARY_BLOB = "binary_blob"


class RetrievalStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"


class ParserStrategyType(str, Enum):
    PDF_TEXT = "pdf_text"
    PDF_TABLE = "pdf_table"
    CSV_TABULAR = "csv_tabular"
    XLSX_SHEET = "xlsx_sheet"
    HTML_DOM = "html_dom"
    HTML_TABLE = "html_table"
    JSON_TREE = "json_tree"
    API_JSON = "api_json"
    API_TABULAR = "api_tabular"
    TEXT_BLOCK = "text_block"


class ParsedObjectType(str, Enum):
    DOCUMENT = "document"
    TABLE = "table"
    FIELD = "field"
    BLOCK = "block"


class ParsingStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


class PartialParseStatus(str, Enum):
    NOT_PARTIAL = "not_partial"
    PARTIAL_USEFUL = "partial_useful"
    PARTIAL_LIMITED = "partial_limited"


class WarningSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class FailureSeverity(str, Enum):
    RECOVERABLE = "recoverable"
    BLOCKING = "blocking"
    CRITICAL = "critical"


class ConfidenceStatus(str, Enum):
    NOT_AVAILABLE = "not_available"
    HEURISTIC = "heuristic"
    DECLARED = "declared"


class RightsRestrictionLevel(str, Enum):
    PUBLIC = "public"
    PREMIUM_RESTRICTED = "premium_restricted"
    INTERNAL_RESTRICTED = "internal_restricted"


class ReplayabilityStatus(str, Enum):
    REPLAYABLE = "replayable"
    PARTIALLY_REPLAYABLE = "partially_replayable"
    NOT_REPLAYABLE = "not_replayable"


class LocationKind(str, Enum):
    PDF_PAGE = "pdf_page"
    PDF_TABLE = "pdf_table"
    TABLE_CELL = "table_cell"
    XLSX_SHEET = "xlsx_sheet"
    TEXT_BLOCK = "text_block"
    HTML_SELECTOR = "html_selector"
    JSON_PATH = "json_path"
    API_ENDPOINT = "api_endpoint"
    API_PAYLOAD_POINTER = "api_payload_pointer"
    URI_FRAGMENT = "uri_fragment"


class ParsingScopeKind(str, Enum):
    RAW_ASSET_VERSION = "raw_asset_version"
    PARSED_DOCUMENT = "parsed_document"
    PARSED_TABLE = "parsed_table"
    PARSED_FIELD = "parsed_field"
    PARSED_BLOCK = "parsed_block"
    STRUCTURAL_LOCATION = "structural_location"
    EXTRACTION_METADATA = "extraction_metadata"


class FailureStage(str, Enum):
    RETRIEVAL = "retrieval"
    RAW_PRESERVATION = "raw_preservation"
    DOCUMENT_PARSE = "document_parse"
    TABLE_PARSE = "table_parse"
    FIELD_PARSE = "field_parse"
    BLOCK_PARSE = "block_parse"
    LOCATION_CAPTURE = "location_capture"


__all__ = [
    "ConfidenceStatus",
    "FailureSeverity",
    "FailureStage",
    "LocationKind",
    "ParsedObjectType",
    "ParserStrategyType",
    "ParsingScopeKind",
    "ParsingStatus",
    "PartialParseStatus",
    "RawAssetKind",
    "ReplayabilityStatus",
    "RetrievalStatus",
    "RightsRestrictionLevel",
    "SourceFormatFamily",
    "WarningSeverity",
]
