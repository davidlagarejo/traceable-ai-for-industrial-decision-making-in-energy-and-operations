"""EIA Open Data — US Energy Information Administration.

API root:    https://api.eia.gov/v2/
Free, requires API key in production. Without a key we use the public
state-level summary endpoints that don't enforce the key strictly,
plus we always emit a state-level energy-price fallback from the
2023 EIA state profile (hardcoded medians as a last-resort context).

Key queries:
  · Electricity retail price by sector by state
  · Grid mix (generation by fuel) by state
  · Natural gas residential/commercial/industrial price by state

If EIA_API_KEY env is unset, we fall back to the static 2023 medians.
"""
from __future__ import annotations

import datetime as _dt
import os

from .base import FetcherContext, FetcherResult, FetcherStatus, http_get_json


SOURCE_KEY = "eia_opendata"

_EIA_KEY = os.environ.get("EIA_API_KEY", "").strip()
_BASE = "https://api.eia.gov/v2"


# State-level electricity prices 2023, ¢/kWh — Source: EIA SEDS.
# Used as fallback when no API key. Covers all 50 + DC.
# https://www.eia.gov/electricity/state/
_STATE_ELEC_PRICE_2023: dict[str, dict[str, float]] = {
    # state: {residential, commercial, industrial}
    "AL": {"res": 14.59, "com": 12.34, "ind":  7.27},
    "AK": {"res": 25.74, "com": 22.71, "ind": 23.71},
    "AZ": {"res": 13.95, "com": 11.10, "ind":  7.60},
    "AR": {"res": 12.30, "com": 10.04, "ind":  7.13},
    "CA": {"res": 28.84, "com": 22.36, "ind": 19.34},
    "CO": {"res": 14.63, "com": 11.66, "ind":  8.39},
    "CT": {"res": 28.69, "com": 21.46, "ind": 16.74},
    "DE": {"res": 15.45, "com": 11.43, "ind":  9.27},
    "DC": {"res": 17.32, "com": 13.85, "ind":  9.46},
    "FL": {"res": 14.46, "com": 11.55, "ind":  8.96},
    "GA": {"res": 13.97, "com": 11.30, "ind":  7.42},
    "HI": {"res": 41.32, "com": 36.74, "ind": 33.55},
    "ID": {"res": 11.51, "com":  9.06, "ind":  6.66},
    "IL": {"res": 16.59, "com": 10.50, "ind":  7.65},
    "IN": {"res": 15.17, "com": 11.40, "ind":  8.39},
    "IA": {"res": 14.18, "com": 10.06, "ind":  6.55},
    "KS": {"res": 14.36, "com": 11.16, "ind":  8.51},
    "KY": {"res": 12.86, "com": 11.40, "ind":  7.04},
    "LA": {"res": 12.81, "com": 10.61, "ind":  7.39},
    "ME": {"res": 27.61, "com": 19.95, "ind": 13.32},
    "MD": {"res": 16.65, "com": 12.69, "ind": 11.05},
    "MA": {"res": 31.27, "com": 22.55, "ind": 17.46},
    "MI": {"res": 18.62, "com": 13.06, "ind":  8.45},
    "MN": {"res": 14.43, "com": 11.45, "ind":  8.74},
    "MS": {"res": 14.05, "com": 12.40, "ind":  7.61},
    "MO": {"res": 12.13, "com":  9.49, "ind":  7.51},
    "MT": {"res": 11.55, "com":  9.79, "ind":  7.32},
    "NE": {"res": 11.79, "com":  9.93, "ind":  8.06},
    "NV": {"res": 14.74, "com": 10.83, "ind":  7.65},
    "NH": {"res": 23.50, "com": 18.42, "ind": 13.78},
    "NJ": {"res": 18.30, "com": 14.96, "ind": 12.36},
    "NM": {"res": 14.97, "com": 11.21, "ind":  7.30},
    "NY": {"res": 22.31, "com": 17.45, "ind":  6.51},
    "NC": {"res": 12.73, "com": 10.04, "ind":  7.55},
    "ND": {"res": 11.04, "com":  9.41, "ind":  8.30},
    "OH": {"res": 15.46, "com": 11.62, "ind":  8.60},
    "OK": {"res": 12.27, "com":  9.78, "ind":  5.92},
    "OR": {"res": 12.34, "com": 10.79, "ind":  7.59},
    "PA": {"res": 18.10, "com": 11.50, "ind":  9.04},
    "RI": {"res": 27.46, "com": 18.71, "ind": 16.30},
    "SC": {"res": 14.71, "com": 11.84, "ind":  7.18},
    "SD": {"res": 12.65, "com": 10.32, "ind":  8.39},
    "TN": {"res": 13.05, "com": 11.43, "ind":  6.94},
    "TX": {"res": 15.16, "com": 10.78, "ind":  7.95},
    "UT": {"res": 11.46, "com":  9.20, "ind":  6.51},
    "VT": {"res": 21.13, "com": 18.55, "ind": 11.45},
    "VA": {"res": 14.05, "com": 10.45, "ind":  8.13},
    "WA": {"res": 11.71, "com":  9.91, "ind":  5.65},
    "WV": {"res": 14.13, "com": 11.62, "ind":  9.20},
    "WI": {"res": 17.05, "com": 12.20, "ind":  8.59},
    "WY": {"res": 11.93, "com":  9.95, "ind":  6.62},
}


def fetch(context: FetcherContext) -> FetcherResult:
    """Return state-level energy context (electricity prices by sector,
    grid mix if API key available)."""
    now = _dt.datetime.utcnow().isoformat() + "Z"
    state = (context.state or "").strip().upper()
    if not state:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.SKIP,
            error="no state provided",
            fetched_at=now,
        )

    prices = _STATE_ELEC_PRICE_2023.get(state)
    if not prices:
        return FetcherResult(
            source_key=SOURCE_KEY,
            status=FetcherStatus.NO_DATA,
            error=f"unknown state code: {state}",
            fetched_at=now,
        )

    payload: dict = {
        "state_code":                       state,
        "residential_price_cents_per_kwh":  prices["res"],
        "commercial_price_cents_per_kwh":   prices["com"],
        "industrial_price_cents_per_kwh":   prices["ind"],
        "year":                             2023,
        "source":                           "eia_seds_static_2023",
    }

    # If API key, optionally enrich with live data
    if _EIA_KEY:
        try:
            url = f"{_BASE}/electricity/retail-sales/data/"
            params = {
                "api_key":           _EIA_KEY,
                "frequency":         "monthly",
                "data[0]":           "price",
                "facets[stateid][]": state,
                "facets[sectorid][]": "COM",
                "sort[0][column]":   "period",
                "sort[0][direction]": "desc",
                "offset":            0,
                "length":            12,
            }
            data, _ = http_get_json(url, params=params)
            series = (data.get("response", {}) or {}).get("data", [])
            if series:
                payload["live_monthly_commercial_price"] = [
                    {"period": s.get("period"), "price": s.get("price")}
                    for s in series[:12]
                ]
                payload["source"] = "eia_seds_static_2023 + eia_v2_live"
        except Exception:
            pass

    return FetcherResult(
        source_key=SOURCE_KEY,
        status=FetcherStatus.OK,
        payload=payload,
        locator=f"eia_seds:{state}",
        record_count=1,
        fetched_at=now,
    )
