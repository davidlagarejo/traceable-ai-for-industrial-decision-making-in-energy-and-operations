"""Knowledge memory architecture (V4 P0 item 11).

States:
  pending     ← AI/extractor produces; lives in knowledge_pending/<kind>/
  approved    ← human-approved via dashboard; lives in knowledge_memory/approved/
  deprecated  ← previously approved, now retired (kept for audit)
  superseded  ← replaced by a newer version (kept for audit)
  rejected   ← human-rejected; lives in knowledge_memory/rejected/

Transitions are reversible by reverse-operation (e.g., a deprecated
entry can be re-approved). Every transition is recorded in
knowledge_memory_log.jsonl.

This module operates on FILES (atomic moves) — no in-memory state.
That's intentional: the filesystem IS the audit trail.
"""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[4]
_REGISTRY_ROOT = _REPO_ROOT / "runtime-orchestrator" / "zlab_skill" / "registry"
_PENDING_ROOT = _REGISTRY_ROOT / "knowledge_pending"
_MEMORY_ROOT = _REGISTRY_ROOT / "knowledge_memory"
_AUDIT_LOG = _MEMORY_ROOT / "knowledge_memory_log.jsonl"


class MemoryState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_id(knowledge_id: str) -> str:
    s = (knowledge_id or "").strip().lower()
    if not s:
        raise ValueError("knowledge_id is required")
    if "/" in s or ".." in s or "\\" in s:
        raise ValueError(f"invalid knowledge_id: {knowledge_id!r}")
    if not all(c.isalnum() or c in "_-" for c in s):
        raise ValueError(f"knowledge_id must be alnum+underscore+hyphen only: {knowledge_id!r}")
    return s


def _filename_for(knowledge_id: str) -> str:
    return f"{_safe_id(knowledge_id)}.v1.json"


def _pending_path(kind: str, knowledge_id: str) -> Path:
    return _PENDING_ROOT / kind / _filename_for(knowledge_id)


def _memory_path(state: MemoryState, knowledge_id: str) -> Path:
    return _MEMORY_ROOT / state.value / _filename_for(knowledge_id)


def _ensure_dirs() -> None:
    for kind_dir in _PENDING_ROOT.glob("*"):
        if kind_dir.is_dir():
            kind_dir.mkdir(parents=True, exist_ok=True)
    for state in MemoryState:
        (_MEMORY_ROOT / state.value).mkdir(parents=True, exist_ok=True)


def _append_audit(event: dict[str, Any]) -> None:
    _ensure_dirs()
    event = {**event, "ts": _now()}
    try:
        with _AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + os.linesep)
    except OSError:
        pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ── Public transitions ──────────────────────────────────────────────────


def promote_to_memory(
    knowledge_id: str, kind: str, reviewer: str
) -> dict[str, Any]:
    """Move from pending/<kind>/ to memory/approved/. Records reviewer."""
    _ensure_dirs()
    knowledge_id = _safe_id(knowledge_id)
    reviewer = (reviewer or "").strip()
    if not reviewer:
        raise ValueError("reviewer is required")
    src = _pending_path(kind, knowledge_id)
    if not src.exists():
        raise FileNotFoundError(
            f"no pending '{knowledge_id}' under kind '{kind}'"
        )
    dst = _memory_path(MemoryState.APPROVED, knowledge_id)
    if dst.exists():
        raise FileExistsError(
            f"knowledge_id '{knowledge_id}' already in approved memory"
        )
    payload = _read_json(src)
    payload["__approved_at__"] = _now()
    payload["__approved_by__"] = reviewer
    payload["__source_pending_kind__"] = kind
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "promote", "id": knowledge_id, "kind": kind, "by": reviewer})
    return payload


def reject(
    knowledge_id: str, kind: str, reviewer: str, reason: str
) -> dict[str, Any]:
    """Move from pending/<kind>/ to memory/rejected/ with reason."""
    _ensure_dirs()
    knowledge_id = _safe_id(knowledge_id)
    reviewer = (reviewer or "").strip()
    reason = (reason or "").strip()
    if not reviewer:
        raise ValueError("reviewer is required")
    if not reason:
        raise ValueError("rejection reason is required")
    src = _pending_path(kind, knowledge_id)
    if not src.exists():
        raise FileNotFoundError(
            f"no pending '{knowledge_id}' under kind '{kind}'"
        )
    dst = _memory_path(MemoryState.REJECTED, knowledge_id)
    payload = _read_json(src)
    payload["__rejected_at__"] = _now()
    payload["__rejected_by__"] = reviewer
    payload["__rejection_reason__"] = reason[:1000]
    payload["__source_pending_kind__"] = kind
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "reject", "id": knowledge_id, "kind": kind, "by": reviewer, "reason": reason[:200]})
    return payload


def deprecate(
    knowledge_id: str, reviewer: str, reason: str = ""
) -> dict[str, Any]:
    """Move from approved/ to deprecated/ (retire an active piece of
    knowledge without rejecting it outright)."""
    _ensure_dirs()
    knowledge_id = _safe_id(knowledge_id)
    reviewer = (reviewer or "").strip()
    if not reviewer:
        raise ValueError("reviewer is required")
    src = _memory_path(MemoryState.APPROVED, knowledge_id)
    if not src.exists():
        raise FileNotFoundError(f"no approved '{knowledge_id}' to deprecate")
    dst = _memory_path(MemoryState.DEPRECATED, knowledge_id)
    payload = _read_json(src)
    payload["__deprecated_at__"] = _now()
    payload["__deprecated_by__"] = reviewer
    if reason:
        payload["__deprecation_reason__"] = reason[:1000]
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "deprecate", "id": knowledge_id, "by": reviewer})
    return payload


def supersede(
    old_id: str, new_id: str, reviewer: str
) -> dict[str, Any]:
    """Mark old as superseded by new. Both must exist in approved/. The
    old entry moves to superseded/; new stays in approved/."""
    _ensure_dirs()
    old_id = _safe_id(old_id)
    new_id = _safe_id(new_id)
    reviewer = (reviewer or "").strip()
    if not reviewer:
        raise ValueError("reviewer is required")
    src = _memory_path(MemoryState.APPROVED, old_id)
    if not src.exists():
        raise FileNotFoundError(f"no approved '{old_id}' to supersede")
    new_path = _memory_path(MemoryState.APPROVED, new_id)
    if not new_path.exists():
        raise FileNotFoundError(
            f"superseding id '{new_id}' must already be in approved/"
        )
    dst = _memory_path(MemoryState.SUPERSEDED, old_id)
    payload = _read_json(src)
    payload["__superseded_at__"] = _now()
    payload["__superseded_by_id__"] = new_id
    payload["__superseded_by_reviewer__"] = reviewer
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "supersede", "id": old_id, "by_new_id": new_id, "reviewer": reviewer})
    return payload


def restore_from_deprecated(knowledge_id: str, reviewer: str) -> dict[str, Any]:
    """Reverse a deprecation — move from deprecated/ back to approved/."""
    _ensure_dirs()
    knowledge_id = _safe_id(knowledge_id)
    reviewer = (reviewer or "").strip()
    if not reviewer:
        raise ValueError("reviewer is required")
    src = _memory_path(MemoryState.DEPRECATED, knowledge_id)
    if not src.exists():
        raise FileNotFoundError(f"no deprecated '{knowledge_id}' to restore")
    dst = _memory_path(MemoryState.APPROVED, knowledge_id)
    if dst.exists():
        raise FileExistsError(
            f"'{knowledge_id}' already exists in approved/ — cannot restore"
        )
    payload = _read_json(src)
    payload.pop("__deprecated_at__", None)
    payload.pop("__deprecated_by__", None)
    payload.pop("__deprecation_reason__", None)
    payload["__restored_at__"] = _now()
    payload["__restored_by__"] = reviewer
    dst.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    src.unlink()
    _append_audit({"event": "restore", "id": knowledge_id, "by": reviewer})
    return payload


# ── Listing helpers ─────────────────────────────────────────────────────


def list_in_state(state: MemoryState) -> list[dict[str, Any]]:
    """Return summaries of every knowledge entry currently in `state`."""
    _ensure_dirs()
    state_dir = _MEMORY_ROOT / state.value
    out: list[dict[str, Any]] = []
    if not state_dir.exists():
        return out
    for path in sorted(state_dir.glob("*.json")):
        if path.name.startswith("."):
            continue
        payload = _read_json(path)
        if not payload:
            continue
        out.append({
            "id": payload.get("id", path.stem),
            "version": payload.get("version", ""),
            "knowledge_kind": payload.get("knowledge_kind", ""),
            "asset_families": payload.get("asset_families", []),
            "claim_ceiling": payload.get("claim_ceiling", ""),
            "approved_at": payload.get("__approved_at__", ""),
            "approved_by": payload.get("__approved_by__", ""),
            "rejected_at": payload.get("__rejected_at__", ""),
            "rejected_by": payload.get("__rejected_by__", ""),
            "rejection_reason": payload.get("__rejection_reason__", ""),
            "deprecated_at": payload.get("__deprecated_at__", ""),
            "superseded_by_id": payload.get("__superseded_by_id__", ""),
        })
    return out


def list_pending(kind: str) -> list[dict[str, Any]]:
    """Return summaries of pending entries under a kind subfolder."""
    _ensure_dirs()
    kind_dir = _PENDING_ROOT / kind
    out: list[dict[str, Any]] = []
    if not kind_dir.exists():
        return out
    for path in sorted(kind_dir.glob("*.json")):
        if path.name.startswith("."):
            continue
        payload = _read_json(path)
        if not payload:
            continue
        out.append({
            "id": payload.get("id", path.stem),
            "version": payload.get("version", ""),
            "knowledge_kind": payload.get("knowledge_kind", ""),
            "asset_families": payload.get("asset_families", []),
            "claim_ceiling": payload.get("claim_ceiling", ""),
            "proposed_at": payload.get("__proposed_at__", ""),
            "proposed_by": payload.get("__proposed_by__", ""),
        })
    return out
