"""Output models for motor_006."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CandidateMatch:
    candidate_match_id: str
    record_id: str
    candidate_ref: str
    candidate_type: str
    match_features: Dict[str, Any]
    match_result: str
    rule_version: str
    evidence_refs: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IdentityRecord:
    identity_record_id: str
    evaluated_record_ids: List[str]
    decision: str
    confidence_band: str
    evidence_refs: List[str]
    rule_version: str
    lineage_refs: List[str]
    ambiguity_flag_id: Optional[str]
    conflict_ids: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EntityCluster:
    entity_cluster_id: str
    canonical_entity_id: Optional[str]
    member_record_ids: List[str]
    cluster_status: str
    identity_record_ids: List[str]
    lineage_refs: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResolutionConflict:
    conflict_id: str
    involved_record_ids: List[str]
    involved_candidate_match_ids: List[str]
    conflict_type: str
    blocking_reason: str
    recommended_next_step: str
    related_identity_record_ids: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AmbiguityFlag:
    ambiguity_flag_id: str
    identity_record_id: str
    ambiguity_reason: str
    severity: str
    affected_record_ids: List[str]
    evidence_refs: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
