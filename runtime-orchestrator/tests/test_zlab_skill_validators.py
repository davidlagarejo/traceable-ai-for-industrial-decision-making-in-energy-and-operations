from runtime_orchestrator.zlab_skill import (
    apply_combination_validators,
    build_combination_activation_register,
    build_combination_review_register,
    load_registry_bundle,
)


def test_combination_validators_pass_seed_combo_when_contract_is_sound() -> None:
    bundle = load_registry_bundle()
    activation_rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
        ],
    )

    validated = apply_combination_validators(activation_rows, registry_bundle=bundle)

    assert len(validated) == 1
    assert validated[0]["validator_state"] == "passed"
    assert validated[0]["validator_findings"] == []


def test_combination_validators_block_forbidden_financial_language() -> None:
    bundle = load_registry_bundle()
    activation_rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
        ],
    )
    activation_rows[0]["allowed_language"] = "This combo supports ROI hardening."

    validated = apply_combination_validators(activation_rows, registry_bundle=bundle)
    review_rows = build_combination_review_register(
        combination_activation_register=validated,
    )

    assert validated[0]["validator_state"] == "blocked"
    assert any(finding["validator"] == "FinancialOutputValidator" for finding in validated[0]["validator_findings"])
    assert review_rows[0]["operator_decision"] == "blocked_by_validator"


def test_validator_engine_uses_registry_catalog() -> None:
    bundle = load_registry_bundle()
    activation_rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
        ],
    )
    activation_rows[0]["source_basis"] = []

    validated = apply_combination_validators(activation_rows, registry_bundle=bundle)

    assert any(finding["validator"] == "SourceTraceabilityValidator" for finding in validated[0]["validator_findings"])
