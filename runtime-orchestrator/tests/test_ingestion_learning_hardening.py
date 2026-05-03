from __future__ import annotations

import json
from pathlib import Path

from runtime_orchestrator.adapters.motor_024 import Motor024Adapter
from runtime_orchestrator.ingestion_learning import (
    build_next_ingestion_priority_update,
    build_source_yield_memory,
)
from runtime_orchestrator.ingestion_learning_store import (
    load_pipeline_learning_summary,
    save_pipeline_learning_summary,
)
from runtime_orchestrator.models import PipelineRun, PipelineStatus
from runtime_orchestrator import pipeline_orchestrator as orchestrator_module


def _previous_run_summary() -> dict:
    return {
        "run_id": "run:prev",
        "pipeline_id": "ova-2026",
        "recommended_report_type": "Decision-Blocked Asset Brief",
        "report_type_trace": {
            "final_published_report_type": "Decision-Blocked Asset Brief",
        },
        "phase_self_evaluation_summary": {
            "overall_result": "unresolved",
        },
        "evidence_maturity_summary": {
            "cluster_levels": {
                "identity_cluster": "L2",
                "geometry_size_cluster": "L2",
                "regulatory_cluster": "L2",
            },
            "key_bottlenecks": ["systems_cluster", "utility_bills"],
        },
        "key_variable_bottlenecks": ["systems_cluster", "utility_bills"],
        "case_delta_summary": {
            "current_snapshot": {
                "mandatory_source_gaps": ["nyc_dob_permits"],
                "accepted_source_count": 1,
                "belief_revision_count": 2,
                "report_preflight_passed": False,
                "critical_preflight_failure_count": 1,
            }
        },
        "source_yield_memory_summary": {
            "by_source_family": {
                "nyc_pluto_property": {"yield_score": 1},
                "nyc_ll84_energy_benchmarking": {"yield_score": 0},
            },
            "productive_source_count": 1,
        },
        "ingestion_learning_summary": {
            "belief_revision_count": 2,
            "report_preflight_passed": False,
            "critical_preflight_failure_count": 1,
        },
    }


def _motor_024_inputs(previous_run_summary: dict | None = None) -> dict:
    return {
        "__pipeline__": {"case_id": "ZLab-ingestion-learning"},
        "__runtime__": {
            "run_id": "run:current",
            "pipeline_id": "ova-2026",
            "recommended_report_type": "Compliance / Investment Screening Brief",
            "report_type_trace": {
                "final_published_report_type": "Compliance / Investment Screening Brief",
            },
            "previous_run_summary": previous_run_summary or {},
        },
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
            "source_register": [
                {"source_type": "nyc_pluto_property", "accepted": True},
                {"source_type": "nyc_ll84_energy_benchmarking", "accepted": True},
            ],
            "routing_plan_compliance": {
                "routing_ready": True,
                "total_routed_sources": 3,
                "accepted_routed_sources": 2,
                "mandatory_sources_missing_from_executor": ["nyc_dob_permits"],
            },
            "source_family_coverage_table": [
                {
                    "source_family": "nyc_pluto_property",
                    "queried": True,
                    "found": True,
                    "authority": "high",
                    "scope": "asset_level",
                    "fields_extracted": ["GFA", "year_built"],
                    "missing": [],
                    "support_note": "Source contributed asset-level support for the listed fields.",
                },
                {
                    "source_family": "nyc_ll84_energy_benchmarking",
                    "queried": True,
                    "found": True,
                    "authority": "high",
                    "scope": "asset_level",
                    "fields_extracted": ["current_EUI"],
                    "missing": ["emissions"],
                    "support_note": "Source contributed asset-level support for the listed fields.",
                },
                {
                    "source_family": "nyc_dob_permits",
                    "queried": False,
                    "found": False,
                    "authority": "high",
                    "scope": "NOT_QUERIED",
                    "fields_extracted": [],
                    "missing": ["systems"],
                    "support_note": "Source required by routing plan but not executed by the current executor.",
                },
            ],
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
                {
                    "claim_name": "numeric_eui_claim",
                    "current_permission": "allowed",
                    "required_evidence": ["ll84 benchmark"],
                    "dependency_variables": ["current_EUI"],
                    "upgrade_path": [],
                },
                {
                    "claim_name": "roi_scenario_claim",
                    "current_permission": "prohibited",
                    "required_evidence": ["utility bills", "meter map"],
                    "dependency_variables": ["utility_bills", "control_boundary"],
                    "upgrade_path": [],
                },
            ],
            "decision_permission_register": [],
            "cluster_report_readiness_profile": {"strong_public_screening_possible": True},
            "report_readiness_register": {
                "report_type_allowed": ["Compliance / Investment Screening Brief"],
                "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
            },
            "maturity_summary": {
                "cluster_levels": {
                    "identity_cluster": "L3",
                    "geometry_size_cluster": "L3",
                    "regulatory_cluster": "L3",
                },
                "key_bottlenecks": ["utility_bills"],
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
                    "scenario": "A. Owner-controllable energy upside exists only after control-boundary confirmation.",
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
        "motor_020": {
            "belief_revision_register": [
                {
                    "case_id": "c1",
                    "case_name": "Compliance investment",
                    "recommended_action": "upgrade_candidate",
                }
            ]
        },
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


def test_motor_024_emits_ingestion_learning_registers():
    out = Motor024Adapter().run(_motor_024_inputs(_previous_run_summary()))

    assert out["case_delta_register"]["previous_run_id"] == "run:prev"
    assert out["case_delta_register"]["net_progress_state"] == "improved"
    assert "systems_cluster" in out["case_delta_register"]["blockers_removed"]
    assert "identity_cluster" in out["case_delta_register"]["clusters_upgraded"]

    source_yield = out["source_yield_memory_register"]["by_source_family"]
    assert source_yield["nyc_pluto_property"]["trend"] == "improved"
    assert source_yield["nyc_ll84_energy_benchmarking"]["yield_band"] in {"low", "medium"}

    priorities = out["next_ingestion_priority_update"]["priorities"]
    assert priorities[0]["action_type"] == "execute_missing_mandatory_source"
    assert priorities[0]["target"] == "nyc_dob_permits"
    assert out["ingestion_learning_register"]["summary"]["previous_run_id"] == "run:prev"
    assert out["pipeline_health_summary"]["next_ingestion_priority_count"] >= 1


def test_source_yield_memory_tracks_browser_and_static_modes() -> None:
    summary = build_source_yield_memory(
        [
            {
                "source_family": "dallas_building_permit_portal",
                "queried": True,
                "found": True,
                "authority": "high",
                "scope": "JURISDICTION_LEVEL",
                "fields_extracted": [],
                "missing": [],
                "support_note": "Portal context only.",
                "selected_acquisition_mode": "playwright_public_page",
                "static_probe_attempted": True,
                "static_usable": False,
                "static_render_mode": "shell_or_sparse",
                "browser_attempted": True,
                "browser_success": True,
                "browser_failure": False,
                "browser_attempt_status": "success",
                "browser_justified": True,
            },
            {
                "source_family": "harris_cad_property_search_portal",
                "queried": True,
                "found": True,
                "authority": "high",
                "scope": "JURISDICTION_LEVEL",
                "fields_extracted": [],
                "missing": [],
                "support_note": "Portal context only.",
                "selected_acquisition_mode": "playwright_public_page",
                "static_probe_attempted": True,
                "static_usable": False,
                "static_render_mode": "shell_or_sparse",
                "browser_attempted": True,
                "browser_success": False,
                "browser_failure": True,
                "browser_attempt_status": "failed",
                "browser_justified": True,
            },
        ],
        {
            "source_yield_memory_summary": {
                "source_acquisition_yield_memory": {
                    "by_source_family": {
                        "harris_cad_property_search_portal": {
                            "browser_failure_count": 1,
                            "browser_success_count": 0,
                            "static_failure_count": 1,
                            "recommended_acquisition_mode": "undecided",
                        }
                    }
                }
            }
        },
    )

    acquisition = summary["source_acquisition_yield_memory"]["by_source_family"]
    assert acquisition["dallas_building_permit_portal"]["recommended_acquisition_mode"] == "prefer_browser"
    assert acquisition["harris_cad_property_search_portal"]["recommended_acquisition_mode"] == "avoid_browser"
    assert summary["browser_justified_source_families"] == ["dallas_building_permit_portal"]
    assert summary["browser_waste_source_families"] == ["harris_cad_property_search_portal"]
    assert summary["browser_success_failure_summary"]["success_count"] == 1
    assert summary["browser_success_failure_summary"]["failure_count"] == 1
    assert summary["static_success_failure_summary"]["failure_count"] == 2


def test_next_ingestion_priority_update_flags_repeated_browser_waste() -> None:
    priorities = build_next_ingestion_priority_update(
        {},
        {},
        {},
        {},
        {"net_progress_state": "mixed"},
        {
            "browser_waste_source_families": ["harris_cad_property_search_portal"],
            "by_source_family": {},
        },
    )["priorities"]

    assert any(
        row["action_type"] == "refine_anchor_before_browser_retry"
        and row["target"] == "harris_cad_property_search_portal"
        for row in priorities
    )


def test_pipeline_orchestrator_refreshes_ingestion_learning_fields(orchestrator):
    run = PipelineRun(
        run_id="run:test-learning",
        pipeline_id="ova-2026",
        started_at="2026-04-29T00:00:00+00:00",
    )
    orchestrator._refresh_run_semantics(
        run,
        {
            "motor_024": {
                "phase_self_evaluation_register": {
                    "summary": {
                        "overall_result": "partially_resolved",
                    }
                },
                "case_delta_register": {"net_progress_state": "improved"},
                "source_yield_memory_register": {"productive_source_count": 2},
                "next_ingestion_priority_update": {
                    "priority_count": 3,
                    "top_priority_action": "execute_missing_mandatory_source",
                },
                "ingestion_learning_register": {
                    "summary": {
                        "previous_run_id": "run:prev",
                        "net_progress_state": "improved",
                    }
                },
            }
        },
    )
    assert run.case_delta_summary["net_progress_state"] == "improved"
    assert run.source_yield_memory_summary["productive_source_count"] == 2
    assert run.next_ingestion_priority_update["priority_count"] == 3
    assert run.ingestion_learning_summary["previous_run_id"] == "run:prev"
    assert run.to_dict()["ingestion_learning_summary"]["net_progress_state"] == "improved"


def test_load_previous_pipeline_run_summary_reads_latest_matching_run(tmp_path, monkeypatch):
    older = tmp_path / "run:older.json"
    newer = tmp_path / "run:newer.json"
    other = tmp_path / "run:other.json"
    older.write_text(
        json.dumps(
            {
                "run_id": "run:older",
                "pipeline_id": "ova-2026",
                "started_at": "2026-04-28T00:00:00+00:00",
                "completed_at": "2026-04-28T00:10:00+00:00",
                "recommended_report_type": "Decision-Blocked Asset Brief",
            }
        ),
        encoding="utf-8",
    )
    newer.write_text(
        json.dumps(
            {
                "run_id": "run:newer",
                "pipeline_id": "ova-2026",
                "started_at": "2026-04-29T00:00:00+00:00",
                "completed_at": "2026-04-29T00:10:00+00:00",
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "report_type_trace": {"final_published_report_type": "Compliance / Investment Screening Brief"},
                "ingestion_learning_summary": {"net_progress_state": "improved"},
            }
        ),
        encoding="utf-8",
    )
    other.write_text(
        json.dumps(
            {
                "run_id": "run:other",
                "pipeline_id": "wil-2026",
                "started_at": "2026-04-29T00:00:00+00:00",
                "completed_at": "2026-04-29T00:11:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(orchestrator_module, "DEFAULT_RUN_REGISTRY_DIR", tmp_path)
    summary = orchestrator_module._load_previous_pipeline_run_summary("ova-2026", "run:current")
    assert summary["run_id"] == "run:newer"
    assert summary["recommended_report_type"] == "Compliance / Investment Screening Brief"
    assert summary["ingestion_learning_summary"]["net_progress_state"] == "improved"


def test_load_previous_pipeline_run_summary_prefers_learning_store(tmp_path, monkeypatch):
    learning_dir = tmp_path / "learning"
    run_dir = tmp_path / "runs"
    run_dir.mkdir()
    (run_dir / "run:older.json").write_text(
        json.dumps(
            {
                "run_id": "run:older",
                "pipeline_id": "ova-2026",
                "completed_at": "2026-04-28T00:10:00+00:00",
                "recommended_report_type": "Decision-Blocked Asset Brief",
            }
        ),
        encoding="utf-8",
    )
    save_pipeline_learning_summary(
        {
            "run_id": "run:store-latest",
            "pipeline_id": "ova-2026",
            "completed_at": "2026-04-29T00:10:00+00:00",
            "status": "completed",
            "recommended_report_type": "Compliance / Investment Screening Brief",
            "report_type_trace": {"final_published_report_type": "Compliance / Investment Screening Brief"},
            "phase_self_evaluation_summary": {"overall_result": "partially_resolved"},
            "evidence_maturity_summary": {},
            "key_variable_bottlenecks": [],
            "case_delta_summary": {},
            "source_yield_memory_summary": {},
            "next_ingestion_priority_update": {},
            "ingestion_learning_summary": {"net_progress_state": "improved"},
        },
        store_dir=learning_dir,
    )
    monkeypatch.setattr(orchestrator_module, "DEFAULT_RUN_REGISTRY_DIR", run_dir)
    monkeypatch.setattr(orchestrator_module, "load_pipeline_learning_summary", lambda pipeline_id: load_pipeline_learning_summary(pipeline_id, store_dir=learning_dir))
    summary = orchestrator_module._load_previous_pipeline_run_summary("ova-2026", "run:current")
    assert summary["run_id"] == "run:store-latest"
    assert summary["ingestion_learning_summary"]["net_progress_state"] == "improved"


def test_persist_run_writes_ingestion_learning_store(tmp_path, monkeypatch, orchestrator):
    run_dir = tmp_path / "runs"
    learning_dir = tmp_path / "learning"
    monkeypatch.setattr(orchestrator_module, "DEFAULT_RUN_REGISTRY_DIR", run_dir)
    monkeypatch.setattr(orchestrator_module, "save_pipeline_learning_summary", lambda payload: save_pipeline_learning_summary(payload, store_dir=learning_dir))
    run = PipelineRun(
        run_id="run:store-write",
        pipeline_id="ova-2026",
        started_at="2026-04-29T00:00:00+00:00",
        completed_at="2026-04-29T00:10:00+00:00",
        status=PipelineStatus.COMPLETED,
        recommended_report_type="Compliance / Investment Screening Brief",
        report_type_trace={"final_published_report_type": "Compliance / Investment Screening Brief"},
        phase_self_evaluation_summary={"overall_result": "partially_resolved"},
        case_delta_summary={"net_progress_state": "improved"},
        source_yield_memory_summary={"productive_source_count": 2},
        next_ingestion_priority_update={"priority_count": 3},
        ingestion_learning_summary={"net_progress_state": "improved", "top_priority_action": "request_missing_evidence"},
    )
    orchestrator._persist_run(run)
    summary = load_pipeline_learning_summary("ova-2026", store_dir=learning_dir)
    assert summary["run_id"] == "run:store-write"
    assert summary["ingestion_learning_summary"]["top_priority_action"] == "request_missing_evidence"
