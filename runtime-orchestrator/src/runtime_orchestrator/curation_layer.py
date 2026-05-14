"""Curation Layer — human review persistence for the /revisar dashboard.

Dashboard refresh anchor (2026-05-14): the center column of /revisar
becomes the human curation surface. This module holds the persistence
contracts so the future "translation skill" can read everything humans
decided without scraping HTML.

Layout on disk (relative to runtime-orchestrator/):

  curation/
  ├── combination_edits/<run_id>.json     ← per-run combination decisions
  ├── pdf_annotations/<run_id>.json       ← per-run PDF mark-up
  └── curation_log.jsonl                  ← global audit trail

Three primitives:

  1. record_combination_decision(...)  — accept / reject / modify a combo
  2. record_pdf_annotation(...)        — click-region comment on PDF
  3. export_curation_bundle(run_id)    — single dict ready for downstream skill

This layer NEVER mutates motor outputs, registries, or memory. It only
records human intent. The intent is consumed later by a separate skill
(out of scope for V9).
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


_CURATION_ROOT_ENV = "ZLAB_CURATION_ROOT"


def curation_root() -> Path:
    """Resolve the on-disk root for curation artifacts.

    Honors `ZLAB_CURATION_ROOT` env var so tests can isolate writes.
    Default: `runtime-orchestrator/curation/`.
    """
    override = os.environ.get(_CURATION_ROOT_ENV, "").strip()
    if override:
        return Path(override)
    # runtime-orchestrator/src/runtime_orchestrator/curation_layer.py
    # → runtime-orchestrator/curation/
    return Path(__file__).resolve().parents[2] / "curation"


def _ensure_dirs() -> dict[str, Path]:
    root = curation_root()
    dirs = {
        "root":      root,
        "combos":    root / "combination_edits",
        "pdfs":      root / "pdf_annotations",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs


def _audit_log_path() -> Path:
    return curation_root() / "curation_log.jsonl"


def _append_audit(event: dict[str, Any]) -> None:
    """Append-only JSONL audit trail."""
    _ensure_dirs()
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with _audit_log_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


# ── 1. Combination decisions ────────────────────────────────────────


@dataclass(frozen=True)
class CombinationDecision:
    decision_id: str                       # uuid4
    run_id: str
    combination_id: str
    decision: str                          # "accept" | "reject" | "modify"
    modify_instruction: str = ""           # free-text from curator
    curator: str = "anonymous"
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision_id":         self.decision_id,
            "run_id":              self.run_id,
            "combination_id":      self.combination_id,
            "decision":            self.decision,
            "modify_instruction":  self.modify_instruction,
            "curator":             self.curator,
            "metadata":            dict(self.metadata),
        }


_ALLOWED_DECISIONS = frozenset({"accept", "reject", "modify"})


def record_combination_decision(
    *,
    run_id: str,
    combination_id: str,
    decision: str,
    modify_instruction: str = "",
    curator: str = "anonymous",
    metadata: Mapping[str, Any] | None = None,
) -> CombinationDecision:
    """Persist a combination decision for `run_id`.

    Behavior:
      - File `combination_edits/<run_id>.json` is a list of decisions.
      - Multiple decisions for the same combination_id accumulate;
        the most recent one wins (downstream reader takes the last).
      - decision must be one of {accept, reject, modify}.
      - if decision == "modify", `modify_instruction` should be non-empty
        but is not enforced (curator may amend later).

    Returns the persisted CombinationDecision.
    """
    decision = (decision or "").strip().lower()
    if decision not in _ALLOWED_DECISIONS:
        raise ValueError(
            f"decision must be one of {sorted(_ALLOWED_DECISIONS)}, got {decision!r}"
        )
    if not run_id or not combination_id:
        raise ValueError("run_id and combination_id are required")

    record = CombinationDecision(
        decision_id=str(uuid.uuid4()),
        run_id=str(run_id),
        combination_id=str(combination_id),
        decision=decision,
        modify_instruction=str(modify_instruction or ""),
        curator=str(curator or "anonymous"),
        metadata=dict(metadata or {}),
    )

    dirs = _ensure_dirs()
    path = dirs["combos"] / f"{record.run_id}.json"
    existing: list[dict[str, Any]] = []
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []
    existing.append(record.as_dict())
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False),
                    encoding="utf-8")

    _append_audit({
        "kind": "combination_decision",
        "decision_id": record.decision_id,
        "run_id": record.run_id,
        "combination_id": record.combination_id,
        "decision": record.decision,
        "curator": record.curator,
    })
    return record


def load_combination_decisions(run_id: str) -> list[dict[str, Any]]:
    """Return all decisions persisted for `run_id` (chronological order)."""
    path = _ensure_dirs()["combos"] / f"{run_id}.json"
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
        return rows if isinstance(rows, list) else []
    except json.JSONDecodeError:
        return []


def latest_combination_decisions(run_id: str) -> dict[str, dict[str, Any]]:
    """Return {combination_id: latest_decision_dict} for `run_id`."""
    out: dict[str, dict[str, Any]] = {}
    for row in load_combination_decisions(run_id):
        cid = str(row.get("combination_id", "")).strip()
        if cid:
            out[cid] = row
    return out


# ── 2. PDF annotations ─────────────────────────────────────────────


@dataclass(frozen=True)
class PDFAnnotation:
    annotation_id: str
    run_id: str
    pdf_path: str            # path or URL relative to runtime
    page: int                # 1-indexed page number
    region: dict[str, Any]   # {x, y, w, h} normalized (0-1) OR free text
    comment: str
    suggested_change: str = ""
    curator: str = "anonymous"
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "annotation_id":     self.annotation_id,
            "run_id":            self.run_id,
            "pdf_path":          self.pdf_path,
            "page":              self.page,
            "region":            dict(self.region),
            "comment":           self.comment,
            "suggested_change":  self.suggested_change,
            "curator":           self.curator,
            "metadata":          dict(self.metadata),
        }


def record_pdf_annotation(
    *,
    run_id: str,
    pdf_path: str,
    page: int,
    region: Mapping[str, Any] | None,
    comment: str,
    suggested_change: str = "",
    curator: str = "anonymous",
    metadata: Mapping[str, Any] | None = None,
) -> PDFAnnotation:
    """Persist a PDF annotation for `run_id`.

    Behavior:
      - File `pdf_annotations/<run_id>.json` is a list.
      - `region` is a free dict (normalized x/y/w/h or freeform). May be empty.
      - `comment` is required (the curator's note).
      - `suggested_change` is optional but recommended (the proposed edit).

    Returns the persisted PDFAnnotation.
    """
    if not run_id or not pdf_path:
        raise ValueError("run_id and pdf_path are required")
    if not str(comment or "").strip():
        raise ValueError("comment is required")
    try:
        page_i = int(page)
    except (TypeError, ValueError):
        raise ValueError("page must be an integer")
    if page_i < 1:
        raise ValueError("page must be ≥ 1 (1-indexed)")

    record = PDFAnnotation(
        annotation_id=str(uuid.uuid4()),
        run_id=str(run_id),
        pdf_path=str(pdf_path),
        page=page_i,
        region=dict(region or {}),
        comment=str(comment).strip(),
        suggested_change=str(suggested_change or "").strip(),
        curator=str(curator or "anonymous"),
        metadata=dict(metadata or {}),
    )

    dirs = _ensure_dirs()
    path = dirs["pdfs"] / f"{record.run_id}.json"
    existing: list[dict[str, Any]] = []
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []
    existing.append(record.as_dict())
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False),
                    encoding="utf-8")

    _append_audit({
        "kind": "pdf_annotation",
        "annotation_id": record.annotation_id,
        "run_id": record.run_id,
        "page": record.page,
        "curator": record.curator,
    })
    return record


def load_pdf_annotations(run_id: str) -> list[dict[str, Any]]:
    path = _ensure_dirs()["pdfs"] / f"{run_id}.json"
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
        return rows if isinstance(rows, list) else []
    except json.JSONDecodeError:
        return []


def delete_pdf_annotation(run_id: str, annotation_id: str) -> bool:
    """Remove a single annotation. Returns True if found and removed."""
    path = _ensure_dirs()["pdfs"] / f"{run_id}.json"
    if not path.exists():
        return False
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if not isinstance(rows, list):
        return False
    before = len(rows)
    rows = [r for r in rows if r.get("annotation_id") != annotation_id]
    if len(rows) == before:
        return False
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    _append_audit({
        "kind": "pdf_annotation_deleted",
        "annotation_id": annotation_id,
        "run_id": run_id,
    })
    return True


# ── 3. Export bundle ───────────────────────────────────────────────


def export_curation_bundle(run_id: str) -> dict[str, Any]:
    """Single dict ready for downstream translation skill to consume.

    Shape:
      {
        "run_id": str,
        "exported_at": iso8601,
        "combination_decisions": [...],
        "latest_per_combination": {combo_id: decision_dict},
        "pdf_annotations": [...],
        "annotation_count": int,
        "modify_count": int,
        "reject_count": int,
        "accept_count": int,
      }
    """
    combos = load_combination_decisions(run_id)
    annots = load_pdf_annotations(run_id)
    latest = latest_combination_decisions(run_id)
    counters = {"accept_count": 0, "reject_count": 0, "modify_count": 0}
    for row in latest.values():
        d = row.get("decision", "")
        if d == "accept":
            counters["accept_count"] += 1
        elif d == "reject":
            counters["reject_count"] += 1
        elif d == "modify":
            counters["modify_count"] += 1
    return {
        "run_id": run_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "combination_decisions": combos,
        "latest_per_combination": latest,
        "pdf_annotations": annots,
        "annotation_count": len(annots),
        **counters,
    }
