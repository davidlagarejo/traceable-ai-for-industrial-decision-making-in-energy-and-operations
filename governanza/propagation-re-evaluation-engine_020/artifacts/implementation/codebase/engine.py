"""Deterministic implementation for motor_020.

The engine treats upstream records as immutable input dictionaries and emits
only re-evaluation jobs, stale markers, and propagation audit records.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from .models import PropagationRecord, ReEvaluationJob, StaleObject


MOTOR_ID = "motor_020"
DEFAULT_RULE_VERSION = "prop-rules-020.1.0"
DEFAULT_EVALUATED_AT = "1970-01-01T00:00:00Z"
VALID_TRIGGER_TYPES = {"version_record", "quality_record", "change_event"}
VALID_DECISIONS = {
    "jobs_emitted",
    "no_affected_objects",
    "blocked_untraceable",
    "rejected_invalid_input",
    "deduplicated",
}


class PropagationReEvaluationEngine:
    """Compute stale downstream targets and queued re-evaluation jobs."""

    produced_by_motor = MOTOR_ID

    def run(
        self,
        *,
        version_records: Sequence[Mapping[str, Any]],
        quality_records: Sequence[Mapping[str, Any]],
        change_events: Sequence[Mapping[str, Any]],
        evaluated_at: str | None = None,
        rule_version: str = DEFAULT_RULE_VERSION,
    ) -> dict[str, list[dict[str, Any]]]:
        """Return motor_020 outputs for a batch of upstream signals.

        The method is deterministic: identifiers, hashes, timestamps, ordering,
        deduplication, and rejection records are derived from the supplied
        inputs and the rule version.
        """

        if not self._is_record_collection(version_records):
            return self._batch_rejection(
                reason="version_records must be a list-like collection.",
                rejected_ref="version_records",
                evaluated_at=evaluated_at,
                rule_version=rule_version,
            )
        if not self._is_record_collection(quality_records):
            return self._batch_rejection(
                reason="quality_records must be a list-like collection.",
                rejected_ref="quality_records",
                evaluated_at=evaluated_at,
                rule_version=rule_version,
            )
        if not self._is_record_collection(change_events):
            return self._batch_rejection(
                reason="change_events must be a list-like collection.",
                rejected_ref="change_events",
                evaluated_at=evaluated_at,
                rule_version=rule_version,
            )
        if not version_records and not quality_records and not change_events:
            return self._batch_rejection(
                reason="At least one input collection must contain a trigger.",
                rejected_ref="empty_batch",
                evaluated_at=evaluated_at,
                rule_version=rule_version,
            )

        version_items = [copy.deepcopy(dict(item)) for item in version_records]
        quality_items = [copy.deepcopy(dict(item)) for item in quality_records]
        change_items = [copy.deepcopy(dict(item)) for item in change_events]

        valid_versions, rejected_versions = self._validate_records(
            version_items, "version_record"
        )
        valid_qualities, rejected_qualities = self._validate_records(
            quality_items, "quality_record"
        )
        valid_changes, rejected_changes = self._validate_records(
            change_items, "change_event"
        )

        produced_at = self._deterministic_evaluated_at(
            evaluated_at,
            [*valid_versions, *valid_qualities, *valid_changes],
        )

        output_jobs: list[ReEvaluationJob] = []
        output_stale: list[StaleObject] = []
        output_records: list[PropagationRecord] = []

        for rejected in [*rejected_versions, *rejected_qualities, *rejected_changes]:
            output_records.append(
                self._rejection_record(
                    trigger_ref=rejected["ref"],
                    trigger_type=rejected["trigger_type"],
                    rejected_input_refs=[rejected["ref"]],
                    message=rejected["message"],
                    produced_at=produced_at,
                    rule_version=rule_version,
                )
            )

        triggers = self._select_triggers(valid_changes, valid_versions, valid_qualities)
        if not triggers and not output_records:
            output_records.append(
                self._rejection_record(
                    trigger_ref="NO_VALID_TRIGGER",
                    trigger_type="invalid_batch",
                    rejected_input_refs=["empty_valid_trigger_set"],
                    message="No valid version_record, quality_record, or change_event was available.",
                    produced_at=produced_at,
                    rule_version=rule_version,
                )
            )

        seen_jobs: set[tuple[str, str, str, str]] = set()
        for trigger_type, trigger in triggers:
            records, stale_items, jobs = self._process_trigger(
                trigger=trigger,
                trigger_type=trigger_type,
                version_records=valid_versions,
                quality_records=valid_qualities,
                change_events=valid_changes,
                produced_at=produced_at,
                rule_version=rule_version,
                seen_jobs=seen_jobs,
            )
            output_records.extend(records)
            output_stale.extend(stale_items)
            output_jobs.extend(jobs)

        return {
            "re_evaluation_job": [item.to_dict() for item in output_jobs],
            "stale_set": [item.to_dict() for item in output_stale],
            "propagation_log": [item.to_dict() for item in output_records],
        }

    def _process_trigger(
        self,
        *,
        trigger: Mapping[str, Any],
        trigger_type: str,
        version_records: list[dict[str, Any]],
        quality_records: list[dict[str, Any]],
        change_events: list[dict[str, Any]],
        produced_at: str,
        rule_version: str,
        seen_jobs: set[tuple[str, str, str, str]],
    ) -> tuple[list[PropagationRecord], list[StaleObject], list[ReEvaluationJob]]:
        trigger_ref = self._primary_ref(trigger, trigger_type)
        trigger_timestamp = self._trigger_timestamp(trigger, trigger_type)
        source_ref = self._source_ref(trigger, trigger_type)
        parent_id = self._string_or_none(trigger.get("parent_id"))
        context_versions = self._linked_versions(trigger, trigger_type, version_records)
        context_qualities = self._linked_qualities(
            trigger,
            trigger_type,
            quality_records,
            context_versions,
        )
        input_refs = self._input_refs_for_context(
            trigger_ref,
            context_versions,
            context_qualities,
        )
        candidates = self._candidate_targets(
            trigger=trigger,
            trigger_type=trigger_type,
            context_versions=context_versions,
            context_qualities=context_qualities,
            input_refs=input_refs,
        )

        record_id = self._propagation_record_id(
            trigger_ref=trigger_ref,
            input_refs=input_refs,
            affected_refs=[candidate.get("target_object_ref") for candidate in candidates],
            rule_version=rule_version,
        )

        secondary_decisions: list[str] = []
        rejected_refs: list[str] = []
        emitted_job_ids: list[str] = []
        stale_object_ids: list[str] = []
        affected_object_refs: list[str] = []
        dependency_paths: list[list[str]] = []
        stale_items: list[StaleObject] = []
        jobs: list[ReEvaluationJob] = []
        error_code: str | None = None

        for candidate in sorted(
            candidates,
            key=lambda item: (
                str(item.get("target_object_ref") or ""),
                str(item.get("target_version_ref") or ""),
                "|".join(item.get("dependency_path") or []),
            ),
        ):
            target_ref = self._string_or_none(candidate.get("target_object_ref"))
            target_version_ref = self._string_or_none(candidate.get("target_version_ref"))
            dependency_path = self._dedupe_strings(candidate.get("dependency_path") or [])
            evidence_refs = self._dedupe_strings(candidate.get("evidence_refs") or [])
            lineage_refs = self._dedupe_strings(candidate.get("lineage_refs") or [])

            if not target_ref or not dependency_path:
                secondary_decisions = self._append_once(
                    secondary_decisions, "blocked_untraceable"
                )
                rejected_refs = self._append_once(rejected_refs, target_ref or trigger_ref)
                error_code = error_code or "UNTRACEABLE_PROPAGATION_PATH"
                continue
            if candidate.get("traceable") is False:
                secondary_decisions = self._append_once(
                    secondary_decisions, "blocked_untraceable"
                )
                rejected_refs = self._append_once(rejected_refs, target_ref)
                error_code = error_code or "UNTRACEABLE_PROPAGATION_PATH"
                continue
            if not evidence_refs:
                secondary_decisions = self._append_once(
                    secondary_decisions, "unsafe_job_blocked"
                )
                rejected_refs = self._append_once(rejected_refs, target_ref)
                error_code = "UNSAFE_REEVALUATION_JOB"
                continue

            dedupe_key = (
                trigger_ref,
                target_ref,
                target_version_ref or "",
                rule_version,
            )
            if dedupe_key in seen_jobs:
                secondary_decisions = self._append_once(
                    secondary_decisions, "deduplicated"
                )
                continue
            seen_jobs.add(dedupe_key)

            job_id = self._job_id(
                trigger_ref=trigger_ref,
                target_ref=target_ref,
                target_version_ref=target_version_ref,
                rule_version=rule_version,
            )
            stale_object_id = self._stale_object_id(
                trigger_ref=trigger_ref,
                target_ref=target_ref,
                target_version_ref=target_version_ref,
                rule_version=rule_version,
            )

            stale = self._build_stale_object(
                stale_object_id=stale_object_id,
                object_ref=target_ref,
                version_ref=target_version_ref,
                stale_reason=str(candidate["stale_reason"]),
                trigger_ref=trigger_ref,
                trigger_type=trigger_type,
                lineage_refs=lineage_refs,
                dependency_path=dependency_path,
                severity=str(candidate["severity"]),
                detected_at=trigger_timestamp,
                propagation_record_id=record_id,
                job_id=job_id,
                source_ref=source_ref,
                produced_at=produced_at,
                parent_id=parent_id,
            )
            job = self._build_job(
                job_id=job_id,
                target_object_ref=target_ref,
                target_version_ref=target_version_ref,
                trigger_ref=trigger_ref,
                trigger_type=trigger_type,
                reason_code=str(candidate["reason_code"]),
                priority=str(candidate["priority"]),
                dependency_path=dependency_path,
                input_refs=input_refs,
                evidence_refs=evidence_refs,
                propagation_record_id=record_id,
                stale_object_id=stale_object_id,
                source_ref=source_ref,
                produced_at=produced_at,
                parent_id=parent_id,
                rule_version=rule_version,
            )

            stale_items.append(stale)
            jobs.append(job)
            emitted_job_ids.append(job.job_id)
            stale_object_ids.append(stale.stale_object_id)
            affected_object_refs = self._append_once(affected_object_refs, target_ref)
            dependency_paths.append(dependency_path)

        if emitted_job_ids:
            decision = "jobs_emitted"
        elif "deduplicated" in secondary_decisions:
            decision = "deduplicated"
        elif "blocked_untraceable" in secondary_decisions or "unsafe_job_blocked" in secondary_decisions:
            decision = "blocked_untraceable"
        else:
            decision = "no_affected_objects"

        record = self._build_propagation_record(
            propagation_record_id=record_id,
            input_refs=input_refs,
            trigger_ref=trigger_ref,
            trigger_type=trigger_type,
            affected_object_refs=affected_object_refs,
            emitted_job_ids=emitted_job_ids,
            stale_object_ids=stale_object_ids,
            rejected_input_refs=rejected_refs,
            dependency_paths=dependency_paths,
            decision=decision,
            secondary_decisions=secondary_decisions,
            error_code=error_code,
            source_ref=source_ref,
            produced_at=produced_at,
            parent_id=parent_id,
            rule_version=rule_version,
        )

        return [record], stale_items, jobs

    def _validate_records(
        self, records: list[dict[str, Any]], trigger_type: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        valid: list[dict[str, Any]] = []
        rejected: list[dict[str, str]] = []
        for index, record in enumerate(records):
            ref = self._primary_ref(record, trigger_type) or f"{trigger_type}:{index}"
            message = self._validation_error(record, trigger_type)
            if message:
                rejected.append(
                    {
                        "ref": ref,
                        "trigger_type": trigger_type,
                        "message": message,
                    }
                )
            else:
                valid.append(record)
        return valid, rejected

    def _validation_error(self, record: Mapping[str, Any], trigger_type: str) -> str | None:
        if trigger_type == "version_record":
            missing = self._missing_fields(
                record,
                ["version_id", "object_id", "object_type", "mutation_type", "created_at"],
            )
            if missing:
                return f"VersionRecord is missing required fields: {', '.join(missing)}."
            if not self._timestamp_parseable(record.get("created_at")):
                return "VersionRecord.created_at is not parseable."
            if not self._has_any_ref(
                record,
                [
                    "lineage_refs",
                    "dependency_edges",
                    "impact_set",
                    "affected_dependencies",
                    "provenance_refs",
                    "evidence_refs",
                    "prior_version_ref",
                    "previous_version_ref",
                ],
            ):
                return "VersionRecord has no lineage, dependency, impact, provenance, or prior-version reference."
            return None

        if trigger_type == "quality_record":
            missing = self._missing_fields(
                record,
                ["quality_record_id", "subject_ref", "evaluation_status", "evaluated_at"],
            )
            if missing:
                return f"QualityRecord is missing required fields: {', '.join(missing)}."
            if not self._timestamp_parseable(record.get("evaluated_at")):
                return "QualityRecord.evaluated_at is not parseable."
            return None

        if trigger_type == "change_event":
            missing = self._missing_fields(
                record,
                ["event_id", "source_id", "change_type", "severity", "detected_at"],
            )
            if missing:
                return f"ChangeEvent is missing required fields: {', '.join(missing)}."
            if not self._timestamp_parseable(record.get("detected_at")):
                return "ChangeEvent.detected_at is not parseable."
            if not self._has_any_ref(record, ["evidence_refs", "lineage_refs", "impact_set"]):
                return "ChangeEvent has no evidence, lineage, or impact reference."
            return None

        return "Unknown trigger type."

    def _select_triggers(
        self,
        valid_changes: list[dict[str, Any]],
        valid_versions: list[dict[str, Any]],
        valid_qualities: list[dict[str, Any]],
    ) -> list[tuple[str, dict[str, Any]]]:
        if valid_changes:
            return [("change_event", item) for item in self._sort_by_ref(valid_changes, "event_id")]
        if valid_versions:
            return [
                ("version_record", item)
                for item in self._sort_by_ref(valid_versions, "version_id")
            ]
        return [
            ("quality_record", item)
            for item in self._sort_by_ref(valid_qualities, "quality_record_id")
            if self._quality_requires_propagation(item)
        ]

    def _linked_versions(
        self,
        trigger: Mapping[str, Any],
        trigger_type: str,
        version_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if trigger_type == "version_record":
            return [dict(trigger)]
        linked = []
        for version in version_records:
            if trigger_type == "change_event" and self._change_links_version(trigger, version):
                linked.append(version)
            elif trigger_type == "quality_record" and self._quality_links_version(trigger, version):
                linked.append(version)
        return self._sort_by_ref(linked, "version_id")

    def _linked_qualities(
        self,
        trigger: Mapping[str, Any],
        trigger_type: str,
        quality_records: list[dict[str, Any]],
        context_versions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if trigger_type == "quality_record":
            return [dict(trigger)]

        impacted = set()
        for version in context_versions:
            impacted.update(self._target_refs_from_record(version))

        linked = []
        for quality in quality_records:
            subject_ref = self._string_or_none(quality.get("subject_ref"))
            if subject_ref and subject_ref in impacted:
                linked.append(quality)
                continue
            if trigger_type == "change_event" and self._change_links_quality(trigger, quality):
                linked.append(quality)
                continue
            if any(self._quality_links_version(quality, version) for version in context_versions):
                linked.append(quality)
        return self._sort_by_ref(linked, "quality_record_id")

    def _candidate_targets(
        self,
        *,
        trigger: Mapping[str, Any],
        trigger_type: str,
        context_versions: list[dict[str, Any]],
        context_qualities: list[dict[str, Any]],
        input_refs: list[str],
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        reason_code = self._reason_code(trigger, trigger_type)
        stale_reason = self._stale_reason(reason_code)
        severity = self._severity(trigger, trigger_type)
        priority = self._priority(trigger, trigger_type, severity, dependency_depth=1)

        if trigger_type == "quality_record" and self._quality_requires_propagation(trigger):
            target_ref = self._string_or_none(trigger.get("subject_ref"))
            candidates.append(
                self._candidate(
                    target_ref=target_ref,
                    target_version_ref=self._version_ref_for_quality(trigger),
                    trigger=trigger,
                    context_version=None,
                    context_quality=trigger,
                    reason_code=reason_code,
                    stale_reason=stale_reason,
                    severity=severity,
                    priority=priority,
                    input_refs=input_refs,
                )
            )

        for version in context_versions:
            for target in self._targets_from_version(version):
                candidate = self._candidate(
                    target_ref=target["target_object_ref"],
                    target_version_ref=target.get("target_version_ref"),
                    trigger=trigger,
                    context_version=version,
                    context_quality=self._quality_for_target(
                        target.get("target_object_ref"),
                        context_qualities,
                    ),
                    reason_code=reason_code,
                    stale_reason=stale_reason,
                    severity=severity,
                    priority=self._priority(
                        trigger,
                        trigger_type,
                        severity,
                        dependency_depth=len(target.get("dependency_path") or []),
                    ),
                    input_refs=input_refs,
                    extra_path=target.get("dependency_path"),
                    extra_lineage=target.get("lineage_refs"),
                    extra_evidence=target.get("evidence_refs"),
                    traceable=target.get("traceable", True),
                )
                candidates.append(candidate)

        if trigger_type == "change_event":
            for target in self._targets_from_change_event(trigger):
                candidates.append(
                    self._candidate(
                        target_ref=target["target_object_ref"],
                        target_version_ref=target.get("target_version_ref"),
                        trigger=trigger,
                        context_version=None,
                        context_quality=self._quality_for_target(
                            target.get("target_object_ref"),
                            context_qualities,
                        ),
                        reason_code=reason_code,
                        stale_reason=stale_reason,
                        severity=severity,
                        priority=priority,
                        input_refs=input_refs,
                        extra_path=target.get("dependency_path"),
                        extra_lineage=target.get("lineage_refs"),
                        extra_evidence=target.get("evidence_refs"),
                        traceable=target.get("traceable", True),
                    )
                )

        if trigger_type == "change_event" and not candidates:
            for quality in context_qualities:
                if self._quality_requires_propagation(quality):
                    candidates.append(
                        self._candidate(
                            target_ref=self._string_or_none(quality.get("subject_ref")),
                            target_version_ref=self._version_ref_for_quality(quality),
                            trigger=trigger,
                            context_version=None,
                            context_quality=quality,
                            reason_code=reason_code,
                            stale_reason=stale_reason,
                            severity=severity,
                            priority=priority,
                            input_refs=input_refs,
                        )
                    )

        return self._dedupe_candidates(candidates)

    def _candidate(
        self,
        *,
        target_ref: str | None,
        target_version_ref: str | None = None,
        trigger: Mapping[str, Any],
        context_version: Mapping[str, Any] | None,
        context_quality: Mapping[str, Any] | None,
        reason_code: str,
        stale_reason: str,
        severity: str,
        priority: str,
        input_refs: list[str],
        extra_path: Iterable[Any] | None = None,
        extra_lineage: Iterable[Any] | None = None,
        extra_evidence: Iterable[Any] | None = None,
        traceable: bool = True,
    ) -> dict[str, Any]:
        trigger_type = self._infer_trigger_type(trigger)
        path_parts: list[Any] = [self._primary_ref(trigger, trigger_type)]
        if trigger.get("source_id"):
            path_parts.append(trigger.get("source_id"))
        path_parts.extend(self._list_values(trigger.get("lineage_refs")))
        if context_version is not None:
            path_parts.append(context_version.get("version_id"))
            path_parts.append(context_version.get("object_id") or context_version.get("object_ref"))
            path_parts.extend(self._list_values(context_version.get("lineage_refs")))
        if context_quality is not None:
            path_parts.append(context_quality.get("quality_record_id"))
            path_parts.append(context_quality.get("subject_ref"))
            path_parts.extend(self._list_values(context_quality.get("lineage_refs")))
        path_parts.extend(self._list_values(extra_path))
        if target_ref:
            path_parts.append(target_ref)

        evidence_refs: list[Any] = []
        evidence_refs.extend(self._evidence_refs(trigger))
        if context_version is not None:
            evidence_refs.extend(self._evidence_refs(context_version))
        if context_quality is not None:
            evidence_refs.extend(self._evidence_refs(context_quality))
        evidence_refs.extend(self._list_values(extra_evidence))
        evidence_refs.extend(input_refs)

        lineage_refs: list[Any] = []
        lineage_refs.extend(self._list_values(trigger.get("lineage_refs")))
        if context_version is not None:
            lineage_refs.extend(self._list_values(context_version.get("lineage_refs")))
        if context_quality is not None:
            lineage_refs.extend(self._list_values(context_quality.get("lineage_refs")))
        lineage_refs.extend(self._list_values(extra_lineage))

        return {
            "target_object_ref": target_ref,
            "target_version_ref": target_version_ref,
            "dependency_path": self._dedupe_strings(path_parts),
            "evidence_refs": self._dedupe_strings(evidence_refs),
            "lineage_refs": self._dedupe_strings(lineage_refs),
            "reason_code": reason_code,
            "stale_reason": stale_reason,
            "severity": severity,
            "priority": priority,
            "traceable": traceable,
        }

    def _targets_from_version(self, version: Mapping[str, Any]) -> list[dict[str, Any]]:
        targets: list[dict[str, Any]] = []
        for field in ("impact_set", "affected_dependencies"):
            for target in self._raw_items(version.get(field)):
                targets.append(self._normalize_target(target, version))
        for edge in self._raw_items(version.get("dependency_edges")):
            targets.append(self._normalize_target(edge, version))
        return [target for target in targets if target.get("target_object_ref")]

    def _targets_from_change_event(self, event: Mapping[str, Any]) -> list[dict[str, Any]]:
        targets = []
        for target in self._raw_items(event.get("impact_set")):
            normalized = self._normalize_target(target, event)
            if normalized.get("target_object_ref"):
                targets.append(normalized)
        return targets

    def _normalize_target(
        self, target: Any, source_record: Mapping[str, Any]
    ) -> dict[str, Any]:
        if isinstance(target, Mapping):
            target_ref = self._first_string(
                target,
                [
                    "target_object_ref",
                    "object_ref",
                    "target_ref",
                    "downstream_ref",
                    "object_id",
                    "subject_ref",
                ],
            )
            target_version_ref = self._first_string(
                target,
                ["target_version_ref", "version_ref", "subject_version_ref"],
            )
            return {
                "target_object_ref": target_ref,
                "target_version_ref": target_version_ref,
                "dependency_path": self._list_values(target.get("dependency_path")),
                "lineage_refs": self._list_values(target.get("lineage_refs")),
                "evidence_refs": self._list_values(target.get("evidence_refs")),
                "traceable": bool(target.get("traceable", True)),
            }
        target_ref = self._string_or_none(target)
        return {
            "target_object_ref": target_ref,
            "target_version_ref": None,
            "dependency_path": [
                source_record.get("version_id") or source_record.get("event_id"),
                target_ref,
            ],
            "lineage_refs": self._list_values(source_record.get("lineage_refs")),
            "evidence_refs": self._evidence_refs(source_record),
            "traceable": True,
        }

    def _build_job(self, **fields: Any) -> ReEvaluationJob:
        base = {
            "job_id": fields["job_id"],
            "target_object_ref": fields["target_object_ref"],
            "target_version_ref": fields["target_version_ref"],
            "trigger_ref": fields["trigger_ref"],
            "trigger_type": fields["trigger_type"],
            "reason_code": fields["reason_code"],
            "priority": fields["priority"],
            "dependency_path": fields["dependency_path"],
            "input_refs": fields["input_refs"],
            "evidence_refs": fields["evidence_refs"],
            "propagation_record_id": fields["propagation_record_id"],
            "stale_object_id": fields["stale_object_id"],
            "status": "queued",
            "blocking_reason": None,
            "propagation_rule_version": fields["rule_version"],
            "version_id": f"{fields['job_id']}:v1",
            "created_at": fields["produced_at"],
            "updated_at": fields["produced_at"],
            "version_hash": "",
            "source_ref": fields["source_ref"],
            "produced_by_motor": MOTOR_ID,
            "produced_at": fields["produced_at"],
            "parent_id": fields["parent_id"],
        }
        base["version_hash"] = self._version_hash(base)
        return ReEvaluationJob(**base)

    def _build_stale_object(self, **fields: Any) -> StaleObject:
        base = {
            "stale_object_id": fields["stale_object_id"],
            "object_ref": fields["object_ref"],
            "version_ref": fields["version_ref"],
            "stale_reason": fields["stale_reason"],
            "trigger_ref": fields["trigger_ref"],
            "trigger_type": fields["trigger_type"],
            "lineage_refs": fields["lineage_refs"],
            "dependency_path": fields["dependency_path"],
            "severity": fields["severity"],
            "detected_at": fields["detected_at"],
            "propagation_record_id": fields["propagation_record_id"],
            "job_id": fields["job_id"],
            "version_id": f"{fields['stale_object_id']}:v1",
            "created_at": fields["produced_at"],
            "updated_at": fields["produced_at"],
            "version_hash": "",
            "source_ref": fields["source_ref"],
            "produced_by_motor": MOTOR_ID,
            "produced_at": fields["produced_at"],
            "parent_id": fields["parent_id"],
        }
        base["version_hash"] = self._version_hash(base)
        return StaleObject(**base)

    def _build_propagation_record(self, **fields: Any) -> PropagationRecord:
        stale_set_ref = (
            f"stale-set:{fields['propagation_record_id']}"
            if fields["stale_object_ids"]
            else None
        )
        base = {
            "propagation_record_id": fields["propagation_record_id"],
            "input_refs": fields["input_refs"],
            "trigger_ref": fields["trigger_ref"],
            "trigger_type": fields["trigger_type"],
            "affected_object_refs": fields["affected_object_refs"],
            "emitted_job_ids": fields["emitted_job_ids"],
            "stale_object_ids": fields["stale_object_ids"],
            "stale_set_ref": stale_set_ref,
            "rejected_input_refs": fields["rejected_input_refs"],
            "dependency_paths": fields["dependency_paths"],
            "decision": fields["decision"],
            "secondary_decisions": fields["secondary_decisions"],
            "error_code": fields["error_code"],
            "rule_version": fields["rule_version"],
            "evaluated_at": fields["produced_at"],
            "version_id": f"{fields['propagation_record_id']}:v1",
            "created_at": fields["produced_at"],
            "updated_at": fields["produced_at"],
            "version_hash": "",
            "source_ref": fields["source_ref"],
            "produced_by_motor": MOTOR_ID,
            "produced_at": fields["produced_at"],
            "parent_id": fields["parent_id"],
        }
        base["version_hash"] = self._version_hash(base)
        return PropagationRecord(**base)

    def _rejection_record(
        self,
        *,
        trigger_ref: str,
        trigger_type: str,
        rejected_input_refs: list[str],
        message: str,
        produced_at: str,
        rule_version: str,
    ) -> PropagationRecord:
        record_id = self._stable_id(
            "propagation",
            [trigger_ref, trigger_type, rejected_input_refs, message, rule_version],
        )
        return self._build_propagation_record(
            propagation_record_id=record_id,
            input_refs=[],
            trigger_ref=trigger_ref,
            trigger_type=trigger_type,
            affected_object_refs=[],
            emitted_job_ids=[],
            stale_object_ids=[],
            rejected_input_refs=rejected_input_refs,
            dependency_paths=[],
            decision="rejected_invalid_input",
            secondary_decisions=[],
            error_code="INVALID_PROPAGATION_INPUT",
            source_ref=trigger_ref,
            produced_at=produced_at,
            parent_id=None,
            rule_version=rule_version,
        )

    def _batch_rejection(
        self,
        *,
        reason: str,
        rejected_ref: str,
        evaluated_at: str | None,
        rule_version: str,
    ) -> dict[str, list[dict[str, Any]]]:
        produced_at = self._deterministic_evaluated_at(evaluated_at, [])
        record = self._rejection_record(
            trigger_ref="INVALID_BATCH",
            trigger_type="invalid_batch",
            rejected_input_refs=[rejected_ref],
            message=reason,
            produced_at=produced_at,
            rule_version=rule_version,
        )
        return {
            "re_evaluation_job": [],
            "stale_set": [],
            "propagation_log": [record.to_dict()],
        }

    def _input_refs_for_context(
        self,
        trigger_ref: str,
        versions: list[dict[str, Any]],
        qualities: list[dict[str, Any]],
    ) -> list[str]:
        refs: list[Any] = [trigger_ref]
        refs.extend(version.get("version_id") for version in versions)
        refs.extend(quality.get("quality_record_id") for quality in qualities)
        return self._dedupe_strings(refs)

    def _quality_for_target(
        self, target_ref: Any, quality_records: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        target = self._string_or_none(target_ref)
        if target is None:
            return None
        for quality in quality_records:
            if self._string_or_none(quality.get("subject_ref")) == target:
                return quality
        return None

    def _change_links_version(
        self, change: Mapping[str, Any], version: Mapping[str, Any]
    ) -> bool:
        source_id = self._string_or_none(change.get("source_id"))
        version_source_refs = self._dedupe_strings(
            [
                version.get("source_id"),
                version.get("source_ref"),
                version.get("object_id"),
                version.get("object_ref"),
            ]
        )
        if source_id and source_id in version_source_refs:
            return True
        if self._intersects(change.get("lineage_refs"), version.get("lineage_refs")):
            return True
        if self._intersects(change.get("evidence_refs"), version.get("provenance_refs")):
            return True
        if self._intersects(change.get("evidence_refs"), version.get("evidence_refs")):
            return True
        return False

    def _change_links_quality(
        self, change: Mapping[str, Any], quality: Mapping[str, Any]
    ) -> bool:
        if self._intersects(change.get("lineage_refs"), quality.get("lineage_refs")):
            return True
        if self._intersects(change.get("evidence_refs"), quality.get("evidence_refs")):
            return True
        return False

    def _quality_links_version(
        self, quality: Mapping[str, Any], version: Mapping[str, Any]
    ) -> bool:
        subject_ref = self._string_or_none(quality.get("subject_ref"))
        if subject_ref and subject_ref in self._target_refs_from_record(version):
            return True
        if subject_ref and subject_ref == self._string_or_none(version.get("object_id")):
            return True
        if self._intersects(quality.get("lineage_refs"), version.get("lineage_refs")):
            return True
        return False

    def _quality_requires_propagation(self, quality: Mapping[str, Any]) -> bool:
        status = str(quality.get("evaluation_status") or "").strip().lower()
        if status in {"fail", "failed", "conditional_pass", "warning", "disqualified"}:
            return True
        if self._list_values(quality.get("quality_flags")):
            return True
        score = quality.get("fitness_score")
        try:
            return score is not None and float(score) < 1.0
        except (TypeError, ValueError):
            return False

    def _target_refs_from_record(self, record: Mapping[str, Any]) -> list[str]:
        refs = []
        for target in self._targets_from_version(record):
            target_ref = self._string_or_none(target.get("target_object_ref"))
            if target_ref:
                refs.append(target_ref)
        return self._dedupe_strings(refs)

    def _reason_code(self, trigger: Mapping[str, Any], trigger_type: str) -> str:
        if trigger_type == "version_record":
            return "version_change"
        if trigger_type == "quality_record":
            return "quality_change"
        change_type = str(trigger.get("change_type") or "").strip().lower()
        if "contract" in change_type:
            return "contract_change"
        if "taxonomy" in change_type:
            return "taxonomy_change"
        if "library" in change_type:
            return "library_change"
        return "source_change"

    def _stale_reason(self, reason_code: str) -> str:
        return {
            "version_change": "upstream_version_changed",
            "quality_change": "quality_degraded",
            "source_change": "source_changed",
            "contract_change": "contract_changed",
            "taxonomy_change": "taxonomy_changed",
            "library_change": "library_changed",
        }[reason_code]

    def _severity(self, trigger: Mapping[str, Any], trigger_type: str) -> str:
        if trigger_type == "change_event":
            raw = str(trigger.get("severity") or "info").strip().lower()
            if raw in {"critical", "warning", "info"}:
                return raw
            if raw in {"high", "urgent"}:
                return "critical"
            return "warning"
        if trigger_type == "quality_record":
            status = str(trigger.get("evaluation_status") or "").strip().lower()
            flags = [str(flag).lower() for flag in self._list_values(trigger.get("quality_flags"))]
            if status in {"fail", "failed", "disqualified"} or any(
                "blocking" in flag or "critical" in flag for flag in flags
            ):
                return "critical"
            if status in {"conditional_pass", "warning"} or flags:
                return "warning"
            return "info"
        mutation = str(trigger.get("mutation_type") or "").strip().lower()
        if mutation in {"delete", "breaking", "contract_change", "taxonomy_change"}:
            return "critical"
        if mutation in {"update", "merge", "split", "schema_change"}:
            return "warning"
        return "info"

    def _priority(
        self,
        trigger: Mapping[str, Any],
        trigger_type: str,
        severity: str,
        dependency_depth: int,
    ) -> str:
        if severity == "critical":
            return "urgent" if dependency_depth <= 4 else "high"
        if severity == "warning":
            if trigger_type == "quality_record":
                return "high"
            return "medium"
        return "low"

    def _trigger_timestamp(self, trigger: Mapping[str, Any], trigger_type: str) -> str:
        field = {
            "version_record": "created_at",
            "quality_record": "evaluated_at",
            "change_event": "detected_at",
        }.get(trigger_type)
        if not field:
            return DEFAULT_EVALUATED_AT
        return self._format_timestamp(self._parse_timestamp(trigger.get(field)))

    def _source_ref(self, trigger: Mapping[str, Any], trigger_type: str) -> str:
        for field in ("source_ref", "source_id", "object_id", "subject_ref"):
            value = self._string_or_none(trigger.get(field))
            if value:
                return value
        return self._primary_ref(trigger, trigger_type)

    def _version_ref_for_quality(self, quality: Mapping[str, Any]) -> str | None:
        return self._first_string(
            quality,
            [
                "subject_version_ref",
                "version_ref",
                "target_version_ref",
                "source_version_ref",
            ],
        )

    def _primary_ref(self, record: Mapping[str, Any], trigger_type: str) -> str:
        field = {
            "version_record": "version_id",
            "quality_record": "quality_record_id",
            "change_event": "event_id",
        }.get(trigger_type)
        if field:
            value = self._string_or_none(record.get(field))
            if value:
                return value
        return self._string_or_none(record.get("record_id")) or "UNKNOWN_INPUT"

    def _infer_trigger_type(self, record: Mapping[str, Any]) -> str:
        if record.get("event_id"):
            return "change_event"
        if record.get("version_id"):
            return "version_record"
        if record.get("quality_record_id"):
            return "quality_record"
        return "invalid_batch"

    def _propagation_record_id(
        self,
        *,
        trigger_ref: str,
        input_refs: list[str],
        affected_refs: Iterable[Any],
        rule_version: str,
    ) -> str:
        return self._stable_id(
            "propagation",
            [trigger_ref, self._dedupe_strings(input_refs), self._dedupe_strings(affected_refs), rule_version],
        )

    def _job_id(
        self,
        *,
        trigger_ref: str,
        target_ref: str,
        target_version_ref: str | None,
        rule_version: str,
    ) -> str:
        return self._stable_id("rejob", [trigger_ref, target_ref, target_version_ref, rule_version])

    def _stale_object_id(
        self,
        *,
        trigger_ref: str,
        target_ref: str,
        target_version_ref: str | None,
        rule_version: str,
    ) -> str:
        return self._stable_id("stale", [trigger_ref, target_ref, target_version_ref, rule_version])

    def _deterministic_evaluated_at(
        self, explicit: str | None, records: list[Mapping[str, Any]]
    ) -> str:
        if explicit:
            return self._format_timestamp(self._parse_timestamp(explicit))
        parsed: list[datetime] = []
        for record in records:
            for field in ("created_at", "evaluated_at", "detected_at"):
                if record.get(field) and self._timestamp_parseable(record.get(field)):
                    parsed.append(self._parse_timestamp(record.get(field)))
        if not parsed:
            return DEFAULT_EVALUATED_AT
        return self._format_timestamp(max(parsed))

    def _parse_timestamp(self, value: Any) -> datetime:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("timestamp is missing")
        text = value.strip()
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _format_timestamp(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )

    def _timestamp_parseable(self, value: Any) -> bool:
        try:
            self._parse_timestamp(value)
            return True
        except (TypeError, ValueError):
            return False

    def _stable_id(self, prefix: str, payload: Any) -> str:
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()[:24]
        return f"{prefix}_{digest}"

    def _version_hash(self, record: Mapping[str, Any]) -> str:
        payload = dict(record)
        payload.pop("version_hash", None)
        return "sha256:" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()

    def _missing_fields(self, record: Mapping[str, Any], fields: list[str]) -> list[str]:
        return [field for field in fields if self._string_or_none(record.get(field)) is None]

    def _has_any_ref(self, record: Mapping[str, Any], fields: list[str]) -> bool:
        for field in fields:
            value = record.get(field)
            if self._list_values(value):
                return True
            if self._string_or_none(value):
                return True
        return False

    def _evidence_refs(self, record: Mapping[str, Any]) -> list[str]:
        refs: list[Any] = []
        for field in (
            "provenance_refs",
            "evidence_refs",
            "lineage_refs",
            "impact_set",
            "affected_dependencies",
            "subject_ref",
            "source_id",
            "prior_version_ref",
            "previous_version_ref",
            "current_version_ref",
        ):
            refs.extend(self._list_values(record.get(field)))
        return self._dedupe_strings(refs)

    def _list_values(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, (str, bytes)):
            return [value.decode("utf-8") if isinstance(value, bytes) else value]
        if isinstance(value, Mapping):
            ref = self._first_string(
                value,
                [
                    "target_object_ref",
                    "object_ref",
                    "target_ref",
                    "downstream_ref",
                    "object_id",
                    "subject_ref",
                    "ref",
                    "id",
                ],
            )
            return [ref] if ref else []
        if isinstance(value, Iterable):
            values: list[Any] = []
            for item in value:
                if isinstance(item, Mapping):
                    ref = self._first_string(
                        item,
                        [
                            "target_object_ref",
                            "object_ref",
                            "target_ref",
                            "downstream_ref",
                            "object_id",
                            "subject_ref",
                            "ref",
                            "id",
                        ],
                    )
                    if ref:
                        values.append(ref)
                else:
                    values.append(item)
            return values
        return [value]

    def _raw_items(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, (str, bytes)) or isinstance(value, Mapping):
            return [value]
        if isinstance(value, Iterable):
            return list(value)
        return [value]

    def _dedupe_strings(self, values: Iterable[Any]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for value in values:
            text = self._string_or_none(value)
            if text is None or text in seen:
                continue
            seen.add(text)
            output.append(text)
        return output

    def _dedupe_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, tuple[str, ...]]] = set()
        output: list[dict[str, Any]] = []
        for candidate in candidates:
            key = (
                str(candidate.get("target_object_ref") or ""),
                str(candidate.get("target_version_ref") or ""),
                tuple(candidate.get("dependency_path") or []),
            )
            if key in seen:
                continue
            seen.add(key)
            output.append(candidate)
        return output

    def _append_once(self, values: list[str], value: str) -> list[str]:
        if value not in values:
            values.append(value)
        return values

    def _intersects(self, left: Any, right: Any) -> bool:
        left_set = set(self._dedupe_strings(self._list_values(left)))
        right_set = set(self._dedupe_strings(self._list_values(right)))
        return bool(left_set and right_set and left_set.intersection(right_set))

    def _first_string(self, record: Mapping[str, Any], fields: list[str]) -> str | None:
        for field in fields:
            value = self._string_or_none(record.get(field))
            if value:
                return value
        return None

    def _string_or_none(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _sort_by_ref(self, records: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
        return sorted(records, key=lambda item: str(item.get(field) or ""))

    def _is_record_collection(self, value: Any) -> bool:
        return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
