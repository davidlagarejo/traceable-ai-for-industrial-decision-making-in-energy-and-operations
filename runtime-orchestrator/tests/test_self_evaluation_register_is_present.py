from __future__ import annotations

from runtime_orchestrator.adapters.motor_024 import Motor024Adapter
from runtime_orchestrator.models import PipelineRun
from runtime_orchestrator.pipeline_orchestrator import PipelineOrchestrator


def test_motor_024_emits_phase_self_evaluation_register_and_summary():
    out = Motor024Adapter().run(
        {
            "__pipeline__": {"case_id": "ZLab-test-self-eval"},
            "motor_001": {},
            "motor_002": {},
            "motor_007": {
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "target_classification_object": {"target_type": "OPERATING_ASSET"},
                "target_definition_contract": {"target_name": "One Vanderbilt"},
            },
            "motor_009": {},
            "motor_028": {
                "routing_plan_compliance": {
                    "routing_ready": True,
                    "total_routed_sources": 5,
                    "accepted_routed_sources": 4,
                    "mandatory_sources_missing_from_executor": [],
                }
            },
            "motor_012": {
                "asset_field_register": [
                    {
                        "field": "address",
                        "value": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                        "status": "OBSERVED",
                        "identity_supported": True,
                        "physical_substrate_supported": False,
                        "operating_substrate_supported": False,
                        "regulatory_supported": False,
                        "notes": "Source confirms identity only, not physical operating substrate.",
                    }
                ]
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "roi_scenario_claim", "current_permission": "prohibited"},
                ],
                "decision_permission_register": [],
                "cluster_report_readiness_profile": {"strong_public_screening_possible": True},
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                },
            },
            "motor_013": {},
            "motor_014": {
                "claim_permission_summary": {"allowed": 1, "conditional": 0, "prohibited": 1, "deferred": 0},
                "minimum_evidence_unlock_map": [
                    {
                        "evidence_item": "Utility bills and meter map",
                        "source": "owner / operator",
                        "why_needed": "Confirm owner-controllable energy basis.",
                        "unlocks": ["underwriting", "retrofit screening"],
                        "effort": "medium",
                        "priority": "high",
                    }
                ],
                "scenario_space": [
                    {
                        "scenario": "A. Owner-controllable energy upside exists only after tenant/control boundary confirmation.",
                        "financial_meaning": "Avoid unsupported underwriting uplift.",
                        "what_would_falsify_it": "Lease and metering evidence show tenant pass-through dominates.",
                        "evidence_needed": "Utility bills + meter map + lease control boundary",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "Utility bills and meter map",
                    }
                ],
                "financial_exposure_register": [
                    {
                        "assumption": "Owner-controllable energy upside exists",
                        "current_support": "unsupported until utility and control-boundary evidence arrive",
                        "downside_if_wrong": "Retrofit CAPEX fails to improve owner economics",
                        "evidence_needed": "Utility bills + meter map + lease control boundary",
                        "financial_consequence": "Remove energy upside from screening until validated",
                        "linked_decision_front": "Compliance investment",
                    }
                ],
            },
            "motor_019": {},
            "motor_020": {},
            "motor_015": {},
            "motor_016": {
                "report_package": {
                    "context_integrity_scan": {"render_eligible": True},
                    "case_adaptation_memo": {
                        "rows": [{"dimension": "asset_type_logic"}],
                        "substantive_dimension_count": 6,
                        "required_dimension_count": 7,
                        "template_contamination_failure": False,
                        "failure_reasons": [],
                    },
                }
            },
            "motor_017": {},
            "motor_027": {},
            "motor_033": {
                "tad_preliminary": {
                    "decision_front_actions": [
                        {"decision_front": "Compliance investment", "current_status": "VALIDATE FIRST"},
                        {"decision_front": "Seller / operator evidence request", "current_status": "ACT NOW"},
                    ]
                }
            },
        }
    )

    register = out["phase_self_evaluation_register"]
    assert register["summary"]["total_phases"] >= 8
    assert register["summary"]["overall_result"] in {"resolved", "partially_resolved", "unresolved"}
    for row in register["rows"]:
        assert set(row) == {"phase", "change_implemented", "test_run", "result", "remaining_gap"}
        assert row["result"] in {"resolved", "partially_resolved", "unresolved"}
    assert out["pipeline_health_summary"]["phase_self_evaluation_summary"]["overall_result"] == register["summary"]["overall_result"]


def test_pipeline_orchestrator_refreshes_phase_self_evaluation_summary(orchestrator):
    run = PipelineRun(
        run_id="run:test-self-eval",
        pipeline_id="test-self-eval",
        started_at="2026-04-29T00:00:00+00:00",
    )
    orchestrator._refresh_run_semantics(
        run,
        {
            "motor_025": {
                "report_type_trace": {
                    "early_report_type_gate": "Decision-Blocked Asset Brief",
                    "maturity_refined_report_type": "Compliance / Investment Screening Brief",
                    "final_published_report_type": "Compliance / Investment Screening Brief",
                    "report_type_override_reason": "Strong public screening evidence supports a higher report class.",
                }
            },
            "motor_024": {
                "phase_self_evaluation_register": {
                    "summary": {
                        "overall_result": "partially_resolved",
                        "resolved": 5,
                        "partially_resolved": 3,
                        "unresolved": 1,
                    }
                }
            }
        },
    )
    assert run.phase_self_evaluation_summary["overall_result"] == "partially_resolved"
    assert run.to_dict()["phase_self_evaluation_summary"]["resolved"] == 5
    assert run.report_type_trace["final_published_report_type"] == "Compliance / Investment Screening Brief"
