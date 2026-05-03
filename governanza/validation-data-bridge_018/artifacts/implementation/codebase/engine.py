"""Deterministic implementation for motor_018.

The bridge connects already-processed real upstream records to a validation
dataset. It does not ingest new files, normalize values, resolve identities,
score quality, make verification decisions, or create field evidence.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass, replace
from decimal import Decimal
import hashlib
import json
from typing import Any

from .errors import ValidationDataBridgeError
from .models import (
    BridgeManifest,
    BridgeRecord,
    EvidentiaryLink,
    EvidentiaryRecord,
    ValidationBridgeResult,
    ValidationDataSet,
)


MOTOR_ID = "motor_018"
EVIDENCE_LEVEL = "validation_data"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
DEFAULT_INCLUSION_CRITERIA = [
    "registered_source",
    "validation_rights_allowed",
    "complete_ingestion_lineage",
    "complete_normalization_trace",
    "quality_not_disqualified",
]

SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"
SOURCE_NOT_REGISTERED = "SOURCE_NOT_REGISTERED"
RIGHTS_PROFILE_DENIES_VALIDATION = "RIGHTS_PROFILE_DENIES_VALIDATION"
RIGHTS_RESTRICTION_CONFLICT = "RIGHTS_RESTRICTION_CONFLICT"
MISSING_INGESTION_LINEAGE = "MISSING_INGESTION_LINEAGE"
MISSING_NORMALIZATION_TRACE = "MISSING_NORMALIZATION_TRACE"
MISSING_QUALITY_RECORD = "MISSING_QUALITY_RECORD"
SYNTHETIC_INPUT_NOT_ALLOWED = "SYNTHETIC_INPUT_NOT_ALLOWED"
QUALITY_DISQUALIFIED = "QUALITY_DISQUALIFIED"
LOW_FITNESS_SCORE = "LOW_FITNESS_SCORE"
MANIFEST_MISMATCH = "MANIFEST_MISMATCH"
EVIDENCE_LEVEL_INVALID = "EVIDENCE_LEVEL_INVALID"

LOW_FITNESS_WARNING = "low_fitness_score"
IDENTITY_AMBIGUOUS_WARNING = "identity_ambiguous"
RESTRICTED_RIGHTS_WARNING = "restricted_rights"


class ValidationDataBridge:
    """Core deterministic interface for Validation Data Bridge."""

    def __init__(
        self,
        *,
        produced_at: str = DEFAULT_PRODUCED_AT,
        parent_ids: Mapping[str, str | None] | None = None,
    ) -> None:
        self.produced_at = _require_text(produced_at, "produced_at")
        self.parent_ids = dict(parent_ids or {})

    def run(
        self,
        *,
        source_registry: Mapping[str, Any],
        ingestion_records: Sequence[Mapping[str, Any]],
        normalized_records: Sequence[Mapping[str, Any]],
        identity_records: Sequence[Mapping[str, Any]] | None = None,
        quality_records: Sequence[Mapping[str, Any]],
        validation_scope: str,
        destination_policy_ref: str | None = None,
        inclusion_criteria: Sequence[str] | None = None,
        minimum_fitness_score: float | Decimal | int | None = None,
        low_fitness_policy: str = "warn",
    ) -> ValidationBridgeResult:
        """Build a validation data package from upstream Phase 1 records."""

        registry = _as_mapping(source_registry, "source_registry")
        ingestion_list = _record_list(ingestion_records, "ingestion_records")
        normalized_list = _record_list(normalized_records, "normalized_records")
        identity_list = _record_list(identity_records or [], "identity_records")
        quality_list = _record_list(quality_records, "quality_records")
        scope = _require_text(validation_scope, "validation_scope")
        destination = _optional_text(destination_policy_ref, "destination_policy_ref")
        criteria = _string_list(
            inclusion_criteria if inclusion_criteria is not None else DEFAULT_INCLUSION_CRITERIA,
            "inclusion_criteria",
        )
        threshold = _optional_number(minimum_fitness_score, "minimum_fitness_score")
        low_policy = _require_text(low_fitness_policy, "low_fitness_policy")
        if low_policy not in {"warn", "exclude"}:
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "low_fitness_policy must be 'warn' or 'exclude'",
                field="low_fitness_policy",
            )

        registry_index = _source_registry_index(registry)
        source_registry_snapshot_id = registry_index["snapshot_id"]
        source_ref = f"source_registry:{source_registry_snapshot_id}"
        sources_by_id = registry_index["sources"]
        ingestion_by_id = _index_by_required_id(
            ingestion_list, "ingestion_record_id", "ingestion_records"
        )
        quality_by_id = _index_by_required_id(
            quality_list, "quality_record_id", "quality_records"
        )
        quality_by_normalized_id = _index_by_optional_unique_id(
            quality_list,
            "normalized_record_id",
            "quality_records.normalized_record_id",
        )
        identity_by_id = _index_by_required_id(
            identity_list,
            "identity_record_id",
            "identity_records",
        )
        identity_by_normalized_id = _index_by_optional_unique_id(
            identity_list,
            "normalized_record_id",
            "identity_records.normalized_record_id",
        )

        records: list[BridgeRecord] = []
        links: list[EvidentiaryLink] = []
        exclusion_reasons: dict[str, str] = {}
        warning_reasons: dict[str, list[str]] = {}
        source_ids_observed: set[str] = set()
        restriction_refs: set[str] = set()

        for index, normalized in enumerate(
            sorted(normalized_list, key=lambda record: _sort_key(record, "normalized_record_id"))
        ):
            classification = self._classify_candidate(
                index=index,
                normalized=normalized,
                sources_by_id=sources_by_id,
                ingestion_by_id=ingestion_by_id,
                quality_by_id=quality_by_id,
                quality_by_normalized_id=quality_by_normalized_id,
                identity_by_id=identity_by_id,
                identity_by_normalized_id=identity_by_normalized_id,
                destination_policy_ref=destination,
                minimum_fitness_score=threshold,
                low_fitness_policy=low_policy,
            )
            source_id = classification.get("source_id")
            if source_id:
                source_ids_observed.add(source_id)

            exclusion_reason = classification.get("exclusion_reason")
            if exclusion_reason:
                exclusion_reasons[classification["candidate_ref"]] = exclusion_reason
                restriction_refs.update(classification.get("restriction_refs", []))
                continue

            record, record_links = self._build_included_record(classification)
            records.append(record)
            links.extend(record_links)
            restriction_refs.update(record.restriction_refs)
            if record.warning_codes:
                warning_reasons[record.bridge_record_id] = list(record.warning_codes)

        bridge_record_ids = [record.bridge_record_id for record in records]
        all_link_ids = [link.evidentiary_link_id for link in links]
        exclusion_summary = dict(sorted(Counter(exclusion_reasons.values()).items()))
        warning_summary = _warning_summary(warning_reasons)
        restriction_list = sorted(restriction_refs)
        rebuild_inputs = _rebuild_inputs(
            source_registry_snapshot_id=source_registry_snapshot_id,
            ingestion_records=ingestion_list,
            normalized_records=normalized_list,
            identity_records=identity_list,
            quality_records=quality_list,
        )

        dataset_base = {
            "validation_scope": scope,
            "destination_policy_ref": destination,
            "source_registry_snapshot_id": source_registry_snapshot_id,
            "bridge_record_ids": bridge_record_ids,
            "inclusion_criteria": criteria,
            "exclusion_summary": exclusion_summary,
            "warning_summary": warning_summary,
            "restriction_refs": restriction_list,
            "source_ref": source_ref,
            "parent_id": self.parent_ids.get("validation_data_set"),
            "produced_by_motor": MOTOR_ID,
        }
        dataset_hash = _stable_hash(dataset_base)
        dataset_id = f"{MOTOR_ID}:validation_data_set:{scope}:{_hash_prefix(dataset_hash)}"

        manifest_base = {
            "validation_data_set_id": dataset_id,
            "source_registry_snapshot_id": source_registry_snapshot_id,
            "source_ids": sorted(source_ids_observed),
            "included_record_ids": bridge_record_ids,
            "excluded_record_refs": sorted(exclusion_reasons),
            "exclusion_reasons": dict(sorted(exclusion_reasons.items())),
            "warning_reasons": dict(sorted(warning_reasons.items())),
            "restriction_refs": restriction_list,
            "rebuild_inputs": rebuild_inputs,
            "source_ref": source_ref,
            "parent_id": self.parent_ids.get("bridge_manifest"),
            "produced_by_motor": MOTOR_ID,
        }
        manifest_hash = _stable_hash(manifest_base)
        manifest_id = f"{MOTOR_ID}:bridge_manifest:{dataset_id}:{_hash_prefix(manifest_hash)}"

        limits_of_use = [
            "Output evidence_level is validation_data only.",
            "This record is not field_evidence.",
            "This record cannot close claims or emit truth decisions by itself.",
            "Rights, access, license and redistribution restrictions remain binding.",
        ]
        evidentiary_base = {
            "validation_data_set_id": dataset_id,
            "bridge_manifest_id": manifest_id,
            "evidence_level": EVIDENCE_LEVEL,
            "validation_scope": scope,
            "evidentiary_link_ids": all_link_ids,
            "limits_of_use": limits_of_use,
            "restriction_refs": restriction_list,
            "source_ref": f"{dataset_id}|{source_ref}",
            "parent_id": self.parent_ids.get("evidentiary_record"),
            "produced_by_motor": MOTOR_ID,
        }
        evidentiary_hash = _stable_hash(evidentiary_base)
        evidentiary_record_id = (
            f"{MOTOR_ID}:evidentiary_record:{dataset_id}:{_hash_prefix(evidentiary_hash)}"
        )

        records = [
            replace(record, validation_data_set_id=dataset_id)
            for record in records
        ]
        validation_data_set = ValidationDataSet(
            validation_data_set_id=dataset_id,
            version_id=f"{MOTOR_ID}:v:validation_data_set:{_hash_prefix(dataset_hash)}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=dataset_hash,
            evidence_level=EVIDENCE_LEVEL,
            validation_scope=scope,
            destination_policy_ref=destination,
            source_registry_snapshot_id=source_registry_snapshot_id,
            bridge_record_ids=bridge_record_ids,
            inclusion_criteria=criteria,
            exclusion_summary=exclusion_summary,
            warning_summary=warning_summary,
            restriction_refs=restriction_list,
            bridge_manifest_id=manifest_id,
            evidentiary_record_id=evidentiary_record_id,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=self.parent_ids.get("validation_data_set"),
        )
        bridge_manifest = BridgeManifest(
            bridge_manifest_id=manifest_id,
            validation_data_set_id=dataset_id,
            version_id=f"{MOTOR_ID}:v:bridge_manifest:{_hash_prefix(manifest_hash)}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=manifest_hash,
            source_registry_snapshot_id=source_registry_snapshot_id,
            source_ids=sorted(source_ids_observed),
            included_record_ids=bridge_record_ids,
            excluded_record_refs=sorted(exclusion_reasons),
            exclusion_reasons=dict(sorted(exclusion_reasons.items())),
            warning_reasons=dict(sorted(warning_reasons.items())),
            restriction_refs=restriction_list,
            rebuild_inputs=rebuild_inputs,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=self.parent_ids.get("bridge_manifest"),
        )
        evidentiary_record = EvidentiaryRecord(
            evidentiary_record_id=evidentiary_record_id,
            validation_data_set_id=dataset_id,
            bridge_manifest_id=manifest_id,
            version_id=f"{MOTOR_ID}:v:evidentiary_record:{_hash_prefix(evidentiary_hash)}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=evidentiary_hash,
            evidence_level=EVIDENCE_LEVEL,
            validation_scope=scope,
            evidentiary_link_ids=all_link_ids,
            limits_of_use=limits_of_use,
            restriction_refs=restriction_list,
            source_ref=f"{dataset_id}|{source_ref}",
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=self.parent_ids.get("evidentiary_record"),
        )

        result = ValidationBridgeResult(
            validation_data_set=validation_data_set,
            bridge_records=records,
            evidentiary_links=links,
            bridge_manifest=bridge_manifest,
            evidentiary_record=evidentiary_record,
        )
        _assert_output_consistency(result)
        return result

    def _classify_candidate(
        self,
        *,
        index: int,
        normalized: Mapping[str, Any],
        sources_by_id: Mapping[str, Mapping[str, Any]],
        ingestion_by_id: Mapping[str, Mapping[str, Any]],
        quality_by_id: Mapping[str, Mapping[str, Any]],
        quality_by_normalized_id: Mapping[str, Mapping[str, Any]],
        identity_by_id: Mapping[str, Mapping[str, Any]],
        identity_by_normalized_id: Mapping[str, Mapping[str, Any]],
        destination_policy_ref: str | None,
        minimum_fitness_score: float | None,
        low_fitness_policy: str,
    ) -> dict[str, Any]:
        normalized_record_id = _require_text(
            normalized.get("normalized_record_id"),
            "normalized_records.normalized_record_id",
        )
        candidate_ref = normalized_record_id or f"normalized_record:{index}"
        source_id = _optional_text(normalized.get("source_id"), "normalized_records.source_id")
        ingestion_record_id = _optional_text(
            normalized.get("ingestion_record_id"),
            "normalized_records.ingestion_record_id",
        )
        quality_record_id_ref = _optional_text(
            normalized.get("quality_record_id"),
            "normalized_records.quality_record_id",
        )
        identity_record_id_ref = _optional_text(
            normalized.get("identity_record_id"),
            "normalized_records.identity_record_id",
        )

        if _has_synthetic_marker(normalized):
            return _excluded(candidate_ref, source_id, SYNTHETIC_INPUT_NOT_ALLOWED)

        if not source_id or source_id not in sources_by_id:
            return _excluded(candidate_ref, source_id, SOURCE_NOT_REGISTERED)
        source_entry = sources_by_id[source_id]
        restriction_refs = list(source_entry["restriction_refs"])
        if _has_synthetic_marker(source_entry.get("raw", {})):
            return _excluded(
                candidate_ref,
                source_id,
                SYNTHETIC_INPUT_NOT_ALLOWED,
                restriction_refs=restriction_refs,
            )
        rights_profile_id = source_entry["rights_profile_id"]
        if not rights_profile_id:
            return _excluded(
                candidate_ref,
                source_id,
                SOURCE_NOT_REGISTERED,
                restriction_refs=restriction_refs,
            )
        if not source_entry["validation_use"]:
            return _excluded(
                candidate_ref,
                source_id,
                RIGHTS_PROFILE_DENIES_VALIDATION,
                restriction_refs=restriction_refs,
            )
        if _destination_conflicts(destination_policy_ref, source_entry):
            return _excluded(
                candidate_ref,
                source_id,
                RIGHTS_RESTRICTION_CONFLICT,
                restriction_refs=restriction_refs,
            )

        if not ingestion_record_id or ingestion_record_id not in ingestion_by_id:
            return _excluded(
                candidate_ref,
                source_id,
                MISSING_INGESTION_LINEAGE,
                restriction_refs=restriction_refs,
            )
        ingestion = ingestion_by_id[ingestion_record_id]
        if _has_synthetic_marker(ingestion):
            return _excluded(
                candidate_ref,
                source_id,
                SYNTHETIC_INPUT_NOT_ALLOWED,
                restriction_refs=restriction_refs,
            )
        raw_record_ref = _optional_text(ingestion.get("raw_record_ref"), "raw_record_ref")
        ingestion_lineage = ingestion.get("ingestion_lineage")
        if not raw_record_ref or not _has_lineage(ingestion_lineage):
            return _excluded(
                candidate_ref,
                source_id,
                MISSING_INGESTION_LINEAGE,
                restriction_refs=restriction_refs,
            )

        original_value_ref = _optional_text(
            normalized.get("original_value_ref"),
            "normalized_records.original_value_ref",
        )
        canonical_value_ref = _optional_text(
            normalized.get("canonical_value_ref"),
            "normalized_records.canonical_value_ref",
        )
        normalization_rule_ref = _normalization_rule_ref(normalized)
        if not original_value_ref or not canonical_value_ref or not normalization_rule_ref:
            return _excluded(
                candidate_ref,
                source_id,
                MISSING_NORMALIZATION_TRACE,
                restriction_refs=restriction_refs,
            )

        quality = None
        if quality_record_id_ref:
            quality = quality_by_id.get(quality_record_id_ref)
        if quality is None:
            quality = quality_by_normalized_id.get(normalized_record_id)
        if quality is None:
            return _excluded(
                candidate_ref,
                source_id,
                MISSING_QUALITY_RECORD,
                restriction_refs=restriction_refs,
            )
        if _has_synthetic_marker(quality):
            return _excluded(
                candidate_ref,
                source_id,
                SYNTHETIC_INPUT_NOT_ALLOWED,
                restriction_refs=restriction_refs,
            )
        quality_record_id = _require_text(
            quality.get("quality_record_id"),
            "quality_records.quality_record_id",
        )
        quality_flags = _string_list(quality.get("quality_flags", []), "quality_flags")
        fitness_score = _optional_number(quality.get("fitness_score"), "fitness_score")
        disqualification_reason = _optional_text(
            quality.get("disqualification_reason"),
            "quality_records.disqualification_reason",
        )
        if disqualification_reason:
            return _excluded(
                candidate_ref,
                source_id,
                QUALITY_DISQUALIFIED,
                restriction_refs=restriction_refs,
            )

        identity = None
        if identity_record_id_ref:
            identity = identity_by_id.get(identity_record_id_ref)
        if identity is None:
            identity = identity_by_normalized_id.get(normalized_record_id)
        if identity is not None and _has_synthetic_marker(identity):
            return _excluded(
                candidate_ref,
                source_id,
                SYNTHETIC_INPUT_NOT_ALLOWED,
                restriction_refs=restriction_refs,
            )

        identity_record_id = None
        identity_ambiguity_flag = False
        if identity is not None:
            identity_record_id = _require_text(
                identity.get("identity_record_id"),
                "identity_records.identity_record_id",
            )
            ambiguity_value = identity.get("ambiguity_flag", False)
            if not isinstance(ambiguity_value, bool):
                raise ValidationDataBridgeError(
                    SCHEMA_VALIDATION_ERROR,
                    "identity ambiguity flag must be boolean",
                    field="identity_records.ambiguity_flag",
                    candidate_ref=candidate_ref,
                )
            identity_ambiguity_flag = ambiguity_value

        warning_codes: list[str] = []
        if identity_ambiguity_flag:
            warning_codes.append(IDENTITY_AMBIGUOUS_WARNING)
        if (
            minimum_fitness_score is not None
            and fitness_score is not None
            and fitness_score < minimum_fitness_score
        ):
            if low_fitness_policy == "exclude":
                return _excluded(
                    candidate_ref,
                    source_id,
                    LOW_FITNESS_SCORE,
                    restriction_refs=restriction_refs,
                )
            warning_codes.append(LOW_FITNESS_WARNING)
        if source_entry.get("warn_on_restrictions") and restriction_refs:
            warning_codes.append(RESTRICTED_RIGHTS_WARNING)

        return {
            "candidate_ref": candidate_ref,
            "source_id": source_id,
            "source_ref": source_entry["source_ref"],
            "rights_profile_id": rights_profile_id,
            "access_class": source_entry["access_class"],
            "restriction_refs": restriction_refs,
            "ingestion_record_id": ingestion_record_id,
            "raw_record_ref": raw_record_ref,
            "parsed_record_ref": _optional_text(
                ingestion.get("parsed_record_ref"),
                "ingestion_records.parsed_record_ref",
            ),
            "normalized_record_id": normalized_record_id,
            "original_value_ref": original_value_ref,
            "canonical_value_ref": canonical_value_ref,
            "normalization_rule_ref": normalization_rule_ref,
            "identity_record_id": identity_record_id,
            "identity_ambiguity_flag": identity_ambiguity_flag,
            "quality_record_id": quality_record_id,
            "fitness_score": fitness_score,
            "quality_flags": quality_flags,
            "disqualification_reason": None,
            "validation_status": (
                "eligible_with_warning" if warning_codes else "eligible"
            ),
            "warning_codes": sorted(set(warning_codes)),
            "exclusion_reason": None,
        }

    def _build_included_record(
        self,
        classification: Mapping[str, Any],
    ) -> tuple[BridgeRecord, list[EvidentiaryLink]]:
        record_hash_payload = {
            "source_id": classification["source_id"],
            "rights_profile_id": classification["rights_profile_id"],
            "access_class": classification["access_class"],
            "ingestion_record_id": classification["ingestion_record_id"],
            "raw_record_ref": classification["raw_record_ref"],
            "parsed_record_ref": classification["parsed_record_ref"],
            "normalized_record_id": classification["normalized_record_id"],
            "original_value_ref": classification["original_value_ref"],
            "canonical_value_ref": classification["canonical_value_ref"],
            "normalization_rule_ref": classification["normalization_rule_ref"],
            "identity_record_id": classification["identity_record_id"],
            "identity_ambiguity_flag": classification["identity_ambiguity_flag"],
            "quality_record_id": classification["quality_record_id"],
            "fitness_score": classification["fitness_score"],
            "quality_flags": classification["quality_flags"],
            "disqualification_reason": classification["disqualification_reason"],
            "validation_status": classification["validation_status"],
            "warning_codes": classification["warning_codes"],
            "exclusion_reason": classification["exclusion_reason"],
            "evidence_level": EVIDENCE_LEVEL,
            "restriction_refs": classification["restriction_refs"],
            "lineage_refs": _lineage_refs(classification),
            "source_ref": classification["source_ref"],
            "parent_id": self.parent_ids.get("bridge_record"),
            "produced_by_motor": MOTOR_ID,
        }
        record_hash = _stable_hash(record_hash_payload)
        record_id = (
            f"{MOTOR_ID}:bridge_record:"
            f"{classification['normalized_record_id']}:{_hash_prefix(record_hash)}"
        )
        record_links = self._build_links(record_id, classification)
        record = BridgeRecord(
            bridge_record_id=record_id,
            validation_data_set_id="",
            version_id=f"{MOTOR_ID}:v:bridge_record:{_hash_prefix(record_hash)}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=record_hash,
            source_id=classification["source_id"],
            rights_profile_id=classification["rights_profile_id"],
            access_class=classification["access_class"],
            ingestion_record_id=classification["ingestion_record_id"],
            raw_record_ref=classification["raw_record_ref"],
            parsed_record_ref=classification["parsed_record_ref"],
            normalized_record_id=classification["normalized_record_id"],
            original_value_ref=classification["original_value_ref"],
            canonical_value_ref=classification["canonical_value_ref"],
            normalization_rule_ref=classification["normalization_rule_ref"],
            identity_record_id=classification["identity_record_id"],
            identity_ambiguity_flag=classification["identity_ambiguity_flag"],
            quality_record_id=classification["quality_record_id"],
            fitness_score=classification["fitness_score"],
            quality_flags=list(classification["quality_flags"]),
            disqualification_reason=classification["disqualification_reason"],
            validation_status=classification["validation_status"],
            warning_codes=list(classification["warning_codes"]),
            exclusion_reason=classification["exclusion_reason"],
            evidence_level=EVIDENCE_LEVEL,
            evidentiary_link_ids=[link.evidentiary_link_id for link in record_links],
            restriction_refs=list(classification["restriction_refs"]),
            source_ref=classification["source_ref"],
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=self.parent_ids.get("bridge_record"),
        )
        return record, record_links

    def _build_links(
        self,
        bridge_record_id: str,
        classification: Mapping[str, Any],
    ) -> list[EvidentiaryLink]:
        link_specs = [
            (
                "motor_008",
                classification["rights_profile_id"],
                "source_rights",
                classification["restriction_refs"],
            ),
            (
                "motor_004",
                classification["ingestion_record_id"],
                "ingestion_lineage",
                [],
            ),
            (
                "motor_005",
                classification["normalized_record_id"],
                "normalization_trace",
                [],
            ),
            (
                "motor_007",
                classification["quality_record_id"],
                "quality_assessment",
                [],
            ),
        ]
        if classification["identity_record_id"]:
            link_specs.append(
                (
                    "motor_006",
                    classification["identity_record_id"],
                    "identity_resolution",
                    [],
                )
            )

        links = []
        for upstream_motor_id, upstream_ref, link_type, restrictions in link_specs:
            restriction_refs = sorted(set(restrictions))
            lineage_hash = _stable_hash(
                {
                    "upstream_motor_id": upstream_motor_id,
                    "upstream_artifact_ref": upstream_ref,
                    "link_type": link_type,
                    "restriction_refs": restriction_refs,
                }
            )
            link_hash = _stable_hash(
                {
                    "bridge_record_id": bridge_record_id,
                    "upstream_motor_id": upstream_motor_id,
                    "upstream_artifact_ref": upstream_ref,
                    "link_type": link_type,
                    "evidence_level": EVIDENCE_LEVEL,
                    "restriction_refs": restriction_refs,
                    "lineage_hash": lineage_hash,
                    "parent_id": self.parent_ids.get("evidentiary_link"),
                    "produced_by_motor": MOTOR_ID,
                }
            )
            links.append(
                EvidentiaryLink(
                    evidentiary_link_id=(
                        f"{MOTOR_ID}:evidentiary_link:"
                        f"{bridge_record_id}:{link_type}:{_hash_prefix(link_hash)}"
                    ),
                    bridge_record_id=bridge_record_id,
                    version_id=f"{MOTOR_ID}:v:evidentiary_link:{_hash_prefix(link_hash)}",
                    created_at=self.produced_at,
                    updated_at=self.produced_at,
                    version_hash=link_hash,
                    upstream_motor_id=upstream_motor_id,
                    upstream_artifact_ref=upstream_ref,
                    link_type=link_type,
                    evidence_level=EVIDENCE_LEVEL,
                    restriction_refs=restriction_refs,
                    lineage_hash=lineage_hash,
                    source_ref=str(upstream_ref),
                    produced_by_motor=MOTOR_ID,
                    produced_at=self.produced_at,
                    parent_id=self.parent_ids.get("evidentiary_link"),
                )
            )
        return links


def run_validation_data_bridge(**kwargs: Any) -> ValidationBridgeResult:
    """Convenience wrapper using the default deterministic bridge."""

    return ValidationDataBridge().run(**kwargs)


def _excluded(
    candidate_ref: str,
    source_id: str | None,
    reason: str,
    *,
    restriction_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    return {
        "candidate_ref": candidate_ref,
        "source_id": source_id,
        "exclusion_reason": reason,
        "restriction_refs": sorted(set(restriction_refs or [])),
    }


def _assert_output_consistency(result: ValidationBridgeResult) -> None:
    dataset = result.validation_data_set
    manifest = result.bridge_manifest
    evidentiary_record = result.evidentiary_record
    if dataset.evidence_level != EVIDENCE_LEVEL:
        raise ValidationDataBridgeError(
            EVIDENCE_LEVEL_INVALID,
            "ValidationDataSet evidence_level must be validation_data",
        )
    if evidentiary_record.evidence_level != EVIDENCE_LEVEL:
        raise ValidationDataBridgeError(
            EVIDENCE_LEVEL_INVALID,
            "EvidentiaryRecord evidence_level must be validation_data",
        )
    if dataset.bridge_record_ids != manifest.included_record_ids:
        raise ValidationDataBridgeError(
            MANIFEST_MISMATCH,
            "ValidationDataSet.bridge_record_ids and BridgeManifest.included_record_ids differ",
        )
    if set(manifest.excluded_record_refs) != set(manifest.exclusion_reasons):
        raise ValidationDataBridgeError(
            MANIFEST_MISMATCH,
            "every excluded record ref must have one explicit exclusion reason",
        )
    link_ids = {link.evidentiary_link_id for link in result.evidentiary_links}
    links_by_record: dict[str, set[str]] = {}
    for link in result.evidentiary_links:
        if link.evidence_level != EVIDENCE_LEVEL:
            raise ValidationDataBridgeError(
                EVIDENCE_LEVEL_INVALID,
                "EvidentiaryLink evidence_level must be validation_data",
            )
        links_by_record.setdefault(link.bridge_record_id, set()).add(link.link_type)
    for record in result.bridge_records:
        if record.evidence_level != EVIDENCE_LEVEL:
            raise ValidationDataBridgeError(
                EVIDENCE_LEVEL_INVALID,
                "BridgeRecord evidence_level must be validation_data",
            )
        required_fields = {
            "source_id": record.source_id,
            "rights_profile_id": record.rights_profile_id,
            "ingestion_record_id": record.ingestion_record_id,
            "raw_record_ref": record.raw_record_ref,
            "normalized_record_id": record.normalized_record_id,
            "original_value_ref": record.original_value_ref,
            "canonical_value_ref": record.canonical_value_ref,
            "normalization_rule_ref": record.normalization_rule_ref,
            "quality_record_id": record.quality_record_id,
        }
        missing = [name for name, value in required_fields.items() if not value]
        if missing:
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "BridgeRecord is missing required lineage fields",
                field=",".join(missing),
                candidate_ref=record.normalized_record_id,
            )
        if not set(record.evidentiary_link_ids).issubset(link_ids):
            raise ValidationDataBridgeError(
                MANIFEST_MISMATCH,
                "BridgeRecord references a missing EvidentiaryLink",
                candidate_ref=record.normalized_record_id,
            )
        expected_links = {
            "source_rights",
            "ingestion_lineage",
            "normalization_trace",
            "quality_assessment",
        }
        if record.identity_record_id:
            expected_links.add("identity_resolution")
        if not expected_links.issubset(links_by_record.get(record.bridge_record_id, set())):
            raise ValidationDataBridgeError(
                MANIFEST_MISMATCH,
                "BridgeRecord does not have all required evidentiary link types",
                candidate_ref=record.normalized_record_id,
            )
    if evidentiary_record.bridge_manifest_id != manifest.bridge_manifest_id:
        raise ValidationDataBridgeError(
            MANIFEST_MISMATCH,
            "EvidentiaryRecord.bridge_manifest_id must reference BridgeManifest",
        )


def _source_registry_index(registry: Mapping[str, Any]) -> dict[str, Any]:
    snapshot_id = (
        _optional_text(registry.get("snapshot_id"), "source_registry.snapshot_id")
        or _optional_text(
            registry.get("source_registry_snapshot_id"),
            "source_registry.source_registry_snapshot_id",
        )
        or _optional_text(registry.get("id"), "source_registry.id")
    )
    if not snapshot_id:
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "source registry snapshot id is required",
            field="source_registry.snapshot_id",
        )
    rights_profiles = _rights_profiles(registry)
    raw_sources = _source_entries(registry)
    sources: dict[str, dict[str, Any]] = {}
    for raw_source in raw_sources:
        source_id = (
            _optional_text(raw_source.get("source_id"), "source_id")
            or _optional_text(raw_source.get("id"), "source.id")
        )
        if not source_id:
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "source entry missing source_id",
                field="source_registry.sources.source_id",
            )
        rights_profile = _as_mapping_or_none(raw_source.get("rights_profile"))
        rights_profile_id = (
            _optional_text(raw_source.get("rights_profile_id"), "rights_profile_id")
            or (
                _optional_text(rights_profile.get("rights_profile_id"), "rights_profile_id")
                if rights_profile
                else None
            )
            or (
                _optional_text(rights_profile.get("id"), "rights_profile.id")
                if rights_profile
                else None
            )
        )
        if rights_profile_id and rights_profile_id in rights_profiles:
            rights_profile = {
                **rights_profiles[rights_profile_id],
                **(rights_profile or {}),
            }
        validation_use = _allows_validation(raw_source, rights_profile)
        restriction_refs = sorted(
            set(_restriction_refs(raw_source) + _restriction_refs(rights_profile or {}))
        )
        access_class = (
            _optional_text(raw_source.get("access_class"), "access_class")
            or (
                _optional_text(rights_profile.get("access_class"), "access_class")
                if rights_profile
                else None
            )
            or "unspecified"
        )
        source_ref = (
            _optional_text(raw_source.get("source_ref"), "source_ref")
            or f"source_registry:{snapshot_id}:{source_id}"
        )
        sources[source_id] = {
            "source_id": source_id,
            "rights_profile_id": rights_profile_id,
            "validation_use": validation_use,
            "access_class": access_class,
            "restriction_refs": restriction_refs,
            "source_ref": source_ref,
            "allowed_destination_policies": _lenient_string_list(
                raw_source.get("allowed_destination_policies")
                or (rights_profile or {}).get("allowed_destination_policies")
            ),
            "denied_destination_policies": _lenient_string_list(
                raw_source.get("denied_destination_policies")
                or (rights_profile or {}).get("denied_destination_policies")
            ),
            "warn_on_restrictions": bool(
                raw_source.get("warn_on_restrictions")
                or (rights_profile or {}).get("warn_on_restrictions")
            ),
            "raw": raw_source,
        }
    return {"snapshot_id": snapshot_id, "sources": sources}


def _source_entries(registry: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    containers = [
        registry.get("sources"),
        registry.get("source_registration"),
        registry.get("source_registrations"),
        registry.get("registered_sources"),
        registry.get("entries"),
    ]
    for container in containers:
        entries = _mapping_values_or_sequence(container)
        if entries:
            return entries
    if _optional_text(registry.get("source_id"), "source_registry.source_id"):
        return [registry]
    discovered = [
        value
        for value in registry.values()
        if isinstance(value, Mapping)
        and (
            _optional_text(value.get("source_id"), "source_id")
            or _optional_text(value.get("id"), "source.id")
        )
    ]
    if discovered:
        return discovered
    raise ValidationDataBridgeError(
        SCHEMA_VALIDATION_ERROR,
        "source registry must contain at least one source entry",
        field="source_registry.sources",
    )


def _rights_profiles(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    profiles: dict[str, Mapping[str, Any]] = {}
    for candidate in [
        registry.get("rights_profiles"),
        registry.get("rights_profile_registry"),
        registry.get("rights_profile"),
    ]:
        for profile in _mapping_values_or_sequence(candidate):
            profile_id = (
                _optional_text(profile.get("rights_profile_id"), "rights_profile_id")
                or _optional_text(profile.get("id"), "rights_profile.id")
            )
            if profile_id:
                profiles[profile_id] = profile
    return profiles


def _mapping_values_or_sequence(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        if any(
            key in value
            for key in (
                "source_id",
                "rights_profile_id",
                "validation_use",
                "allowed_uses",
            )
        ):
            return [value]
        entries = list(value.values())
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        entries = list(value)
    else:
        return []
    output = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "registry containers must contain mappings",
                field="source_registry",
            )
        output.append(entry)
    return output


def _allows_validation(
    source_entry: Mapping[str, Any],
    rights_profile: Mapping[str, Any] | None,
) -> bool:
    candidates = [
        source_entry.get("validation_use"),
        source_entry.get("allows_validation"),
        (rights_profile or {}).get("validation_use"),
        (rights_profile or {}).get("allows_validation"),
    ]
    for value in candidates:
        if value is not None:
            return _truthy(value)
    allowed_uses = _lenient_string_list(source_entry.get("allowed_uses")) + _lenient_string_list(
        (rights_profile or {}).get("allowed_uses")
    )
    return any(use.lower() in {"validation", "internal_validation"} for use in allowed_uses)


def _destination_conflicts(
    destination_policy_ref: str | None,
    source_entry: Mapping[str, Any],
) -> bool:
    if not destination_policy_ref:
        return False
    destination = destination_policy_ref.lower()
    denied = [policy.lower() for policy in source_entry.get("denied_destination_policies", [])]
    if any(policy and (policy == destination or policy in destination) for policy in denied):
        return True
    allowed = [policy.lower() for policy in source_entry.get("allowed_destination_policies", [])]
    if allowed and destination not in allowed:
        return True
    restrictions = " ".join(source_entry.get("restriction_refs", [])).lower()
    redistribution_terms = ("redistribution", "external", "public", "export")
    internal_only_terms = ("no-redistribution", "internal-only", "internal_validation", "access:internal")
    return any(term in destination for term in redistribution_terms) and any(
        term in restrictions for term in internal_only_terms
    )


def _restriction_refs(record: Mapping[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in (
        "restriction_refs",
        "restrictions",
        "license_refs",
        "license_restrictions",
        "access_restrictions",
        "redistribution_restrictions",
    ):
        refs.extend(_lenient_string_list(record.get(key)))
    return refs


def _normalization_rule_ref(normalized: Mapping[str, Any]) -> str | None:
    direct = (
        _optional_text(normalized.get("normalization_rule_ref"), "normalization_rule_ref")
        or _optional_text(normalized.get("normalization_rule_id"), "normalization_rule_id")
    )
    if direct:
        return direct
    rule_log = normalized.get("normalization_rule_log")
    if isinstance(rule_log, Sequence) and not isinstance(rule_log, (str, bytes, bytearray)):
        for item in rule_log:
            text = _optional_text(item, "normalization_rule_log")
            if text:
                return text
    return None


def _lineage_refs(classification: Mapping[str, Any]) -> list[str]:
    refs = [
        classification["rights_profile_id"],
        classification["ingestion_record_id"],
        classification["normalized_record_id"],
        classification["quality_record_id"],
    ]
    if classification["identity_record_id"]:
        refs.append(classification["identity_record_id"])
    return refs


def _rebuild_inputs(
    *,
    source_registry_snapshot_id: str,
    ingestion_records: Sequence[Mapping[str, Any]],
    normalized_records: Sequence[Mapping[str, Any]],
    identity_records: Sequence[Mapping[str, Any]],
    quality_records: Sequence[Mapping[str, Any]],
) -> dict[str, list[str]]:
    return {
        "source_registry": [source_registry_snapshot_id],
        "ingestion_records": _sorted_record_ids(ingestion_records, "ingestion_record_id"),
        "normalized_records": _sorted_record_ids(normalized_records, "normalized_record_id"),
        "identity_records": _sorted_record_ids(identity_records, "identity_record_id"),
        "quality_records": _sorted_record_ids(quality_records, "quality_record_id"),
    }


def _sorted_record_ids(records: Sequence[Mapping[str, Any]], field: str) -> list[str]:
    ids = []
    for record in records:
        value = _optional_text(record.get(field), field)
        if value:
            ids.append(value)
    return sorted(set(ids))


def _warning_summary(warning_reasons: Mapping[str, Sequence[str]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for warnings in warning_reasons.values():
        counter.update(warnings)
    return dict(sorted(counter.items()))


def _index_by_required_id(
    records: Sequence[Mapping[str, Any]],
    id_field: str,
    collection_name: str,
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = _require_text(record.get(id_field), f"{collection_name}.{id_field}")
        if record_id in indexed:
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "duplicate upstream record id",
                field=f"{collection_name}.{id_field}",
                candidate_ref=record_id,
            )
        indexed[record_id] = record
    return indexed


def _index_by_optional_unique_id(
    records: Sequence[Mapping[str, Any]],
    id_field: str,
    field_name: str,
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = _optional_text(record.get(id_field), field_name)
        if not record_id:
            continue
        if record_id in indexed:
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "duplicate upstream relationship id",
                field=field_name,
                candidate_ref=record_id,
            )
        indexed[record_id] = record
    return indexed


def _record_list(value: Any, field: str) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "input must be a list of records",
            field=field,
        )
    output = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValidationDataBridgeError(
                SCHEMA_VALIDATION_ERROR,
                "each input record must be a mapping",
                field=f"{field}[{index}]",
            )
        output.append(item)
    return output


def _as_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "input must be a mapping",
            field=field,
        )
    return value


def _as_mapping_or_none(value: Any) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    raise ValidationDataBridgeError(
        SCHEMA_VALIDATION_ERROR,
        "rights profile must be a mapping when provided",
        field="rights_profile",
    )


def _require_text(value: Any, field: str) -> str:
    text = _optional_text(value, field)
    if not text:
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "required text field is missing",
            field=field,
        )
    return text


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return str(value)
    raise ValidationDataBridgeError(
        SCHEMA_VALIDATION_ERROR,
        "field must be text",
        field=field,
    )


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "field must be a list of strings",
            field=field,
        )
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "field must be a list of strings",
            field=field,
        )
    output = []
    for index, item in enumerate(value):
        text = _optional_text(item, f"{field}[{index}]")
        if text:
            output.append(text)
    return output


def _lenient_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        text = _optional_text(value, "string_list")
        return [text] if text else []
    output = []
    for item in value:
        text = _optional_text(item, "string_list")
        if text:
            output.append(text)
    return output


def _optional_number(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValidationDataBridgeError(
            SCHEMA_VALIDATION_ERROR,
            "field must be numeric",
            field=field,
        )
    return float(value)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "allowed", "permit", "permitted"}
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return bool(value)
    return False


def _has_lineage(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return any(_optional_text(item, "ingestion_lineage") for item in value)
    return False


def _has_synthetic_marker(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"synthetic_data_flag", "synthetic_support_flag"} and _truthy(item):
                return True
            if lowered == "source_type" and str(item).strip().lower() == "synthetic":
                return True
            if lowered == "evidence_level" and str(item).strip().lower() == "synthetic_support":
                return True
            if lowered in {"synthetic_generation_run", "capability_demonstration_report"}:
                return True
            if _has_synthetic_marker(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_synthetic_marker(item) for item in value)
    return False


def _sort_key(record: Mapping[str, Any], field: str) -> str:
    return _optional_text(record.get(field), field) or ""


def _stable_hash(value: Any) -> str:
    payload = json.dumps(
        _canonical(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical(value: Any) -> Any:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    return value


def _hash_prefix(version_hash: str, length: int = 16) -> str:
    return version_hash.replace("sha256:", "")[:length]
