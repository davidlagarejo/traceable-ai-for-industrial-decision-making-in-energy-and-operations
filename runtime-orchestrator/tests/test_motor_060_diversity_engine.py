"""Tests for motor_060 — Report Diversity Engine."""
from __future__ import annotations

import pytest

from runtime_orchestrator import pattern_library
from runtime_orchestrator.adapters.motor_060 import Motor060Adapter


@pytest.fixture(autouse=True)
def _reset_patterns():
    pattern_library.reset_cache()
    yield
    pattern_library.reset_cache()


def _run(target_type=""):
    adapter = Motor060Adapter()
    return adapter.run(
        {"motor_007": {"target_definition_contract": {"target_type": target_type}}}
    )


def test_warehouse_plan_includes_known_axes():
    out = _run("warehouse_distribution")
    plan = out["diversity_axis_plan"]
    assert plan["asset_family"] == "warehouse_distribution"
    assert plan["status"] == "ok"
    assert "logistics_throughput" in plan["required_themes"]
    assert "tariff_orchestration" in plan["required_themes"]
    assert "thermal_exchange" in plan["required_themes"]


def test_warehouse_dominant_axis_is_first_axis():
    out = _run("warehouse_distribution")
    plan = out["diversity_axis_plan"]
    assert plan["dominant_axis"] == plan["required_themes"][0]


def test_unknown_family_returns_empty_plan():
    out = _run("not_a_real_family")
    plan = out["diversity_axis_plan"]
    assert plan["status"] == "no_pattern_library_for_family"
    assert plan["required_themes"] == []
    assert plan["library_version"] is None


def test_no_target_type_yields_empty_plan():
    out = _run("")
    plan = out["diversity_axis_plan"]
    assert plan["status"] == "no_pattern_library_for_family"


def test_flat_concept_markers_aggregated():
    out = _run("manufacturing_facility")
    assert out["concept_marker_count"] > 0
    assert "compressed air" in out["flat_concept_markers"] or "compressed_air" in out["flat_concept_markers"]


def test_axis_concept_markers_and_falsifiers_carried_per_axis():
    out = _run("commercial_building")
    plan = out["diversity_axis_plan"]
    # Pick a known axis and verify both halves are present
    axes = plan["axis_concept_markers"]
    assert "tenant_boundary" in axes
    assert "tenant" in axes["tenant_boundary"] or "owner control" in axes["tenant_boundary"]
    falsifiers = plan["axis_falsifiers"]["tenant_boundary"]
    assert any("lease" in f for f in falsifiers)


def test_axis_count_matches_required_themes():
    out = _run("datacenter")
    assert out["axis_count"] == len(out["diversity_axis_plan"]["required_themes"])


def test_minimum_unique_evidence_packs_at_least_three():
    out = _run("warehouse_distribution")
    plan = out["diversity_axis_plan"]
    assert plan["minimum_unique_evidence_packs"] >= 3


def test_library_version_propagates_to_top_level():
    out = _run("warehouse_distribution")
    plan = out["diversity_axis_plan"]
    assert out["library_version"] == plan["library_version"]
    assert plan["library_version"]  # non-empty SemVer string
