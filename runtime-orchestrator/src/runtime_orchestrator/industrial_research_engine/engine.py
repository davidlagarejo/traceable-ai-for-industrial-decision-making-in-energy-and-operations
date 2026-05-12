"""Engine entry points (V4 P0 item 1).

The Industrial Research Engine surface from the outside. Two public
functions:

  extract_knowledge(source_url, topic, source_type) — STUB. Raises
    NotImplementedError in V4 Phase 0. Real implementation lands in
    V4 Phase 1 with PDF parsing + LLM structuring.

  propose_knowledge(payload, kind, proposed_by) — fully implemented.
    Validates payload via the schema validator, writes it to
    knowledge_pending/<kind>/ for human approval in the dashboard.

This module is the canonical entry point — both the CLI
(scripts/propose_knowledge.py) and any future motor (motor_028
discovery → research engine) MUST route through these functions.
NO bypassing.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .routing import NotImplementedExtractor
from .schemas import KNOWLEDGE_KINDS, CombinationObject, KnowledgeObject
from .validators import (
    KnowledgeValidationError,
    validate_combination,
    validate_knowledge,
)


_REPO_ROOT = Path(__file__).resolve().parents[4]
_PENDING_ROOT = (
    _REPO_ROOT / "runtime-orchestrator" / "zlab_skill" / "registry" / "knowledge_pending"
)
_AUDIT_LOG = _PENDING_ROOT / "knowledge_proposal_log.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_id(knowledge_id: str) -> str:
    s = (knowledge_id or "").strip().lower()
    if not s:
        raise KnowledgeValidationError("knowledge_id is required")
    if "/" in s or ".." in s or "\\" in s:
        raise KnowledgeValidationError(f"invalid knowledge_id: {knowledge_id!r}")
    if not all(c.isalnum() or c in "_-" for c in s):
        raise KnowledgeValidationError(
            f"knowledge_id must be alnum+underscore+hyphen only: {knowledge_id!r}"
        )
    return s


def _ensure_kind_dir(kind: str) -> Path:
    d = _PENDING_ROOT / kind
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append_audit(event: dict[str, Any]) -> None:
    _PENDING_ROOT.mkdir(parents=True, exist_ok=True)
    event = {**event, "ts": _now()}
    try:
        with _AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + os.linesep)
    except OSError:
        pass


def extract_knowledge(
    source_url: str, topic: str, source_type: str = "pdf"
) -> dict[str, Any]:
    """V4 Phase 0 stub. Raises NotImplementedError.

    The signature is locked so V4 Phase 1 plugs in the real implementation
    without changing callers. Returns (when implemented) a dict that
    passes validate_knowledge() or validate_combination().
    """
    extractor = NotImplementedExtractor()
    return extractor.extract(source_url, topic, source_type)


def propose_knowledge(
    payload: dict[str, Any],
    kind: str | None = None,
    proposed_by: str = "ai",
) -> dict[str, Any]:
    """Canonical write path. Validates and lands payload in
    knowledge_pending/<kind>/.

    Parameters:
      payload: a knowledge dict matching the schema. Must include `id`,
        `version`, `knowledge_kind`, etc.
      kind: optional override for the destination folder. Defaults to
        payload["knowledge_kind"]. Must be one of KNOWLEDGE_KINDS.
      proposed_by: identifier for who is proposing (default 'ai').

    Returns: the stamped, validated payload.

    Raises: KnowledgeValidationError on schema failure, FileExistsError
    on duplicate id in any pending state.
    """
    if not isinstance(payload, dict):
        raise KnowledgeValidationError("payload must be a JSON object (dict)")

    # Determine kind
    declared_kind = str(payload.get("knowledge_kind", "")).strip()
    target_kind = (kind or declared_kind).strip()
    if not target_kind:
        raise KnowledgeValidationError(
            "knowledge_kind is required (set kind= or payload.knowledge_kind)"
        )
    if target_kind not in KNOWLEDGE_KINDS:
        raise KnowledgeValidationError(
            f"unknown knowledge_kind: {target_kind!r}. Valid: {KNOWLEDGE_KINDS}"
        )

    # Validate via the appropriate validator
    if target_kind == "combination":
        validated: KnowledgeObject = validate_combination(payload)
    else:
        # Ensure the payload reflects the target kind even if caller
        # passed a different declared kind by mistake.
        payload = {**payload, "knowledge_kind": target_kind}
        validated = validate_knowledge(payload)

    knowledge_id = _safe_id(validated.id)
    fname = f"{knowledge_id}.v1.json"
    dest_dir = _ensure_kind_dir(target_kind)
    dest = dest_dir / fname

    # Refuse duplicate across all pending subfolders
    for kind_dir in _PENDING_ROOT.glob("*"):
        if not kind_dir.is_dir():
            continue
        candidate = kind_dir / fname
        if candidate.exists():
            raise FileExistsError(
                f"knowledge_id '{knowledge_id}' already pending in "
                f"{kind_dir.name}/ — reject or reset before re-proposing"
            )

    # Stamp + write
    out = validated.to_dict()
    out["__proposed_at__"] = _now()
    out["__proposed_by__"] = (proposed_by or "ai").strip()
    out["__pending_kind__"] = target_kind
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    _append_audit({
        "event": "propose_knowledge",
        "id": knowledge_id,
        "kind": target_kind,
        "by": out["__proposed_by__"],
    })
    return out
