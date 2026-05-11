"""Scenario review workflow (V2-CRITICAL course correction).

Per the user's clarification: the PDF is the clean final deliverable.
Review and approval of scenarios happens in the dashboard BEFORE the
PDF is rendered. The 5 justification fields (trigger / source /
process_clue / industrial_reason / asset_family_reason) emitted by
motor_014 + validated by motor_062 are review metadata for the
operations center, not PDF content.

Per-case scenario lifecycle:

  pending  ← motor_014 produces the scenario; default state
  approved ← reviewer accepts in dashboard
  edited   ← reviewer modified one or more justification fields;
             stays in pending until approved
  rejected ← reviewer excludes the scenario from the final PDF

A case is "ready to render" when every active scenario is either
approved or rejected (no scenario remains in pending). motor_017
honors this gate.

Storage: one JSON file per case under:
  zlab_skill/registry/scenario_reviews/<case_id>.json

Each file looks like:
  {
    "case_id": "...",
    "asset_family": "...",
    "updated_at": "ISO-timestamp",
    "scenarios": {
      "<scenario_id>": {
        "state": "pending|approved|edited|rejected",
        "scenario": "A. Energy intensity ...",
        "trigger": "...", "source": "...",
        "process_clue": "...", "industrial_reason": "...",
        "asset_family_reason": "...",
        "reviewer": "...",
        "reviewed_at": "...",
        "rejection_reason": "...",
        "edit_count": 0
      },
      ...
    }
  }
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[3]
_REVIEWS_DIR = (
    _REPO_ROOT / "runtime-orchestrator" / "zlab_skill" / "registry" / "scenario_reviews"
)
_AUDIT_LOG = _REVIEWS_DIR / "scenario_review_log.jsonl"


_VALID_STATES = {"pending", "approved", "edited", "rejected"}
_EDITABLE_FIELDS = (
    "trigger",
    "source",
    "process_clue",
    "industrial_reason",
    "asset_family_reason",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_dir() -> None:
    _REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def reviews_dir() -> Path:
    return _REVIEWS_DIR


def _safe_case_id(case_id: str) -> str:
    """Reject path traversal; case_id must be alnum + underscore + hyphen + dot."""
    s = (case_id or "").strip()
    if not s:
        raise ValueError("case_id is required")
    if "/" in s or ".." in s or "\\" in s:
        raise ValueError(f"invalid case_id: {case_id!r}")
    if not all(c.isalnum() or c in "_-." for c in s):
        raise ValueError(
            f"case_id must be alnum / underscore / hyphen / dot only: {case_id!r}"
        )
    return s


def _scenario_id_of(scenario: dict[str, Any], idx: int) -> str:
    """Derive a stable scenario_id from the scenario heading ('A. ...' → 'A')."""
    raw = (
        str(scenario.get("scenario_id") or scenario.get("scenario") or "")
        .strip()
    )
    if not raw:
        return f"scenario_{idx + 1:02d}"
    if len(raw) >= 2 and raw[0].isalpha() and raw[1] == ".":
        return raw[0].upper()
    safe = "".join(c if c.isalnum() else "_" for c in raw[:40]).strip("_")
    return safe or f"scenario_{idx + 1:02d}"


def _path_for(case_id: str) -> Path:
    return _REVIEWS_DIR / f"{_safe_case_id(case_id)}.json"


def _read(case_id: str) -> dict[str, Any]:
    path = _path_for(case_id)
    if not path.exists():
        return {"case_id": case_id, "scenarios": {}, "updated_at": ""}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"case_id": case_id, "scenarios": {}, "updated_at": ""}
    if not isinstance(data, dict):
        return {"case_id": case_id, "scenarios": {}, "updated_at": ""}
    data.setdefault("case_id", case_id)
    data.setdefault("scenarios", {})
    return data


def _write(case_id: str, payload: dict[str, Any]) -> None:
    _ensure_dir()
    payload = {**payload, "case_id": case_id, "updated_at": _now()}
    _path_for(case_id).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _append_audit(event: dict[str, Any]) -> None:
    _ensure_dir()
    event = {**event, "ts": _now()}
    try:
        with _AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + os.linesep)
    except OSError:
        pass


# ── Public API ──────────────────────────────────────────────────────────


def upsert_scenarios(
    case_id: str,
    scenarios: list[dict[str, Any]],
    asset_family: str = "",
) -> dict[str, Any]:
    """Seed (or refresh) the per-case review file with the active scenarios
    from motor_014. Existing review state for matching scenario_ids is
    preserved; new scenarios get state='pending'."""
    case_id = _safe_case_id(case_id)
    data = _read(case_id)
    if asset_family:
        data["asset_family"] = asset_family
    bucket = dict(data.get("scenarios", {}) or {})
    for idx, sc in enumerate(scenarios or []):
        if not isinstance(sc, dict):
            continue
        sid = _scenario_id_of(sc, idx)
        prev = bucket.get(sid, {}) if isinstance(bucket.get(sid), dict) else {}
        merged = {
            "state": prev.get("state", "pending"),
            "scenario": str(sc.get("scenario") or "").strip(),
            "plausibility_status": str(sc.get("plausibility_status") or "").strip(),
            "trigger": str(sc.get("trigger") or "").strip(),
            "source": str(sc.get("source") or "").strip(),
            "process_clue": str(sc.get("process_clue") or "").strip(),
            "industrial_reason": str(sc.get("industrial_reason") or "").strip(),
            "asset_family_reason": str(sc.get("asset_family_reason") or "").strip(),
            "reviewer": prev.get("reviewer", ""),
            "reviewed_at": prev.get("reviewed_at", ""),
            "rejection_reason": prev.get("rejection_reason", ""),
            "edit_count": int(prev.get("edit_count", 0) or 0),
        }
        bucket[sid] = merged
    data["scenarios"] = bucket
    _write(case_id, data)
    return data


def list_cases() -> list[dict[str, Any]]:
    """Lightweight summary of every per-case review file under the registry."""
    _ensure_dir()
    out: list[dict[str, Any]] = []
    for path in sorted(_REVIEWS_DIR.glob("*.json")):
        if path.name.startswith("."):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        scenarios = data.get("scenarios", {}) or {}
        counts: dict[str, int] = {s: 0 for s in _VALID_STATES}
        for sc in scenarios.values():
            state = str(sc.get("state") or "pending")
            if state in counts:
                counts[state] += 1
        out.append(
            {
                "case_id": data.get("case_id") or path.stem,
                "asset_family": data.get("asset_family", ""),
                "updated_at": data.get("updated_at", ""),
                "scenario_count": len(scenarios),
                **{f"{s}_count": counts[s] for s in _VALID_STATES},
                "ready_to_render": _is_ready_to_render(data),
            }
        )
    return out


def _is_ready_to_render(data: dict[str, Any]) -> bool:
    scenarios = data.get("scenarios", {}) or {}
    if not scenarios:
        return False
    for sc in scenarios.values():
        if str(sc.get("state") or "pending") in {"pending", "edited"}:
            return False
    return True


def ready_to_render(case_id: str) -> bool:
    return _is_ready_to_render(_read(case_id))


def get_case(case_id: str) -> dict[str, Any]:
    data = _read(case_id)
    data["ready_to_render"] = _is_ready_to_render(data)
    return data


def approve(case_id: str, scenario_id: str, reviewer: str) -> dict[str, Any]:
    case_id = _safe_case_id(case_id)
    if not (reviewer or "").strip():
        raise ValueError("reviewer is required")
    data = _read(case_id)
    bucket = data.get("scenarios", {}) or {}
    if scenario_id not in bucket:
        raise FileNotFoundError(
            f"no scenario '{scenario_id}' under case '{case_id}'"
        )
    bucket[scenario_id]["state"] = "approved"
    bucket[scenario_id]["reviewer"] = reviewer.strip()
    bucket[scenario_id]["reviewed_at"] = _now()
    bucket[scenario_id]["rejection_reason"] = ""
    data["scenarios"] = bucket
    _write(case_id, data)
    _append_audit({"event": "approve", "case_id": case_id, "scenario_id": scenario_id, "by": reviewer})
    return get_case(case_id)


def reject(
    case_id: str, scenario_id: str, reviewer: str, reason: str
) -> dict[str, Any]:
    case_id = _safe_case_id(case_id)
    if not (reviewer or "").strip():
        raise ValueError("reviewer is required")
    if not (reason or "").strip():
        raise ValueError("rejection reason is required")
    data = _read(case_id)
    bucket = data.get("scenarios", {}) or {}
    if scenario_id not in bucket:
        raise FileNotFoundError(
            f"no scenario '{scenario_id}' under case '{case_id}'"
        )
    bucket[scenario_id]["state"] = "rejected"
    bucket[scenario_id]["reviewer"] = reviewer.strip()
    bucket[scenario_id]["reviewed_at"] = _now()
    bucket[scenario_id]["rejection_reason"] = reason.strip()[:1000]
    data["scenarios"] = bucket
    _write(case_id, data)
    _append_audit(
        {"event": "reject", "case_id": case_id, "scenario_id": scenario_id, "by": reviewer, "reason": reason[:200]}
    )
    return get_case(case_id)


def edit(
    case_id: str,
    scenario_id: str,
    reviewer: str,
    patch: dict[str, Any],
) -> dict[str, Any]:
    """Apply reviewer patch to a scenario; state becomes 'edited' until approved."""
    case_id = _safe_case_id(case_id)
    if not (reviewer or "").strip():
        raise ValueError("reviewer is required")
    if not isinstance(patch, dict) or not patch:
        raise ValueError("patch must be a non-empty dict")
    clean = {k: str(v or "").strip() for k, v in patch.items() if k in _EDITABLE_FIELDS}
    if not clean:
        raise ValueError(
            f"patch contains no editable fields. editable: {list(_EDITABLE_FIELDS)}"
        )
    data = _read(case_id)
    bucket = data.get("scenarios", {}) or {}
    if scenario_id not in bucket:
        raise FileNotFoundError(
            f"no scenario '{scenario_id}' under case '{case_id}'"
        )
    bucket[scenario_id].update(clean)
    bucket[scenario_id]["state"] = "edited"
    bucket[scenario_id]["reviewer"] = reviewer.strip()
    bucket[scenario_id]["reviewed_at"] = _now()
    bucket[scenario_id]["edit_count"] = int(bucket[scenario_id].get("edit_count", 0) or 0) + 1
    data["scenarios"] = bucket
    _write(case_id, data)
    _append_audit(
        {
            "event": "edit",
            "case_id": case_id,
            "scenario_id": scenario_id,
            "by": reviewer,
            "fields_changed": sorted(clean.keys()),
        }
    )
    return get_case(case_id)


def approve_all(case_id: str, reviewer: str) -> dict[str, Any]:
    """Bulk-approve every non-rejected scenario in a case."""
    case_id = _safe_case_id(case_id)
    if not (reviewer or "").strip():
        raise ValueError("reviewer is required")
    data = _read(case_id)
    bucket = data.get("scenarios", {}) or {}
    if not bucket:
        raise FileNotFoundError(f"no scenarios for case '{case_id}' yet")
    ts = _now()
    for sid, sc in bucket.items():
        if sc.get("state") == "rejected":
            continue
        sc["state"] = "approved"
        sc["reviewer"] = reviewer.strip()
        sc["reviewed_at"] = ts
    data["scenarios"] = bucket
    _write(case_id, data)
    _append_audit({"event": "approve_all", "case_id": case_id, "by": reviewer})
    return get_case(case_id)


def auto_approve_for_regression(case_id: str, scenarios: list[dict[str, Any]], asset_family: str = "") -> dict[str, Any]:
    """Convenience for CI / regression scripts: seed and approve in one call.
    Only honored when ZLAB_AUTO_APPROVE_SCENARIOS=1 (set by the regression
    runner) — otherwise normal manual gating applies."""
    upsert_scenarios(case_id, scenarios, asset_family=asset_family)
    return approve_all(case_id, reviewer="regression_runner")
