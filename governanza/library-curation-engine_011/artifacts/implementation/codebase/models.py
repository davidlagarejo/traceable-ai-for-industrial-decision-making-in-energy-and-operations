"""Output models for motor_011.

The dataclasses mirror the Library Curation Engine technical schema and keep
all upstream quality, identity, and duplicate evidence as references.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class LibraryObject:
    library_object_id: str
    source_object_ref: str
    quality_record_ref: str
    identity_record_ref: str
    dedup_evidence_refs: list[str]
    curation_status: str
    curation_rule_version: str
    curation_run_id: str
    bundle_scope: str
    warning_refs: list[str]
    rejection_reason_ref: Optional[str]
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


@dataclass
class CuratedBundle:
    curated_bundle_id: str
    bundle_scope: str
    member_library_object_refs: list[str]
    excluded_candidate_refs: list[str]
    rejection_refs: list[str]
    selection_rule_version: str
    curation_run_id: str
    membership_fingerprint: str
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


@dataclass
class LibraryVersion:
    library_version_id: str
    version_id: str
    versioned_object_ref: str
    versioned_object_type: str
    content_fingerprint: str
    version_hash: str
    prior_version_ref: Optional[str]
    curation_rule_version: str
    rebuild_manifest_ref: Optional[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]
    lineage_refs: list[str]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CurationRejection:
    curation_rejection_id: str
    candidate_ref: str
    error_code: str
    blocking_evidence_refs: list[str]
    quality_record_ref: Optional[str]
    identity_record_ref: Optional[str]
    dedup_evidence_refs: list[str]
    curation_run_id: str
    curation_rule_version: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]
    created_at: str
    updated_at: str
    version_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CurationResult:
    library_object: list[LibraryObject]
    curated_bundle: CuratedBundle
    library_version: list[LibraryVersion]
    curation_rejection: list[CurationRejection]

    def to_dict(self) -> dict[str, Any]:
        return {
            "library_object": [item.to_dict() for item in self.library_object],
            "curated_bundle": self.curated_bundle.to_dict(),
            "library_version": [item.to_dict() for item in self.library_version],
            "curation_rejection": [
                item.to_dict() for item in self.curation_rejection
            ],
        }
