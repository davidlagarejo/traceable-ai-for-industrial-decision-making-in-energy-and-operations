"""Tests for motor_035 industrial_authority_routing (Gap D).

Verifies that motor_035 attaches an asset-family-aware authority hierarchy
projection from the industrial source catalog (139 sources). Existing
public_data_routing behavior is unaffected.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_035 import (
    Motor035Adapter,
    _build_industrial_authority_routing,
)


def _projection(family: str) -> dict:
    return _build_industrial_authority_routing(family)


def test_cold_chain_routing_has_tier1_iiar_or_ashrae():
    p = _projection("cold_chain_facility")
    tier1_ids = {e["source_id"] for e in p["tier_1"]}
    assert any(sid.startswith("iiar_") or sid.startswith("ashrae_") or sid.startswith("epa_") for sid in tier1_ids)
    assert p["total_sources"] > 0


def test_manufacturing_routing_includes_iso_and_doe():
    p = _projection("manufacturing_facility")
    ids = {e["source_id"] for e in p["tier_1"] + p["tier_2"]}
    assert "iso_50001" in ids
    assert "doe_iac_database" in ids


def test_commercial_building_routing_includes_ashrae_90_1_and_ll97():
    p = _projection("commercial_building")
    tier1_ids = {e["source_id"] for e in p["tier_1"]}
    assert "ashrae_90_1" in tier1_ids
    assert "nyc_ll97" in tier1_ids


def test_datacenter_routing_includes_tc99_and_uptime():
    p = _projection("datacenter")
    ids = {e["source_id"] for e in p["tier_1"] + p["tier_2"]}
    assert "ashrae_tc99" in ids
    assert "uptime_tier_standards" in ids


def test_unknown_family_returns_empty():
    p = _projection("space_elevator")
    assert p["total_sources"] == 0
    assert p["tier_1"] == []


def test_empty_family_returns_empty_dict():
    p = _projection("")
    assert p == {}


def test_tier_caps_enforced():
    p = _projection("commercial_building")
    assert len(p["tier_1"]) <= 40
    assert len(p["tier_2"]) <= 25
    assert len(p["tier_3"]) <= 15


def test_adapter_attaches_industrial_authority_routing_field():
    adapter = Motor035Adapter()
    out = adapter.run({
        "motor_001": {},
        "motor_006": {},
        "motor_007": {
            "target_definition_contract": {
                "target_type": "cold_chain_facility",
                "asset_family": "cold_chain_facility",
            },
        },
    })
    assert "industrial_authority_routing" in out
    routing = out["industrial_authority_routing"]
    assert routing.get("asset_family") == "cold_chain_facility"
    assert routing.get("total_sources", 0) > 0
