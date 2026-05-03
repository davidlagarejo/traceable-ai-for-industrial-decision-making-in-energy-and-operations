"""Deterministic implementation for motor_011.

The engine promotes already evaluated upstream objects into governed library
outputs. It never ingests raw data, recalculates quality, resolves identity, or
rewrites duplicate evidence.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Optional

from .errors import CurationInputError
from .models import (
    CuratedBundle,
    CurationRejection,
    CurationResult,
    LibraryObject,
    LibraryVersion,
)


MOTOR_ID = "motor_011"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
DEFAULT_ACCEPTED_STATUSES = ("pass",)
DEFAULT_BLOCKING_IDENTITY_DECISIONS = frozenset(
    {"ambiguous", "contradictory", "conflict", "unresolved"}
)
DEFAULT_ACCEPTED_IDENTITY_DECISIONS = frozenset(
    {"same_entity", "same_as", "resolved", "unique_entity", "accepted", "match"}
)
SUPPRESSION_CODE = "CURATION_DUPLICATE_SUPPRESSED"


@dataclass(frozen=True)
class _Policy:
    curation_run_id: str
    curation_rule_version: str
    bundle_scope: str
    accepted_quality_statuses: frozenset[str]
    blocking_flag_codes: frozenset[str]
    duplicate_policy: str
    produced_at: str
    requires_resolved_identity: bool
    blocking_identity_decisions: frozenset[str]
    accepted_identity_decisions: frozenset[str]
    blocking_identity_confidence_bands: frozenset[str]
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class _DedupAssessment:
    evidence_refs_by_candidate: dict[str, list[str]]
    suppressed_by_candidate: dict[str, list[str]]
    invalid_by_candidate: dict[str, list[str]]


class LibraryCurationEngine:
    """Core deterministic interface for Library Curation Engine."""

    def curate(
        self,
        *,
        quality_records: Iterable[Mapping[str, Any]],
        identity_records: Iterable[Mapping[str, Any]],
        dedup_records: Iterable[Mapping[str, Any]],
        curation_policy: Mapping[str, Any],
    ) -> CurationResult:
        """Validate upstream evidence, emit library outputs, and version them."""

        policy = self._parse_policy(curation_policy)
        quality_items = _as_sequence("quality_records", quality_records)
        identity_items = _as_sequence("identity_records", identity_records)
        dedup_items = _as_sequence("dedup_records", dedup_records)

        candidate_refs = self._candidate_refs(policy, quality_items)
        quality_by_subject = self._index_quality_records(quality_items)
        identity_by_candidate = self._index_identity_records(identity_items, candidate_refs)
        dedup = self._assess_dedup_records(dedup_items, candidate_refs, policy)

        library_objects: list[LibraryObject] = []
        object_versions: list[LibraryVersion] = []
        rejections: list[CurationRejection] = []

        for candidate_ref in sorted(candidate_refs):
            quality_result = self._quality_for_candidate(
                candidate_ref, quality_by_subject, policy
            )
            if isinstance(quality_result, CurationRejection):
                rejections.append(quality_result)
                continue
            quality_record = quality_result

            identity_result = self._identity_for_candidate(
                candidate_ref, identity_by_candidate, policy, quality_record
            )
            if isinstance(identity_result, CurationRejection):
                rejections.append(identity_result)
                continue
            identity_record = identity_result

            invalid_dedup_refs = dedup.invalid_by_candidate.get(candidate_ref, [])
            if invalid_dedup_refs:
                rejections.append(
                    self._build_rejection(
                        candidate_ref=candidate_ref,
                        error_code="CURATION_DEDUP_REF_INVALID",
                        blocking_evidence_refs=invalid_dedup_refs,
                        policy=policy,
                        quality_record=quality_record,
                        identity_record=identity_record,
                        dedup_evidence_refs=dedup.evidence_refs_by_candidate.get(
                            candidate_ref, []
                        ),
                    )
                )
                continue

            dedup_evidence_refs = dedup.evidence_refs_by_candidate.get(candidate_ref, [])
            if candidate_ref in dedup.suppressed_by_candidate:
                suppression_refs = dedup.suppressed_by_candidate[candidate_ref]
                rejections.append(
                    self._build_rejection(
                        candidate_ref=candidate_ref,
                        error_code=SUPPRESSION_CODE,
                        blocking_evidence_refs=suppression_refs,
                        policy=policy,
                        quality_record=quality_record,
                        identity_record=identity_record,
                        dedup_evidence_refs=dedup_evidence_refs,
                    )
                )
                continue

            library_object, object_version = self._build_library_object(
                candidate_ref=candidate_ref,
                quality_record=quality_record,
                identity_record=identity_record,
                dedup_evidence_refs=dedup_evidence_refs,
                policy=policy,
            )
            library_objects.append(library_object)
            object_versions.append(object_version)

        library_objects = sorted(
            library_objects, key=lambda item: item.library_object_id
        )
        rejections = sorted(rejections, key=lambda item: item.curation_rejection_id)
        curated_bundle, bundle_version = self._build_bundle(
            library_objects=library_objects,
            rejections=rejections,
            policy=policy,
        )
        versions = sorted(
            [*object_versions, bundle_version], key=lambda item: item.library_version_id
        )
        return CurationResult(
            library_object=library_objects,
            curated_bundle=curated_bundle,
            library_version=versions,
            curation_rejection=rejections,
        )

    def run(self, **kwargs: Any) -> CurationResult:
        """Alias for orchestrators that call motors through a run method."""

        return self.curate(**kwargs)

    def _parse_policy(self, curation_policy: Mapping[str, Any]) -> _Policy:
        if not isinstance(curation_policy, Mapping):
            raise CurationInputError(
                code="CURATION_POLICY_BLOCKED",
                message="curation_policy must be a mapping",
                field="curation_policy",
            )

        curation_run_id = _required_policy_string(
            curation_policy, "curation_run_id"
        )
        curation_rule_version = _required_policy_string(
            curation_policy, "curation_rule_version"
        )
        bundle_scope = _required_policy_string(curation_policy, "bundle_scope")
        accepted_statuses = _policy_string_set(
            curation_policy,
            "accepted_quality_statuses",
            DEFAULT_ACCEPTED_STATUSES,
        )
        blocking_flags = _policy_string_set(
            curation_policy, "blocking_flag_codes", ()
        )
        duplicate_policy = _optional_string(
            curation_policy.get("duplicate_policy")
        ) or "retain_representative"
        produced_at = (
            _optional_string(curation_policy.get("published_at"))
            or _optional_string(curation_policy.get("produced_at"))
            or DEFAULT_PRODUCED_AT
        )
        requires_resolved_identity = bool(
            curation_policy.get("requires_resolved_identity", True)
        )
        blocking_identity_decisions = _policy_string_set(
            curation_policy,
            "blocking_identity_decisions",
            DEFAULT_BLOCKING_IDENTITY_DECISIONS,
        )
        accepted_identity_decisions = _policy_string_set(
            curation_policy,
            "accepted_identity_decisions",
            DEFAULT_ACCEPTED_IDENTITY_DECISIONS,
        )
        blocking_identity_confidence_bands = _policy_string_set(
            curation_policy, "blocking_identity_confidence_bands", ()
        )
        return _Policy(
            curation_run_id=curation_run_id,
            curation_rule_version=curation_rule_version,
            bundle_scope=bundle_scope,
            accepted_quality_statuses=frozenset(accepted_statuses),
            blocking_flag_codes=frozenset(blocking_flags),
            duplicate_policy=duplicate_policy,
            produced_at=produced_at,
            requires_resolved_identity=requires_resolved_identity,
            blocking_identity_decisions=frozenset(blocking_identity_decisions),
            accepted_identity_decisions=frozenset(accepted_identity_decisions),
            blocking_identity_confidence_bands=frozenset(
                blocking_identity_confidence_bands
            ),
            raw=curation_policy,
        )

    def _candidate_refs(
        self, policy: _Policy, quality_records: Sequence[Mapping[str, Any]]
    ) -> list[str]:
        policy_candidates = policy.raw.get("candidate_refs")
        if policy_candidates is not None:
            return _dedupe_sorted(_required_string_sequence(policy_candidates))

        refs: list[str] = []
        for record in quality_records:
            if not isinstance(record, Mapping):
                raise CurationInputError(
                    code="CURATION_QUALITY_REF_MISSING",
                    message="quality_records must contain mapping objects",
                    field="quality_records",
                )
            subject_ref = _optional_string(record.get("subject_ref"))
            if subject_ref is not None:
                refs.append(subject_ref)
        return _dedupe_sorted(refs)

    def _index_quality_records(
        self, records: Sequence[Mapping[str, Any]]
    ) -> dict[str, list[Mapping[str, Any]]]:
        by_subject: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in records:
            if not isinstance(record, Mapping):
                raise CurationInputError(
                    code="CURATION_QUALITY_REF_MISSING",
                    message="quality_records must contain mapping objects",
                    field="quality_records",
                )
            subject_ref = _optional_string(record.get("subject_ref"))
            if subject_ref is not None:
                by_subject[subject_ref].append(record)
        return dict(by_subject)

    def _index_identity_records(
        self,
        records: Sequence[Mapping[str, Any]],
        candidate_refs: Sequence[str],
    ) -> dict[str, list[Mapping[str, Any]]]:
        candidate_set = set(candidate_refs)
        by_candidate: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for record in records:
            if not isinstance(record, Mapping):
                raise CurationInputError(
                    code="CURATION_IDENTITY_REF_MISSING",
                    message="identity_records must contain mapping objects",
                    field="identity_records",
                )
            refs = _identity_candidate_refs(record)
            for candidate_ref in sorted(candidate_set.intersection(refs)):
                by_candidate[candidate_ref].append(record)
        for candidate_ref in by_candidate:
            by_candidate[candidate_ref].sort(key=_identity_record_sort_key)
        return dict(by_candidate)

    def _assess_dedup_records(
        self,
        records: Sequence[Mapping[str, Any]],
        candidate_refs: Sequence[str],
        policy: _Policy,
    ) -> _DedupAssessment:
        candidate_set = set(candidate_refs)
        evidence_by_candidate: dict[str, list[str]] = defaultdict(list)
        suppressed_by_candidate: dict[str, list[str]] = defaultdict(list)
        invalid_by_candidate: dict[str, list[str]] = defaultdict(list)

        for record in records:
            if not isinstance(record, Mapping):
                raise CurationInputError(
                    code="CURATION_DEDUP_REF_INVALID",
                    message="dedup_records must contain mapping objects",
                    field="dedup_records",
                )

            record_ref = _dedup_record_ref(record)
            evidence_refs = _dedupe_sorted(
                [
                    *([record_ref] if record_ref else []),
                    *_string_refs(record.get("cluster_ref")),
                    *_string_refs(record.get("cluster_id")),
                    *_string_refs(record.get("rationale_refs")),
                    *_string_refs(record.get("evidence_refs")),
                ]
            )
            action_refs = _dedup_action_refs(record)
            unknown_action_refs = sorted(action_refs.difference(candidate_set))
            if unknown_action_refs:
                raise CurationInputError(
                    code="CURATION_DEDUP_REF_INVALID",
                    message="dedup recommendation references a candidate outside the curation candidate set",
                    field="dedup_records",
                    candidate_ref=unknown_action_refs[0],
                    details={"unknown_candidate_refs": unknown_action_refs},
                )

            participants = sorted(
                candidate_set.intersection(_dedup_participant_refs(record))
            )
            for candidate_ref in participants:
                evidence_by_candidate[candidate_ref].extend(evidence_refs)

            member_refs = _string_refs(record.get("member_refs")) or _string_refs(
                record.get("member_record_refs")
            )
            if not member_refs:
                member_refs = _string_refs(record.get("members")) or _string_refs(
                    record.get("cluster_members")
                )

            affected_refs = sorted(action_refs.intersection(candidate_set)) or participants
            has_cluster_ref = bool(
                _string_refs(record.get("cluster_ref"))
                or _string_refs(record.get("cluster_id"))
            )
            if has_cluster_ref and member_refs and len(set(member_refs)) < 2:
                for candidate_ref in affected_refs:
                    invalid_by_candidate[candidate_ref].extend(
                        evidence_refs or [candidate_ref]
                    )

            suppressed_refs = _dedup_suppressed_refs(record).intersection(candidate_set)
            if policy.duplicate_policy != "retain_all":
                for candidate_ref in sorted(suppressed_refs):
                    suppression_evidence = evidence_refs or [candidate_ref]
                    suppressed_by_candidate[candidate_ref].extend(suppression_evidence)
                    evidence_by_candidate[candidate_ref].extend(suppression_evidence)

        return _DedupAssessment(
            evidence_refs_by_candidate={
                key: _dedupe_sorted(value)
                for key, value in evidence_by_candidate.items()
            },
            suppressed_by_candidate={
                key: _dedupe_sorted(value)
                for key, value in suppressed_by_candidate.items()
            },
            invalid_by_candidate={
                key: _dedupe_sorted(value)
                for key, value in invalid_by_candidate.items()
            },
        )

    def _quality_for_candidate(
        self,
        candidate_ref: str,
        quality_by_subject: Mapping[str, Sequence[Mapping[str, Any]]],
        policy: _Policy,
    ) -> Mapping[str, Any] | CurationRejection:
        records = list(quality_by_subject.get(candidate_ref, []))
        if len(records) != 1:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                error_code="CURATION_QUALITY_REF_MISSING",
                blocking_evidence_refs=[candidate_ref, *[_quality_ref(item) for item in records]],
                policy=policy,
            )

        quality_record = records[0]
        quality_ref = _quality_ref(quality_record)
        if not self._quality_record_has_required_fields(quality_record):
            return self._build_rejection(
                candidate_ref=candidate_ref,
                error_code="CURATION_QUALITY_REF_MISSING",
                blocking_evidence_refs=[candidate_ref, quality_ref],
                policy=policy,
                quality_record=quality_record,
            )

        evaluation_status = _optional_string(
            quality_record.get("evaluation_status")
        )
        status_key = (evaluation_status or "").lower()
        flags = _quality_flags(quality_record)
        blocking_flags = sorted(set(flags).intersection(policy.blocking_flag_codes))
        disqualification_reason = quality_record.get("disqualification_reason")
        if (
            status_key in {"rejected", "disqualified"}
            or status_key not in policy.accepted_quality_statuses
            or blocking_flags
            or disqualification_reason
        ):
            evidence = [
                candidate_ref,
                quality_ref,
                *blocking_flags,
                *_string_refs(disqualification_reason),
            ]
            return self._build_rejection(
                candidate_ref=candidate_ref,
                error_code="CURATION_QUALITY_NOT_ELIGIBLE",
                blocking_evidence_refs=evidence,
                policy=policy,
                quality_record=quality_record,
            )
        return quality_record

    def _identity_for_candidate(
        self,
        candidate_ref: str,
        identity_by_candidate: Mapping[str, Sequence[Mapping[str, Any]]],
        policy: _Policy,
        quality_record: Mapping[str, Any],
    ) -> Mapping[str, Any] | CurationRejection:
        records = list(identity_by_candidate.get(candidate_ref, []))
        if not records:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                error_code="CURATION_IDENTITY_REF_MISSING",
                blocking_evidence_refs=[candidate_ref, _quality_ref(quality_record)],
                policy=policy,
                quality_record=quality_record,
            )

        missing_evidence: list[str] = []
        ambiguous_evidence: list[str] = []
        for record in records:
            identity_ref = _identity_ref(record)
            if not self._identity_record_has_required_fields(record):
                missing_evidence.extend([candidate_ref, identity_ref])
                continue

            decision = (_optional_string(record.get("decision")) or "").lower()
            confidence_band = (
                _optional_string(record.get("confidence_band")) or ""
            ).lower()
            if (
                decision in policy.blocking_identity_decisions
                or confidence_band in policy.blocking_identity_confidence_bands
                or (
                    policy.requires_resolved_identity
                    and decision not in policy.accepted_identity_decisions
                )
            ):
                ambiguous_evidence.extend(
                    [candidate_ref, identity_ref, *_string_refs(record.get("evidence_refs"))]
                )
                continue
            return record

        if ambiguous_evidence:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                error_code="CURATION_IDENTITY_AMBIGUOUS",
                blocking_evidence_refs=ambiguous_evidence,
                policy=policy,
                quality_record=quality_record,
                identity_record=records[0],
            )
        return self._build_rejection(
            candidate_ref=candidate_ref,
            error_code="CURATION_IDENTITY_REF_MISSING",
            blocking_evidence_refs=missing_evidence or [candidate_ref],
            policy=policy,
            quality_record=quality_record,
            identity_record=records[0],
        )

    def _quality_record_has_required_fields(self, record: Mapping[str, Any]) -> bool:
        required = (
            "quality_record_id",
            "subject_ref",
            "evaluation_status",
            "fitness_score",
            "phase_contract_ref",
            "evaluation_run_id",
        )
        if any(_optional_string(record.get(field)) is None for field in required if field != "fitness_score"):
            return False
        score = record.get("fitness_score")
        if isinstance(score, bool) or score is None:
            return False
        if isinstance(score, (int, float)):
            return True
        return isinstance(score, Mapping)

    def _identity_record_has_required_fields(self, record: Mapping[str, Any]) -> bool:
        if _optional_string(record.get("identity_record_id")) is None:
            return False
        if _optional_string(record.get("decision")) is None:
            return False
        if _optional_string(record.get("confidence_band")) is None:
            return False
        if _optional_string(record.get("rule_version")) is None:
            return False
        evidence_refs = record.get("evidence_refs")
        return bool(_required_list_of_strings_or_none(evidence_refs))

    def _build_library_object(
        self,
        *,
        candidate_ref: str,
        quality_record: Mapping[str, Any],
        identity_record: Mapping[str, Any],
        dedup_evidence_refs: Sequence[str],
        policy: _Policy,
    ) -> tuple[LibraryObject, LibraryVersion]:
        warning_refs = self._warning_refs(quality_record)
        evaluation_status = (
            _optional_string(quality_record.get("evaluation_status")) or ""
        ).lower()
        curation_status = (
            "included_with_warning"
            if warning_refs or evaluation_status == "conditional_pass"
            else "included"
        )
        provenance_refs = _dedupe_sorted(
            [
                _quality_ref(quality_record),
                _optional_string(quality_record.get("phase_contract_ref")),
                _optional_string(quality_record.get("evaluation_run_id")),
                *_string_refs(quality_record.get("provenance_refs")),
                _identity_ref(identity_record),
                *_string_refs(identity_record.get("evidence_refs")),
                *_string_refs(identity_record.get("provenance_refs")),
                *dedup_evidence_refs,
            ]
        )
        lineage_refs = _dedupe_sorted(
            [
                _optional_string(quality_record.get("phase_contract_ref")),
                _optional_string(quality_record.get("evaluation_run_id")),
                *_string_refs(quality_record.get("lineage_refs")),
                _optional_string(identity_record.get("rule_version")),
                *_string_refs(identity_record.get("lineage_refs")),
                *dedup_evidence_refs,
            ]
        )
        object_payload = {
            "source_object_ref": candidate_ref,
            "quality_record_ref": _quality_ref(quality_record),
            "identity_record_ref": _identity_ref(identity_record),
            "dedup_evidence_refs": _dedupe_sorted(dedup_evidence_refs),
            "curation_status": curation_status,
            "curation_rule_version": policy.curation_rule_version,
            "curation_run_id": policy.curation_run_id,
            "bundle_scope": policy.bundle_scope,
            "warning_refs": warning_refs,
            "provenance_refs": provenance_refs,
            "lineage_refs": lineage_refs,
        }
        library_object_id = _stable_id("lo", object_payload)
        version_hash = _hash_payload(object_payload)
        library_version = self._build_version(
            versioned_object_ref=library_object_id,
            versioned_object_type="library_object",
            content_fingerprint=version_hash,
            curation_rule_version=policy.curation_rule_version,
            source_ref=candidate_ref,
            lineage_refs=lineage_refs,
            produced_at=policy.produced_at,
            prior_version_ref=None,
            rebuild_manifest_ref=_optional_string(policy.raw.get("rebuild_manifest_ref")),
        )
        library_object = LibraryObject(
            library_object_id=library_object_id,
            source_object_ref=candidate_ref,
            quality_record_ref=_quality_ref(quality_record),
            identity_record_ref=_identity_ref(identity_record),
            dedup_evidence_refs=_dedupe_sorted(dedup_evidence_refs),
            curation_status=curation_status,
            curation_rule_version=policy.curation_rule_version,
            curation_run_id=policy.curation_run_id,
            bundle_scope=policy.bundle_scope,
            warning_refs=warning_refs,
            rejection_reason_ref=None,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            source_ref=candidate_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=policy.produced_at,
            parent_id=None,
            version_id=library_version.library_version_id,
            created_at=policy.produced_at,
            updated_at=policy.produced_at,
            version_hash=version_hash,
        )
        return library_object, library_version

    def _build_bundle(
        self,
        *,
        library_objects: Sequence[LibraryObject],
        rejections: Sequence[CurationRejection],
        policy: _Policy,
    ) -> tuple[CuratedBundle, LibraryVersion]:
        member_refs = sorted(item.library_object_id for item in library_objects)
        excluded_refs = sorted(item.candidate_ref for item in rejections)
        rejection_refs = sorted(item.curation_rejection_id for item in rejections)
        membership_fingerprint = _hash_payload(
            {
                "bundle_scope": policy.bundle_scope,
                "member_library_object_refs": member_refs,
                "excluded_candidate_refs": excluded_refs,
                "rejection_refs": rejection_refs,
                "selection_rule_version": policy.curation_rule_version,
            }
        )
        provenance_refs = _dedupe_sorted(
            [
                policy.curation_run_id,
                policy.bundle_scope,
                *[
                    ref
                    for item in library_objects
                    for ref in item.provenance_refs
                ],
                *[
                    ref
                    for item in rejections
                    for ref in item.blocking_evidence_refs
                ],
            ]
        )
        lineage_refs = _dedupe_sorted(
            [
                policy.curation_run_id,
                policy.curation_rule_version,
                policy.bundle_scope,
                *[ref for item in library_objects for ref in item.lineage_refs],
                *[
                    ref
                    for item in rejections
                    for ref in item.blocking_evidence_refs
                ],
            ]
        )
        bundle_payload = {
            "bundle_scope": policy.bundle_scope,
            "member_library_object_refs": member_refs,
            "excluded_candidate_refs": excluded_refs,
            "rejection_refs": rejection_refs,
            "selection_rule_version": policy.curation_rule_version,
            "curation_run_id": policy.curation_run_id,
            "membership_fingerprint": membership_fingerprint,
            "provenance_refs": provenance_refs,
            "lineage_refs": lineage_refs,
        }
        curated_bundle_id = _stable_id("cb", bundle_payload)
        version_hash = _hash_payload(bundle_payload)
        bundle_version = self._build_version(
            versioned_object_ref=curated_bundle_id,
            versioned_object_type="curated_bundle",
            content_fingerprint=version_hash,
            curation_rule_version=policy.curation_rule_version,
            source_ref=policy.bundle_scope,
            lineage_refs=lineage_refs,
            produced_at=policy.produced_at,
            prior_version_ref=None,
            rebuild_manifest_ref=_optional_string(policy.raw.get("rebuild_manifest_ref")),
        )
        curated_bundle = CuratedBundle(
            curated_bundle_id=curated_bundle_id,
            bundle_scope=policy.bundle_scope,
            member_library_object_refs=member_refs,
            excluded_candidate_refs=excluded_refs,
            rejection_refs=rejection_refs,
            selection_rule_version=policy.curation_rule_version,
            curation_run_id=policy.curation_run_id,
            membership_fingerprint=membership_fingerprint,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            source_ref=policy.bundle_scope,
            produced_by_motor=MOTOR_ID,
            produced_at=policy.produced_at,
            parent_id=None,
            version_id=bundle_version.library_version_id,
            created_at=policy.produced_at,
            updated_at=policy.produced_at,
            version_hash=version_hash,
        )
        return curated_bundle, bundle_version

    def _build_version(
        self,
        *,
        versioned_object_ref: str,
        versioned_object_type: str,
        content_fingerprint: str,
        curation_rule_version: str,
        source_ref: str,
        lineage_refs: Sequence[str],
        produced_at: str,
        prior_version_ref: Optional[str],
        rebuild_manifest_ref: Optional[str],
    ) -> LibraryVersion:
        version_payload = {
            "versioned_object_ref": versioned_object_ref,
            "versioned_object_type": versioned_object_type,
            "content_fingerprint": content_fingerprint,
            "prior_version_ref": prior_version_ref,
            "curation_rule_version": curation_rule_version,
            "source_ref": source_ref,
            "lineage_refs": _dedupe_sorted(lineage_refs),
        }
        library_version_id = _stable_id("lv", version_payload)
        version_hash = _hash_payload(version_payload)
        return LibraryVersion(
            library_version_id=library_version_id,
            version_id=library_version_id,
            versioned_object_ref=versioned_object_ref,
            versioned_object_type=versioned_object_type,
            content_fingerprint=content_fingerprint,
            version_hash=version_hash,
            prior_version_ref=prior_version_ref,
            curation_rule_version=curation_rule_version,
            rebuild_manifest_ref=rebuild_manifest_ref,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=prior_version_ref,
            lineage_refs=_dedupe_sorted(lineage_refs),
            created_at=produced_at,
            updated_at=produced_at,
        )

    def _build_rejection(
        self,
        *,
        candidate_ref: str,
        error_code: str,
        blocking_evidence_refs: Sequence[Optional[str]],
        policy: _Policy,
        quality_record: Optional[Mapping[str, Any]] = None,
        identity_record: Optional[Mapping[str, Any]] = None,
        dedup_evidence_refs: Sequence[str] = (),
    ) -> CurationRejection:
        quality_record_ref = _quality_ref(quality_record) if quality_record else None
        identity_record_ref = _identity_ref(identity_record) if identity_record else None
        blocking_refs = _dedupe_sorted(
            [
                candidate_ref,
                quality_record_ref,
                identity_record_ref,
                *blocking_evidence_refs,
                *dedup_evidence_refs,
            ]
        )
        rejection_id = _stable_id(
            "cr",
            {
                "candidate_ref": candidate_ref,
                "error_code": error_code,
                "curation_run_id": policy.curation_run_id,
                "blocking_evidence_refs": blocking_refs,
            },
        )
        payload = {
            "curation_rejection_id": rejection_id,
            "candidate_ref": candidate_ref,
            "error_code": error_code,
            "blocking_evidence_refs": blocking_refs,
            "quality_record_ref": quality_record_ref,
            "identity_record_ref": identity_record_ref,
            "dedup_evidence_refs": _dedupe_sorted(dedup_evidence_refs),
            "curation_run_id": policy.curation_run_id,
            "curation_rule_version": policy.curation_rule_version,
            "source_ref": candidate_ref,
        }
        return CurationRejection(
            curation_rejection_id=rejection_id,
            candidate_ref=candidate_ref,
            error_code=error_code,
            blocking_evidence_refs=blocking_refs,
            quality_record_ref=quality_record_ref,
            identity_record_ref=identity_record_ref,
            dedup_evidence_refs=_dedupe_sorted(dedup_evidence_refs),
            curation_run_id=policy.curation_run_id,
            curation_rule_version=policy.curation_rule_version,
            source_ref=candidate_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=policy.produced_at,
            parent_id=None,
            created_at=policy.produced_at,
            updated_at=policy.produced_at,
            version_hash=_hash_payload(payload),
        )

    def _warning_refs(self, quality_record: Mapping[str, Any]) -> list[str]:
        explicit_warning_refs = _string_refs(quality_record.get("warning_refs"))
        if explicit_warning_refs:
            return _dedupe_sorted(explicit_warning_refs)
        status = (_optional_string(quality_record.get("evaluation_status")) or "").lower()
        flags = _quality_flags(quality_record)
        if status == "conditional_pass" or flags:
            return _dedupe_sorted(flags)
        return []


def run_library_curation(**kwargs: Any) -> CurationResult:
    return LibraryCurationEngine().curate(**kwargs)


def _as_sequence(name: str, value: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if isinstance(value, (str, bytes)) or isinstance(value, Mapping):
        raise CurationInputError(
            code="CURATION_POLICY_BLOCKED",
            message=f"{name} must be an iterable of mapping objects",
            field=name,
        )
    return list(value)


def _required_policy_string(policy: Mapping[str, Any], field: str) -> str:
    value = _optional_string(policy.get(field))
    if value is None:
        raise CurationInputError(
            code="CURATION_POLICY_BLOCKED",
            message=f"curation_policy.{field} must be a non-empty string",
            field=f"curation_policy.{field}",
        )
    return value


def _policy_string_set(
    policy: Mapping[str, Any], field: str, default: Iterable[str]
) -> frozenset[str]:
    value = policy.get(field)
    if value is None:
        return frozenset(str(item).lower() for item in default)
    values = _required_string_sequence(value)
    return frozenset(item.lower() for item in values)


def _required_string_sequence(value: Any) -> list[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise CurationInputError(
            code="CURATION_POLICY_BLOCKED",
            message="expected a sequence of non-empty strings",
            field="curation_policy",
        )
    result: list[str] = []
    for item in value:
        string_item = _optional_string(item)
        if string_item is None:
            raise CurationInputError(
                code="CURATION_POLICY_BLOCKED",
                message="expected a sequence of non-empty strings",
                field="curation_policy",
            )
        result.append(string_item)
    return result


def _required_list_of_strings_or_none(value: Any) -> Optional[list[str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return None
    result: list[str] = []
    for item in value:
        text = _optional_string(item)
        if text is None:
            return None
        result.append(text)
    return result


def _optional_string(value: Any) -> Optional[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _string_refs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        refs: list[str] = []
        for item in value:
            text = _optional_string(item)
            if text is not None:
                refs.append(text)
        return refs
    return []


def _quality_flags(record: Mapping[str, Any]) -> list[str]:
    flags = record.get("quality_flags", [])
    if flags is None:
        return []
    if not isinstance(flags, Sequence) or isinstance(flags, (str, bytes)):
        return ["invalid_quality_flags"]
    return _dedupe_sorted(
        flag for flag in (_optional_string(item) for item in flags) if flag is not None
    )


def _identity_candidate_refs(record: Mapping[str, Any]) -> set[str]:
    refs: set[str] = set()
    for field in (
        "evaluated_record_ids",
        "evaluated_record_refs",
        "source_object_refs",
        "candidate_refs",
    ):
        refs.update(_string_refs(record.get(field)))
    for field in ("source_object_ref", "subject_ref", "candidate_ref", "record_ref"):
        refs.update(_string_refs(record.get(field)))
    return refs


def _dedup_record_ref(record: Mapping[str, Any]) -> Optional[str]:
    for field in (
        "dedup_record_id",
        "dedup_decision_id",
        "decision_id",
        "duplicate_cluster_id",
        "cluster_id",
        "similarity_id",
        "record_id",
        "id",
    ):
        ref = _optional_string(record.get(field))
        if ref is not None:
            return ref
    cluster_ref = _optional_string(record.get("cluster_ref"))
    if cluster_ref is not None:
        return cluster_ref
    return None


def _dedup_participant_refs(record: Mapping[str, Any]) -> set[str]:
    refs = set(_dedup_action_refs(record))
    for field in (
        "member_refs",
        "member_record_refs",
        "members",
        "cluster_members",
        "candidate_refs",
        "target_record_refs",
        "target_refs",
    ):
        refs.update(_string_refs(record.get(field)))
    return refs


def _dedup_action_refs(record: Mapping[str, Any]) -> set[str]:
    refs: set[str] = set()
    for field in (
        "candidate_ref",
        "source_object_ref",
        "representative_ref",
        "retain_representative",
        "suppressed_candidate_ref",
        "suppress_duplicate",
    ):
        refs.update(_string_refs(record.get(field)))
    for field in (
        "candidate_refs",
        "target_record_refs",
        "target_refs",
        "suppressed_candidate_refs",
        "suppress_duplicate_refs",
    ):
        refs.update(_string_refs(record.get(field)))
    return refs


def _dedup_suppressed_refs(record: Mapping[str, Any]) -> set[str]:
    refs: set[str] = set()
    for field in (
        "suppressed_candidate_ref",
        "suppress_duplicate",
        "suppressed_ref",
    ):
        refs.update(_string_refs(record.get(field)))
    for field in ("suppressed_candidate_refs", "suppress_duplicate_refs"):
        refs.update(_string_refs(record.get(field)))

    recommendation = (_optional_string(record.get("recommendation")) or "").lower()
    if recommendation in {
        "suppress",
        "suppress_duplicate",
        "exclude_duplicate",
        "excluded_duplicate",
        "suppress_candidate",
    }:
        refs.update(_string_refs(record.get("candidate_ref")))
        refs.update(_string_refs(record.get("target_record_refs")))
        refs.update(_string_refs(record.get("target_refs")))
    return refs


def _identity_record_sort_key(record: Mapping[str, Any]) -> str:
    return _identity_ref(record) or _hash_payload(record)


def _quality_ref(record: Optional[Mapping[str, Any]]) -> Optional[str]:
    if not record:
        return None
    return _optional_string(record.get("quality_record_id"))


def _identity_ref(record: Optional[Mapping[str, Any]]) -> Optional[str]:
    if not record:
        return None
    return _optional_string(record.get("identity_record_id"))


def _dedupe_sorted(values: Iterable[Optional[str]]) -> list[str]:
    return sorted({value for value in values if isinstance(value, str) and value.strip()})


def _stable_id(prefix: str, payload: Any) -> str:
    return f"{prefix}_{_hash_payload(payload)[:20]}"


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
