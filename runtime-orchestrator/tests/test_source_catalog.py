"""Tests for the industrial source catalog loader (Gap C)."""
from __future__ import annotations

from runtime_orchestrator.source_catalog import (
    all_sources,
    is_known_source,
    load_catalog,
    routing_for_family,
    source_by_id,
    sources_for_family,
    sources_for_tag,
)


def test_catalog_loads_at_least_100_sources():
    sources = all_sources()
    assert len(sources) >= 100, f"expected 100+ sources, got {len(sources)}"


def test_catalog_has_tier_definitions():
    cat = load_catalog()
    assert "tier_definitions" in cat
    assert set(cat["tier_definitions"].keys()) == {"1", "2", "3"}


def test_every_source_has_required_fields():
    required = {"source_id", "name", "publisher", "type", "authority_tier", "asset_families", "topic_tags"}
    for entry in all_sources():
        missing = required - set(entry.keys())
        assert not missing, f"source {entry.get('source_id')!r} missing fields: {missing}"


def test_authority_tier_only_1_2_or_3():
    for entry in all_sources():
        assert entry["authority_tier"] in {1, 2, 3}, entry["source_id"]


def test_known_cold_chain_sources_present():
    cold = {e["source_id"] for e in sources_for_family("cold_chain_facility")}
    assert "iiar_bulletin_109" in cold
    assert "ashrae_handbook_refrigeration" in cold
    assert "epa_snap" in cold


def test_known_manufacturing_sources_present():
    mfg = {e["source_id"] for e in sources_for_family("manufacturing_facility")}
    assert "doe_iac_database" in mfg
    assert "doe_amo_best_practices" in mfg
    assert "iso_50001" in mfg


def test_known_commercial_building_sources_present():
    bldg = {e["source_id"] for e in sources_for_family("commercial_building")}
    assert "ashrae_90_1" in bldg
    assert "nyc_ll97" in bldg
    assert "energy_star_portfolio_manager" in bldg


def test_known_datacenter_sources_present():
    dc = {e["source_id"] for e in sources_for_family("datacenter")}
    assert "ashrae_tc99" in dc
    assert "uptime_tier_standards" in dc
    assert "ashrae_90_4" in dc


def test_sources_for_tag_refrigeration_duty():
    refr = sources_for_tag("refrigeration_duty")
    ids = {e["source_id"] for e in refr}
    assert "iiar_standard_2" in ids
    assert "ashrae_handbook_refrigeration" in ids


def test_routing_for_family_buckets_by_tier():
    routing = routing_for_family("cold_chain_facility")
    assert set(routing.keys()) == {1, 2, 3}
    assert len(routing[1]) > 0
    assert len(routing[2]) > 0


def test_source_by_id_returns_entry():
    entry = source_by_id("ashrae_90_1")
    assert entry is not None
    assert entry["publisher"] == "ASHRAE"


def test_source_by_id_returns_none_for_unknown():
    assert source_by_id("nonexistent_xxx") is None


def test_is_known_source_recognizes_catalog_entries():
    assert is_known_source("IIAR Bulletin 109") is True
    assert is_known_source("ashrae_90_1 retrieved 2024-03-10") is True


def test_is_known_source_rejects_unknown_text():
    assert is_known_source("My uncle Bob said it was fine") is False
    assert is_known_source("") is False


def test_sources_for_family_sorted_by_tier_first():
    refr = sources_for_family("cold_chain_facility")
    tiers = [e["authority_tier"] for e in refr]
    assert tiers == sorted(tiers), "expected results sorted by authority_tier"


def test_at_least_30_handbooks_present():
    handbooks = [e for e in all_sources() if e.get("type") == "handbook"]
    assert len(handbooks) >= 25, f"expected 25+ handbooks, got {len(handbooks)}"


def test_at_least_10_case_studies_present():
    case_studies = [e for e in all_sources() if e.get("type") == "case_study"]
    assert len(case_studies) >= 10, f"expected 10+ case studies, got {len(case_studies)}"
