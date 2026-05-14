from __future__ import annotations

from typing import Any

from ..phase_units import to_belief_revision_event_register
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
from ..zlab_skill import (
    apply_combination_validators,
    build_active_skill_pattern_state,
    build_admissible_combination_review_register,
    build_asset_context_vector,
    build_combination_activation_register,
    build_combination_review_register,
    build_context_differentiator_register,
    build_latent_combination_candidate_register,
    build_registry_gold_nugget_register,
    build_registry_pattern_activation_register,
    build_registry_tad_action_register,
    build_skill_cutover_authority_register,
    load_registry_bundle,
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

        # V8 demo helper — accept admissible combinations automatically
        # for this single run. Opt-in via pipeline_inputs flag (does NOT
        # bypass any gate, just sets default_decision to "accepted" for
        # candidates that already passed validators).
        _pipeline = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        _auto_accept = bool(_pipeline.get("__auto_accept_combinations__", False))
        _combo_default_decision = "accepted" if _auto_accept else "needs_review"

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
        authoritative_financial_exposure_register = list(
            m53.get("authoritative_financial_exposure_register", m53.get("financial_exposure_type_register", [])) or []
        )
        financial_exposure_authority_state = str(
            m53.get("financial_exposure_authority_state", "legacy_primary")
        ).strip() or "legacy_primary"
        expanded_tad_action_register = build_expanded_tad_action_register(
            asset_family_research_profile=asset_family_research_profile,
            gap_taxonomy_register=list(m51.get("gap_taxonomy_register", []) or []),
            evidence_need_class_register=list(m51.get("evidence_need_class_register", []) or []),
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            activated_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            financial_exposure_type_register=authoritative_financial_exposure_register,
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
            financial_exposure_type_register=authoritative_financial_exposure_register,
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            expanded_tad_action_register=expanded_tad_action_register,
        )
        gold_nugget_strength_register = build_gold_nugget_strength_register(
            gold_nugget_register=gold_nugget_register,
        )
        try:
            registry_bundle = load_registry_bundle()
        except Exception:
            registry_bundle = {}
        skill_active_pattern_ids, skill_active_pattern_sources, anti_trigger_signals = build_active_skill_pattern_state(
            motor_049_output=inputs.get("motor_049", {}) if isinstance(inputs.get("motor_049"), dict) else {},
            motor_051_output=m51,
            motor_052_output=m52,
            motor_053_output=m53,
        )
        skill_combination_activation_register = build_combination_activation_register(
            registry_bundle=registry_bundle,
            active_pattern_ids=skill_active_pattern_ids,
            anti_trigger_signals=anti_trigger_signals,
        )
        skill_combination_activation_register = apply_combination_validators(
            skill_combination_activation_register,
            registry_bundle=registry_bundle,
        )
        skill_combination_review_register = build_combination_review_register(
            combination_activation_register=skill_combination_activation_register,
            default_decision=_combo_default_decision,
        )
        full_skill_pattern_activation_register = build_registry_pattern_activation_register(
            registry_bundle=registry_bundle,
            active_pattern_sources=skill_active_pattern_sources,
        )
        skill_asset_context_vector = build_asset_context_vector(
            asset_family_research_profile=asset_family_research_profile,
            runtime_context={},
            motor_051_output=m51,
            motor_052_output=m52,
            motor_053_output=m53,
        )
        skill_context_differentiator_register = build_context_differentiator_register(
            asset_context_vector=skill_asset_context_vector,
        )
        skill_latent_combination_candidate_register = build_latent_combination_candidate_register(
            registry_bundle=registry_bundle,
            active_pattern_ids=skill_active_pattern_ids,
            active_pattern_rows=full_skill_pattern_activation_register,
            asset_context_vector=skill_asset_context_vector,
        )
        skill_admissible_combination_review_register = build_admissible_combination_review_register(
            latent_combination_candidate_register=skill_latent_combination_candidate_register,
            default_decision=_combo_default_decision,
        )
        skill_expanded_tad_action_register = build_registry_tad_action_register(
            combination_review_register=skill_combination_review_register,
            skill_pattern_activation_register=full_skill_pattern_activation_register,
            skill_financial_exposure_register=authoritative_financial_exposure_register,
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            claim_impact_register=list(inputs.get("motor_049", {}).get("claim_impact_register", []) or [])
            if isinstance(inputs.get("motor_049"), dict)
            else [],
        )
        required_skill_tad_actions = {
            "BUILD_FAIR_PEER_SET",
            "VALIDATE_TARIFF_EXPOSURE",
            "VALIDATE_CONTROL_BOUNDARY",
            "VALIDATE_LOSS_PATTERN",
            "DO_NOT_MODEL_YET",
            "DO_NOT_SENSOR_YET",
            "DO_NOT_INVEST_YET",
            "PROHIBIT_CLAIM",
        }
        skill_tad_action_ids = {
            str(row.get("strategic_action", "")).strip()
            for row in skill_expanded_tad_action_register
            if str(row.get("strategic_action", "")).strip()
        }
        tad_authority_state = (
            "skill_primary"
            if required_skill_tad_actions.issubset(skill_tad_action_ids)
            else "legacy_primary_skill_shadow"
        )
        authoritative_tad_action_register = (
            skill_expanded_tad_action_register
            if tad_authority_state == "skill_primary"
            else expanded_tad_action_register
        )
        skill_gold_nugget_register = build_registry_gold_nugget_register(
            registry_bundle=registry_bundle,
            combination_review_register=skill_combination_review_register,
            skill_pattern_activation_register=full_skill_pattern_activation_register,
            skill_financial_exposure_register=authoritative_financial_exposure_register,
            tad_action_register=authoritative_tad_action_register,
            asset_family_research_profile=asset_family_research_profile,
        )
        skill_gold_nugget_themes = {
            str(row.get("nugget_theme", "")).strip()
            for row in skill_gold_nugget_register
            if str(row.get("nugget_theme", "")).strip()
        }
        asset_family = str(asset_family_research_profile.get("asset_family", "")).strip()
        if asset_family == "commercial_building":
            required_gold_nugget_themes = {
                "controls_or_schedule",
                "boundary_leakage",
                "model_prematurity",
            }
        elif asset_family == "industrial_manufacturing":
            required_gold_nugget_themes = {
                "process_dominance",
                "support_utility_loss",
                "model_prematurity",
            }
        else:
            required_gold_nugget_themes = {
                "comparison_invalidity",
                "tariff_orchestration",
                "boundary_leakage",
            }
        gold_nugget_authority_state = (
            "skill_primary"
            if 3 <= len(skill_gold_nugget_register) <= 5
            and required_gold_nugget_themes.issubset(skill_gold_nugget_themes)
            else "legacy_primary_skill_shadow"
        )
        authoritative_gold_nugget_register = (
            skill_gold_nugget_register
            if gold_nugget_authority_state == "skill_primary"
            else gold_nugget_register
        )
        skill_cutover_authority_register = build_skill_cutover_authority_register(
            legacy_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            skill_pattern_register=list(m52.get("skill_pattern_activation_register", []) or []),
            legacy_financial_exposure_register=list(m53.get("financial_exposure_type_register", []) or []),
            skill_financial_exposure_register=list(m53.get("skill_financial_exposure_register", []) or []),
            skill_combination_review_register=skill_combination_review_register,
            legacy_tad_register=expanded_tad_action_register,
            skill_tad_register=skill_expanded_tad_action_register,
            legacy_gold_nugget_register=gold_nugget_register,
            skill_gold_nugget_register=skill_gold_nugget_register,
            promoted_domains=[
                domain
                for domain, state in (
                    ("patterns", str(m52.get("pattern_authority_state", "legacy_primary_skill_shadow")).strip()),
                    ("financial_exposure", financial_exposure_authority_state),
                    ("tad", tad_authority_state),
                    ("gold_nuggets", gold_nugget_authority_state),
                )
                if state == "skill_primary"
            ],
        )
        prohibited_action_register = build_prohibited_action_register(
            expanded_tad_action_register=authoritative_tad_action_register,
        )
        congruence_claim_contract_register = build_congruence_claim_contract_register(
            strategic_gold_nugget_register=authoritative_gold_nugget_register,
            strategic_gold_nugget_source=(
                "motor_054.authoritative_gold_nugget_register"
                if gold_nugget_authority_state == "skill_primary"
                else "motor_054.strategic_gold_nugget_register"
            ),
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
            "skill_active_pattern_ids": skill_active_pattern_ids,
            "skill_active_pattern_sources": skill_active_pattern_sources,
            "skill_asset_context_vector": skill_asset_context_vector,
            "skill_context_differentiator_register": skill_context_differentiator_register,
            "skill_combination_activation_register": skill_combination_activation_register,
            "skill_combination_review_register": skill_combination_review_register,
            "skill_latent_combination_candidate_register": skill_latent_combination_candidate_register,
            "skill_admissible_combination_review_register": skill_admissible_combination_review_register,
            "skill_expanded_tad_action_register": skill_expanded_tad_action_register,
            "skill_gold_nugget_register": skill_gold_nugget_register,
            "skill_cutover_authority_register": skill_cutover_authority_register,
            "authoritative_financial_exposure_register": authoritative_financial_exposure_register,
            "financial_exposure_authority_state": financial_exposure_authority_state,
            "authoritative_tad_action_register": authoritative_tad_action_register,
            "tad_authority_state": tad_authority_state,
            "authoritative_gold_nugget_register": authoritative_gold_nugget_register,
            "gold_nugget_authority_state": gold_nugget_authority_state,
            "prohibited_action_register": prohibited_action_register,
            "congruence_claim_contract_register": congruence_claim_contract_register,
            # V5 P2: canonical Phase 7 unit (Master Doc §4) — projection of
            # claim contracts + congruence enrichments into
            # belief_revision_event records. Sparse data → empty register.
            "belief_revision_event_register": to_belief_revision_event_register(
                belief_revision_log=[
                    {
                        "event_id": f"BRE-{contract.get('claim_id', i)}",
                        "target_object": contract.get("claim_id", ""),
                        "prior_state": contract.get("prior_state", "unsupported"),
                        "trigger_event": "claim_contract_assigned",
                        "dependency_type": "claim_governance",
                        "causal_statement": contract.get("rationale", ""),
                        "scope_impact": contract.get("scope_impact", "claim_visibility_only"),
                        "propagation_scope": list(contract.get("affected_claims", []) or []),
                        "publication_consequence": contract.get("publication_consequence", ""),
                        "lifecycle_action": contract.get("lifecycle_action", "maintain"),
                    }
                    for i, contract in enumerate(congruence_claim_contract_register or [])
                    if isinstance(contract, dict)
                ],
                contradiction_register=None,
            ),
            "gold_nugget_count": len(gold_nugget_register),
            "gold_nugget_strength_count": len(gold_nugget_strength_register),
            "strategic_gold_nugget_count": len(gold_nugget_register),
            "congruence_action_priority_count": len(congruence_action_priority_register),
            "expanded_tad_action_count": len(expanded_tad_action_register),
            "skill_combination_activation_count": len(skill_combination_activation_register),
            "skill_combination_review_count": len(skill_combination_review_register),
            "skill_latent_combination_candidate_count": len(skill_latent_combination_candidate_register),
            "skill_admissible_combination_review_count": len(skill_admissible_combination_review_register),
            "skill_expanded_tad_action_count": len(skill_expanded_tad_action_register),
            "skill_gold_nugget_count": len(skill_gold_nugget_register),
            "authoritative_tad_action_count": len(authoritative_tad_action_register),
            "authoritative_gold_nugget_count": len(authoritative_gold_nugget_register),
            "prohibited_action_count": len(prohibited_action_register),
            "congruence_claim_contract_count": len(congruence_claim_contract_register),
        }
