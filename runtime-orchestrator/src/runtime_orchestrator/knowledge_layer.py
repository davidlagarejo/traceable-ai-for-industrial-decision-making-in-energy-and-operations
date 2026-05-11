"""Knowledge Layer YAML loader (Layer A — Governed Knowledge).

Loads the 4 dedicated knowledge YAMLs added in V2 Gap F:
  - machine_logic.yaml
  - compressed_air_logic.yaml
  - control_boundary_logic.yaml
  - power_quality_logic.yaml

These YAMLs cross-reference registry pattern_ids with industrial source_ids
from the catalog (Gap C). They were inert until V2-LIVE Item 4 wired them
into motor_050 (Asset Operational Logic) and motor_052 (Loss Pattern &
Maintenance Reality), where they surface as `knowledge_layer_registry`
for downstream consumers (composer, validators).

Usage:
  from runtime_orchestrator.knowledge_layer import load_knowledge_layer_registry

  reg = load_knowledge_layer_registry()
  # reg = {"machine_logic": {...}, "compressed_air_logic": {...},
  #        "control_boundary_logic": {...}, "power_quality_logic": {...}}
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


_REPO_ROOT = Path(__file__).resolve().parents[3]
_ZLAB_SKILL_DIR = _REPO_ROOT / "runtime-orchestrator" / "zlab_skill"


# Knowledge blocks (V2 Gap F) — short_id → filename. Stable order for
# deterministic output across processes.
_KNOWLEDGE_BLOCKS: tuple[tuple[str, str], ...] = (
    ("machine_logic", "machine_logic.yaml"),
    ("compressed_air_logic", "compressed_air_logic.yaml"),
    ("control_boundary_logic", "control_boundary_logic.yaml"),
    ("power_quality_logic", "power_quality_logic.yaml"),
)


def knowledge_layer_dir() -> Path:
    return _ZLAB_SKILL_DIR


@lru_cache(maxsize=1)
def load_knowledge_layer_registry() -> dict[str, dict[str, Any]]:
    """Load all 4 V2-Gap-F knowledge YAMLs.

    Returns a dict keyed by short_id (machine_logic, compressed_air_logic,
    control_boundary_logic, power_quality_logic). Missing files yield an
    empty dict for that block — never raises.
    """
    out: dict[str, dict[str, Any]] = {}
    for short_id, filename in _KNOWLEDGE_BLOCKS:
        path = _ZLAB_SKILL_DIR / filename
        if not path.exists():
            out[short_id] = {}
            continue
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        out[short_id] = payload
    return out


def pattern_ids_for_block(short_id: str) -> list[str]:
    reg = load_knowledge_layer_registry()
    block = reg.get(short_id, {}) or {}
    eq = block.get("registry_equivalence", {}) or {}
    return list(eq.get("pattern_ids", []) or [])


def industrial_sources_for_block(short_id: str) -> list[str]:
    reg = load_knowledge_layer_registry()
    block = reg.get(short_id, {}) or {}
    eq = block.get("registry_equivalence", {}) or {}
    return list(eq.get("industrial_sources", []) or [])


def knowledge_layer_summary() -> dict[str, Any]:
    """Compact projection of all 4 blocks for motor outputs.

    Returns:
      {
        "blocks": [
          {"short_id": "machine_logic", "knowledge_type": "...",
           "pattern_ids": [...], "industrial_sources": [...]},
          ...
        ],
        "total_blocks": 4,
        "total_pattern_refs": N,
        "total_source_refs": M,
      }
    """
    reg = load_knowledge_layer_registry()
    blocks: list[dict[str, Any]] = []
    total_patterns = 0
    total_sources = 0
    for short_id, _filename in _KNOWLEDGE_BLOCKS:
        block = reg.get(short_id, {}) or {}
        eq = block.get("registry_equivalence", {}) or {}
        pattern_ids = list(eq.get("pattern_ids", []) or [])
        sources = list(eq.get("industrial_sources", []) or [])
        blocks.append(
            {
                "short_id": short_id,
                "knowledge_type": str(eq.get("knowledge_type") or ""),
                "pattern_ids": pattern_ids,
                "industrial_sources": sources,
                "scope_count": len(block.get("scope", []) or []),
                "governing_principles_count": len(block.get("governing_principles", []) or []),
            }
        )
        total_patterns += len(pattern_ids)
        total_sources += len(sources)
    return {
        "blocks": blocks,
        "total_blocks": len(blocks),
        "total_pattern_refs": total_patterns,
        "total_source_refs": total_sources,
    }
