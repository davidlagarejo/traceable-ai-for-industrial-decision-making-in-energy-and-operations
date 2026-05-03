from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_STALE_WITH_PID_SECONDS = 20
_STALE_WITHOUT_PID_SECONDS = 30


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _stale_age_seconds(data: dict[str, Any], path: Path | None) -> float | None:
    dt = _parse_dt(data.get("last_heartbeat_at")) or _parse_dt(data.get("started_at"))
    if dt is None and path is not None and path.exists():
        try:
            dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except Exception:
            dt = None
    if dt is None:
        return None
    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def _reconciled_terminal_status(data: dict[str, Any]) -> str:
    motor_results = data.get("motor_results", {}) or {}
    has_progress = any(
        (result or {}).get("status") in {"completed", "cached", "stub", "failed"}
        for result in motor_results.values()
    )
    return "partial" if has_progress else "failed"


def reconcile_run_manifest_dict(
    data: dict[str, Any],
    *,
    path: Path | None = None,
) -> tuple[dict[str, Any], bool]:
    if not isinstance(data, dict) or not data:
        return data, False
    if data.get("status") != "running":
        return data, False

    runner_pid = data.get("runner_pid")
    age_s = _stale_age_seconds(data, path)
    ttl = _STALE_WITH_PID_SECONDS if runner_pid else _STALE_WITHOUT_PID_SECONDS

    if runner_pid and _pid_alive(int(runner_pid)):
        return data, False
    if age_s is not None and age_s < ttl:
        return data, False

    reconciled = dict(data)
    reconciled["status"] = _reconciled_terminal_status(reconciled)
    reconciled["completed_at"] = reconciled.get("completed_at") or _now()
    reconciled["reconciled_from_status"] = "running"
    reconciled["reconciled_reason"] = (
        "runner_pid missing or no longer alive; run marked stale and reconciled automatically"
    )
    reconciled["error"] = reconciled.get("error") or "Run interrupted before clean completion."

    motor_results = {
        mid: dict(result or {})
        for mid, result in (reconciled.get("motor_results", {}) or {}).items()
    }
    for result in motor_results.values():
        if result.get("status") == "running":
            result["status"] = "failed"
            result["error"] = result.get("error") or "Motor interrupted before completion."
    reconciled["motor_results"] = motor_results
    return reconciled, True


def load_run_manifest(path: Path, *, persist_reconciliation: bool = True) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}

    reconciled, changed = reconcile_run_manifest_dict(data, path=path)
    if changed and persist_reconciliation:
        try:
            path.write_text(json.dumps(reconciled, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
    return reconciled
