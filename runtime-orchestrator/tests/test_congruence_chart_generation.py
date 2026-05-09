from __future__ import annotations

from runtime_orchestrator.adapters.motor_016 import _apply_chart_strategic_surface_gate
from runtime_orchestrator.adapters.motor_018 import Motor018Adapter


def _base_inputs(*, report_identity_state: str, report_mode: str) -> dict:
    return {
        "__pipeline__": {
            "case_title": "Congruence Chart Test",
            "facility_inputs": {
                "input_04_primary_use": {},
                "input_05_size": {},
            },
        },
        "motor_007": {
            "report_identity_state": report_identity_state,
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_name": "Test Asset",
                    "target_identifier": "test-asset",
                    "jurisdiction_scope": ["US-IL"],
                },
                "asset_identity_bundle": {},
                "system_typology_prior": {},
                "asset_energy_behavior_prior": {},
                "technical_prior_ceiling": "bounded_asset_context",
            }
        },
        "motor_014": {
            "inference_records": [],
            "decision_front_register": [],
            "minimum_evidence_unlock_map": [],
            "scenario_space": [],
            "asset_context_readiness_summary": {},
        },
        "motor_028": {
            "discovery_summary": {},
            "enriched_data": {
                "financials": {},
                "benchmark_routing_register": {},
                "asset_geocoder": {},
                "extended_sources": {},
            },
        },
        "motor_047": {
            "report_mode": report_mode,
            "executive_thesis": {
                "dominant_contradiction": "Area benchmark vs service-level complexity",
                "why_current_question_is_premature": "The comparison basis is still wrong until dock activity, charging windows, and control boundary are normalized.",
                "what_reality_feature_changes_the_decision": "dock activity profile + charging schedule + utility bills",
                "dominant_operational_misunderstanding": "Capital may be targeting the wrong variable before the denominator is normalized.",
                "hidden_system_boundary_error": "The hidden boundary error is assuming that the visible payer and the controllable load boundary are the same thing.",
                "invalid_comparison_risk": "Area-based peer comparison remains structurally invalid until service intensity and control boundary are normalized.",
                "dominant_loss_logic": "The dominant hidden loss may be charging-window demand structure rather than generic kWh waste.",
                "surprising_but_evidenced_takeaway": "The problem may not be energy inefficiency at all.",
                "thesis_ranked_conflict_register": [
                    {
                        "layers_involved": ["benchmarking", "operation", "control", "finance"],
                    }
                ],
            },
        },
        "motor_049": {
            "local_truth_confidence_register": [
                {
                    "claim_key": "warehouse_service_complexity",
                    "research_claim": "Service intensity drives comparison validity.",
                    "local_truth_confidence": "bounded_strong_local_truth",
                    "binding_state": "sufficiently_bound",
                },
                {
                    "claim_key": "tariff_boundary_logic",
                    "research_claim": "Tariff structure changes what should be measured first.",
                    "local_truth_confidence": "bounded_partial_local_truth",
                    "binding_state": "partially_bound",
                },
            ],
            "utility_charge_breakdown_register": [
                {
                    "charge_type": "demand_charge",
                    "charge_amount": "12000",
                    "demand_kw": "780",
                    "pf_or_reactive_signal": "",
                }
            ],
            "tariff_exposure_register": [
                {
                    "exposure_type": "demand_charge_exposure",
                }
            ],
            "next_best_search_register": [
                {
                    "need_id": "warehouse_subtype",
                    "next_search_target": "Confirm warehouse subtype",
                    "public_source_likelihood": "high",
                    "stop_condition": "asset subtype classified with evidence_state >= L2",
                },
                {
                    "need_id": "operator_boundary",
                    "next_search_target": "Bound operator / tenant boundary",
                    "public_source_likelihood": "medium",
                    "stop_condition": "owner and operator boundary discussed as observed or explicitly unbound",
                },
            ],
            "stop_condition_register": [
                {
                    "path_type": "public_search",
                    "path_id": "warehouse_subtype",
                    "stop_condition": "asset subtype classified with evidence_state >= L2",
                },
                {
                    "path_type": "public_search",
                    "path_id": "operator_boundary",
                    "stop_condition": "owner and operator boundary discussed as observed or explicitly unbound",
                },
            ],
            "gap_taxonomy_register": [
                {"gap_type": "missing_comparability"},
                {"gap_type": "missing_control_evidence"},
                {"gap_type": "missing_tariff_evidence"},
                {"gap_type": "missing_comparability"},
            ],
        },
        "motor_051": {
            "normalization_requirements_register": [
                {
                    "normalization_dimension": "service_level_or_movement_intensity_proxy",
                    "current_state": "partially_bound",
                },
                {
                    "normalization_dimension": "climate_and_operating_schedule",
                    "current_state": "public_context_seeded",
                },
            ],
            "invalid_comparison_risk_register": [
                {
                    "risk_name": "warehouse_area_only_comparison",
                    "risk_level": "critical",
                }
            ],
            "cross_layer_congruence_register": [
                {
                    "contradiction": "Area benchmark vs service-level complexity",
                    "layers": ["benchmarking", "operation", "logistics"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
                {
                    "contradiction": "Demand structure vs charging schedule",
                    "layers": ["finance", "tariff", "operation"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
            ],
            "peer_requirement_register": [
                {
                    "requirement_key": "dock_density_and_service_intensity",
                    "peer_requirement": "dock density, throughput proxy, and operating schedule",
                    "current_evidence": "not_yet_evidenced",
                    "comparison_status": "blocked",
                },
                {
                    "requirement_key": "control_boundary_and_tariff",
                    "peer_requirement": "tenant/operator boundary, metering boundary, and tariff context",
                    "current_evidence": "partially_bound",
                    "comparison_status": "conditional",
                },
            ],
            "comparison_blocker_register": [
                {
                    "blocker_code": "dock_density_and_service_intensity",
                }
            ],
        },
        "motor_052": {
            "measurement_strategy_register": [
                {
                    "hypothesis": "service_intensity_not_area_drives_cost",
                    "minimum_measurement": "utility bills + operating schedule + service-level proxy + dock activity profile",
                    "hardware_trigger": "Temporary data logging only if schedule and activity records cannot discriminate the question.",
                }
            ],
            "hardware_minimality_register": [
                {
                    "data_need": "service_intensity_not_area_drives_cost",
                    "cheapest_valid_source": "utility bills / tariff records",
                    "upgrade_path": "Add interval data or temporary analyzer only if bills show a material tariff or demand question.",
                }
            ],
        },
        "motor_053": {
            "finance_physics_dependency_register": [
                {
                    "financial_assumption": "area-normalized energy captures the economics",
                    "physical_dependency": "service level, movement intensity and charging profile must not dominate cost logic",
                    "risk_if_wrong": "Optimization can target area-based symptoms while the real cost driver is service complexity.",
                }
            ],
            "cost_driver_dependency_register": [
                {
                    "cost_driver": "service level and movement / storage integrity",
                    "physical_dependency": "dock activity profile and charging schedule",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
        },
    }


def test_motor_018_generates_congruence_charts_for_structural_sections():
    out = Motor018Adapter().run(
        _base_inputs(
            report_identity_state="Compliance / Investment Screening Brief",
            report_mode="Compliance / Investment Screening Brief",
        )
    )

    by_id = {row["asset_id"]: row for row in out["chart_assets"]}

    assert out["chart_assets"][0]["asset_id"] == "chart_congruence_binding_state"
    assert out["chart_strategic_value_summary"]["thesis_critical_count"] >= 5
    assert out["chart_strategic_value_summary"]["supportive_context_count"] >= 1
    assert by_id["chart_congruence_binding_state"]["section_hint"] == "cf_minimum_evidence"
    assert by_id["chart_fair_comparison_gate"]["section_hint"] == "cf_peer_comparison"
    assert (
        by_id["chart_cross_layer_congruence_map"]["section_hint"]
        == "cf_dominant_structural_contradiction"
    )
    assert by_id["chart_measurement_minimality_path"]["section_hint"] == "cf_minimum_evidence"
    assert by_id["chart_cost_driver_signal_profile"]["section_hint"] == "cf_financial_exposure"
    assert by_id["chart_gap_taxonomy_profile"]["section_hint"] == "c3_blocking_conflicts"
    assert by_id["chart_next_best_search_path"]["section_hint"] == "c7_validation_architecture"
    assert by_id["chart_peer_requirement_readiness"]["section_hint"] == "c10_competitive_peer"
    assert by_id["chart_gap_taxonomy_profile"]["chart_category"] == "gap_taxonomy"
    assert by_id["chart_gap_taxonomy_profile"]["chart_lane"] == "validation"
    assert by_id["chart_gap_taxonomy_profile"]["chart_intent"] == "evidence_gap_diagnosis"
    assert by_id["chart_fair_comparison_gate"]["strategic_value_tier"] == "thesis_critical"
    assert by_id["chart_context_routing_status"]["strategic_value_tier"] == "supportive_context"
    assert by_id["chart_fair_comparison_gate"]["strategic_value_score"] > by_id["chart_context_routing_status"]["strategic_value_score"]
    assert by_id["chart_next_best_search_path"]["chart_category"] == "next_best_search"
    assert by_id["chart_next_best_search_path"]["chart_lane"] == "validation"
    assert by_id["chart_next_best_search_path"]["chart_intent"] == "search_program"
    assert by_id["chart_peer_requirement_readiness"]["chart_category"] == "peer_requirement_readiness"
    assert by_id["chart_gap_taxonomy_profile"]["chart_category_catalog_version"] == "runtime_orchestrator.chart_taxonomy.v1"
    assert by_id["chart_gap_taxonomy_profile"]["chart_taxonomy_catalog_version"] == "runtime_orchestrator.chart_taxonomy.v1"
    assert by_id["chart_fair_comparison_gate"]["chart_curation_mode"] == "structural"
    assert by_id["chart_gap_taxonomy_profile"]["chart_curation_mode"] == "structural_support"
    assert by_id["chart_fair_comparison_gate"]["title"] == "Peer Comparison Trust Gate"
    assert by_id["chart_fair_comparison_gate"]["title_es"] == "Filtro de Confianza para Comparación con Pares"
    assert by_id["chart_fair_comparison_gate"]["binding_anchor_type"] == "contradiction"
    assert by_id["chart_fair_comparison_gate"]["contradiction_id"] == "dominant_contradiction"
    assert by_id["chart_cost_driver_signal_profile"]["binding_anchor_type"] == "hypothesis"
    assert by_id["chart_cost_driver_signal_profile"]["hypothesis_id"] in {
        "challenger_hypothesis",
        "alternative_variable_candidate",
        "bounded_structural_hypothesis",
    }
    assert by_id["chart_context_routing_status"]["binding_state"] in {"bound", "bound_fallback"}
    assert (
        by_id["chart_context_routing_status"]["contradiction_id"]
        or by_id["chart_context_routing_status"]["hypothesis_id"]
        or by_id["chart_context_routing_status"]["nugget_id"]
    )
    assert all(by_id[key]["image_b64"] for key in by_id if key.startswith("chart_"))
    assert all(by_id[key]["chart_context"]["case_fingerprint"] for key in by_id if key.startswith("chart_"))
    assert all(by_id[key]["chart_context"]["target_name"] == "Test Asset" for key in by_id if key.startswith("chart_"))
    assert all(by_id[key]["chart_case_match_state"] == "same_case" for key in by_id if key.startswith("chart_"))


def test_motor_018_generates_congruence_charts_for_exploratory_sections():
    out = Motor018Adapter().run(
        _base_inputs(
            report_identity_state="Exploratory Prior Brief",
            report_mode="Exploratory Prior Brief",
        )
    )

    by_id = {row["asset_id"]: row for row in out["chart_assets"]}

    assert by_id["chart_congruence_binding_state"]["section_hint"] == "cf_minimum_evidence"
    assert by_id["chart_fair_comparison_gate"]["section_hint"] == "cf_peer_comparison"
    assert (
        by_id["chart_cross_layer_congruence_map"]["section_hint"]
        == "cf_dominant_structural_contradiction"
    )
    assert by_id["chart_measurement_minimality_path"]["section_hint"] == "cf_minimum_evidence"
    assert by_id["chart_cost_driver_signal_profile"]["section_hint"] == "cf_financial_exposure"
    assert by_id["chart_next_best_search_path"]["chart_curation_mode"] == "exploratory_support"
    assert by_id["chart_fair_comparison_gate"]["chart_curation_mode"] == "exploratory"
    assert by_id["chart_fair_comparison_gate"]["title"] == "Benchmark Trust Gate"
    assert by_id["chart_fair_comparison_gate"]["description_es"].startswith("Normalizaciones")


def test_motor_018_uses_distinct_congruence_copy_by_mode():
    structural = Motor018Adapter().run(
        _base_inputs(
            report_identity_state="Compliance / Investment Screening Brief",
            report_mode="Compliance / Investment Screening Brief",
        )
    )
    exploratory = Motor018Adapter().run(
        _base_inputs(
            report_identity_state="Exploratory Prior Brief",
            report_mode="Exploratory Prior Brief",
        )
    )

    structural_by_id = {row["asset_id"]: row for row in structural["chart_assets"]}
    exploratory_by_id = {row["asset_id"]: row for row in exploratory["chart_assets"]}

    assert (
        structural_by_id["chart_cross_layer_congruence_map"]["title"]
        != exploratory_by_id["chart_cross_layer_congruence_map"]["title"]
    )
    assert "thesis" in structural_by_id["chart_cross_layer_congruence_map"]["description"]
    assert "screening" in exploratory_by_id["chart_cross_layer_congruence_map"]["description"]


def test_motor_018_uses_distinct_legacy_chart_copy_by_mode():
    blocked = Motor018Adapter().run(
        _base_inputs(
            report_identity_state="Decision-Blocked Asset Brief",
            report_mode="Exploratory Prior Brief",
        )
    )
    exploratory = Motor018Adapter().run(
        _base_inputs(
            report_identity_state="Exploratory Prior Brief",
            report_mode="Exploratory Prior Brief",
        )
    )

    blocked_by_id = {row["asset_id"]: row for row in blocked["chart_assets"]}
    exploratory_by_id = {row["asset_id"]: row for row in exploratory["chart_assets"]}

    assert blocked_by_id["chart_context_routing_status"]["chart_curation_mode"] == "blocked"
    assert exploratory_by_id["chart_context_routing_status"]["chart_curation_mode"] == "exploratory_support"
    assert (
        blocked_by_id["chart_context_routing_status"]["title"]
        != exploratory_by_id["chart_context_routing_status"]["title"]
    )
    assert blocked_by_id["chart_context_routing_status"]["title_es"] == "Filtro de Preparación de Enrutamiento"
    assert blocked_by_id["chart_gap_taxonomy_profile"]["chart_curation_mode"] == "blocked"
    assert blocked_by_id["chart_peer_requirement_readiness"]["title"] == "Peer Requirement Blockers"


def test_motor_018_uses_executive_thesis_as_chart_fallback_surface():
    inputs = _base_inputs(
        report_identity_state="Exploratory Prior Brief",
        report_mode="Exploratory Prior Brief",
    )
    inputs["motor_051"]["normalization_requirements_register"] = []
    inputs["motor_051"]["invalid_comparison_risk_register"] = []
    inputs["motor_051"]["cross_layer_congruence_register"] = []
    inputs["motor_053"]["finance_physics_dependency_register"] = []
    inputs["motor_053"]["cost_driver_dependency_register"] = []
    inputs["motor_049"]["utility_charge_breakdown_register"] = []
    inputs["motor_049"]["tariff_exposure_register"] = []

    out = Motor018Adapter().run(inputs)
    by_id = {row["asset_id"]: row for row in out["chart_assets"]}

    assert "chart_fair_comparison_gate" in by_id
    assert "chart_cross_layer_congruence_map" in by_id
    assert "chart_cost_driver_signal_profile" in by_id
    assert "motor_047.executive_thesis" in by_id["chart_fair_comparison_gate"]["data_dependencies"]
    assert "motor_047.executive_thesis" in by_id["chart_cross_layer_congruence_map"]["data_dependencies"]
    assert "motor_047.executive_thesis" in by_id["chart_cost_driver_signal_profile"]["data_dependencies"]


def test_chart_strategic_surface_gate_demotes_decorative_body_charts_to_appendix_when_strategic_density_is_high():
    filtered_map, policy_register, summary = _apply_chart_strategic_surface_gate(
        resolved_chart_asset_list_map={
            "cf_dominant_structural_contradiction": [
                {
                    "asset_id": "chart_cross_layer_congruence_map",
                    "strategic_value_tier": "thesis_critical",
                    "image_b64": "a",
                },
                {
                    "asset_id": "chart_context_routing_body",
                    "strategic_value_tier": "decorative_risk",
                    "image_b64": "b",
                },
            ],
            "cf_peer_comparison": [
                {
                    "asset_id": "chart_fair_comparison_gate",
                    "strategic_value_tier": "thesis_critical",
                    "image_b64": "c",
                }
            ],
            "cf_financial_exposure": [
                {
                    "asset_id": "chart_cost_driver_signal_profile",
                    "strategic_value_tier": "thesis_critical",
                    "image_b64": "d",
                },
                {
                    "asset_id": "chart_structural_support_context",
                    "strategic_value_tier": "strategic_support",
                    "image_b64": "e",
                },
            ],
            "a1_evidence_traceability": [
                {
                    "asset_id": "chart_context_routing_appendix",
                    "strategic_value_tier": "decorative_risk",
                    "image_b64": "f",
                }
            ],
        },
        body_section_ids={
            "cf_dominant_structural_contradiction",
            "cf_peer_comparison",
            "cf_financial_exposure",
        },
        appendix_section_ids=["a1_evidence_traceability"],
        appendix_demote_section_id="a1_evidence_traceability",
    )

    assert summary["body_gate_activated"] is True
    assert summary["decorative_risk_body_count_demoted"] == 1
    assert summary["decorative_risk_body_count_suppressed"] == 0
    assert summary["body_strategic_anchor_count"] == 4
    assert [
        row["asset_id"]
        for row in filtered_map["cf_dominant_structural_contradiction"]
    ] == ["chart_cross_layer_congruence_map"]
    assert [
        row["asset_id"]
        for row in filtered_map["a1_evidence_traceability"]
    ] == ["chart_context_routing_appendix", "chart_context_routing_body"]

    register_by_id = {row["asset_id"]: row for row in policy_register}
    assert (
        register_by_id["chart_context_routing_body"]["strategic_surface_policy_state"]
        == "demoted_decorative_risk_to_appendix"
    )
    assert register_by_id["chart_context_routing_body"]["demoted_to_section_id"] == "a1_evidence_traceability"
    assert (
        register_by_id["chart_context_routing_appendix"]["strategic_surface_policy_state"]
        == "appendix_or_non_body_exempt"
    )
