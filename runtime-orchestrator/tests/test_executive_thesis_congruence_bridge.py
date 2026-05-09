from __future__ import annotations

from runtime_orchestrator.adapters.motor_047 import Motor047Adapter


def _one_vanderbilt_bridge_inputs() -> dict:
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
                },
                {
                    "canonical_output_mode": "Structural Contradiction Brief",
                    "selected_for_publication": False,
                    "classification_state": "eligible_primary_structural",
                },
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
                },
                {
                    "variable": "tenant metering opacity",
                    "layer": "metering",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_could_matter": "Without it, whole-building logic can mislead the owner.",
                    "decision_impact": "Changes whether the benchmark is decision-useful.",
                },
            ]
        },
        "motor_040": {
            "cross_layer_conflict_register": [
                {
                    "conflict": "Regulation vs control boundary",
                    "why_it_matters": "Owner-facing compliance pressure can be mistaken for owner-capturable economics.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "selection_basis": {"total_rank_score": 9},
                },
                {
                    "conflict": "Benchmark signal vs owner economics",
                    "why_it_matters": "A benchmark can support screening without supporting ROI.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "selection_basis": {"total_rank_score": 7},
                },
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
            "authoritative_gold_nugget_register": [
                {
                    "nugget_id": "wrong_problem_frame",
                    "gold_nugget": "The visible question may be premature: high building energy means owner retrofit opportunity.",
                },
                {
                    "nugget_id": "wrong_benchmark_basis",
                    "gold_nugget": "The benchmark can be structurally invalid even when it looks intuitively relevant.",
                },
                {
                    "nugget_id": "wrong_capital_target",
                    "gold_nugget": "The capital target may be wrong even if the technical symptom is real.",
                },
                {
                    "nugget_id": "wrong_measurement_instinct",
                    "gold_nugget": "The next best measurement may be a bill, map or log, not a new sensor.",
                },
            ],
            "gold_nugget_authority_state": "skill_primary",
            "strategic_gold_nugget_register": [
                {
                    "nugget_id": "wrong_problem_frame",
                    "gold_nugget": "LEGACY SHOULD NOT WIN WHEN AUTHORITATIVE NUGGETS ARE PRESENT.",
                },
                {
                    "nugget_id": "wrong_benchmark_basis",
                    "gold_nugget": "The benchmark can be structurally invalid even when it looks intuitively relevant.",
                },
                {
                    "nugget_id": "wrong_capital_target",
                    "gold_nugget": "The capital target may be wrong even if the technical symptom is real.",
                },
                {
                    "nugget_id": "wrong_measurement_instinct",
                    "gold_nugget": "The next best measurement may be a bill, map or log, not a new sensor.",
                },
            ],
            "congruence_action_priority_register": [
                {
                    "strategic_action": "REQUEST_MINIMUM_EVIDENCE",
                    "status": "VALIDATE FIRST",
                    "why": "You may be solving the wrong problem before the system is bounded.",
                    "gold_nugget": "You may be solving the wrong problem before the system is bounded.",
                    "evidence_needed": ["tenant metering map", "lease responsibility matrix", "utility bills", "LL97 filing basis"],
                    "prohibited_action": "Do not invest yet against the visible symptom alone.",
                },
                {
                    "strategic_action": "REQUEST_FAIR_PEER_SET",
                    "status": "COMPARE FAIRLY",
                    "why": "Whole-building comparisons are structurally invalid if owner burden and controllable load are not normalized together.",
                    "gold_nugget": "A benchmark can be structurally invalid before any performance claim is made.",
                    "evidence_needed": ["owner / tenant control boundary", "tenant metering map", "schedule context"],
                    "prohibited_action": "Do not claim peer superiority or infer local waste from an invalid comparison.",
                },
            ],
        },
    }


def _inadmissible_inputs() -> dict:
    return {
        "motor_034": {
            "canonical_problem_frame": {
                "stated_problem": "Need bounded target understanding before structural interpretation.",
                "reframed_problem": "",
                "dominant_conflict": "",
                "reasoning_path": "legacy_decision_gating_only",
                "problem_frame_active": False,
            },
            "claim_contract_register": [],
            "report_output_mode_classifier_table": [
                {
                    "canonical_output_mode": "Target Classification Brief",
                    "selected_for_publication": True,
                    "classification_state": "selected_primary_default",
                }
            ],
        },
        "motor_037": {
            "system_abstraction": {
                "selected_archetype_id": "target_not_yet_structurally_modelable",
            }
        },
        "motor_038": {"dominant_variable_register": []},
        "motor_040": {"cross_layer_conflict_register": []},
        "motor_041": {"problem_framing_register": []},
        "motor_043": {"competitive_comparison_register": []},
        "motor_044": {"conditional_redesign_register": []},
        "motor_045": {"structural_financial_exposure_register": []},
        "motor_046": {"minimum_evidence_for_discrimination_register": []},
        "motor_014": {"scenario_space": []},
        "motor_033": {"expanded_structural_tad_action_register": []},
        "motor_051": {"invalid_problem_frame_register": [], "invalid_comparison_risk_register": [], "cross_layer_congruence_register": []},
        "motor_052": {"loss_pattern_hypothesis_register": [], "maintenance_reality_register": [], "measurement_strategy_register": []},
        "motor_053": {"regulatory_physics_register": [], "finance_physics_dependency_register": []},
        "motor_054": {"strategic_gold_nugget_register": [], "congruence_action_priority_register": []},
    }


def test_motor_047_enriches_the_thesis_with_congruence_specific_takes():
    out = Motor047Adapter().run(_one_vanderbilt_bridge_inputs())
    thesis = out["executive_thesis"]

    assert thesis["dominant_operational_misunderstanding"].startswith("The visible question may be premature")
    assert "boundary" in thesis["hidden_system_boundary_error"].lower()
    assert "structurally invalid" in thesis["invalid_comparison_risk"]
    assert "governance and metering opacity" in thesis["dominant_loss_logic"]
    assert "not broader sensor deployment" in thesis["measurement_minimality_take"]
    assert "Owner-facing compliance logic" in thesis["regulatory_physics_take"]
    assert "only holds if owner control over the dominant covered load and schedule boundary" in thesis["finance_to_physics_take"]
    assert "maintenance proof remains a decision-relevant gap" in thesis["maintenance_reality_take"].lower()
    assert "The next best discriminator is utility bills + tenant metering map + lease responsibility matrix" in thesis["why_current_question_is_premature"]
    assert thesis["gold_nugget_authority_state"] == "skill_primary"
    assert thesis["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert thesis["top_gold_nuggets"][0]["gold_nugget"].startswith("The visible question may be premature")
    assert len(thesis["congruence_action_priority_register"]) <= 5


def test_motor_047_keeps_inadmissible_cases_bounded_after_congruence_bridge():
    out = Motor047Adapter().run(_inadmissible_inputs())
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "inadmissible_thesis"
    assert thesis["dominant_operational_misunderstanding"] == ""
    assert thesis["hidden_system_boundary_error"] == ""
    assert thesis["invalid_comparison_risk"] == ""
    assert thesis["dominant_loss_logic"] == ""
    assert thesis["measurement_minimality_take"] == ""
    assert thesis["regulatory_physics_take"] == ""
    assert thesis["finance_to_physics_take"] == ""
    assert thesis["maintenance_reality_take"] == ""
    assert thesis["congruence_action_priority_register"] == []


def test_motor_047_emits_conditional_structural_intelligence_when_local_closure_is_blocked_but_strategic_signals_exist():
    inputs = _one_vanderbilt_bridge_inputs()
    inputs["motor_034"]["canonical_problem_frame"]["problem_frame_active"] = False
    inputs["motor_037"]["system_abstraction"]["selected_archetype_id"] = "target_not_yet_structurally_modelable"
    out = Motor047Adapter().run(inputs)
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "conditional_structural_intelligence"
    assert thesis["local_claim_closure_state"] == "blocked"
    assert thesis["conditional_intelligence_available"] is True
    assert thesis["dominant_contradiction"] == "Regulation vs control boundary"
    assert thesis["minimum_discriminating_evidence"]
    assert thesis["top_actions"]
    assert "owner controls the dominant covered load" in thesis["reframed_problem"].lower()


def test_motor_047_uses_congruence_actions_when_structural_tad_is_empty():
    inputs = _one_vanderbilt_bridge_inputs()
    inputs["motor_033"] = {"expanded_structural_tad_action_register": []}
    out = Motor047Adapter().run(inputs)
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["top_actions"]
    assert thesis["top_actions"][0]["action"] == "Request Minimum Evidence"
    assert thesis["what_is_admissible_now"][0] == "Request Minimum Evidence"
    assert "tenant metering map" in thesis["top_actions"][0]["maps_to"]
    assert "utility bills" in thesis["top_actions"][0]["maps_to"]


def test_motor_047_emits_hidden_system_boundary_error_for_logistics_style_invalid_comparison():
    inputs = {
        "motor_014": {"scenario_space": []},
        "motor_033": {"expanded_structural_tad_action_register": []},
        "motor_034": {
            "canonical_problem_frame": {
                "stated_problem": "high energy per area means warehouse inefficiency",
                "reframed_problem": "Which operational intensity variable defines a fair comparison basis.",
                "dominant_conflict": "Area benchmark vs service-level complexity",
                "minimum_evidence_to_discriminate": "service-level proxy + dock activity profile + charging schedule",
                "minimum_evidence_source": "case-specific evidence request",
                "problem_frame_active": True,
                "reasoning_path": "structural_first",
                "leading_structural_output_mode": "System Redesign Hypothesis Brief",
            },
            "claim_contract_register": [],
            "report_output_mode_classifier_table": [
                {
                    "canonical_output_mode": "Exploratory Prior Brief",
                    "selected_for_publication": True,
                    "classification_state": "selected_primary_default",
                }
            ],
        },
        "motor_037": {
            "system_abstraction": {
                "selected_archetype_id": "logistics_warehouse_generic",
                "asset_type": {"statement": "warehouse distribution"},
                "dominant_process_type": {"statement": "warehouse movement and dispatch"},
            }
        },
        "motor_038": {
            "dominant_variable_register": [
                {
                    "variable": "owner_control_boundary",
                    "layer": "control",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_could_matter": "Boundary determines whether the cost signal is comparable.",
                    "decision_impact": "Fair comparison and CAPEX timing.",
                }
            ]
        },
        "motor_040": {"cross_layer_conflict_register": []},
        "motor_041": {
            "problem_framing_register": [
                {
                    "stated_problem": "high energy per area means warehouse inefficiency",
                    "reframed_problem": "Which operational intensity variable defines a fair comparison basis.",
                    "strategic_risk": "Area-only logic can target the wrong cost driver.",
                }
            ]
        },
        "motor_043": {"competitive_comparison_register": []},
        "motor_044": {"conditional_redesign_register": []},
        "motor_045": {"structural_financial_exposure_register": []},
        "motor_046": {
            "minimum_evidence_for_discrimination_register": [
                {
                    "minimum_evidence": "service-level proxy + dock activity profile + charging schedule",
                    "source": "case-specific evidence request",
                    "unlocks": ["better-bounded next question"],
                }
            ]
        },
        "motor_051": {
            "invalid_problem_frame_register": [
                {
                    "apparent_problem": "high_energy_per_area_means_warehouse_inefficiency",
                    "why_invalid_or_premature": "Service level and movement intensity may dominate the comparison.",
                    "what_problem_should_be_tested_instead": "Which operational intensity variable defines a fair comparison basis.",
                    "evidence_needed": ["service-level proxy", "dock activity profile", "charging schedule"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "invalid_comparison_risk_register": [
                {
                    "trigger": "Area-based comparison is invalid before operational intensity is normalized.",
                    "required_normalization": ["service level", "throughput proxy", "dock activity profile", "charging schedule"],
                }
            ],
            "cross_layer_congruence_register": [
                {
                    "contradiction": "Area benchmark vs service-level complexity",
                    "layers": ["benchmarking", "operation", "logistics"],
                    "strategic_risk": "Area-only logic can hide the real operational driver.",
                    "evidence_needed": ["service-level proxy", "dock activity profile", "charging schedule"],
                    "possible_redesign": "Normalize operational intensity before diagnosing inefficiency.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
        },
        "motor_052": {"loss_pattern_hypothesis_register": [], "maintenance_reality_register": [], "measurement_strategy_register": []},
        "motor_053": {"regulatory_physics_register": [], "finance_physics_dependency_register": []},
        "motor_054": {"strategic_gold_nugget_register": [], "congruence_action_priority_register": []},
    }

    out = Motor047Adapter().run(inputs)
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["hidden_system_boundary_error"] != ""
    assert "boundary" in thesis["hidden_system_boundary_error"].lower()


def test_motor_047_emits_hidden_system_boundary_error_for_infrastructure_style_invalid_comparison():
    inputs = {
        "motor_014": {"scenario_space": []},
        "motor_033": {"expanded_structural_tad_action_register": []},
        "motor_034": {
            "canonical_problem_frame": {
                "stated_problem": "high node energy automatically means waste",
                "reframed_problem": "Which continuity or dispatch variable actually defines the fair comparison and cost boundary.",
                "dominant_conflict": "Energy average vs service continuity burden",
                "minimum_evidence_to_discriminate": "service continuity profile + dispatch burden proxy + redundancy class + utility bills and tariff structure",
                "minimum_evidence_source": "case-specific evidence request",
                "problem_frame_active": True,
                "reasoning_path": "structural_first",
                "leading_structural_output_mode": "Exploratory Prior Brief",
            },
            "claim_contract_register": [],
            "report_output_mode_classifier_table": [
                {
                    "canonical_output_mode": "Exploratory Prior Brief",
                    "selected_for_publication": True,
                    "classification_state": "selected_primary_default",
                }
            ],
        },
        "motor_037": {
            "system_abstraction": {
                "selected_archetype_id": "infrastructure_node_generic",
                "asset_type": {"statement": "infrastructure node"},
                "dominant_process_type": {"statement": "power continuity and dispatch"},
            }
        },
        "motor_038": {"dominant_variable_register": []},
        "motor_040": {"cross_layer_conflict_register": []},
        "motor_041": {
            "problem_framing_register": [
                {
                    "stated_problem": "high node energy automatically means waste",
                    "reframed_problem": "Which continuity or dispatch variable actually defines the fair comparison and cost boundary.",
                    "strategic_risk": "Average-energy framing can target the wrong economic boundary.",
                }
            ]
        },
        "motor_043": {"competitive_comparison_register": []},
        "motor_044": {"conditional_redesign_register": []},
        "motor_045": {"structural_financial_exposure_register": []},
        "motor_046": {
            "minimum_evidence_for_discrimination_register": [
                {
                    "minimum_evidence": "service continuity profile + dispatch burden proxy + redundancy class + utility bills and tariff structure",
                    "source": "case-specific evidence request",
                    "unlocks": ["bounded node economics"],
                }
            ]
        },
        "motor_051": {
            "invalid_problem_frame_register": [
                {
                    "apparent_problem": "high_node_energy_automatically_means_waste",
                    "why_invalid_or_premature": "The dominant driver may be service continuity burden, dispatch duty, redundancy class or tariff structure rather than avoidable waste.",
                    "what_problem_should_be_tested_instead": "Which continuity or dispatch variable actually defines the fair comparison and cost boundary.",
                    "evidence_needed": ["service continuity profile", "dispatch burden proxy", "redundancy class", "utility bills and tariff structure"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "invalid_comparison_risk_register": [
                {
                    "trigger": "Average-energy comparison is invalid before continuity burden is normalized.",
                    "required_normalization": ["service continuity", "dispatch burden", "redundancy class", "demand structure"],
                }
            ],
            "cross_layer_congruence_register": [
                {
                    "contradiction": "Energy average vs service continuity burden",
                    "layers": ["benchmarking", "operation", "continuity"],
                    "strategic_risk": "Average-energy framing can label continuity duty or redundancy burden as waste before the node-level service obligation is normalized.",
                    "evidence_needed": ["service continuity profile", "dispatch burden proxy", "redundancy class", "utility bills and tariff structure"],
                    "possible_redesign": "Normalize continuity and dispatch burden before diagnosing inefficiency or sizing optimization CAPEX.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
        },
        "motor_052": {"loss_pattern_hypothesis_register": [], "maintenance_reality_register": [], "measurement_strategy_register": []},
        "motor_053": {
            "regulatory_physics_register": [],
            "finance_physics_dependency_register": [
                {
                    "financial_assumption": "headline energy or demand cost is the main economic problem",
                    "physical_dependency": "service continuity burden, dispatch duty and redundancy class must not be the real drivers of the visible cost structure",
                    "risk_if_wrong": "Optimization capital can target a secondary utility symptom while the real economic boundary remains uptime, continuity or constrained dispatch.",
                    "evidence_needed": ["utility bills", "tariff structure", "service continuity or dispatch logs", "equipment inventory"],
                }
            ],
        },
        "motor_054": {"strategic_gold_nugget_register": [], "congruence_action_priority_register": []},
    }

    out = Motor047Adapter().run(inputs)
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["hidden_system_boundary_error"] != ""
    assert "continuity" in thesis["hidden_system_boundary_error"].lower() or "boundary" in thesis["hidden_system_boundary_error"].lower()
    assert thesis["interpretive_signal_register"]
    assert thesis["interpretive_signal_register"][0]["signal_type"] == "continuity_boundary_confusion"


def test_motor_047_emits_utility_heavy_interpretive_signals_for_demand_structure_case():
    inputs = {
        "motor_014": {"scenario_space": []},
        "motor_033": {"expanded_structural_tad_action_register": []},
        "motor_034": {
            "canonical_problem_frame": {
                "stated_problem": "high site consumption automatically means the main utility opportunity is generic efficiency",
                "reframed_problem": "Which demand, PF, sequencing or support-system variable actually defines the cost boundary.",
                "dominant_conflict": "Consumption framing vs demand-structure reality",
                "minimum_evidence_to_discriminate": "utility bills with demand or PF charges + tariff structure + major motor inventory + support-duty schedule",
                "minimum_evidence_source": "case-specific evidence request",
                "problem_frame_active": True,
                "reasoning_path": "structural_first",
                "leading_structural_output_mode": "Exploratory Prior Brief",
            },
            "claim_contract_register": [],
            "report_output_mode_classifier_table": [
                {
                    "canonical_output_mode": "Exploratory Prior Brief",
                    "selected_for_publication": True,
                    "classification_state": "selected_primary_default",
                }
            ],
        },
        "motor_037": {
            "system_abstraction": {
                "selected_archetype_id": "utility_heavy_site_generic",
                "asset_type": {"statement": "utility_heavy_site"},
                "dominant_process_type": {"statement": "support-utility generation, motive-power duty and distribution support"},
            }
        },
        "motor_038": {"dominant_variable_register": []},
        "motor_040": {"cross_layer_conflict_register": []},
        "motor_041": {
            "problem_framing_register": [
                {
                    "stated_problem": "high site consumption automatically means the main utility opportunity is generic efficiency",
                    "reframed_problem": "Which demand, PF, sequencing or support-system variable actually defines the cost boundary.",
                    "strategic_risk": "Consumption framing can target the wrong utility boundary.",
                }
            ]
        },
        "motor_043": {"competitive_comparison_register": []},
        "motor_044": {"conditional_redesign_register": []},
        "motor_045": {"structural_financial_exposure_register": []},
        "motor_046": {
            "minimum_evidence_for_discrimination_register": [
                {
                    "minimum_evidence": "utility bills with demand or PF charges + tariff structure + major motor inventory + support-duty schedule",
                    "source": "case-specific evidence request",
                    "unlocks": ["bounded utility-heavy economics"],
                }
            ]
        },
        "motor_051": {
            "invalid_problem_frame_register": [
                {
                    "apparent_problem": "high_site_consumption_automatically_means_main_utility_opportunity",
                    "why_invalid_or_premature": "The dominant driver may be demand structure, PF or reactive exposure, support-system duty or sequencing rather than total consumption alone.",
                    "what_problem_should_be_tested_instead": "Which demand, PF, sequencing or support-system variable actually defines the cost boundary.",
                    "evidence_needed": ["utility bills with demand or PF charges", "tariff structure", "major motor inventory", "support-duty schedule"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "invalid_comparison_risk_register": [
                {
                    "trigger": "Consumption-only framing is invalid before demand and support-duty structure are normalized.",
                    "required_normalization": ["demand structure", "PF exposure", "support-duty schedule", "major motor inventory"],
                }
            ],
            "cross_layer_congruence_register": [
                {
                    "contradiction": "Consumption framing vs demand-structure reality",
                    "layers": ["finance", "tariff", "physics"],
                    "strategic_risk": "Aggregate-consumption framing can miss that demand peaks, PF or reactive structure, and support-system sequencing are the real economic boundary.",
                    "evidence_needed": ["utility bills with demand or PF charges", "tariff structure", "major motor inventory", "interval demand profile"],
                    "possible_redesign": "Discriminate demand, PF and sequencing logic before broad consumption-reduction CAPEX.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
        },
        "motor_052": {"loss_pattern_hypothesis_register": [], "maintenance_reality_register": [], "measurement_strategy_register": []},
        "motor_053": {
            "regulatory_physics_register": [],
            "finance_physics_dependency_register": [
                {
                    "financial_assumption": "headline energy cost is the main economic problem",
                    "physical_dependency": "cost must be driven by controllable support-system loss rather than demand structure or support-system duty",
                    "risk_if_wrong": "Capital can chase kWh reduction while the actual cost driver remains demand, PF or unstable support-duty behavior.",
                    "evidence_needed": ["utility bills", "tariff structure", "major motor inventory", "support-duty schedule"],
                }
            ],
        },
        "motor_054": {"strategic_gold_nugget_register": [], "congruence_action_priority_register": []},
    }

    out = Motor047Adapter().run(inputs)
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["interpretive_signal_register"]
    assert thesis["interpretive_signal_register"][0]["signal_type"] == "false_consumption_priority"
    assert "demand" in thesis["hidden_assumption_at_risk"].lower()
    assert "support-system" in thesis["surprising_but_evidenced_takeaway"].lower() or "demand-structure" in thesis["surprising_but_evidenced_takeaway"].lower()
