"""Data objects emitted by motor_018."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationDataSet:
    validation_data_set_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    evidence_level: str
    validation_scope: str
    destination_policy_ref: str | None
    source_registry_snapshot_id: str
    bridge_record_ids: list[str]
    inclusion_criteria: list[str]
    exclusion_summary: dict[str, int]
    warning_summary: dict[str, int]
    restriction_refs: list[str]
    bridge_manifest_id: str
    evidentiary_record_id: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BridgeRecord:
    bridge_record_id: str
    validation_data_set_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_id: str
    rights_profile_id: str
    access_class: str
    ingestion_record_id: str
    raw_record_ref: str
    parsed_record_ref: str | None
    normalized_record_id: str
    original_value_ref: str
    canonical_value_ref: str
    normalization_rule_ref: str
    identity_record_id: str | None
    identity_ambiguity_flag: bool
    quality_record_id: str
    fitness_score: float | None
    quality_flags: list[str]
    disqualification_reason: str | None
    validation_status: str
    warning_codes: list[str]
    exclusion_reason: str | None
    evidence_level: str
    evidentiary_link_ids: list[str]
    restriction_refs: list[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidentiaryLink:
    evidentiary_link_id: str
    bridge_record_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    upstream_motor_id: str
    upstream_artifact_ref: str
    link_type: str
    evidence_level: str
    restriction_refs: list[str]
    lineage_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BridgeManifest:
    bridge_manifest_id: str
    validation_data_set_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_registry_snapshot_id: str
    source_ids: list[str]
    included_record_ids: list[str]
    excluded_record_refs: list[str]
    exclusion_reasons: dict[str, str]
    warning_reasons: dict[str, list[str]]
    restriction_refs: list[str]
    rebuild_inputs: dict[str, list[str]]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidentiaryRecord:
    evidentiary_record_id: str
    validation_data_set_id: str
    bridge_manifest_id: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    evidence_level: str
    validation_scope: str
    evidentiary_link_ids: list[str]
    limits_of_use: list[str]
    restriction_refs: list[str]
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationBridgeResult:
    validation_data_set: ValidationDataSet
    bridge_records: list[BridgeRecord]
    evidentiary_links: list[EvidentiaryLink]
    bridge_manifest: BridgeManifest
    evidentiary_record: EvidentiaryRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_data_set": self.validation_data_set.to_dict(),
            "bridge_records": [record.to_dict() for record in self.bridge_records],
            "evidentiary_links": [link.to_dict() for link in self.evidentiary_links],
            "bridge_manifest": self.bridge_manifest.to_dict(),
            "evidentiary_record": self.evidentiary_record.to_dict(),
        }
