"""Comparable Facility Finder — peer set by NAICS + climate + state.

Derives a peer comparison context by intersecting:
  · State (geographic)
  · Climate zone (similar weather load)
  · Asset family (similar process type)
  · EPA Envirofacts neighbors (already-fetched data)

Returns a list of "peer candidates" the framework should compare
against — solving the "verbatim nugget reuse" problem where the
framework cycled the SAME peer set for every case.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from .base import FetcherContext, FetcherResult, FetcherStatus


SOURCE_KEY = "comparable_finder"


# Asset family → NAICS keyword hints (used to filter EPA neighbors).
_ASSET_FAMILY_NAICS_KEYWORDS: dict[str, list[str]] = {
    "cold_chain_facility":      ["refrigerat", "cold storage", "warehous"],
    "cold_chain_distribution":  ["refrigerat", "cold storage", "distribut"],
    "manufacturing_facility":   ["manufactur", "fabric", "plant"],
    "warehouse_distribution":   ["warehous", "distribut", "logistic"],
    "commercial_building":      ["office", "commercial", "retail"],
    "datacenter":               ["data", "computer", "telecom"],
    "thermal_process_facility": ["thermal", "process heat", "boiler"],
    "food_processing":          ["food", "beverage", "dairy", "meat"],
    "fulfillment_center":       ["fulfill", "e-commerce", "logistic"],
    "infrastructure_node":      ["rail", "transit", "infrastruct"],
}


def fetch(
    context: FetcherContext,
    *,
    epa_neighbors: list[dict] | None = None,
    osm_neighbors: list[dict] | None = None,
) -> FetcherResult:
    """Build a peer comparison set from already-fetched neighbor data.

    Args:
      context: facility context
      epa_neighbors: list of facility dicts from epa_envirofacts.fetch().payload.facilities_in_city
      osm_neighbors: list of neighbors dicts from osm_overpass.fetch().payload.neighbors

    Output payload:
      peer_candidates: filtered list with relevance score
      total_evaluated: int
      best_peer_count: int
    """
    now = _dt.datetime.utcnow().isoformat() + "Z"
    epa_neighbors = epa_neighbors or []
    osm_neighbors = osm_neighbors or []

    asset_family = (context.asset_family or "").strip().lower()
    keywords = _ASSET_FAMILY_NAICS_KEYWORDS.get(asset_family, [])

    candidates: list[dict] = []
    # Score EPA neighbors by name/site_type containing asset-family keywords
    for f in epa_neighbors:
        name      = str(f.get("name", "") or "").lower()
        site_type = str(f.get("site_type", "") or "").lower()
        score = 0
        matched_kws: list[str] = []
        for kw in keywords:
            if kw in name or kw in site_type:
                score += 1
                matched_kws.append(kw)
        if score > 0:
            candidates.append({
                "source":         "epa_envirofacts",
                "name":           f.get("name", ""),
                "address":        f.get("address", ""),
                "city":           f.get("city", ""),
                "state":          f.get("state", ""),
                "registry_id":    f.get("registry_id", ""),
                "site_type":      f.get("site_type", ""),
                "relevance":      score,
                "matched_keywords": matched_kws,
            })
    # Score OSM neighbors by building/industrial tags
    for s in osm_neighbors:
        name = str(s.get("name", "") or "").lower()
        score = 0
        matched_kws: list[str] = []
        if s.get("building") == "industrial" and asset_family in (
            "manufacturing_facility", "cold_chain_facility", "warehouse_distribution"
        ):
            score += 1
            matched_kws.append("building=industrial")
        if s.get("man_made") == "warehouse" and "warehouse" in asset_family:
            score += 1
            matched_kws.append("man_made=warehouse")
        if s.get("cold_storage") and "cold_chain" in asset_family:
            score += 2
            matched_kws.append("cold_storage")
        for kw in keywords:
            if kw in name:
                score += 1
                matched_kws.append(f"name~{kw}")
                break
        if score > 0:
            candidates.append({
                "source":         "openstreetmap",
                "name":           s.get("name", "") or "(unnamed)",
                "osm_id":         s.get("osm_id", ""),
                "lat":            s.get("lat"),
                "lon":            s.get("lon"),
                "building":       s.get("building", ""),
                "relevance":      score,
                "matched_keywords": matched_kws,
            })

    # Sort by relevance desc, cap at 20
    candidates.sort(key=lambda c: c["relevance"], reverse=True)
    best = candidates[:20]

    payload = {
        "asset_family":      asset_family,
        "state":             context.state,
        "search_keywords":   keywords,
        "peer_candidates":   best,
        "best_peer_count":   len(best),
        "total_evaluated":   len(epa_neighbors) + len(osm_neighbors),
    }
    status = FetcherStatus.OK if best else FetcherStatus.NO_DATA
    return FetcherResult(
        source_key=SOURCE_KEY,
        status=status,
        payload=payload,
        locator=f"comparables:{asset_family}/{context.state}",
        record_count=len(best),
        fetched_at=now,
    )
