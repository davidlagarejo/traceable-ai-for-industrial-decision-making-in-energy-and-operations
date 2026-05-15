"""Discovery Orchestrator — runs every US-wide fetcher in sequence and
returns a single bundle the pipeline can consume.

Flow:
  1. Census Geocoder         → enriches context with lat/lon
  2. NOAA Climate            → climate zone heuristic
  3. EPA Envirofacts         → national facility registry + GHG emitters
  4. EIA OpenData            → electricity prices by state
  5. OSM Overpass            → industrial/commercial neighbors
  6. Comparable Finder       → peer candidates from EPA + OSM data

Hard Gate (FIX-7):
  After all fetchers complete, count how many returned status=OK.
  If found_count < MIN_REAL_DATA_THRESHOLD, the orchestrator reports
  `sufficient_for_pipeline=False` so motor_028 can fail fast instead of
  running 58 motors on empty data.

Each fetcher failure is isolated — one fetcher erroring does NOT crash
the others.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from .base import FetcherContext, FetcherResult, FetcherStatus
from . import (
    census_geocoder,
    company_web_scraper,
    comparable_finder,
    eia_opendata,
    epa_envirofacts,
    noaa_climate,
    osm_overpass,
)


# Hard gate: pipeline must NOT proceed unless we have at least
# this many OK fetcher results.
MIN_REAL_DATA_THRESHOLD = 3


def _parse_city_from_matched(matched: str) -> str:
    """Census Geocoder returns 'STREET, CITY, STATE, ZIP'. Extract CITY."""
    parts = [p.strip() for p in (matched or "").split(",")]
    if len(parts) >= 3:
        return parts[-3]  # city is third from end
    return ""


def _parse_zip_from_matched(matched: str) -> str:
    """Last comma-separated token is the ZIP."""
    parts = [p.strip() for p in (matched or "").split(",")]
    if parts:
        last = parts[-1]
        # ZIP is the first 5 digits
        digits = "".join(c for c in last if c.isdigit())[:5]
        if len(digits) == 5:
            return digits
    return ""


def _enrich_context_from_geocoder(
    ctx: FetcherContext, geo: FetcherResult,
) -> FetcherContext:
    """Update context with lat/lon/state/city/zip from Census Geocoder if returned OK."""
    if geo.status != FetcherStatus.OK:
        return ctx
    p = geo.payload
    matched = str(p.get("matched_address") or "")
    return FetcherContext(
        address=ctx.address,
        city=ctx.city or _parse_city_from_matched(matched),
        state=p.get("state_abbreviation") or ctx.state or "",
        zip_code=ctx.zip_code or _parse_zip_from_matched(matched),
        lat=p.get("lat") or ctx.lat,
        lon=p.get("lon") or ctx.lon,
        naics=ctx.naics,
        asset_family=ctx.asset_family,
        facility_name=ctx.facility_name,
    )


def run_full_discovery(context: FetcherContext) -> dict[str, Any]:
    """Run every fetcher in sequence. Returns a bundle dict suitable for
    motor_028 to consume.

    Output shape:
      {
        results:               {source_key: FetcherResult.as_dict()},
        enriched_context:      FetcherContext.as_dict(),
        ok_count:              int,
        no_data_count:         int,
        error_count:           int,
        skip_count:            int,
        sufficient_for_pipeline: bool,
        ok_sources:            [str, ...],
        no_data_sources:       [str, ...],
        error_sources:         [str, ...],
        started_at:            iso8601,
        completed_at:          iso8601,
      }
    """
    started = _dt.datetime.utcnow().isoformat() + "Z"
    results: dict[str, FetcherResult] = {}

    # 1. Census Geocoder
    geo = _safe_run(census_geocoder.fetch, context)
    results[census_geocoder.SOURCE_KEY] = geo

    # Enrich context with lat/lon/state for downstream fetchers
    ctx = _enrich_context_from_geocoder(context, geo)

    # 2. NOAA Climate
    results[noaa_climate.SOURCE_KEY] = _safe_run(noaa_climate.fetch, ctx)

    # 3. EPA Envirofacts
    epa = _safe_run(epa_envirofacts.fetch, ctx)
    results[epa_envirofacts.SOURCE_KEY] = epa

    # 4. EIA OpenData
    results[eia_opendata.SOURCE_KEY] = _safe_run(eia_opendata.fetch, ctx)

    # 5. OSM Overpass
    osm = _safe_run(osm_overpass.fetch, ctx)
    results[osm_overpass.SOURCE_KEY] = osm

    # 6. Comparable Finder (consumes EPA + OSM payloads)
    epa_neighbors = (epa.payload.get("facilities_in_city")
                     if epa.status == FetcherStatus.OK else []) or []
    osm_neighbors = (osm.payload.get("neighbors")
                     if osm.status == FetcherStatus.OK else []) or []
    comp = comparable_finder.fetch(
        ctx, epa_neighbors=epa_neighbors, osm_neighbors=osm_neighbors,
    )
    results[comparable_finder.SOURCE_KEY] = comp

    # 7. Company Web Scraper — uses DuckDuckGo + Playwright. Useful when
    # the facility is private (not in SEC/county records). Slower than
    # the rest of the orchestrator (~10-25s) so it runs LAST.
    # Disabled when facility_name is empty.
    results[company_web_scraper.SOURCE_KEY] = _safe_run(
        company_web_scraper.fetch, ctx, max_pages=3,
    )

    # Tally
    by_status: dict[str, int] = {}
    by_source_status: dict[str, list[str]] = {
        "ok": [], "no_data": [], "error": [], "skip": [],
    }
    for k, r in results.items():
        st_value = r.status.value if isinstance(r.status, FetcherStatus) else str(r.status)
        by_status[st_value] = by_status.get(st_value, 0) + 1
        if st_value in by_source_status:
            by_source_status[st_value].append(k)

    ok_count = by_status.get("ok", 0)
    completed = _dt.datetime.utcnow().isoformat() + "Z"

    return {
        "results":                {k: r.as_dict() for k, r in results.items()},
        "enriched_context":       ctx.as_dict(),
        "ok_count":               ok_count,
        "no_data_count":          by_status.get("no_data", 0),
        "error_count":            by_status.get("error", 0),
        "skip_count":             by_status.get("skip", 0),
        "rate_limited_count":     by_status.get("rate_limited", 0),
        "sufficient_for_pipeline": ok_count >= MIN_REAL_DATA_THRESHOLD,
        "min_threshold":          MIN_REAL_DATA_THRESHOLD,
        "ok_sources":             by_source_status["ok"],
        "no_data_sources":        by_source_status["no_data"],
        "error_sources":          by_source_status["error"],
        "started_at":             started,
        "completed_at":           completed,
    }


def _safe_run(fn, *args, **kwargs) -> FetcherResult:
    """Run a fetcher catching any exception so one failure can't kill the
    discovery pass."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        from .base import FetcherStatus
        return FetcherResult(
            source_key=getattr(fn.__module__.split(".")[-1], "SOURCE_KEY", "unknown"),
            status=FetcherStatus.ERROR,
            error=f"orchestrator_exception: {type(exc).__name__}: {exc}",
            fetched_at=_dt.datetime.utcnow().isoformat() + "Z",
        )
