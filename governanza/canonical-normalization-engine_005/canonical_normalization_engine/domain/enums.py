from __future__ import annotations

from enum import Enum


class SchemaProfileKind(str, Enum):
    SHARED = "shared"
    PHASE_1_BUNDLE = "phase_1_bundle"
    PHASE_2_OBJECT = "phase_2_object"
    PHASE_3_OUTPUT = "phase_3_output"
    PHASE_4_VERIFICATION = "phase_4_verification"


class CanonicalSchemaRegistryStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class CanonicalSchemaVersionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RETIRED = "retired"


class FieldLifecycleStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class RuleLifecycleStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class CanonicalFieldType(str, Enum):
    STRING_DISCIPLINED = "string_disciplined"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    YEAR = "year"
    ENUM_CONTROLLED = "enum_controlled"
    RATIO = "ratio"
    PERCENTAGE = "percentage"
    CURRENCY_AMOUNT = "currency_amount"
    MEASURE_WITH_UNIT = "measure_with_unit"


class MeasurementFamily(str, Enum):
    ENERGY = "energy"
    POWER = "power"
    FLOW = "flow"
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    AREA = "area"
    VOLUME = "volume"
    EMISSIONS = "emissions"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    RATIO = "ratio"


class ObservedValueType(str, Enum):
    UNKNOWN = "unknown"
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    YEAR = "year"
    ENUM_TOKEN = "enum_token"
    UNIT_VALUE = "unit_value"
    CURRENCY_VALUE = "currency_value"
    NULL_LITERAL = "null_literal"


class NormalizationStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    NON_NORMALIZABLE = "non_normalizable"
    FAILED = "failed"


class PartialNormalizationStatus(str, Enum):
    NOT_PARTIAL = "not_partial"
    PARTIAL_USEFUL = "partial_useful"
    PARTIAL_LIMITED = "partial_limited"


class WarningSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CoercionSafetyLevel(str, Enum):
    SAFE = "safe"
    CONDITIONAL = "conditional"
    UNSAFE = "unsafe"


class ConversionRuleType(str, Enum):
    FACTOR = "factor"
    AFFINE = "affine"
    DECLARED_RATE = "declared_rate"
    OFFICIAL_TABLE = "official_table"
    FIXED_POLICY_TABLE = "fixed_policy_table"


class ReplayabilityStatus(str, Enum):
    REPLAYABLE = "replayable"
    PARTIALLY_REPLAYABLE = "partially_replayable"
    NOT_REPLAYABLE = "not_replayable"


class MissingnessStatus(str, Enum):
    NOT_MISSING = "not_missing"
    EXPLICIT_NULL = "explicit_null"
    MISSING_NOT_PRESENT = "missing_not_present"
    NOT_PARSEABLE = "not_parseable"
    NOT_NORMALIZABLE = "not_normalizable"
    WITHHELD_OR_REDACTED = "withheld_or_redacted"


class MixedValueStatus(str, Enum):
    NOT_MIXED = "not_mixed"
    RANGE_EXPRESSION = "range_expression"
    MULTI_VALUE_EXPRESSION = "multi_value_expression"
    MIXED_DETECTED = "mixed_detected"


class RangeCheckResult(str, Enum):
    NOT_CHECKED = "not_checked"
    IN_RANGE = "in_range"
    SUSPICIOUS = "suspicious"
    OUT_OF_RANGE = "out_of_range"


class PrecisionKind(str, Enum):
    EXACT = "exact"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class NormalizationScopeKind(str, Enum):
    NORMALIZATION_RUN = "normalization_run"
    NORMALIZED_RECORD_SET = "normalized_record_set"
    NORMALIZED_RECORD = "normalized_record"
    NORMALIZED_FIELD = "normalized_field"
    NON_NORMALIZABLE_FIELD = "non_normalizable_field"
    PARTIAL_NORMALIZATION = "partial_normalization"
