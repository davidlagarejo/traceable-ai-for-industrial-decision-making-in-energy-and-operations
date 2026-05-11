"""Asset-family hybrid catalog loader (Layer A — Governed Knowledge).

Loads `governanza/asset-operational-logic-engine_050/hybrids/asset_family_hybrids.json`
(RECOVERY_2026-05-10 §2, Gap B). motor_061 consumes this to admit
justified cross-family pattern activations as `hybrid_admissible` rather
than flagging them as contamination.

A hybrid is admitted only when ONE of its `justification_triggers` is
present in the evidence (facility/process tokens from motor_007 or
industrial_evidence_register from motor_054).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[3]
_HYBRIDS_PATH = (
    _REPO_ROOT
    / "governanza"
    / "asset-operational-logic-engine_050"
    / "hybrids"
    / "asset_family_hybrids.json"
)


def hybrids_path() -> Path:
    return _HYBRIDS_PATH


@lru_cache(maxsize=1)
def load_hybrids() -> dict[str, Any]:
    if not _HYBRIDS_PATH.exists():
        return {"catalog_id": "asset_family_hybrids", "hybrids": []}
    try:
        return json.loads(_HYBRIDS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"catalog_id": "asset_family_hybrids", "hybrids": []}


def all_hybrids() -> list[dict[str, Any]]:
    return list(load_hybrids().get("hybrids", []) or [])


def hybrids_for_primary(primary_family: str) -> list[dict[str, Any]]:
    if not primary_family:
        return []
    p = primary_family.strip().lower()
    return [h for h in all_hybrids() if str(h.get("primary", "")).lower() == p]


def find_admissible_hybrid(
    primary_family: str,
    evidence_tokens: set[str],
) -> dict[str, Any] | None:
    """Return the first hybrid whose primary matches and whose justification
    trigger appears in evidence_tokens. Returns None if no hybrid applies.
    """
    if not primary_family or not evidence_tokens:
        return None
    tokens_lower = {str(t).strip().lower() for t in evidence_tokens if t}
    for hybrid in hybrids_for_primary(primary_family):
        triggers = {str(t).strip().lower() for t in hybrid.get("justification_triggers", []) or []}
        if triggers.intersection(tokens_lower):
            return hybrid
    return None


def shared_patterns_for_hybrid(hybrid: dict[str, Any]) -> set[str]:
    if not hybrid:
        return set()
    return {str(p).strip() for p in hybrid.get("shared_patterns", []) or [] if p}
