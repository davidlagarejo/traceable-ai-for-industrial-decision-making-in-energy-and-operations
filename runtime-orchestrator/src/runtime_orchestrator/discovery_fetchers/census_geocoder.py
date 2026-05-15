"""Census Geocoder — US Census Bureau public API (no key required).

API root:
  https://geocoding.geo.census.gov/geocoder

Endpoints used:
  · /locations/onelineaddress      → lat/lon + matched address
  · /geographies/onelineaddress    → above + tract / county / state geocodes

Free, no API key. Rate limit ~250 req/min.
Docs: https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
"""
from __future__ import annotations

import datetime as _dt

from .base import FetcherContext, FetcherResult, FetcherStatus, http_get_json


SOURCE_KEY = "census_geocoder"

_BASE = "https://geocoding.geo.census.gov/geocoder"
_BENCHMARK = "Public_AR_Current"
_VINTAGE   = "Current_Current"


def fetch(context: FetcherContext) -> FetcherResult:
    """Geocode an address via Census. Returns lat/lon + geoid + tract."""
    address = (context.address or "").strip()
    if not address:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="no address provided",
            fetched_at=_dt.datetime.utcnow().isoformat() + "Z",
        )
    url = f"{_BASE}/geographies/onelineaddress"
    params = {
        "address":   address,
        "benchmark": _BENCHMARK,
        "vintage":   _VINTAGE,
        "format":    "json",
    }
    try:
        data, locator = http_get_json(url, params=params)
    except Exception as exc:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.ERROR,
            error=f"{type(exc).__name__}: {exc}",
            locator=url,
            fetched_at=_dt.datetime.utcnow().isoformat() + "Z",
        )

    matches = (data.get("result", {}) or {}).get("addressMatches") or []
    if not matches:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.NO_DATA,
            payload={"raw_response": data},
            error="no address match",
            locator=locator,
            fetched_at=_dt.datetime.utcnow().isoformat() + "Z",
        )

    m = matches[0]
    coords = m.get("coordinates", {}) or {}
    geos   = m.get("geographies", {}) or {}
    tracts = (geos.get("Census Tracts") or geos.get("Census Tracts ") or [])
    counties = (geos.get("Counties") or [])
    states   = (geos.get("States") or [])
    payload = {
        "matched_address":   m.get("matchedAddress", ""),
        "lat":               coords.get("y"),
        "lon":               coords.get("x"),
        "tract_geoid":       (tracts[0].get("GEOID") if tracts else ""),
        "tract_name":        (tracts[0].get("NAME") if tracts else ""),
        "county_name":       (counties[0].get("NAME") if counties else ""),
        "county_geoid":      (counties[0].get("GEOID") if counties else ""),
        "state_name":        (states[0].get("NAME") if states else ""),
        "state_geoid":       (states[0].get("GEOID") if states else ""),
        "state_abbreviation": (states[0].get("STUSAB") if states else ""),
    }
    return FetcherResult(
        source_key=SOURCE_KEY,
        status=FetcherStatus.OK,
        payload=payload,
        locator=locator,
        record_count=1,
        fetched_at=_dt.datetime.utcnow().isoformat() + "Z",
    )
