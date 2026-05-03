from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from .results import ValidationSeverity


class RuleCode(str, Enum):
    SCHEMA_VERSION_REGISTRY_REFERENCE_INVALID = "schema_version.registry_reference_invalid"
    SCHEMA_VERSION_SUPERSEDES_REFERENCE_INVALID = "schema_version.supersedes_reference_invalid"
    SCHEMA_VERSION_SUPERSEDES_REGISTRY_MISMATCH = "schema_version.supersedes_registry_mismatch"
    FIELD_SCHEMA_VERSION_REFERENCE_INVALID = "field.schema_version_reference_invalid"
    MAPPING_SCHEMA_VERSION_REFERENCE_INVALID = "mapping.schema_version_reference_invalid"
    MAPPING_FIELD_REFERENCE_INVALID = "mapping.field_reference_invalid"
    MAPPING_FIELD_SCHEMA_MISMATCH = "mapping.field_schema_mismatch"
    COERCION_SCHEMA_VERSION_REFERENCE_INVALID = "coercion.schema_version_reference_invalid"
    UNIT_CONVERSION_SCHEMA_VERSION_REFERENCE_INVALID = "unit_conversion.schema_version_reference_invalid"
    CURRENCY_CONVERSION_SCHEMA_VERSION_REFERENCE_INVALID = "currency_conversion.schema_version_reference_invalid"
    RUN_SCHEMA_REGISTRY_REFERENCE_INVALID = "run.schema_registry_reference_invalid"
    RUN_SCHEMA_VERSION_REFERENCE_INVALID = "run.schema_version_reference_invalid"
    RUN_SCHEMA_REGISTRY_MISMATCH = "run.schema_registry_mismatch"
    RUN_NON_COMPLETE_DECLARED = "run.non_complete_declared"
    NORMALIZED_FIELD_RUN_REFERENCE_INVALID = "normalized_field.run_reference_invalid"
    NORMALIZED_FIELD_RECORD_REFERENCE_INVALID = "normalized_field.record_reference_invalid"
    NORMALIZED_FIELD_FIELD_REFERENCE_INVALID = "normalized_field.field_reference_invalid"
    NORMALIZED_FIELD_FIELD_SCHEMA_MISMATCH = "normalized_field.field_schema_mismatch"
    NORMALIZED_FIELD_RECORD_RUN_MISMATCH = "normalized_field.record_run_mismatch"
    NORMALIZED_FIELD_RECORD_PARENT_MISMATCH = "normalized_field.record_parent_mismatch"
    NORMALIZED_FIELD_MAPPING_REFERENCE_INVALID = "normalized_field.mapping_reference_invalid"
    NORMALIZED_FIELD_MAPPING_FIELD_MISMATCH = "normalized_field.mapping_field_mismatch"
    NORMALIZED_FIELD_MAPPING_SCHEMA_MISMATCH = "normalized_field.mapping_schema_mismatch"
    NORMALIZED_FIELD_COERCION_REFERENCE_INVALID = "normalized_field.coercion_reference_invalid"
    NORMALIZED_FIELD_COERCION_SCHEMA_MISMATCH = "normalized_field.coercion_schema_mismatch"
    NORMALIZED_FIELD_UNIT_RULE_REFERENCE_INVALID = "normalized_field.unit_rule_reference_invalid"
    NORMALIZED_FIELD_UNIT_RULE_INCOHERENT = "normalized_field.unit_rule_incoherent"
    NORMALIZED_FIELD_UNIT_RULE_SCHEMA_MISMATCH = "normalized_field.unit_rule_schema_mismatch"
    NORMALIZED_FIELD_CURRENCY_RULE_REFERENCE_INVALID = "normalized_field.currency_rule_reference_invalid"
    NORMALIZED_FIELD_CURRENCY_RULE_INCOHERENT = "normalized_field.currency_rule_incoherent"
    NORMALIZED_FIELD_CURRENCY_RULE_SCHEMA_MISMATCH = "normalized_field.currency_rule_schema_mismatch"
    NORMALIZED_FIELD_TRIPLE_VALUE_INCOHERENT = "normalized_field.triple_value_incoherent"
    NORMALIZED_FIELD_PARTIAL_DECLARED = "normalized_field.partial_declared"
    NORMALIZED_FIELD_NON_NORMALIZABLE_DECLARED = "normalized_field.non_normalizable_declared"
    NORMALIZED_FIELD_RANGE_ATTENTION = "normalized_field.range_attention"
    NORMALIZED_RECORD_RUN_REFERENCE_INVALID = "normalized_record.run_reference_invalid"
    NORMALIZED_RECORD_RECORD_SET_REFERENCE_INVALID = "normalized_record.record_set_reference_invalid"
    NORMALIZED_RECORD_FIELD_REFERENCE_INVALID = "normalized_record.field_reference_invalid"
    NORMALIZED_RECORD_FIELD_RUN_MISMATCH = "normalized_record.field_run_mismatch"
    NORMALIZED_RECORD_FIELD_PARENT_MISMATCH = "normalized_record.field_parent_mismatch"
    NORMALIZED_RECORD_COMPLETE_INCOHERENT = "normalized_record.complete_incoherent"
    NORMALIZED_RECORD_PARTIAL_INCOHERENT = "normalized_record.partial_incoherent"
    RECORD_SET_RUN_REFERENCE_INVALID = "record_set.run_reference_invalid"
    RECORD_SET_SCHEMA_VERSION_REFERENCE_INVALID = "record_set.schema_version_reference_invalid"
    RECORD_SET_RUN_SCHEMA_MISMATCH = "record_set.run_schema_mismatch"
    RECORD_SET_RECORD_REFERENCE_INVALID = "record_set.record_reference_invalid"
    RECORD_SET_RECORD_RUN_MISMATCH = "record_set.record_run_mismatch"
    RECORD_SET_RECORD_PARENT_MISMATCH = "record_set.record_parent_mismatch"
    RECORD_SET_COMPLETE_INCOHERENT = "record_set.complete_incoherent"
    RECORD_SET_PARTIAL_INCOHERENT = "record_set.partial_incoherent"
    WARNING_RUN_REFERENCE_INVALID = "warning.run_reference_invalid"
    WARNING_SCOPE_UNRESOLVED = "warning.scope_unresolved"
    WARNING_SCOPE_RUN_MISMATCH = "warning.scope_run_mismatch"
    WARNING_DECLARED = "warning.declared"
    NON_NORMALIZABLE_RUN_REFERENCE_INVALID = "non_normalizable.run_reference_invalid"
    NON_NORMALIZABLE_CANDIDATE_FIELD_REFERENCE_INVALID = "non_normalizable.candidate_field_reference_invalid"
    NON_NORMALIZABLE_CANDIDATE_FIELD_SCHEMA_MISMATCH = "non_normalizable.candidate_field_schema_mismatch"
    NON_NORMALIZABLE_MAPPING_REFERENCE_INVALID = "non_normalizable.mapping_reference_invalid"
    NON_NORMALIZABLE_MAPPING_FIELD_MISMATCH = "non_normalizable.mapping_field_mismatch"
    NON_NORMALIZABLE_MAPPING_SCHEMA_MISMATCH = "non_normalizable.mapping_schema_mismatch"
    NON_NORMALIZABLE_DECLARED = "non_normalizable.declared"
    PARTIAL_RUN_REFERENCE_INVALID = "partial.run_reference_invalid"
    PARTIAL_NORMALIZED_FIELD_REFERENCE_INVALID = "partial.normalized_field_reference_invalid"
    PARTIAL_NON_NORMALIZABLE_REFERENCE_INVALID = "partial.non_normalizable_reference_invalid"
    PARTIAL_FIELD_RUN_MISMATCH = "partial.field_run_mismatch"
    PARTIAL_DECLARED = "partial.declared"
    REPLAY_RUN_REFERENCE_INVALID = "replay.run_reference_invalid"
    REPLAY_SCHEMA_VERSION_REFERENCE_INVALID = "replay.schema_version_reference_invalid"
    REPLAY_RUN_SCHEMA_MISMATCH = "replay.run_schema_mismatch"
    REPLAY_RECORD_SET_REFERENCE_INVALID = "replay.record_set_reference_invalid"
    REPLAY_RECORD_SET_MISMATCH = "replay.record_set_mismatch"
    REPLAY_MAPPING_RULE_REFERENCE_INVALID = "replay.mapping_rule_reference_invalid"
    REPLAY_MAPPING_RULE_SCHEMA_MISMATCH = "replay.mapping_rule_schema_mismatch"
    REPLAY_COERCION_RULE_REFERENCE_INVALID = "replay.coercion_rule_reference_invalid"
    REPLAY_COERCION_RULE_SCHEMA_MISMATCH = "replay.coercion_rule_schema_mismatch"
    REPLAY_UNIT_RULE_REFERENCE_INVALID = "replay.unit_rule_reference_invalid"
    REPLAY_UNIT_RULE_SCHEMA_MISMATCH = "replay.unit_rule_schema_mismatch"
    REPLAY_CURRENCY_RULE_REFERENCE_INVALID = "replay.currency_rule_reference_invalid"
    REPLAY_CURRENCY_RULE_SCHEMA_MISMATCH = "replay.currency_rule_schema_mismatch"
    REPLAY_SOURCE_PROVENANCE_MISMATCH = "replay.source_provenance_mismatch"
    REPLAY_NOT_FULLY_REPLAYABLE = "replay.not_fully_replayable"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    severity: ValidationSeverity
    blocking: bool


def _warning() -> RuleProfile:
    return RuleProfile(ValidationSeverity.WARNING, False)


def _error() -> RuleProfile:
    return RuleProfile(ValidationSeverity.ERROR, True)


RULE_PROFILES: dict[RuleCode, RuleProfile] = {
    RuleCode.SCHEMA_VERSION_REGISTRY_REFERENCE_INVALID: _error(),
    RuleCode.SCHEMA_VERSION_SUPERSEDES_REFERENCE_INVALID: _error(),
    RuleCode.SCHEMA_VERSION_SUPERSEDES_REGISTRY_MISMATCH: _error(),
    RuleCode.FIELD_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.MAPPING_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.MAPPING_FIELD_REFERENCE_INVALID: _error(),
    RuleCode.MAPPING_FIELD_SCHEMA_MISMATCH: _error(),
    RuleCode.COERCION_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.UNIT_CONVERSION_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.CURRENCY_CONVERSION_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.RUN_SCHEMA_REGISTRY_REFERENCE_INVALID: _error(),
    RuleCode.RUN_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.RUN_SCHEMA_REGISTRY_MISMATCH: _error(),
    RuleCode.RUN_NON_COMPLETE_DECLARED: _warning(),
    RuleCode.NORMALIZED_FIELD_RUN_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_RECORD_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_FIELD_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_FIELD_SCHEMA_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_RECORD_RUN_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_RECORD_PARENT_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_MAPPING_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_MAPPING_FIELD_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_MAPPING_SCHEMA_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_COERCION_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_COERCION_SCHEMA_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_UNIT_RULE_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_UNIT_RULE_INCOHERENT: _error(),
    RuleCode.NORMALIZED_FIELD_UNIT_RULE_SCHEMA_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_CURRENCY_RULE_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_FIELD_CURRENCY_RULE_INCOHERENT: _error(),
    RuleCode.NORMALIZED_FIELD_CURRENCY_RULE_SCHEMA_MISMATCH: _error(),
    RuleCode.NORMALIZED_FIELD_TRIPLE_VALUE_INCOHERENT: _error(),
    RuleCode.NORMALIZED_FIELD_PARTIAL_DECLARED: _warning(),
    RuleCode.NORMALIZED_FIELD_NON_NORMALIZABLE_DECLARED: _warning(),
    RuleCode.NORMALIZED_FIELD_RANGE_ATTENTION: _warning(),
    RuleCode.NORMALIZED_RECORD_RUN_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_RECORD_RECORD_SET_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_RECORD_FIELD_REFERENCE_INVALID: _error(),
    RuleCode.NORMALIZED_RECORD_FIELD_RUN_MISMATCH: _error(),
    RuleCode.NORMALIZED_RECORD_FIELD_PARENT_MISMATCH: _error(),
    RuleCode.NORMALIZED_RECORD_COMPLETE_INCOHERENT: _error(),
    RuleCode.NORMALIZED_RECORD_PARTIAL_INCOHERENT: _error(),
    RuleCode.RECORD_SET_RUN_REFERENCE_INVALID: _error(),
    RuleCode.RECORD_SET_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.RECORD_SET_RUN_SCHEMA_MISMATCH: _error(),
    RuleCode.RECORD_SET_RECORD_REFERENCE_INVALID: _error(),
    RuleCode.RECORD_SET_RECORD_RUN_MISMATCH: _error(),
    RuleCode.RECORD_SET_RECORD_PARENT_MISMATCH: _error(),
    RuleCode.RECORD_SET_COMPLETE_INCOHERENT: _error(),
    RuleCode.RECORD_SET_PARTIAL_INCOHERENT: _error(),
    RuleCode.WARNING_RUN_REFERENCE_INVALID: _error(),
    RuleCode.WARNING_SCOPE_UNRESOLVED: _error(),
    RuleCode.WARNING_SCOPE_RUN_MISMATCH: _error(),
    RuleCode.WARNING_DECLARED: _warning(),
    RuleCode.NON_NORMALIZABLE_RUN_REFERENCE_INVALID: _error(),
    RuleCode.NON_NORMALIZABLE_CANDIDATE_FIELD_REFERENCE_INVALID: _error(),
    RuleCode.NON_NORMALIZABLE_CANDIDATE_FIELD_SCHEMA_MISMATCH: _error(),
    RuleCode.NON_NORMALIZABLE_MAPPING_REFERENCE_INVALID: _error(),
    RuleCode.NON_NORMALIZABLE_MAPPING_FIELD_MISMATCH: _error(),
    RuleCode.NON_NORMALIZABLE_MAPPING_SCHEMA_MISMATCH: _error(),
    RuleCode.NON_NORMALIZABLE_DECLARED: _warning(),
    RuleCode.PARTIAL_RUN_REFERENCE_INVALID: _error(),
    RuleCode.PARTIAL_NORMALIZED_FIELD_REFERENCE_INVALID: _error(),
    RuleCode.PARTIAL_NON_NORMALIZABLE_REFERENCE_INVALID: _error(),
    RuleCode.PARTIAL_FIELD_RUN_MISMATCH: _error(),
    RuleCode.PARTIAL_DECLARED: _warning(),
    RuleCode.REPLAY_RUN_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_SCHEMA_VERSION_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_RUN_SCHEMA_MISMATCH: _error(),
    RuleCode.REPLAY_RECORD_SET_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_RECORD_SET_MISMATCH: _error(),
    RuleCode.REPLAY_MAPPING_RULE_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_MAPPING_RULE_SCHEMA_MISMATCH: _error(),
    RuleCode.REPLAY_COERCION_RULE_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_COERCION_RULE_SCHEMA_MISMATCH: _error(),
    RuleCode.REPLAY_UNIT_RULE_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_UNIT_RULE_SCHEMA_MISMATCH: _error(),
    RuleCode.REPLAY_CURRENCY_RULE_REFERENCE_INVALID: _error(),
    RuleCode.REPLAY_CURRENCY_RULE_SCHEMA_MISMATCH: _error(),
    RuleCode.REPLAY_SOURCE_PROVENANCE_MISMATCH: _error(),
    RuleCode.REPLAY_NOT_FULLY_REPLAYABLE: _warning(),
}


def profile_for(rule_code: RuleCode) -> RuleProfile:
    return RULE_PROFILES[rule_code]
