from __future__ import annotations

from enum import Enum


class PhaseId(str, Enum):
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"


class ObjectKind(str, Enum):
    SOURCE_RECORD = "source_record"
    SOURCE_VERSION = "source_version"
    RAW_ASSET = "raw_asset"
    PARSED_OBJECT = "parsed_object"
    NORMALIZED_OBJECT = "normalized_object"
    BUNDLE = "bundle"
    FACILITY_PRIOR = "facility_prior"
    UNCERTAINTY_MARKER = "uncertainty_marker"
    PRIOR_ASSUMPTION = "prior_assumption"
    REGULATORY_FLAG = "regulatory_flag"
    BENCHMARK_BUNDLE = "benchmark_bundle"
    INFERENCE_CASE_REGISTER = "inference_case_register"
    HYPOTHESIS_REGISTER = "hypothesis_register"
    TENSION_MAP = "tension_map"
    CONFLICT_REGISTER = "conflict_register"
    OPPORTUNITY_CANDIDATE_MATRIX = "opportunity_candidate_matrix"
    EVIDENCE_GAP_REGISTER = "evidence_gap_register"
    VALIDATION_QUEUE = "validation_queue"
    NEXT_BEST_QUESTIONS = "next_best_questions"
    OUTPUT_BLOCK = "output_block"
    ARTIFACT = "artifact"
    AUDIENCE_VIEW = "audience_view"
    MACHINE_EXPORT_BUNDLE = "machine_export_bundle"
    REPORT_PACKAGE = "report_package"
    CLAIM_UPGRADE_CANDIDATE_REGISTER = "claim_upgrade_candidate_register"
    REQUIRED_SITE_EVIDENCE_REGISTER = "required_site_evidence_register"
    BASELINE_HARDENING_REGISTER = "baseline_hardening_register"
    INSTRUMENTATION_GAP_REGISTER = "instrumentation_gap_register"
    CLAIM_UPGRADE_DECISION_MAP = "claim_upgrade_decision_map"
    DO_NOT_UPGRADE_REGISTER = "do_not_upgrade_register"


class DependencyType(str, Enum):
    SOURCE_INPUT = "source_input"
    DERIVES_FROM = "derives_from"
    AGGREGATES = "aggregates"
    USES_CONTRACT = "uses_contract"
    USES_TAXONOMY = "uses_taxonomy"
    USES_RULE_PACK = "uses_rule_pack"
    USES_LIBRARY = "uses_library"
    USES_MODEL = "uses_model"
    REPLACES = "replaces"


class DependencyTargetKind(str, Enum):
    OBJECT_IDENTITY = "object_identity"
    OBJECT_VERSION = "object_version"
    REFERENCE_VERSION = "reference_version"


class IdentityStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REPLACED = "replaced"
    REPLACEMENT = "replacement"


class VersionLifecycleStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RECONSTRUCTED = "reconstructed"
    RETIRED = "retired"


class StaleState(str, Enum):
    FRESH = "fresh"
    STALE_REBUILD_RECOMMENDED = "stale_rebuild_recommended"
    STALE_MIGRATION_REQUIRED = "stale_migration_required"
    STALE_BLOCKED = "stale_blocked"


class ImpactSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeSeverity(str, Enum):
    ADDITIVE = "additive"
    RESTRICTIVE = "restrictive"
    BREAKING = "breaking"
    UNKNOWN = "unknown"


class ChangeKind(str, Enum):
    CONTENT_ADDED = "content_added"
    CONTENT_REMOVED = "content_removed"
    DEPENDENCY_PIN_CHANGED = "dependency_pin_changed"
    METADATA_CHANGED = "metadata_changed"
    STATUS_CHANGED = "status_changed"
    COMPOSITION_CHANGED = "composition_changed"
    FINGERPRINT_CHANGED = "fingerprint_changed"
    SEMANTIC_CHANGED = "semantic_changed"


class RebuildabilityStatus(str, Enum):
    REBUILDABLE = "rebuildable"
    PARTIALLY_REBUILDABLE = "partially_rebuildable"
    NOT_REBUILDABLE = "not_rebuildable"


class ComparabilityStatus(str, Enum):
    COMPARABLE = "comparable"
    CONDITIONALLY_COMPARABLE = "conditionally_comparable"
    NOT_COMPARABLE = "not_comparable"


class RetentionStatus(str, Enum):
    ACTIVE = "active"
    RETAINED = "retained"
    ARCHIVE_CANDIDATE = "archive_candidate"
    ARCHIVED = "archived"


class LineageIntegrityStatus(str, Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    BROKEN = "broken"


class ReferenceKind(str, Enum):
    CONTRACT_VERSION = "contract_version"
    TAXONOMY_VERSION = "taxonomy_version"
    RULE_PACK_VERSION = "rule_pack_version"
    LIBRARY_VERSION = "library_version"
    MODEL_VERSION = "model_version"
    ENGINE_VERSION = "engine_version"
