from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime_orchestrator.congruence_intelligence.discovery_planner import (
    build_accepted_evidence_type_register,
    build_discovery_need_register,
    build_discovery_stop_condition_register,
    build_search_family_execution_plan,
)
from runtime_orchestrator.congruence_intelligence.dynamic_intake import (
    build_congruence_case_state,
    build_decision_context_register,
    build_dynamic_intake_question_register,
    build_intake_priority_register,
    build_question_candidate_register,
    build_question_normalization_register,
    build_required_from_register,
)
from runtime_orchestrator.congruence_intelligence.hypothesis_ingestion import (
    build_claim_impact_register,
    build_hypothesis_discrimination_register,
    build_rival_hypothesis_register,
)
from runtime_orchestrator.congruence_intelligence.next_best_search import (
    build_next_best_search_register,
)
from runtime_orchestrator.congruence_intelligence.peer_set_builder import (
    build_peer_requirement_register,
)

_FIXTURES_DIR = Path(__file__).with_name("fixtures")


def load_baseline_fixture(name: str) -> dict[str, Any]:
    path = _FIXTURES_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_contract_snapshot() -> dict[str, list[str]]:
    path = _FIXTURES_DIR / "dynamic_congruence_register_contract_snapshot.json"
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return {str(key): list(value) for key, value in raw.items()}


def build_baseline_register_bundle(fixture: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    discovery_need_register = build_discovery_need_register(
        target_definition=dict(fixture.get("target_definition", {}) or {}),
        coverage_gaps=list(fixture.get("coverage_gaps", []) or []),
        requestable_evidence_items=list(fixture.get("requestable_evidence_items", []) or []),
        attempts=list(fixture.get("attempts", []) or []),
        search_budget_register=list(fixture.get("search_budget_register", []) or []),
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
    intake_stop_condition_register = [
        {
            "path_id": str(row.get("need_id", "")).strip(),
            "minimum_sufficient_evidence": str(row.get("minimum_sufficient_evidence", "")).strip(),
            "stop_condition": str(row.get("stop_condition", "")).strip(),
            "downgrade_condition": str(row.get("downgrade_condition", "")).strip(),
            "escalation_condition": str(row.get("escalation_condition", "")).strip(),
        }
        for row in discovery_stop_condition_register
        if str(row.get("need_id", "")).strip()
    ] + [dict(row) for row in list(fixture.get("pack_stop_conditions", []) or [])]
    next_best_search_register = build_next_best_search_register(
        discovery_need_register=discovery_need_register,
        discovery_stop_condition_register=discovery_stop_condition_register,
        search_budget_register=list(fixture.get("search_budget_register", []) or []),
    )
    congruence_case_state = build_congruence_case_state(
        asset_family_research_profile=dict(fixture.get("asset_family_research_profile", {}) or {}),
        operational_intake_pack=dict(fixture.get("operational_intake_pack", {}) or {}),
        discovery_need_register=discovery_need_register,
        target_definition=dict(fixture.get("target_definition", {}) or {}),
    )
    decision_context_register = build_decision_context_register(
        asset_family_research_profile=dict(fixture.get("asset_family_research_profile", {}) or {}),
        operational_intake_pack=dict(fixture.get("operational_intake_pack", {}) or {}),
        discovery_need_register=discovery_need_register,
        congruence_case_state=congruence_case_state,
        target_definition=dict(fixture.get("target_definition", {}) or {}),
    )
    question_candidate_register = build_question_candidate_register(
        asset_family_research_profile=dict(fixture.get("asset_family_research_profile", {}) or {}),
        operational_intake_pack=dict(fixture.get("operational_intake_pack", {}) or {}),
        discovery_need_register=discovery_need_register,
        stop_condition_register=intake_stop_condition_register,
        congruence_case_state=congruence_case_state,
        decision_context_register=decision_context_register,
        target_definition=dict(fixture.get("target_definition", {}) or {}),
    )
    question_normalization_register = build_question_normalization_register(
        asset_family_research_profile=dict(fixture.get("asset_family_research_profile", {}) or {}),
        question_candidate_register=question_candidate_register,
    )
    dynamic_intake_question_register = build_dynamic_intake_question_register(
        asset_family_research_profile=dict(fixture.get("asset_family_research_profile", {}) or {}),
        operational_intake_pack=dict(fixture.get("operational_intake_pack", {}) or {}),
        discovery_need_register=discovery_need_register,
        stop_condition_register=intake_stop_condition_register,
        congruence_case_state=congruence_case_state,
        target_definition=dict(fixture.get("target_definition", {}) or {}),
    )
    required_from_register = build_required_from_register(
        dynamic_intake_question_register=dynamic_intake_question_register,
    )
    intake_priority_register = build_intake_priority_register(
        dynamic_intake_question_register=dynamic_intake_question_register,
    )
    rival_hypothesis_register = build_rival_hypothesis_register(
        dynamic_intake_question_register=dynamic_intake_question_register,
        stop_condition_register=intake_stop_condition_register,
        next_best_search_register=next_best_search_register,
    )
    hypothesis_discrimination_register = build_hypothesis_discrimination_register(
        dynamic_intake_question_register=dynamic_intake_question_register,
        stop_condition_register=intake_stop_condition_register,
        next_best_search_register=next_best_search_register,
    )
    claim_impact_register = build_claim_impact_register(
        dynamic_intake_question_register=dynamic_intake_question_register,
        stop_condition_register=intake_stop_condition_register,
    )
    peer_requirement_register = build_peer_requirement_register(
        asset_family_research_profile=dict(fixture.get("asset_family_research_profile", {}) or {}),
        fair_comparison_profile=dict(fixture.get("fair_comparison_profile", {}) or {}),
        operational_intake_pack=dict(fixture.get("operational_intake_pack", {}) or {}),
        dynamic_intake_question_register=dynamic_intake_question_register,
    )
    return {
        "discovery_need_register": discovery_need_register,
        "search_family_execution_plan": search_family_execution_plan,
        "accepted_evidence_type_register": accepted_evidence_type_register,
        "discovery_stop_condition_register": discovery_stop_condition_register,
        "intake_stop_condition_register": intake_stop_condition_register,
        "next_best_search_register": next_best_search_register,
        "decision_context_register": decision_context_register,
        "question_candidate_register": question_candidate_register,
        "question_normalization_register": question_normalization_register,
        "dynamic_intake_question_register": dynamic_intake_question_register,
        "required_from_register": required_from_register,
        "intake_priority_register": intake_priority_register,
        "rival_hypothesis_register": rival_hypothesis_register,
        "hypothesis_discrimination_register": hypothesis_discrimination_register,
        "claim_impact_register": claim_impact_register,
        "peer_requirement_register": peer_requirement_register,
    }
