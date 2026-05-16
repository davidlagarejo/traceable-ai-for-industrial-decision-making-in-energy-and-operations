"""Audit log — cada propuesta queda registrada con su método, evidencia,
y timestamp en `combinations_audit_log.jsonl`. Esto permite:

  · Reproducibilidad: re-correr el proposer en el mismo input → mismas
    propuestas → mismas entries de log.
  · Trazabilidad: por qué se propuso esta combination en esta fecha.
  · Feedback loop: cuando un humano rechaza, asociamos rechazo →
    proposal_method → ajustar pesos del método.

Phase 0 inscribed: ninguna entry de este log invoca LLM. Solo datos
estructurados de qué se generó y cómo.
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any


def _log_path() -> Path:
    """zlab_skill/registry/combinations_audit_log.jsonl"""
    return (Path(__file__).resolve().parents[3]
            / "zlab_skill" / "registry"
            / "combinations_audit_log.jsonl")


def write_audit_entry(candidate, *, asset_family: str) -> None:
    """Append one JSONL line per candidate proposed."""
    p = _log_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event":             "proposed",
        "timestamp":         _dt.datetime.utcnow().isoformat() + "Z",
        "candidate_id":      candidate.id,
        "asset_family":      asset_family,
        "proposal_method":   candidate.proposal_method,
        "pattern_set":       candidate.pattern_set,
        "confidence_score":  candidate.confidence_score,
        "stable_signature":  candidate.stable_signature(),
        "corpus_citation_count":  len(candidate.corpus_citations),
        "regulatory_basis_count": len(candidate.regulatory_basis),
        "decision_implication":   candidate.decision_implication.get("action", ""),
    }
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_curation_event(candidate_id: str, action: str, *,
                          reason: str = "", actor: str = "user") -> None:
    """Append a curation event (approve / reject / modify) when a human
    decides on a candidate. Called from the dashboard endpoint."""
    if action not in ("approve", "reject", "modify"):
        return
    p = _log_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event":          f"curation_{action}",
        "timestamp":      _dt.datetime.utcnow().isoformat() + "Z",
        "candidate_id":   candidate_id,
        "actor":          actor,
        "reason":         reason[:300],
    }
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_recent_entries(n: int = 50) -> list[dict[str, Any]]:
    """Read last N entries (for dashboard /combinations history)."""
    p = _log_path()
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out[-n:][::-1]   # newest first
