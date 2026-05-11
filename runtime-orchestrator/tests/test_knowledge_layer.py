"""Tests for the knowledge layer YAML loader (V2-LIVE Item 4).

Loads the 4 Gap-F YAMLs (machine_logic, compressed_air_logic,
control_boundary_logic, power_quality_logic) and verifies motor_050 +
motor_052 surface them through `knowledge_layer_registry`.
"""
from __future__ import annotations

from runtime_orchestrator.knowledge_layer import (
    industrial_sources_for_block,
    knowledge_layer_summary,
    load_knowledge_layer_registry,
    pattern_ids_for_block,
)


def test_loads_all_4_blocks():
    reg = load_knowledge_layer_registry()
    assert set(reg.keys()) == {
        "machine_logic",
        "compressed_air_logic",
        "control_boundary_logic",
        "power_quality_logic",
    }


def test_every_block_has_registry_equivalence_with_patterns_and_sources():
    reg = load_knowledge_layer_registry()
    for short_id, block in reg.items():
        eq = block.get("registry_equivalence", {})
        assert isinstance(eq, dict), f"{short_id} missing registry_equivalence"
        assert eq.get("pattern_ids"), f"{short_id} has no pattern_ids"
        assert eq.get("industrial_sources"), f"{short_id} has no industrial_sources"


def test_machine_logic_references_known_patterns():
    pids = pattern_ids_for_block("machine_logic")
    # Per the YAML, machine_logic references rotating + process equipment
    assert any(p in pids for p in ("compressor_staging", "refrigeration_duty", "chiller_degradation_plausibility"))


def test_machine_logic_references_known_catalog_sources():
    src = industrial_sources_for_block("machine_logic")
    assert any(s in src for s in ("sme_handbook", "epri_motors_drives", "nema_mg1"))


def test_compressed_air_logic_references_doe_or_cagi():
    src = industrial_sources_for_block("compressed_air_logic")
    assert any(s in src for s in ("cagi_compressed_air_handbook", "doe_compressed_air_challenge"))


def test_control_boundary_logic_references_isa_or_vendor():
    src = industrial_sources_for_block("control_boundary_logic")
    assert any(s in src for s in ("isa_handbook", "siemens_process_automation", "honeywell_building_controls"))


def test_power_quality_logic_references_ieee():
    src = industrial_sources_for_block("power_quality_logic")
    assert "ieee_519" in src


def test_summary_aggregates_4_blocks():
    s = knowledge_layer_summary()
    assert s["total_blocks"] == 4
    assert s["total_pattern_refs"] > 0
    assert s["total_source_refs"] > 0
    short_ids = [b["short_id"] for b in s["blocks"]]
    assert short_ids == [
        "machine_logic",
        "compressed_air_logic",
        "control_boundary_logic",
        "power_quality_logic",
    ]


def test_summary_preserves_scope_count_and_governing_principles_count():
    s = knowledge_layer_summary()
    for block in s["blocks"]:
        # All 4 YAMLs declare scope + governing_principles
        assert block["scope_count"] > 0, f"{block['short_id']} missing scope"
        assert block["governing_principles_count"] > 0, f"{block['short_id']} missing principles"


# ── Motor adapter integration ────────────────────────────────────────────


def test_motor_050_surfaces_knowledge_layer_registry():
    from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
    adapter = Motor050Adapter()
    out = adapter.run({"motor_007": {}, "motor_049": {}, "motor_060": {}})
    assert "knowledge_layer_registry" in out
    klr = out["knowledge_layer_registry"]
    assert klr["total_blocks"] == 4


def test_motor_052_surfaces_knowledge_layer_registry():
    from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
    adapter = Motor052Adapter()
    out = adapter.run({})
    assert "knowledge_layer_registry" in out
    klr = out["knowledge_layer_registry"]
    assert klr["total_blocks"] == 4
