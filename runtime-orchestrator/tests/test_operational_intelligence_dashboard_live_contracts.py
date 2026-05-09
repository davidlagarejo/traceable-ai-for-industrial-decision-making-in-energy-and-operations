from __future__ import annotations

import json
from pathlib import Path

import dashboard as dashboard_module


_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "operational_intelligence_dashboard_live_contract_snapshot.json"


def test_dashboard_api_live_current_contract_snapshot_stays_stable(monkeypatch) -> None:
    fake_run = {
        "run_id": "run:oisk-baseline",
        "pipeline_id": "oisk-2026",
        "status": "completed",
        "recommended_report_type": "Target Clarification Brief",
        "report_type_trace": {
            "early_report_type_gate": "Target Clarification Brief",
            "maturity_refined_report_type": "Target Clarification Brief",
            "final_published_report_type": "Target Clarification Brief",
        },
        "phase_self_evaluation_summary": {"overall_result": "resolved"},
        "previous_run_id": "run:prev",
        "ingestion_learning_summary": {"net_progress_state": "stable"},
        "case_delta_summary": {"net_progress_state": "stable"},
        "source_yield_memory_summary": {"productive_source_count": 0},
        "next_ingestion_priority_update": {"priority_count": 0},
        "motor_results": {},
    }
    fake_active = {
        "run_id": "run:oisk-baseline",
        "pipeline_id": "oisk-2026",
        "status": "completed",
    }

    monkeypatch.setattr(dashboard_module, "_all_runs", lambda: [fake_active])
    monkeypatch.setattr(
        dashboard_module,
        "_select_active_run",
        lambda runs, requested_run_id="", requested_pipeline_id="": fake_active,
    )
    monkeypatch.setattr(dashboard_module, "_load_run", lambda run_id: fake_run)
    monkeypatch.setattr(
        dashboard_module,
        "_run_detail",
        lambda run_id: {
            "motors": [],
            "case_title": "Operational Intelligence Baseline",
            "summary": {},
            "motor_overview": {},
            "started_at": "",
            "duration_s": 0,
            "error": "",
        },
    )
    monkeypatch.setattr(dashboard_module, "_company_info", lambda raw_run: {})
    monkeypatch.setattr(dashboard_module, "_target_info", lambda raw_run: {"label": "TEST TARGET"})
    monkeypatch.setattr(dashboard_module, "_research_activity", lambda raw_run: {"summary": {}, "attempts": [], "note": ""})
    monkeypatch.setattr(
        dashboard_module,
        "_ingestion_activity",
        lambda raw_run: {
            "available": True,
            "classification": {"target_type": "AMBIGUOUS_TARGET", "recommended_report_type": "Target Clarification Brief"},
            "summary": {"sources_total": 0, "blocking_fields_total": 0, "missing_evidence_total": 0},
            "learning": {"summary": {"net_progress_state": "stable"}},
            "blocking_fields": [],
            "missing_evidence": [],
        },
    )
    monkeypatch.setattr(dashboard_module, "_focus_activity", lambda raw_run, motors: [])
    monkeypatch.setattr(dashboard_module, "_chart_activity", lambda raw_run: {"status": "completed", "total_charts": 0, "errors": [], "assets": []})
    monkeypatch.setattr(
        dashboard_module,
        "_congruence_brain_activity",
        lambda raw_run: {
            "available": True,
            "registry": {"patterns": 8, "combinations": 1, "source_basis": 1},
            "active_pattern_ids": [],
            "active_pattern_sources": [],
            "pattern_authority_state": "skill_primary",
            "pattern_authority_summary": {"pattern_authority_state": "skill_primary"},
            "registry_pattern_activation_register": [],
            "authoritative_pattern_activation_register": [],
            "anti_trigger_signals": [],
            "combination_activation_register": [],
            "combination_review_register": [],
            "licensed_research": {
                "available": True,
                "licensed_research_capability_enabled": False,
                "provider_session_register": [],
                "provider_summary": {"provider_count": 4, "ready_provider_count": 0, "session_required_count": 4},
                "extraction_review_register": [],
                "approved_pattern_promotion_register": [],
                "approved_combination_promotion_register": [],
            },
            "promotion_summary": {"reviewed_extractions": 0, "approved_patterns": 0, "approved_combinations": 0},
            "decision_summary": {"total": 0, "by_decision": {}},
            "decision_store": {"updated_at": "", "path": "", "stored_decision_count": 0},
            "note": "",
        },
    )
    monkeypatch.setattr(dashboard_module, "_audit_failures", lambda run_id: [])
    monkeypatch.setattr(dashboard_module, "_pdf_for_run", lambda raw_run, allow_global_fallback=False: None)
    monkeypatch.setattr(dashboard_module, "_pdf_variants_for_run", lambda raw_run: {})

    client = dashboard_module.app.test_client()
    response = client.get("/api/live?pipeline_id=oisk-2026")
    payload = response.get_json()

    assert response.status_code == 200
    assert sorted(payload.keys()) == sorted(json.loads(_FIXTURE_PATH.read_text(encoding="utf-8")))
