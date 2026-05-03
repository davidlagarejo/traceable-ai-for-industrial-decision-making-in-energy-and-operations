"""Deterministic implementation of motor_024.

The registry captures exception events, override records, and tension signals
from all motors in the system and emits immutable GovernanceEvent objects with
full lineage traceability. The motor never resolves exceptions, never changes
policies, and never enriches or modifies the incoming event payload.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from .models import (
    ExceptionRecord,
    GovernanceEvent,
    GovernanceEventResult,
    GovernanceRejection,
    TensionSignal,
)

MOTOR_ID = "motor_024"

_DENIED_TOKENS = (":deny", ":denied", ":blocked", ":disallow", ":forbid", "not_allowed")
_UNSTABLE_VALUES = {"", "unknown", "undefined", "null", "none"}
_VALID_EVENT_TYPES = {"exception", "override", "tension"}


class GovernanceEventRegistry:
    """Register governance signals emitted by all motors in the system."""

    def __init__(self) -> None:
        self._registry: dict[str, GovernanceEvent] = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def register_exception(
        self,
        *,
        source_motor_id: str,
        exception_code: str,
        exception_payload: Mapping[str, Any],
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
    ) -> GovernanceEventResult:
        raw_payload = {
            "source_motor_id": source_motor_id,
            "event_type": "exception",
            "exception_code": exception_code,
            "exception_payload": dict(exception_payload),
            "captured_at": captured_at,
            "phase_contract_ref": phase_contract_ref,
            "lineage_context_ref": lineage_context_ref,
        }
        return self._register(
            event_type="exception",
            source_motor_id=source_motor_id,
            captured_at=captured_at,
            phase_contract_ref=phase_contract_ref,
            lineage_context_ref=lineage_context_ref,
            raw_payload=raw_payload,
            extra={"exception_code": exception_code, "exception_payload": dict(exception_payload)},
        )

    def register_override(
        self,
        *,
        source_motor_id: str,
        override_id: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
        policy_ref: str = "",
    ) -> GovernanceEventResult:
        raw_payload = {
            "source_motor_id": source_motor_id,
            "event_type": "override",
            "override_id": override_id,
            "policy_ref": policy_ref,
            "captured_at": captured_at,
            "phase_contract_ref": phase_contract_ref,
            "lineage_context_ref": lineage_context_ref,
        }
        return self._register(
            event_type="override",
            source_motor_id=source_motor_id,
            captured_at=captured_at,
            phase_contract_ref=phase_contract_ref,
            lineage_context_ref=lineage_context_ref,
            raw_payload=raw_payload,
            extra={},
        )

    def register_tension(
        self,
        *,
        motor_a_id: str,
        motor_b_id: str,
        conflict_description: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
        source_motor_id: str = "",
    ) -> GovernanceEventResult:
        effective_source = source_motor_id or motor_a_id
        raw_payload = {
            "source_motor_id": effective_source,
            "event_type": "tension",
            "motor_a_id": motor_a_id,
            "motor_b_id": motor_b_id,
            "conflict_description": conflict_description,
            "captured_at": captured_at,
            "phase_contract_ref": phase_contract_ref,
            "lineage_context_ref": lineage_context_ref,
        }
        rejection = self._validate_tension_actors(motor_a_id, motor_b_id)
        if rejection is not None:
            return GovernanceEventResult(
                governance_event=None,
                exception_record=None,
                tension_signal=None,
                rejection=rejection,
            )
        return self._register(
            event_type="tension",
            source_motor_id=effective_source,
            captured_at=captured_at,
            phase_contract_ref=phase_contract_ref,
            lineage_context_ref=lineage_context_ref,
            raw_payload=raw_payload,
            extra={
                "motor_a_id": motor_a_id,
                "motor_b_id": motor_b_id,
                "conflict_description": conflict_description,
            },
        )

    # ── Internal orchestration ────────────────────────────────────────────────

    def _register(
        self,
        *,
        event_type: str,
        source_motor_id: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
        raw_payload: dict[str, Any],
        extra: dict[str, Any],
    ) -> GovernanceEventResult:
        rejection = self._validate_preconditions(
            event_type=event_type,
            source_motor_id=source_motor_id,
            captured_at=captured_at,
            phase_contract_ref=phase_contract_ref,
            lineage_context_ref=lineage_context_ref,
        )
        if rejection is not None:
            return GovernanceEventResult(
                governance_event=None,
                exception_record=None,
                tension_signal=None,
                rejection=rejection,
            )

        now = self._now_iso()
        governance_event_id = self._stable_id(
            "governance_event",
            source_motor_id,
            event_type,
            captured_at,
            lineage_context_ref,
        )

        if governance_event_id in self._registry:
            return GovernanceEventResult(
                governance_event=None,
                exception_record=None,
                tension_signal=None,
                rejection=GovernanceRejection(
                    error_code="GOV_DUPLICATE_EVENT",
                    error_message=f"governance_event_id already exists: {governance_event_id}",
                    source_motor_id=source_motor_id,
                    captured_at=captured_at,
                ),
            )

        gov_fields: dict[str, Any] = {
            "governance_event_id": governance_event_id,
            "event_type": event_type,
            "source_motor_id": source_motor_id,
            "captured_at": captured_at,
            "phase_contract_ref": phase_contract_ref,
            "lineage_id": lineage_context_ref,
            "raw_event_payload": raw_payload,
            "version_id": f"{governance_event_id}:v1",
            "created_at": now,
            "updated_at": now,
            "produced_by_motor": MOTOR_ID,
            "produced_at": now,
            "parent_id": lineage_context_ref,
        }
        gov_fields["version_hash"] = self._version_hash(gov_fields)
        governance_event = GovernanceEvent(**gov_fields)
        self._registry[governance_event_id] = governance_event

        exception_record: Optional[ExceptionRecord] = None
        tension_signal: Optional[TensionSignal] = None

        if event_type == "exception":
            exception_record = self._build_exception_record(
                governance_event_id=governance_event_id,
                source_motor_id=source_motor_id,
                lineage_id=lineage_context_ref,
                now=now,
                extra=extra,
            )
        elif event_type == "tension":
            tension_signal = self._build_tension_signal(
                governance_event_id=governance_event_id,
                lineage_id=lineage_context_ref,
                now=now,
                extra=extra,
            )

        return GovernanceEventResult(
            governance_event=governance_event,
            exception_record=exception_record,
            tension_signal=tension_signal,
            rejection=None,
        )

    def _build_exception_record(
        self,
        *,
        governance_event_id: str,
        source_motor_id: str,
        lineage_id: str,
        now: str,
        extra: dict[str, Any],
    ) -> ExceptionRecord:
        exception_code = extra.get("exception_code", "")
        exception_record_id = self._stable_id(
            "exception_record", governance_event_id, exception_code
        )
        fields: dict[str, Any] = {
            "exception_record_id": exception_record_id,
            "governance_event_id": governance_event_id,
            "source_motor_id": source_motor_id,
            "exception_code": exception_code,
            "exception_payload": extra.get("exception_payload", {}),
            "lineage_id": lineage_id,
            "version_id": f"{exception_record_id}:v1",
            "created_at": now,
            "produced_by_motor": MOTOR_ID,
            "produced_at": now,
        }
        fields["version_hash"] = self._version_hash(fields)
        return ExceptionRecord(**fields)

    def _build_tension_signal(
        self,
        *,
        governance_event_id: str,
        lineage_id: str,
        now: str,
        extra: dict[str, Any],
    ) -> TensionSignal:
        motor_a_id = extra.get("motor_a_id", "")
        motor_b_id = extra.get("motor_b_id", "")
        tension_signal_id = self._stable_id(
            "tension_signal", governance_event_id, motor_a_id, motor_b_id
        )
        fields: dict[str, Any] = {
            "tension_signal_id": tension_signal_id,
            "governance_event_id": governance_event_id,
            "motor_a_id": motor_a_id,
            "motor_b_id": motor_b_id,
            "conflict_description": extra.get("conflict_description", ""),
            "lineage_id": lineage_id,
            "version_id": f"{tension_signal_id}:v1",
            "created_at": now,
            "produced_by_motor": MOTOR_ID,
            "produced_at": now,
        }
        fields["version_hash"] = self._version_hash(fields)
        return TensionSignal(**fields)

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate_preconditions(
        self,
        *,
        event_type: str,
        source_motor_id: str,
        captured_at: str,
        phase_contract_ref: str,
        lineage_context_ref: str,
    ) -> Optional[GovernanceRejection]:
        if not self._stable_ref(source_motor_id):
            return GovernanceRejection(
                error_code="GOV_MISSING_REQUIRED_FIELD",
                error_message="source_motor_id is required and must be a stable identifier",
                source_motor_id=source_motor_id,
                captured_at=captured_at,
            )
        if not self._stable_ref(captured_at):
            return GovernanceRejection(
                error_code="GOV_MISSING_REQUIRED_FIELD",
                error_message="captured_at is required",
                source_motor_id=source_motor_id,
                captured_at=captured_at,
            )
        if not self._stable_ref(lineage_context_ref):
            return GovernanceRejection(
                error_code="GOV_MISSING_REQUIRED_FIELD",
                error_message="lineage_context_ref is required",
                source_motor_id=source_motor_id,
                captured_at=captured_at,
            )
        if event_type not in _VALID_EVENT_TYPES:
            return GovernanceRejection(
                error_code="GOV_UNKNOWN_EVENT_TYPE",
                error_message=f"event_type must be one of {sorted(_VALID_EVENT_TYPES)}, got: {event_type!r}",
                source_motor_id=source_motor_id,
                captured_at=captured_at,
            )
        if not self._phase_contract_allows(phase_contract_ref):
            return GovernanceRejection(
                error_code="GOV_PHASE_CONTRACT_DENIED",
                error_message=f"phase_contract_ref does not authorize this event: {phase_contract_ref!r}",
                source_motor_id=source_motor_id,
                captured_at=captured_at,
            )
        return None

    def _validate_tension_actors(
        self, motor_a_id: str, motor_b_id: str
    ) -> Optional[GovernanceRejection]:
        if motor_a_id == motor_b_id:
            return GovernanceRejection(
                error_code="GOV_INVALID_TENSION_ACTORS",
                error_message=f"motor_a_id and motor_b_id must be different, got: {motor_a_id!r}",
                source_motor_id=motor_a_id,
                captured_at="",
            )
        return None

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _stable_ref(self, value: str) -> bool:
        stripped = value.strip() if isinstance(value, str) else ""
        return stripped.lower() not in _UNSTABLE_VALUES

    def _phase_contract_allows(self, phase_contract_ref: str) -> bool:
        if not self._stable_ref(phase_contract_ref):
            return False
        lower = phase_contract_ref.lower()
        return not any(token in lower for token in _DENIED_TOKENS)

    def _stable_id(self, prefix: str, *parts: str) -> str:
        digest = hashlib.sha256(
            "\x1f".join(str(p) for p in parts).encode("utf-8")
        ).hexdigest()[:24]
        return f"{prefix}_{digest}"

    def _version_hash(self, fields: dict[str, Any]) -> str:
        without_hash = {k: v for k, v in fields.items() if k != "version_hash"}
        canonical = json.dumps(without_hash, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _now_iso(self) -> str:
        t = time.gmtime()
        return (
            f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
            f"T{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}Z"
        )
