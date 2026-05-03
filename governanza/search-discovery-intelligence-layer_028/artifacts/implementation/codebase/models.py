"""Data objects emitted by motor_028."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field as dataclass_field
from typing import Any


@dataclass(frozen=True)
class DiscoveryPlan:
    plan_id: str
    request_id: str
    scope_terms: list[str]
    original_scope_terms: list[str]
    queries: list[dict[str, Any]]
    filters: dict[str, Any]
    seed_source_ids: list[str]
    taxonomy_version: str
    input_versions: dict[str, str | None]
    access_restrictions: list[str]
    stop_conditions: list[str]
    created_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceCandidateRecord:
    candidate_id: str
    run_id: str
    locator: str
    title: str
    publisher: str | None
    source_type: str
    domain_taxonomic: list[str]
    matched_terms: list[str]
    discovery_reason: str
    discovery_method: str
    discovered_at: str
    candidate_status: str
    discovery_classification: str
    linked_source_id: str | None
    duplicate_of_candidate_id: str | None
    rights_review_required: bool
    access_class: str | None
    provenance: dict[str, Any]
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoverageGapRecord:
    gap_id: str
    run_id: str
    scope_terms: list[str]
    gap_type: str
    severity: str
    supporting_signal_ids: list[str]
    evidence: dict[str, Any]
    taxonomy_relation: dict[str, Any]
    observed_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiscoveryRejectionRecord:
    rejection_id: str
    run_id: str
    locator: str | None
    reason_code: str
    reason_detail: str
    observed_at: str
    source_ref: str | None
    provenance: dict[str, Any]
    produced_by_motor: str
    produced_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiscoveryRunManifest:
    run_id: str
    plan_id: str
    input_versions: dict[str, str | None]
    executed_queries: list[dict[str, Any]]
    candidate_ids: list[str]
    rejection_ids: list[str]
    limitations_observed: list[str]
    run_started_at: str
    run_completed_at: str
    run_status: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiscoveryResult:
    discovery_plan: DiscoveryPlan
    source_candidate_records: list[SourceCandidateRecord] = dataclass_field(
        default_factory=list
    )
    coverage_gap_records: list[CoverageGapRecord] = dataclass_field(default_factory=list)
    discovery_run_manifest: DiscoveryRunManifest | None = None
    discovery_rejection_records: list[DiscoveryRejectionRecord] = dataclass_field(
        default_factory=list
    )
    degradation_signals: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "discovery_plan": self.discovery_plan.to_dict(),
            "source_candidate_record": [
                item.to_dict() for item in self.source_candidate_records
            ],
            "coverage_gap_record": [
                item.to_dict() for item in self.coverage_gap_records
            ],
            "discovery_run_manifest": (
                self.discovery_run_manifest.to_dict()
                if self.discovery_run_manifest is not None
                else None
            ),
            "discovery_rejection_record": [
                item.to_dict() for item in self.discovery_rejection_records
            ],
            "degradation_signals": [dict(item) for item in self.degradation_signals],
        }
