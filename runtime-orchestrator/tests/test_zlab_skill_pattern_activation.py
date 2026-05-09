from runtime_orchestrator.zlab_skill import load_registry_bundle


EXPECTED_FOUNDATIONAL_PATTERN_IDS = {
    "warehouse_mhe_charging_demand_peak",
    "warehouse_dock_infiltration_loss",
    "cold_chain_status_unknown",
    "value_boundary_leakage_owner_operator",
    "reactive_power_exposure",
    "hvac_schedule_drift",
    "high_bay_lighting_waste",
    "compressed_air_leak_plausibility",
    "process_load_vs_waste",
    "steam_trap_failure_plausibility",
    "boiler_degradation_plausibility",
    "chiller_degradation_plausibility",
    "maintenance_maturity_not_evidenced",
    "maintenance_hidden_value_driver",
    "demand_charge_exposure_unknown",
    "fair_comparison_invalid_area_metric",
    "digital_twin_prematurity",
    "sensor_prematurity",
    "tenant_operator_boundary_unresolved",
    "benchmark_denominator_error",
    "procurement_vs_maintenance_conflict",
    "procurement_vs_lifecycle_cost",
    "compliance_vs_control_mismatch",
}


def test_foundational_pattern_pack_is_present_and_bounded() -> None:
    bundle = load_registry_bundle()
    patterns_by_id = bundle["patterns_by_id"]

    assert EXPECTED_FOUNDATIONAL_PATTERN_IDS.issubset(patterns_by_id)

    for pattern_id in EXPECTED_FOUNDATIONAL_PATTERN_IDS:
        row = patterns_by_id[pattern_id]
        assert row["confidence_ceiling"] == "L2"
        assert row["minimum_evidence_to_activate"]
        assert row["minimum_evidence_to_confirm"]
        assert row["falsification_conditions"]
        assert row["allowed_claim_language"]
        assert row["prohibited_claim_language"]
