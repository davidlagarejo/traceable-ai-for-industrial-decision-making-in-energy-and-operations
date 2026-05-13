"""Engine entry points — knowledge proposal canonical write path.

This module is the canonical write path for the Industrial Research Engine.
Three public functions:

  propose_knowledge(payload, kind, proposed_by) — fully implemented.
    Validates payload via the schema validator, writes it to
    knowledge_pending/<kind>/ for human approval in the dashboard.

  propose_knowledge_from_manual_text(source_id, topic, target_kind, payload, ...)
    — convenience wrapper that auto-stamps source_basis + extraction_metadata
    when a human is pasting a hand-authored draft. Used by the
    scripts/extract_knowledge.py CLI.

  extract_knowledge(source_url, topic, source_type) — INTENTIONAL STUB.
    Automated extraction lives in `zlab_skill.local_pdf_autodraft` and
    `zlab_skill.extractor` (deterministic, rule-based, no LLM in the
    analytical path). This entrypoint exists only to fail loud if a
    caller assumes there is an LLM-driven extractor here.

Phase 0 law: the LLM is never the analytical engine. The extraction
machinery is deterministic. The LLM only appears in motor_019 as a
post-framework narrator.

All callers (CLIs, motors, dashboard) MUST route writes through
propose_knowledge[ _from_manual_text ]. NO bypassing.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..source_catalog import source_by_id
from .routing import NotImplementedExtractor
from .schemas import KNOWLEDGE_KINDS, CombinationObject, KnowledgeObject
from .validators import (
    KnowledgeValidationError,
    validate_combination,
    validate_combination_v6_strict,
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
    """INTENTIONAL STUB — automated extraction lives elsewhere.

    Automated PDF/source extraction is implemented as a deterministic
    rule-based pipeline in:
        - runtime_orchestrator.zlab_skill.local_pdf_autodraft
        - runtime_orchestrator.zlab_skill.extractor
        - runtime_orchestrator.zlab_skill.research_loop_controller

    This entrypoint raises NotImplementedError on purpose so any caller
    that wrongly assumes an LLM-driven extractor lives here fails loud
    and is redirected to the correct (deterministic) path.
    """
    extractor = NotImplementedExtractor()
    return extractor.extract(source_url, topic, source_type)


def propose_knowledge_from_manual_text(
    *,
    source_id: str,
    topic: str,
    target_kind: str,
    knowledge_payload: dict[str, Any],
    proposed_by: str = "manual_extraction",
) -> dict[str, Any]:
    """Hand-authored draft path — stamps provenance + proposes.

    Used when a human reads an authoritative source and types the
    KnowledgeObject JSON by hand. The function:
      1. Verifies source_id exists in the industrial_source_catalog
      2. Auto-stamps source_basis (if the payload didn't include it)
      3. Auto-stamps extraction_metadata (topic, source_id, path)
      4. Routes through propose_knowledge for validation + landing

    Returns the stamped, validated payload (same shape as
    propose_knowledge). Raises KnowledgeValidationError on schema
    failure, ValueError if source_id is unknown, FileExistsError on
    duplicate id.
    """
    if not source_by_id(source_id):
        raise ValueError(
            f"source_id {source_id!r} is not in the industrial_source_catalog. "
            "Add it to the catalog (or propose it as new knowledge of kind "
            "'source') before submitting manual drafts that cite it."
        )

    # Source provenance — append if not already present
    sb = list(knowledge_payload.get("source_basis", []) or [])
    if not any(
        isinstance(s, dict) and s.get("source_id") == source_id for s in sb
    ):
        sb.append({"source_id": source_id, "confidence": "manual"})
        knowledge_payload = {**knowledge_payload, "source_basis": sb}

    # Extraction metadata stamp
    em = dict(knowledge_payload.get("extraction_metadata", {}) or {})
    em.setdefault("topic", topic)
    em.setdefault("source_id", source_id)
    em.setdefault("extraction_path", "manual")
    knowledge_payload = {**knowledge_payload, "extraction_metadata": em}

    return propose_knowledge(
        knowledge_payload, kind=target_kind, proposed_by=proposed_by
    )


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

    # Validate via the appropriate validator.
    # V6 P13.5 — if hard-block mode is active, route combinations through
    # the V6 strict validator (required_evidence_pack, tad_mapping, render
    # modes, ≥2 patterns, etc.). Soft mode keeps the V5 validator for
    # backward compat with the 4 pre-V6 approved combinations.
    if target_kind == "combination":
        import os
        _v6_strict = (os.environ.get("ZLAB_VALIDATORS_HARD_BLOCK", "") or "").lower().strip() in ("1", "true", "yes", "on")
        if _v6_strict:
            validated: KnowledgeObject = validate_combination_v6_strict(payload)
        else:
            validated = validate_combination(payload)
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
