from __future__ import annotations

from typing import Any

from ..congruence_intelligence.claim_governor import build_congruence_claim_contract_register
from ..congruence_intelligence.gold_nuggets import (
    build_gold_nugget_strength_register,
    build_strategic_gold_nugget_register,
)
from ..congruence_intelligence.strategic_tad import (
    build_congruence_action_priority_register,
    build_congruence_tad_enrichment_register,
    build_expanded_tad_action_register,
    build_prohibited_action_register,
)
from .base import BaseMotorAdapter


class Motor054Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_054"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_049", "motor_051", "motor_052", "motor_053"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m51 = dict(inputs.get("motor_051", {}) or {})
        m52 = dict(inputs.get("motor_052", {}) or {})
        m53 = dict(inputs.get("motor_053", {}) or {})

        asset_family_research_profile = (
            dict(inputs.get("motor_049", {}).get("asset_family_research_profile", {}) or {})
            if isinstance(inputs.get("motor_049"), dict)
            else {}
        )

        congruence_action_priority_register = build_congruence_action_priority_register(
            asset_family_research_profile=asset_family_research_profile,
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            invalid_problem_frame_register=list(m51.get("invalid_problem_frame_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
        )
        congruence_tad_enrichment_register = build_congruence_tad_enrichment_register(
            congruence_action_priority_register=congruence_action_priority_register,
        )
        expanded_tad_action_register = build_expanded_tad_action_register(
            asset_family_research_profile=asset_family_research_profile,
            gap_taxonomy_register=list(m51.get("gap_taxonomy_register", []) or []),
            evidence_need_class_register=list(m51.get("evidence_need_class_register", []) or []),
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            activated_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            financial_exposure_type_register=list(m53.get("financial_exposure_type_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            claim_impact_register=list(inputs.get("motor_049", {}).get("claim_impact_register", []) or [])
            if isinstance(inputs.get("motor_049"), dict)
            else [],
        )
        gold_nugget_register = build_strategic_gold_nugget_register(
            asset_family_research_profile=asset_family_research_profile,
            invalid_problem_frame_register=list(m51.get("invalid_problem_frame_register", []) or []),
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
            gold_nugget_candidate_register=list(m51.get("gold_nugget_candidate_register", []) or []),
            activated_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            financial_exposure_type_register=list(m53.get("financial_exposure_type_register", []) or []),
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            expanded_tad_action_register=expanded_tad_action_register,
        )
        gold_nugget_strength_register = build_gold_nugget_strength_register(
            gold_nugget_register=gold_nugget_register,
        )
        prohibited_action_register = build_prohibited_action_register(
            expanded_tad_action_register=expanded_tad_action_register,
        )
        congruence_claim_contract_register = build_congruence_claim_contract_register(
            strategic_gold_nugget_register=gold_nugget_register,
            congruence_action_priority_register=congruence_action_priority_register,
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            regulatory_physics_register=list(m53.get("regulatory_physics_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
            loss_pattern_hypothesis_register=list(m52.get("loss_pattern_hypothesis_register", []) or []),
            culture_execution_proxy_register=list(m53.get("culture_execution_proxy_register", []) or []),
        )
        return {
            "gold_nugget_register": gold_nugget_register,
            "gold_nugget_strength_register": gold_nugget_strength_register,
            "strategic_gold_nugget_register": gold_nugget_register,
            "congruence_action_priority_register": congruence_action_priority_register,
            "congruence_tad_enrichment_register": congruence_tad_enrichment_register,
            "expanded_tad_action_register": expanded_tad_action_register,
            "prohibited_action_register": prohibited_action_register,
            "congruence_claim_contract_register": congruence_claim_contract_register,
            "gold_nugget_count": len(gold_nugget_register),
            "gold_nugget_strength_count": len(gold_nugget_strength_register),
            "strategic_gold_nugget_count": len(gold_nugget_register),
            "congruence_action_priority_count": len(congruence_action_priority_register),
            "expanded_tad_action_count": len(expanded_tad_action_register),
            "prohibited_action_count": len(prohibited_action_register),
            "congruence_claim_contract_count": len(congruence_claim_contract_register),
        }
