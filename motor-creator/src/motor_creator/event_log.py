from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .config import EVENT_LOG_FILE, RUNTIME_DIR


class EventType(str, Enum):
    ORCHESTRATOR_START = "orchestrator_start"
    ORCHESTRATOR_ABORT = "orchestrator_abort"
    CYCLE_DETECTED = "cycle_detected"
    MOTOR_SELECTED = "motor_selected"
    DEPENDENCY_CHECK_PASS = "dependency_check_pass"
    DEPENDENCY_CHECK_FAIL = "dependency_check_fail"
    GATE_EVALUATED = "gate_evaluated"
    GATE_PASSED = "gate_passed"
    GATE_FAILED = "gate_failed"
    GATE_MANUAL_PENDING = "gate_manual_pending"
    STAGE_ADVANCED = "stage_advanced"
    MOTOR_CLOSED = "motor_closed"
    MOTOR_BLOCKED = "motor_blocked"
    MOTOR_PAUSED = "motor_paused"
    ARTIFACT_CREATED = "artifact_created"
    CORRECTION_OPENED = "correction_opened"
    MANUAL_APPROVED = "manual_approved"
    STATE_WRITTEN = "state_written"
    DRY_RUN = "dry_run"
    ERROR = "error"


def append_event(
    event_type: EventType,
    motor_id: str,
    payload: dict[str, Any],
    log_path: Path = EVENT_LOG_FILE,
    dry_run: bool = False,
) -> None:
    """Append a single event to the JSONL audit log. No-op on dry_run."""
    if dry_run:
        return

    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type.value,
        "motor_id": motor_id,
        **payload,
    }
    line = json.dumps(event, ensure_ascii=False)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_events(
    log_path: Path = EVENT_LOG_FILE,
    motor_id: str | None = None,
) -> list[dict]:
    """Read all events from log, optionally filtered by motor_id."""
    if not log_path.exists():
        return []
    events: list[dict] = []
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if motor_id is None or ev.get("motor_id") == motor_id:
                    events.append(ev)
            except json.JSONDecodeError:
                continue
    return events
