"""Tests for the US-wide discovery_fetchers package.

These are UNIT tests (no network) — they mock or call helper functions.
The end-to-end live test is in test_discovery_live.py (skipped in CI).
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.discovery_fetchers import (
    FetcherContext,
    FetcherResult,
    FetcherStatus,
    comparable_finder,
    eia_opendata,
    noaa_climate,
    playwright_scraper,
)


# ── FetcherContext / Result dataclasses ─────────────────────────────


def test_context_as_dict_round_trip():
    ctx = FetcherContext(
        address="123 Main St", city="Springfield", state="IL",
        zip_code="62701", lat=39.78, lon=-89.65,
        naics="493120", asset_family="warehouse_distribution",
    )
    d = ctx.as_dict()
    assert d["state"] == "IL"
    assert d["lat"] == 39.78
    assert d["asset_family"] == "warehouse_distribution"


def test_result_status_serializes_to_string():
    r = FetcherResult(source_key="x", status=FetcherStatus.OK,
                      payload={"a": 1})
    d = r.as_dict()
    assert d["status"] == "ok"


# ── NOAA Climate fallback ──────────────────────────────────────────


def test_noaa_state_heuristic_returns_climate_zone():
    ctx = FetcherContext(state="IL")
    r = noaa_climate.fetch(ctx)
    assert r.status == FetcherStatus.OK
    assert r.payload["ashrae_climate_zone_heuristic"] == "5A"


def test_noaa_unknown_state_returns_no_data():
    ctx = FetcherContext(state="ZZ")
    r = noaa_climate.fetch(ctx)
    assert r.status == FetcherStatus.NO_DATA


def test_noaa_no_state_returns_no_data():
    ctx = FetcherContext()
    r = noaa_climate.fetch(ctx)
    assert r.status == FetcherStatus.NO_DATA


# ── EIA OpenData fallback (static 2023 SEDS) ───────────────────────


def test_eia_returns_state_prices_without_api_key(monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    ctx = FetcherContext(state="CA")
    r = eia_opendata.fetch(ctx)
    assert r.status == FetcherStatus.OK
    assert r.payload["state_code"] == "CA"
    assert r.payload["commercial_price_cents_per_kwh"] > 20  # CA is expensive
    assert r.payload["industrial_price_cents_per_kwh"] > 15


def test_eia_unknown_state_returns_no_data():
    ctx = FetcherContext(state="XX")
    r = eia_opendata.fetch(ctx)
    assert r.status == FetcherStatus.NO_DATA


def test_eia_no_state_returns_skip():
    r = eia_opendata.fetch(FetcherContext())
    assert r.status == FetcherStatus.SKIP


# ── Comparable Finder (no network — pure data shaping) ─────────────


def test_comparable_finder_scores_epa_neighbors_by_keyword():
    ctx = FetcherContext(state="IL", asset_family="cold_chain_facility")
    epa_neighbors = [
        {"name": "Lakeshore REFRIGERATED Storage", "site_type": "warehouse"},
        {"name": "Joe's Bakery", "site_type": "retail"},
        {"name": "Cold Storage Distribution Inc", "site_type": "warehouse"},
    ]
    r = comparable_finder.fetch(ctx, epa_neighbors=epa_neighbors, osm_neighbors=[])
    assert r.status == FetcherStatus.OK
    cands = r.payload["peer_candidates"]
    # The refrigerated and cold-storage facilities should be top
    assert len(cands) == 2
    assert all("refrigerat" in str(c.get("matched_keywords", [])).lower()
               or "cold storage" in str(c.get("matched_keywords", [])).lower()
               for c in cands)


def test_comparable_finder_scores_osm_industrial_for_manufacturing():
    ctx = FetcherContext(state="OH", asset_family="manufacturing_facility")
    osm_neighbors = [
        {"name": "ACME Manufacturing", "building": "industrial"},
        {"name": "Bookstore", "building": "retail"},
    ]
    r = comparable_finder.fetch(ctx, epa_neighbors=[], osm_neighbors=osm_neighbors)
    assert r.status == FetcherStatus.OK
    cands = r.payload["peer_candidates"]
    assert len(cands) == 1
    assert "industrial" in str(cands[0]["matched_keywords"]).lower()


def test_comparable_finder_returns_no_data_when_no_matches():
    ctx = FetcherContext(state="WA", asset_family="cold_chain_facility")
    r = comparable_finder.fetch(ctx, epa_neighbors=[{"name": "office building"}], osm_neighbors=[])
    assert r.status == FetcherStatus.NO_DATA


# ── Playwright scraper graceful fallback ───────────────────────────


def test_playwright_skip_when_not_installed():
    # Whether playwright is installed or not, the function should
    # NEVER crash for an empty URL or missing import.
    r = playwright_scraper.fetch_page(url="")
    assert r.status == FetcherStatus.SKIP


# ── Orchestrator structure (no network) ────────────────────────────


def test_orchestrator_returns_bundle_shape(monkeypatch):
    """Smoke test: ensure orchestrator returns expected keys even if all
    fetchers fail."""
    # Mock every fetcher to return ERROR — bundle structure must still
    # be intact, sufficient_for_pipeline must be False.
    from runtime_orchestrator.discovery_fetchers import orchestrator as orch

    err = FetcherResult(source_key="mock", status=FetcherStatus.ERROR, error="mock")

    monkeypatch.setattr(
        orch.census_geocoder, "fetch", lambda ctx: err,
    )
    monkeypatch.setattr(orch.noaa_climate, "fetch", lambda ctx: err)
    monkeypatch.setattr(orch.epa_envirofacts, "fetch", lambda ctx: err)
    monkeypatch.setattr(orch.eia_opendata, "fetch", lambda ctx: err)
    monkeypatch.setattr(orch.osm_overpass, "fetch", lambda ctx: err)
    monkeypatch.setattr(orch.comparable_finder, "fetch",
                        lambda ctx, **kw: err)

    ctx = FetcherContext(address="x")
    bundle = orch.run_full_discovery(ctx)

    assert "results" in bundle
    assert bundle["ok_count"] == 0
    assert bundle["error_count"] == 6
    assert bundle["sufficient_for_pipeline"] is False
    assert bundle["min_threshold"] == 3
    assert "started_at" in bundle and "completed_at" in bundle


def test_orchestrator_sufficient_when_3_ok(monkeypatch):
    from runtime_orchestrator.discovery_fetchers import orchestrator as orch
    ok = FetcherResult(source_key="x", status=FetcherStatus.OK, payload={})
    err = FetcherResult(source_key="x", status=FetcherStatus.ERROR, error="e")
    monkeypatch.setattr(orch.census_geocoder, "fetch", lambda ctx: ok)
    monkeypatch.setattr(orch.noaa_climate, "fetch", lambda ctx: ok)
    monkeypatch.setattr(orch.epa_envirofacts, "fetch", lambda ctx: ok)
    monkeypatch.setattr(orch.eia_opendata, "fetch", lambda ctx: err)
    monkeypatch.setattr(orch.osm_overpass, "fetch", lambda ctx: err)
    monkeypatch.setattr(orch.comparable_finder, "fetch",
                        lambda ctx, **kw: err)
    bundle = orch.run_full_discovery(FetcherContext(address="x"))
    assert bundle["ok_count"] == 3
    assert bundle["sufficient_for_pipeline"] is True
