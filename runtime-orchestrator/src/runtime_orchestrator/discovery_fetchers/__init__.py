"""US-wide discovery fetchers — real public data sources.

This package was created in response to "el framework no está haciendo
nada en discovery" — the existing motor_028 declares 138 sources but
~90% are jurisdiction-specific (NYC/SF/LA/Texas/CA). For other US
locations (e.g., Chicago, IL) the framework was falling back to
ineffective primary sources.

Each fetcher returns a standardized FetcherResult and works against
PUBLIC, FREE-TIER APIs that require no API keys for basic use:

  · census_geocoder      → lat/lon + geoid + tract + jurisdiction
  · noaa_climate         → climate normals 1991-2020, HDD/CDD per station
  · epa_envirofacts      → facility registry, permits, emissions (national)
  · eia_opendata         → electricity prices, grid mix, utility territory
  · osm_overpass         → nearby industrial/commercial facilities
  · comparable_finder    → peer facilities by NAICS + climate zone + size
  · playwright_scraper   → fallback for JS-heavy public portals

Doctrine:
  - Never store API keys in code. EIA/NOAA can run without keys for
    public-tier queries.
  - Return STATUS even when no data: status ∈ {ok, no_data, error, skip}
  - Fail loud: a fetcher that errors must surface the error, not silently
    return empty.
  - Each fetcher is a pure function (context dict in → FetcherResult out).
"""
from __future__ import annotations

from .base import FetcherContext, FetcherResult, FetcherStatus
from . import (
    census_geocoder,
    noaa_climate,
    epa_envirofacts,
    eia_opendata,
    osm_overpass,
    comparable_finder,
    playwright_scraper,
    orchestrator,
)
from .orchestrator import run_full_discovery, MIN_REAL_DATA_THRESHOLD

__all__ = [
    "FetcherContext",
    "FetcherResult",
    "FetcherStatus",
    "census_geocoder",
    "noaa_climate",
    "epa_envirofacts",
    "eia_opendata",
    "osm_overpass",
    "comparable_finder",
    "playwright_scraper",
    "orchestrator",
    "run_full_discovery",
    "MIN_REAL_DATA_THRESHOLD",
]
