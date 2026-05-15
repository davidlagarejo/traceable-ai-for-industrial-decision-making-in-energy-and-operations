"""EPA Envirofacts — national facility registry + permits + emissions.

Envirofacts is EPA's master public registry. API root:
  https://enviro.epa.gov/enviro/efservice/

Key tables we query:
  · FRS_FACILITY_SITE — Facility Registry Service (any registered facility)
  · ICIS_AIR_FACILITIES — air permits (NESHAP, NSPS, Title V)
  · TRI_FACILITY — toxic release inventory
  · RCRA_FACILITY — hazardous waste handlers
  · GHGP_FACILITIES — greenhouse gas reporting (>25,000 tCO2e/yr)

Format syntax:
  https://enviro.epa.gov/enviro/efservice/<table>/<col>/<op>/<value>/<count_or_offset>/JSON

No API key required. Public data.
"""
from __future__ import annotations

import datetime as _dt

from .base import FetcherContext, FetcherResult, FetcherStatus, http_get_json


SOURCE_KEY = "epa_envirofacts"
_BASE = "https://enviro.epa.gov/enviro/efservice"


def _city_token(city: str) -> str:
    """EPA uses uppercased city name for matching."""
    return (city or "").strip().upper().replace(" ", "%20")


def _query_facilities_by_city_state(city: str, state: str, limit: int = 20,
                                     zip_code: str = "") -> list[dict]:
    """Look up facilities in FRS_FACILITY_SITE. Strict city+state filter.
    If zip_code is provided, filter by postal_code for relevance."""
    if not city or not state:
        return []
    # Strict equality on both city and state
    parts = [
        f"STATE_CODE/=/{state}",
        f"CITY_NAME/=/{_city_token(city)}",
    ]
    if zip_code:
        zip5 = (zip_code or "").strip()[:5]
        if zip5:
            parts.append(f"POSTAL_CODE/BEGINNING/{zip5}")
    url = f"{_BASE}/FRS_FACILITY_SITE/" + "/".join(parts) + f"/0/{limit}/JSON"
    try:
        data, _ = http_get_json(url)
    except Exception:
        return []
    if isinstance(data, dict):
        return [data]
    return data if isinstance(data, list) else []


def _query_ghg_emitters(state: str, limit: int = 10) -> list[dict]:
    """Find big GHG emitters in the same state — useful context for
    comparable peers."""
    if not state:
        return []
    url = (
        f"{_BASE}/V_GHG_EMITTER_FACILITY"
        f"/STATE/=/{state}"
        f"/0/{limit}/JSON"
    )
    try:
        data, _ = http_get_json(url)
    except Exception:
        return []
    if isinstance(data, dict):
        return [data]
    return data if isinstance(data, list) else []


def fetch(context: FetcherContext) -> FetcherResult:
    """Look up federal environmental footprint of the target's
    surroundings (city+state).

    Returns:
      payload.facilities_in_city        — FRS registered facilities in city
      payload.ghg_emitters_in_state     — GHGRP facilities (>25k tCO2e)
      payload.facility_count_city       — count
      payload.estimated_local_industry  — list of subsector names found
    """
    now = _dt.datetime.utcnow().isoformat() + "Z"
    city  = (context.city  or "").strip()
    state = (context.state or "").strip().upper()
    if not city and not state:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="no city/state provided",
            fetched_at=now,
        )

    facilities = _query_facilities_by_city_state(
        city, state, limit=25, zip_code=context.zip_code,
    )
    ghg = _query_ghg_emitters(state, limit=15)

    # Aggregate sector hints from facility classifications.
    # EPA Envirofacts returns lowercase field names.
    subsectors: set[str] = set()
    for f in facilities:
        for k in ("site_type_name", "primary_name"):
            v = str(f.get(k, "") or "").strip()
            if v:
                subsectors.add(v[:60])

    payload = {
        "facilities_in_city":        [
            {
                "registry_id":   f.get("registry_id"),
                "name":          f.get("primary_name") or f.get("std_name"),
                "address":       f.get("location_address") or f.get("std_full_address"),
                "city":          f.get("city_name"),
                "state":         f.get("state_code"),
                "zip":           f.get("postal_code"),
                "site_type":     f.get("site_type_name"),
                "operating":     f.get("operating_status"),
                "active_status": f.get("interest_status_code"),
            }
            for f in facilities[:25]
        ],
        "facility_count_city":       len(facilities),
        "ghg_emitters_in_state":     [
            {
                "facility_id":     g.get("FACILITY_ID"),
                "name":            g.get("FACILITY_NAME"),
                "city":            g.get("CITY"),
                "ghg_tCO2e":       g.get("GHG_QUANTITY") or g.get("TOTAL_REPORTED_EMISSIONS"),
                "industry_type":   g.get("INDUSTRY_TYPE_SECTORS"),
            }
            for g in ghg[:15]
        ],
        "ghg_emitter_count_state":   len(ghg),
        "estimated_local_industry":  sorted(subsectors)[:20],
    }

    if not facilities and not ghg:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.NO_DATA,
            payload=payload,
            error="no EPA records for this city/state",
            fetched_at=now,
        )
    return FetcherResult(
        source_key=SOURCE_KEY,
        status=FetcherStatus.OK,
        payload=payload,
        locator=f"epa_envirofacts:{state}/{city}",
        record_count=len(facilities) + len(ghg),
        fetched_at=now,
    )
