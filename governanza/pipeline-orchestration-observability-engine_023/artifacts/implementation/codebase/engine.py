"""Deterministic core for the Pipeline Orchestration + Observability Engine.

The engine validates execution events against phase contracts from motor_001,
then emits operational logs, metrics, alerts, and retry decisions. It never
modifies contracts, motor state files, artifacts, dependencies, or business
payloads from observed motors.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


MOTOR_ID = "motor_023"
SCHEMA_VERSION = "motor_023.schema.v1"
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

EVENT_TYPES = {
    "queued",
    "started",
    "stage_completed",
    "failed",
    "retried",
    "skipped",
    "aborted",
    "heartbeat",
    "timeout",
}
STATUSES = {
    "pending",
    "running",
    "succeeded",
    "failed",
    "skipped",
    "aborted",
    "timed_out",
}
REJECTION_CODES = {
    "INVALID_EVENT_SHAPE",
    "UNKNOWN_CONTRACT_SCOPE",
    "INVALID_CAUSAL_ORDER",
    "UNSUPPORTED_OPERATION_REQUEST",
}
DECISIONS = {"retry", "suppress_retry", "abort"}
REASON_CODES = {
    "retryable_failure",
    "max_attempts_reached",
    "non_retryable_error",
    "no_failure",
    "invalid_event",
    "missing_contract_scope",
}

REQUIRED_EVENT_FIELDS = (
    "source_event_id",
    "run_id",
    "motor_id",
    "stage_name",
    "event_type",
    "status",
    "timestamp",
    "received_at",
    "correlation_id",
    "source_ref",
    "version_id",
    "produced_by_motor",
    "produced_at",
)

UNSUPPORTED_OPERATION_MARKERS = (
    "motor_state.json",
    "phase_contracts",
    "dependency",
    "dependencies",
    "artifact",
    "artifacts",
    "gate",
    "gates",
    "business_logic",
    "business logic",
    "conformance",
    "contract edit",
)


@dataclass(frozen=True)
class ExecutionLog:
    log_id: str
    source_event_id: str
    run_id: str
    motor_id: str
    stage_name: str
    event_type: str
    status: str
    timestamp: str
    correlation_id: str
    attempt_number: int
    previous_log_id: Optional[str]
    payload_ref: Optional[str]
    immutability_state: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MetricRecord:
    metric_id: str
    metric_name: str
    metric_value: float
    unit: str
    aggregation_method: str
    window_start: str
    window_end: str
    motor_id: str
    stage_name: Optional[str]
    run_id: Optional[str]
    source_log_ids: List[str]
    source_event_ids: List[str]
    calculation_status: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AlertEvent:
    alert_id: str
    alert_type: str
    severity: str
    triggering_condition: str
    run_id: str
    motor_id: str
    stage_name: Optional[str]
    linked_log_id: str
    linked_metric_id: Optional[str]
    timestamp: str
    dedupe_key: str
    acknowledgement_status: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RetryDecision:
    decision_id: str
    decision: str
    reason_code: str
    attempt_number: int
    max_attempts: int
    retry_after_seconds: int
    linked_failure_event_id: Optional[str]
    linked_log_id: Optional[str]
    run_id: str
    motor_id: str
    stage_name: str
    policy_ref: str
    timestamp: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProcessingResult:
    observed_event: Dict[str, Any]
    execution_log: Optional[ExecutionLog]
    metric_records: Tuple[MetricRecord, ...]
    alert_events: Tuple[AlertEvent, ...]
    retry_decision: Optional[RetryDecision]
    rejection_code: Optional[str] = None
    duplicate_of_log_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observed_event": dict(self.observed_event),
            "execution_log": self.execution_log.to_dict() if self.execution_log else None,
            "metric_records": [record.to_dict() for record in self.metric_records],
            "alert_events": [event.to_dict() for event in self.alert_events],
            "retry_decision": self.retry_decision.to_dict() if self.retry_decision else None,
            "rejection_code": self.rejection_code,
            "duplicate_of_log_id": self.duplicate_of_log_id,
        }


class PipelineOrchestrationObservabilityEngine:
    """Orchestrates validated operational visibility for observed motor runs."""

    def __init__(
        self,
        phase_contracts: Any,
        retry_policy_config: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self._allowed_scopes = _normalize_phase_contracts(phase_contracts)
        self._retry_policy = _normalize_retry_policy(retry_policy_config or {})
        self._events_by_source_id: Dict[str, Dict[str, Any]] = {}
        self._canonical_events_by_source_id: Dict[str, str] = {}
        self._logs_by_source_id: Dict[str, ExecutionLog] = {}
        self._logs_by_id: Dict[str, ExecutionLog] = {}
        self._last_log_by_correlation_id: Dict[str, ExecutionLog] = {}
        self._run_start_by_run_id: Dict[str, datetime] = {}
        self._alerts_by_dedupe_key: Dict[str, AlertEvent] = {}
        self._retry_decisions_by_failure_event_id: Dict[str, RetryDecision] = {}

    def process_event(self, motor_execution_event: Mapping[str, Any]) -> ProcessingResult:
        """Validate one execution event and emit deterministic operational outputs."""

        if not isinstance(motor_execution_event, Mapping):
            return self._reject({}, "INVALID_EVENT_SHAPE")

        raw_event = dict(motor_execution_event)
        shape_error = self._validate_event_shape(raw_event)
        if shape_error:
            return self._reject(raw_event, shape_error)

        timestamp = _parse_datetime(raw_event["timestamp"])
        received_at = _parse_datetime(raw_event["received_at"])
        produced_at = _parse_datetime(raw_event["produced_at"])

        if timestamp is None or received_at is None or produced_at is None:
            return self._reject(raw_event, "INVALID_EVENT_SHAPE")

        if _contains_unsupported_operation(raw_event):
            return self._reject(raw_event, "UNSUPPORTED_OPERATION_REQUEST")

        if not self._is_scope_allowed(raw_event["motor_id"], raw_event["stage_name"]):
            return self._reject(raw_event, "UNKNOWN_CONTRACT_SCOPE")

        source_event_id = str(raw_event["source_event_id"])
        canonical_event = _canonical_event(raw_event)
        existing_event = self._canonical_events_by_source_id.get(source_event_id)
        if existing_event is not None:
            existing_log = self._logs_by_source_id.get(source_event_id)
            if existing_event == canonical_event and existing_log is not None:
                duplicate_metric = self._build_metric_record(
                    metric_name="deduplicated_event_count",
                    metric_value=1,
                    unit="count",
                    aggregation_method="count",
                    window_start=timestamp,
                    window_end=received_at,
                    motor_id=str(raw_event["motor_id"]),
                    stage_name=str(raw_event["stage_name"]),
                    run_id=str(raw_event["run_id"]),
                    source_log_ids=[existing_log.log_id],
                    source_event_ids=[source_event_id],
                    produced_at=received_at,
                    parent_id=None,
                )
                observed_event = dict(self._events_by_source_id[source_event_id])
                return ProcessingResult(
                    observed_event=observed_event,
                    execution_log=None,
                    metric_records=(duplicate_metric,),
                    alert_events=(),
                    retry_decision=None,
                    duplicate_of_log_id=existing_log.log_id,
                )
            return self._reject(raw_event, "INVALID_CAUSAL_ORDER")

        causal_rejection = self._validate_causal_order(raw_event, timestamp)
        if causal_rejection:
            linked_alerts: Tuple[AlertEvent, ...] = ()
            previous_log = self._last_log_by_correlation_id.get(str(raw_event["correlation_id"]))
            if previous_log is not None:
                linked_alerts = (
                    self._build_alert_event(
                        alert_type="causal_order_error",
                        severity="error",
                        triggering_condition="event timestamp breaks correlation causal order",
                        run_id=str(raw_event["run_id"]),
                        motor_id=str(raw_event["motor_id"]),
                        stage_name=str(raw_event["stage_name"]),
                        linked_log_id=previous_log.log_id,
                        linked_metric_id=None,
                        produced_at=received_at,
                    ),
                )
            return self._reject(raw_event, causal_rejection, alert_events=linked_alerts)

        observed_event = self._build_observed_event(raw_event, timestamp, received_at, produced_at)
        execution_log = self._build_execution_log(observed_event, timestamp, received_at)
        metric_records = tuple(self._metrics_for_event(observed_event, execution_log, timestamp, received_at))
        alert_events = tuple(self._alerts_for_event(observed_event, execution_log, received_at))
        retry_decision = self._build_retry_decision(observed_event, execution_log, received_at)

        self._events_by_source_id[source_event_id] = observed_event
        self._canonical_events_by_source_id[source_event_id] = canonical_event
        self._logs_by_source_id[source_event_id] = execution_log
        self._logs_by_id[execution_log.log_id] = execution_log
        self._last_log_by_correlation_id[str(observed_event["correlation_id"])] = execution_log
        run_id = str(observed_event["run_id"])
        if run_id not in self._run_start_by_run_id:
            self._run_start_by_run_id[run_id] = timestamp
        if retry_decision.linked_failure_event_id:
            self._retry_decisions_by_failure_event_id[retry_decision.linked_failure_event_id] = retry_decision

        return ProcessingResult(
            observed_event=observed_event,
            execution_log=execution_log,
            metric_records=metric_records,
            alert_events=alert_events,
            retry_decision=retry_decision,
        )

    def evaluate_clock_tick(self, clock_tick: str) -> Dict[str, List[Dict[str, Any]]]:
        """Emit timeout or heartbeat-missing signals for stale active logs."""

        tick = _parse_datetime(clock_tick)
        if tick is None:
            return {"metric_records": [], "alert_events": []}

        timeout_seconds = int(self._retry_policy["timeout_seconds"])
        metric_records: List[MetricRecord] = []
        alert_events: List[AlertEvent] = []

        for log in sorted(self._last_log_by_correlation_id.values(), key=lambda item: item.log_id):
            if log.status not in {"pending", "running"} and log.event_type not in {"started", "heartbeat"}:
                continue

            log_time = _parse_datetime(log.timestamp)
            if log_time is None:
                continue
            age_seconds = int((tick - log_time).total_seconds())
            if age_seconds <= timeout_seconds:
                continue

            metric_records.append(
                self._build_metric_record(
                    metric_name="heartbeat_age_seconds",
                    metric_value=age_seconds,
                    unit="seconds",
                    aggregation_method="latest",
                    window_start=log_time,
                    window_end=tick,
                    motor_id=log.motor_id,
                    stage_name=log.stage_name,
                    run_id=log.run_id,
                    source_log_ids=[log.log_id],
                    source_event_ids=[log.source_event_id],
                    produced_at=tick,
                    parent_id=None,
                )
            )
            alert_events.append(
                self._build_alert_event(
                    alert_type="heartbeat_missing",
                    severity="warning",
                    triggering_condition=f"no heartbeat within {timeout_seconds} seconds",
                    run_id=log.run_id,
                    motor_id=log.motor_id,
                    stage_name=log.stage_name,
                    linked_log_id=log.log_id,
                    linked_metric_id=metric_records[-1].metric_id,
                    produced_at=tick,
                )
            )

        return {
            "metric_records": [record.to_dict() for record in metric_records],
            "alert_events": [event.to_dict() for event in alert_events],
        }

    def logs(self) -> Tuple[ExecutionLog, ...]:
        """Return accepted logs without allowing callers to mutate engine state."""

        return tuple(self._logs_by_id[key] for key in sorted(self._logs_by_id))

    def _validate_event_shape(self, event: Mapping[str, Any]) -> Optional[str]:
        for field in REQUIRED_EVENT_FIELDS:
            if field not in event or event[field] is None or event[field] == "":
                return "INVALID_EVENT_SHAPE"

        if str(event["event_type"]) not in EVENT_TYPES:
            return "INVALID_EVENT_SHAPE"
        if str(event["status"]) not in STATUSES:
            return "INVALID_EVENT_SHAPE"
        if str(event["produced_by_motor"]) != MOTOR_ID:
            return "INVALID_EVENT_SHAPE"
        if "validation_status" in event and event["validation_status"] not in {"accepted", "rejected"}:
            return "INVALID_EVENT_SHAPE"

        attempt_number = event.get("attempt_number", 0)
        if not isinstance(attempt_number, int) or attempt_number < 0:
            return "INVALID_EVENT_SHAPE"

        if not str(event["version_id"]):
            return "INVALID_EVENT_SHAPE"
        return None

    def _validate_causal_order(self, event: Mapping[str, Any], timestamp: datetime) -> Optional[str]:
        run_id = str(event["run_id"])
        run_start = self._run_start_by_run_id.get(run_id)
        if run_start is not None and timestamp < run_start:
            return "INVALID_CAUSAL_ORDER"

        correlation_id = str(event["correlation_id"])
        previous_log = self._last_log_by_correlation_id.get(correlation_id)
        if previous_log is not None:
            previous_timestamp = _parse_datetime(previous_log.timestamp)
            if previous_timestamp is not None and timestamp < previous_timestamp:
                return "INVALID_CAUSAL_ORDER"
            parent_id = event.get("parent_id")
            if parent_id and str(parent_id) != previous_log.source_event_id and str(parent_id) != previous_log.log_id:
                return "INVALID_CAUSAL_ORDER"

        return None

    def _is_scope_allowed(self, motor_id: str, stage_name: str) -> bool:
        stages = self._allowed_scopes.get(str(motor_id))
        if not stages:
            return False
        return "*" in stages or str(stage_name) in stages

    def _build_observed_event(
        self,
        event: Mapping[str, Any],
        timestamp: datetime,
        received_at: datetime,
        produced_at: datetime,
    ) -> Dict[str, Any]:
        created_at = _format_datetime(_parse_datetime(event.get("created_at")) or received_at)
        observed = dict(event)
        observed.update(
            {
                "timestamp": _format_datetime(timestamp),
                "received_at": _format_datetime(received_at),
                "produced_at": _format_datetime(produced_at),
                "attempt_number": int(event.get("attempt_number", 0)),
                "error_type": event.get("error_type"),
                "payload_ref": event.get("payload_ref"),
                "validation_status": "accepted",
                "rejection_code": None,
                "version_id": str(event.get("version_id") or SCHEMA_VERSION),
                "created_at": created_at,
                "updated_at": created_at,
                "source_ref": str(event["source_ref"]),
                "produced_by_motor": MOTOR_ID,
                "parent_id": event.get("parent_id"),
            }
        )
        observed["version_hash"] = _stable_hash(_without_version_hash(observed))
        return observed

    def _build_execution_log(
        self,
        observed_event: Mapping[str, Any],
        timestamp: datetime,
        received_at: datetime,
    ) -> ExecutionLog:
        source_event_id = str(observed_event["source_event_id"])
        previous_log = self._last_log_by_correlation_id.get(str(observed_event["correlation_id"]))
        previous_log_id = previous_log.log_id if previous_log else None
        created_at = _format_datetime(received_at)
        log = ExecutionLog(
            log_id=f"log-{source_event_id}",
            source_event_id=source_event_id,
            run_id=str(observed_event["run_id"]),
            motor_id=str(observed_event["motor_id"]),
            stage_name=str(observed_event["stage_name"]),
            event_type=str(observed_event["event_type"]),
            status=str(observed_event["status"]),
            timestamp=_format_datetime(timestamp),
            correlation_id=str(observed_event["correlation_id"]),
            attempt_number=int(observed_event.get("attempt_number", 0)),
            previous_log_id=previous_log_id,
            payload_ref=observed_event.get("payload_ref"),
            immutability_state="append_only",
            version_id=SCHEMA_VERSION,
            created_at=created_at,
            updated_at=created_at,
            version_hash="",
            source_ref=source_event_id,
            produced_by_motor=MOTOR_ID,
            produced_at=created_at,
            parent_id=previous_log_id,
        )
        return _with_version_hash(log)

    def _metrics_for_event(
        self,
        observed_event: Mapping[str, Any],
        execution_log: ExecutionLog,
        timestamp: datetime,
        received_at: datetime,
    ) -> List[MetricRecord]:
        event_type = str(observed_event["event_type"])
        status = str(observed_event["status"])

        if event_type == "stage_completed" and status == "succeeded":
            metric_name = "stage_completion_count"
        elif event_type == "failed" or status == "failed":
            metric_name = "failure_count"
        elif event_type == "retried":
            metric_name = "retry_count"
        else:
            return []

        return [
            self._build_metric_record(
                metric_name=metric_name,
                metric_value=1,
                unit="count",
                aggregation_method="count",
                window_start=timestamp,
                window_end=received_at,
                motor_id=str(observed_event["motor_id"]),
                stage_name=str(observed_event["stage_name"]),
                run_id=str(observed_event["run_id"]),
                source_log_ids=[execution_log.log_id],
                source_event_ids=[str(observed_event["source_event_id"])],
                produced_at=received_at,
                parent_id=None,
            )
        ]

    def _alerts_for_event(
        self,
        observed_event: Mapping[str, Any],
        execution_log: ExecutionLog,
        produced_at: datetime,
    ) -> List[AlertEvent]:
        event_type = str(observed_event["event_type"])
        status = str(observed_event["status"])
        attempt_number = int(observed_event.get("attempt_number", 0))
        max_attempts = int(self._retry_policy["max_attempts"])
        error_type = observed_event.get("error_type")

        if event_type == "timeout" or status == "timed_out":
            return [
                self._build_alert_event(
                    alert_type="timeout",
                    severity="error",
                    triggering_condition="execution reported timeout",
                    run_id=str(observed_event["run_id"]),
                    motor_id=str(observed_event["motor_id"]),
                    stage_name=str(observed_event["stage_name"]),
                    linked_log_id=execution_log.log_id,
                    linked_metric_id=None,
                    produced_at=produced_at,
                )
            ]

        if event_type != "failed" and status != "failed" and event_type != "aborted" and status != "aborted":
            return []

        if error_type in self._retry_policy["retryable_error_types"] and attempt_number >= max_attempts:
            return [
                self._build_alert_event(
                    alert_type="retry_exhausted",
                    severity="error",
                    triggering_condition="retryable failure reached max_attempts",
                    run_id=str(observed_event["run_id"]),
                    motor_id=str(observed_event["motor_id"]),
                    stage_name=str(observed_event["stage_name"]),
                    linked_log_id=execution_log.log_id,
                    linked_metric_id=None,
                    produced_at=produced_at,
                )
            ]

        severity = "warning" if error_type in self._retry_policy["retryable_error_types"] else "error"
        return [
            self._build_alert_event(
                alert_type="failure",
                severity=severity,
                triggering_condition="execution reported failure",
                run_id=str(observed_event["run_id"]),
                motor_id=str(observed_event["motor_id"]),
                stage_name=str(observed_event["stage_name"]),
                linked_log_id=execution_log.log_id,
                linked_metric_id=None,
                produced_at=produced_at,
            )
        ]

    def _build_metric_record(
        self,
        metric_name: str,
        metric_value: float,
        unit: str,
        aggregation_method: str,
        window_start: datetime,
        window_end: datetime,
        motor_id: str,
        stage_name: Optional[str],
        run_id: Optional[str],
        source_log_ids: Sequence[str],
        source_event_ids: Sequence[str],
        produced_at: datetime,
        parent_id: Optional[str],
    ) -> MetricRecord:
        if window_end < window_start:
            window_end = window_start
        source_log_ids = sorted(str(item) for item in source_log_ids)
        source_event_ids = sorted(str(item) for item in source_event_ids)
        metric_basis = {
            "metric_name": metric_name,
            "motor_id": motor_id,
            "stage_name": stage_name,
            "run_id": run_id,
            "window_start": _format_datetime(window_start),
            "window_end": _format_datetime(window_end),
            "source_log_ids": source_log_ids,
            "source_event_ids": source_event_ids,
        }
        created_at = _format_datetime(produced_at)
        metric = MetricRecord(
            metric_id=f"metric-{_stable_hash(metric_basis)[:16]}",
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
            aggregation_method=aggregation_method,
            window_start=_format_datetime(window_start),
            window_end=_format_datetime(window_end),
            motor_id=motor_id,
            stage_name=stage_name,
            run_id=run_id,
            source_log_ids=list(source_log_ids),
            source_event_ids=list(source_event_ids),
            calculation_status="complete",
            version_id=SCHEMA_VERSION,
            created_at=created_at,
            updated_at=created_at,
            version_hash="",
            source_ref=_compose_source_ref(source_log_ids, source_event_ids),
            produced_by_motor=MOTOR_ID,
            produced_at=created_at,
            parent_id=parent_id,
        )
        return _with_version_hash(metric)

    def _build_alert_event(
        self,
        alert_type: str,
        severity: str,
        triggering_condition: str,
        run_id: str,
        motor_id: str,
        stage_name: Optional[str],
        linked_log_id: str,
        linked_metric_id: Optional[str],
        produced_at: datetime,
    ) -> AlertEvent:
        window_key = _format_datetime(produced_at)
        dedupe_key = "|".join(
            [
                alert_type,
                triggering_condition,
                motor_id,
                stage_name or "",
                run_id,
                window_key,
            ]
        )
        parent_alert = self._alerts_by_dedupe_key.get(dedupe_key)
        parent_id = parent_alert.alert_id if parent_alert else None
        acknowledgement_status = "suppressed_by_dedupe" if parent_alert else "unacknowledged"
        created_at = _format_datetime(produced_at)
        source_ref = linked_metric_id if linked_metric_id else linked_log_id
        alert = AlertEvent(
            alert_id=f"alert-{_stable_hash([dedupe_key, linked_log_id, parent_id])[:16]}",
            alert_type=alert_type,
            severity=severity,
            triggering_condition=triggering_condition,
            run_id=run_id,
            motor_id=motor_id,
            stage_name=stage_name,
            linked_log_id=linked_log_id,
            linked_metric_id=linked_metric_id,
            timestamp=created_at,
            dedupe_key=dedupe_key,
            acknowledgement_status=acknowledgement_status,
            version_id=SCHEMA_VERSION,
            created_at=created_at,
            updated_at=created_at,
            version_hash="",
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=created_at,
            parent_id=parent_id,
        )
        alert = _with_version_hash(alert)
        self._alerts_by_dedupe_key[dedupe_key] = alert
        return alert

    def _build_retry_decision(
        self,
        observed_event: Mapping[str, Any],
        execution_log: ExecutionLog,
        produced_at: datetime,
    ) -> RetryDecision:
        attempt_number = int(observed_event.get("attempt_number", 0))
        max_attempts = int(self._retry_policy["max_attempts"])
        error_type = observed_event.get("error_type")
        is_failure = (
            observed_event["event_type"] in {"failed", "timeout", "aborted"}
            or observed_event["status"] in {"failed", "timed_out", "aborted"}
        )
        linked_failure_event_id: Optional[str] = None

        if not is_failure:
            decision = "suppress_retry"
            reason_code = "no_failure"
            retry_after_seconds = 0
        elif error_type in self._retry_policy["retryable_error_types"] and attempt_number < max_attempts:
            decision = "retry"
            reason_code = "retryable_failure"
            retry_after_seconds = int(self._retry_policy["retry_after_seconds"])
            linked_failure_event_id = str(observed_event["source_event_id"])
        elif error_type in self._retry_policy["retryable_error_types"]:
            decision = "abort"
            reason_code = "max_attempts_reached"
            retry_after_seconds = 0
            linked_failure_event_id = str(observed_event["source_event_id"])
        else:
            decision = "abort"
            reason_code = "non_retryable_error"
            retry_after_seconds = 0
            linked_failure_event_id = str(observed_event["source_event_id"])

        parent_decision = (
            self._retry_decisions_by_failure_event_id.get(linked_failure_event_id)
            if linked_failure_event_id
            else None
        )
        parent_id = parent_decision.decision_id if parent_decision else None
        policy_ref = str(
            self._retry_policy.get("policy_ref")
            or f"phase_contracts:motor_001:{observed_event['motor_id']}:{observed_event['stage_name']}"
        )
        created_at = _format_datetime(produced_at)
        source_ref = linked_failure_event_id or execution_log.log_id
        retry_decision = RetryDecision(
            decision_id=f"decision-{_stable_hash([source_ref, decision, reason_code, attempt_number, parent_id])[:16]}",
            decision=decision,
            reason_code=reason_code,
            attempt_number=attempt_number,
            max_attempts=max_attempts,
            retry_after_seconds=retry_after_seconds,
            linked_failure_event_id=linked_failure_event_id,
            linked_log_id=execution_log.log_id,
            run_id=str(observed_event["run_id"]),
            motor_id=str(observed_event["motor_id"]),
            stage_name=str(observed_event["stage_name"]),
            policy_ref=policy_ref,
            timestamp=created_at,
            version_id=SCHEMA_VERSION,
            created_at=created_at,
            updated_at=created_at,
            version_hash="",
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=created_at,
            parent_id=parent_id,
        )
        return _with_version_hash(retry_decision)

    def _reject(
        self,
        event: Mapping[str, Any],
        rejection_code: str,
        alert_events: Tuple[AlertEvent, ...] = (),
    ) -> ProcessingResult:
        if rejection_code not in REJECTION_CODES:
            rejection_code = "INVALID_EVENT_SHAPE"
        rejected = dict(event)
        produced_at = (
            _parse_datetime(rejected.get("produced_at"))
            or _parse_datetime(rejected.get("received_at"))
            or _parse_datetime(rejected.get("timestamp"))
            or EPOCH
        )
        rejected["validation_status"] = "rejected"
        rejected["rejection_code"] = rejection_code
        rejected["produced_by_motor"] = MOTOR_ID
        rejected["produced_at"] = _format_datetime(produced_at)
        rejected.setdefault("version_id", SCHEMA_VERSION)
        rejected.setdefault("source_ref", rejected.get("source_event_id", "unaccepted-input"))
        rejected.setdefault("created_at", _format_datetime(produced_at))
        rejected.setdefault("updated_at", _format_datetime(produced_at))
        rejected["version_hash"] = _stable_hash(_without_version_hash(rejected))
        return ProcessingResult(
            observed_event=rejected,
            execution_log=None,
            metric_records=(),
            alert_events=alert_events,
            retry_decision=None,
            rejection_code=rejection_code,
        )


def _normalize_phase_contracts(phase_contracts: Any) -> Dict[str, Set[str]]:
    allowed: Dict[str, Set[str]] = {}

    def add_scope(motor_id: Any, stages: Any) -> None:
        if motor_id is None:
            return
        motor_key = str(motor_id)
        if motor_key not in allowed:
            allowed[motor_key] = set()
        if stages is None:
            return
        if isinstance(stages, str):
            allowed[motor_key].add(stages)
            return
        if isinstance(stages, Mapping):
            nested = (
                stages.get("stages")
                or stages.get("stage_names")
                or stages.get("allowed_stages")
                or stages.get("stage_name")
            )
            add_scope(motor_key, nested)
            return
        if isinstance(stages, Iterable):
            for stage in stages:
                if isinstance(stage, Mapping):
                    add_scope(motor_key, stage.get("stage_name") or stage.get("name"))
                elif stage is not None:
                    allowed[motor_key].add(str(stage))

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            if "phase_contracts" in node:
                visit(node["phase_contracts"])
            if "motors" in node:
                visit(node["motors"])
            if "allowed_motors" in node:
                visit(node["allowed_motors"])
            if "motor_id" in node:
                stages = (
                    node.get("stages")
                    or node.get("stage_names")
                    or node.get("allowed_stages")
                    or node.get("stage_name")
                )
                add_scope(node["motor_id"], stages)
            for key, value in node.items():
                if key in {"phase_contracts", "motors", "allowed_motors", "motor_id"}:
                    continue
                if str(key).startswith("motor_"):
                    add_scope(key, value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
            for item in node:
                visit(item)

    visit(phase_contracts)
    return {motor: stages for motor, stages in allowed.items() if stages}


def _normalize_retry_policy(config: Mapping[str, Any]) -> Dict[str, Any]:
    max_attempts = config.get("max_attempts", 0)
    if not isinstance(max_attempts, int) or max_attempts < 0:
        raise ValueError("retry_policy_config.max_attempts must be a non-negative integer")

    retryable_error_types = config.get("retryable_error_types", ())
    if isinstance(retryable_error_types, str):
        retryable_error_types = [retryable_error_types]

    retry_after_seconds = _retry_after_seconds(config.get("backoff_profile", 0))
    timeout_seconds = config.get("timeout_seconds", 300)
    if not isinstance(timeout_seconds, int) or timeout_seconds < 0:
        raise ValueError("retry_policy_config.timeout_seconds must be a non-negative integer")

    return {
        "max_attempts": max_attempts,
        "retryable_error_types": {str(item) for item in retryable_error_types},
        "retry_after_seconds": retry_after_seconds,
        "timeout_seconds": timeout_seconds,
        "policy_ref": config.get("policy_ref"),
    }


def _retry_after_seconds(backoff_profile: Any) -> int:
    if isinstance(backoff_profile, int):
        return max(0, backoff_profile)
    if isinstance(backoff_profile, Mapping):
        seconds = backoff_profile.get("seconds", backoff_profile.get("retry_after_seconds", 0))
        return max(0, int(seconds))
    if isinstance(backoff_profile, str):
        match = re.fullmatch(r"fixed_(\d+)_seconds", backoff_profile)
        if match:
            return int(match.group(1))
        if backoff_profile.isdigit():
            return int(backoff_profile)
    return 0


def _contains_unsupported_operation(event: Mapping[str, Any]) -> bool:
    checked_values: List[str] = []
    for field in ("payload_ref", "requested_operation", "operation", "payload"):
        if field in event and event[field] is not None:
            checked_values.append(json.dumps(event[field], sort_keys=True, default=str).lower())
    return any(marker in " ".join(checked_values) for marker in UNSUPPORTED_OPERATION_MARKERS)


def _canonical_event(event: Mapping[str, Any]) -> str:
    ignored = {"validation_status", "rejection_code", "created_at", "updated_at", "version_hash"}
    return _canonical_json({key: value for key, value in event.items() if key not in ignored})


def _compose_source_ref(source_log_ids: Sequence[str], source_event_ids: Sequence[str]) -> str:
    parts = []
    if source_log_ids:
        parts.append("logs:" + ",".join(source_log_ids))
    if source_event_ids:
        parts.append("events:" + ",".join(source_event_ids))
    return "|".join(parts)


def _parse_datetime(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_datetime(value: datetime) -> str:
    normalized = value.astimezone(timezone.utc)
    if normalized.microsecond:
        return normalized.isoformat().replace("+00:00", "Z")
    return normalized.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _with_version_hash(record: Any) -> Any:
    record_dict = asdict(record)
    return replace(record, version_hash=_stable_hash(_without_version_hash(record_dict)))


def _without_version_hash(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "version_hash"}


def _stable_hash(payload: Any) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
