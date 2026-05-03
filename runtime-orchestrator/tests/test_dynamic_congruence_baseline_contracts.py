from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _dynamic_congruence_baselines import (
    build_baseline_register_bundle,
    load_baseline_fixture,
    load_contract_snapshot,
)


def _assert_row_contract(register_name: str, rows: list[dict[str, object]], expected_keys: list[str]) -> None:
    assert rows, f"{register_name} should not be empty in the baseline fixture"
    actual_keys = sorted(rows[0].keys())
    assert actual_keys == expected_keys
    for row in rows:
        assert sorted(row.keys()) == expected_keys


def test_dynamic_congruence_baseline_fixtures_encode_expected_asset_families() -> None:
    warehouse = load_baseline_fixture("dynamic_congruence_baseline_warehouse.json")
    manufacturing = load_baseline_fixture("dynamic_congruence_baseline_manufacturing.json")

    assert warehouse["asset_family_research_profile"]["asset_family"] == "logistics_warehouse"
    assert warehouse["target_definition"]["target_type"] == "warehouse_distribution"
    assert manufacturing["asset_family_research_profile"]["asset_family"] == "industrial_manufacturing"
    assert manufacturing["target_definition"]["target_type"] == "manufacturing_facility"


def test_warehouse_dynamic_congruence_baseline_bundle_stays_populated() -> None:
    fixture = load_baseline_fixture("dynamic_congruence_baseline_warehouse.json")
    bundle = build_baseline_register_bundle(fixture)

    discovery_need_ids = {row["need_id"] for row in bundle["discovery_need_register"]}
    question_ids = {row["question_id"] for row in bundle["dynamic_intake_question_register"]}
    peer_requirement_keys = {row["requirement_key"] for row in bundle["peer_requirement_register"]}

    assert "warehouse_subtype_classification" in discovery_need_ids
    assert "dock_and_service_intensity" in discovery_need_ids
    assert "operator_boundary_and_control" in discovery_need_ids
    assert "utility_territory_and_tariff_context" in discovery_need_ids
    assert "warehouse_subtype_and_cold_chain_status" in question_ids
    assert "warehouse_dock_cycles_and_operating_hours" in question_ids
    assert "warehouse_mhe_charging_profile" in question_ids
    assert "warehouse_control_boundary" in question_ids
    assert "asset_subtype_or_temperature_regime" in peer_requirement_keys
    assert "dock_density_and_service_intensity" in peer_requirement_keys
    assert "control_boundary_and_tariff" in peer_requirement_keys


def test_manufacturing_dynamic_congruence_baseline_bundle_stays_populated() -> None:
    fixture = load_baseline_fixture("dynamic_congruence_baseline_manufacturing.json")
    bundle = build_baseline_register_bundle(fixture)

    discovery_need_ids = {row["need_id"] for row in bundle["discovery_need_register"]}
    question_ids = {row["question_id"] for row in bundle["dynamic_intake_question_register"]}
    peer_requirement_keys = {row["requirement_key"] for row in bundle["peer_requirement_register"]}

    assert "process_and_permit_profile" in discovery_need_ids
    assert "thermal_system_and_utility_mix" in discovery_need_ids
    assert "throughput_proxy_and_schedule" in discovery_need_ids
    assert "manufacturing_process_and_thermal_lane" in question_ids
    assert "manufacturing_compressed_air_use" in question_ids
    assert "manufacturing_throughput_and_product_mix" in question_ids
    assert "process_type_and_thermal_lane" in peer_requirement_keys
    assert "throughput_product_mix_and_schedule" in peer_requirement_keys
    assert "support_system_stack" in peer_requirement_keys


def test_dynamic_congruence_register_contract_snapshot_matches_warehouse_baseline() -> None:
    snapshot = load_contract_snapshot()
    fixture = load_baseline_fixture("dynamic_congruence_baseline_warehouse.json")
    bundle = build_baseline_register_bundle(fixture)

    for register_name, expected_keys in snapshot.items():
        _assert_row_contract(register_name, bundle[register_name], expected_keys)


def test_dynamic_congruence_register_contract_snapshot_matches_manufacturing_baseline() -> None:
    snapshot = load_contract_snapshot()
    fixture = load_baseline_fixture("dynamic_congruence_baseline_manufacturing.json")
    bundle = build_baseline_register_bundle(fixture)

    for register_name, expected_keys in snapshot.items():
        _assert_row_contract(register_name, bundle[register_name], expected_keys)
