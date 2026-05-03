from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .config import GOVERNANZA, MOTOR_STATE_FILENAME
from .models import MotorEntry, MotorState


def get_motor_dir(motor_entry: MotorEntry, governanza: Path = GOVERNANZA) -> Path:
    return governanza / motor_entry.slug


def write_motor_state(
    motor_entry: MotorEntry,
    state: MotorState,
    governanza: Path = GOVERNANZA,
    dry_run: bool = False,
) -> Path:
    """
    Atomic write of motor_state.json.
    Creates the motor directory if it doesn't exist.
    Uses tmp file + os.replace to prevent partial writes.
    """
    motor_dir = get_motor_dir(motor_entry, governanza)

    if not dry_run:
        motor_dir.mkdir(parents=True, exist_ok=True)

    target = motor_dir / MOTOR_STATE_FILENAME
    payload = json.dumps(state.to_dict(), indent=2, ensure_ascii=False)

    if dry_run:
        return target

    # Write to temp file in same directory, then atomically replace
    fd, tmp_path = tempfile.mkstemp(dir=motor_dir, suffix=".tmp", prefix="motor_state_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp_path, target)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    return target
