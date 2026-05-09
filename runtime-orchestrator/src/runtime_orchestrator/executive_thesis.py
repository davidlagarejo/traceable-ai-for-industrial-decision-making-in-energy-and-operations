from __future__ import annotations

from typing import Any

from .composer_helpers.composition import (
    _capital_logic_if_assumption_breaks,
    _capital_logic_if_assumption_holds,
    _client_facing_tad_actions,
    _conditional_minimum_evidence,
    _conditional_structural_intelligence_available,
    _confidence_level,
    _dominant_loss_logic_take,
    _dominant_operational_misunderstanding,
    _effective_primary_problem,
    _evidence_state,
    _fallback_conditional_conflict,
    _finance_to_physics_take,
    _financial_rows,
    _hidden_assumption_at_risk,
    _hidden_system_boundary_error,
    _inadmissibility_reason,
    _interpretive_signal_register,
    _invalid_comparison_risk_take,
    _maintenance_reality_take,
    _measurement_minimality_take,
    _primary_financial_exposure,
    _primary_peer_comparison,
    _primary_redesign,
    _ranked_conflict_register,
    _regulatory_physics_take,
    _sorted_tad_actions,
    _subject_family,
    _surprising_takeaway,
    _top_scenarios,
    _what_is_not_admissible,
    _what_reality_feature_changes_the_decision,
    _why_current_question_is_premature,
)
from .composer_helpers.registers import (
    _build_correlation_constellation_register,
    _build_evidence_pack_register,
    _build_thesis_constellation_register,
    _translated_congruence_conflict_register,
)
from .composer_helpers.selection import (
    _STRUCTURAL_CLASSIFICATION_STATES,
    _selected_output_mode,
    _supporting_modes,
    _top_dominant_variables,
    _top_gold_nugget_rows,
)
from .composer_helpers.text_helpers import (
    _CONCEPT_MARKER_MAP,
    _TOKEN_STOPWORDS,
    _concept_markers,
    _dedupe,
    _format_label,
    _is_semantically_redundant,
    _join_sentences,
    _list_text,
    _overlap_ratio,
    _overlap_score,
    _shared_token_count,
    _split_compound_evidence,
    _text,
    _tokens,
)
from .output_taxonomy import canonicalize_output_mode

_TAD_STATUS_PRIORITY = {
    "ACT NOW": 0,
    "VALIDATE FIRST": 1,
    "COMPARE TO PEERS": 2,
    "REDESIGN HYPOTHESIS": 3,
    "INVESTIGATE": 4,
    "DEFER": 5,
    "NO-GO": 6,
    "DO NOT MODEL YET": 7,
}



def build_executive_thesis(  # noqa: PLR0913
    *,
    system_abstraction: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
    problem_framing_register: list[dict[str, Any]],
    dominant_variable_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    scenario_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    expanded_structural_tad_action_register: list[dict[str, Any]],
    claim_contract_register: list[dict[str, Any]],
    report_output_mode_classifier_table: list[dict[str, Any]],
    invalid_problem_frame_register: list[dict[str, Any]] | None = None,
    invalid_comparison_risk_register: list[dict[str, Any]] | None = None,
    cross_layer_congruence_register: list[dict[str, Any]] | None = None,
    loss_pattern_hypothesis_register: list[dict[str, Any]] | None = None,
    maintenance_reality_register: list[dict[str, Any]] | None = None,
    measurement_strategy_register: list[dict[str, Any]] | None = None,
    regulatory_physics_register: list[dict[str, Any]] | None = None,
    finance_physics_dependency_register: list[dict[str, Any]] | None = None,
    strategic_gold_nugget_register: list[dict[str, Any]] | None = None,
    strategic_gold_nugget_source_register: str = "motor_054.strategic_gold_nugget_register",
    strategic_gold_nugget_authority_state: str = "legacy_primary_skill_shadow",
    gold_nugget_strength_register: list[dict[str, Any]] | None = None,
    congruence_action_priority_register: list[dict[str, Any]] | None = None,
    congruence_claim_contract_register: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    invalid_problem_frame_register = list(invalid_problem_frame_register or [])
    invalid_comparison_risk_register = list(invalid_comparison_risk_register or [])
    cross_layer_congruence_register = list(cross_layer_congruence_register or [])
    loss_pattern_hypothesis_register = list(loss_pattern_hypothesis_register or [])
    maintenance_reality_register = list(maintenance_reality_register or [])
    measurement_strategy_register = list(measurement_strategy_register or [])
    regulatory_physics_register = list(regulatory_physics_register or [])
    finance_physics_dependency_register = list(finance_physics_dependency_register or [])
    strategic_gold_nugget_register = list(strategic_gold_nugget_register or [])
    gold_nugget_strength_register = list(gold_nugget_strength_register or [])
    congruence_action_priority_register = list(congruence_action_priority_register or [])
    congruence_claim_contract_register = list(congruence_claim_contract_register or [])

    effective_primary_problem = _effective_primary_problem(
        problem_framing_register=problem_framing_register,
        invalid_problem_frame_register=invalid_problem_frame_register,
    )
    effective_conflict_register = list(cross_layer_conflict_register or [])
    if not effective_conflict_register:
        effective_conflict_register = _translated_congruence_conflict_register(cross_layer_congruence_register)
    ranked_conflicts = _ranked_conflict_register(
        canonical_problem_frame=canonical_problem_frame,
        cross_layer_conflict_register=effective_conflict_register,
        structural_financial_exposure_register=structural_financial_exposure_register,
        minimum_evidence_for_discrimination_register=minimum_evidence_for_discrimination_register,
        expanded_structural_tad_action_register=expanded_structural_tad_action_register,
        claim_contract_register=claim_contract_register,
    )
    primary_conflict = ranked_conflicts[0] if ranked_conflicts else {}
    primary_minimum_evidence = (
        minimum_evidence_for_discrimination_register[0]
        if minimum_evidence_for_discrimination_register
        else {}
    )
    primary_redesign = _primary_redesign(conditional_redesign_register)
    primary_financial = _primary_financial_exposure(structural_financial_exposure_register)
    primary_peer = _primary_peer_comparison(competitive_comparison_register)
    selected_mode = _selected_output_mode(report_output_mode_classifier_table)
    supporting_modes = _supporting_modes(report_output_mode_classifier_table, selected_mode)
    subject_family = _subject_family(
        system_abstraction=system_abstraction,
        canonical_problem_frame=canonical_problem_frame,
        cross_layer_conflict_register=effective_conflict_register,
    )
    minimum_discriminating_evidence = _split_compound_evidence(
        primary_minimum_evidence.get("minimum_evidence")
        or canonical_problem_frame.get("minimum_evidence_to_discriminate")
    )
    top_actions = _client_facing_tad_actions(
        expanded_structural_tad_action_register,
        _text(primary_conflict.get("conflict")) or _text(canonical_problem_frame.get("dominant_conflict")),
        minimum_discriminating_evidence,
        congruence_action_priority_register=congruence_action_priority_register,
    )
    evidence_state = _evidence_state(
        canonical_problem_frame,
        cross_layer_conflict_register,
        structural_financial_exposure_register,
    )
    what_is_admissible_now = [row["action"] for row in top_actions[:3]]
    prohibited_actions = _what_is_not_admissible(
        claim_contract_register,
        governed_claim_contract_register=congruence_claim_contract_register,
    )
    top_scenarios = _top_scenarios(scenario_register)
    top_variables = _top_dominant_variables(dominant_variable_register)
    selected_top_gold_nuggets = _top_gold_nugget_rows(
        strategic_gold_nugget_register,
        gold_nugget_strength_register=gold_nugget_strength_register,
        limit=8,
    )
    why_it_matters = (
        _text(primary_conflict.get("why_it_matters"))
        or _text(primary_financial.get("financial_exposure_if_wrong"))
        or _text(effective_primary_problem.get("strategic_risk"))
    )
    dominant_risk = (
        _text(primary_financial.get("financial_exposure_if_wrong"))
        or _text(effective_primary_problem.get("strategic_risk"))
    )
    dominant_contradiction = _text(primary_conflict.get("conflict")) or _text(canonical_problem_frame.get("dominant_conflict"))
    structural_thesis_admissible = bool(canonical_problem_frame.get("problem_frame_active", False)) and bool(dominant_contradiction)
    if not structural_thesis_admissible:
        inadmissibility_reason = _inadmissibility_reason(
            selected_mode=selected_mode,
            canonical_problem_frame=canonical_problem_frame,
            system_abstraction=system_abstraction,
        )
        conditional_intelligence_available = _conditional_structural_intelligence_available(
            effective_primary_problem=effective_primary_problem,
            canonical_problem_frame=canonical_problem_frame,
            ranked_conflicts=ranked_conflicts,
            invalid_problem_frame_register=invalid_problem_frame_register,
            invalid_comparison_risk_register=invalid_comparison_risk_register,
            loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            finance_physics_dependency_register=finance_physics_dependency_register,
            strategic_gold_nugget_register=strategic_gold_nugget_register,
            congruence_action_priority_register=congruence_action_priority_register,
            conditional_redesign_register=conditional_redesign_register,
            top_variables=top_variables,
        )
        if conditional_intelligence_available:
            fallback_conflict = primary_conflict or _fallback_conditional_conflict(
                canonical_problem_frame=canonical_problem_frame,
                effective_primary_problem=effective_primary_problem,
                invalid_problem_frame_register=invalid_problem_frame_register,
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            )
            conditional_ranked_conflicts = list(ranked_conflicts or [fallback_conflict])
            conditional_primary_conflict = dict(conditional_ranked_conflicts[0] if conditional_ranked_conflicts else fallback_conflict)
            conditional_dominant_contradiction = _text(conditional_primary_conflict.get("conflict")) or "Visible framing vs dominant structural driver"
            conditional_minimum_evidence = _conditional_minimum_evidence(
                primary_minimum_evidence=primary_minimum_evidence,
                canonical_problem_frame=canonical_problem_frame,
                effective_primary_problem=effective_primary_problem,
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
            )
            conditional_top_actions = _client_facing_tad_actions(
                expanded_structural_tad_action_register,
                conditional_dominant_contradiction,
                conditional_minimum_evidence,
                congruence_action_priority_register=congruence_action_priority_register,
            )
            conditional_evidence_state = (
                _text(effective_primary_problem.get("evidence_state"))
                or _text(conditional_primary_conflict.get("evidence_state"))
                or _text(primary_financial.get("evidence_state"))
                or "CONDITIONAL_HYPOTHESIS"
            )
            conditional_why_it_matters = (
                _text(conditional_primary_conflict.get("why_it_matters"))
                or _text(primary_financial.get("financial_exposure_if_wrong"))
                or _text(effective_primary_problem.get("strategic_risk"))
                or inadmissibility_reason
            )
            conditional_dominant_risk = (
                _text(primary_financial.get("financial_exposure_if_wrong"))
                or _text(effective_primary_problem.get("strategic_risk"))
                or "A local structural thesis would still overstate what the system actually knows, but the current framing may still be strategically wrong."
            )
            conditional_hidden_assumption = _hidden_assumption_at_risk(subject_family, conditional_dominant_contradiction)
            conditional_measurement_take = _measurement_minimality_take(measurement_strategy_register)
            conditional_regulatory_take = _regulatory_physics_take(regulatory_physics_register)
            conditional_finance_take = _finance_to_physics_take(finance_physics_dependency_register)
            conditional_maintenance_take = _maintenance_reality_take(maintenance_reality_register)
            conditional_operational_misunderstanding = _dominant_operational_misunderstanding(
                invalid_problem_frame_register=invalid_problem_frame_register,
                strategic_gold_nugget_register=strategic_gold_nugget_register,
            )
            conditional_hidden_boundary_error = _hidden_system_boundary_error(
                cross_layer_congruence_register=cross_layer_congruence_register,
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
            )
            conditional_invalid_comparison = _invalid_comparison_risk_take(invalid_comparison_risk_register)
            conditional_loss_logic = _dominant_loss_logic_take(
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
                maintenance_reality_register=maintenance_reality_register,
                strategic_gold_nugget_register=strategic_gold_nugget_register,
            )
            conditional_evidence_pack_register = _build_evidence_pack_register(
                minimum_discriminating_evidence=conditional_minimum_evidence,
                minimum_evidence_source=_text(primary_minimum_evidence.get("source"))
                or _text(canonical_problem_frame.get("minimum_evidence_source"))
                or "conditional_structural_intelligence_layer",
                minimum_evidence_unlocks=_list_text(primary_minimum_evidence.get("unlocks"))
                or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks"))
                or [
                    "local structural closure",
                    "fair comparison admissibility",
                    "capital logic discrimination",
                ],
                invalid_comparison_risk_register=invalid_comparison_risk_register,
                finance_physics_dependency_register=finance_physics_dependency_register,
                loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
                effective_primary_problem=effective_primary_problem,
            )
            conditional_thesis_constellation_register = _build_thesis_constellation_register(
                primary_conflict=conditional_primary_conflict,
                ranked_conflicts=conditional_ranked_conflicts,
                top_variables=top_variables,
                invalid_comparison_risk=conditional_invalid_comparison,
                dominant_loss_logic=conditional_loss_logic,
                hidden_system_boundary_error=conditional_hidden_boundary_error,
                top_gold_nuggets=selected_top_gold_nuggets,
                evidence_pack_register=conditional_evidence_pack_register,
            )
            conditional_correlation_constellation_register = _build_correlation_constellation_register(
                conditional_ranked_conflicts,
            )
            conditional_interpretive_signal_register = _interpretive_signal_register(
                subject_family=subject_family,
                dominant_contradiction=conditional_dominant_contradiction,
                evidence_state=conditional_evidence_state,
                primary_problem=effective_primary_problem,
                primary_financial=primary_financial,
                primary_redesign=primary_redesign,
                primary_peer=primary_peer,
                minimum_discriminating_evidence=conditional_minimum_evidence,
            )
            return {
                "declared_problem": _text(effective_primary_problem.get("stated_problem"))
                or _text(canonical_problem_frame.get("stated_problem"))
                or "Need bounded target understanding before structural interpretation.",
                "reframed_problem": _text(effective_primary_problem.get("reframed_problem"))
                or _text(canonical_problem_frame.get("reframed_problem"))
                or "The current framing may be wrong even though local structural closure remains blocked.",
                "dominant_contradiction": conditional_dominant_contradiction,
                "why_it_matters": conditional_why_it_matters,
                "dominant_risk": conditional_dominant_risk,
                "hidden_assumption_at_risk": conditional_hidden_assumption,
                "why_current_question_is_premature": _join_sentences(
                    inadmissibility_reason,
                    _why_current_question_is_premature(
                        subject_family,
                        conditional_dominant_contradiction,
                        conditional_minimum_evidence,
                    ),
                    conditional_measurement_take,
                ),
                "what_reality_feature_changes_the_decision": _what_reality_feature_changes_the_decision(
                    subject_family,
                    conditional_dominant_contradiction,
                ),
                "capital_logic_if_assumption_holds": _join_sentences(
                    _capital_logic_if_assumption_holds(
                        subject_family,
                        primary_redesign,
                        primary_financial,
                    ),
                    conditional_finance_take,
                ),
                "capital_logic_if_assumption_breaks": _capital_logic_if_assumption_breaks(
                    subject_family,
                    primary_financial,
                    primary_redesign,
                ),
                "surprising_but_evidenced_takeaway": _surprising_takeaway(
                    subject_family=subject_family,
                    interpretive_signal_register=conditional_interpretive_signal_register,
                    hidden_assumption_at_risk=conditional_hidden_assumption,
                    dominant_contradiction=conditional_dominant_contradiction,
                ),
                "what_is_admissible_now": [row["action"] for row in conditional_top_actions[:3]],
                "what_is_not_admissible": prohibited_actions,
                "minimum_discriminating_evidence": conditional_minimum_evidence,
                "minimum_discriminating_evidence_source": _text(primary_minimum_evidence.get("source"))
                or _text(canonical_problem_frame.get("minimum_evidence_source"))
                or "conditional_structural_intelligence_layer",
                "minimum_discriminating_evidence_unlocks": _list_text(primary_minimum_evidence.get("unlocks"))
                or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks"))
                or [
                    "local structural closure",
                    "fair comparison admissibility",
                    "capital logic discrimination",
                ],
                "conditional_redesign": primary_redesign,
                "evidence_state": conditional_evidence_state,
                "report_mode": selected_mode,
                "confidence_level": _confidence_level(conditional_evidence_state),
                "top_dominant_variables": top_variables,
                "top_scenarios": top_scenarios,
                "top_actions": conditional_top_actions,
                "dominant_lens": conditional_dominant_contradiction,
                "supporting_modes": supporting_modes,
                "primary_financial_exposure": primary_financial,
                "primary_peer_comparison": primary_peer,
                "dominant_operational_misunderstanding": conditional_operational_misunderstanding,
                "hidden_system_boundary_error": conditional_hidden_boundary_error,
                "invalid_comparison_risk": conditional_invalid_comparison,
                "dominant_loss_logic": conditional_loss_logic,
                "measurement_minimality_take": conditional_measurement_take,
                "regulatory_physics_take": conditional_regulatory_take,
                "finance_to_physics_take": conditional_finance_take,
                "maintenance_reality_take": conditional_maintenance_take,
                "top_gold_nuggets": selected_top_gold_nuggets,
                "gold_nugget_source_register": _text(strategic_gold_nugget_source_register),
                "gold_nugget_authority_state": _text(strategic_gold_nugget_authority_state) or "legacy_primary_skill_shadow",
                "gold_nugget_strength_register": gold_nugget_strength_register[:8],
                "evidence_pack_register": conditional_evidence_pack_register,
                "thesis_constellation_register": conditional_thesis_constellation_register,
                "correlation_constellation_register": conditional_correlation_constellation_register,
                "congruence_action_priority_register": congruence_action_priority_register[:5],
                "interpretive_signal_register": conditional_interpretive_signal_register,
                "dominant_contradiction_selection_basis": dict(conditional_primary_conflict.get("selection_basis", {}) or {}),
                "thesis_ranked_conflict_register": conditional_ranked_conflicts,
                "rejected_contradiction_candidates": conditional_ranked_conflicts[1:],
                "governed_claim_contract_register": congruence_claim_contract_register,
                "governed_claim_contract_count": len(congruence_claim_contract_register),
                "thesis_state": "conditional_structural_intelligence",
                "local_thesis_state": "inadmissible_local_closure",
                "local_claim_closure_state": "blocked",
                "conditional_intelligence_available": True,
                "conditional_intelligence_reason": "Local structural closure remains blocked, but bounded archetypal and conditional intelligence is still admissible.",
                "inadmissibility_reason": inadmissibility_reason,
                "compression_targets": {
                    "max_dominant_variables": 4,
                    "max_primary_scenarios": 3,
                    "max_primary_actions": 4,
                    "max_primary_redesign_paths": 2,
                    "max_primary_evidence_packs": 3,
                },
            }
        return {
            "declared_problem": _text(effective_primary_problem.get("stated_problem"))
            or _text(canonical_problem_frame.get("stated_problem"))
            or "Need bounded target understanding before structural interpretation.",
            "reframed_problem": "Structural interpretation remains premature because the case is not yet bounded enough to support a dominant contradiction.",
            "dominant_contradiction": "",
            "why_it_matters": inadmissibility_reason,
            "dominant_risk": "A structural thesis here would overstate what the system actually knows about the case.",
            "hidden_assumption_at_risk": "",
            "why_current_question_is_premature": inadmissibility_reason,
            "what_reality_feature_changes_the_decision": "",
            "capital_logic_if_assumption_holds": "",
            "capital_logic_if_assumption_breaks": "",
            "surprising_but_evidenced_takeaway": "",
            "what_is_admissible_now": [],
            "what_is_not_admissible": prohibited_actions,
            "minimum_discriminating_evidence": [],
            "minimum_discriminating_evidence_source": "",
            "minimum_discriminating_evidence_unlocks": [],
            "conditional_redesign": {},
            "evidence_state": "INADMISSIBLE_CLAIM",
            "report_mode": selected_mode,
            "confidence_level": "inadmissible",
            "top_dominant_variables": [],
            "top_scenarios": [],
            "top_actions": [],
            "dominant_lens": "",
            "supporting_modes": [],
            "primary_financial_exposure": {},
            "primary_peer_comparison": {},
            "dominant_operational_misunderstanding": "",
            "hidden_system_boundary_error": "",
            "invalid_comparison_risk": "",
            "dominant_loss_logic": "",
            "measurement_minimality_take": "",
            "regulatory_physics_take": "",
            "finance_to_physics_take": "",
            "maintenance_reality_take": "",
            "top_gold_nuggets": [],
            "gold_nugget_source_register": _text(strategic_gold_nugget_source_register),
            "gold_nugget_authority_state": _text(strategic_gold_nugget_authority_state) or "legacy_primary_skill_shadow",
            "gold_nugget_strength_register": [],
            "evidence_pack_register": [],
            "thesis_constellation_register": [],
            "correlation_constellation_register": [],
            "congruence_action_priority_register": [],
            "interpretive_signal_register": [],
            "dominant_contradiction_selection_basis": {},
            "thesis_ranked_conflict_register": [],
            "rejected_contradiction_candidates": [],
            "governed_claim_contract_register": congruence_claim_contract_register,
            "governed_claim_contract_count": len(congruence_claim_contract_register),
            "thesis_state": "inadmissible_thesis",
            "local_thesis_state": "inadmissible_local_closure",
            "local_claim_closure_state": "blocked",
            "conditional_intelligence_available": False,
            "conditional_intelligence_reason": "",
            "inadmissibility_reason": inadmissibility_reason,
            "compression_targets": {
                "max_dominant_variables": 0,
                "max_primary_scenarios": 0,
                "max_primary_actions": 0,
                "max_primary_redesign_paths": 0,
                "max_primary_evidence_packs": 0,
            },
        }
    hidden_assumption_at_risk = _hidden_assumption_at_risk(subject_family, dominant_contradiction)
    dominant_operational_misunderstanding = _dominant_operational_misunderstanding(
        invalid_problem_frame_register=invalid_problem_frame_register,
        strategic_gold_nugget_register=strategic_gold_nugget_register,
    )
    hidden_system_boundary_error = _hidden_system_boundary_error(
        cross_layer_congruence_register=cross_layer_congruence_register,
        invalid_comparison_risk_register=invalid_comparison_risk_register,
        finance_physics_dependency_register=finance_physics_dependency_register,
    )
    invalid_comparison_risk = _invalid_comparison_risk_take(invalid_comparison_risk_register)
    dominant_loss_logic = _dominant_loss_logic_take(
        loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
        maintenance_reality_register=maintenance_reality_register,
        strategic_gold_nugget_register=strategic_gold_nugget_register,
    )
    measurement_minimality_take = _measurement_minimality_take(measurement_strategy_register)
    regulatory_physics_take = _regulatory_physics_take(regulatory_physics_register)
    finance_to_physics_take = _finance_to_physics_take(finance_physics_dependency_register)
    maintenance_reality_take = _maintenance_reality_take(maintenance_reality_register)
    evidence_pack_register = _build_evidence_pack_register(
        minimum_discriminating_evidence=minimum_discriminating_evidence,
        minimum_evidence_source=_text(primary_minimum_evidence.get("source"))
        or _text(canonical_problem_frame.get("minimum_evidence_source")),
        minimum_evidence_unlocks=_list_text(primary_minimum_evidence.get("unlocks"))
        or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks")),
        invalid_comparison_risk_register=invalid_comparison_risk_register,
        finance_physics_dependency_register=finance_physics_dependency_register,
        loss_pattern_hypothesis_register=loss_pattern_hypothesis_register,
        effective_primary_problem=effective_primary_problem,
    )
    interpretive_signal_register = _interpretive_signal_register(
        subject_family=subject_family,
        dominant_contradiction=dominant_contradiction,
        evidence_state=evidence_state,
        primary_problem=effective_primary_problem,
        primary_financial=primary_financial,
        primary_redesign=primary_redesign,
        primary_peer=primary_peer,
        minimum_discriminating_evidence=minimum_discriminating_evidence,
    )
    thesis_constellation_register = _build_thesis_constellation_register(
        primary_conflict=primary_conflict,
        ranked_conflicts=ranked_conflicts,
        top_variables=top_variables,
        invalid_comparison_risk=invalid_comparison_risk,
        dominant_loss_logic=dominant_loss_logic,
        hidden_system_boundary_error=hidden_system_boundary_error,
        top_gold_nuggets=selected_top_gold_nuggets,
        evidence_pack_register=evidence_pack_register,
    )
    correlation_constellation_register = _build_correlation_constellation_register(
        ranked_conflicts,
    )
    return {
        "declared_problem": _text(effective_primary_problem.get("stated_problem"))
        or _text(canonical_problem_frame.get("stated_problem")),
        "reframed_problem": _text(effective_primary_problem.get("reframed_problem"))
        or _text(canonical_problem_frame.get("reframed_problem")),
        "dominant_contradiction": dominant_contradiction,
        "why_it_matters": why_it_matters,
        "dominant_risk": dominant_risk,
        "hidden_assumption_at_risk": hidden_assumption_at_risk,
        "why_current_question_is_premature": _join_sentences(
            _why_current_question_is_premature(
                subject_family,
                dominant_contradiction,
                minimum_discriminating_evidence,
            ),
            measurement_minimality_take,
        ),
        "what_reality_feature_changes_the_decision": _what_reality_feature_changes_the_decision(
            subject_family,
            dominant_contradiction,
        ),
        "capital_logic_if_assumption_holds": _join_sentences(
            _capital_logic_if_assumption_holds(
                subject_family,
                primary_redesign,
                primary_financial,
            ),
            finance_to_physics_take,
        ),
        "capital_logic_if_assumption_breaks": _capital_logic_if_assumption_breaks(
            subject_family,
            primary_financial,
            primary_redesign,
        ),
        "surprising_but_evidenced_takeaway": _surprising_takeaway(
            subject_family=subject_family,
            interpretive_signal_register=interpretive_signal_register,
            hidden_assumption_at_risk=hidden_assumption_at_risk,
            dominant_contradiction=dominant_contradiction,
        ),
        "dominant_operational_misunderstanding": dominant_operational_misunderstanding,
        "hidden_system_boundary_error": hidden_system_boundary_error,
        "invalid_comparison_risk": invalid_comparison_risk,
        "dominant_loss_logic": dominant_loss_logic,
        "measurement_minimality_take": measurement_minimality_take,
        "regulatory_physics_take": regulatory_physics_take,
        "finance_to_physics_take": finance_to_physics_take,
        "maintenance_reality_take": maintenance_reality_take,
        "top_gold_nuggets": selected_top_gold_nuggets,
        "gold_nugget_source_register": _text(strategic_gold_nugget_source_register),
        "gold_nugget_authority_state": _text(strategic_gold_nugget_authority_state) or "legacy_primary_skill_shadow",
        "gold_nugget_strength_register": gold_nugget_strength_register[:8],
        "evidence_pack_register": evidence_pack_register,
        "thesis_constellation_register": thesis_constellation_register,
        "correlation_constellation_register": correlation_constellation_register,
        "what_is_admissible_now": what_is_admissible_now,
        "what_is_not_admissible": prohibited_actions,
        "minimum_discriminating_evidence": minimum_discriminating_evidence,
        "minimum_discriminating_evidence_source": _text(primary_minimum_evidence.get("source"))
        or _text(canonical_problem_frame.get("minimum_evidence_source")),
        "minimum_discriminating_evidence_unlocks": _list_text(primary_minimum_evidence.get("unlocks"))
        or _list_text(canonical_problem_frame.get("minimum_evidence_unlocks")),
        "conditional_redesign": primary_redesign,
        "evidence_state": evidence_state,
        "report_mode": selected_mode,
        "confidence_level": _confidence_level(evidence_state),
        "top_dominant_variables": top_variables,
        "top_scenarios": top_scenarios,
        "top_actions": top_actions,
        "dominant_lens": dominant_contradiction,
        "supporting_modes": supporting_modes,
        "primary_financial_exposure": primary_financial,
        "primary_peer_comparison": primary_peer,
        "congruence_action_priority_register": congruence_action_priority_register[:5],
        "governed_claim_contract_register": congruence_claim_contract_register,
        "governed_claim_contract_count": len(congruence_claim_contract_register),
        "interpretive_signal_register": interpretive_signal_register,
        "dominant_contradiction_selection_basis": dict(primary_conflict.get("selection_basis", {}) or {}),
        "thesis_ranked_conflict_register": ranked_conflicts,
        "rejected_contradiction_candidates": ranked_conflicts[1:],
        "thesis_state": "admissible_structural_thesis",
        "local_thesis_state": "admissible_local_structural_closure",
        "local_claim_closure_state": "admissible",
        "conditional_intelligence_available": False,
        "conditional_intelligence_reason": "",
        "inadmissibility_reason": "",
        "compression_targets": {
            "max_dominant_variables": 4,
            "max_primary_scenarios": 3,
            "max_primary_actions": 4,
            "max_primary_redesign_paths": 2,
            "max_primary_evidence_packs": 3,
        },
    }
