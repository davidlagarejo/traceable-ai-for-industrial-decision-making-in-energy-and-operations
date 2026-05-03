"""Deterministic entity identity resolution for motor_006."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .errors import IdentityResolutionError
from .models import (
    AmbiguityFlag,
    CandidateMatch,
    EntityCluster,
    IdentityRecord,
    ResolutionConflict,
)


MOTOR_ID = "motor_006"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
DEFAULT_ALIAS_FIELDS = (
    "legal_name",
    "full_name",
    "normalized_name",
    "name",
    "display_name",
)
DEFAULT_IDENTIFIER_FIELDS = (
    "org_tax_id",
    "national_researcher_id",
    "person_id",
    "organization_id",
    "institution_id",
    "external_id",
    "registry_id",
)


@dataclass(frozen=True)
class _Comparison:
    match_features: Dict[str, Any]
    match_result: str
    evidence_refs: List[str]
    score: int
    conflict_type: Optional[str] = None

    @property
    def has_evidence(self) -> bool:
        return bool(
            self.match_features["alias_overlap"]
            or self.match_features["matching_identifiers"]
            or self.match_features["conflicting_identifiers"]
        )


class EntityIdentityResolutionEngine:
    """Resolve normalized records against canonical entities without mutating inputs."""

    def resolve(
        self,
        normalized_records: Sequence[Mapping[str, Any]],
        canonical_entities: Sequence[Mapping[str, Any]],
        resolution_policy: Mapping[str, Any],
        previous_identity_records: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        normalized_snapshot = deepcopy(normalized_records)
        canonical_snapshot = deepcopy(canonical_entities)

        previous_identity_records = previous_identity_records or []
        self._validate_inputs(
            normalized_records,
            canonical_entities,
            resolution_policy,
            previous_identity_records,
        )

        rule_version = str(resolution_policy["rule_version"]).strip()
        produced_at = str(resolution_policy.get("produced_at") or DEFAULT_PRODUCED_AT)

        candidate_matches: List[CandidateMatch] = []
        conflicts: List[ResolutionConflict] = []
        identity_records: List[IdentityRecord] = []
        clusters: List[EntityCluster] = []
        ambiguity_flags: List[AmbiguityFlag] = []

        records_by_id = {str(record["record_id"]): record for record in normalized_records}
        canonical_by_id = {
            str(entity["canonical_entity_id"]): entity for entity in canonical_entities
        }
        matches_by_record: Dict[str, List[Tuple[CandidateMatch, Mapping[str, Any], int]]] = {
            str(record["record_id"]): [] for record in normalized_records
        }
        non_pass_matches_by_record: Dict[str, List[CandidateMatch]] = {
            str(record["record_id"]): [] for record in normalized_records
        }
        conflict_ids_by_record: Dict[str, List[str]] = {
            str(record["record_id"]): [] for record in normalized_records
        }

        for collision_records, field_name, field_values in self._record_identifier_collisions(
            normalized_records,
            resolution_policy,
        ):
            match_ids: List[str] = []
            candidate_ref = self._stable_id(
                "entity_cluster_candidate",
                {
                    "record_ids": self._record_ids(collision_records),
                    "field_name": field_name,
                    "field_values": sorted(field_values),
                    "rule_version": rule_version,
                },
            )
            for record in collision_records:
                features = {
                    "taxonomy_compatible": True,
                    "alias_overlap": self._record_aliases(record, resolution_policy),
                    "matching_identifiers": {},
                    "conflicting_identifiers": {
                        field_name: self._normalize_scalar(
                            self._record_identifiers(record, resolution_policy).get(field_name)
                        )
                    },
                    "score": 0,
                }
                evidence_refs = [
                    f"normalized_record:{record['record_id']}:identifier:{field_name}"
                ]
                match = self._make_candidate_match(
                    record,
                    candidate_ref,
                    "entity_cluster",
                    features,
                    "fail",
                    evidence_refs,
                    rule_version,
                    produced_at,
                )
                candidate_matches.append(match)
                match_ids.append(match.candidate_match_id)

            conflict = self._make_conflict(
                collision_records,
                match_ids,
                "identifier_collision",
                f"Records share an entity alias but disagree on strong identifier {field_name}.",
                "split_cluster",
                rule_version,
                produced_at,
            )
            conflicts.append(conflict)
            for record in collision_records:
                conflict_ids_by_record[str(record["record_id"])].append(conflict.conflict_id)

            identity = self._make_identity_record(
                collision_records,
                "distinct_entity",
                "medium",
                match_ids,
                rule_version,
                produced_at,
                previous_identity_records,
                None,
                [conflict.conflict_id],
            )
            identity_records.append(identity)

        for record in normalized_records:
            record_id = str(record["record_id"])
            for canonical_entity in canonical_entities:
                comparison = self._compare_record_to_canonical(
                    record,
                    canonical_entity,
                    resolution_policy,
                )
                if not comparison.has_evidence:
                    continue

                match = self._make_candidate_match(
                    record,
                    str(canonical_entity["canonical_entity_id"]),
                    "canonical_entity",
                    comparison.match_features,
                    comparison.match_result,
                    comparison.evidence_refs,
                    rule_version,
                    produced_at,
                )
                candidate_matches.append(match)

                if comparison.match_result == "pass":
                    matches_by_record[record_id].append(
                        (match, canonical_entity, comparison.score)
                    )
                else:
                    non_pass_matches_by_record[record_id].append(match)

                if comparison.conflict_type is not None:
                    conflict = self._make_conflict(
                        [record],
                        [match.candidate_match_id],
                        comparison.conflict_type,
                        self._blocking_reason(comparison.conflict_type),
                        self._next_step(comparison.conflict_type),
                        rule_version,
                        produced_at,
                    )
                    conflicts.append(conflict)
                    conflict_ids_by_record[record_id].append(conflict.conflict_id)

        canonical_assignments: Dict[str, List[Tuple[Mapping[str, Any], CandidateMatch, int]]] = {}
        records_with_closed_collision = {
            record_id
            for identity in identity_records
            if identity.decision == "distinct_entity"
            for record_id in identity.evaluated_record_ids
        }

        for record in normalized_records:
            record_id = str(record["record_id"])
            pass_matches = sorted(
                matches_by_record[record_id],
                key=lambda item: (-item[2], str(item[1]["canonical_entity_id"])),
            )
            if pass_matches:
                top_score = pass_matches[0][2]
                top_matches = [item for item in pass_matches if item[2] == top_score]
                if len(top_matches) > 1 and resolution_policy.get("tie_breaker") != "canonical_id":
                    match_ids = [item[0].candidate_match_id for item in top_matches]
                    conflict = self._make_conflict(
                        [record],
                        match_ids,
                        "evidence_tie",
                        "Two or more canonical candidates have equal deterministic evidence.",
                        "keep_ambiguous",
                        rule_version,
                        produced_at,
                    )
                    conflicts.append(conflict)
                    conflict_ids_by_record[record_id].append(conflict.conflict_id)
                    identity, flag = self._make_ambiguous_identity_and_flag(
                        [record],
                        "candidate_tie",
                        "blocking",
                        match_ids,
                        rule_version,
                        produced_at,
                        previous_identity_records,
                        [conflict.conflict_id],
                    )
                    identity_records.append(identity)
                    ambiguity_flags.append(flag)
                    clusters.append(
                        self._make_cluster(
                            None,
                            [record],
                            "ambiguous",
                            [identity.identity_record_id],
                            produced_at,
                        )
                    )
                    continue

                selected_match, selected_entity, selected_score = top_matches[0]
                canonical_id = str(selected_entity["canonical_entity_id"])
                canonical_assignments.setdefault(canonical_id, []).append(
                    (record, selected_match, selected_score)
                )
                continue

            if conflict_ids_by_record[record_id]:
                evidence_refs = [
                    match.candidate_match_id
                    for match in non_pass_matches_by_record[record_id]
                ]
                identity = self._make_identity_record(
                    [record],
                    "distinct_entity",
                    "medium",
                    evidence_refs,
                    rule_version,
                    produced_at,
                    previous_identity_records,
                    None,
                    conflict_ids_by_record[record_id],
                )
                identity_records.append(identity)
                continue

            ambiguity_reason = (
                "insufficient_evidence"
                if non_pass_matches_by_record[record_id]
                else "missing_canonical_reference"
            )
            evidence_refs = [
                match.candidate_match_id for match in non_pass_matches_by_record[record_id]
            ]
            if not evidence_refs:
                evidence_refs = [f"normalized_record:{record_id}:no_compatible_candidate"]
            identity, flag = self._make_ambiguous_identity_and_flag(
                [record],
                ambiguity_reason,
                "blocking",
                evidence_refs,
                rule_version,
                produced_at,
                previous_identity_records,
                [],
            )
            identity_records.append(identity)
            ambiguity_flags.append(flag)
            clusters.append(
                self._make_cluster(
                    None,
                    [record],
                    "ambiguous",
                    [identity.identity_record_id],
                    produced_at,
                )
            )

        for canonical_id, assigned_items in sorted(canonical_assignments.items()):
            canonical_entity = canonical_by_id[canonical_id]
            grouped_items = self._split_confirmed_group_if_identifier_collision(
                assigned_items,
                resolution_policy,
            )
            for group_items in grouped_items:
                group_records = [item[0] for item in group_items]
                evidence_refs = [item[1].candidate_match_id for item in group_items]
                confidence_band = self._confidence_band(
                    max(item[2] for item in group_items),
                    resolution_policy,
                )
                if len(group_records) > 1 and any(
                    str(record["record_id"]) in records_with_closed_collision
                    for record in group_records
                ):
                    confidence_band = "medium"
                identity = self._make_identity_record(
                    group_records,
                    "same_entity",
                    confidence_band,
                    evidence_refs,
                    rule_version,
                    produced_at,
                    previous_identity_records,
                    None,
                    [],
                    [canonical_entity],
                )
                identity_records.append(identity)
                clusters.append(
                    self._make_cluster(
                        canonical_id,
                        group_records,
                        "confirmed",
                        [identity.identity_record_id],
                        produced_at,
                        [canonical_entity],
                    )
                )

        if normalized_records != normalized_snapshot or canonical_entities != canonical_snapshot:
            raise IdentityResolutionError(
                "ERR_SILENT_INPUT_MUTATION",
                "Input objects changed during identity resolution.",
            )

        return {
            "identity_resolution_record": [
                item.to_dict()
                for item in self._sort_by_id(identity_records, "identity_record_id")
            ],
            "entity_cluster": [
                item.to_dict() for item in self._sort_by_id(clusters, "entity_cluster_id")
            ],
            "ambiguity_flag": [
                item.to_dict()
                for item in self._sort_by_id(ambiguity_flags, "ambiguity_flag_id")
            ],
            "resolution_conflict": [
                item.to_dict() for item in self._sort_by_id(conflicts, "conflict_id")
            ],
            "candidate_match": [
                item.to_dict()
                for item in self._sort_by_id(candidate_matches, "candidate_match_id")
            ],
        }

    def _validate_inputs(
        self,
        normalized_records: Sequence[Mapping[str, Any]],
        canonical_entities: Sequence[Mapping[str, Any]],
        resolution_policy: Mapping[str, Any],
        previous_identity_records: Sequence[Mapping[str, Any]],
    ) -> None:
        if not isinstance(normalized_records, list):
            raise IdentityResolutionError(
                "ERR_INPUT_TYPE_INVALID",
                "normalized_records must be an array.",
                {"field": "normalized_records"},
            )
        if not isinstance(canonical_entities, list):
            raise IdentityResolutionError(
                "ERR_INPUT_TYPE_INVALID",
                "canonical_entities must be an array.",
                {"field": "canonical_entities"},
            )
        if not isinstance(resolution_policy, Mapping):
            raise IdentityResolutionError(
                "ERR_INPUT_TYPE_INVALID",
                "resolution_policy must be an object.",
                {"field": "resolution_policy"},
            )
        if not isinstance(previous_identity_records, list):
            raise IdentityResolutionError(
                "ERR_INPUT_TYPE_INVALID",
                "previous_identity_records must be an array when provided.",
                {"field": "previous_identity_records"},
            )
        if not str(resolution_policy.get("rule_version") or "").strip():
            raise IdentityResolutionError(
                "ERR_POLICY_VERSION_MISSING",
                "resolution_policy.rule_version is required.",
                {"field": "resolution_policy.rule_version"},
            )

        seen_record_ids: Set[str] = set()
        for index, record in enumerate(normalized_records):
            if not isinstance(record, Mapping):
                raise IdentityResolutionError(
                    "ERR_NORMALIZED_RECORD_INVALID",
                    "Each normalized record must be an object.",
                    {"index": index},
                )
            record_id = str(record.get("record_id") or "").strip()
            if not record_id:
                raise IdentityResolutionError(
                    "ERR_NORMALIZED_RECORD_INVALID",
                    "record_id is required on every normalized record.",
                    {"index": index},
                )
            if record_id in seen_record_ids:
                raise IdentityResolutionError(
                    "ERR_NORMALIZED_RECORD_INVALID",
                    "record_id values must be unique inside a batch.",
                    {"record_id": record_id},
                )
            seen_record_ids.add(record_id)
            if not str(record.get("source_ref") or "").strip():
                raise IdentityResolutionError(
                    "ERR_MISSING_PROVENANCE",
                    "source_ref is required on every normalized record.",
                    {"record_id": record_id},
                )
            if not str(record.get("provenance_ref") or "").strip():
                raise IdentityResolutionError(
                    "ERR_MISSING_PROVENANCE",
                    "provenance_ref is required on every normalized record.",
                    {"record_id": record_id},
                )
            lineage_refs = record.get("lineage_refs")
            if not isinstance(lineage_refs, list) or not lineage_refs:
                raise IdentityResolutionError(
                    "ERR_MISSING_PROVENANCE",
                    "lineage_refs must be a non-empty array.",
                    {"record_id": record_id},
                )
            if "normalized_fields" not in record and "raw_fields" in record:
                raise IdentityResolutionError(
                    "ERR_UNNORMALIZED_INPUT",
                    "raw_fields cannot replace normalized_fields.",
                    {"record_id": record_id},
                )
            if not isinstance(record.get("normalized_fields"), Mapping):
                raise IdentityResolutionError(
                    "ERR_UNNORMALIZED_INPUT",
                    "normalized_fields must be an object.",
                    {"record_id": record_id},
                )
            if not str(record.get("entity_type") or "").strip():
                raise IdentityResolutionError(
                    "ERR_NORMALIZED_RECORD_INVALID",
                    "entity_type is required on every normalized record.",
                    {"record_id": record_id},
                )

        seen_canonical_ids: Set[str] = set()
        for index, entity in enumerate(canonical_entities):
            if not isinstance(entity, Mapping):
                raise IdentityResolutionError(
                    "ERR_CANONICAL_ENTITY_INVALID",
                    "Each canonical entity must be an object.",
                    {"index": index},
                )
            canonical_id = str(entity.get("canonical_entity_id") or "").strip()
            if not canonical_id:
                raise IdentityResolutionError(
                    "ERR_CANONICAL_ENTITY_INVALID",
                    "canonical_entity_id is required.",
                    {"index": index},
                )
            if canonical_id in seen_canonical_ids:
                raise IdentityResolutionError(
                    "ERR_CANONICAL_ENTITY_INVALID",
                    "canonical_entity_id values must be unique inside a batch.",
                    {"canonical_entity_id": canonical_id},
                )
            seen_canonical_ids.add(canonical_id)
            if not str(entity.get("entity_type") or "").strip():
                raise IdentityResolutionError(
                    "ERR_CANONICAL_ENTITY_INVALID",
                    "entity_type is required on every canonical entity.",
                    {"canonical_entity_id": canonical_id},
                )
            if not str(entity.get("taxonomy_version_id") or "").strip():
                raise IdentityResolutionError(
                    "ERR_CANONICAL_ENTITY_INVALID",
                    "taxonomy_version_id is required on every canonical entity.",
                    {"canonical_entity_id": canonical_id},
                )
            if "external_identifiers" in entity and not isinstance(
                entity["external_identifiers"], Mapping
            ):
                raise IdentityResolutionError(
                    "ERR_CANONICAL_ENTITY_INVALID",
                    "external_identifiers must be an object when present.",
                    {"canonical_entity_id": canonical_id},
                )

    def _compare_record_to_canonical(
        self,
        record: Mapping[str, Any],
        canonical_entity: Mapping[str, Any],
        policy: Mapping[str, Any],
    ) -> _Comparison:
        record_id = str(record["record_id"])
        canonical_id = str(canonical_entity["canonical_entity_id"])
        record_type = self._normalize_scalar(record.get("entity_type"))
        canonical_type = self._normalize_scalar(canonical_entity.get("entity_type"))
        taxonomy_compatible = record_type == canonical_type

        record_aliases = set(self._record_aliases(record, policy))
        canonical_aliases = set(self._canonical_aliases(canonical_entity, policy))
        alias_overlap = sorted(record_aliases & canonical_aliases)

        record_identifiers = self._record_identifiers(record, policy)
        canonical_identifiers = self._canonical_identifiers(canonical_entity, policy)
        matching_identifiers: Dict[str, str] = {}
        conflicting_identifiers: Dict[str, Dict[str, str]] = {}
        for field_name in sorted(set(record_identifiers) & set(canonical_identifiers)):
            record_value = self._normalize_scalar(record_identifiers[field_name])
            canonical_value = self._normalize_scalar(canonical_identifiers[field_name])
            if record_value == canonical_value:
                matching_identifiers[field_name] = record_value
            else:
                conflicting_identifiers[field_name] = {
                    "record": record_value,
                    "canonical": canonical_value,
                }

        weights = policy.get("weights") if isinstance(policy.get("weights"), Mapping) else {}
        alias_weight = int(weights.get("alias", 1))
        identifier_weight = int(weights.get("identifier", 2))
        score = min(len(alias_overlap), 1) * alias_weight
        score += len(matching_identifiers) * identifier_weight

        evidence_refs = []
        for alias in alias_overlap:
            evidence_refs.append(f"normalized_record:{record_id}:alias:{alias}")
            evidence_refs.append(f"canonical_entity:{canonical_id}:alias:{alias}")
        for field_name in sorted(matching_identifiers):
            evidence_refs.append(f"normalized_record:{record_id}:identifier:{field_name}")
            evidence_refs.append(f"canonical_entity:{canonical_id}:identifier:{field_name}")
        for field_name in sorted(conflicting_identifiers):
            evidence_refs.append(f"normalized_record:{record_id}:identifier:{field_name}")
            evidence_refs.append(f"canonical_entity:{canonical_id}:identifier:{field_name}")

        features = {
            "taxonomy_compatible": taxonomy_compatible,
            "alias_overlap": alias_overlap,
            "matching_identifiers": matching_identifiers,
            "conflicting_identifiers": conflicting_identifiers,
            "score": score,
        }

        if not taxonomy_compatible:
            return _Comparison(features, "fail", evidence_refs, score, "taxonomy_mismatch")
        if conflicting_identifiers:
            return _Comparison(features, "fail", evidence_refs, score, "identifier_collision")
        if score >= int(policy.get("match_threshold", 2)):
            return _Comparison(features, "pass", evidence_refs, score)
        if evidence_refs:
            return _Comparison(features, "insufficient", evidence_refs, score)
        return _Comparison(features, "insufficient", [], score)

    def _record_identifier_collisions(
        self,
        normalized_records: Sequence[Mapping[str, Any]],
        policy: Mapping[str, Any],
    ) -> List[Tuple[List[Mapping[str, Any]], str, Set[str]]]:
        collisions: List[Tuple[List[Mapping[str, Any]], str, Set[str]]] = []
        groups: Dict[Tuple[str, str], List[Mapping[str, Any]]] = {}
        for record in normalized_records:
            aliases = self._record_aliases(record, policy)
            if not aliases:
                continue
            key = (self._normalize_scalar(record["entity_type"]), aliases[0])
            groups.setdefault(key, []).append(record)

        for group_records in groups.values():
            if len(group_records) < 2:
                continue
            fields = sorted(
                {
                    field_name
                    for record in group_records
                    for field_name in self._record_identifiers(record, policy)
                }
            )
            for field_name in fields:
                values = {
                    self._normalize_scalar(
                        self._record_identifiers(record, policy).get(field_name)
                    )
                    for record in group_records
                    if field_name in self._record_identifiers(record, policy)
                }
                if len(values) > 1:
                    collisions.append((list(group_records), field_name, values))
        return collisions

    def _split_confirmed_group_if_identifier_collision(
        self,
        assigned_items: List[Tuple[Mapping[str, Any], CandidateMatch, int]],
        policy: Mapping[str, Any],
    ) -> List[List[Tuple[Mapping[str, Any], CandidateMatch, int]]]:
        if len(assigned_items) < 2:
            return [assigned_items]
        records = [item[0] for item in assigned_items]
        for group_records, _, _ in self._record_identifier_collisions(records, policy):
            collision_ids = {str(record["record_id"]) for record in group_records}
            split: List[List[Tuple[Mapping[str, Any], CandidateMatch, int]]] = []
            for item in assigned_items:
                if str(item[0]["record_id"]) in collision_ids:
                    split.append([item])
            remaining = [
                item
                for item in assigned_items
                if str(item[0]["record_id"]) not in collision_ids
            ]
            if remaining:
                split.append(remaining)
            return split
        return [assigned_items]

    def _make_candidate_match(
        self,
        record: Mapping[str, Any],
        candidate_ref: str,
        candidate_type: str,
        match_features: Dict[str, Any],
        match_result: str,
        evidence_refs: List[str],
        rule_version: str,
        produced_at: str,
    ) -> CandidateMatch:
        base = {
            "record_id": str(record["record_id"]),
            "candidate_ref": candidate_ref,
            "candidate_type": candidate_type,
            "match_features": self._canonical_jsonable(match_features),
            "match_result": match_result,
            "rule_version": rule_version,
            "evidence_refs": sorted(set(evidence_refs)),
        }
        candidate_match_id = self._stable_id("candidate_match", base)
        payload = {
            "candidate_match_id": candidate_match_id,
            **base,
            "source_ref": str(record["source_ref"]),
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
        }
        payload = self._with_versioning(payload, produced_at)
        return CandidateMatch(**payload)

    def _make_identity_record(
        self,
        records: Sequence[Mapping[str, Any]],
        decision: str,
        confidence_band: str,
        evidence_refs: List[str],
        rule_version: str,
        produced_at: str,
        previous_identity_records: Sequence[Mapping[str, Any]],
        ambiguity_flag_id: Optional[str],
        conflict_ids: List[str],
        canonical_entities: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> IdentityRecord:
        evaluated_record_ids = self._record_ids(records)
        lineage_refs = self._lineage_refs(records, canonical_entities or [])
        core = {
            "evaluated_record_ids": evaluated_record_ids,
            "decision": decision,
            "confidence_band": confidence_band,
            "evidence_refs": sorted(set(evidence_refs)),
            "rule_version": rule_version,
            "lineage_refs": lineage_refs,
            "conflict_ids": sorted(set(conflict_ids)),
        }
        identity_record_id = self._stable_id("identity_record", core)
        parent_id = self._matching_previous_identity_id(
            previous_identity_records,
            evaluated_record_ids,
        )
        payload = {
            "identity_record_id": identity_record_id,
            **core,
            "ambiguity_flag_id": ambiguity_flag_id,
            "source_ref": self._source_ref(records),
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parent_id,
        }
        payload = self._with_versioning(payload, produced_at)
        return IdentityRecord(**payload)

    def _make_ambiguous_identity_and_flag(
        self,
        records: Sequence[Mapping[str, Any]],
        ambiguity_reason: str,
        severity: str,
        evidence_refs: List[str],
        rule_version: str,
        produced_at: str,
        previous_identity_records: Sequence[Mapping[str, Any]],
        conflict_ids: List[str],
    ) -> Tuple[IdentityRecord, AmbiguityFlag]:
        provisional_identity = self._make_identity_record(
            records,
            "ambiguous",
            "unresolved",
            evidence_refs,
            rule_version,
            produced_at,
            previous_identity_records,
            None,
            conflict_ids,
        )
        flag = self._make_ambiguity_flag(
            provisional_identity.identity_record_id,
            records,
            ambiguity_reason,
            severity,
            evidence_refs,
            produced_at,
        )
        identity = self._make_identity_record(
            records,
            "ambiguous",
            "unresolved",
            evidence_refs,
            rule_version,
            produced_at,
            previous_identity_records,
            flag.ambiguity_flag_id,
            conflict_ids,
        )
        flag.identity_record_id = identity.identity_record_id
        flag = self._refresh_ambiguity_flag_hash(flag, produced_at)
        return identity, flag

    def _make_ambiguity_flag(
        self,
        identity_record_id: str,
        records: Sequence[Mapping[str, Any]],
        ambiguity_reason: str,
        severity: str,
        evidence_refs: List[str],
        produced_at: str,
    ) -> AmbiguityFlag:
        affected_record_ids = self._record_ids(records)
        base = {
            "identity_record_id": identity_record_id,
            "ambiguity_reason": ambiguity_reason,
            "severity": severity,
            "affected_record_ids": affected_record_ids,
            "evidence_refs": sorted(set(evidence_refs)),
        }
        ambiguity_flag_id = self._stable_id("ambiguity_flag", base)
        payload = {
            "ambiguity_flag_id": ambiguity_flag_id,
            **base,
            "source_ref": self._source_ref(records),
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
        }
        payload = self._with_versioning(payload, produced_at)
        return AmbiguityFlag(**payload)

    def _refresh_ambiguity_flag_hash(
        self,
        flag: AmbiguityFlag,
        produced_at: str,
    ) -> AmbiguityFlag:
        payload = flag.to_dict()
        payload.pop("version_hash", None)
        payload.pop("version_id", None)
        payload.pop("created_at", None)
        payload.pop("updated_at", None)
        refreshed = self._with_versioning(payload, produced_at)
        return AmbiguityFlag(**refreshed)

    def _make_cluster(
        self,
        canonical_entity_id: Optional[str],
        records: Sequence[Mapping[str, Any]],
        cluster_status: str,
        identity_record_ids: List[str],
        produced_at: str,
        canonical_entities: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> EntityCluster:
        core = {
            "canonical_entity_id": canonical_entity_id,
            "member_record_ids": self._record_ids(records),
            "cluster_status": cluster_status,
            "identity_record_ids": sorted(set(identity_record_ids)),
            "lineage_refs": self._lineage_refs(records, canonical_entities or []),
        }
        entity_cluster_id = self._stable_id("entity_cluster", core)
        payload = {
            "entity_cluster_id": entity_cluster_id,
            **core,
            "source_ref": self._source_ref(records),
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
        }
        payload = self._with_versioning(payload, produced_at)
        return EntityCluster(**payload)

    def _make_conflict(
        self,
        records: Sequence[Mapping[str, Any]],
        candidate_match_ids: List[str],
        conflict_type: str,
        blocking_reason: str,
        recommended_next_step: str,
        rule_version: str,
        produced_at: str,
    ) -> ResolutionConflict:
        core = {
            "involved_record_ids": self._record_ids(records),
            "involved_candidate_match_ids": sorted(set(candidate_match_ids)),
            "conflict_type": conflict_type,
            "blocking_reason": blocking_reason,
            "recommended_next_step": recommended_next_step,
            "rule_version": rule_version,
        }
        conflict_id = self._stable_id("resolution_conflict", core)
        payload = {
            "conflict_id": conflict_id,
            "involved_record_ids": core["involved_record_ids"],
            "involved_candidate_match_ids": core["involved_candidate_match_ids"],
            "conflict_type": conflict_type,
            "blocking_reason": blocking_reason,
            "recommended_next_step": recommended_next_step,
            "related_identity_record_ids": [],
            "source_ref": self._source_ref(records),
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
        }
        payload = self._with_versioning(payload, produced_at)
        return ResolutionConflict(**payload)

    def _record_aliases(
        self,
        record: Mapping[str, Any],
        policy: Mapping[str, Any],
    ) -> List[str]:
        normalized_fields = record["normalized_fields"]
        aliases: List[str] = []
        alias_fields = self._policy_string_list(policy, "alias_fields", DEFAULT_ALIAS_FIELDS)
        for field_name in alias_fields:
            aliases.extend(self._values_as_list(normalized_fields.get(field_name)))
        aliases.extend(self._values_as_list(normalized_fields.get("aliases")))
        return sorted({self._normalize_scalar(value) for value in aliases if value})

    def _canonical_aliases(
        self,
        canonical_entity: Mapping[str, Any],
        policy: Mapping[str, Any],
    ) -> List[str]:
        aliases: List[str] = []
        alias_fields = self._policy_string_list(policy, "alias_fields", DEFAULT_ALIAS_FIELDS)
        for field_name in alias_fields:
            aliases.extend(self._values_as_list(canonical_entity.get(field_name)))
        aliases.extend(self._values_as_list(canonical_entity.get("aliases")))
        return sorted({self._normalize_scalar(value) for value in aliases if value})

    def _record_identifiers(
        self,
        record: Mapping[str, Any],
        policy: Mapping[str, Any],
    ) -> Dict[str, str]:
        normalized_fields = record["normalized_fields"]
        identifiers: Dict[str, str] = {}
        external_identifiers = normalized_fields.get("external_identifiers")
        if isinstance(external_identifiers, Mapping):
            for key, value in external_identifiers.items():
                normalized = self._normalize_scalar(value)
                if normalized:
                    identifiers[str(key)] = normalized
        for field_name in self._policy_string_list(
            policy,
            "strong_identifier_fields",
            DEFAULT_IDENTIFIER_FIELDS,
        ):
            normalized = self._normalize_scalar(normalized_fields.get(field_name))
            if normalized:
                identifiers[field_name] = normalized
        return identifiers

    def _canonical_identifiers(
        self,
        canonical_entity: Mapping[str, Any],
        policy: Mapping[str, Any],
    ) -> Dict[str, str]:
        identifiers: Dict[str, str] = {}
        external_identifiers = canonical_entity.get("external_identifiers")
        if isinstance(external_identifiers, Mapping):
            for key, value in external_identifiers.items():
                normalized = self._normalize_scalar(value)
                if normalized:
                    identifiers[str(key)] = normalized
        for field_name in self._policy_string_list(
            policy,
            "strong_identifier_fields",
            DEFAULT_IDENTIFIER_FIELDS,
        ):
            normalized = self._normalize_scalar(canonical_entity.get(field_name))
            if normalized:
                identifiers[field_name] = normalized
        return identifiers

    def _policy_string_list(
        self,
        policy: Mapping[str, Any],
        field_name: str,
        default_values: Iterable[str],
    ) -> List[str]:
        values = policy.get(field_name)
        if not isinstance(values, list):
            return list(default_values)
        return [str(value) for value in values if str(value).strip()]

    def _values_as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _normalize_scalar(self, value: Any) -> str:
        if value is None:
            return ""
        return " ".join(str(value).strip().upper().split())

    def _confidence_band(self, score: int, policy: Mapping[str, Any]) -> str:
        if score >= int(policy.get("high_confidence_score", 3)):
            return "high"
        if score >= int(policy.get("match_threshold", 2)):
            return "medium"
        if score > 0:
            return "low"
        return "unresolved"

    def _blocking_reason(self, conflict_type: str) -> str:
        reasons = {
            "identifier_collision": "Strong identifiers are incompatible.",
            "taxonomy_mismatch": "Record and candidate belong to incompatible entity classes.",
            "evidence_tie": "Deterministic evidence does not select one candidate.",
        }
        return reasons.get(conflict_type, "Resolution conflict blocks a closed decision.")

    def _next_step(self, conflict_type: str) -> str:
        steps = {
            "identifier_collision": "split_cluster",
            "taxonomy_mismatch": "manual_review",
            "evidence_tie": "keep_ambiguous",
        }
        return steps.get(conflict_type, "manual_review")

    def _record_ids(self, records: Sequence[Mapping[str, Any]]) -> List[str]:
        return sorted({str(record["record_id"]) for record in records})

    def _source_ref(self, records: Sequence[Mapping[str, Any]]) -> str:
        return "|".join(sorted({str(record["source_ref"]) for record in records}))

    def _lineage_refs(
        self,
        records: Sequence[Mapping[str, Any]],
        canonical_entities: Sequence[Mapping[str, Any]],
    ) -> List[str]:
        refs: Set[str] = set()
        for record in records:
            refs.update(str(value) for value in record.get("lineage_refs", []))
            refs.add(str(record["provenance_ref"]))
        for entity in canonical_entities:
            refs.update(str(value) for value in entity.get("lineage_refs", []))
            refs.add(f"canonical_entity:{entity['canonical_entity_id']}")
            refs.add(f"taxonomy:{entity['taxonomy_version_id']}")
        return sorted(refs)

    def _matching_previous_identity_id(
        self,
        previous_identity_records: Sequence[Mapping[str, Any]],
        evaluated_record_ids: List[str],
    ) -> Optional[str]:
        target = sorted(evaluated_record_ids)
        for record in previous_identity_records:
            if sorted(str(value) for value in record.get("evaluated_record_ids", [])) == target:
                previous_id = record.get("identity_record_id")
                if previous_id:
                    return str(previous_id)
        return None

    def _with_versioning(self, payload: Dict[str, Any], produced_at: str) -> Dict[str, Any]:
        version_hash = self._hash(payload)
        payload = dict(payload)
        payload["version_id"] = f"v1_{version_hash[:12]}"
        payload["created_at"] = produced_at
        payload["updated_at"] = produced_at
        payload["version_hash"] = version_hash
        return payload

    def _stable_id(self, prefix: str, material: Mapping[str, Any]) -> str:
        return f"{prefix}_{self._hash(material)[:16]}"

    def _hash(self, material: Mapping[str, Any]) -> str:
        encoded = json.dumps(
            self._canonical_jsonable(material),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _canonical_jsonable(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(key): self._canonical_jsonable(val) for key, val in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._canonical_jsonable(item) for item in value]
        return value

    def _sort_by_id(self, items: Sequence[Any], id_field: str) -> List[Any]:
        return sorted(items, key=lambda item: getattr(item, id_field))
