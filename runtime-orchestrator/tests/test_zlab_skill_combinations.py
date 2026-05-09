from runtime_orchestrator.zlab_skill import (
    build_admissible_combination_review_register,
    build_asset_context_vector,
    build_combination_search_gap_record,
    build_combination_activation_register,
    build_combination_review_register,
    build_latent_combination_cluster_register,
    build_latent_combination_candidate_register,
    load_registry_bundle,
)


def test_combination_engine_activates_seed_combo_when_all_required_patterns_are_present() -> None:
    bundle = load_registry_bundle()

    rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
        ],
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["combination_id"] == "warehouse_tariff_boundary_area_combo"
    assert row["activation_state"] == "candidate"
    assert row["adjudication_required"] is True
    assert "peer superiority" in " ".join(row["prohibited_claims"]).lower()


def test_combination_engine_skips_combo_when_required_pattern_is_missing() -> None:
    bundle = load_registry_bundle()

    rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
        ],
    )

    assert rows == []


def test_combination_engine_skips_combo_when_anti_trigger_signal_matches() -> None:
    bundle = load_registry_bundle()

    rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
        ],
        anti_trigger_signals=["fair peer set already normalized"],
    )

    assert rows == []


def test_combination_review_register_is_adjudication_ready() -> None:
    bundle = load_registry_bundle()
    activation_rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
        ],
    )

    review_rows = build_combination_review_register(
        combination_activation_register=activation_rows,
        default_decision="needs_review",
    )

    assert len(review_rows) == 1
    assert review_rows[0]["operator_decision"] == "needs_review"
    assert review_rows[0]["validator_state"] == "not_run"


def test_manufacturing_combo_activates_when_support_utility_stack_is_present() -> None:
    bundle = load_registry_bundle()

    rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "compressed_air_leak_plausibility",
            "maintenance_maturity_not_evidenced",
            "reactive_power_exposure",
        ],
    )

    combo_ids = {row["combination_id"] for row in rows}
    assert "manufacturing_support_utility_maintenance_combo" in combo_ids


def test_latent_combination_engine_builds_contextual_pool() -> None:
    bundle = load_registry_bundle()
    asset_context_vector = build_asset_context_vector(
        asset_family_research_profile={
            "asset_family": "logistics_warehouse",
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
            "service_intensity": "high throughput",
        }
    )
    active_pattern_rows = [
        {
            "pattern_id": "warehouse_mhe_charging_demand_peak",
            "pattern_name": "MHE charging demand exposure",
            "activation_state": "structurally_plausible",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "minimum_evidence_to_confirm": ["utility bills", "charging schedule"],
        },
        {
            "pattern_id": "value_boundary_leakage_owner_operator",
            "pattern_name": "Control boundary leakage",
            "activation_state": "structurally_plausible",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "minimum_evidence_to_confirm": ["lease matrix"],
        },
        {
            "pattern_id": "fair_comparison_invalid_area_metric",
            "pattern_name": "Area-only comparison invalidity",
            "activation_state": "structurally_plausible",
            "evidence_state": "critical",
            "minimum_evidence_to_confirm": ["service level", "dock density"],
        },
        {
            "pattern_id": "demand_charge_exposure_unknown",
            "pattern_name": "Demand charge exposure unknown",
            "activation_state": "structurally_plausible",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "minimum_evidence_to_confirm": ["tariff schedule"],
        },
    ]

    rows = build_latent_combination_candidate_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
            "demand_charge_exposure_unknown",
        ],
        active_pattern_rows=active_pattern_rows,
        asset_context_vector=asset_context_vector,
    )

    assert rows
    first = rows[0]
    assert first["candidate_origin"] == "latent_synthesis"
    assert first["asset_context_vector"]["solar_profile"] == "morning_solar_peak"
    assert first["context_differentiators"]
    assert first["why_this_asset_is_not_generic"]
    assert first["asset_context_specificity"] >= 4
    assert first["score_breakdown"]["context_alignment_score"] >= 5
    assert first["score_breakdown"]["source_basis_score"] >= 1
    assert first["score_breakdown"]["evidence_support_score"] >= 2
    assert first["minimum_evidence"]


def test_latent_combination_engine_diverges_for_morning_vs_afternoon_context() -> None:
    bundle = load_registry_bundle()
    morning = build_asset_context_vector(
        asset_family_research_profile={
            "asset_family": "commercial_building",
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
        }
    )
    afternoon = build_asset_context_vector(
        asset_family_research_profile={
            "asset_family": "commercial_building",
            "solar_profile": "afternoon",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
        }
    )

    active_pattern_ids = [
        "hvac_schedule_drift",
        "demand_charge_exposure_unknown",
        "digital_twin_prematurity",
    ]
    morning_rows = build_latent_combination_candidate_register(
        registry_bundle=bundle,
        active_pattern_ids=active_pattern_ids,
        asset_context_vector=morning,
    )
    afternoon_rows = build_latent_combination_candidate_register(
        registry_bundle=bundle,
        active_pattern_ids=active_pattern_ids,
        asset_context_vector=afternoon,
    )

    assert morning_rows and afternoon_rows
    assert morning_rows[0]["combination_id"] != afternoon_rows[0]["combination_id"]
    assert "morning" in " ".join(morning_rows[0]["context_differentiators"]).lower()
    assert "afternoon" in " ".join(afternoon_rows[0]["context_differentiators"]).lower()


def test_latent_combination_engine_can_expand_pattern_pool_from_knowledge_atoms() -> None:
    bundle = load_registry_bundle()
    asset_context_vector = build_asset_context_vector(
        asset_family_research_profile={
            "asset_family": "logistics_warehouse",
            "solar_profile": "morning",
            "utility_tariff_context": "demand charge tariff",
        }
    )
    knowledge_atom_register = [
        {
            "atom_id": "atom::paper::demand_charge",
            "knowledge_type": "FINANCIAL_TRANSLATION",
            "statement": "Demand timing may dominate cost even when annual kWh is not extreme.",
            "document_ref": "10.1000/demand-charge",
            "provider_key": "ieee",
            "source_basis_id": "licensed_research_public_technical_priors",
            "supported_pattern_ids": ["demand_charge_exposure_unknown"],
            "supported_combination_ids": [],
        }
    ]

    rows = build_latent_combination_candidate_register(
        registry_bundle=bundle,
        active_pattern_ids=["warehouse_mhe_charging_demand_peak"],
        asset_context_vector=asset_context_vector,
        knowledge_atom_register=knowledge_atom_register,
    )

    assert rows
    candidate = next(
        row
        for row in rows
        if set(row["pattern_ids"]) == {"warehouse_mhe_charging_demand_peak", "demand_charge_exposure_unknown"}
    )
    assert candidate["knowledge_atom_count"] == 1
    assert "atom::paper::demand_charge" in candidate["supporting_atom_ids"]
    assert candidate["score_breakdown"]["knowledge_atom_support_score"] >= 2


def test_combination_search_gap_record_marks_under_investigation_when_pool_and_coverage_are_shallow() -> None:
    gap = build_combination_search_gap_record(
        latent_combination_candidate_register=[{"combination_id": "latent::1"} for _ in range(4)],
        admissible_combination_review_register=[{"combination_id": "latent::1"}],
        source_coverage_summary={
            "coverage_strength": "thin",
            "document_count": 1,
            "provider_count": 1,
            "knowledge_atom_count": 2,
            "visible_reference_count": 0,
            "supported_pattern_count": 2,
        },
        asset_context_vector={"asset_family": "commercial_building"},
        active_pattern_ids=["hvac_schedule_drift"],
    )

    assert gap["search_status"] == "incomplete_under_investigated"
    assert gap["severity"] == "high"
    assert "latent_pool_below_minimum" in gap["gap_flags"]
    assert "coverage_proof_not_strong" in gap["gap_flags"]


def test_combination_search_gap_record_allows_review_when_coverage_is_strong() -> None:
    gap = build_combination_search_gap_record(
        latent_combination_candidate_register=[{"combination_id": f"latent::{idx}"} for idx in range(18)],
        admissible_combination_review_register=[{"combination_id": f"latent::{idx}"} for idx in range(6)],
        source_coverage_summary={
            "coverage_strength": "strong",
            "document_count": 4,
            "provider_count": 2,
            "knowledge_atom_count": 10,
            "visible_reference_count": 3,
            "supported_pattern_count": 5,
        },
        asset_context_vector={"asset_family": "industrial_manufacturing"},
        active_pattern_ids=[
            "compressed_air_leak_plausibility",
            "reactive_power_exposure",
            "maintenance_maturity_not_evidenced",
        ],
    )

    assert gap["coverage_proof_strong"] is True
    assert gap["search_status"] == "thin_but_reviewable"
    assert gap["severity"] == "medium"
    assert "coverage_proof_not_strong" not in gap["gap_flags"]


def test_admissible_combination_review_register_filters_latent_pool() -> None:
    bundle = load_registry_bundle()
    asset_context_vector = build_asset_context_vector(
        asset_family_research_profile={
            "asset_family": "industrial_manufacturing",
            "operating_rhythm": "continuous",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "single owner operator",
        }
    )
    latent_rows = build_latent_combination_candidate_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "compressed_air_leak_plausibility",
            "maintenance_maturity_not_evidenced",
            "reactive_power_exposure",
        ],
        asset_context_vector=asset_context_vector,
    )

    review_rows = build_admissible_combination_review_register(
        latent_combination_candidate_register=latent_rows,
        default_decision="needs_review",
    )

    assert review_rows
    assert all(row["operator_decision"] == "needs_review" for row in review_rows)
    assert all(row["candidate_origin"] == "latent_synthesis" for row in review_rows)


def test_latent_combination_cluster_register_groups_candidates() -> None:
    bundle = load_registry_bundle()
    asset_context_vector = build_asset_context_vector(
        asset_family_research_profile={
            "asset_family": "logistics_warehouse",
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
        }
    )
    latent_rows = build_latent_combination_candidate_register(
        registry_bundle=bundle,
        active_pattern_ids=[
            "warehouse_mhe_charging_demand_peak",
            "value_boundary_leakage_owner_operator",
            "fair_comparison_invalid_area_metric",
            "demand_charge_exposure_unknown",
        ],
        asset_context_vector=asset_context_vector,
    )

    clusters = build_latent_combination_cluster_register(
        latent_combination_candidate_register=latent_rows,
    )

    assert clusters
    assert clusters[0]["candidate_count"] >= 1
    assert clusters[0]["context_signature"] == asset_context_vector["context_signature"]
