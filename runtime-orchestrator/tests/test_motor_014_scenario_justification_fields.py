"""Tests for motor_014 scenario justification fields (V2-LIVE Item 1).

Per RECOVERY_2026-05-10 §11.B, every scenario in scenario_space must carry
trigger / source / process_clue / industrial_reason / asset_family_reason
so motor_062 can audit them. This test suite verifies all per-family
branches emit the 5 fields.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_014 import (
    _build_scenario_space,
    _justification_for,
    _scenario_letter,
    _SCENARIO_JUSTIFICATION,
)


_REQUIRED_FIELDS = (
    "trigger",
    "source",
    "process_clue",
    "industrial_reason",
    "asset_family_reason",
)


# ── Helper tests ─────────────────────────────────────────────────────────


def test_scenario_letter_extracts_leading_letter():
    assert _scenario_letter("A. Energy intensity...") == "A"
    assert _scenario_letter("D. Asset cannot yet be characterized") == "D"


def test_scenario_letter_returns_empty_for_unconventional_heading():
    assert _scenario_letter("Energy intensity") == ""
    assert _scenario_letter("") == ""


def test_justification_table_covers_4_letters_per_family():
    families_in_table = {family for (family, letter) in _SCENARIO_JUSTIFICATION.keys()}
    for family in families_in_table:
        letters = {letter for (f, letter) in _SCENARIO_JUSTIFICATION.keys() if f == family}
        assert letters == {"A", "B", "C", "D"}, f"family {family} missing letters: {letters}"


def test_every_justification_entry_has_all_5_fields():
    for key, fields in _SCENARIO_JUSTIFICATION.items():
        for field in _REQUIRED_FIELDS:
            assert field in fields, f"{key} missing {field}"
            assert fields[field].strip(), f"{key}.{field} is empty"


def test_justification_for_falls_back_to_default():
    out = _justification_for("nonexistent_family", "A. Anything", "test_asset")
    # Falls back to default family A
    assert out["trigger"]
    assert out["source"]


def test_justification_for_returns_safe_empty_when_letter_missing():
    out = _justification_for("logistics", "no letter heading", "test_asset")
    assert set(out.keys()) == set(_REQUIRED_FIELDS)
    # All empty when no letter resolved
    assert all(v == "" for v in out.values())


# ── End-to-end: every scenario in every family carries the 5 fields ──


@pytest.mark.parametrize(
    "asset_name,target_type",
    [
        ("Lakeshore Cold Storage", "warehouse_distribution"),  # logistics
        ("Wilsonart Plant", "manufacturing_facility"),         # manufacturing
        ("BXP Tower", "commercial_building"),                  # building
        ("DLR Datacenter", "datacenter"),                      # default
        ("CSX Yard", "infrastructure_node"),                   # infrastructure
    ],
)
def test_scenario_space_emits_5_fields_per_scenario(asset_name, target_type):
    rows = _build_scenario_space(
        asset_name=asset_name,
        missing_clusters=["geometry_size_cluster"],
        regulatory_flags=["nyc_ll97"],
        target_type=target_type,
        decision_front_register=[],
        minimum_evidence_unlock_map=[],
    )
    assert len(rows) == 4, f"expected 4 scenarios for {target_type}, got {len(rows)}"
    for row in rows:
        for field in _REQUIRED_FIELDS:
            assert field in row, f"{target_type} scenario missing {field}"
            assert row[field].strip(), f"{target_type} scenario {field} empty"


def test_logistics_scenario_a_cites_logistics_sources():
    rows = _build_scenario_space(
        asset_name="Acme DC",
        missing_clusters=[],
        regulatory_flags=[],
        target_type="warehouse_distribution",
        decision_front_register=[],
        minimum_evidence_unlock_map=[],
    )
    a = next(r for r in rows if r["scenario"].startswith("A."))
    # Should cite at least one logistics-flavored source
    assert any(tag in a["source"].lower() for tag in ("doe_eere_mhe", "werc", "ashrae_handbook_hvac_applications_ch24"))


def test_manufacturing_scenario_a_cites_doe_amo_or_iac():
    rows = _build_scenario_space(
        asset_name="Acme Plant",
        missing_clusters=[],
        regulatory_flags=[],
        target_type="manufacturing_facility",
        decision_front_register=[],
        minimum_evidence_unlock_map=[],
    )
    a = next(r for r in rows if r["scenario"].startswith("A."))
    assert any(tag in a["source"].lower() for tag in ("doe_amo", "doe_iac", "eia_mecs", "sme_handbook"))


def test_building_scenario_c_cites_ll97_or_berdo_or_title24():
    rows = _build_scenario_space(
        asset_name="Acme Tower",
        missing_clusters=[],
        regulatory_flags=["local_emissions_law"],
        target_type="commercial_building",
        decision_front_register=[],
        minimum_evidence_unlock_map=[],
    )
    c = next(r for r in rows if r["scenario"].startswith("C."))
    src = c["source"].lower()
    assert any(tag in src for tag in ("nyc_ll97", "boston_berdo", "ca_title24_part6", "crrem"))
