from __future__ import annotations

from enum import Enum


class EntityType(str, Enum):
    PUBLISHER = "publisher"
    ISSUING_BODY = "issuing_body"
    UTILITY = "utility"
    JURISDICTIONAL_BODY = "jurisdictional_body"
    STANDARD_FRAMEWORK_ISSUER = "standard_framework_issuer"
    FACILITY = "facility"
    PLANT = "plant"
    CAMPUS = "campus"
    BUILDING = "building"
    SYSTEM = "system"
    SUBSYSTEM = "subsystem"
    ASSET = "asset"
    EQUIPMENT_FAMILY = "equipment_family"
    INSTRUMENTATION_ITEM = "instrumentation_item"
    BENCHMARK_SOURCE_FAMILY = "benchmark_source_family"
    REGULATORY_REFERENCE = "regulatory_reference"
    METHODOLOGY_DOCUMENT = "methodology_document"
    CASE_STUDY_REFERENCE = "case_study_reference"
    EVIDENCE_SOURCE_FAMILY = "evidence_source_family"


class CanonicalEntityStatus(str, Enum):
    ACTIVE = "active"
    MERGED = "merged"
    SPLIT = "split"
    RETIRED = "retired"


class ResolutionStatus(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    NO_MATCH = "no_match"
    AMBIGUOUS = "ambiguous"
    RELATED_NOT_EQUIVALENT = "related_not_equivalent"
    MERGED = "merged"
    SPLIT = "split"


class ResolutionMode(str, Enum):
    AUTO_RESOLVED = "auto_resolved"
    HUMAN_CONFIRMED = "human_confirmed"
    HUMAN_REJECTED = "human_rejected"
    CARRIED_FORWARD = "carried_forward"


class ConfidenceStatus(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class CandidateMatchStatus(str, Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class AmbiguityStatus(str, Enum):
    OPEN = "open"
    NEEDS_REVIEW = "needs_review"
    CARRIED_FORWARD = "carried_forward"
    RESOLVED = "resolved"


class HistoricalEventType(str, Enum):
    MERGE = "merge"
    SPLIT = "split"


class EvidenceBasisType(str, Enum):
    EXACT_EXTERNAL_IDENTIFIER = "exact_external_identifier"
    GOVERNED_ALIAS = "governed_alias"
    NORMALIZED_NAME = "normalized_name"
    PARENT_CONTEXT = "parent_context"
    JURISDICTION_CONTEXT = "jurisdiction_context"
    OWNER_OPERATOR_CONTEXT = "owner_operator_context"
    DOCUMENT_ISSUER_CONTEXT = "document_issuer_context"
    TAXONOMY_CONTEXT = "taxonomy_context"
    STRUCTURAL_CONTEXT = "structural_context"
    HUMAN_ASSERTION = "human_assertion"


class HistoryStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    MERGED = "merged"
    SPLIT = "split"
    CLOSED = "closed"


class RelatedEntityRelationshipType(str, Enum):
    PARENT_CHILD = "parent_child"
    SIBLING = "sibling"
    ISSUER_DOCUMENT = "issuer_document"
    FACILITY_SYSTEM = "facility_system"
    CAMPUS_BUILDING = "campus_building"
    SOURCE_FAMILY_MEMBER = "source_family_member"
    OPERATOR_ASSET = "operator_asset"
    OTHER_GOVERNED = "other_governed"
