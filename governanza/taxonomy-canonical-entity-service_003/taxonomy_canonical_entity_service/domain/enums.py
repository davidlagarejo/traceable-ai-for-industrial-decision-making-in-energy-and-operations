from __future__ import annotations

from enum import Enum


class PhaseId(str, Enum):
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"


class TaxonomyDomain(str, Enum):
    SOURCE_FAMILY = "source_family"
    PUBLISHER_TYPE = "publisher_type"
    JURISDICTION = "jurisdiction"
    GEOGRAPHY = "geography"
    SECTOR = "sector"
    SUBSECTOR = "subsector"
    BENCHMARK_FAMILY = "benchmark_family"
    REGULATORY_FAMILY = "regulatory_family"
    FACILITY_TYPE = "facility_type"
    SYSTEM_FAMILY = "system_family"
    ASSET_FAMILY = "asset_family"
    ARCHETYPE_FAMILY = "archetype_family"
    CLIMATE_ENERGY_CONTEXT_FAMILY = "climate_energy_context_family"
    REGULATORY_TRIGGER_FAMILY = "regulatory_trigger_family"
    PRIOR_ASSUMPTION_FAMILY = "prior_assumption_family"
    UNCERTAINTY_FAMILY = "uncertainty_family"
    INFERENCE_CASE_FAMILY = "inference_case_family"
    TENSION_FAMILY = "tension_family"
    CONFLICT_FAMILY = "conflict_family"
    OPPORTUNITY_FAMILY = "opportunity_family"
    EVIDENCE_GAP_FAMILY = "evidence_gap_family"
    VALIDATION_ACTION_FAMILY = "validation_action_family"
    OUTPUT_BLOCK_TYPE = "output_block_type"
    ARTIFACT_TYPE = "artifact_type"
    AUDIENCE_VIEW_TYPE = "audience_view_type"
    REPORT_PACKAGE_COMPONENT_TYPE = "report_package_component_type"
    CLAIM_UPGRADE_CANDIDATE_FAMILY = "claim_upgrade_candidate_family"
    REQUIRED_SITE_EVIDENCE_FAMILY = "required_site_evidence_family"
    BASELINE_HARDENING_FAMILY = "baseline_hardening_family"
    INSTRUMENTATION_GAP_FAMILY = "instrumentation_gap_family"
    UPGRADE_DECISION_FAMILY = "upgrade_decision_family"


class CanonicalEntityKind(str, Enum):
    FACILITY = "facility"
    SYSTEM = "system"
    SUBSYSTEM = "subsystem"
    EQUIPMENT = "equipment"
    FUEL = "fuel"
    ENERGY_VECTOR = "energy_vector"
    METRIC = "metric"
    REGULATORY_FRAMEWORK = "regulatory_framework"
    MEASUREMENT_INSTRUMENT = "measurement_instrument"
    EVIDENCE_TYPE = "evidence_type"
    CLAIM_FAMILY = "claim_family"


class TaxonomyRegistryStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class TaxonomyVersionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RETIRED = "retired"


class TaxonomyNodeType(str, Enum):
    ROOT = "root"
    INTERNAL = "internal"
    LEAF = "leaf"


class NodeStatus(str, Enum):
    ACTIVE = "active"
    PROVISIONAL = "provisional"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class TermLifecycleStatus(str, Enum):
    ACTIVE = "active"
    LEGACY_ONLY = "legacy_only"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class AliasKind(str, Enum):
    ALIAS = "alias"
    SYNONYM = "synonym"


class AliasStatus(str, Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


class EntityStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    MERGED = "merged"
    RETIRED = "retired"


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    CONDITIONAL = "conditional"
    DEPRECATED = "deprecated"


class EquivalenceStatus(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CONTEXTUAL = "contextual"


class MatchStatus(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    AMBIGUOUS = "ambiguous"


class SemanticRelationType(str, Enum):
    BROADER = "broader"
    NARROWER = "narrower"
    EQUIVALENT = "equivalent"
    RELATED = "related"
    INCOMPATIBLE = "incompatible"
    AMBIGUOUS = "ambiguous"


class AmbiguityStatus(str, Enum):
    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class JoinSafetyLevel(str, Enum):
    SAFE = "safe"
    CONDITIONAL = "conditional"
    UNSAFE = "unsafe"


class BoundaryStatus(str, Enum):
    DEFINED = "defined"
    PROVISIONAL = "provisional"
    INSUFFICIENT = "insufficient"


class DeprecationStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REPLACED = "replaced"
    RETIRED = "retired"


class TaxonomyChangeKind(str, Enum):
    ADDITIVE = "additive"
    RENAME = "rename"
    DEPRECATION = "deprecation"
    SPLIT = "split"
    MERGE = "merge"
    BOUNDARY_REDEFINITION = "boundary_redefinition"
    RELATION_CHANGE = "relation_change"


class ComparabilityStatus(str, Enum):
    COMPARABLE = "comparable"
    CONDITIONALLY_COMPARABLE = "conditionally_comparable"
    NOT_COMPARABLE = "not_comparable"


class ConflictSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SemanticIntegrityStatus(str, Enum):
    OK = "ok"
    ISSUES_PRESENT = "issues_present"
    BROKEN = "broken"


class TaxonomyLocatorKind(str, Enum):
    TAXONOMY_REGISTRY = "taxonomy_registry"
    TAXONOMY_VERSION = "taxonomy_version"
    TAXONOMY_NODE = "taxonomy_node"
    CANONICAL_TERM = "canonical_term"
    ALIAS_RECORD = "alias_record"
    LEGACY_TERM_RECORD = "legacy_term_record"
    CANONICAL_ENTITY = "canonical_entity"

