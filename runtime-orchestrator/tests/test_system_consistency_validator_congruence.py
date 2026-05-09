from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

from runtime_orchestrator.adapters.motor_036 import Motor036Adapter
from runtime_orchestrator.structural_intelligence import CANONICAL_EVIDENCE_LAYERS

_BASE_VALIDATOR_TEST_PATH = Path(__file__).with_name("test_system_consistency_validator.py")
_BASE_VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "test_system_consistency_validator_base",
    _BASE_VALIDATOR_TEST_PATH,
)
assert _BASE_VALIDATOR_SPEC and _BASE_VALIDATOR_SPEC.loader
_BASE_VALIDATOR_MODULE = importlib.util.module_from_spec(_BASE_VALIDATOR_SPEC)
_BASE_VALIDATOR_SPEC.loader.exec_module(_BASE_VALIDATOR_MODULE)
_report_package = _BASE_VALIDATOR_MODULE._report_package


def _claim_contract(claim_id: str, statement: str, *, evidence_state: str = "CONDITIONAL_HYPOTHESIS") -> dict:
    return {
        "claim_id": claim_id,
        "statement": statement,
        "evidence_state": evidence_state,
        "supporting_sources": ["ll84::site"],
        "assumptions": ["Bounded screening interpretation only."],
        "falsification_condition": "Contrary boundary, schedule, or control evidence overturns this bounded reading.",
        "minimum_evidence_required": ["bounded minimum evidence"],
        "allowed_use": ["screening-grade structural interpretation"],
        "prohibited_use": ["ROI, savings, or compliance closure"],
    }


def _statement_trace(
    section_id: str,
    section_title: str,
    claim_id: str,
    contract_map: dict[str, dict],
    *,
    excerpt: str,
) -> dict:
    contract = contract_map[claim_id]
    return {
        "section_id": section_id,
        "section_title": section_title,
        "section_surface": "body",
        "block_id": f"{section_id}:block-1",
        "claim_id": claim_id,
        "visible_statement_excerpt": excerpt,
        "statement": contract["statement"],
        "evidence_state": contract["evidence_state"],
        "supporting_sources": list(contract["supporting_sources"]),
        "assumptions": list(contract["assumptions"]),
        "falsification_condition": contract["falsification_condition"],
        "minimum_evidence_required": list(contract["minimum_evidence_required"]),
        "allowed_use": list(contract["allowed_use"]),
        "prohibited_use": list(contract["prohibited_use"]),
        "permission": "conditional",
    }


def _canonical_output_mode_classifier_rows(selected_mode: str) -> list[dict]:
    canonical_modes = [
        "Target Classification Brief",
        "Decision-Blocked Asset Brief",
        "Exploratory Prior Brief",
        "Compliance / Investment Screening Brief",
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
        "Full Technical Decision Intelligence Report",
    ]
    rows: list[dict] = []
    for mode in canonical_modes:
        rows.append(
            {
                "canonical_output_mode": mode,
                "visible_output_mode": mode,
                "selected_for_publication": mode == selected_mode,
                "classification_state": "selected_primary_default" if mode == selected_mode else "available_non_selected",
            }
        )
    return rows


def _evidence_state_by_layer_register() -> list[dict]:
    return [
        {
            "layer": layer,
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "dominant_open_questions": f"Bound the dominant {layer} dependency before acting.",
            "observed_support": ["bounded public support"],
            "structural_risk_if_wrong": f"The case can be misread if the {layer} layer is interpreted too early.",
        }
        for layer in CANONICAL_EVIDENCE_LAYERS
    ]


def _base_inputs() -> dict:
    document_type = "Compliance / Investment Screening Brief"
    claim_contract_register = [
        _claim_contract(
            "compliance_screening_claim",
            "Public records support bounded compliance and investment screening, but not closure or retrofit economics.",
        ),
        _claim_contract(
            "financial_exposure_claim",
            "Owner economics remain exposed if the regulated boundary and the controllable load boundary do not match.",
        ),
        _claim_contract(
            "dominant_variables_claim",
            "Control boundary, schedule, and metering visibility dominate interpretation before retrofit logic.",
        ),
        _claim_contract(
            "scenario_space_claim",
            "The main scenarios depend on whether owner-controlled systems or tenant-driven loads dominate realized economics.",
        ),
        _claim_contract(
            "minimum_evidence_claim",
            "Tenant metering, utility bills, and lease responsibility are the minimum evidence needed to discriminate the case.",
        ),
    ]
    evidence_state_by_layer_register = _evidence_state_by_layer_register()
    report_package = _report_package(
        "Executive structural thesis present.",
        "Operational identity bounded.",
        "ROI remains prohibited.",
        document_type,
        source_family_coverage_table=[
            {
                "source_name": "NYC LL84",
                "found": True,
                "scope": "ASSET_LEVEL",
                "fields_extracted": ["current_EUI"],
            }
        ],
        extra_appendix_sections=[
            {
                "title": "Public Source Coverage Table",
                "chapter_id": "A8",
                "blocks": [{"content": "Bounded public source coverage is active."}],
            },
            {
                "title": "Report Type Classifier Table",
                "chapter_id": "A9",
                "blocks": [{"content": "Canonical output-mode classifier remains bounded and complete."}],
            },
        ],
        claim_contract_register=claim_contract_register,
    )
    report_package["claim_contract_register"] = list(claim_contract_register)
    report_package["executive_thesis"].update(
        {
            "dominant_operational_misunderstanding": "The visible question may be premature: high building energy means owner retrofit opportunity.",
            "hidden_system_boundary_error": "The hidden system-boundary error is assuming that the burdened actor and the controllable load boundary are the same thing.",
            "invalid_comparison_risk": "This comparison remains structurally invalid until owner / tenant control boundary, tenant metering map, schedule context are normalized.",
            "dominant_loss_logic": "The dominant hidden loss may be governance and metering opacity rather than pure technical inefficiency.",
            "measurement_minimality_take": "The next best discriminator is utility bills + tenant metering map + lease responsibility matrix, not broader sensor deployment.",
            "regulatory_physics_take": "NYC benchmarking and building performance obligations: Owner-facing compliance logic attaches to whole-building performance and can collide with unresolved tenant or control boundaries.",
            "finance_to_physics_take": "Owner economics track whole-building performance pressure only holds if owner control over the dominant covered load and schedule boundary.",
            "maintenance_reality_take": "Maintenance proof remains a decision-relevant gap because condition, scheduling and controls maintenance can change whether the visible issue is technical waste or governance drift.",
        }
    )
    report_package["main_report_outline"]["compression_state"] = "thesis_compressed"
    report_package["main_report_outline"]["congruence_visible_signal_count"] = 4
    report_package["congruence_visibility_register"] = [
        {
            "field_name": "measurement_minimality_take",
            "section_key": "minimum_evidence",
            "section_title": "Minimum Evidence for Discrimination",
            "visibility_state": "body_embedded_existing_section",
            "reason": "Measurement logic stays in the evidence section.",
        }
    ]
    report_package["compression_decision_log"] = [
        {
            "decision_type": "congruence_selective_promotion",
            "visible_congruence_signal_count": 4,
            "visible_congruence_fields": [
                "dominant_operational_misunderstanding",
                "invalid_comparison_risk",
                "measurement_minimality_take",
                "finance_to_physics_take",
            ],
            "reason": "Only thesis-relevant congruence signals are embedded into existing sections.",
        }
    ]
    report_package["body_to_appendix_justification_map"] = {
        "Minimum Evidence for Discrimination": ["Congruence Technical Registers"],
    }
    report_package.setdefault("structural_intelligence_registers", {})[
        "evidence_state_by_layer_register"
    ] = list(evidence_state_by_layer_register)

    contract_map = {row["claim_id"]: row for row in claim_contract_register}
    section_map = {
        str(section.get("title", "")).strip(): str(section.get("chapter_id", "")).strip()
        for section in (
            list(report_package["approved_views"]["report_view"]["body_sections"])
            + list(report_package["approved_views"]["report_view"]["appendix_sections"])
        )
    }
    report_package["section_claim_trace_register"].extend(
        [
            _statement_trace(
                section_map["Dominant Variables"],
                "Dominant Variables",
                "dominant_variables_claim",
                contract_map,
                excerpt="Control boundary, schedule, and metering visibility dominate interpretation before retrofit logic.",
            ),
            _statement_trace(
                section_map["Scenario Space"],
                "Scenario Space",
                "scenario_space_claim",
                contract_map,
                excerpt="The main scenarios depend on whether owner-controlled systems or tenant-driven loads dominate realized economics.",
            ),
            _statement_trace(
                section_map["Financial Exposure Under Uncertainty"],
                "Financial Exposure Under Uncertainty",
                "financial_exposure_claim",
                contract_map,
                excerpt="Owner economics remain exposed if the regulated boundary and the controllable load boundary do not match.",
            ),
            _statement_trace(
                section_map["Minimum Evidence for Discrimination"],
                "Minimum Evidence for Discrimination",
                "minimum_evidence_claim",
                contract_map,
                excerpt="Tenant metering, utility bills, and lease responsibility are the minimum evidence needed to discriminate the case.",
            ),
        ]
    )

    return {
        "motor_012": {
            "facility_prior": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "jurisdiction_scope": ["US-NY-NYC"],
                }
            },
            "asset_field_register": [
                {
                    "field": "address",
                    "value": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
                    "status": "OBSERVED",
                    "scope": "ASSET_LEVEL",
                }
            ],
            "dataset_coverage_register": [
                {"dataset_key": "nyc_pluto", "status": "accepted"},
                {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted"},
                {"dataset_key": "nyc_ll97_emissions", "status": "accepted"},
                {"dataset_key": "nyc_dob_permits", "status": "accepted"},
                {"dataset_key": "nyc_dof_property_record", "status": "accepted"},
            ],
        },
        "motor_014": {
            "claim_permission_register": [],
            "claim_permission_summary": {},
            "scenario_evidence_link_register": [
                {
                    "scenario": "owner-controlled systems dominate",
                    "financial_meaning": "Owner-side optimization remains economically material.",
                    "falsification_condition": "Tenant-driven load and lease evidence dominate the realized economics.",
                    "linked_evidence_item": "tenant metering map",
                }
            ],
        },
        "motor_016": {"report_package": report_package},
        "motor_028": {
            "source_register": [
                {
                    "source_id": "ll84::site",
                    "source_family": "benchmarking_disclosure_record",
                    "title": "LL84",
                    "accepted": True,
                }
            ]
        },
        "motor_033": {"decision_front_actions": [], "expanded_structural_tad_action_register": []},
        "motor_034": {
            "report_type_classifier_table": [],
            "report_output_mode_classifier_table": _canonical_output_mode_classifier_rows(document_type),
            "structural_output_mode_classifier_table": [],
            "structural_output_mode_summary": {},
            "canonical_problem_frame": {
                "leading_structural_output_mode": "Compliance / Investment Screening Brief",
            },
            "claim_permission_register": [],
            "claim_contract_register": list(claim_contract_register),
            "structural_claim_permission_register": [],
        },
        "motor_037": {"system_abstraction": {"asset_type": {"statement": "commercial building"}}},
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
                    "hypothesis": "Tenant-driven loads dominate realized economics.",
                    "if_confirmed": "Control-boundary redesign precedes owner-side CAPEX.",
                    "if_falsified": "Owner-controlled systems move back to the front of the queue.",
                    "next_evidence": ["tenant metering map", "lease responsibility matrix"],
                }
            ]
        },
        "motor_045": {
            "structural_financial_exposure_register": [
                {
                    "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                }
            ],
            "evidence_state_by_layer_register": list(evidence_state_by_layer_register),
        },
        "motor_046": {
            "minimum_evidence_for_discrimination_register": [
                {
                    "rival_hypotheses": ["owner-controlled load", "tenant-driven load"],
                    "minimum_evidence": "bounded minimum evidence",
                    "what_it_confirms": "Which boundary dominates the economics.",
                    "what_it_falsifies": "A premature owner-only retrofit framing.",
                }
            ]
        },
        "motor_049": {
            "asset_family_research_profile": {
                "asset_family": "commercial_building",
                "route_state": "operational_asset_candidate",
                "research_mode": "public_only_screening",
            },
            "local_evidence_binding_register": [
                {
                    "research_claim": "Owner / tenant control boundary may dominate the economics of any efficiency or compliance pathway.",
                    "current_local_binding_state": "public_context_only_unbound",
                }
            ],
        },
        "motor_051": {
            "invalid_problem_frame_register": [
                {
                    "apparent_problem": "high_building_energy_means_owner_retrofit_opportunity",
                    "why_invalid_or_premature": "The unresolved issue may be control boundary and owner economic capture.",
                }
            ],
            "invalid_comparison_risk_register": [
                {
                    "risk_name": "whole_building_owner_capturable_comparison",
                    "risk_level": "high",
                    "trigger": "Whole-building comparisons are structurally invalid if owner burden and controllable load are not normalized together.",
                    "required_normalization": ["owner / tenant control boundary", "tenant metering map", "schedule context"],
                }
            ],
        },
        "motor_052": {
            "measurement_strategy_register": [
                {
                    "hypothesis": "owner_vs_tenant_control_boundary_drives_the_case",
                    "minimum_measurement": "utility bills + tenant metering map + lease responsibility matrix",
                    "why": "The first discriminating question is boundary and economic capture, not extra sensing.",
                    "hardware_trigger": "No new hardware until document and metering-boundary evidence fail to discriminate the question.",
                }
            ],
            "hardware_minimality_register": [
                {
                    "data_need": "owner_vs_tenant_control_boundary_drives_the_case",
                    "cheapest_valid_source": "utility bills / tariff records",
                    "accuracy": "screening-grade",
                    "limitation": "Cannot localize subsystem behavior by itself.",
                    "upgrade_path": "Add interval data or temporary analyzer only if bills show a material tariff or demand question.",
                }
            ],
            "loss_pattern_hypothesis_register": [
                {
                    "pattern_name": "missing_control_boundary_visibility",
                    "pattern_class": "structural_pattern",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "hypothesis": "The dominant hidden loss may be governance and metering opacity rather than pure technical inefficiency.",
                    "allowed_language": "Plausible recurring pattern for this system family; must be locally falsified before diagnosis.",
                    "prohibited_language": "Do not state that the site has this loss as observed fact without local evidence.",
                }
            ],
            "maintenance_reality_register": [
                {
                    "reality_claim": "maintenance proof remains a decision-relevant gap",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_matters": "Condition, scheduling and controls maintenance can change whether the visible issue is technical waste or governance drift.",
                }
            ],
        },
        "motor_053": {
            "regulatory_physics_register": [
                {
                    "regulatory_signal": "NYC benchmarking and building performance obligations",
                    "physical_implication": "Owner-facing compliance logic attaches to whole-building performance and can collide with unresolved tenant or control boundaries.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "what_it_supports": ["screening-grade compliance context"],
                    "what_it_does_not_support": ["compliance closure", "proof of current operation"],
                }
            ],
            "finance_physics_dependency_register": [
                {
                    "financial_assumption": "owner economics track whole-building performance pressure",
                    "physical_dependency": "owner control over the dominant covered load and schedule boundary",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "risk_if_wrong": "Owner-side CAPEX can improve site metrics without improving owner-capturable economics.",
                    "evidence_needed": ["utility bills", "tenant metering map", "lease responsibility matrix", "central plant topology"],
                }
            ],
        },
        "motor_054": {
            "strategic_gold_nugget_register": [
                {
                    "nugget_id": "wrong_problem_frame",
                    "gold_nugget": "The visible question may be premature: high building energy means owner retrofit opportunity.",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "congruence_action_priority_register": [
                {
                    "strategic_action": "REQUEST_MINIMUM_EVIDENCE",
                    "status": "VALIDATE FIRST",
                    "why": "You may be solving the wrong problem before the system is bounded.",
                    "gold_nugget": "You may be solving the wrong problem before the system is bounded.",
                    "evidence_needed": ["tenant metering map", "lease responsibility matrix"],
                    "prohibited_action": "Do not invest yet against the visible symptom alone.",
                },
                {
                    "strategic_action": "MEASURE_ONLY_IF_MATERIAL",
                    "status": "VALIDATE FIRST",
                    "why": "The next best evidence may be cheaper and less invasive than expected.",
                    "gold_nugget": "The next best evidence may be cheaper and less invasive than expected.",
                    "evidence_needed": ["utility bills + tenant metering map + lease responsibility matrix"],
                    "prohibited_action": "No new hardware until document and metering-boundary evidence fail to discriminate the question.",
                },
            ],
            "congruence_claim_contract_register": [
                {
                    "claim_id": "congruence_invalid_comparison_claim",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
                {
                    "claim_id": "congruence_measurement_minimality_claim",
                    "evidence_state": "ARCHETYPAL_PRIOR",
                },
                {
                    "claim_id": "congruence_finance_physics_claim",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
                {
                    "claim_id": "congruence_gold_nugget_claim",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                },
            ],
        },
    }


def test_motor_036_accepts_bounded_congruence_lane():
    out = Motor036Adapter().run(_base_inputs())
    assert out["critical_failure_count"] == 0
    assert out["can_render_pdf"] is True


def test_motor_036_accepts_authoritative_gold_nugget_register_without_legacy_alias():
    inputs = deepcopy(_base_inputs())
    inputs["motor_054"]["authoritative_gold_nugget_register"] = list(
        inputs["motor_054"]["strategic_gold_nugget_register"]
    )
    inputs["motor_054"]["gold_nugget_authority_state"] = "skill_primary"
    inputs["motor_054"]["strategic_gold_nugget_register"] = []

    out = Motor036Adapter().run(inputs)
    assert out["critical_failure_count"] == 0
    assert out["can_render_pdf"] is True


def test_motor_036_blocks_invalid_comparison_as_peer_evidence():
    inputs = deepcopy(_base_inputs())
    inputs["motor_043"]["competitive_comparison_register"][0]["evidence_state"] = "OBSERVED_FACT"
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "invalid_comparison_not_used_as_peer_evidence" in failure_ids


def test_motor_036_blocks_measurement_recommendation_without_hypothesis():
    inputs = deepcopy(_base_inputs())
    inputs["motor_052"]["measurement_strategy_register"][0]["hypothesis"] = ""
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "measurement_recommendations_require_hypothesis" in failure_ids


def test_motor_036_blocks_premature_hardware_escalation():
    inputs = deepcopy(_base_inputs())
    inputs["motor_052"]["hardware_minimality_register"][0]["cheapest_valid_source"] = "temporary analyzer"
    inputs["motor_052"]["hardware_minimality_register"][0]["upgrade_path"] = "Install permanent monitoring immediately."
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "hardware_recommendations_follow_cheapest_valid_source_path" in failure_ids


def test_motor_036_blocks_loss_pattern_as_local_fact():
    inputs = deepcopy(_base_inputs())
    inputs["motor_052"]["loss_pattern_hypothesis_register"][0]["evidence_state"] = "OBSERVED_FACT"
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "loss_patterns_not_presented_as_local_fact" in failure_ids


def test_motor_036_blocks_permit_signal_as_operational_proof():
    inputs = deepcopy(_base_inputs())
    inputs["motor_053"]["regulatory_physics_register"][0]["what_it_does_not_support"] = []
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "permit_signal_not_treated_as_operational_proof" in failure_ids


def test_motor_036_blocks_finance_claim_without_physical_dependency():
    inputs = deepcopy(_base_inputs())
    inputs["motor_053"]["finance_physics_dependency_register"][0]["physical_dependency"] = ""
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "finance_claims_bind_to_physical_dependency" in failure_ids


def test_motor_036_blocks_research_claims_without_binding_discipline():
    inputs = deepcopy(_base_inputs())
    inputs["motor_049"]["local_evidence_binding_register"] = [{"research_claim": "Owner / tenant control boundary may dominate the economics."}]
    inputs["motor_054"]["congruence_claim_contract_register"][0]["evidence_state"] = "OBSERVED_FACT"
    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["critical_failures"]}
    assert "research_derived_claims_respect_local_binding" in failure_ids
