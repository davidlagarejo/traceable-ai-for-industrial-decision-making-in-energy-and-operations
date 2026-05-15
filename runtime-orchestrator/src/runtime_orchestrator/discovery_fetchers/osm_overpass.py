"""OpenStreetMap Overpass — nearby facilities + industrial neighbors.

Overpass API:  https://overpass-api.de/api/interpreter
Free, no key required, rate-limited but generous.

We query a small bounding box around lat/lon for:
  · industrial buildings (man_made=warehouse, industrial=*, building=industrial)
  · commercial neighbors
  · cold storage / refrigeration tags (cold_storage=*)
  · nearby utilities / substations
"""
from __future__ import annotations

import datetime as _dt
import urllib.parse
import urllib.request

from .base import FetcherContext, FetcherResult, FetcherStatus, DEFAULT_USER_AGENT


SOURCE_KEY = "osm_overpass"
_OVERPASS = "https://overpass-api.de/api/interpreter"


_QUERY_TEMPLATE = """
[out:json][timeout:25];
(
  node["building"="industrial"](around:{radius_m},{lat},{lon});
  way["building"="industrial"](around:{radius_m},{lat},{lon});
  way["industrial"](around:{radius_m},{lat},{lon});
  way["man_made"="warehouse"](around:{radius_m},{lat},{lon});
  way["building"="warehouse"](around:{radius_m},{lat},{lon});
  way["building"~"^(commercial|retail|office)$"](around:{radius_m},{lat},{lon});
  way["cold_storage"](around:{radius_m},{lat},{lon});
  way["power"="substation"](around:{radius_m_subst},{lat},{lon});
);
out tags center 60;
"""


def _post_overpass(query: str, timeout: int = 30) -> dict | None:
    """POST query to Overpass API."""
    req = urllib.request.Request(_OVERPASS, method="POST")
    req.add_header("User-Agent", DEFAULT_USER_AGENT)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    try:
        with urllib.request.urlopen(req, data=body, timeout=timeout) as resp:
            import json as _json
            return _json.loads(resp.read())
    except Exception:
        return None


def fetch(context: FetcherContext) -> FetcherResult:
    """Query OSM for industrial/commercial neighbors within 1 km."""
    now = _dt.datetime.utcnow().isoformat() + "Z"
    if not context.lat or not context.lon:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="no lat/lon provided",
            fetched_at=now,
        )
    query = _QUERY_TEMPLATE.format(
        lat=context.lat, lon=context.lon,
        radius_m=1000, radius_m_subst=2500,
    )
    data = _post_overpass(query)
    if data is None:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.ERROR,
            error="Overpass request failed (network/timeout)",
            fetched_at=now,
        )
    elements = data.get("elements", []) or []
    if not elements:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.NO_DATA,
            error="no industrial/commercial neighbors found within 1 km",
            fetched_at=now,
        )

    def _shape(e: dict) -> dict:
        tags = e.get("tags", {}) or {}
        center = e.get("center", {}) or {}
        return {
            "osm_id":      f"{e.get('type','?')}/{e.get('id','?')}",
            "name":        tags.get("name", ""),
            "building":    tags.get("building", ""),
            "industrial":  tags.get("industrial", ""),
            "operator":    tags.get("operator", ""),
            "lat":         e.get("lat") or center.get("lat"),
            "lon":         e.get("lon") or center.get("lon"),
            "cold_storage": tags.get("cold_storage", ""),
            "man_made":    tags.get("man_made", ""),
            "power":       tags.get("power", ""),
            "tags":        {k: v for k, v in tags.items() if k in
                            {"addr:street", "addr:city", "ref", "wikidata", "wikipedia"}},
        }

    shaped = [_shape(e) for e in elements[:60]]
    industrial = [s for s in shaped if s["building"] == "industrial" or s["industrial"] or s["man_made"] == "warehouse"]
    cold = [s for s in shaped if s["cold_storage"]]
    substations = [s for s in shaped if s["power"] == "substation"]

    payload = {
        "neighbors":                  shaped,
        "neighbor_count":             len(shaped),
        "industrial_count":           len(industrial),
        "cold_storage_count":         len(cold),
        "nearby_substation_count":    len(substations),
        "radius_m":                   1000,
    }
    return FetcherResult(
        source_key=SOURCE_KEY,
        status=FetcherStatus.OK,
        payload=payload,
        locator=f"overpass:around({context.lat},{context.lon},1000m)",
        record_count=len(shaped),
        fetched_at=now,
    )
