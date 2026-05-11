"""Industrial Source Catalog loader (Layer A — Governed Knowledge).

Loads the 100+ authoritative industrial sources catalogued in
`governanza/asset-operational-logic-engine_050/sources/industrial_source_catalog.json`
(RECOVERY_2026-05-10 §3, Gap C).

Each source carries:
  - authority_tier (1=regulatory/standards, 2=peer-reviewed/handbooks,
    3=vendor/industry whitepapers)
  - asset_families (list of families the source applies to)
  - topic_tags (e.g. refrigeration_duty, compressed_air_logic, ...)
  - jurisdiction, citation_format

Consumers:
  - motor_035 (public_data_routing) — Gap D will use this for per-family
    source routing with authority hierarchy.
  - motor_062 (scenario_justification_validator) — validates that the
    `source` field on each active scenario references a catalog entry.

Usage:
  from runtime_orchestrator.source_catalog import (
      load_catalog, sources_for_family, sources_for_tag,
  )

  iiar = load_catalog()["sources"]
  cold = sources_for_family("cold_chain_facility")
  refr = sources_for_tag("refrigeration_duty")
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATALOG_PATH = (
    _REPO_ROOT
    / "governanza"
    / "asset-operational-logic-engine_050"
    / "sources"
    / "industrial_source_catalog.json"
)


def catalog_path() -> Path:
    return _CATALOG_PATH


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    """Load the full catalog JSON (cached). Returns an empty catalog if absent."""
    if not _CATALOG_PATH.exists():
        return {"catalog_id": "industrial_source_catalog", "sources": []}
    try:
        return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"catalog_id": "industrial_source_catalog", "sources": []}


def all_sources() -> list[dict[str, Any]]:
    return list(load_catalog().get("sources", []) or [])


def source_by_id(source_id: str) -> dict[str, Any] | None:
    if not source_id:
        return None
    for entry in all_sources():
        if entry.get("source_id") == source_id:
            return entry
    return None


@lru_cache(maxsize=64)
def sources_for_family(asset_family: str) -> tuple[dict[str, Any], ...]:
    """Return the immutable tuple of sources applicable to a given asset family."""
    if not asset_family:
        return tuple()
    family = asset_family.strip().lower()
    if not family:
        return tuple()
    matches = [
        entry
        for entry in all_sources()
        if family in {str(f).strip().lower() for f in entry.get("asset_families", []) or []}
    ]
    matches.sort(key=lambda e: (e.get("authority_tier", 9), e.get("source_id", "")))
    return tuple(matches)


@lru_cache(maxsize=128)
def sources_for_tag(topic_tag: str) -> tuple[dict[str, Any], ...]:
    """Return sources whose topic_tags include the given tag."""
    if not topic_tag:
        return tuple()
    tag = topic_tag.strip().lower()
    matches = [
        entry
        for entry in all_sources()
        if tag in {str(t).strip().lower() for t in entry.get("topic_tags", []) or []}
    ]
    matches.sort(key=lambda e: (e.get("authority_tier", 9), e.get("source_id", "")))
    return tuple(matches)


def routing_for_family(asset_family: str) -> dict[int, list[dict[str, Any]]]:
    """Return sources for a family bucketed by authority_tier.

    Output: {1: [...], 2: [...], 3: [...]}

    motor_035 (Gap D) consumes this to emit per-family source hierarchy.
    """
    buckets: dict[int, list[dict[str, Any]]] = {1: [], 2: [], 3: []}
    for entry in sources_for_family(asset_family):
        tier = entry.get("authority_tier")
        if tier in buckets:
            buckets[tier].append(entry)
    return buckets


def is_known_source(source_reference: str) -> bool:
    """Heuristic: does `source_reference` mention any known source name/id?

    Used by motor_062 to mark scenario.source fields as either backed by
    a catalog entry or unstructured prose.
    """
    if not source_reference:
        return False
    text = source_reference.strip().lower()
    if not text:
        return False
    for entry in all_sources():
        if entry.get("source_id", "").lower() in text:
            return True
        name_tokens = (entry.get("name") or "").lower().split(" - ")
        primary = name_tokens[0].strip()
        if primary and primary in text:
            return True
    return False
