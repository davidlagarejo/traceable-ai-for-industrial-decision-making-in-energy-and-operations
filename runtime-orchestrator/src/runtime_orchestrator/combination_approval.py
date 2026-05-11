"""Combination approval workflow (V2-LIVE Item 7 — dashboard approval).

Per the RECOVERY_2026-05-09 prompt: combinations MUST be approved by a
human in the dashboard before they activate. Before this module, AI-
proposed combinations were written directly to `combinations/` and
auto-loaded as approved.

This module introduces a 3-state lifecycle:

  combinations_pending/   ← AI writes proposals here
  combinations/           ← user approves them; loader picks them up
  combinations_rejected/  ← user rejects with reason; kept for audit

API consumed by dashboard.py:
  list_pending()              → [{combination_id, name, pattern_ids, ...}]
  list_rejected()             → [{combination_id, reason, rejected_at, ...}]
  propose(payload)            → write to pending/
  approve(combination_id, reviewer) → move pending → approved
  reject(combination_id, reviewer, reason) → move pending → rejected
  reset(combination_id)       → move rejected → pending (re-review)

Each move records a decision in `combination_approval_log.jsonl` (audit
trail). The functions are filesystem-pure and return JSON-serializable
dicts so the dashboard can return them directly to the UI.

CANONICAL PROPOSAL ENTRY POINTS (V2-CRITICAL Item 2):
  - Programmatic:  combination_approval.propose(payload, proposed_by='ai')
  - CLI:           python3 scripts/propose_combination.py path/to/combo.json

DO NOT write JSON files directly to combinations/. That bypasses human
approval. Any AI / automated flow that needs to register a new
combination MUST go through one of the entry points above so the file
lands in combinations_pending/ and waits for review.
"""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_ROOT = _REPO_ROOT / "runtime-orchestrator" / "zlab_skill" / "registry"
_APPROVED_DIR = _REGISTRY_ROOT / "combinations"
_PENDING_DIR = _REGISTRY_ROOT / "combinations_pending"
_REJECTED_DIR = _REGISTRY_ROOT / "combinations_rejected"
_AUDIT_LOG = _REGISTRY_ROOT / "combination_approval_log.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_dirs() -> None:
    for d in (_APPROVED_DIR, _PENDING_DIR, _REJECTED_DIR):
        d.mkdir(parents=True, exist_ok=True)


def approved_dir() -> Path:
    return _APPROVED_DIR


def pending_dir() -> Path:
    return _PENDING_DIR


def rejected_dir() -> Path:
    return _REJECTED_DIR


def _safe_combination_id(combination_id: str) -> str:
    """Reject path traversal and invalid characters. Lower-case, alnum + _."""
    s = (combination_id or "").strip().lower()
    if not s:
        raise ValueError("combination_id is required")
    if "/" in s or ".." in s or "\\" in s:
        raise ValueError(f"invalid combination_id: {combination_id!r}")
    if not all(c.isalnum() or c == "_" for c in s):
        raise ValueError(f"combination_id must be alnum+underscore only: {combination_id!r}")
    return s


def _filename_for(combination_id: str) -> str:
    return f"{_safe_combination_id(combination_id)}.v1.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _scan_dir(directory: Path) -> list[dict[str, Any]]:
    """Return all JSON specs under `directory` as a list, sorted by id."""
    _ensure_dirs()
    rows: list[dict[str, Any]] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if not isinstance(payload, dict) or not payload:
            continue
        payload["__path__"] = str(path)
        payload["__filename__"] = path.name
        rows.append(payload)
    return rows


def _summarize(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact projection for the dashboard list view."""
    return {
        "combination_id": payload.get("id", ""),
        "name": payload.get("name", ""),
        "version": payload.get("version", ""),
        "pattern_ids": list(payload.get("pattern_ids", []) or []),
        "pattern_count": len(payload.get("pattern_ids", []) or []),
        "tad_action": payload.get("tad_action", ""),
        "combined_hypothesis": str(payload.get("combined_hypothesis") or "")[:240],
        "strategic_risk": str(payload.get("strategic_risk") or "")[:240],
        "minimum_evidence_count": len(payload.get("minimum_evidence", []) or []),
        "proposed_at": payload.get("__proposed_at__", ""),
        "proposed_by": payload.get("__proposed_by__", ""),
        "rejected_at": payload.get("__rejected_at__", ""),
        "rejected_by": payload.get("__rejected_by__", ""),
        "rejection_reason": payload.get("__rejection_reason__", ""),
        "approved_at": payload.get("__approved_at__", ""),
        "approved_by": payload.get("__approved_by__", ""),
        "edited_at": payload.get("__edited_at__", ""),
        "edited_by": payload.get("__edited_by__", ""),
        "edit_count": int(payload.get("__edit_count__", 0) or 0),
    }


def _append_audit(record: dict[str, Any]) -> None:
    _ensure_dirs()
    record = {**record, "ts": _now()}
    try:
        with _AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + os.linesep)
    except OSError:
        pass


# ── Public API ──────────────────────────────────────────────────────────


def list_pending() -> list[dict[str, Any]]:
    return [_summarize(p) for p in _scan_dir(_PENDING_DIR)]


def list_approved() -> list[dict[str, Any]]:
    return [_summarize(p) for p in _scan_dir(_APPROVED_DIR)]


def list_rejected() -> list[dict[str, Any]]:
    return [_summarize(p) for p in _scan_dir(_REJECTED_DIR)]


def summary() -> dict[str, int]:
    return {
        "pending_count": len(_scan_dir(_PENDING_DIR)),
        "approved_count": len(_scan_dir(_APPROVED_DIR)),
        "rejected_count": len(_scan_dir(_REJECTED_DIR)),
    }


def propose(payload: dict[str, Any], proposed_by: str = "ai") -> dict[str, Any]:
    """Write a new combination proposal to combinations_pending/.

    The payload must contain an `id` field (combination_id). Stamps the
    record with __proposed_at__ + __proposed_by__ and returns the summary.
    Refuses to overwrite an existing pending/approved/rejected entry with
    the same id (caller must reset/reject the existing one first).
    """
    _ensure_dirs()
    combination_id = _safe_combination_id(payload.get("id", ""))
    fname = _filename_for(combination_id)

    # Conflict detection across all 3 dirs.
    for state, d in (("pending", _PENDING_DIR), ("approved", _APPROVED_DIR), ("rejected", _REJECTED_DIR)):
        if (d / fname).exists():
            raise FileExistsError(
                f"combination_id '{combination_id}' already exists in {state} "
                f"({d / fname}). Reject/reset the existing entry first."
            )

    stamped = {
        **payload,
        "__proposed_at__": _now(),
        "__proposed_by__": proposed_by or "unknown",
    }
    out_path = _PENDING_DIR / fname
    out_path.write_text(json.dumps(stamped, indent=2, ensure_ascii=False), encoding="utf-8")
    _append_audit({"event": "propose", "combination_id": combination_id, "by": proposed_by})
    return _summarize(stamped | {"__path__": str(out_path), "__filename__": out_path.name})


def approve(combination_id: str, reviewer: str) -> dict[str, Any]:
    """Move a pending combination to approved/, stamping reviewer metadata."""
    _ensure_dirs()
    combination_id = _safe_combination_id(combination_id)
    fname = _filename_for(combination_id)
    src = _PENDING_DIR / fname
    if not src.exists():
        raise FileNotFoundError(f"no pending combination '{combination_id}' to approve")
    dst = _APPROVED_DIR / fname
    if dst.exists():
        raise FileExistsError(
            f"combination_id '{combination_id}' already exists in approved/"
        )
    payload = _read_json(src)
    payload["__approved_at__"] = _now()
    payload["__approved_by__"] = reviewer or "unknown"
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "approve", "combination_id": combination_id, "by": reviewer})
    return _summarize(payload | {"__path__": str(dst), "__filename__": dst.name})


def reject(combination_id: str, reviewer: str, reason: str) -> dict[str, Any]:
    """Move a pending combination to rejected/, recording reason + reviewer."""
    _ensure_dirs()
    combination_id = _safe_combination_id(combination_id)
    fname = _filename_for(combination_id)
    src = _PENDING_DIR / fname
    if not src.exists():
        raise FileNotFoundError(f"no pending combination '{combination_id}' to reject")
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("rejection reason is required")
    dst = _REJECTED_DIR / fname
    payload = _read_json(src)
    payload["__rejected_at__"] = _now()
    payload["__rejected_by__"] = reviewer or "unknown"
    payload["__rejection_reason__"] = reason[:1000]
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "reject", "combination_id": combination_id, "by": reviewer, "reason": reason[:200]})
    return _summarize(payload | {"__path__": str(dst), "__filename__": dst.name})


# Fields the reviewer is allowed to edit while a combination is pending.
# `id` is locked (it's the filename) and the system-stamped __*__ keys are
# managed by this module. Everything else listed here is editable.
_EDITABLE_FIELDS: tuple[str, ...] = (
    "name",
    "version",
    "pattern_ids",
    "trigger_logic",
    "anti_triggers",
    "combined_hypothesis",
    "strategic_risk",
    "minimum_evidence",
    "financial_exposure",
    "tad_action",
    "prohibited_claims",
    "confidence_ceiling",
    "knowledge_type",
    "claim_permissions_impact",
    "example_outputs",
    "tests",
    "notes",
)


def editable_fields() -> tuple[str, ...]:
    return _EDITABLE_FIELDS


def edit(combination_id: str, reviewer: str, patch: dict[str, Any]) -> dict[str, Any]:
    """Apply a reviewer patch to a pending combination.

    Only fields in _EDITABLE_FIELDS are touched; everything else in the
    payload is preserved (including system stamps). Stamps __edited_at__
    + __edited_by__ + increments __edit_count__.

    Raises:
      FileNotFoundError — no pending combination with that id
      ValueError        — patch is empty, contains no editable fields, or
                          reviewer is empty
    """
    _ensure_dirs()
    combination_id = _safe_combination_id(combination_id)
    if not (reviewer or "").strip():
        raise ValueError("reviewer is required")
    if not isinstance(patch, dict) or not patch:
        raise ValueError("patch must be a non-empty dict")

    # Filter to editable fields only (silent drop of unknown / locked keys).
    clean_patch = {k: v for k, v in patch.items() if k in _EDITABLE_FIELDS}
    if not clean_patch:
        raise ValueError(
            f"patch contains no editable fields. "
            f"Editable: {list(_EDITABLE_FIELDS)}"
        )

    fname = _filename_for(combination_id)
    path = _PENDING_DIR / fname
    if not path.exists():
        raise FileNotFoundError(
            f"no pending combination '{combination_id}' to edit"
        )

    payload = _read_json(path)
    prev_edit_count = int(payload.get("__edit_count__", 0) or 0)
    payload.update(clean_patch)
    payload["__edited_at__"] = _now()
    payload["__edited_by__"] = reviewer.strip()
    payload["__edit_count__"] = prev_edit_count + 1
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _append_audit(
        {
            "event": "edit",
            "combination_id": combination_id,
            "by": reviewer,
            "fields_changed": sorted(clean_patch.keys()),
            "edit_count": payload["__edit_count__"],
        }
    )
    return _summarize(payload | {"__path__": str(path), "__filename__": path.name})


def reset_to_pending(combination_id: str, reviewer: str) -> dict[str, Any]:
    """Move a rejected combination back to pending for re-review."""
    _ensure_dirs()
    combination_id = _safe_combination_id(combination_id)
    fname = _filename_for(combination_id)
    src = _REJECTED_DIR / fname
    if not src.exists():
        raise FileNotFoundError(f"no rejected combination '{combination_id}' to reset")
    dst = _PENDING_DIR / fname
    if dst.exists():
        raise FileExistsError(
            f"combination_id '{combination_id}' already pending"
        )
    payload = _read_json(src)
    # Clear rejection metadata; preserve proposal stamps.
    for key in ("__rejected_at__", "__rejected_by__", "__rejection_reason__"):
        payload.pop(key, None)
    payload["__reset_at__"] = _now()
    payload["__reset_by__"] = reviewer or "unknown"
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "reset", "combination_id": combination_id, "by": reviewer})
    return _summarize(payload | {"__path__": str(dst), "__filename__": dst.name})


def get_full(combination_id: str, state: str = "pending") -> dict[str, Any]:
    """Return the full JSON payload for a combination_id in the given state."""
    combination_id = _safe_combination_id(combination_id)
    fname = _filename_for(combination_id)
    state_dir = {
        "pending": _PENDING_DIR,
        "approved": _APPROVED_DIR,
        "rejected": _REJECTED_DIR,
    }.get(state)
    if state_dir is None:
        raise ValueError(f"unknown state: {state!r}")
    path = state_dir / fname
    if not path.exists():
        raise FileNotFoundError(f"no '{combination_id}' in {state}")
    payload = _read_json(path)
    payload["__path__"] = str(path)
    payload["__filename__"] = path.name
    return payload
