from __future__ import annotations

from runtime_orchestrator.adapters.motor_016 import Motor016Adapter


def test_motor_016_exposes_full_evidence_maturity_matrix_appendix():
    out = Motor016Adapter().run(
        {
            "__pipeline__": {
                "case_id": "ZLab-asset-commercial-building-one-vanderbilt-2026",
                "case_title": "One Vanderbilt",
                "case_subtitle": "Asset Decision-Admissibility Brief",
                "organization": "ZLab",
                "analyst": "Autonomous Decision System",
                "facility_inputs": {
                    "input_01_location": {"address": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017"},
                    "input_02_facility_type": {"primary_classification": "commercial_building"},
                    "input_03_sector": {"owner_name": "SL Green Realty Corp", "owner_ticker": "SLG", "exchange": "NYSE"},
                    "input_04_primary_use": {},
                    "input_05_size": {},
                    "input_06_vintage": {},
                    "input_09_known_systems": {},
                    "input_10_main_concern": {},
                },
            },
            "__runtime__": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "target_label": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                },
                "target_admissibility_state": "bounded_asset",
                "asset_context_readiness": "asset_context_partial",
                "report_identity_state": "Decision-Blocked Asset Brief",
                "recommended_report_type": "Decision-Blocked Asset Brief",
                "dominant_evidence_scope": "asset_level",
                "missing_observable_clusters": ["utility_bills", "HVAC_type"],
            },
            "motor_012": {
                "facility_prior": {
                    "entities": {},
                    "prior_assumptions_pack": [],
                    "uncertainty_markers": [],
                    "operational_tension_hypotheses": [],
                    "system_asset_hypotheses": [],
                },
                "evidence_lineage": {},
                "compliance_applicability_case": {
                    "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                },
            },
            "motor_014": {
                "decision_core_lineage": {},
                "inference_records": [],
                "tension_records": [],
                "conflict_register": [],
                "opportunity_candidates": [],
                "uncertainty_register": [],
                "evidence_gap_register": [],
                "validation_queue": [],
                "next_best_questions": [],
                "claim_permission_summary": {"allowed_count": 1, "conditional_count": 1, "prohibited_count": 1},
                "variable_bottleneck_register": [
                    {"decision_name": "compliance_investment", "current_variable_bottleneck": "compliance_filing"}
                ],
                "report_readiness_register": {
                    "report_type_allowed": ["Decision-Blocked Asset Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                },
                "variable_maturity_register": [
                    {
                        "variable_name": "GFA",
                        "variable_family": "physical",
                        "maturity_level": "L3",
                        "source_scope": "ASSET_LEVEL",
                        "evidence_source": "nyc_pluto_property::ova",
                        "authority_score": "high",
                        "uncertainty_reason": "Official NYC PLUTO record observed.",
                        "allowed_outputs": ["compliance screening", "area-normalized screening"],
                        "prohibited_outputs": ["verified savings"],
                        "decisions_unlocked": ["compliance_investment"],
                    },
                    {
                        "variable_name": "compliance_filing",
                        "variable_family": "regulatory",
                        "maturity_level": "L2",
                        "source_scope": "ASSET_LEVEL",
                        "evidence_source": "nyc_ll97_covered_buildings_list::ova",
                        "authority_score": "high",
                        "uncertainty_reason": "CBL + LL84 observed, but not certified LL97 filing.",
                        "allowed_outputs": ["compliance screening"],
                        "prohibited_outputs": ["compliance closure"],
                        "decisions_unlocked": [],
                    },
                ],
                "claim_permission_register": [
                    {
                        "claim_name": "ll97_penalty_screening_claim",
                        "current_permission": "allowed",
                        "reason_if_blocked": "",
                        "upgrade_path": [],
                    },
                    {
                        "claim_name": "compliance_closure_claim",
                        "current_permission": "prohibited",
                        "reason_if_blocked": "compliance_filing below required maturity",
                        "upgrade_path": ["Certified LL97 filing PDF or BEAM export"],
                    },
                ],
                "decision_permission_register": [
                    {
                        "decision_name": "compliance_investment",
                        "admissibility_state": "conditional",
                        "current_variable_bottleneck": "compliance_filing",
                        "allowed_action": "VALIDATE FIRST",
                        "evidence_needed": ["Certified LL97 filing PDF or BEAM export"],
                    }
                ],
            },
            "motor_015": {
                "output_blocks": [],
                "composite_reading": {"decision_state": "Blocked pending minimum evidence."},
                "facility_prior_id": "prior::ova",
                "traceability_register": {"block_traces": []},
            },
            "motor_018": {"chart_assets": [], "chart_errors": []},
            "motor_019": {"written_sections": [], "codex_available": False, "llm_governance_summary": {}},
            "motor_028": {
                "quality_gate_passed": True,
                "requestable_evidence_items": [],
                "enriched_data": {
                    "financials": {},
                    "extended_sources": {},
                    "benchmark_routing_register": {},
                    "source_scope_register": {},
                },
            },
            "motor_033": {"tad_preliminary": {"tad_action_plan": [], "posture_summary": {}}},
            "motor_034": {
                "maturity_summary": {
                    "counts_by_level": {"L0": 1, "L1": 0, "L2": 1, "L3": 1, "L4": 0},
                    "key_bottlenecks": ["compliance_filing"],
                },
                "report_readiness_register": {
                    "report_type_allowed": ["Decision-Blocked Asset Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                },
            },
        }
    )

    report_view = out["report_package"]["approved_views"]["report_view"]
    appendix = next(
        section
        for section in report_view["appendix_sections"]
        if section["title"] == "Evidence Maturity & Claim Permission Matrix"
    )
    content = appendix["blocks"][0]["content"]

    assert "REPORT READINESS" in content
    assert "VARIABLE MATURITY REGISTER" in content
    assert "CLAIM PERMISSION REGISTER" in content
    assert "DECISION PERMISSION REGISTER" in content
    assert "compliance_filing" in content
    assert "Certified LL97 filing PDF or BEAM export" in content
    assert out["report_package"]["evidence_maturity_registers"]["decision_permission_register"][0]["decision_name"] == "compliance_investment"


def test_motor_016_refines_visible_document_type_from_report_readiness_when_bounded_asset_is_screening_ready():
    out = Motor016Adapter().run(
        {
            "__pipeline__": {
                "case_id": "ZLab-asset-commercial-building-one-vanderbilt-2026",
                "case_title": "One Vanderbilt",
                "case_subtitle": "Asset Decision-Admissibility Brief",
                "organization": "ZLab",
                "analyst": "Autonomous Decision System",
                "facility_inputs": {
                    "input_01_location": {"address": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017"},
                    "input_02_facility_type": {"primary_classification": "commercial_building"},
                    "input_03_sector": {"owner_name": "SL Green Realty Corp", "owner_ticker": "SLG", "exchange": "NYSE"},
                    "input_04_primary_use": {},
                    "input_05_size": {},
                    "input_06_vintage": {},
                    "input_09_known_systems": {},
                    "input_10_main_concern": {},
                },
            },
            "__runtime__": {
                "target_definition": {
                    "target_type": "commercial_building",
                    "target_name": "One Vanderbilt",
                    "target_label": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                },
                "target_admissibility_state": "bounded_asset",
                "asset_context_readiness": "asset_context_minimal",
                "report_identity_state": "Decision-Blocked Asset Brief",
                "recommended_report_type": "Decision-Blocked Asset Brief",
                "dominant_evidence_scope": "asset_level",
                "missing_observable_clusters": ["utility_bills", "HVAC_type"],
            },
            "motor_012": {"facility_prior": {"entities": {}, "prior_assumptions_pack": [], "uncertainty_markers": [], "operational_tension_hypotheses": [], "system_asset_hypotheses": []}, "evidence_lineage": {}, "compliance_applicability_case": {}},
            "motor_014": {"decision_core_lineage": {}, "inference_records": [], "tension_records": [], "conflict_register": [], "opportunity_candidates": [], "uncertainty_register": [], "evidence_gap_register": [], "validation_queue": [], "next_best_questions": [], "claim_permission_summary": {}, "variable_bottleneck_register": [], "report_readiness_register": {"report_type_allowed": ["Compliance / Investment Screening Brief"], "report_type_prohibited": ["Full Technical Decision Intelligence Report"], "reason": "Strong public asset-level identity, geometry, and regulatory evidence support screening-grade use."}},
            "motor_015": {"output_blocks": [], "composite_reading": {"decision_state": "Screening-grade public evidence available."}, "facility_prior_id": "prior::ova", "traceability_register": {"block_traces": []}},
            "motor_018": {"chart_assets": [], "chart_errors": []},
            "motor_019": {"written_sections": [], "codex_available": False, "llm_governance_summary": {}},
            "motor_028": {"quality_gate_passed": True, "requestable_evidence_items": [], "enriched_data": {"financials": {}, "extended_sources": {}, "benchmark_routing_register": {}, "source_scope_register": {}}},
            "motor_033": {"tad_preliminary": {"tad_action_plan": [], "posture_summary": {}}},
            "motor_034": {
                "maturity_summary": {"counts_by_level": {"L0": 2, "L1": 0, "L2": 1, "L3": 3, "L4": 0}, "key_bottlenecks": ["utility_bills", "HVAC_type"]},
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                    "reason": "Strong public asset-level identity, geometry, and regulatory evidence support screening-grade use.",
                },
            },
        }
    )

    assert out["report_package"]["document_type"] == "Compliance / Investment Screening Brief"
