from pathlib import Path

from runtime_orchestrator.zlab_skill import (
    ALLOWED_KNOWLEDGE_TYPES,
    default_registry_root,
    load_registry_bundle,
)


def test_registry_root_exists():
    assert default_registry_root().exists()


def test_registry_seed_bundle_loads_and_cross_validates():
    bundle = load_registry_bundle()

    assert bundle["counts"]["patterns"] >= 20
    assert bundle["counts"]["combinations"] >= 2
    assert bundle["counts"]["source_basis"] >= 1
    assert bundle["counts"]["validators"] >= 10
    assert bundle["counts"]["memory_policies"] >= 5

    pattern_ids = set(bundle["patterns_by_id"])
    assert "warehouse_mhe_charging_demand_peak" in pattern_ids
    assert "value_boundary_leakage_owner_operator" in pattern_ids
    assert "fair_comparison_invalid_area_metric" in pattern_ids
    assert "warehouse_dock_infiltration_loss" in pattern_ids
    assert "reactive_power_exposure" in pattern_ids
    assert "digital_twin_prematurity" in pattern_ids
    assert "sensor_prematurity" in pattern_ids
    assert "cold_chain_status_unknown" in pattern_ids
    assert "high_bay_lighting_waste" in pattern_ids
    assert "compressed_air_leak_plausibility" in pattern_ids
    assert "maintenance_maturity_not_evidenced" in pattern_ids
    assert "maintenance_hidden_value_driver" in pattern_ids
    assert "demand_charge_exposure_unknown" in pattern_ids
    assert "compliance_vs_control_mismatch" in pattern_ids
    assert "hvac_schedule_drift" in pattern_ids
    assert "steam_trap_failure_plausibility" in pattern_ids
    assert "boiler_degradation_plausibility" in pattern_ids
    assert "chiller_degradation_plausibility" in pattern_ids
    assert "tenant_operator_boundary_unresolved" in pattern_ids
    assert "benchmark_denominator_error" in pattern_ids
    assert "procurement_vs_maintenance_conflict" in pattern_ids
    assert "process_load_vs_waste" in pattern_ids
    assert "procurement_vs_lifecycle_cost" in pattern_ids

    combo = bundle["combinations_by_id"]["warehouse_tariff_boundary_area_combo"]
    assert combo["adjudication_required"] is True
    assert set(combo["pattern_ids"]).issubset(pattern_ids)
    manufacturing_combo = bundle["combinations_by_id"]["manufacturing_support_utility_maintenance_combo"]
    assert manufacturing_combo["adjudication_required"] is True
    assert set(manufacturing_combo["pattern_ids"]).issubset(pattern_ids)

    validator_ids = set(bundle["validators_by_id"])
    assert "claim_governor_combination_minimum_evidence" in validator_ids
    assert "financial_output_forbidden_terms" in validator_ids
    assert "memory_scope_cross_company_guard" in validator_ids
    assert "report_output_template_contamination_guard" in validator_ids

    memory_policy_ids = set(bundle["memory_policies_by_id"])
    assert "pattern_memory_global_structured_prior" in memory_policy_ids
    assert "validation_memory_company_confined" in memory_policy_ids
    assert "company_memory_company_confined" in memory_policy_ids
    assert "source_memory_provider_family" in memory_policy_ids
    assert "contradiction_memory_company_confined" in memory_policy_ids


def test_seed_patterns_respect_prompt_l2_ceiling_and_allowed_knowledge_types():
    bundle = load_registry_bundle()

    for row in bundle["patterns"]:
        assert row["confidence_ceiling"] == "L2"
        assert set(row["knowledge_type"]).issubset(ALLOWED_KNOWLEDGE_TYPES)
        assert row["allowed_claim_language"]
        assert row["prohibited_claim_language"]


def test_prompt_section_20_structure_files_exist_as_registry_equivalence_indexes():
    skill_root = Path(default_registry_root()).parent
    expected = {
        "asset_archetypes.yaml",
        "process_logic.yaml",
        "loss_patterns.yaml",
        "financial_translation.yaml",
        "fair_comparison_rules.yaml",
        "maintenance_reality.yaml",
        "measurement_minimality.yaml",
        "regulatory_physical_signals.yaml",
        "culture_execution_proxies.yaml",
        "gold_nugget_templates.yaml",
        "pattern_combinations.yaml",
        "tad_action_rules.yaml",
        "validators.yaml",
    }
    found = {path.name for path in skill_root.glob("*.yaml")}
    assert expected.issubset(found)
    for filename in sorted(expected):
        assert "registry_equivalence" in (skill_root / filename).read_text(encoding="utf-8")
