"""Source confidence registry (V4 P0 item 7).

Wraps the existing 139-source `industrial_source_catalog.json` (Gap C,
scaffolding S6) with a confidence dimension that the research engine
uses when deciding which extractions to promote.

The catalog already declares `authority_tier` (1 regulatory, 2 peer-
review/handbook, 3 vendor/industry). This module:

  - exposes `source_confidence_for(source_id)` returning a tuple
    (tier, confidence_band, allowed_use)
  - declares the canonical confidence bands
  - documents what each tier permits

The confidence value lives ONLY in code derived from the catalog; we do
NOT introduce new content (the catalog is S6 scaffolding — V4 Phase 0
must not expand it).
"""
from __future__ import annotations

from typing import Any

from ..source_catalog import source_by_id


# Confidence bands and their epistemic meaning.
SOURCE_CONFIDENCE_TIERS: dict[int, dict[str, Any]] = {
    1: {
        "band": "high",
        "description": (
            "Regulatory body, codes, mandatory standards. Authoritative for "
            "compliance framing; permits TAD validation actions."
        ),
        "permits_closure": True,
        "claim_ceiling_max": "L2",
        "examples": ["DOE Better Plants", "EPA GHGRP", "IIAR Bulletins", "ASHRAE 90.1"],
    },
    2: {
        "band": "medium-high",
        "description": (
            "Peer-reviewed engineering handbook, national lab report, "
            "industry consensus standard. Useful for structural reasoning "
            "and pattern derivation."
        ),
        "permits_closure": True,
        "claim_ceiling_max": "L2",
        "examples": ["ASHRAE Handbook", "ACEEE Summer Study", "EPRI Reports"],
    },
    3: {
        "band": "medium",
        "description": (
            "Vendor application guide, industry whitepaper, trade-association "
            "case study, market report. Useful as cross-reference but cannot "
            "be the sole closure source."
        ),
        "permits_closure": False,
        "claim_ceiling_max": "L1",
        "examples": ["Danfoss Handbook", "CBRE Sustainability Report"],
    },
}


def source_confidence_for(source_id: str) -> dict[str, Any] | None:
    """Return the confidence record for a catalog source_id, or None if
    the source is not in the 139-source catalog."""
    if not source_id:
        return None
    entry = source_by_id(source_id)
    if not entry:
        return None
    tier = int(entry.get("authority_tier") or 0)
    tier_info = SOURCE_CONFIDENCE_TIERS.get(tier)
    if not tier_info:
        return None
    return {
        "source_id": source_id,
        "name": entry.get("name", ""),
        "publisher": entry.get("publisher", ""),
        "authority_tier": tier,
        "confidence_band": tier_info["band"],
        "permits_closure": tier_info["permits_closure"],
        "claim_ceiling_max": tier_info["claim_ceiling_max"],
        "asset_families": list(entry.get("asset_families", []) or []),
        "topic_tags": list(entry.get("topic_tags", []) or []),
    }


def aggregate_confidence(source_ids: list[str]) -> str:
    """Return the dominant confidence band when multiple sources are cited.

    Rule: HIGH if any tier-1 source present; MEDIUM-HIGH if only tier-2;
    MEDIUM if only tier-3 or unrecognized.
    """
    found_tiers: set[int] = set()
    for sid in source_ids or []:
        info = source_confidence_for(sid)
        if info:
            found_tiers.add(info["authority_tier"])
    if 1 in found_tiers:
        return "high"
    if 2 in found_tiers:
        return "medium-high"
    if 3 in found_tiers:
        return "medium"
    return "unknown"
