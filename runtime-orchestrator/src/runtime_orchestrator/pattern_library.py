"""Pattern Library loader (Layer A — Governed Knowledge).

Loads asset-family-specific concept markers and falsifiers from JSON files
in `governanza/asset-operational-logic-engine_050/patterns/`. The library
is asset-agnostic: callers ask for a specific family and receive a
read-only view of its tokens and axes.

This replaces the hardcoded `_CONCEPT_MARKER_MAP` that previously lived
inside `executive_thesis.py` (RECOVERY_BACKLOG.md R-30..R-37).

Usage:
  from runtime_orchestrator.pattern_library import load_pattern_library

  pattern = load_pattern_library("warehouse_distribution")
  if pattern is not None:
      tokens = pattern["concept_markers"]
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


# Resolved relative to this file: runtime-orchestrator/src/runtime_orchestrator/
# → up 3 levels to repo root, then governanza/asset-operational-logic-engine_050/patterns/
_REPO_ROOT = Path(__file__).resolve().parents[3]
_PATTERNS_DIR = _REPO_ROOT / "governanza" / "asset-operational-logic-engine_050" / "patterns"


def patterns_directory() -> Path:
    """Return the absolute Path to the patterns directory."""
    return _PATTERNS_DIR


@lru_cache(maxsize=None)
def _load_pattern_file(asset_family: str) -> dict[str, Any] | None:
    """Load and cache a single pattern JSON. Returns None if absent or invalid."""
    if not asset_family:
        return None
    safe_name = asset_family.strip().lower().replace(" ", "_")
    if not safe_name or "/" in safe_name or ".." in safe_name:
        return None
    candidate = _PATTERNS_DIR / f"{safe_name}.json"
    if not candidate.exists():
        return None
    try:
        data = json.loads(candidate.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def load_pattern_library(asset_family: str) -> dict[str, Any] | None:
    """Return the read-only pattern dict for `asset_family`, or None.

    The returned dict carries:
      - asset_family: str
      - library_version: str (SemVer)
      - last_validated_at: str (ISO date)
      - concept_markers: list[str]
      - axes: dict[axis_name, {concept_markers, falsifiers}]

    Callers must NOT mutate the returned dict (it is the cached payload).
    """
    return _load_pattern_file(asset_family)


def asset_family_concept_markers(asset_family: str) -> set[str]:
    """Convenience: flat set of concept_markers for an asset family.

    Returns empty set if the family is not registered.
    """
    pattern = load_pattern_library(asset_family)
    if pattern is None:
        return set()
    flat = set()
    for token in pattern.get("concept_markers", []) or []:
        if isinstance(token, str) and token.strip():
            flat.add(token.strip().lower())
    for axis_data in (pattern.get("axes", {}) or {}).values():
        for token in (axis_data.get("concept_markers", []) or []):
            if isinstance(token, str) and token.strip():
                flat.add(token.strip().lower())
    return flat


def list_registered_families() -> list[str]:
    """Return the asset families with a JSON file present."""
    if not _PATTERNS_DIR.exists():
        return []
    return sorted(
        path.stem
        for path in _PATTERNS_DIR.glob("*.json")
        if path.is_file()
    )


def reset_cache() -> None:
    """Clear the pattern cache. Useful for tests that mutate JSON files."""
    _load_pattern_file.cache_clear()
