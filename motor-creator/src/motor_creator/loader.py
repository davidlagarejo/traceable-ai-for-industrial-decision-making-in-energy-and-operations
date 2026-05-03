from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import (
    GOVERNANZA,
    MOTOR_DEPENDENCIES_FILE,
    MOTOR_STATE_FILENAME,
)
from .models import MotorEntry, MotorState, STAGE_SEQUENCE


def load_motor_dependencies(path: Path = MOTOR_DEPENDENCIES_FILE) -> dict[str, MotorEntry]:
    """Load motor_dependencies.json and return all motor entries."""
    with open(path) as f:
        raw = json.load(f)

    motors: dict[str, MotorEntry] = {}
    for motor_id, data in raw["motors"].items():
        motors[motor_id] = MotorEntry(
            motor_id=motor_id,
            name=data["name"],
            group=data["group"],
            catalog_status=data["catalog_status"],
            requires=data.get("requires", []),
            orchestrator_eligible=data.get("orchestrator_eligible", True),
        )
    return motors


def motor_dir(motor_entry: MotorEntry, governanza: Path = GOVERNANZA) -> Path:
    """Return the directory path for a motor."""
    return governanza / motor_entry.slug


def motor_state_path(motor_entry: MotorEntry, governanza: Path = GOVERNANZA) -> Path:
    return motor_dir(motor_entry, governanza) / MOTOR_STATE_FILENAME


def load_motor_state(
    motor_entry: MotorEntry, governanza: Path = GOVERNANZA
) -> Optional[MotorState]:
    """Load motor_state.json for a motor. Returns None if not found."""
    state_path = motor_state_path(motor_entry, governanza)
    if not state_path.exists():
        return None

    with open(state_path) as f:
        data = json.load(f)

    return MotorState(
        motor_id=data["motor_id"],
        motor_name=data["motor_name"],
        purpose=data.get("purpose", ""),
        current_stage=data["current_stage"],
        stage_sequence=data.get("stage_sequence", [s.value for s in STAGE_SEQUENCE]),
        completed_stages=data.get("completed_stages", []),
        artifacts=data.get("artifacts", {}),
        missing_artifacts=data.get("missing_artifacts", []),
        validations=data.get("validations", []),
        corrections=data.get("corrections", []),
        status=data["status"],
        blocked=data.get("blocked", False),
        paused=data.get("paused", False),
        waiting_on=data.get("waiting_on"),
        closure=data.get("closure", {"is_closed": False, "closed_at": None, "closure_notes": ""}),
        notes=data.get("notes", ""),
        updated_at=data.get("updated_at", ""),
    )


def initialize_motor_state(motor_entry: MotorEntry) -> MotorState:
    """Create a fresh not_started state for a motor that has no state file yet."""
    now = datetime.now(timezone.utc).isoformat()
    stages = [s.value for s in STAGE_SEQUENCE]

    artifacts: dict = {}
    from .models import STAGE_ARTIFACTS
    for stage in STAGE_SEQUENCE:
        artifacts[stage.value] = {
            "exists": False,
            "items": STAGE_ARTIFACTS[stage],
        }

    return MotorState(
        motor_id=motor_entry.motor_id,
        motor_name=motor_entry.name,
        purpose="",
        current_stage=stages[0],
        stage_sequence=stages,
        completed_stages=[],
        artifacts=artifacts,
        missing_artifacts=[],
        validations=[],
        corrections=[],
        status="not_started",
        blocked=False,
        paused=False,
        waiting_on=None,
        closure={"is_closed": False, "closed_at": None, "closure_notes": ""},
        notes="",
        updated_at=now,
    )


def get_or_init_state(
    motor_entry: MotorEntry, governanza: Path = GOVERNANZA
) -> MotorState:
    """Load existing state or initialize a fresh one."""
    state = load_motor_state(motor_entry, governanza)
    if state is None:
        return initialize_motor_state(motor_entry)
    return state


def load_all_states(
    motors: dict[str, MotorEntry], governanza: Path = GOVERNANZA
) -> dict[str, MotorState]:
    """Load (or init) state for all motors."""
    return {
        motor_id: get_or_init_state(entry, governanza)
        for motor_id, entry in motors.items()
    }
