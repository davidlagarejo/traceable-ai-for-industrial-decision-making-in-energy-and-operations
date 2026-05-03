"""Deterministic implementation for motor_010.

The engine detects document-level exact duplicates and near duplicates using
stable fingerprints, canonical field signatures, fixed thresholds, and version
context. It emits advisory output objects only; it never mutates upstream input.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import hashlib
import itertools
import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Optional

from .errors import DuplicateInputError
from .models import (
    DeduplicationDecision,
    DuplicateCluster,
    DuplicateSimilarityResult,
    SimilarityRecord,
    ThresholdProfile,
)


MOTOR_ID = "motor_010"
DEFAULT_METHOD_VERSION = "dup-sim-1.0.0"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"

DOCUMENT_LEVEL_FIELDS = frozenset(
    {
        "content_fingerprint",
        "date",
        "document_date",
        "document_id",
        "effective_date",
        "file_hash",
        "permit",
        "permit_id",
        "raw_fingerprint",
        "source_document_id",
        "source_doc_id",
    }
)


@dataclass(frozen=True)
class _RecordView:
    ref: str
    level: str
    source_refs: tuple[str, ...]
    lineage_refs: tuple[str, ...]
    upstream_refs: tuple[str, ...]
    raw_fingerprint: Optional[str] = None
    parsed_signature: Optional[str] = None
    normalized_signature: Optional[str] = None
    signature_fields: frozenset[str] = frozenset()


@dataclass(frozen=True)
class _VersionView:
    version_id: str
    object_ref: str
    lineage_id: str
    content_fingerprint: str
    relation_refs: frozenset[str]
    external_context: bool


class DuplicateSimilarityControlEngine:
    """Core deterministic interface for Duplicate / Similarity Control Engine."""

    def process(
        self,
        *,
        parsed_records: Iterable[Mapping[str, Any]],
        normalized_records: Iterable[Mapping[str, Any]],
        version_records: Iterable[Mapping[str, Any]],
        method_version: str = DEFAULT_METHOD_VERSION,
        threshold_profile_ref: Optional[str] = "threshold:default:2026-04",
        threshold_profile: Optional[dict[str, Any]] = None,
        produced_at: str = DEFAULT_PRODUCED_AT,
    ) -> DuplicateSimilarityResult:
        """Validate inputs, compute duplicate evidence, and emit advisory outputs."""

        if not isinstance(method_version, str) or not method_version.strip():
            raise DuplicateInputError(
                code="DUPLICATE_INPUT_INVALID_METHOD_VERSION",
                message="method_version must be a non-empty string",
                field="method_version",
            )

        profile = ThresholdProfile.from_mapping(threshold_profile_ref, threshold_profile)
        parsed = self._parse_parsed_records(parsed_records)
        normalized = self._parse_normalized_records(normalized_records, parsed)

        if not parsed and not normalized:
            raise DuplicateInputError(
                code="DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD",
                message="at least one parsed or normalized record is required",
                field="parsed_records",
            )

        records_by_ref = {record.ref: record for record in [*parsed, *normalized]}
        versions = self._parse_version_records(version_records, records_by_ref)
        version_refs = self._build_version_refs(records_by_ref, versions)
        self._validate_version_coverage(records_by_ref, version_refs)

        similarities = self._build_similarity_records(
            parsed=parsed,
            normalized=normalized,
            version_refs=version_refs,
            versions=versions,
            method_version=method_version,
            profile=profile,
            produced_at=produced_at,
        )
        clusters = self._build_clusters(
            similarities=similarities,
            method_version=method_version,
            profile=profile,
            produced_at=produced_at,
        )
        decisions = self._build_decisions(
            clusters=clusters,
            method_version=method_version,
            produced_at=produced_at,
        )

        return DuplicateSimilarityResult(
            duplicate_cluster=clusters,
            similarity_score=sorted(similarities, key=lambda item: item.similarity_id),
            dedup_recommendation=decisions,
        )

    def run(self, **kwargs: Any) -> DuplicateSimilarityResult:
        """Alias kept for callers that use motor-style run naming."""

        return self.process(**kwargs)

    def _parse_parsed_records(
        self, parsed_records: Iterable[Mapping[str, Any]]
    ) -> list[_RecordView]:
        views: list[_RecordView] = []
        seen: set[str] = set()
        for item in _as_sequence("parsed_records", parsed_records):
            if not isinstance(item, Mapping):
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD",
                    message="parsed_records must contain mapping objects",
                    field="parsed_records",
                )

            record_id = _required_string(item, "record_id", "DUPLICATE_INPUT_MISSING_TRACEABILITY")
            if record_id in seen:
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_MISSING_TRACEABILITY",
                    message="parsed record identifiers must be unique",
                    field="record_id",
                    record_ref=record_id,
                )
            seen.add(record_id)

            source_id = _required_string(item, "source_id", "DUPLICATE_INPUT_MISSING_TRACEABILITY")
            if not _has_traceability_metadata(item):
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_MISSING_TRACEABILITY",
                    message="parsed record must preserve provenance or lineage metadata",
                    field="provenance",
                    record_ref=record_id,
                )

            raw_fingerprint = item.get("raw_fingerprint")
            if raw_fingerprint is not None:
                if not isinstance(raw_fingerprint, str) or not raw_fingerprint.strip():
                    raise DuplicateInputError(
                        code="DUPLICATE_INPUT_INVALID_FINGERPRINT_TYPE",
                        message="raw_fingerprint must be a non-empty string when present",
                        field="raw_fingerprint",
                        record_ref=record_id,
                    )
                raw_fingerprint = raw_fingerprint.strip()

            parsed_fields = item.get("parsed_fields")
            parsed_signature = _string_or_canonical(item.get("parsed_signature"))
            if parsed_signature is None:
                parsed_signature = _canonical_payload_signature(parsed_fields)

            signature_fields = _signature_field_names(parsed_fields, parsed_signature)
            lineage_refs = _lineage_refs(item)
            views.append(
                _RecordView(
                    ref=record_id,
                    level="parsed",
                    source_refs=(record_id, source_id),
                    lineage_refs=lineage_refs,
                    upstream_refs=(),
                    raw_fingerprint=raw_fingerprint,
                    parsed_signature=parsed_signature,
                    signature_fields=signature_fields,
                )
            )
        return sorted(views, key=lambda record: record.ref)

    def _parse_normalized_records(
        self,
        normalized_records: Iterable[Mapping[str, Any]],
        parsed_records: list[_RecordView],
    ) -> list[_RecordView]:
        parsed_refs = {record.ref for record in parsed_records}
        views: list[_RecordView] = []
        seen: set[str] = set()
        for item in _as_sequence("normalized_records", normalized_records):
            if not isinstance(item, Mapping):
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD",
                    message="normalized_records must contain mapping objects",
                    field="normalized_records",
                )

            normalized_id = _required_string(
                item, "normalized_record_id", "DUPLICATE_INPUT_MISSING_TRACEABILITY"
            )
            if normalized_id in seen:
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_MISSING_TRACEABILITY",
                    message="normalized record identifiers must be unique",
                    field="normalized_record_id",
                    record_ref=normalized_id,
                )
            seen.add(normalized_id)

            upstream = _optional_string(item.get("record_id"))
            bridge = _first_present_string(item, ("lineage_bridge", "parsed_record_ref", "upstream_record_ref"))
            if upstream and upstream not in parsed_refs and not bridge:
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_BROKEN_REFERENCE",
                    message="normalized record must reference an included parsed record or an explicit lineage bridge",
                    field="record_id",
                    record_ref=normalized_id,
                )
            if not upstream and not bridge:
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_BROKEN_REFERENCE",
                    message="normalized record must carry a parsed record reference or explicit lineage bridge",
                    field="record_id",
                    record_ref=normalized_id,
                )

            if not _has_traceability_metadata(item):
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_MISSING_TRACEABILITY",
                    message="normalized record must preserve lineage metadata",
                    field="lineage_ref",
                    record_ref=normalized_id,
                )
            _required_string(
                item,
                "normalization_version",
                "DUPLICATE_INPUT_MISSING_TRACEABILITY",
                record_ref=normalized_id,
            )

            normalized_fields = item.get("normalized_fields")
            normalized_signature = _string_or_canonical(item.get("normalized_signature"))
            if normalized_signature is None:
                normalized_signature = _canonical_payload_signature(normalized_fields)

            source_refs = [normalized_id]
            upstream_refs: list[str] = []
            if upstream:
                source_refs.append(upstream)
                upstream_refs.append(upstream)
            if bridge:
                source_refs.append(bridge)
                upstream_refs.append(bridge)

            views.append(
                _RecordView(
                    ref=normalized_id,
                    level="normalized",
                    source_refs=tuple(sorted(set(source_refs))),
                    lineage_refs=_lineage_refs(item),
                    upstream_refs=tuple(sorted(set(upstream_refs))),
                    normalized_signature=normalized_signature,
                    signature_fields=_signature_field_names(normalized_fields, normalized_signature),
                )
            )
        return sorted(views, key=lambda record: record.ref)

    def _parse_version_records(
        self,
        version_records: Iterable[Mapping[str, Any]],
        records_by_ref: Mapping[str, _RecordView],
    ) -> list[_VersionView]:
        versions: list[_VersionView] = []
        accepted_refs = set(records_by_ref)
        for record in records_by_ref.values():
            accepted_refs.update(record.upstream_refs)

        for item in _as_sequence("version_records", version_records):
            if not isinstance(item, Mapping):
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_INVALID_VERSION_CONTEXT",
                    message="version_records must contain mapping objects",
                    field="version_records",
                )
            version_id = _required_string(
                item, "version_id", "DUPLICATE_INPUT_INVALID_VERSION_CONTEXT"
            )
            object_ref = _required_string(
                item, "object_ref", "DUPLICATE_INPUT_INVALID_VERSION_CONTEXT", record_ref=version_id
            )
            lineage_id = _required_string(
                item, "lineage_id", "DUPLICATE_INPUT_INVALID_VERSION_CONTEXT", record_ref=object_ref
            )
            content_fingerprint = _required_string(
                item,
                "content_fingerprint",
                "DUPLICATE_INPUT_INVALID_VERSION_CONTEXT",
                record_ref=object_ref,
            )
            external = bool(item.get("external_context") or item.get("scope") == "external")
            if object_ref not in accepted_refs and not external:
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_BROKEN_REFERENCE",
                    message="version_record.object_ref must resolve to an input record or be explicit external context",
                    field="object_ref",
                    record_ref=object_ref,
                )

            linked_record = records_by_ref.get(object_ref)
            if linked_record and linked_record.lineage_refs and lineage_id not in linked_record.lineage_refs:
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_INVALID_VERSION_CONTEXT",
                    message="version_record.lineage_id conflicts with input lineage metadata",
                    field="lineage_id",
                    record_ref=object_ref,
                )

            relation_refs = _relation_refs(item)
            versions.append(
                _VersionView(
                    version_id=version_id,
                    object_ref=object_ref,
                    lineage_id=lineage_id,
                    content_fingerprint=content_fingerprint,
                    relation_refs=relation_refs,
                    external_context=external,
                )
            )
        return sorted(versions, key=lambda version: (version.object_ref, version.version_id))

    def _build_version_refs(
        self,
        records_by_ref: Mapping[str, _RecordView],
        versions: Sequence[_VersionView],
    ) -> dict[str, tuple[str, ...]]:
        by_object: dict[str, list[str]] = {}
        for version in versions:
            by_object.setdefault(version.object_ref, []).append(version.version_id)

        refs: dict[str, tuple[str, ...]] = {}
        for record in records_by_ref.values():
            collected = list(by_object.get(record.ref, ()))
            for upstream_ref in record.upstream_refs:
                collected.extend(by_object.get(upstream_ref, ()))
            refs[record.ref] = tuple(sorted(set(collected)))
        return refs

    def _validate_version_coverage(
        self,
        records_by_ref: Mapping[str, _RecordView],
        version_refs: Mapping[str, tuple[str, ...]],
    ) -> None:
        for record_ref in sorted(records_by_ref):
            if not version_refs.get(record_ref):
                raise DuplicateInputError(
                    code="DUPLICATE_INPUT_INVALID_VERSION_CONTEXT",
                    message="every comparable record requires resolved version context",
                    field="version_records",
                    record_ref=record_ref,
                )

    def _build_similarity_records(
        self,
        *,
        parsed: Sequence[_RecordView],
        normalized: Sequence[_RecordView],
        version_refs: Mapping[str, tuple[str, ...]],
        versions: Sequence[_VersionView],
        method_version: str,
        profile: ThresholdProfile,
        produced_at: str,
    ) -> list[SimilarityRecord]:
        records: list[SimilarityRecord] = []

        for left, right in itertools.combinations(parsed, 2):
            if left.raw_fingerprint and left.raw_fingerprint == right.raw_fingerprint:
                records.append(
                    self._similarity_record(
                        left=left,
                        right=right,
                        comparison_level="raw",
                        score=1.0,
                        similarity_kind="exact_duplicate",
                        evidence_features=("raw_fingerprint",),
                        version_refs=version_refs,
                        versions=versions,
                        method_version=method_version,
                        profile=profile,
                        produced_at=produced_at,
                    )
                )
                continue

            if (
                left.parsed_signature
                and right.parsed_signature
                and _has_document_level_feature(left)
                and _has_document_level_feature(right)
            ):
                score = _signature_similarity(left.parsed_signature, right.parsed_signature)
                kind = _classify_score(score, profile)
                if kind:
                    records.append(
                        self._similarity_record(
                            left=left,
                            right=right,
                            comparison_level="parsed",
                            score=score,
                            similarity_kind=kind,
                            evidence_features=("parsed_field_signature",),
                            version_refs=version_refs,
                            versions=versions,
                            method_version=method_version,
                            profile=profile,
                            produced_at=produced_at,
                        )
                    )

        for left, right in itertools.combinations(normalized, 2):
            if (
                left.normalized_signature
                and right.normalized_signature
                and _has_document_level_feature(left)
                and _has_document_level_feature(right)
            ):
                score = _signature_similarity(left.normalized_signature, right.normalized_signature)
                kind = _classify_score(score, profile)
                if kind:
                    records.append(
                        self._similarity_record(
                            left=left,
                            right=right,
                            comparison_level="normalized",
                            score=score,
                            similarity_kind=kind,
                            evidence_features=("normalized_field_signature",),
                            version_refs=version_refs,
                            versions=versions,
                            method_version=method_version,
                            profile=profile,
                            produced_at=produced_at,
                        )
                    )

        return _dedupe_similarities(records)

    def _similarity_record(
        self,
        *,
        left: _RecordView,
        right: _RecordView,
        comparison_level: str,
        score: float,
        similarity_kind: str,
        evidence_features: Sequence[str],
        version_refs: Mapping[str, tuple[str, ...]],
        versions: Sequence[_VersionView],
        method_version: str,
        profile: ThresholdProfile,
        produced_at: str,
    ) -> SimilarityRecord:
        left_ref, right_ref = sorted((left.ref, right.ref))
        pair_version_refs = tuple(
            sorted(set(version_refs.get(left.ref, ()) + version_refs.get(right.ref, ())))
        )
        features = list(evidence_features)
        if _has_version_successor_relation(left, right, versions):
            similarity_kind = "reviewable_similarity"
            features.append("version_successor_relation")

        score = round(max(0.0, min(1.0, float(score))), 6)
        similarity_id = _stable_id(
            "similarity", left_ref, right_ref, comparison_level, method_version
        )
        source_ref = tuple(
            sorted(set((left.ref, right.ref, *left.source_refs, *right.source_refs, *pair_version_refs)))
        )
        payload = {
            "similarity_id": similarity_id,
            "left_record_ref": left_ref,
            "right_record_ref": right_ref,
            "comparison_level": comparison_level,
            "similarity_score": score,
            "similarity_kind": similarity_kind,
            "method_version": method_version,
            "evidence_features": sorted(set(features)),
            "threshold_profile_ref": profile.ref,
            "version_context_refs": pair_version_refs,
            "cluster_id": None,
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
        }
        version_hash = _hash_payload(payload)
        return SimilarityRecord(
            similarity_id=similarity_id,
            left_record_ref=left_ref,
            right_record_ref=right_ref,
            comparison_level=comparison_level,
            similarity_score=score,
            similarity_kind=similarity_kind,
            method_version=method_version,
            evidence_features=sorted(set(features)),
            threshold_profile_ref=profile.ref,
            version_context_refs=list(pair_version_refs),
            cluster_id=None,
            version_id=f"{similarity_id}:version:{version_hash[:16]}",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash=version_hash,
            source_ref=list(source_ref),
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=None,
        )

    def _build_clusters(
        self,
        *,
        similarities: Sequence[SimilarityRecord],
        method_version: str,
        profile: ThresholdProfile,
        produced_at: str,
    ) -> list[DuplicateCluster]:
        accepted = [
            item
            for item in similarities
            if item.similarity_kind in {"exact_duplicate", "near_duplicate"}
        ]
        clusters: list[DuplicateCluster] = []
        for key in sorted({_cluster_key(item) for item in accepted}):
            scoped_edges = [item for item in accepted if _cluster_key(item) == key]
            parent: dict[str, str] = {}

            def find(node: str) -> str:
                parent.setdefault(node, node)
                while parent[node] != node:
                    parent[node] = parent[parent[node]]
                    node = parent[node]
                return node

            def union(left: str, right: str) -> None:
                root_left = find(left)
                root_right = find(right)
                if root_left != root_right:
                    parent[max(root_left, root_right)] = min(root_left, root_right)

            for edge in scoped_edges:
                union(edge.left_record_ref, edge.right_record_ref)

            components: dict[str, set[str]] = {}
            for node in sorted(parent):
                components.setdefault(find(node), set()).add(node)

            for members_set in components.values():
                members = sorted(members_set)
                if len(members) < 2:
                    continue
                evidence = [
                    edge
                    for edge in scoped_edges
                    if edge.left_record_ref in members and edge.right_record_ref in members
                ]
                evidence_refs = sorted({edge.similarity_id for edge in evidence})
                version_context_refs = sorted(
                    {ref for edge in evidence for ref in edge.version_context_refs}
                )
                match_scope, cluster_kind = key
                cluster_id = _stable_id(
                    "cluster", members, match_scope, cluster_kind, method_version
                )
                cluster_fingerprint = _hash_payload(
                    {
                        "member_record_refs": members,
                        "match_scope": match_scope,
                        "cluster_kind": cluster_kind,
                        "evidence_refs": evidence_refs,
                        "method_version": method_version,
                        "threshold_profile_ref": profile.ref,
                        "version_context_refs": version_context_refs,
                    }
                )
                source_ref = sorted(set((*members, *evidence_refs, *version_context_refs)))
                payload = {
                    "cluster_id": cluster_id,
                    "member_record_refs": members,
                    "cluster_fingerprint": cluster_fingerprint,
                    "match_scope": match_scope,
                    "cluster_kind": cluster_kind,
                    "evidence_refs": evidence_refs,
                    "method_version": method_version,
                    "threshold_profile_ref": profile.ref,
                    "version_context_refs": version_context_refs,
                    "source_ref": source_ref,
                    "produced_by_motor": MOTOR_ID,
                    "produced_at": produced_at,
                    "parent_id": None,
                }
                version_hash = _hash_payload(payload)
                cluster = DuplicateCluster(
                    cluster_id=cluster_id,
                    member_record_refs=members,
                    cluster_fingerprint=cluster_fingerprint,
                    match_scope=match_scope,
                    cluster_kind=cluster_kind,
                    evidence_refs=evidence_refs,
                    method_version=method_version,
                    threshold_profile_ref=profile.ref,
                    version_context_refs=version_context_refs,
                    version_id=f"{cluster_id}:version:{version_hash[:16]}",
                    created_at=produced_at,
                    updated_at=produced_at,
                    version_hash=version_hash,
                    source_ref=source_ref,
                    produced_by_motor=MOTOR_ID,
                    produced_at=produced_at,
                    parent_id=None,
                )
                for edge in evidence:
                    self._attach_cluster(edge, cluster_id)
                clusters.append(cluster)

        return sorted(clusters, key=lambda item: item.cluster_id)

    def _attach_cluster(self, similarity: SimilarityRecord, cluster_id: str) -> None:
        similarity.cluster_id = cluster_id
        payload = similarity.to_dict()
        payload.pop("version_id")
        payload.pop("created_at")
        payload.pop("updated_at")
        payload.pop("version_hash")
        version_hash = _hash_payload(payload)
        similarity.version_hash = version_hash
        similarity.version_id = f"{similarity.similarity_id}:version:{version_hash[:16]}"

    def _build_decisions(
        self,
        *,
        clusters: Sequence[DuplicateCluster],
        method_version: str,
        produced_at: str,
    ) -> list[DeduplicationDecision]:
        decisions: list[DeduplicationDecision] = []
        for cluster in sorted(clusters, key=lambda item: item.cluster_id):
            if cluster.cluster_kind == "exact_duplicate":
                recommendation = "suppress_duplicate"
                target_refs = cluster.member_record_refs[1:]
            elif cluster.cluster_kind == "near_duplicate":
                recommendation = "manual_review"
                target_refs = cluster.member_record_refs
            else:
                recommendation = "keep_all"
                target_refs = cluster.member_record_refs

            target_refs = sorted(set(target_refs))
            if not set(target_refs).issubset(set(cluster.member_record_refs)):
                raise DuplicateInputError(
                    code="DUPLICATE_OUTPUT_INVALID_DECISION_TARGET",
                    message="decision targets must be a subset of cluster members",
                    field="target_record_refs",
                    record_ref=cluster.cluster_id,
                )

            decision_id = _stable_id(
                "decision", cluster.cluster_id, recommendation, target_refs, method_version
            )
            source_ref = sorted(set((cluster.cluster_id, *cluster.evidence_refs, *target_refs)))
            payload = {
                "decision_id": decision_id,
                "cluster_id": cluster.cluster_id,
                "recommendation": recommendation,
                "target_record_refs": target_refs,
                "rationale_refs": cluster.evidence_refs,
                "decision_status": "recommended_only",
                "method_version": method_version,
                "source_ref": source_ref,
                "produced_by_motor": MOTOR_ID,
                "produced_at": produced_at,
                "parent_id": None,
            }
            version_hash = _hash_payload(payload)
            decisions.append(
                DeduplicationDecision(
                    decision_id=decision_id,
                    cluster_id=cluster.cluster_id,
                    recommendation=recommendation,
                    target_record_refs=target_refs,
                    rationale_refs=cluster.evidence_refs,
                    decision_status="recommended_only",
                    method_version=method_version,
                    version_id=f"{decision_id}:version:{version_hash[:16]}",
                    created_at=produced_at,
                    updated_at=produced_at,
                    version_hash=version_hash,
                    source_ref=source_ref,
                    produced_by_motor=MOTOR_ID,
                    produced_at=produced_at,
                    parent_id=None,
                )
            )
        return sorted(decisions, key=lambda item: item.decision_id)


def run_duplicate_similarity_control(**kwargs: Any) -> DuplicateSimilarityResult:
    return DuplicateSimilarityControlEngine().process(**kwargs)


def _as_sequence(name: str, value: Iterable[Mapping[str, Any]]) -> Sequence[Mapping[str, Any]]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise DuplicateInputError(
            code="DUPLICATE_INPUT_UNSUPPORTED_PAYLOAD",
            message=f"{name} must be an iterable of mapping objects",
            field=name,
        )
    return tuple(value)


def _required_string(
    item: Mapping[str, Any],
    field: str,
    code: str,
    record_ref: Optional[str] = None,
) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DuplicateInputError(
            code=code,
            message=f"{field} must be a non-empty string",
            field=field,
            record_ref=record_ref or _optional_string(item.get("record_id")),
        )
    return value.strip()


def _optional_string(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _first_present_string(item: Mapping[str, Any], fields: Sequence[str]) -> Optional[str]:
    for field in fields:
        value = _optional_string(item.get(field))
        if value:
            return value
    return None


def _has_traceability_metadata(item: Mapping[str, Any]) -> bool:
    provenance = item.get("provenance")
    if isinstance(provenance, Mapping) and bool(provenance):
        return True
    for field in ("provenance_ref", "lineage_ref", "lineage_id", "lineage_bridge"):
        if _optional_string(item.get(field)):
            return True
    return False


def _lineage_refs(item: Mapping[str, Any]) -> tuple[str, ...]:
    refs = []
    for field in ("lineage_ref", "lineage_id", "lineage_bridge"):
        value = _optional_string(item.get(field))
        if value:
            refs.append(value)
    return tuple(sorted(set(refs)))


def _relation_refs(item: Mapping[str, Any]) -> frozenset[str]:
    refs: set[str] = set()
    for field in ("predecessor_ref", "successor_ref", "predecessor_id", "successor_id"):
        value = _optional_string(item.get(field))
        if value:
            refs.add(value)
    for field in ("predecessor_refs", "successor_refs", "predecessor_ids", "successor_ids"):
        value = item.get(field)
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            refs.update(str(ref).strip() for ref in value if str(ref).strip())
    return frozenset(refs)


def _string_or_canonical(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, Mapping) or isinstance(value, list):
        return _canonical_json(value)
    return None


def _canonical_payload_signature(value: Any) -> Optional[str]:
    if isinstance(value, Mapping) and value:
        return _canonical_json(value)
    if isinstance(value, list) and value:
        return _canonical_json(value)
    return None


def _signature_field_names(value: Any, signature: Optional[str]) -> frozenset[str]:
    fields: set[str] = set()
    if isinstance(value, Mapping):
        fields.update(str(key).lower() for key in value.keys())
    if signature:
        for part in signature.replace(";", "|").split("|"):
            if "=" in part:
                fields.add(part.split("=", 1)[0].strip().lower())
            elif ":" in part:
                fields.add(part.split(":", 1)[0].strip().lower())
    return frozenset(field for field in fields if field)


def _has_document_level_feature(record: _RecordView) -> bool:
    if record.raw_fingerprint:
        return True
    return bool(record.signature_fields & DOCUMENT_LEVEL_FIELDS)


def _signature_similarity(left: str, right: str) -> float:
    if left == right:
        return 1.0
    return max(0.0, min(1.0, SequenceMatcher(None, left, right).ratio()))


def _classify_score(score: float, profile: ThresholdProfile) -> Optional[str]:
    if score >= 1.0:
        return "exact_duplicate"
    if score >= profile.near_duplicate_threshold:
        return "near_duplicate"
    if score >= profile.manual_review_floor:
        return "reviewable_similarity"
    return None


def _has_version_successor_relation(
    left: _RecordView, right: _RecordView, versions: Sequence[_VersionView]
) -> bool:
    left_refs = {left.ref, *left.upstream_refs}
    right_refs = {right.ref, *right.upstream_refs}
    left_versions = {
        version.version_id
        for version in versions
        if version.object_ref in left_refs
    }
    right_versions = {
        version.version_id
        for version in versions
        if version.object_ref in right_refs
    }
    left_all = left_refs | left_versions
    right_all = right_refs | right_versions
    for version in versions:
        if version.object_ref in left_refs and version.relation_refs & right_all:
            return True
        if version.object_ref in right_refs and version.relation_refs & left_all:
            return True
    return False


def _dedupe_similarities(records: Sequence[SimilarityRecord]) -> list[SimilarityRecord]:
    by_id: dict[str, SimilarityRecord] = {}
    priority = {"exact_duplicate": 3, "near_duplicate": 2, "reviewable_similarity": 1}
    for record in records:
        current = by_id.get(record.similarity_id)
        if current is None or priority[record.similarity_kind] > priority[current.similarity_kind]:
            by_id[record.similarity_id] = record
    return sorted(by_id.values(), key=lambda item: item.similarity_id)


def _cluster_key(similarity: SimilarityRecord) -> tuple[str, str]:
    if similarity.similarity_kind == "exact_duplicate":
        return similarity.comparison_level, "exact_duplicate"
    return similarity.comparison_level, "near_duplicate"


def _stable_id(kind: str, *parts: Any) -> str:
    return f"{MOTOR_ID}:{kind}:{_hash_payload(parts)}"


def _hash_payload(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
