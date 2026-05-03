"""Output models for motor_012.

The dataclasses mirror the Public Data Engine technical schema. They preserve
upstream source, quality, library, provenance, and lineage references while
keeping Fase 2 inference objects outside this motor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class FacilityPrior:
    facility_prior_id: str
    record_id: str
    facility_ref: str
    prior_scope: str
    library_object_refs: list[str]
    source_refs: list[str]
    source_registry_snapshot_ref: str
    quality_record_refs: list[str]
    contextual_bundle_refs: list[str]
    input_snapshot_refs: dict[str, str]
    eligibility_rule_version: str
    packaging_run_id: str
    exclusion_record_refs: list[str]
    provenance_refs: list[str]
    lineage_refs: list[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContextualBundle:
    bundle_id: str
    record_id: str
    facility_prior_ref: str
    facility_ref: str
    context_scope: str
    library_object_refs: list[str]
    source_refs: list[str]
    quality_record_refs: list[str]
    source_registry_snapshot_ref: str
    bundle_rule_version: str
    bundle_fingerprint: str
    exclusion_record_refs: list[str]
    provenance_refs: list[str]
    lineage_refs: list[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Phase1Package:
    package_id: str
    record_id: str
    package_version: str
    package_scope: str
    generated_at: str
    facility_prior_ref: str
    contextual_bundle_refs: list[str]
    input_snapshot_refs: dict[str, str]
    source_registry_snapshot_ref: str
    library_object_refs: list[str]
    source_refs: list[str]
    quality_record_refs: list[str]
    validation_status: str
    rejection_refs: list[str]
    packaging_run_id: str
    packaging_rule_version: str
    provenance_refs: list[str]
    lineage_refs: list[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PackagingRejection:
    packaging_rejection_id: str
    record_id: str
    candidate_ref: str
    candidate_type: str
    error_code: str
    blocking_rule: str
    blocking_reference_refs: list[str]
    affected_output_ref: Optional[str]
    exclusion_scope: str
    provenance_refs: list[str]
    lineage_refs: list[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicDataResult:
    facility_prior: Optional[FacilityPrior]
    contextual_bundle: list[ContextualBundle]
    phase1_package: Optional[Phase1Package]
    packaging_rejection: list[PackagingRejection]

    @property
    def status(self) -> str:
        if self.phase1_package is None:
            return "rejected"
        return self.phase1_package.validation_status

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "facility_prior": (
                self.facility_prior.to_dict() if self.facility_prior else None
            ),
            "contextual_bundle": [
                item.to_dict() for item in self.contextual_bundle
            ],
            "phase1_package": (
                self.phase1_package.to_dict() if self.phase1_package else None
            ),
            "packaging_rejection": [
                item.to_dict() for item in self.packaging_rejection
            ],
        }
