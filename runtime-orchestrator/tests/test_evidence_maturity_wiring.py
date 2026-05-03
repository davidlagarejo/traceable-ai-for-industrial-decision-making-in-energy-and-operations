from __future__ import annotations

from runtime_orchestrator.adapters.motor_019 import Motor019Adapter
from runtime_orchestrator.adapters.motor_024 import Motor024Adapter
from runtime_orchestrator.adapters.motor_025 import Motor025Adapter
from runtime_orchestrator.adapters import motor_019 as motor_019_module


def test_motor_025_holds_report_when_maturity_layer_prohibits_current_identity():
    out = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_034": {
                "claim_permission_register": [
                    {
                        "claim_name": "roi_scenario_claim",
                        "current_permission": "prohibited",
                    }
                ],
                "decision_permission_register": [],
                "report_readiness_register": {
                    "report_type_allowed": ["Entity Address Classification Brief"],
                    "report_type_prohibited": ["Decision-Blocked Asset Brief"],
                    "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                },
            },
            "motor_022": {"__stub__": True},
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "claim_permission_block_count": 1,
                    "key_variable_bottlenecks": ["utility_bills"],
                    "report_readiness_allowed": ["Entity Address Classification Brief"],
                    "report_readiness_prohibited": ["Decision-Blocked Asset Brief"],
                    "report_readiness_reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )

    report_state = out["epistemic_status_register"]["report_package"]
    pdf_state = out["epistemic_status_register"]["pdf_output"]
    assert report_state["publication_state"] == "hold_for_validation"
    assert pdf_state["publication_state"] == "hold_for_validation"
    assert "report_package" in out["blocked_outputs"]
    assert out["report_readiness_reason"] == "Critical variable bottlenecks keep the case below normal technical-report maturity."
    assert any(
        "evidence-maturity readiness ceiling" in trigger.lower()
        for trigger in report_state["downgrade_triggers"]
    )


def test_motor_025_refines_bounded_asset_identity_to_screening_brief_when_readiness_allows_it():
    out = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_034": {
                "claim_permission_register": [],
                "decision_permission_register": [],
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Strong public asset-level identity, geometry, and regulatory evidence support screening-grade use.",
                },
            },
            "motor_022": {"__stub__": True},
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": [
                        "Asset Context Insufficiency Brief",
                        "Pre-Verification Asset Brief",
                        "Decision-Blocked Asset Brief",
                        "Exploratory Prior Brief",
                        "Compliance / Investment Screening Brief",
                    ],
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "recommended_report_type": "Decision-Blocked Asset Brief",
                    "report_readiness_allowed": ["Compliance / Investment Screening Brief"],
                    "report_readiness_prohibited": ["Full Technical Decision Intelligence Report"],
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )

    assert out["report_identity_state"] == "Compliance / Investment Screening Brief"
    assert out["recommended_report_type"] == "Compliance / Investment Screening Brief"


def test_motor_025_refines_operable_bounded_asset_identity_to_exploratory_prior_when_full_technical_is_not_ready():
    out = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_034": {
                "claim_permission_register": [],
                "decision_permission_register": [],
                "report_readiness_register": {
                    "report_type_allowed": ["Exploratory Prior Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                },
            },
            "motor_022": {"__stub__": True},
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "target_admissibility_state": "bounded_asset_with_operable_context",
                    "allowed_report_classes": [
                        "Decision-Blocked Asset Brief",
                        "Exploratory Prior Brief",
                        "Compliance / Investment Screening Brief",
                        "Full Technical Decision Intelligence Report",
                    ],
                    "report_identity_state": "Full Technical Decision Intelligence Report",
                    "recommended_report_type": "Full Technical Decision Intelligence Report",
                    "report_readiness_allowed": ["Exploratory Prior Brief"],
                    "report_readiness_prohibited": ["Full Technical Decision Intelligence Report"],
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )

    assert out["report_identity_state"] == "Exploratory Prior Brief"
    assert out["recommended_report_type"] == "Exploratory Prior Brief"


def test_motor_025_holds_report_when_mandatory_routed_source_was_not_executed():
    out = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_034": {"claim_permission_register": [], "decision_permission_register": [], "report_readiness_register": {}},
            "motor_022": {"__stub__": True},
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "mandatory_source_gap_count": 1,
                    "mandatory_sources_missing_from_executor": ["nyc_dof_property_record"],
                    "routing_plan_gate_passed": False,
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )

    report_state = out["epistemic_status_register"]["report_package"]
    pdf_state = out["epistemic_status_register"]["pdf_output"]
    assert report_state["publication_state"] == "hold_for_validation"
    assert pdf_state["publication_state"] == "hold_for_validation"
    assert out["mandatory_source_gap_count"] == 1
    assert out["mandatory_sources_missing_from_executor"] == ["nyc_dof_property_record"]
    assert any(
        "mandatory routed public sources were not executed" in trigger.lower()
        for trigger in report_state["downgrade_triggers"]
    )


def test_motor_024_registers_critical_report_preflight_failures():
    out = Motor024Adapter().run(
        {
            "motor_001": {},
            "motor_002": {},
            "motor_007": {},
            "motor_009": {},
            "motor_028": {},
            "motor_012": {},
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "roi_scenario_claim", "current_permission": "prohibited"},
                ],
                "decision_permission_register": [],
                "report_readiness_register": {},
            },
            "motor_013": {},
            "motor_014": {
                "claim_permission_summary": {"allowed": 0, "conditional": 0, "prohibited": 1, "deferred": 0},
                "minimum_evidence_unlock_map": [
                    {"evidence_item": "Process line, utility, and controls system inventory"},
                    {"evidence_item": "Process line inventory and major energy-using equipment list"},
                ],
                "scenario_space": [
                    {
                        "scenario": "A. Process load is structural",
                        "financial_meaning": "",
                        "what_would_falsify_it": "",
                        "evidence_needed": "",
                    }
                ],
            },
            "motor_019": {},
            "motor_020": {},
            "motor_015": {},
            "motor_016": {
                "report_package": {
                    "context_integrity_scan": {
                        "render_eligible": False,
                        "scan_status": "blocked",
                        "issue_count": 2,
                    }
                }
            },
            "motor_017": {},
            "motor_027": {},
            "motor_033": {},
        }
    )

    preflight = out["report_preflight_register"]
    assert not preflight["passed"]
    assert preflight["critical_failure_count"] >= 3
    failed = {row["check"] for row in preflight["critical_failures"]}
    assert "claim_permission_counts_match" in failed
    assert "claim_permission_contract_complete" in failed
    assert "scenario_contract_complete" in failed
    assert "minimum_evidence_pack_deduped" in failed
    assert "context_integrity_render_eligible" in failed
    assert "case_adaptation_memo_present" in failed
    assert not out["pipeline_health_summary"]["report_preflight_passed"]


def test_motor_025_holds_report_when_report_preflight_fails():
    out = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_034": {"claim_permission_register": [], "decision_permission_register": [], "report_readiness_register": {}},
            "motor_022": {"__stub__": True},
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "source_quality_gate_passed": True,
                    "final_report_ready": False,
                    "traceability_chain_complete": True,
                    "report_preflight_passed": False,
                    "report_preflight_critical_failure_count": 2,
                    "report_preflight_failures": [
                        {"check": "claim_permission_counts_match"},
                        {"check": "scenario_contract_complete"},
                    ],
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )

    report_state = out["epistemic_status_register"]["report_package"]
    pdf_state = out["epistemic_status_register"]["pdf_output"]
    assert report_state["publication_state"] == "hold_for_validation"
    assert pdf_state["publication_state"] == "hold_for_validation"
    assert not out["report_preflight_passed"]
    assert out["report_preflight_critical_failure_count"] == 2
    assert any(
        "preflight" in trigger.lower()
        for trigger in report_state["downgrade_triggers"]
    )


def test_motor_024_flags_template_contamination_failure_from_case_adaptation_memo():
    out = Motor024Adapter().run(
        {
            "motor_001": {},
            "motor_002": {},
            "motor_007": {},
            "motor_009": {},
            "motor_028": {},
            "motor_012": {},
            "motor_034": {"claim_permission_register": [], "decision_permission_register": [], "report_readiness_register": {}},
            "motor_013": {},
            "motor_014": {"claim_permission_summary": {}, "minimum_evidence_unlock_map": [], "scenario_space": []},
            "motor_019": {},
            "motor_020": {},
            "motor_015": {},
            "motor_016": {
                "report_package": {
                    "context_integrity_scan": {"render_eligible": True, "scan_status": "passed", "issue_count": 0},
                    "case_adaptation_memo": {
                        "rows": [{"dimension": "asset_type_logic"}],
                        "substantive_dimension_count": 1,
                        "required_dimension_count": 6,
                        "template_contamination_failure": True,
                        "failure_reasons": ["Case adaptation memo does not cover enough critical adaptation dimensions."],
                    },
                }
            },
            "motor_017": {},
            "motor_027": {},
            "motor_033": {},
        }
    )

    preflight = out["report_preflight_register"]
    assert not preflight["passed"]
    assert preflight["case_adaptation_summary"]["template_contamination_failure"]
    failed = {row["check"] for row in preflight["critical_failures"]}
    assert "template_contamination_failure" in failed


def test_motor_024_flags_literal_lint_and_wrong_context_hits_from_context_integrity_scan():
    out = Motor024Adapter().run(
        {
            "motor_001": {},
            "motor_002": {},
            "motor_007": {},
            "motor_009": {},
            "motor_028": {},
            "motor_012": {},
            "motor_034": {"claim_permission_register": [], "decision_permission_register": [], "report_readiness_register": {}},
            "motor_013": {},
            "motor_014": {"claim_permission_summary": {}, "minimum_evidence_unlock_map": [], "scenario_space": []},
            "motor_019": {},
            "motor_020": {},
            "motor_015": {},
            "motor_016": {
                "report_package": {
                    "context_integrity_scan": {
                        "render_eligible": False,
                        "scan_status": "blocked",
                        "issue_count": 4,
                        "issues": [
                            {"issue_code": "instruction_leakage_prose", "section_id": "c1"},
                            {"issue_code": "invalid_zero_gfa", "section_id": "c2"},
                            {"issue_code": "legacy_ll97_reference", "section_id": "c5"},
                            {"issue_code": "legacy_prologis_reference", "section_id": "c1"},
                        ],
                    },
                    "case_adaptation_memo": {
                        "rows": [{"dimension": "asset_type_logic"}],
                        "substantive_dimension_count": 6,
                        "required_dimension_count": 6,
                        "template_contamination_failure": False,
                        "failure_reasons": [],
                    },
                }
            },
            "motor_017": {},
            "motor_027": {},
            "motor_033": {},
        }
    )

    preflight = out["report_preflight_register"]
    assert not preflight["passed"]
    failed = {row["check"] for row in preflight["critical_failures"]}
    assert "critical_context_issue_codes_clear" in failed
    assert "literal_instruction_leakage_clear" in failed
    assert "factual_blank_or_zero_field_leakage_clear" in failed
    assert "wrong_asset_or_jurisdiction_or_regulation_clear" in failed


def test_motor_024_flags_internal_render_scaffolding_from_context_integrity_scan():
    out = Motor024Adapter().run(
        {
            "motor_001": {},
            "motor_002": {},
            "motor_007": {},
            "motor_009": {},
            "motor_028": {},
            "motor_012": {},
            "motor_034": {"claim_permission_register": [], "decision_permission_register": [], "report_readiness_register": {}},
            "motor_013": {},
            "motor_014": {"claim_permission_summary": {}, "minimum_evidence_unlock_map": [], "scenario_space": []},
            "motor_019": {},
            "motor_020": {},
            "motor_015": {},
            "motor_016": {
                "report_package": {
                    "context_integrity_scan": {
                        "render_eligible": False,
                        "scan_status": "blocked",
                        "issue_count": 4,
                        "issues": [
                            {"issue_code": "instruction_leakage_reader_takeaway", "section_id": "c1"},
                            {"issue_code": "instruction_leakage_technical_reference_data", "section_id": "c3"},
                            {"issue_code": "instruction_leakage_epistemic_marker", "section_id": "c6"},
                            {"issue_code": "instruction_leakage_chapter_marker", "section_id": "a4"},
                        ],
                    },
                    "case_adaptation_memo": {
                        "rows": [{"dimension": "asset_type_logic"}],
                        "substantive_dimension_count": 6,
                        "required_dimension_count": 6,
                        "template_contamination_failure": False,
                        "failure_reasons": [],
                    },
                }
            },
            "motor_017": {},
            "motor_027": {},
            "motor_033": {},
        }
    )

    preflight = out["report_preflight_register"]
    assert not preflight["passed"]
    failed = {row["check"] for row in preflight["critical_failures"]}
    assert "literal_instruction_leakage_clear" in failed


def test_motor_019_exposes_maturity_constraints_in_section_packets(monkeypatch):
    monkeypatch.setattr(motor_019_module, "_codex_up", lambda: True)
    monkeypatch.setattr(
        motor_019_module,
        "_call_codex",
        lambda prompt, ctx, timeout=45: (
            '{"en":"Bounded section. Validation still governs advancement.","es":"Seccion acotada. La validacion sigue gobernando el avance."}',
            None,
        ),
    )

    out = Motor019Adapter().run(
        {
            "__pipeline__": {
                "facility_inputs": {
                    "input_01_location": {"address": "350 FIFTH AVENUE, NEW YORK, NY, 10118"},
                    "input_02_facility_type": {"primary_classification": "commercial_building"},
                    "input_03_sector": {"owner_name": "Empire State Realty Trust", "owner_ticker": "ESRT"},
                    "input_04_primary_use": {},
                    "input_05_size": {},
                    "input_06_vintage": {},
                    "input_09_known_systems": {},
                    "input_10_main_concern": {},
                }
            },
            "motor_001": {"subject_definition": {"subject_kind": "address_candidate"}},
            "motor_012": {
                "facility_prior": {
                    "target_definition": {"target_type": "commercial_building"},
                    "asset_context_readiness": "asset_context_insufficient",
                    "system_asset_hypotheses": [],
                    "operational_tension_hypotheses": [],
                    "regulatory_flag_bundle": {},
                    "benchmark_bundle": {},
                },
                "compliance_applicability_case": {},
            },
            "motor_014": {
                "inference_records": [],
                "conflict_register": [],
                "tension_records": [],
                "opportunity_candidates": [],
                "validation_queue": [],
                "next_best_questions": [],
                "composite_reading": {"decision_state": "Blocked pending minimum evidence."},
                "decision_front_register": [
                    {
                        "decision_front": "Energy retrofit CAPEX",
                        "current_status": "NO-GO",
                        "why": "Utility data missing.",
                        "required_evidence": "Utility bills and system inventory",
                        "admissible_action": "Request evidence",
                    }
                ],
                "minimum_evidence_unlock_map": [],
                "scenario_space": [
                    {
                        "scenario_name": "Asset cannot yet be technically characterized",
                        "plausibility_status": "currently_dominant",
                    }
                ],
                "asset_context_readiness_summary": {},
                "information_deficit_score": "HIGH",
                "claim_permission_register": [
                    {
                        "claim_name": "roi_scenario_claim",
                        "current_permission": "prohibited",
                        "reason_if_blocked": "utility_bills below required maturity",
                        "upgrade_path": ["12-24 months utility bills"],
                    }
                ],
                "decision_permission_register": [
                    {
                        "decision_name": "retrofit_capex",
                        "admissibility_state": "validate_first",
                        "current_variable_bottleneck": "utility_bills",
                        "allowed_action": "VALIDATE FIRST",
                        "evidence_needed": ["12-24 months utility bills"],
                    }
                ],
                "variable_maturity_register": [
                    {
                        "variable_name": "utility_bills",
                        "maturity_level": "L0",
                        "source_scope": "NOT_OBSERVED",
                        "authority_score": "none",
                        "uncertainty_reason": "Not observed",
                    },
                    {
                        "variable_name": "GFA",
                        "maturity_level": "L1",
                        "source_scope": "BENCHMARK_LEVEL",
                        "authority_score": "medium",
                        "uncertainty_reason": "Benchmark proxy only",
                    },
                ],
                "claim_permission_summary": {
                    "allowed_count": 0,
                    "conditional_count": 0,
                    "prohibited_count": 1,
                },
                "variable_bottleneck_register": [
                    {
                        "decision_name": "retrofit_capex",
                        "current_variable_bottleneck": "utility_bills",
                    }
                ],
                "report_readiness_register": {
                    "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                    "report_type_allowed": ["Decision-Blocked Asset Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                },
            },
            "motor_028": {
                "enriched_data": {
                    "financials": {},
                    "company_name": "Empire State Realty Trust",
                    "ticker": "ESRT",
                    "extended_sources": {},
                }
            },
            "motor_033": {"tad_preliminary": {"decision_front_actions": [], "recommended_posture": "validate_first"}},
            "motor_034": {
                "maturity_summary": {"key_bottlenecks": ["utility_bills", "GFA"]},
                "report_readiness_register": {
                    "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                    "report_type_allowed": ["Decision-Blocked Asset Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                },
            },
        }
    )

    exec_packet = next(packet for packet in out["section_packets"] if packet["section_id"] == "s01_exec_narrative")
    financial_packet = next(packet for packet in out["section_packets"] if packet["section_id"] == "s03_financial_narrative")

    assert exec_packet["source_facts"]["report_readiness_reason"] == "Critical variable bottlenecks keep the case below normal technical-report maturity."
    assert exec_packet["source_facts"]["blocked_claims"] == ["roi_scenario_claim"]
    assert exec_packet["source_facts"]["key_variable_bottlenecks"] == ["utility_bills", "GFA"]

    financial_claim_names = {
        row["claim_name"] for row in financial_packet["source_facts"]["financial_claim_permissions"]
    }
    assert "roi_scenario_claim" in financial_claim_names
    assert out["llm_governance_summary"]["blocked_claim_count"] == 1
