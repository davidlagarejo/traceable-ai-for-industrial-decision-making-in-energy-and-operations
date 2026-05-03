"""Output objects for motor_010.

The dataclasses mirror the technical schema and keep outputs reference-based.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class SimilarityRecord:
    similarity_id: str
    left_record_ref: str
    right_record_ref: str
    comparison_level: str
    similarity_score: float
    similarity_kind: str
    method_version: str
    evidence_features: list[str]
    threshold_profile_ref: Optional[str]
    version_context_refs: list[str]
    cluster_id: Optional[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: list[str]
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DuplicateCluster:
    cluster_id: str
    member_record_refs: list[str]
    cluster_fingerprint: str
    match_scope: str
    cluster_kind: str
    evidence_refs: list[str]
    method_version: str
    threshold_profile_ref: Optional[str]
    version_context_refs: list[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: list[str]
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeduplicationDecision:
    decision_id: str
    cluster_id: str
    recommendation: str
    target_record_refs: list[str]
    rationale_refs: list[str]
    decision_status: str
    method_version: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: list[str]
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DuplicateSimilarityResult:
    duplicate_cluster: list[DuplicateCluster]
    similarity_score: list[SimilarityRecord]
    dedup_recommendation: list[DeduplicationDecision]

    def to_dict(self) -> dict[str, Any]:
        return {
            "duplicate_cluster": [cluster.to_dict() for cluster in self.duplicate_cluster],
            "similarity_score": [score.to_dict() for score in self.similarity_score],
            "dedup_recommendation": [
                decision.to_dict() for decision in self.dedup_recommendation
            ],
        }


@dataclass(frozen=True)
class ThresholdProfile:
    ref: str = "threshold:default:2026-04"
    near_duplicate_threshold: float = 0.92
    manual_review_floor: float = 0.85

    @classmethod
    def from_mapping(
        cls,
        threshold_profile_ref: Optional[str],
        threshold_profile: Optional[dict[str, Any]],
    ) -> "ThresholdProfile":
        if threshold_profile is None:
            return cls(ref=threshold_profile_ref or cls.ref)

        ref = str(threshold_profile_ref or threshold_profile.get("ref") or cls.ref)
        near = float(
            threshold_profile.get("near_duplicate_threshold", cls.near_duplicate_threshold)
        )
        manual = float(threshold_profile.get("manual_review_floor", cls.manual_review_floor))
        if not (0.0 <= manual <= near <= 1.0):
            from .errors import DuplicateInputError

            raise DuplicateInputError(
                code="DUPLICATE_INPUT_INVALID_THRESHOLD_PROFILE",
                message="threshold profile must satisfy 0.0 <= manual_review_floor <= near_duplicate_threshold <= 1.0",
                field="threshold_profile",
            )
        return cls(
            ref=ref,
            near_duplicate_threshold=near,
            manual_review_floor=manual,
        )
