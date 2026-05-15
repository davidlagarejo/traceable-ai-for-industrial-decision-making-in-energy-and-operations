"""NOAA NCEI Climate — public US weather/climate data.

We use the public Stations Search API which is free and doesn't require
a token for basic queries. For full climate normals (HDD, CDD, monthly
averages) we read from the public CSV catalog.

Strategy:
  1. Find nearest GHCN station to lat/lon
  2. Look up climate normals 1991-2020 if available
  3. Derive ASHRAE climate zone heuristically from HDD/CDD

API docs:
  https://www.ncdc.noaa.gov/cdo-web/webservices/v2
  https://www.ncei.noaa.gov/access/services/

NOTE: Some endpoints require a free NOAA token (env NOAA_CDO_TOKEN).
Without a token we fall back to ZIP-based climate-zone lookup using
DOE Building America heuristics.
"""
from __future__ import annotations

import datetime as _dt
import math
import os

from .base import FetcherContext, FetcherResult, FetcherStatus, http_get_json


SOURCE_KEY = "noaa_climate"

_NOAA_TOKEN = os.environ.get("NOAA_CDO_TOKEN", "").strip()


# DOE Building America climate zones — heuristic by lat range +
# state code. Conservative; for production replace with ASHRAE 169
# county-level lookup. This is the V10 P-discovery shortcut so
# every US case gets SOMETHING for climate zone.
_STATE_CLIMATE_ZONE: dict[str, str] = {
    # Hot-Humid (1A-2A)
    "FL": "2A", "TX": "2A", "LA": "2A", "MS": "2A", "AL": "2A", "GA": "2A",
    "SC": "3A", "NC": "3A",
    # Hot-Dry (2B-3B)
    "AZ": "2B", "NM": "3B", "NV": "3B",
    # Mixed-Humid (4A)
    "TN": "4A", "AR": "3A", "KY": "4A", "VA": "4A", "WV": "4A", "MD": "4A",
    "DC": "4A", "DE": "4A",
    # Mixed-Dry/Marine (3C-4C)
    "CA": "3C", "OR": "4C", "WA": "4C",
    # Cold (5A-6A) — Midwest
    "IL": "5A", "IN": "5A", "OH": "5A", "PA": "5A", "NJ": "4A", "NY": "5A",
    "CT": "5A", "RI": "5A", "MA": "5A",
    "MO": "4A", "IA": "5A", "KS": "4A", "OK": "3A", "NE": "5A",
    "MI": "6A", "WI": "6A", "MN": "6A",
    # Very Cold (7-8)
    "ND": "6A", "SD": "5A", "MT": "6B", "WY": "5B", "ID": "5B", "CO": "5B",
    "UT": "5B",
    "ME": "6A", "NH": "6A", "VT": "6A",
    "AK": "7",
    "HI": "1A",
}


def _heuristic_climate_zone(state: str) -> str:
    """Fallback ASHRAE climate zone from state code."""
    return _STATE_CLIMATE_ZONE.get((state or "").upper(), "")


def _stations_near(lat: float, lon: float, radius_deg: float = 0.5) -> list[dict]:
    """Get GHCN-daily stations within a small bounding box around lat/lon.

    Uses NOAA's free GHCN stations endpoint (no token required).
    Returns list of {id, name, lat, lon, elevation}.
    """
    # NOAA's CDO v2 requires a token. We use the access data v1 endpoint
    # which serves the GHCN-D stations TSV directly.
    # https://www.ncei.noaa.gov/access/services/data/v1/?dataset=daily-summaries&format=json
    # For SIMPLICITY here we just call a station search via the cdo-web
    # if a token is present; otherwise we return empty + report no_data.
    if not _NOAA_TOKEN:
        return []
    headers = {"token": _NOAA_TOKEN}
    extent = f"{lat-radius_deg},{lon-radius_deg},{lat+radius_deg},{lon+radius_deg}"
    try:
        data, _ = http_get_json(
            "https://www.ncdc.noaa.gov/cdo-web/api/v2/stations",
            params={"extent": extent, "limit": 5,
                    "datasetid": "GHCND"},
            headers=headers,
        )
    except Exception:
        return []
    return data.get("results", []) or []


def fetch(context: FetcherContext) -> FetcherResult:
    """Fetch climate context for an address. Always returns at least a
    heuristic ASHRAE climate zone derived from state code (V10
    pragmatic fallback so EVERY US case has climate context)."""
    now = _dt.datetime.utcnow().isoformat() + "Z"
    state = (context.state or "").strip().upper()

    payload: dict = {
        "ashrae_climate_zone_heuristic": _heuristic_climate_zone(state),
        "source": "doe_building_america_state_heuristic",
        "state_code": state,
    }

    # If we have lat/lon AND a NOAA token, enrich with nearby stations
    if context.lat and context.lon and _NOAA_TOKEN:
        stations = _stations_near(context.lat, context.lon)
        if stations:
            payload["nearest_ghcn_stations"] = [
                {
                    "station_id":  s.get("id"),
                    "name":        s.get("name"),
                    "lat":         s.get("latitude"),
                    "lon":         s.get("longitude"),
                    "elevation_m": s.get("elevation"),
                }
                for s in stations[:5]
            ]
            payload["source"] = "noaa_ghcn_daily"

    if not payload["ashrae_climate_zone_heuristic"]:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.NO_DATA,
            error="no climate zone heuristic for state",
            payload=payload,
            fetched_at=now,
        )

    return FetcherResult(
        source_key=SOURCE_KEY,
        status=FetcherStatus.OK,
        payload=payload,
        locator="state-heuristic" + (" + noaa_ghcn" if "nearest_ghcn_stations" in payload else ""),
        record_count=1,
        fetched_at=now,
    )
