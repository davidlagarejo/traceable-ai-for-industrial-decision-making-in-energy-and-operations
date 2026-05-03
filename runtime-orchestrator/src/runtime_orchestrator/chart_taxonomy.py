from __future__ import annotations

CHART_TAXONOMY_CATALOG_VERSION = "runtime_orchestrator.chart_taxonomy.v1"
CHART_CATEGORY_CATALOG_VERSION = CHART_TAXONOMY_CATALOG_VERSION

CHART_TAXONOMY_CATALOG = {
    "chart_congruence_binding_state": {"category": "binding_state", "lane": "congruence", "intent": "claim_binding_gate"},
    "chart_fair_comparison_gate": {"category": "comparison_gate", "lane": "comparison", "intent": "comparability_gate"},
    "chart_cross_layer_congruence_map": {"category": "cross_layer_congruence", "lane": "contradiction", "intent": "cross_layer_contradiction_map"},
    "chart_measurement_minimality_path": {"category": "measurement_minimality", "lane": "validation", "intent": "measurement_escalation_gate"},
    "chart_cost_driver_signal_profile": {"category": "cost_driver_profile", "lane": "finance", "intent": "cost_driver_screen"},
    "chart_gap_taxonomy_profile": {"category": "gap_taxonomy", "lane": "validation", "intent": "evidence_gap_diagnosis"},
    "chart_next_best_search_path": {"category": "next_best_search", "lane": "validation", "intent": "search_program"},
    "chart_peer_requirement_readiness": {"category": "peer_requirement_readiness", "lane": "comparison", "intent": "peer_readiness_gate"},
    "chart_source_scope_balance": {"category": "source_scope_balance", "lane": "context", "intent": "scope_coverage_balance"},
    "chart_asset_context_completeness": {"category": "asset_context_completeness", "lane": "context", "intent": "asset_context_coverage"},
    "chart_investment_uncertainty_map": {"category": "investment_uncertainty", "lane": "decision", "intent": "uncertainty_blocker_map"},
    "chart_minimum_evidence_pack": {"category": "minimum_evidence_pack", "lane": "validation", "intent": "minimum_evidence_request"},
    "chart_scenario_space": {"category": "scenario_space", "lane": "scenario", "intent": "scenario_bounding"},
    "chart_decision_front_status": {"category": "decision_front_status", "lane": "decision", "intent": "decision_posture"},
    "chart_context_routing_status": {"category": "context_routing", "lane": "context", "intent": "routing_readiness"},
    "chart_system_typology_prior": {"category": "system_typology_prior", "lane": "context", "intent": "system_prior_map"},
    "chart_inference_scores": {"category": "inference_scores", "lane": "inference", "intent": "inference_priority"},
    "chart_validation_priority": {"category": "validation_priority", "lane": "validation", "intent": "validation_priority"},
    "chart_revenue_trend": {"category": "revenue_trend", "lane": "finance", "intent": "issuer_scale_context"},
    "chart_revenue_composition": {"category": "revenue_composition", "lane": "finance", "intent": "issuer_mix_context"},
    "chart_debt_discrepancy": {"category": "debt_discrepancy", "lane": "finance", "intent": "financial_discrepancy"},
    "chart_tenant_concentration": {"category": "tenant_concentration", "lane": "finance", "intent": "concentration_risk"},
    "chart_ll97_scenario": {"category": "ll97_scenario", "lane": "regulatory", "intent": "regulatory_scenario"},
    "chart_evidence_ladder": {"category": "evidence_ladder", "lane": "validation", "intent": "evidence_maturity_progression"},
    "chart_validation_effort_matrix": {"category": "validation_effort_matrix", "lane": "validation", "intent": "validation_effort_tradeoff"},
    "chart_ll97_timeline": {"category": "ll97_timeline", "lane": "regulatory", "intent": "regulatory_timeline"},
    "chart_causal_dependency": {"category": "causal_dependency", "lane": "contradiction", "intent": "contradiction_dependency_map"},
    "chart_scenario_decision": {"category": "scenario_decision", "lane": "scenario", "intent": "decision_path_conditioning"},
}


def chart_category(chart_id: str) -> str:
    return CHART_TAXONOMY_CATALOG.get(str(chart_id or "").strip(), {}).get("category", "uncategorized")


def chart_lane(chart_id: str) -> str:
    return CHART_TAXONOMY_CATALOG.get(str(chart_id or "").strip(), {}).get("lane", "uncategorized")


def chart_intent(chart_id: str) -> str:
    return CHART_TAXONOMY_CATALOG.get(str(chart_id or "").strip(), {}).get("intent", "uncategorized")


def chart_taxonomy(chart_id: str) -> dict[str, str]:
    row = CHART_TAXONOMY_CATALOG.get(str(chart_id or "").strip(), {})
    return {
        "category": str(row.get("category", "uncategorized")),
        "lane": str(row.get("lane", "uncategorized")),
        "intent": str(row.get("intent", "uncategorized")),
    }
