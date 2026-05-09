from __future__ import annotations

from runtime_orchestrator.adapters.motor_018 import Motor018Adapter
from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter
from runtime_orchestrator.adapters.motor_054 import Motor054Adapter
from runtime_orchestrator.congruence_intelligence.case_isolation import (
    build_case_namespace_register,
    build_chart_case_match_register,
    build_cross_case_contamination_scan,
)
from runtime_orchestrator.congruence_intelligence.declared_input_governor import (
    annotate_asset_field_register,
    build_declared_input_downgrade_register,
)
from runtime_orchestrator.congruence_intelligence.discovery_planner import (
    build_accepted_evidence_type_register,
    build_discovery_need_register,
    build_discovery_stop_condition_register,
    build_search_family_execution_plan,
)
from runtime_orchestrator.congruence_intelligence.dynamic_case_state import (
    build_discovery_case_state,
)
from runtime_orchestrator.congruence_intelligence.empty_section_policy import (
    apply_empty_section_policy,
    build_section_explanation_fallback_register,
)
from runtime_orchestrator.congruence_intelligence.entity_resolution import build_case_fingerprint
from runtime_orchestrator.congruence_intelligence.next_best_search import (
    build_next_best_search_register,
    build_search_failure_effect_register,
    build_search_success_effect_register,
    build_search_target_priority_register,
)


def _field(
    field: str,
    value,
    *,
    source_id: str | None = None,
    authority_score: str = "declared_input",
    admissibility: str = "DECLARED_INPUT_ONLY",
) -> dict:
    return {
        "field": field,
        "value": value,
        "status": "OBSERVED",
        "source_id": source_id or f"declared_input::{field}",
        "source_family": "",
        "source_title": "",
        "scope": "ASSET_LEVEL",
        "authority_score": authority_score,
        "recency": "current",
        "admissibility": admissibility,
        "notes": "",
    }


def _warehouse_target_definition() -> dict:
    return {
        "target_name": "Sunrise Logistics Hub",
        "target_identifier": "sunrise-logistics-hub-2026",
        "address_raw": "1450 Logistics Parkway, Dallas, TX 75201",
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": ["US-TX"],
        "decision_intent": "underwriting",
        "report_intent": "dynamic_congruence_acceptance",
    }


def _warehouse_m28_packet() -> dict:
    target_definition = _warehouse_target_definition()
    search_budget_register = [
        {
            "budget_scope": "total_public_discovery",
            "budget_state": "bounded",
            "budget_class": "bounded_public_discovery",
        }
    ]
    coverage_gaps = [
        {"gap_type": "asset_primary_anchor_missing", "severity": "critical"},
        {"gap_type": "asset_energy_behavior_reference", "severity": "high"},
        {"gap_type": "asset_context_readiness", "severity": "high"},
    ]
    requestable_evidence_items = [
        {
            "evidence_item": (
                "Verified warehouse subtype, dock count, refrigerated footprint, "
                "charging schedule, and operator boundary"
            ),
            "source": "Owner records, operator records, site plan, and lease summary",
            "why_needed": (
                "Sets the denominator, the valid peer family, tariff interpretation, "
                "and whether value leaks across the control boundary."
            ),
        }
    ]
    attempts: list[dict] = []
    routing_output = {
        "routing_ready": True,
        "report_type_allowed": "Compliance / Investment Screening Brief",
        "target_classification_result": {
            "technical_scraping_allowed": True,
        },
        "regulatory_stack": ["US-TX"],
    }
    case_fingerprint = build_case_fingerprint(target_definition=target_definition)
    discovery_case_state = build_discovery_case_state(
        target_definition=target_definition,
        routing_output=routing_output,
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=requestable_evidence_items,
        attempts=attempts,
        search_budget_register=search_budget_register,
        case_fingerprint=case_fingerprint,
        asset_context_readiness={"state": "asset_localized"},
        runtime_context={},
        routing_plan_compliance={},
    )
    discovery_need_register = build_discovery_need_register(
        target_definition=target_definition,
        coverage_gaps=coverage_gaps,
        requestable_evidence_items=requestable_evidence_items,
        attempts=attempts,
        search_budget_register=search_budget_register,
        dynamic_case_state=discovery_case_state,
    )
    search_family_execution_plan = build_search_family_execution_plan(
        discovery_need_register=discovery_need_register,
    )
    accepted_evidence_type_register = build_accepted_evidence_type_register(
        discovery_need_register=discovery_need_register,
    )
    discovery_stop_condition_register = build_discovery_stop_condition_register(
        discovery_need_register=discovery_need_register,
    )
    next_best_search_register = build_next_best_search_register(
        discovery_need_register=discovery_need_register,
        discovery_stop_condition_register=discovery_stop_condition_register,
        search_budget_register=search_budget_register,
        dynamic_case_state=discovery_case_state,
    )
    return {
        "source_register": [],
        "enriched_data": {
            "benchmark_routing_register": {},
            "asset_geocoder": {},
            "extended_sources": {},
        },
        "search_budget_register": search_budget_register,
        "search_attempt_ledger": attempts,
        "search_attempt_outcome_register": [],
        "search_exhaustion_register": [],
        "discovery_case_state": discovery_case_state,
        "discovery_need_register": discovery_need_register,
        "search_family_execution_plan": search_family_execution_plan,
        "accepted_evidence_type_register": accepted_evidence_type_register,
        "discovery_stop_condition_register": discovery_stop_condition_register,
        "next_best_search_register": next_best_search_register,
        "search_target_priority_register": build_search_target_priority_register(
            next_best_search_register=next_best_search_register,
        ),
        "search_success_effect_register": build_search_success_effect_register(
            next_best_search_register=next_best_search_register,
        ),
        "search_failure_effect_register": build_search_failure_effect_register(
            next_best_search_register=next_best_search_register,
        ),
    }


def _warehouse_inputs() -> dict:
    target_definition = _warehouse_target_definition()
    asset_field_register = annotate_asset_field_register(
        [
            _field("address", target_definition["address_raw"]),
            _field("asset_class", "warehouse_distribution"),
            _field(
                "GFA",
                "420000",
                source_id="county_assessor::sunrise-logistics-hub",
                authority_score="high",
                admissibility="CONFIRMED_ASSET_LEVEL",
            ),
        ]
    )
    return {
        "motor_007": {
            "target_definition_contract": target_definition,
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
            "report_identity_state": "Compliance / Investment Screening Brief",
        },
        "motor_012": {
            "facility_prior": {
                "target_definition": target_definition,
                "asset_identity_bundle": {},
                "system_typology_prior": {},
                "asset_energy_behavior_prior": {},
                "technical_prior_ceiling": "bounded_asset_context",
            },
            "asset_field_register": asset_field_register,
            "declared_input_downgrade_register": build_declared_input_downgrade_register(
                asset_field_register
            ),
        },
        "motor_014": {
            "inference_records": [],
            "decision_front_register": [],
            "minimum_evidence_unlock_map": [],
            "scenario_space": [],
            "asset_context_readiness_summary": {},
        },
        "motor_028": _warehouse_m28_packet(),
    }


def _run_warehouse_chain() -> dict:
    inputs = _warehouse_inputs()
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run(
        {**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52}
    )
    m54 = Motor054Adapter().run(
        {
            **inputs,
            "motor_049": m49,
            "motor_050": m50,
            "motor_051": m51,
            "motor_052": m52,
            "motor_053": m53,
        }
    )
    return {
        "inputs": inputs,
        "motor_049": m49,
        "motor_050": m50,
        "motor_051": m51,
        "motor_052": m52,
        "motor_053": m53,
        "motor_054": m54,
    }


def _run_warehouse_chart_bundle(bundle: dict) -> dict:
    inputs = bundle["inputs"]
    m18 = Motor018Adapter().run(
        {
            "__pipeline__": {
                "case_title": "Sunrise Logistics Hub",
                "facility_inputs": {
                    "input_04_primary_use": {},
                    "input_05_size": {},
                },
            },
            "motor_007": inputs["motor_007"],
            "motor_012": inputs["motor_012"],
            "motor_014": inputs["motor_014"],
            "motor_028": inputs["motor_028"],
            "motor_047": {
                "report_mode": "Compliance / Investment Screening Brief",
            },
            "motor_049": bundle["motor_049"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
        }
    )
    namespace = build_case_namespace_register(
        target_definition=_warehouse_target_definition(),
        case_id="warehouse-dynamic-congruence-acceptance",
        case_title="Sunrise Logistics Hub",
        document_visible_type="Compliance / Investment Screening Brief",
    )
    chart_case_match_register = build_chart_case_match_register(
        case_namespace_register=namespace,
        chart_assets=list(m18.get("chart_assets", []) or []),
    )
    return {
        "motor_018": m18,
        "chart_case_match_register": chart_case_match_register,
        "cross_case_contamination_scan": build_cross_case_contamination_scan(
            chart_case_match_register=chart_case_match_register,
        ),
    }


def test_warehouse_dynamic_congruence_acceptance_bundle_covers_prompt_behaviors():
    bundle = _run_warehouse_chain()
    m49 = bundle["motor_049"]
    m51 = bundle["motor_051"]
    m52 = bundle["motor_052"]
    m53 = bundle["motor_053"]
    m54 = bundle["motor_054"]

    question_ids = {row["question_id"] for row in m49["dynamic_intake_question_register"]}
    assert m49["dynamic_intake_question_count"] >= 4
    assert {
        "warehouse_subtype_and_cold_chain_status",
        "warehouse_dock_cycles_and_operating_hours",
        "warehouse_mhe_charging_profile",
        "warehouse_control_boundary",
    }.issubset(question_ids)
    assert all(int(row["question_score"]) >= int(row["priority_score"]) for row in m49["dynamic_intake_question_register"])
    assert any(row["activation_reasons"] for row in m49["dynamic_intake_question_register"])

    assert m49["next_best_search_count"] >= 4
    assert all(row["search_family"] for row in m49["next_best_search_register"])
    assert all(row["stop_condition"] for row in m49["next_best_search_register"])
    assert any(
        "ask operator" in str(row.get("if_not_found", "")).lower()
        or "ask owner" in str(row.get("if_not_found", "")).lower()
        for row in m49["search_failure_effect_register"]
    )

    subtype_claim = next(
        row
        for row in m49["claim_impact_register"]
        if row["question_id"] == "warehouse_subtype_and_cold_chain_status"
    )
    assert "generic_warehouse_eui_claim" in subtype_claim["blocked_claims"]
    assert "peer_superiority_claim" in subtype_claim["blocked_claims"]

    assert m49["declared_input_downgrade_count"] >= 2
    assert all(row["max_maturity_level"] == 1 for row in m49["declared_input_downgrade_register"])
    assert all(row["confirmation_state"] == "DECLARED_BY_USER" for row in m49["declared_input_downgrade_register"])

    peer_by_key = {row["requirement_key"]: row for row in m51["peer_requirement_register"]}
    assert peer_by_key["asset_subtype_or_temperature_regime"]["comparison_status"] == "blocked"
    assert peer_by_key["dock_density_and_service_intensity"]["comparison_status"] == "blocked"
    assert peer_by_key["control_boundary_and_tariff"]["comparison_status"] == "blocked"
    assert peer_by_key["asset_subtype_or_temperature_regime"]["why_still_unbounded"]
    assert m51["comparison_not_yet_valid_count"] == 1
    assert "Do not compare this warehouse" in m51["comparison_not_yet_valid_register"][0]["explanation"]

    activated_patterns = {row["pattern_name"] for row in m52["activated_pattern_register"]}
    assert "dock_infiltration_and_door_discipline_plausible" in activated_patterns
    assert "forklift_charging_and_demand_spike_plausible" in activated_patterns
    assert all(row["evidence_state"] != "OBSERVED_FACT" for row in m52["loss_pattern_hypothesis_register"])

    exposure_types = {row["financial_exposure_type"] for row in m53["financial_exposure_type_register"]}
    assert "wrong_peer_valuation" in exposure_types
    assert "tariff_exposure_hidden" in exposure_types
    assert "tenant_operator_value_leakage" in exposure_types

    actions = {row["strategic_action"] for row in m54["expanded_tad_action_register"]}
    assert len(actions) > 3
    assert "BUILD_FAIR_PEER_SET" in actions
    assert "VALIDATE_TARIFF_EXPOSURE" in actions
    assert "DO_NOT_MODEL_YET" in actions
    assert "DO_NOT_SENSOR_YET" in actions
    assert "PROHIBIT_CLAIM" in actions
    assert any(
        "cannot discriminate the question" in row["hardware_trigger"].lower()
        or "no hardware upgrade" in row["hardware_trigger"].lower()
        for row in m52["measurement_strategy_register"]
    )

    assert 5 <= m54["gold_nugget_count"] <= 8
    assert any("wrong denominator" in row["gold_nugget"].lower() for row in m54["gold_nugget_register"])
    assert any("tariff design problem" in row["gold_nugget"].lower() for row in m54["gold_nugget_register"])


def test_warehouse_dynamic_congruence_acceptance_prevents_stale_charts_and_empty_peer_sections():
    bundle = _run_warehouse_chain()
    chart_bundle = _run_warehouse_chart_bundle(bundle)
    m18 = chart_bundle["motor_018"]
    m49 = bundle["motor_049"]
    m51 = bundle["motor_051"]

    assert m18["total_charts"] >= 3
    assert all(asset["chart_case_match_state"] == "same_case" for asset in m18["chart_assets"])
    assert all(
        asset["chart_context"]["target_name"] == "Sunrise Logistics Hub"
        for asset in m18["chart_assets"]
    )
    assert chart_bundle["cross_case_contamination_scan"]["render_eligible"] is True
    assert chart_bundle["cross_case_contamination_scan"]["issue_count"] == 0

    fallback_register = build_section_explanation_fallback_register(
        competitive_comparison_register=[],
        comparison_not_yet_valid_register=m51["comparison_not_yet_valid_register"],
        comparison_blocker_register=m51["comparison_blocker_register"],
        peer_requirement_register=m51["peer_requirement_register"],
        source_family_coverage_table=[],
        search_attempt_ledger=m49["search_attempt_ledger"],
        discovery_need_register=m49["discovery_need_register"],
        next_best_search_register=m49["next_best_search_register"],
    )
    body_sections = [
        {
            "section_id": "c10_competitive_peer",
            "title": "Competitive / Peer Comparison",
            "blocks": [{"content": "No competitive-comparison rows were produced."}],
        }
    ]
    body_out, appendix_out, applied_rows, population_rows = apply_empty_section_policy(
        body_sections=body_sections,
        appendix_sections=[],
        section_explanation_fallback_register=fallback_register,
    )

    assert body_out[0]["empty_section_policy_applied"] is True
    assert "What is required to populate it:" in body_out[0]["blocks"][0]["content"]
    assert "Do not compare this warehouse" in body_out[0]["blocks"][0]["content"]
    assert not appendix_out
    assert applied_rows
    assert population_rows[0]["population_state"] == "explained_fallback"
