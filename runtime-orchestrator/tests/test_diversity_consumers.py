"""Tests for R-55..R-57: motor_041, motor_038, motor_050 consume the
diversity_axis_plan emitted by motor_060.

Each consumer surfaces the plan as opt-in metadata; existing behaviour
must remain unchanged when motor_060 is absent (graceful degradation).
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_038 import Motor038Adapter
from runtime_orchestrator.adapters.motor_041 import Motor041Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter


def _diversity_input(asset_family="warehouse_distribution"):
    return {
        "diversity_axis_plan": {
            "asset_family": asset_family,
            "library_version": "1.0.0",
            "dominant_axis": "logistics_throughput",
            "required_themes": [
                "logistics_throughput",
                "tariff_orchestration",
                "thermal_exchange",
                "service_level_intensity",
            ],
            "minimum_unique_evidence_packs": 3,
            "forbidden_repetition_signature_count_max": 2,
            "status": "ok",
        }
    }


# ── R-55: motor_041 ────────────────────────────────────────────────────────


def test_motor_041_surfaces_diversity_axis_plan():
    adapter = Motor041Adapter()
    out = adapter.run({"motor_060": _diversity_input()})
    assert out["diversity_axis_plan"]["asset_family"] == "warehouse_distribution"
    assert "logistics_throughput" in out["diversity_required_themes"]


def test_motor_041_handles_missing_motor_060_gracefully():
    adapter = Motor041Adapter()
    out = adapter.run({})  # no motor_060 input
    assert out["diversity_axis_plan"] == {}
    assert out["diversity_required_themes"] == []


def test_motor_041_does_not_break_legacy_behaviour():
    adapter = Motor041Adapter()
    out = adapter.run({})
    # Legacy fields still present
    assert "problem_framing_register" in out
    assert "problem_framing_count" in out


# ── R-56: motor_038 ────────────────────────────────────────────────────────


def test_motor_038_surfaces_required_themes():
    adapter = Motor038Adapter()
    out = adapter.run({"motor_060": _diversity_input()})
    assert "logistics_throughput" in out["diversity_required_themes"]


def test_motor_038_no_motor_060_yields_empty_themes():
    adapter = Motor038Adapter()
    out = adapter.run({})
    assert out["diversity_required_themes"] == []


def test_motor_038_legacy_fields_intact():
    adapter = Motor038Adapter()
    out = adapter.run({})
    assert "dominant_variable_register" in out
    assert "admissible_variable_count" in out
    assert "observed_or_conditional_variable_count" in out


# ── R-57: motor_050 ────────────────────────────────────────────────────────


def test_motor_050_emits_prohibited_themes_for_warehouse():
    adapter = Motor050Adapter()
    out = adapter.run({"motor_060": _diversity_input("warehouse_distribution")})
    # Required themes from warehouse_distribution
    assert "logistics_throughput" in out["diversity_required_themes"]
    # Prohibited themes are everything OTHER than warehouse axes
    prohibited = out["diversity_prohibited_themes"]
    assert "process_heat" in prohibited  # manufacturing axis, not warehouse
    assert "tenant_boundary" in prohibited  # building axis, not warehouse
    assert "logistics_throughput" not in prohibited  # is required, not prohibited


def test_motor_050_no_motor_060_emits_empty_diversity_lists():
    adapter = Motor050Adapter()
    out = adapter.run({})
    assert out["diversity_required_themes"] == []
    assert out["diversity_prohibited_themes"] == []


def test_motor_050_legacy_fields_intact():
    adapter = Motor050Adapter()
    out = adapter.run({})
    assert "subsystem_count" in out
    assert "control_boundary_count" in out
