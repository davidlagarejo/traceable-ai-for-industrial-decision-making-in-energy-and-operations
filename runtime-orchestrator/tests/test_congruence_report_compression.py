from __future__ import annotations

from runtime_orchestrator.adapters.motor_047 import Motor047Adapter
from runtime_orchestrator.adapters.motor_048 import Motor048Adapter


def _bridge_inputs() -> dict:
    return {
        "motor_014": {
            "scenario_space": [
                {
                    "scenario": "Tenant-driven loads dominate realized economics.",
                    "financial_meaning": "Owner-only retrofit economics weaken.",
                    "evidence_needed": "Tenant metering map + utility bills",
                    "falsification_condition": "Owner-controlled central plant dominates load.",
                }
            ]
        },
        "motor_033": {
            "expanded_structural_tad_action_register": [
                {
                    "action": "Request discriminating evidence pack",
                    "status": "ACT NOW",
                    "why": "This evidence set discriminates the rival structural hypotheses with the highest value of information.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "financial_exposure": "Retrofit CAPEX may not improve owner economics.",
                    "evidence_needed": "Utility bills + tenant metering map + lease responsibility matrix + LL97 filing basis",
                    "prohibited_action": "Do not close ROI or savings claims yet.",
                    "linked_claim": "TAD_action_claim",
                }
            ]
        },
        "motor_034": {
            "canonical_problem_frame": {
                "stated_problem": "Should the owner treat One Vanderbilt as a retrofit-underwriting case?",
                "reframed_problem": "The real question is whether owner-managed base-building systems actually dominate the economic boundary that matters.",
                "dominant_conflict": "Regulation vs control boundary",
                "minimum_evidence_to_discriminate": "utility bills + tenant metering map + lease responsibility matrix + LL97 filing basis",
                "minimum_evidence_source": "structural_minimum_evidence_pack",
                "problem_frame_active": True,
                "reasoning_path": "structural_first",
                "leading_structural_output_mode": "Compliance / Investment Screening Brief",
            },
            "claim_contract_register": [
                {
                    "claim_id": "roi_claim",
                    "statement": "Do not state owner ROI before the value boundary is proven.",
                    "permission": "prohibited",
                }
            ],
            "report_output_mode_classifier_table": [
                {
                    "canonical_output_mode": "Compliance / Investment Screening Brief",
                    "selected_for_publication": True,
                    "classification_state": "selected_primary_default",
                }
            ],
        },
        "motor_037": {
            "system_abstraction": {
                "selected_archetype_id": "commercial_building_structural_screening",
                "asset_type": {"statement": "commercial building"},
                "dominant_process_type": {"statement": "tenant-served office tower"},
            }
        },
        "motor_038": {
            "dominant_variable_register": [
                {
                    "variable": "owner control over covered load boundary",
                    "layer": "control",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_could_matter": "Owner-capturable economics depend on it.",
                    "decision_impact": "Changes whether retrofit logic is admissible.",
                }
            ]
        },
        "motor_040": {
            "cross_layer_conflict_register": [
                {
                    "conflict": "Regulation vs control boundary",
                    "why_it_matters": "Owner-facing compliance pressure can be mistaken for owner-capturable economics.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "selection_basis": {"total_rank_score": 9},
                }
            ]
        },
        "motor_041": {
            "problem_framing_register": [
                {
                    "stated_problem": "Assess retrofit economics for the owner.",
                    "reframed_problem": "Prove whether the owner controls the dominant covered load and economic boundary before underwriting retrofit value.",
                    "strategic_risk": "The case can fund CAPEX on the wrong side of the value boundary.",
                    "why_original_framing_may_be_wrong": "Whole-building visibility does not prove owner-capturable control.",
                }
            ]
        },
        "motor_043": {
            "competitive_comparison_register": [
                {
                    "peer_type": "Archetypal peer pattern",
                    "evidence_state": "ARCHETYPAL_PRIOR",
                    "transferability": "conditional on comparable boundary and load control",
                }
            ]
        },
        "motor_044": {
            "conditional_redesign_register": [
                {
                    "redesign_direction": "control-boundary redesign and submetering-first sequencing",
                    "kill_condition": "Observed full owner control over the dominant covered loads.",
                    "if_falsified": "Owner-only retrofit CAPEX loses priority until the boundary is proven.",
                }
            ]
        },
        "motor_045": {
            "structural_financial_exposure_register": [
                {
                    "financial_exposure_if_wrong": "Retrofit CAPEX may reduce site energy without improving owner-capturable economics.",
                    "structural_assumption": "Owner-capturable value requires owner control over the dominant covered load boundary.",
                }
            ]
        },
        "motor_046": {
            "minimum_evidence_for_discrimination_register": [
                {
                    "minimum_evidence": "utility bills + tenant metering map + lease responsibility matrix + LL97 filing basis",
                    "source": "structural_minimum_evidence_pack",
                    "unlocks": ["owner-capturable logic", "bounded peer comparison"],
                }
            ]
        },
        "motor_051": {
            "invalid_problem_frame_register": [
                {
                    "apparent_problem": "high_building_energy_means_owner_retrofit_opportunity",
                    "why_invalid_or_premature": "The unresolved issue may be control boundary and owner economic capture, not aggregate whole-building energy alone.",
                    "what_problem_should_be_tested_instead": "Whether the owner controls the dominant covered load and economic boundary.",
                    "evidence_needed": ["tenant metering map", "lease responsibility matrix", "utility bills", "LL97 filing basis"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "invalid_comparison_risk_register": [
                {
                    "risk_name": "whole_building_owner_capturable_comparison",
                    "risk_level": "high",
                    "trigger": "Whole-building comparisons are structurally invalid if owner burden and controllable load are not normalized together.",
                    "required_normalization": ["owner / tenant control boundary", "tenant metering map", "schedule context"],
                    "asset_family": "commercial_building",
                }
            ],
            "cross_layer_congruence_register": [
                {
                    "contradiction": "Regulation vs control boundary",
                    "layers": ["regulation", "control", "finance"],
                    "strategic_risk": "Owner-facing compliance and capital pressure may be interpreted as owner-capturable savings before the controllable load boundary is observed.",
                    "evidence_needed": ["tenant metering map", "lease responsibility matrix", "LL97 filing basis"],
                    "possible_redesign": "Control-boundary redesign, submetering and lease architecture before owner-only retrofit logic.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
        },
        "motor_052": {
            "loss_pattern_hypothesis_register": [
                {
                    "pattern_name": "missing_control_boundary_visibility",
                    "hypothesis": "The dominant hidden loss may be governance and metering opacity rather than pure technical inefficiency.",
                }
            ],
            "maintenance_reality_register": [
                {
                    "reality_claim": "maintenance proof remains a decision-relevant gap",
                    "why_it_matters": "Condition, scheduling and controls maintenance can change whether the visible issue is technical waste or governance drift.",
                }
            ],
            "measurement_strategy_register": [
                {
                    "hypothesis": "owner_vs_tenant_control_boundary_drives_the_case",
                    "minimum_measurement": "utility bills + tenant metering map + lease responsibility matrix",
                    "why": "The first discriminating question is boundary and economic capture, not extra sensing.",
                    "hardware_trigger": "No new hardware until document and metering-boundary evidence fail to discriminate the question.",
                }
            ],
        },
        "motor_053": {
            "regulatory_physics_register": [
                {
                    "regulatory_signal": "NYC benchmarking and building performance obligations",
                    "physical_implication": "Owner-facing compliance logic attaches to whole-building performance and can collide with unresolved tenant or control boundaries.",
                }
            ],
            "finance_physics_dependency_register": [
                {
                    "financial_assumption": "owner economics track whole-building performance pressure",
                    "physical_dependency": "owner control over the dominant covered load and schedule boundary",
                    "risk_if_wrong": "Owner-side CAPEX can improve site metrics without improving owner-capturable economics.",
                    "evidence_needed": ["utility bills", "tenant metering map", "lease responsibility matrix", "central plant topology"],
                }
            ],
        },
        "motor_054": {
            "congruence_claim_contract_register": [
                {"claim_id": "congruence_invalid_comparison_claim"},
                {"claim_id": "congruence_measurement_minimality_claim"},
                {"claim_id": "congruence_finance_physics_claim"},
                {"claim_id": "congruence_gold_nugget_claim"},
                {"claim_id": "congruence_action_priority_claim"},
            ],
        },
    }


def test_motor_048_maps_congruence_signals_without_expanding_body():
    inputs = _bridge_inputs()
    m47 = Motor047Adapter().run(inputs)
    out = Motor048Adapter().run({**inputs, "motor_047": m47})

    outline = out["main_report_outline"]
    body_titles = set(outline["body_section_titles"])
    appendix_titles = {row["title"] for row in out["appendix_map"]}

    assert outline["max_primary_sections"] == 12
    assert len(outline["sections"]) == 12
    assert outline["congruence_visible_signal_count"] >= 4
    assert out["congruence_visibility_register"]
    assert all(row["section_title"] in body_titles for row in out["congruence_visibility_register"])
    assert "Congruence Technical Registers" in appendix_titles
    assert "Congruence Technical Registers" not in body_titles
    assert "motor_054.congruence_action_priority_register" in out["section_authority_map"]["minimum_evidence"]
    assert "motor_054.congruence_claim_contract_register" in out["section_authority_map"]["claim_permissions"]
    assert "congruence_invalid_comparison_claim" in out["deduplicated_claim_map"]["peer_comparison"]
    assert len(out["client_facing_tad"]["actions"]) <= 5


def test_motor_048_exposes_prompt_block_mapping_without_reopening_body():
    inputs = _bridge_inputs()
    m47 = Motor047Adapter().run(inputs)
    out = Motor048Adapter().run({**inputs, "motor_047": m47})

    mapping = out["prompt_block_mapping_register"]
    by_title = {row["prompt_block_title"]: row for row in mapping}

    assert len(mapping) == 23
    assert by_title["Executive Strategic Shock"]["mapped_section_title"] == "Executive Structural Thesis"
    assert by_title["Universal Process Map"]["coverage_state"] == "body_embedded_existing_section"
    assert by_title["Traceability"]["coverage_state"] == "appendix_support_register"
    assert by_title["Traceability"]["appendix_title"] == "Evidence & Source Traceability"
