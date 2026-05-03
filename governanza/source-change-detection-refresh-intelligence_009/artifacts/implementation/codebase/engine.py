"""Core deterministic engine for motor_009.

The engine reads upstream records as immutable dictionaries and emits only
motor_009 output objects or structured validation errors.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import ChangeEvent, RefreshPriority, StalenessRecord, StructuredError


COMPARISON_EVIDENCE_FIELDS = (
    "availability_status",
    "observed_schema_signature",
    "content_fingerprint",
    "record_count",
    "access_error_code",
)


class SourceChangeDetectionRefreshIntelligence:
    """Detect source changes, staleness state and advisory refresh priority."""

    produced_by_motor = "motor_009"

    def run(
        self,
        *,
        source_registry: Iterable[dict[str, Any]] | dict[str, dict[str, Any]],
        ingestion_records: Iterable[dict[str, Any]],
        version_history: Iterable[dict[str, Any]],
        calculated_at: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        sources = self._normalize_source_registry(source_registry)
        ingestions_input = [copy.deepcopy(item) for item in ingestion_records]
        versions_input = [copy.deepcopy(item) for item in version_history]

        errors: list[StructuredError] = []
        ingestions_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        versions_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        rejected_sources: set[str] = set()

        for ingestion in ingestions_input:
            source_id = self._require_source_id(ingestion)
            ingestion_id = self._ref(ingestion, "ingestion_id")
            if source_id is None or source_id not in sources:
                errors.append(
                    StructuredError(
                        "INVALID_SOURCE_REFERENCE",
                        source_id,
                        "Ingestion record references a source_id absent from source_registry.",
                        [ingestion_id] if ingestion_id else [],
                    )
                )
                if source_id:
                    rejected_sources.add(source_id)
                continue
            if not self._has_comparison_evidence(ingestion):
                errors.append(
                    StructuredError(
                        "MISSING_COMPARISON_EVIDENCE",
                        source_id,
                        "Ingestion record has no deterministic comparison evidence.",
                        [ingestion_id] if ingestion_id else [],
                    )
                )
                rejected_sources.add(source_id)
                continue
            try:
                ingestion["_parsed_captured_at"] = self._parse_timestamp(ingestion.get("captured_at"))
            except ValueError:
                errors.append(
                    StructuredError(
                        "INVALID_TEMPORAL_ORDER",
                        source_id,
                        "Ingestion captured_at is not a parseable ISO 8601 timestamp.",
                        [ingestion_id] if ingestion_id else [],
                    )
                )
                rejected_sources.add(source_id)
                continue
            ingestions_by_source[source_id].append(ingestion)

        for version in versions_input:
            source_id = self._require_source_id(version)
            version_id = self._ref(version, "version_id")
            if source_id is None or source_id not in sources:
                errors.append(
                    StructuredError(
                        "INVALID_SOURCE_REFERENCE",
                        source_id,
                        "Version record references a source_id absent from source_registry.",
                        [version_id] if version_id else [],
                    )
                )
                if source_id:
                    rejected_sources.add(source_id)
                continue
            try:
                version["_parsed_created_at"] = self._parse_timestamp(version.get("created_at"))
            except ValueError:
                errors.append(
                    StructuredError(
                        "INVALID_TEMPORAL_ORDER",
                        source_id,
                        "Version created_at is not a parseable ISO 8601 timestamp.",
                        [version_id] if version_id else [],
                    )
                )
                rejected_sources.add(source_id)
                continue
            versions_by_source[source_id].append(version)

        effective_calculated_at = calculated_at or self._deterministic_calculated_at(
            ingestions_by_source, versions_by_source
        )
        calculation_time = self._parse_timestamp(effective_calculated_at)
        calculated_at_text = self._format_timestamp(calculation_time)

        events: list[ChangeEvent] = []
        staleness_records: list[StalenessRecord] = []
        priorities: list[RefreshPriority] = []

        for source_id in sorted(sources):
            if source_id in rejected_sources:
                continue
            source = sources[source_id]
            source_ingestions = sorted(
                ingestions_by_source.get(source_id, []),
                key=lambda item: (
                    item["_parsed_captured_at"],
                    str(item.get("ingestion_id") or ""),
                ),
            )
            source_versions = sorted(
                versions_by_source.get(source_id, []),
                key=lambda item: (
                    item["_parsed_created_at"],
                    str(item.get("version_id") or ""),
                ),
            )

            try:
                source_events = self._detect_events(
                    source=source,
                    ingestions=source_ingestions,
                    versions=source_versions,
                    calculated_at=calculated_at_text,
                )
            except ValueError as exc:
                if str(exc) != "UNTRACEABLE_CHANGE_EVENT":
                    raise
                errors.append(
                    StructuredError(
                        "UNTRACEABLE_CHANGE_EVENT",
                        source_id,
                        "Detected change could not preserve sufficient evidence_refs and lineage_refs.",
                        [
                            *self._dedupe(self._ref(item, "ingestion_id") for item in source_ingestions),
                            *self._dedupe(self._ref(item, "version_id") for item in source_versions),
                        ],
                    )
                )
                continue
            events.extend(source_events)

            staleness = self._build_staleness_record(
                source=source,
                ingestions=source_ingestions,
                versions=source_versions,
                events=source_events,
                calculated_at=calculated_at_text,
                calculation_time=calculation_time,
            )
            staleness_records.append(staleness)

            priorities.append(
                self._build_refresh_priority(
                    source=source,
                    events=source_events,
                    staleness=staleness,
                    calculated_at=calculated_at_text,
                )
            )

        return {
            "change_detection_event": [item.to_dict() for item in events],
            "refresh_priority": [item.to_dict() for item in priorities],
            "staleness_signal": [item.to_dict() for item in staleness_records],
            "errors": [item.to_dict() for item in errors],
        }

    def _detect_events(
        self,
        *,
        source: dict[str, Any],
        ingestions: list[dict[str, Any]],
        versions: list[dict[str, Any]],
        calculated_at: str,
    ) -> list[ChangeEvent]:
        if len(ingestions) < 2:
            return []

        previous = ingestions[-2]
        current = ingestions[-1]
        previous_version, current_version = self._version_pair(versions)
        event_specs: list[dict[str, Any]] = []

        if self._access_changed(previous, current):
            event_specs.append(
                {
                    "change_type": "access",
                    "severity": "critical",
                    "detection_rule_ref": "rule.access_state.changed",
                    "comparison_basis": {
                        "previous_availability_status": previous.get("availability_status"),
                        "current_availability_status": current.get("availability_status"),
                        "previous_access_error_code": previous.get("access_error_code"),
                        "current_access_error_code": current.get("access_error_code"),
                    },
                }
            )
        elif previous.get("availability_status") != current.get("availability_status"):
            event_specs.append(
                {
                    "change_type": "availability",
                    "severity": "warning",
                    "detection_rule_ref": "rule.availability_status.changed",
                    "comparison_basis": {
                        "previous_availability_status": previous.get("availability_status"),
                        "current_availability_status": current.get("availability_status"),
                    },
                }
            )

        previous_schema = previous.get("observed_schema_signature")
        current_schema = current.get("observed_schema_signature")
        expected_schema = source.get("expected_schema_signature")
        if current_schema and (
            (previous_schema and previous_schema != current_schema)
            or (expected_schema and expected_schema != current_schema)
        ):
            event_specs.append(
                {
                    "change_type": "schema",
                    "severity": "warning",
                    "detection_rule_ref": "rule.schema_signature.changed",
                    "comparison_basis": {
                        "previous_schema_signature": previous_schema,
                        "current_schema_signature": current_schema,
                        "expected_schema_signature": expected_schema,
                    },
                }
            )

        previous_methodology = self._first_present(
            previous.get("declared_methodology_ref"),
            previous.get("methodology_ref"),
        )
        current_methodology = self._first_present(
            current.get("declared_methodology_ref"),
            current.get("methodology_ref"),
        )
        if previous_methodology and current_methodology and previous_methodology != current_methodology:
            event_specs.append(
                {
                    "change_type": "methodology",
                    "severity": "warning",
                    "detection_rule_ref": "rule.methodology_ref.changed",
                    "comparison_basis": {
                        "previous_methodology_ref": previous_methodology,
                        "current_methodology_ref": current_methodology,
                    },
                }
            )

        has_schema_event = any(spec["change_type"] == "schema" for spec in event_specs)
        previous_fingerprint = previous.get("content_fingerprint")
        current_fingerprint = current.get("content_fingerprint")
        if (
            not has_schema_event
            and previous_fingerprint
            and current_fingerprint
            and previous_fingerprint != current_fingerprint
        ):
            event_specs.append(
                {
                    "change_type": "content_fingerprint",
                    "severity": "info",
                    "detection_rule_ref": "rule.content_fingerprint.changed",
                    "comparison_basis": {
                        "previous_content_fingerprint": previous_fingerprint,
                        "current_content_fingerprint": current_fingerprint,
                    },
                }
            )

        events: list[ChangeEvent] = []
        for spec in event_specs:
            event = self._build_change_event(
                source=source,
                previous=previous,
                current=current,
                previous_version=previous_version,
                current_version=current_version,
                calculated_at=calculated_at,
                **spec,
            )
            events.append(event)
        return events

    def _build_change_event(
        self,
        *,
        source: dict[str, Any],
        previous: dict[str, Any],
        current: dict[str, Any],
        previous_version: dict[str, Any] | None,
        current_version: dict[str, Any] | None,
        change_type: str,
        severity: str,
        detection_rule_ref: str,
        comparison_basis: dict[str, Any],
        calculated_at: str,
    ) -> ChangeEvent:
        source_id = str(source["source_id"])
        previous_ingestion_ref = self._ref(previous, "ingestion_id")
        current_ingestion_ref = self._ref(current, "ingestion_id")
        previous_version_ref = self._ref(previous_version, "version_id") if previous_version else None
        current_version_ref = self._ref(current_version, "version_id") if current_version else None
        evidence_refs = self._dedupe(
            [
                previous_ingestion_ref,
                current_ingestion_ref,
                current_version_ref,
            ]
        )
        lineage_refs = self._lineage_refs(source, previous, current, previous_version, current_version)
        if not evidence_refs or not lineage_refs:
            raise ValueError("UNTRACEABLE_CHANGE_EVENT")

        evidence_hash = self._short_hash(evidence_refs)
        event_id = f"motor_009:{source_id}:event:{change_type}:{calculated_at}:{evidence_hash}"
        base = {
            "record_id": event_id,
            "event_id": event_id,
            "source_id": source_id,
            "change_type": change_type,
            "detected_at": calculated_at,
            "severity": severity,
            "previous_ingestion_ref": previous_ingestion_ref,
            "current_ingestion_ref": current_ingestion_ref,
            "previous_version_ref": previous_version_ref,
            "current_version_ref": current_version_ref,
            "comparison_basis": comparison_basis,
            "evidence_refs": evidence_refs,
            "lineage_refs": lineage_refs,
            "detection_rule_ref": detection_rule_ref,
            "created_at": calculated_at,
            "updated_at": calculated_at,
            "source_ref": self._source_ref(source),
            "produced_by_motor": self.produced_by_motor,
            "produced_at": calculated_at,
            "parent_id": None,
        }
        version_hash = self._hash(base)
        return ChangeEvent(version_id=f"motor_009:version:{version_hash[:16]}", version_hash=version_hash, **base)

    def _build_staleness_record(
        self,
        *,
        source: dict[str, Any],
        ingestions: list[dict[str, Any]],
        versions: list[dict[str, Any]],
        events: list[ChangeEvent],
        calculated_at: str,
        calculation_time: datetime,
    ) -> StalenessRecord:
        source_id = str(source["source_id"])
        latest_ingestion = ingestions[-1] if ingestions else None
        latest_version = versions[-1] if versions else None
        last_observed_time = self._last_observed_time(latest_ingestion, latest_version)
        last_observed_at = self._format_timestamp(last_observed_time) if last_observed_time else None
        age_days = (calculation_time - last_observed_time).days if last_observed_time else None
        expected_interval = source.get("declared_refresh_interval")
        interval_days = self._parse_duration_days(expected_interval)
        event_types = {event.change_type for event in events}

        if last_observed_time is None:
            status = "unknown"
            condition = "no_accepted_observation"
        elif interval_days is None:
            status = "unknown"
            condition = "no_declared_refresh_interval"
        elif "access" in event_types:
            status = "stale"
            condition = "access_blocked_or_error_changed"
        elif age_days is not None and age_days > interval_days and "schema" in event_types:
            status = "watch"
            condition = "interval_exceeded_and_schema_changed"
        elif age_days is not None and age_days > (interval_days * 2):
            status = "stale"
            condition = "refresh_interval_exceeded_twice"
        elif age_days is not None and age_days > interval_days:
            status = "watch"
            condition = "refresh_interval_exceeded"
        else:
            status = "fresh"
            condition = "within_declared_refresh_interval"

        basis_ingestion_refs = self._dedupe(self._ref(item, "ingestion_id") for item in ingestions)
        basis_version_refs = self._dedupe(self._ref(item, "version_id") for item in versions)
        trigger_event_ids = [event.event_id for event in events]
        evidence_hash = self._short_hash([*basis_ingestion_refs, *basis_version_refs])
        staleness_id = f"motor_009:{source_id}:staleness:{status}:{calculated_at}:{evidence_hash}"
        base = {
            "record_id": staleness_id,
            "staleness_id": staleness_id,
            "source_id": source_id,
            "staleness_status": status,
            "last_observed_at": last_observed_at,
            "expected_refresh_interval": expected_interval,
            "age_days": age_days,
            "triggering_condition": condition,
            "trigger_event_ids": trigger_event_ids,
            "basis_ingestion_refs": basis_ingestion_refs,
            "basis_version_refs": basis_version_refs,
            "calculated_at": calculated_at,
            "created_at": calculated_at,
            "updated_at": calculated_at,
            "source_ref": self._source_ref(source),
            "produced_by_motor": self.produced_by_motor,
            "produced_at": calculated_at,
            "parent_id": None,
        }
        version_hash = self._hash(base)
        return StalenessRecord(
            version_id=f"motor_009:version:{version_hash[:16]}",
            version_hash=version_hash,
            **base,
        )

    def _build_refresh_priority(
        self,
        *,
        source: dict[str, Any],
        events: list[ChangeEvent],
        staleness: StalenessRecord,
        calculated_at: str,
    ) -> RefreshPriority:
        source_id = str(source["source_id"])
        event_types = {event.change_type for event in events}
        severities = {event.severity for event in events}

        if "critical" in severities and "access" in event_types:
            level = "urgent"
            reason = "access_change_requires_refresh_attention"
            rule_ref = "rule.priority.access_change.urgent"
        elif "schema" in event_types and staleness.staleness_status in {"watch", "stale"}:
            level = "high"
            reason = "schema_changed_and_refresh_interval_exceeded"
            rule_ref = "rule.priority.schema_change.stale.high"
        elif staleness.staleness_status == "stale":
            level = "medium"
            reason = "refresh_interval_exceeded_without_material_change"
            rule_ref = "rule.priority.stale.medium"
        elif "warning" in severities or staleness.staleness_status == "watch":
            level = "low"
            reason = "change_or_watch_signal_present"
            rule_ref = "rule.priority.watch.low"
        elif "info" in severities:
            level = "low"
            reason = "content_fingerprint_changed_without_structural_or_access_change"
            rule_ref = "rule.priority.content_fingerprint.low"
        elif staleness.staleness_status == "unknown":
            level = "none"
            reason = "no_change_event_and_no_declared_refresh_interval"
            rule_ref = "rule.priority.no_change.unknown_interval.none"
        else:
            level = "none"
            reason = "no_change_event_and_source_fresh"
            rule_ref = "rule.priority.no_change.fresh.none"

        event_ids = [event.event_id for event in events]
        evidence_refs = self._dedupe(
            [
                *event_ids,
                staleness.staleness_id,
                *staleness.basis_ingestion_refs,
                *staleness.basis_version_refs,
            ]
        )
        evidence_hash = self._short_hash(evidence_refs)
        priority_id = f"motor_009:{source_id}:priority:{level}:{calculated_at}:{evidence_hash}"
        base = {
            "record_id": priority_id,
            "priority_id": priority_id,
            "source_id": source_id,
            "priority_level": level,
            "priority_reason": reason,
            "derived_from_event_ids": event_ids,
            "staleness_id": staleness.staleness_id,
            "rule_ref": rule_ref,
            "calculated_at": calculated_at,
            "evidence_refs": evidence_refs,
            "created_at": calculated_at,
            "updated_at": calculated_at,
            "source_ref": staleness.staleness_id,
            "produced_by_motor": self.produced_by_motor,
            "produced_at": calculated_at,
            "parent_id": None,
        }
        version_hash = self._hash(base)
        return RefreshPriority(
            version_id=f"motor_009:version:{version_hash[:16]}",
            version_hash=version_hash,
            **base,
        )

    def _normalize_source_registry(
        self,
        source_registry: Iterable[dict[str, Any]] | dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        if isinstance(source_registry, dict):
            records = []
            for key, value in source_registry.items():
                record = copy.deepcopy(value)
                record.setdefault("source_id", key)
                records.append(record)
        else:
            records = [copy.deepcopy(item) for item in source_registry]

        normalized: dict[str, dict[str, Any]] = {}
        for record in records:
            source_id = self._require_source_id(record)
            if source_id is None:
                raise ValueError("INVALID_SOURCE_REFERENCE")
            normalized[source_id] = record
        return normalized

    def _deterministic_calculated_at(
        self,
        ingestions_by_source: dict[str, list[dict[str, Any]]],
        versions_by_source: dict[str, list[dict[str, Any]]],
    ) -> str:
        timestamps: list[datetime] = []
        for records in ingestions_by_source.values():
            timestamps.extend(record["_parsed_captured_at"] for record in records)
        for records in versions_by_source.values():
            timestamps.extend(record["_parsed_created_at"] for record in records)
        if not timestamps:
            return "1970-01-01T00:00:00Z"
        return self._format_timestamp(max(timestamps))

    def _version_pair(self, versions: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        if not versions:
            return None, None
        current = versions[-1]
        previous_ref = current.get("previous_version_ref")
        previous = None
        if previous_ref:
            previous = next((item for item in versions if item.get("version_id") == previous_ref), None)
        if previous is None and len(versions) >= 2:
            previous = versions[-2]
        return previous, current

    def _lineage_refs(
        self,
        source: dict[str, Any],
        previous: dict[str, Any],
        current: dict[str, Any],
        previous_version: dict[str, Any] | None,
        current_version: dict[str, Any] | None,
    ) -> list[str]:
        refs: list[str | None] = []
        for version in (previous_version, current_version):
            if not version:
                continue
            lineage = version.get("lineage_refs") or []
            if isinstance(lineage, str):
                refs.append(lineage)
            else:
                refs.extend(str(item) for item in lineage if item)
        if not refs:
            refs.extend(
                [
                    self._ref(source, "source_locator_ref"),
                    self._ref(previous, "raw_record_ref"),
                    self._ref(previous, "parsed_record_ref"),
                    self._ref(current, "raw_record_ref"),
                    self._ref(current, "parsed_record_ref"),
                ]
            )
        return self._dedupe(refs)

    def _last_observed_time(
        self,
        latest_ingestion: dict[str, Any] | None,
        latest_version: dict[str, Any] | None,
    ) -> datetime | None:
        candidates: list[datetime] = []
        if latest_ingestion:
            candidates.append(latest_ingestion["_parsed_captured_at"])
        if latest_version:
            candidates.append(latest_version["_parsed_created_at"])
        return max(candidates) if candidates else None

    def _has_comparison_evidence(self, ingestion: dict[str, Any]) -> bool:
        for field in COMPARISON_EVIDENCE_FIELDS:
            value = ingestion.get(field)
            if value is not None and value != "":
                return True
        return False

    def _access_changed(self, previous: dict[str, Any], current: dict[str, Any]) -> bool:
        blocked_states = {"blocked", "forbidden", "unauthorized"}
        previous_status = str(previous.get("availability_status") or "").lower()
        current_status = str(current.get("availability_status") or "").lower()
        previous_error = previous.get("access_error_code")
        current_error = current.get("access_error_code")
        return (
            previous_error != current_error
            and (previous_error is not None or current_error is not None)
        ) or current_status in blocked_states or previous_status in blocked_states

    def _source_ref(self, source: dict[str, Any]) -> str:
        return str(source.get("source_locator_ref") or f"source_registry:{source['source_id']}")

    def _require_source_id(self, record: dict[str, Any]) -> str | None:
        source_id = record.get("source_id")
        if source_id is None:
            return None
        source_id_text = str(source_id).strip()
        return source_id_text or None

    def _ref(self, record: dict[str, Any] | None, key: str) -> str | None:
        if not record:
            return None
        value = record.get(key)
        if value is None or value == "":
            return None
        return str(value)

    def _first_present(self, *values: Any) -> Any:
        for value in values:
            if value is not None and value != "":
                return value
        return None

    def _dedupe(self, values: Iterable[Any]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            if value is None or value == "":
                continue
            text = str(value)
            if text in seen:
                continue
            seen.add(text)
            result.append(text)
        return result

    def _parse_timestamp(self, value: Any) -> datetime:
        if not isinstance(value, str) or not value:
            raise ValueError("timestamp is required")
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError("timestamp must be ISO 8601") from exc
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        return parsed.astimezone(timezone.utc)

    def _format_timestamp(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _parse_duration_days(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.fullmatch(r"P(\d+)D", value)
            if match:
                return int(match.group(1))
        return None

    def _hash(self, value: Any) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _short_hash(self, value: Any) -> str:
        return self._hash(value)[:12]
