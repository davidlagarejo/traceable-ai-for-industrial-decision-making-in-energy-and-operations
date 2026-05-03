from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from .results import ValidationSeverity


class RuleCode(str, Enum):
    REQUEST_FORMAT_INCOHERENT = "request.format_incoherent"
    REQUEST_FORMAT_UNKNOWN = "request.format_unknown"
    RETRIEVAL_REQUEST_REFERENCE_INVALID = "retrieval.request_reference_invalid"
    RETRIEVAL_RAW_ASSET_REFERENCE_INVALID = "retrieval.raw_asset_reference_invalid"
    RETRIEVAL_REQUEST_RAW_MISMATCH = "retrieval.request_raw_mismatch"
    RETRIEVAL_REQUEST_FINGERPRINT_MISMATCH = "retrieval.request_fingerprint_mismatch"
    RETRIEVAL_NON_SUCCESS_DECLARED = "retrieval.non_success_declared"
    RAW_ASSET_FORMAT_INCOHERENT = "raw_asset.format_incoherent"
    RAW_VERSION_RAW_ASSET_REFERENCE_INVALID = "raw_version.raw_asset_reference_invalid"
    RAW_VERSION_RETRIEVAL_REFERENCE_INVALID = "raw_version.retrieval_reference_invalid"
    RAW_VERSION_RETRIEVAL_RAW_MISMATCH = "raw_version.retrieval_raw_mismatch"
    RAW_VERSION_CAPTURE_FROM_FAILED_RETRIEVAL = "raw_version.capture_from_failed_retrieval"
    RAW_VERSION_FORMAT_DIVERGENCE = "raw_version.format_divergence"
    DOCUMENT_RAW_VERSION_REFERENCE_INVALID = "document.raw_version_reference_invalid"
    DOCUMENT_EXTRACTION_REFERENCE_INVALID = "document.extraction_reference_invalid"
    DOCUMENT_STRATEGY_REFERENCE_INVALID = "document.strategy_reference_invalid"
    DOCUMENT_METADATA_MISMATCH = "document.metadata_mismatch"
    DOCUMENT_PARTIAL_DECLARED = "document.partial_declared"
    TABLE_DOCUMENT_REFERENCE_INVALID = "table.document_reference_invalid"
    TABLE_EXTRACTION_REFERENCE_INVALID = "table.extraction_reference_invalid"
    TABLE_LOCATION_REFERENCE_INVALID = "table.location_reference_invalid"
    TABLE_PARENT_PROVENANCE_MISMATCH = "table.parent_provenance_mismatch"
    TABLE_PARTIAL_DECLARED = "table.partial_declared"
    FIELD_DOCUMENT_REFERENCE_INVALID = "field.document_reference_invalid"
    FIELD_EXTRACTION_REFERENCE_INVALID = "field.extraction_reference_invalid"
    FIELD_LOCATION_REFERENCE_INVALID = "field.location_reference_invalid"
    FIELD_PARENT_REFERENCE_INVALID = "field.parent_reference_invalid"
    FIELD_PARENT_PROVENANCE_MISMATCH = "field.parent_provenance_mismatch"
    FIELD_PARTIAL_DECLARED = "field.partial_declared"
    BLOCK_DOCUMENT_REFERENCE_INVALID = "block.document_reference_invalid"
    BLOCK_EXTRACTION_REFERENCE_INVALID = "block.extraction_reference_invalid"
    BLOCK_LOCATION_REFERENCE_INVALID = "block.location_reference_invalid"
    BLOCK_PARENT_REFERENCE_INVALID = "block.parent_reference_invalid"
    BLOCK_PARENT_PROVENANCE_MISMATCH = "block.parent_provenance_mismatch"
    BLOCK_PARTIAL_DECLARED = "block.partial_declared"
    LOCATION_FIELD_COMBINATION_INVALID = "location.field_combination_invalid"
    EXTRACTION_RAW_VERSION_REFERENCE_INVALID = "extraction.raw_version_reference_invalid"
    EXTRACTION_STRATEGY_REFERENCE_INVALID = "extraction.strategy_reference_invalid"
    EXTRACTION_FORMAT_SCOPE_INCOHERENT = "extraction.format_scope_incoherent"
    EXTRACTION_PARTIAL_DECLARED = "extraction.partial_declared"
    EXTRACTION_FAILED_DECLARED = "extraction.failed_declared"
    WARNING_SCOPE_UNRESOLVED = "warning.scope_unresolved"
    WARNING_DECLARED = "warning.declared"
    FAILURE_SCOPE_UNRESOLVED = "failure.scope_unresolved"
    FAILURE_DECLARED = "failure.declared"
    CONFIDENCE_SCOPE_UNRESOLVED = "confidence.scope_unresolved"
    CONFIDENCE_HEURISTIC_DECLARED = "confidence.heuristic_declared"
    STRATEGY_FORMAT_SCOPE_INCOHERENT = "strategy.format_scope_incoherent"
    REPLAY_RAW_VERSION_REFERENCE_INVALID = "replay.raw_version_reference_invalid"
    REPLAY_STRATEGY_REFERENCE_INVALID = "replay.strategy_reference_invalid"
    REPLAY_EXTRACTION_REFERENCE_INVALID = "replay.extraction_reference_invalid"
    REPLAY_OUTPUT_REFERENCE_INVALID = "replay.output_reference_invalid"
    REPLAY_METADATA_MISMATCH = "replay.metadata_mismatch"
    REPLAY_OUTPUT_PROVENANCE_MISMATCH = "replay.output_provenance_mismatch"
    REPLAY_CHECKSUM_MISMATCH = "replay.checksum_mismatch"
    REPLAY_NOT_FULLY_REPLAYABLE = "replay.not_fully_replayable"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ValidationSeverity
    blocking: bool


RULE_PROFILES: dict[RuleCode, RuleProfile] = {
    RuleCode.REQUEST_FORMAT_INCOHERENT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REQUEST_FORMAT_UNKNOWN: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.RETRIEVAL_REQUEST_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RETRIEVAL_RAW_ASSET_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RETRIEVAL_REQUEST_RAW_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RETRIEVAL_REQUEST_FINGERPRINT_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RETRIEVAL_NON_SUCCESS_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.RAW_ASSET_FORMAT_INCOHERENT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RAW_VERSION_RAW_ASSET_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RAW_VERSION_RETRIEVAL_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RAW_VERSION_RETRIEVAL_RAW_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RAW_VERSION_CAPTURE_FROM_FAILED_RETRIEVAL: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.RAW_VERSION_FORMAT_DIVERGENCE: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.DOCUMENT_RAW_VERSION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DOCUMENT_EXTRACTION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DOCUMENT_STRATEGY_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DOCUMENT_METADATA_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.DOCUMENT_PARTIAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.TABLE_DOCUMENT_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TABLE_EXTRACTION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TABLE_LOCATION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TABLE_PARENT_PROVENANCE_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.TABLE_PARTIAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.FIELD_DOCUMENT_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.FIELD_EXTRACTION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.FIELD_LOCATION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.FIELD_PARENT_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.FIELD_PARENT_PROVENANCE_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.FIELD_PARTIAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.BLOCK_DOCUMENT_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BLOCK_EXTRACTION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BLOCK_LOCATION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BLOCK_PARENT_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BLOCK_PARENT_PROVENANCE_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.BLOCK_PARTIAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.LOCATION_FIELD_COMBINATION_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EXTRACTION_RAW_VERSION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EXTRACTION_STRATEGY_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EXTRACTION_FORMAT_SCOPE_INCOHERENT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.EXTRACTION_PARTIAL_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.EXTRACTION_FAILED_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.WARNING_SCOPE_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.WARNING_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.FAILURE_SCOPE_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.FAILURE_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.CONFIDENCE_SCOPE_UNRESOLVED: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.CONFIDENCE_HEURISTIC_DECLARED: RuleProfile(ValidationSeverity.WARNING, False),
    RuleCode.STRATEGY_FORMAT_SCOPE_INCOHERENT: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_RAW_VERSION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_STRATEGY_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_EXTRACTION_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_OUTPUT_REFERENCE_INVALID: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_METADATA_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_OUTPUT_PROVENANCE_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_CHECKSUM_MISMATCH: RuleProfile(ValidationSeverity.ERROR, True),
    RuleCode.REPLAY_NOT_FULLY_REPLAYABLE: RuleProfile(ValidationSeverity.WARNING, False),
}


def profile_for(rule_code: RuleCode) -> RuleProfile:
    return RULE_PROFILES[rule_code]
