from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from runtime_orchestrator.adapters.motor_001 import Motor001Adapter
from runtime_orchestrator.adapters.motor_008 import Motor008Adapter
from runtime_orchestrator.adapters.motor_028 import Motor028Adapter


def _infrastructure_pipeline() -> dict:
    path = Path("/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/infrastructure_positive_inputs.json")
    return json.loads(path.read_text())


def _utility_heavy_pipeline() -> dict:
    path = Path("/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/inputs/utility_heavy_positive_inputs.json")
    return json.loads(path.read_text())


def test_motor_028_accepts_structured_local_asset_anchor_for_bounded_infrastructure_seed(monkeypatch):
    pipeline = _infrastructure_pipeline()
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    m08 = Motor008Adapter().run({"__pipeline__": pipeline, "motor_001": m01})

    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_census_geocoder",
        lambda ctx: None,
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_ashrae_climate_zone",
        lambda ctx: None,
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_eia_state_energy_consumption",
        lambda ctx: None,
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._select_extended_registry",
        lambda ctx, target_definition, route, routing_plan=None: [],
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._get_crawler",
        lambda ctx: SimpleNamespace(get_cached_or_live=lambda key, fn, ctx: None),
    )

    out = Motor028Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}},
            "motor_008": m08,
            "motor_009": {},
            "motor_035": {},
        }
    )

    assert out["quality_gate_passed"] is True
    assert out["structured_local_source_register"]
    assert any(
        gap["gap_type"] == "asset_primary_anchor_missing"
        and "structured local diligence" in gap["detail"].lower()
        for gap in out["coverage_gaps"]
    )


def test_motor_028_accepts_structured_local_asset_anchor_for_bounded_utility_heavy_seed(monkeypatch):
    pipeline = _utility_heavy_pipeline()
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    m08 = Motor008Adapter().run({"__pipeline__": pipeline, "motor_001": m01})

    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_census_geocoder",
        lambda ctx: None,
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_ashrae_climate_zone",
        lambda ctx: None,
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._fetch_eia_state_energy_consumption",
        lambda ctx: None,
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._select_extended_registry",
        lambda ctx, target_definition, route, routing_plan=None: [],
    )
    monkeypatch.setattr(
        "runtime_orchestrator.adapters.motor_028._get_crawler",
        lambda ctx: SimpleNamespace(get_cached_or_live=lambda key, fn, ctx: None),
    )

    out = Motor028Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}},
            "motor_008": m08,
            "motor_009": {},
            "motor_035": {},
        }
    )

    assert out["quality_gate_passed"] is True
    assert out["structured_local_source_register"]
    assert any(
        gap["gap_type"] == "asset_primary_anchor_missing"
        and "structured local diligence" in gap["detail"].lower()
        for gap in out["coverage_gaps"]
    )
