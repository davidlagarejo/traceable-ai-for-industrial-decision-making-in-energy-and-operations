from __future__ import annotations

import json

import dashboard as dashboard_module


def _fake_motor_output(motor_id: str) -> dict:
    if motor_id == "motor_051":
        return {
            "fair_comparison_profile": {"asset_family": "logistics_warehouse"},
            "invalid_comparison_risk_register": [
                {
                    "risk_name": "warehouse_area_only_comparison",
                    "risk_level": "critical",
                    "required_normalization": ["service level", "dock activity profile"],
                }
            ],
            "comparison_validity_register": [
                {"peer_frame": "warehouse_area_only_comparison", "comparable": False}
            ],
        }
    if motor_id == "motor_052":
        return {
            "activated_pattern_register": [
                {
                    "pattern_name": "forklift_charging_and_demand_spike_plausible",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "power_quality_hypothesis_register": [],
            "pattern_authority_state": "skill_primary",
            "pattern_authority_summary": {"pattern_authority_state": "skill_primary"},
            "authoritative_pattern_activation_register": [
                {
                    "pattern_id": "warehouse_mhe_charging_demand_peak",
                    "activation_state": "structurally_plausible",
                }
            ],
        }
    if motor_id == "motor_053":
        return {
            "value_leakage_register": [
                {
                    "financial_exposure_type": "tenant_operator_value_leakage",
                    "why_it_matters": "Boundary leakage remains plausible.",
                }
            ]
        }
    return {}


def _fake_discovery_queue_manifest() -> dict:
    return {
        "provider_key": "ieee",
        "export_path": "/tmp/ieee-export.csv",
        "summary": {"candidate_count": 1, "pattern_promotion_count": 2, "combination_promotion_count": 0},
        "candidate_rows": [
            {
                "candidate_id": "ieee-candidate-01",
                "expected_pdf_name": "ieee-candidate-01.pdf",
                "title": "Reactive power and compressed air maintenance in manufacturing facilities",
                "doi": "10.1109/TIA.2026.999003",
                "journal": "IEEE Transactions on Industry Applications",
                "published_year": "2026",
                "authors": ["D. Researcher", "E. Researcher"],
                "keywords": ["reactive power", "compressed air", "maintenance", "manufacturing"],
                "source_url": "https://ieeexplore.ieee.org/document/999003",
                "manifest": {"provider_key": "ieee", "title": "Reactive power and compressed air maintenance in manufacturing facilities"},
                "metadata_payload": {
                    "provider_key": "ieee",
                    "title": "Reactive power and compressed air maintenance in manufacturing facilities",
                    "doi": "10.1109/TIA.2026.999003",
                    "journal": "IEEE Transactions on Industry Applications",
                    "published_year": "2026",
                    "authors": ["D. Researcher", "E. Researcher"],
                    "source_url": "https://ieeexplore.ieee.org/document/999003",
                    "abstract": "Industrial facilities often combine reactive power exposure, compressed air leakage, and maintenance maturity problems.",
                    "keywords": ["reactive power", "compressed air", "maintenance", "manufacturing"],
                    "notes": "Auto-generated from ieee discovery export.",
                },
                "extraction_payload": {
                    "provider_key": "ieee",
                    "review_status": "auto_draft",
                    "knowledge_atoms": [
                        {
                            "id": "atom::ieee-candidate-01::reactive_power_exposure",
                            "knowledge_type": "FINANCIAL_TRANSLATION",
                            "statement": "Reactive power can shift cost and capacity risk away from simple kWh narratives.",
                            "asset_types": ["industrial_facility"],
                            "applicable_industries": ["manufacturing"],
                            "applicable_contexts": ["inductive loads plausible"],
                            "anti_triggers": [],
                            "falsification_conditions": ["high power factor documented"],
                            "minimum_evidence": ["utility bills", "tariff", "power quality study"],
                            "financial_mechanism": "PF penalties and hidden demand risk can distort capital allocation.",
                            "supporting_excerpt": "Industrial facilities often combine reactive power exposure...",
                            "source_locator": "dashboard_test::ieee::reactive_power",
                            "confidence_ceiling": "L2",
                        },
                        {
                            "id": "atom::ieee-candidate-01::compressed_air_leak_plausibility",
                            "knowledge_type": "LOSS_PATTERN",
                            "statement": "Compressed air systems often hide leakage and control waste behind production demand.",
                            "asset_types": ["industrial_facility"],
                            "applicable_industries": ["manufacturing"],
                            "applicable_contexts": ["compressed air plausible"],
                            "anti_triggers": [],
                            "falsification_conditions": ["no compressed air system"],
                            "minimum_evidence": ["compressor inventory", "leak survey"],
                            "financial_mechanism": "Waste can be structural but still economically material through maintenance and load timing.",
                            "supporting_excerpt": "Industrial facilities often combine reactive power exposure, compressed air leakage...",
                            "source_locator": "dashboard_test::ieee::compressed_air",
                            "confidence_ceiling": "L2",
                        },
                    ],
                    "pattern_candidate_records": [
                        {
                            "id": "pattern_candidate::ieee-candidate-01::reactive_power_exposure",
                            "matched_registry_pattern_id": "reactive_power_exposure",
                            "derived_from_atom_ids": ["atom::ieee-candidate-01::reactive_power_exposure"],
                        },
                        {
                            "id": "pattern_candidate::ieee-candidate-01::compressed_air_leak_plausibility",
                            "matched_registry_pattern_id": "compressed_air_leak_plausibility",
                            "derived_from_atom_ids": ["atom::ieee-candidate-01::compressed_air_leak_plausibility"],
                        },
                    ],
                    "combination_candidate_records": [],
                },
                "matched_pattern_ids": ["reactive_power_exposure", "compressed_air_leak_plausibility"],
                "matched_combination_ids": [],
                "pattern_promotion_count": 2,
                "combination_promotion_count": 0,
                "priority_score": 29,
            }
        ],
        "approved_pattern_promotion_register": [
            {
                "promotion_id": "pattern_promotion::extract::ieee_discovery::ieee-candidate-01::pattern_candidate::ieee-candidate-01::reactive_power_exposure",
                "pattern_id": "reactive_power_exposure",
                "promotion_state": "auto_draft_review_required",
                "source_basis_id": "licensed_research_public_technical_priors",
                "document_ref": "10.1109/TIA.2026.999003",
                "proposed_spec": {"name": "Reactive Power Exposure", "knowledge_type": ["LOSS_PATTERN"]},
            }
        ],
        "approved_combination_promotion_register": [],
        "extraction_review_register": [
            {
                "extraction_id": "extract::ieee_discovery::ieee-candidate-01",
                "review_status": "auto_draft",
                "document_ref": "10.1109/TIA.2026.999003",
            }
        ],
    }


def _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(dashboard_module, "_COMBINATION_DECISION_DIR", tmp_path / "combination")
    monkeypatch.setattr(dashboard_module, "_COMBINATION_EDIT_DIR", tmp_path / "combination-edits")
    monkeypatch.setattr(dashboard_module, "_COMBINATION_REVIEW_CONTROL_DIR", tmp_path / "combination-review-controls")
    monkeypatch.setattr(dashboard_module, "_COMBINATION_FOLLOW_ON_MANIFEST_DIR", tmp_path / "combination-follow-on-manifests")
    monkeypatch.setattr(dashboard_module, "_LATENT_CLUSTER_OVERRIDE_DIR", tmp_path / "latent-cluster-overrides")
    monkeypatch.setattr(dashboard_module, "_PROMOTION_DECISION_DIR", tmp_path / "promotion-decisions")
    monkeypatch.setattr(dashboard_module, "_PROMOTION_EDIT_DIR", tmp_path / "promotion-edits")
    monkeypatch.setattr(dashboard_module, "_DISCOVERY_QUEUE_MANIFEST_DIR", tmp_path / "discovery-manifests")
    monkeypatch.setattr(dashboard_module, "_DISCOVERY_CANDIDATE_DECISION_DIR", tmp_path / "discovery-decisions")
    monkeypatch.setattr(dashboard_module, "_DISCOVERY_CANDIDATE_EDIT_DIR", tmp_path / "discovery-edits")
    monkeypatch.setattr(dashboard_module, "_ARTICLE_REFERENCE_DIR", tmp_path / "article-refs")
    monkeypatch.setattr(dashboard_module, "_ACCEPTED_DISCOVERY_BUNDLE_DIR", tmp_path / "accepted-discovery-bundles")
    monkeypatch.setattr(dashboard_module, "_REFERENCE_BACKED_PROMOTION_DIR", tmp_path / "reference-backed-promotions")
    monkeypatch.setattr(dashboard_module, "_KNOWLEDGE_ATOM_REFRESH_DIR", tmp_path / "knowledge-atom-refresh")
    monkeypatch.setattr(dashboard_module, "_COMBINATION_RERANK_DIR", tmp_path / "combination-rerank")
    monkeypatch.setattr(dashboard_module, "_SEARCH_QUERY_EXECUTION_MANIFEST_DIR", tmp_path / "search-query-execution-manifests")
    monkeypatch.setattr(dashboard_module, "_SEARCH_QUERY_EXECUTION_SESSION_DIR", tmp_path / "search-query-execution-sessions")
    monkeypatch.setattr(dashboard_module, "_SEARCH_QUERY_RESULT_IMPORT_DIR", tmp_path / "search-query-result-imports")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_CAMPAIGN_TRIGGER_DIR", tmp_path / "research-campaign-triggers")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_STATE_DIR", tmp_path / "research-loop-state")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_EVENT_DIR", tmp_path / "research-loop-events")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_JOB_DIR", tmp_path / "research-loop-jobs")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_METRIC_DIR", tmp_path / "research-loop-metrics")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_CONTROL_DIR", tmp_path / "research-loop-controls")
    monkeypatch.setattr(dashboard_module, "_REGISTRY_STAGE_CANDIDATE_DIR", tmp_path / "registry-stage-candidates")
    monkeypatch.setattr(dashboard_module, "_PROVIDER_SESSION_HANDOFF_DIR", tmp_path / "provider-session-handoffs")


def test_congruence_brain_activity_builds_registry_first_review_register(monkeypatch, tmp_path) -> None:
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest("run:oisk-dashboard", _fake_discovery_queue_manifest())
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    result = dashboard_module._congruence_brain_activity(
        {
            "run_id": "run:oisk-dashboard",
            "asset_context": {
                "solar_profile": "morning",
                "operating_rhythm": "early shift",
                "utility_tariff_context": "demand charge tariff",
                "control_boundary": "tenant operator split",
            },
            "licensed_research_activity": {
                "extraction_review_register": [
                    {"extraction_id": "extract::dashboard::01", "review_status": "approved"}
                ],
                "approved_pattern_promotion_register": [
                    {"pattern_id": "licensed_boundary_candidate", "promotion_state": "ready_for_registry_review"}
                ],
                "approved_combination_promotion_register": [
                    {
                        "combination_id": "licensed_boundary_combo",
                        "promotion_state": "ready_for_registry_review",
                    }
                ],
            },
        }
    )

    assert result["available"] is True
    active_pattern_ids = set(result["active_pattern_ids"])
    assert {
        "fair_comparison_invalid_area_metric",
        "value_boundary_leakage_owner_operator",
        "warehouse_mhe_charging_demand_peak",
        "demand_charge_exposure_unknown",
    }.issubset(active_pattern_ids)
    registry_pattern_ids = {row["pattern_id"] for row in result["registry_pattern_activation_register"]}
    assert "warehouse_mhe_charging_demand_peak" in registry_pattern_ids
    assert "fair_comparison_invalid_area_metric" in registry_pattern_ids
    assert result["pattern_authority_state"] == "skill_primary"
    authoritative_pattern_ids = {
        row.get("pattern_id", "")
        for row in result["authoritative_pattern_activation_register"]
    }
    assert "warehouse_mhe_charging_demand_peak" in authoritative_pattern_ids
    assert result["asset_context_vector"]["solar_profile"] == "morning_solar_peak"
    assert result["context_differentiator_register"]
    assert result["latent_combination_candidate_register"]
    assert result["latent_combination_cluster_register"]
    assert result["admissible_combination_review_register"]
    assert result["combination_review_sequence_register"]
    assert result["current_combination_review_row"]["combination_id"]
    assert result["combination_review_queue_summary"]["pending"] >= 1
    assert result["combination_follow_on_research_register"]
    assert result["combination_follow_on_execution_manifest_register"]
    assert result["current_combination_follow_on_execution_manifest"]["combination_id"]
    assert result["current_combination_follow_on_execution_manifest"]["provider_query_template_count"] >= 1
    assert result["current_combination_follow_on_execution_manifest"]["execution_rows"][0]["provider_query_templates"]
    assert result["combination_search_gap_record"]["search_status"] == "incomplete_under_investigated"
    assert "coverage_proof_not_strong" in result["combination_search_gap_record"]["gap_flags"]
    assert result["research_campaign_record"]["campaign_status"] == "coverage_building"
    assert result["research_campaign_trigger_register"]
    assert result["research_loop_state"]["loop_status"] == "seeding_queries"
    assert result["research_loop_state"]["next_action"] == "SEED_QUERY_CANDIDATES"
    assert result["research_loop_job_register"]
    assert result["current_research_job"]["job_type"] == "seed_query_candidates"
    assert result["research_loop_metrics"]["latent_candidate_count"] >= 1
    assert result["research_depth_enforcement_record"]["must_continue_research"] is True
    assert result["research_depth_enforcement_record"]["required_next_source_families"]
    assert result["research_stop_condition_record"]["stop_state"] == "continue_research"
    assert result["licensed_research"]["knowledge_atom_register"]
    assert result["licensed_research"]["source_coverage_summary"]["knowledge_atom_count"] >= 2
    assert result["licensed_research"]["source_family_coverage_register"]
    assert len(result["combination_review_register"]) == 1
    row = result["combination_review_register"][0]
    assert row["combination_id"] == "warehouse_tariff_boundary_area_combo"
    assert row["operator_decision"] == "candidate"
    assert result["promotion_summary"] == {
        "reviewed_extractions": 2,
        "approved_patterns": 2,
        "approved_combinations": 1,
    }
    assert result["licensed_research"]["available"] is True
    assert result["licensed_research"]["provider_summary"]["provider_count"] >= 4
    assert result["licensed_research"]["approved_pattern_promotion_register"][0]["pattern_id"] == "licensed_boundary_candidate"
    assert len(result["licensed_research"]["promotion_review_register"]) == 3
    promotion_ids = {row["promotion_id"] for row in result["licensed_research"]["promotion_review_register"]}
    assert "pattern::licensed_boundary_candidate" in promotion_ids
    assert "combination::licensed_boundary_combo" in promotion_ids
    assert result["licensed_research"]["promotion_decision_summary"]["candidate"] == 3
    assert result["licensed_research"]["accepted_discovery_candidate_bundle"]["summary"]["accepted_count"] == 0
    assert result["licensed_research"]["registry_review_bundle"]["summary"]["accepted_total"] == 0
    assert result["licensed_research"]["registry_stage_preview"]["summary"]["total_rows"] == 0
    assert result["licensed_research"]["provider_handoff_bundle"]["summary"]["provider_count"] >= 4
    assert result["licensed_research"]["provider_handoff_bundle"]["provider_rows"][0]["recommended_action"]
    assert "bootstrap_licensed_provider_session.py" in result["licensed_research"]["provider_handoff_bundle"]["provider_rows"][0]["display_command"]
    assert result["research_loop_state_store"]["exists"] is True
    assert result["research_loop_job_store"]["stored_job_count"] >= 1
    assert result["research_loop_metric_store"]["exists"] is True
    assert result["research_loop_metric_store"]["depth_state"]
    assert result["research_loop_control_store"]["control_state"] == "active"
    assert result["research_loop_event_store"]["stored_event_count"] >= 1


def test_congruence_brain_activity_merges_discovery_queue_and_article_references(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    dashboard_module._persist_article_reference_record(
        run_id,
        {
            "candidate_id": "ieee-candidate-01",
            "reference_state": "visible_text_enriched",
            "acquisition_result": {"visible_text": "Reactive power and compressed air maintenance reference excerpt."},
            "research_document_manifest": {"provider_key": "ieee"},
            "updated_at": "2026-05-05T00:00:00Z",
        },
    )

    result = dashboard_module._congruence_brain_activity({"run_id": run_id, "licensed_research_activity": {}})

    assert len(result["licensed_research"]["discovery_candidate_review_register"]) == 1
    assert result["licensed_research"]["discovery_candidate_review_register"][0]["reference_state"] == "visible_text_enriched"
    assert len(result["licensed_research"]["article_reference_register"]) == 1
    assert result["licensed_research"]["article_reference_register"][0]["reference_excerpt"]


def test_combination_decision_endpoint_persists_and_merges(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}}

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-decision",
        json={
            "run_id": run_id,
            "combination_id": "warehouse_tariff_boundary_area_combo",
            "operator_decision": "accepted_for_case_use",
            "decision_reason": "Accepted in dashboard test.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["operator_decision"] == "accepted_for_case_use"
    assert payload["updated_row"]["decision_reason"] == "Accepted in dashboard test."

    stored = json.loads((tmp_path / "combination" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["run_id"] == run_id
    assert stored["decisions"][0]["combination_id"] == "warehouse_tariff_boundary_area_combo"
    assert stored["decisions"][0]["operator_decision"] == "accepted_for_case_use"


def test_combination_decision_endpoint_accepts_latent_combination_ids(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    latent_id = preview["admissible_combination_review_register"][0]["combination_id"]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-decision",
        json={
            "run_id": run_id,
            "combination_id": latent_id,
            "operator_decision": "accepted_for_case_use",
            "decision_reason": "Accepted latent combination in dashboard test.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["combination_id"] == latent_id
    assert payload["updated_row"]["operator_decision"] == "accepted_for_case_use"


def test_combination_edit_endpoint_persists_patch_and_advances_sequential_queue(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_row = dict(preview["current_combination_review_row"])
    current_id = current_row["combination_id"]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-edit",
        json={
            "run_id": run_id,
            "combination_id": current_id,
            "patch": {
                "combination_name": "Edited Sequential Combination",
                "combined_hypothesis": "Edited combined hypothesis.",
                "strategic_risk": "Edited strategic risk.",
                "minimum_evidence": ["utility bills", "dock profile"],
                "financial_exposure": ["tariff exposure", "boundary leakage"],
                "tad_action": "VALIDATE_FIRST",
                "prohibited_claims": ["ROI", "peer superiority"],
                "allowed_language": "Edited allowed language.",
            },
            "auto_close_review": True,
            "decision_reason": "Modified from dashboard test.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["combination_id"] == current_id
    assert payload["updated_row"]["operator_decision"] == "needs_review"
    assert payload["updated_row"]["combination_name"] == "Edited Sequential Combination"

    stored_edits = json.loads((tmp_path / "combination-edits" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored_edits["run_id"] == run_id
    assert stored_edits["edits"][0]["combination_id"] == current_id
    stored_triggers = json.loads((tmp_path / "research-campaign-triggers" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored_triggers["triggers"]

    refreshed = payload["congruence_brain"]
    next_current = refreshed["current_combination_review_row"]
    if next_current:
        assert next_current["combination_id"] != current_id
    else:
        assert refreshed["combination_review_queue_summary"]["pending"] == 0


def test_combination_review_control_endpoint_can_defer_current_combination(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-review-control",
        json={
            "run_id": run_id,
            "action": "defer_current",
            "combination_id": current_id,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    refreshed = payload["congruence_brain"]
    deferred_ids = refreshed["combination_review_control_store"]["deferred_count"]
    assert deferred_ids >= 1
    current_row = refreshed["current_combination_review_row"]
    if current_row:
        assert refreshed["combination_review_queue_summary"]["deferred"] >= 1

    stored = json.loads((tmp_path / "combination-review-controls" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert current_id in stored["deferred_combination_ids"]
    stored_triggers = json.loads((tmp_path / "research-campaign-triggers" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored_triggers["triggers"]


def test_combination_review_control_endpoint_updates_batch_size(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-review-control",
        json={
            "run_id": run_id,
            "action": "set_batch_size",
            "batch_size": 3,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    refreshed = payload["congruence_brain"]
    assert refreshed["combination_review_queue_summary"]["batch_size"] == 3
    assert refreshed["combination_review_control_store"]["batch_size"] == 3


def test_research_loop_control_endpoint_pauses_loop(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/research-loop-control",
        json={
            "run_id": run_id,
            "requested_action": "pause",
            "control_reason": "waiting for manual source adjudication",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["control_store"]["control_state"] == "paused_by_operator"
    refreshed = payload["congruence_brain"]
    assert refreshed["research_loop_state"]["loop_status"] == "paused_by_operator"
    assert refreshed["research_stop_condition_record"]["stop_state"] == "paused_by_operator"
    assert refreshed["research_loop_control_store"]["control_state"] == "paused_by_operator"


def test_research_loop_advance_endpoint_executes_seed_job(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/research-loop-advance",
        json={"run_id": run_id},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["execution_status"] == "executed"
    assert payload["executed_action"] == "SEED_QUERY_CANDIDATES"
    refreshed = payload["congruence_brain"]
    assert refreshed["current_research_job"]["job_type"] in {
        "draft_reference",
        "capture_search_result",
        "resolve_reference_excerpt",
    }
    stored_manifest = json.loads((tmp_path / "discovery-manifests" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert any(row["candidate_id"].startswith("queryseed-") for row in stored_manifest["candidate_rows"])


def test_combination_decision_needs_review_autoqueues_follow_on_research(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-decision",
        json={
            "run_id": run_id,
            "combination_id": current_id,
            "operator_decision": "needs_review",
            "decision_reason": "Hold for more research.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    stored_triggers = json.loads((tmp_path / "research-campaign-triggers" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored_triggers["triggers"]


def test_combination_follow_on_manifest_materialize_persists_execution_plan(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-follow-on-manifest-materialize",
        json={
            "run_id": run_id,
            "combination_id": current_id,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["record"]["combination_id"] == current_id
    assert payload["record"]["execution_rows"]
    assert payload["record"]["provider_query_template_count"] >= 1
    assert payload["record"]["execution_rows"][0]["provider_query_templates"]

    stored = json.loads((tmp_path / "combination-follow-on-manifests" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["run_id"] == run_id
    assert stored["manifests"][0]["combination_id"] == current_id
    assert stored["manifests"][0]["execution_rows"][0]["provider_query_templates"]


def test_combination_follow_on_seed_candidates_creates_query_seed_discovery_rows(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    expected_seed_count = int(preview["current_combination_follow_on_execution_manifest"]["provider_query_template_count"] or 0)

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={
            "run_id": run_id,
            "combination_id": current_id,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert len(payload["seeded_candidate_ids"]) == expected_seed_count
    assert payload["updated_rows"]
    assert all(candidate_id.startswith("queryseed-") for candidate_id in payload["seeded_candidate_ids"])
    assert "Primary query:" in payload["updated_rows"][0]["metadata_payload"]["notes"]

    stored_manifest = json.loads((tmp_path / "discovery-manifests" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    stored_ids = {row["candidate_id"] for row in stored_manifest["candidate_rows"]}
    assert set(payload["seeded_candidate_ids"]).issubset(stored_ids)


def test_article_reference_read_on_query_seed_creates_query_seed_draft(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_response = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    )
    seeded_payload = seed_response.get_json()
    seed_id = seeded_payload["seeded_candidate_ids"][0]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/article-reference-read",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["reference_state"] == "query_seed_draft"
    assert "Primary query:" in payload["updated_row"]["reference_excerpt"]
    assert payload["updated_row"]["acquisition_result"]["status"] == "query_seed_draft"
    assert payload["updated_row"]["draft_resolution_prefill"]["query_family"]
    assert payload["updated_row"]["draft_resolution_prefill"]["primary_query"]
    assert payload["updated_row"]["draft_resolution_prefill"]["evidence_targets"]
    assert payload["updated_row"]["draft_resolution_prefill"]["search_surface"]
    assert payload["updated_row"]["draft_resolution_prefill"]["execution_hint"]
    assert payload["updated_row"]["acquisition_result"]["search_brief"]
    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    capture_row = next(
        row
        for row in refreshed["search_result_capture_register"]
        if row["candidate_id"] == seed_id
    )
    assert capture_row["next_capture_action"] == "CAPTURE_SEARCH_RESULT"
    execution_row = next(
        row
        for row in refreshed["search_query_execution_register"]
        if row["candidate_id"] == seed_id
    )
    assert execution_row["execution_status"] == "search_ready_capture_pending"
    assert "Primary query:" in execution_row["search_packet_template"]
    assert refreshed["search_result_capture_summary"]["seed_only"] >= 1


def test_article_reference_edit_can_resolve_query_seed_draft_to_manual_text(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/article-reference-edit",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "patch": {
                "source_url": "https://ieeexplore.ieee.org/document/seed-123",
                "reference_excerpt": "This article confirms the demand-charge timing mechanism around charging windows.",
                "notes": "Resolved from IEEE search result.",
                "reference_state": "manual_text_enriched",
            },
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["reference_state"] == "manual_text_enriched"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/seed-123"
    assert "demand-charge timing mechanism" in payload["updated_row"]["reference_excerpt"]
    assert payload["updated_row"]["acquisition_result"]["status"] == "query_seed_manual_capture"


def test_article_reference_quick_resolve_can_resolve_query_seed_draft(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/article-reference-quick-resolve",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "source_url": "https://ieeexplore.ieee.org/document/quick-123",
            "reference_excerpt": "Quick excerpt confirming tariff timing and queue advancement.",
            "notes": "Resolved through quick resolve flow.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["reference_state"] == "manual_text_enriched"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/quick-123"
    assert "Quick excerpt confirming" in payload["updated_row"]["reference_excerpt"]
    assert payload["updated_row"]["acquisition_result"]["status"] == "query_seed_manual_capture"


def test_article_reference_quick_resolve_can_reuse_captured_source_url(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})
    client.post(
        "/api/article-reference-capture-search-result",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "source_url": "https://ieeexplore.ieee.org/document/reused-123",
            "search_result_title": "IEEE captured title",
            "search_result_snippet": "Visible result snippet before quick resolve.",
            "notes": "Captured from IEEE search result.",
        },
    )

    response = client.post(
        "/api/article-reference-quick-resolve",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "reference_excerpt": "Quick excerpt resolved while reusing the captured article URL.",
            "notes": "Resolved through quick resolve flow with captured URL reuse.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["reference_state"] == "manual_text_enriched"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/reused-123"
    assert "reusing the captured article URL" in payload["updated_row"]["reference_excerpt"]


def test_article_reference_capture_search_result_keeps_query_seed_draft_pending(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    before = dashboard_module._congruence_brain_activity(fake_run)
    pending_before = before["reference_resolution_queue_summary"]["pending"]

    response = dashboard_module.app.test_client().post(
        "/api/article-reference-capture-search-result",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "source_url": "https://ieeexplore.ieee.org/document/result-123",
            "search_result_title": "IEEE result title",
            "search_result_snippet": "Visible result snippet before excerpt capture.",
            "notes": "Captured from IEEE search result.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["reference_state"] == "query_seed_draft"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/result-123"
    assert payload["updated_row"]["acquisition_result"]["status"] == "query_seed_result_captured"
    assert payload["updated_row"]["draft_resolution_prefill"]["captured_result_title"] == "IEEE result title"
    assert payload["updated_row"]["draft_resolution_prefill"]["captured_result_snippet"] == "Visible result snippet before excerpt capture."

    after = dashboard_module._congruence_brain_activity(fake_run)
    assert after["search_result_capture_summary"]["result_captured"] >= 1
    capture_row = next(
        row
        for row in after["search_result_capture_register"]
        if row["candidate_id"] == seed_id
    )
    assert capture_row["next_capture_action"] == "RESOLVE_REFERENCE_EXCERPT"
    execution_row = next(
        row
        for row in after["search_query_execution_register"]
        if row["candidate_id"] == seed_id
    )
    assert execution_row["execution_status"] == "result_captured_ready_for_excerpt"
    assert execution_row["captured_result_title"] == "IEEE result title"
    assert after["reference_resolution_queue_summary"]["pending"] == pending_before
    assert after["current_reference_resolution_row"]["candidate_id"] == seed_id
    assert after["current_reference_resolution_row"]["reference_state"] == "query_seed_draft"


def test_search_query_execution_materialize_persists_manifest(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    response = dashboard_module.app.test_client().post(
        "/api/search-query-execution-materialize",
        json={"run_id": run_id},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["search_query_execution_manifest"]["exists"] is True
    stored = json.loads((tmp_path / "search-query-execution-manifests" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["summary"]["pending"] >= 1
    assert any(row["candidate_id"] == seed_id for row in stored["rows"])
    assert stored["session_bundle"]["available"] is True
    assert stored["session_bundle"]["summary"]["pending_rows"] >= 1
    assert "search_execution_capture_workbook_template" in stored["session_bundle"]
    assert any(row["candidate_id"] == seed_id for row in stored["session_bundle"]["rows"])


def test_search_query_execution_import_results_persists_options(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    response = dashboard_module.app.test_client().post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n---\n".join(
                [
                    "\n".join(
                        [
                            f"Candidate ID: {seed_id}",
                            "Rank: 1",
                            "URL: https://ieeexplore.ieee.org/document/import-001",
                            "Title: Imported result 1",
                            "Snippet: Visible import snippet 1.",
                        ]
                    ),
                    "\n".join(
                        [
                            f"Candidate ID: {seed_id}",
                            "Rank: 2",
                            "URL: https://ieeexplore.ieee.org/document/import-002",
                            "Title: Imported result 2",
                            "Snippet: Visible import snippet 2.",
                        ]
                    ),
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert len(stored["result_records"]) == 2
    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    execution_row = next(
        row
        for row in refreshed["search_query_execution_register"]
        if row["candidate_id"] == seed_id
    )
    assert execution_row["imported_result_option_count"] == 2
    assert execution_row["top_imported_result"]["search_result_title"] == "Imported result 1"
    assert refreshed["current_search_query_result_option_row"]["candidate_id"] == seed_id
    assert refreshed["current_search_query_result_option_row"]["current_option_index"] == 1
    assert refreshed["current_search_query_result_option_row"]["current_imported_option"]["search_result_title"] == "Imported result 1"


def test_search_query_execution_import_results_accepts_session_rows(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})
    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    session_bundle = refreshed["search_query_execution_session_bundle"]
    session_rows = session_bundle["rows"]

    assert session_bundle["available"] is True
    assert session_bundle["materialized"] is False
    assert any(row["candidate_id"] == seed_id for row in session_rows)

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_query_execution_session_rows": [
                {
                    **dict(session_rows[0]),
                    "source_url": "https://www.scopus.com/record/session-row-1",
                    "search_result_title": "Session row result 1",
                    "search_result_snippet": "Session row snippet 1.",
                    "selected": True,
                    "notes": "Imported from session row payload.",
                }
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["import_formats"] == ["session_rows"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["candidate_id"] == seed_id
    assert stored["result_records"][0]["import_format"] == "session_rows"
    assert stored["result_records"][0]["selected"] is True


def test_search_query_execution_session_save_persists_store(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})
    session_bundle = dashboard_module._congruence_brain_activity(fake_run)["search_query_execution_session_bundle"]

    response = client.post(
        "/api/search-query-execution-session-save",
        json={
            "run_id": run_id,
            "search_query_execution_session_rows": [
                {
                    **dict(session_bundle["rows"][0]),
                    "source_url": "https://www.scopus.com/record/session-store-1",
                    "search_result_title": "Saved session row 1",
                    "search_result_snippet": "Saved visible snippet 1.",
                    "notes": "Saved in session store.",
                }
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    stored = json.loads((tmp_path / "search-query-execution-sessions" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["rows"][0]["candidate_id"] == seed_id
    assert stored["rows"][0]["search_result_title"] == "Saved session row 1"
    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    assert refreshed["search_query_execution_session_store"]["stored_row_count"] == 1
    assert refreshed["search_query_execution_session_bundle"]["summary"]["ready_rows"] == 1
    assert refreshed["search_query_execution_session_bundle"]["rows"][0]["search_result_title"] == "Saved session row 1"


def test_search_query_execution_session_import_uses_saved_rows(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})
    session_bundle = dashboard_module._congruence_brain_activity(fake_run)["search_query_execution_session_bundle"]
    client.post(
        "/api/search-query-execution-session-save",
        json={
            "run_id": run_id,
            "search_query_execution_session_rows": [
                {
                    **dict(session_bundle["rows"][0]),
                    "source_url": "https://www.scopus.com/record/session-store-import-1",
                    "search_result_title": "Saved import row 1",
                    "search_result_snippet": "Saved import snippet 1.",
                    "selected": True,
                    "notes": "Import from saved session rows.",
                }
            ],
        },
    )

    response = client.post(
        "/api/search-query-execution-session-import",
        json={"run_id": run_id},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["import_formats"] == ["session_rows"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["candidate_id"] == seed_id
    assert stored["result_records"][0]["search_result_title"] == "Saved import row 1"


def test_search_query_execution_session_parse_row_parses_provider_like_line(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    response = client.post(
        "/api/search-query-execution-session-parse-row",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "row_text": "Parsed provider title\thttps://www.scopus.com/record/parse-1\tParsed provider snippet\t\ttrue\tParsed provider notes",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["merged_row"]["candidate_id"] == seed_id
    assert payload["merged_row"]["source_url"] == "https://www.scopus.com/record/parse-1"
    assert payload["merged_row"]["search_result_title"] == "Parsed provider title"
    assert payload["merged_row"]["search_result_snippet"] == "Parsed provider snippet"
    assert "Parsed provider" in payload["merged_row"]["notes"]


def test_search_query_execution_import_results_accepts_structured_records(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    response = dashboard_module.app.test_client().post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_records": [
                {
                    "candidate_id": seed_id,
                    "rank": 1,
                    "url": "https://ieeexplore.ieee.org/document/structured-001",
                    "title": "Structured result 1",
                    "snippet": "Structured snippet 1.",
                    "notes": "Imported through structured records.",
                },
                {
                    "candidate_id": seed_id,
                    "rank": 2,
                    "source_url": "https://ieeexplore.ieee.org/document/structured-002",
                    "search_result_title": "Structured result 2",
                    "search_result_snippet": "Structured snippet 2.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["structured_records"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert len(stored["result_records"]) == 2
    assert stored["result_records"][0]["import_format"] == "structured_records"
    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    execution_row = next(
        row
        for row in refreshed["search_query_execution_register"]
        if row["candidate_id"] == seed_id
    )
    assert execution_row["imported_result_option_count"] == 2
    assert execution_row["imported_result_options"][0]["import_format"] == "structured_records"
    assert refreshed["current_search_query_result_option_row"]["current_option_index"] == 1


def test_search_query_execution_import_results_can_auto_capture_singleton_candidates(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-auto-capture-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Auto capture article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "auto_capture_singleton_candidates": True,
            "search_result_import_records": [
                {
                    "candidate_id": first_seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/auto-capture-1",
                    "search_result_title": "Auto capture result 1",
                    "search_result_snippet": "Visible auto capture snippet 1.",
                },
                {
                    "candidate_id": second_seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/auto-capture-2a",
                    "search_result_title": "Auto capture result 2A",
                    "search_result_snippet": "Visible auto capture snippet 2A.",
                },
                {
                    "candidate_id": second_seed_id,
                    "rank": 2,
                    "source_url": "https://www.scopus.com/record/auto-capture-2b",
                    "search_result_title": "Auto capture result 2B",
                    "search_result_snippet": "Visible auto capture snippet 2B.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["auto_captured_singleton_count"] == 1
    assert payload["summary"]["auto_captured_candidate_ids"] == [first_seed_id]

    refreshed = payload["congruence_brain"]
    first_row = next(
        row for row in refreshed["search_result_capture_register"] if row["candidate_id"] == first_seed_id
    )
    second_execution_row = next(
        row for row in refreshed["search_query_execution_register"] if row["candidate_id"] == second_seed_id
    )
    assert first_row["capture_state"] == "result_captured"
    assert first_row["next_capture_action"] == "RESOLVE_REFERENCE_EXCERPT"
    assert second_execution_row["imported_result_option_count"] == 2
    assert refreshed["current_search_query_result_option_row"]["candidate_id"] == second_seed_id


def test_search_query_execution_import_results_accepts_ordered_records(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-ordered-import-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Ordered import article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_ordered_records": [
                {
                    "source_url": "https://www.scopus.com/record/ordered-import-1",
                    "search_result_title": "Ordered import result 1",
                    "search_result_snippet": "Ordered import snippet 1.",
                },
                {
                    "source_url": "https://www.scopus.com/record/ordered-import-2",
                    "search_result_title": "Ordered import result 2",
                    "search_result_snippet": "Ordered import snippet 2.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_records"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert [row["candidate_id"] for row in stored["result_records"]] == [first_seed_id, second_seed_id]
    assert all(row["import_format"] == "ordered_records" for row in stored["result_records"])


def test_search_query_execution_import_results_accepts_ordered_packet(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-ordered-packet-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Ordered packet article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n---\n".join(
                [
                    "\n".join(
                        [
                            "URL: https://www.scopus.com/record/ordered-packet-1",
                            "Title: Ordered packet result 1",
                            "Snippet: Ordered packet snippet 1.",
                            "Notes: Ordered packet notes 1",
                        ]
                    ),
                    "\n".join(
                        [
                            "URL: https://www.scopus.com/record/ordered-packet-2",
                            "Title: Ordered packet result 2",
                            "Snippet: Ordered packet snippet 2.",
                            "Notes: Ordered packet notes 2",
                        ]
                    ),
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_packet"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert [row["candidate_id"] for row in stored["result_records"]] == [first_seed_id, second_seed_id]
    assert all(row["import_format"] == "ordered_packet" for row in stored["result_records"])


def test_search_query_execution_import_results_accepts_ordered_compact_lines(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-ordered-compact-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Ordered compact article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# URL | Title | Snippet | Excerpt | Selected | Notes",
                    "https://www.scopus.com/record/ordered-compact-1 | Ordered compact result 1 | Ordered compact snippet 1. |  | yes | Ordered compact notes 1",
                    "https://www.scopus.com/record/ordered-compact-2 | Ordered compact result 2 | Ordered compact snippet 2. |  |  | Ordered compact notes 2",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_compact_lines"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert [row["candidate_id"] for row in stored["result_records"]] == [first_seed_id, second_seed_id]
    assert all(row["import_format"] == "ordered_compact_lines" for row in stored["result_records"])
    assert stored["result_records"][0]["selected"] is True


def test_search_query_execution_import_results_accepts_ordered_tsv_lines(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-ordered-tsv-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Ordered TSV article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# URL<TAB>Title<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes",
                    "https://www.scopus.com/record/ordered-tsv-1\tOrdered TSV result 1\tOrdered TSV snippet 1.\t\ttrue\tOrdered TSV notes 1",
                    "https://www.scopus.com/record/ordered-tsv-2\tOrdered TSV result 2\tOrdered TSV snippet 2.\t\t\tOrdered TSV notes 2",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_tsv_lines"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert [row["candidate_id"] for row in stored["result_records"]] == [first_seed_id, second_seed_id]
    assert all(row["import_format"] == "ordered_tsv_lines" for row in stored["result_records"])
    assert stored["result_records"][0]["selected"] is True


def test_search_query_execution_import_results_accepts_ordered_tsv_lines_with_title_first(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-ordered-tsv-title-first-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Ordered TSV title-first article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# Title<TAB>URL<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes",
                    "Ordered TSV title-first result 1\thttps://www.scopus.com/record/ordered-tsv-title-first-1\tOrdered TSV title-first snippet 1.\t\ttrue\tOrdered TSV title-first notes 1",
                    "Ordered TSV title-first result 2\thttps://www.scopus.com/record/ordered-tsv-title-first-2\tOrdered TSV title-first snippet 2.\t\t\tOrdered TSV title-first notes 2",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_tsv_lines"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["source_url"] == "https://www.scopus.com/record/ordered-tsv-title-first-1"
    assert stored["result_records"][0]["search_result_title"] == "Ordered TSV title-first result 1"
    assert stored["result_records"][1]["source_url"] == "https://www.scopus.com/record/ordered-tsv-title-first-2"
    assert stored["result_records"][1]["search_result_title"] == "Ordered TSV title-first result 2"


def test_search_query_execution_import_results_accepts_embedded_link_first_column(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-embedded-link-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Embedded link article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# [Title](URL)<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes",
                    "[Embedded link result 1](https://www.scopus.com/record/embedded-link-1)\tEmbedded link snippet 1.\t\ttrue\tEmbedded link notes 1",
                    "Embedded link result 2 (https://www.scopus.com/record/embedded-link-2)\tEmbedded link snippet 2.\t\t\tEmbedded link notes 2",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_tsv_lines"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["source_url"] == "https://www.scopus.com/record/embedded-link-1"
    assert stored["result_records"][0]["search_result_title"] == "Embedded link result 1"
    assert stored["result_records"][0]["search_result_snippet"] == "Embedded link snippet 1."
    assert stored["result_records"][1]["source_url"] == "https://www.scopus.com/record/embedded-link-2"
    assert stored["result_records"][1]["search_result_title"] == "Embedded link result 2"
    assert stored["result_records"][1]["search_result_snippet"] == "Embedded link snippet 2."


def test_search_query_execution_import_results_accepts_flexible_tsv_rows_with_extra_columns(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-flex-tsv-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Flexible TSV article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# Rank<TAB>Title<TAB>Year<TAB>Source<TAB>URL<TAB>Snippet",
                    "1\tFlexible TSV result 1\t2024\tJournal A\thttps://www.scopus.com/record/flex-tsv-1\tFlexible TSV snippet 1.",
                    "2\tFlexible TSV result 2\t2025\tJournal B\thttps://www.scopus.com/record/flex-tsv-2\tFlexible TSV snippet 2.",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_tsv_lines"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["source_url"] == "https://www.scopus.com/record/flex-tsv-1"
    assert stored["result_records"][0]["search_result_title"] == "Flexible TSV result 1"
    assert stored["result_records"][0]["search_result_snippet"] == "Flexible TSV snippet 1."
    assert stored["result_records"][0]["notes"] == "Year: 2024 | Source: Journal A"
    assert stored["result_records"][1]["source_url"] == "https://www.scopus.com/record/flex-tsv-2"
    assert stored["result_records"][1]["search_result_title"] == "Flexible TSV result 2"
    assert stored["result_records"][1]["search_result_snippet"] == "Flexible TSV snippet 2."
    assert stored["result_records"][1]["notes"] == "Year: 2025 | Source: Journal B"


def test_search_query_execution_import_results_accepts_header_aware_tsv_any_order(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-header-tsv-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Header TSV article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# Source\tYear\tAbstract\tLink\tTitle\tSelected\tNotes",
                    "Journal A\t2024\tHeader-aware snippet 1.\thttps://www.scopus.com/record/header-tsv-1\tHeader-aware result 1\ttrue\tOperator note 1",
                    "Journal B\t2025\tHeader-aware snippet 2.\thttps://www.scopus.com/record/header-tsv-2\tHeader-aware result 2\t\tOperator note 2",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    assert payload["summary"]["import_formats"] == ["ordered_tsv_lines"]
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["source_url"] == "https://www.scopus.com/record/header-tsv-1"
    assert stored["result_records"][0]["search_result_title"] == "Header-aware result 1"
    assert stored["result_records"][0]["search_result_snippet"] == "Header-aware snippet 1."
    assert stored["result_records"][0]["selected"] is True
    assert "Operator note 1" in stored["result_records"][0]["notes"]
    assert "Source: Journal A" in stored["result_records"][0]["notes"]
    assert "Year: 2024" in stored["result_records"][0]["notes"]
    assert stored["result_records"][1]["source_url"] == "https://www.scopus.com/record/header-tsv-2"
    assert stored["result_records"][1]["search_result_title"] == "Header-aware result 2"
    assert stored["result_records"][1]["search_result_snippet"] == "Header-aware snippet 2."


def test_search_query_execution_import_results_uses_provider_fallback_headers_as_snippet(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=seed_id,
        record={
            "provider_key": "ieee",
            "title": "IEEE header article",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/",
            "keywords": ["owner", "operator"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: owner_operator_boundary. Primary query: warehouse owner operator utility boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n".join(
                [
                    "# Document Title\tDocument Link\tPublication Year\tIndex Terms\tSelected\tNotes",
                    "IEEE owner/operator result\thttps://ieeexplore.ieee.org/document/provider-fallback-1\t2026\towner operator utility boundary\ttrue\tImported from IEEE table",
                ]
            ),
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["search_result_title"] == "IEEE owner/operator result"
    assert stored["result_records"][0]["search_result_snippet"] == "owner operator utility boundary"
    assert stored["result_records"][0]["selected"] is True
    assert "Publication Year: 2026" in stored["result_records"][0]["notes"]


def test_congruence_brain_exposes_provider_capture_sheet_for_search_batch(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    for candidate_id in seed_payload["seeded_candidate_ids"][:2]:
        client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": candidate_id})

    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    batch_plan = refreshed["search_query_execution_batch_plan"]

    assert batch_plan["available"] is True
    assert "ordered_result_import_provider_capture_sheet_template" in batch_plan
    assert "# Row 1 · Candidate:" in batch_plan["ordered_result_import_provider_capture_sheet_template"]
    assert "# Primary query:" in batch_plan["ordered_result_import_provider_capture_sheet_template"]
    assert "search_execution_provider_sheet_template" in batch_plan
    assert "# Search line 1:" in batch_plan["search_execution_provider_sheet_template"]
    assert batch_plan["search_execution_provider_guide"]["preferred_surface"]
    assert "search_execution_capture_workbook_template" in batch_plan
    assert "Candidate ID:" in batch_plan["search_execution_capture_workbook_template"]
    assert "URL:" in batch_plan["search_execution_capture_workbook_template"]


def test_search_query_execution_import_results_accepts_provider_search_workbook(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-workbook-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Workbook article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    batch_plan = dashboard_module._congruence_brain_activity(fake_run)["search_query_execution_batch_plan"]
    assert "search_execution_capture_workbook_template" in batch_plan
    workbook = "\n---\n".join(
        [
            "\n".join(
                [
                    "# Provider search workbook · scopus · general_structural_prior_expansion",
                    f"# Row 1 · Candidate: {first_seed_id}",
                    f"Candidate ID: {first_seed_id}",
                    "URL: https://www.scopus.com/record/workbook-1",
                    "Title: Workbook result 1",
                    "Snippet: Workbook snippet 1.",
                    "Selected: true",
                    "Excerpt: ",
                    "Notes: Workbook notes 1",
                ]
            ),
            "\n".join(
                [
                    f"# Row 2 · Candidate: {second_seed_id}",
                    f"Candidate ID: {second_seed_id}",
                    "URL: https://www.scopus.com/record/workbook-2",
                    "Title: Workbook result 2",
                    "Snippet: Workbook snippet 2.",
                    "Selected: ",
                    "Excerpt: ",
                    "Notes: Workbook notes 2",
                ]
            ),
        ]
    )

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": workbook,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["imported_count"] == 2
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["candidate_id"] == first_seed_id
    assert stored["result_records"][0]["search_result_title"] == "Workbook result 1"
    assert stored["result_records"][0]["selected"] is True
    assert stored["result_records"][1]["candidate_id"] == second_seed_id
    assert stored["result_records"][1]["search_result_snippet"] == "Workbook snippet 2."


def test_search_query_execution_import_results_accepts_provider_native_tsv_without_header(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=seed_id,
        record={
            "provider_key": "ieee",
            "title": "IEEE native row article",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/",
            "keywords": ["owner", "operator"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: owner_operator_boundary. Primary query: warehouse owner operator utility boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "IEEE owner/operator result\thttps://ieeexplore.ieee.org/document/provider-native-no-header\t2026\towner operator utility boundary\ttrue\tImported without provider header",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    stored = json.loads((tmp_path / "search-query-result-imports" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["result_records"][0]["source_url"] == "https://ieeexplore.ieee.org/document/provider-native-no-header"
    assert stored["result_records"][0]["search_result_title"] == "IEEE owner/operator result"
    assert stored["result_records"][0]["search_result_snippet"] == "owner operator utility boundary"
    assert stored["result_records"][0]["selected"] is True
    assert "Publication Year: 2026" in stored["result_records"][0]["notes"]


def test_search_query_execution_import_results_can_auto_resolve_singleton_with_excerpt(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "auto_capture_singleton_candidates": True,
            "search_result_import_records": [
                {
                    "candidate_id": seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/auto-resolve-1",
                    "search_result_title": "Auto resolve result 1",
                    "search_result_snippet": "Visible auto resolve snippet 1.",
                    "reference_excerpt": "Real visible excerpt captured at import time.",
                    "notes": "Imported with excerpt already visible.",
                }
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["auto_captured_singleton_count"] == 1
    refreshed = payload["congruence_brain"]
    row = next(
        item for item in refreshed["licensed_research"]["article_reference_register"] if item["candidate_id"] == seed_id
    )
    assert row["reference_state"] == "manual_text_enriched"
    assert row["source_url"] == "https://www.scopus.com/record/auto-resolve-1"
    assert row["reference_excerpt"] == "Real visible excerpt captured at import time."


def test_search_query_execution_import_results_can_auto_promote_selected_multi_option(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_records": [
                {
                    "candidate_id": seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/selected-a",
                    "search_result_title": "Selected result A",
                    "search_result_snippet": "Visible snippet A.",
                },
                {
                    "candidate_id": seed_id,
                    "rank": 2,
                    "source_url": "https://www.scopus.com/record/selected-b",
                    "search_result_title": "Selected result B",
                    "search_result_snippet": "Visible snippet B.",
                    "selected": True,
                    "notes": "Operator already knows B is the correct hit.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["auto_selected_count"] == 1
    assert payload["summary"]["auto_selected_candidate_ids"] == [seed_id]
    refreshed = payload["congruence_brain"]
    capture_row = next(
        row for row in refreshed["search_result_capture_register"] if row["candidate_id"] == seed_id
    )
    assert capture_row["capture_state"] == "result_captured"
    assert capture_row["source_url"] == "https://www.scopus.com/record/selected-b"
    assert capture_row["captured_result_title"] == "Selected result B"


def test_search_query_execution_import_results_can_auto_resolve_selected_multi_option_with_excerpt(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    response = client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_records": [
                {
                    "candidate_id": seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/selected-resolve-a",
                    "search_result_title": "Selected resolve result A",
                    "search_result_snippet": "Visible resolve snippet A.",
                },
                {
                    "candidate_id": seed_id,
                    "rank": 2,
                    "source_url": "https://www.scopus.com/record/selected-resolve-b",
                    "search_result_title": "Selected resolve result B",
                    "search_result_snippet": "Visible resolve snippet B.",
                    "selected": True,
                    "reference_excerpt": "Real visible excerpt for the selected multi-option result.",
                    "notes": "Selected result already includes the excerpt.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["auto_selected_count"] == 1
    assert payload["summary"]["auto_resolved_selected_count"] == 1
    refreshed = payload["congruence_brain"]
    row = next(
        item for item in refreshed["licensed_research"]["article_reference_register"] if item["candidate_id"] == seed_id
    )
    assert row["reference_state"] == "manual_text_enriched"
    assert row["source_url"] == "https://www.scopus.com/record/selected-resolve-b"
    assert row["reference_excerpt"] == "Real visible excerpt for the selected multi-option result."


def test_search_query_result_promote_uses_selected_imported_option(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})
    client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n---\n".join(
                [
                    "\n".join(
                        [
                            f"Candidate ID: {seed_id}",
                            "Rank: 1",
                            "URL: https://ieeexplore.ieee.org/document/import-top",
                            "Title: Imported top result",
                            "Snippet: Visible top snippet.",
                        ]
                    ),
                    "\n".join(
                        [
                            f"Candidate ID: {seed_id}",
                            "Rank: 2",
                            "URL: https://ieeexplore.ieee.org/document/import-second",
                            "Title: Imported second result",
                            "Snippet: Visible second snippet.",
                        ]
                    ),
                ]
            ),
        },
    )

    response = client.post(
        "/api/search-query-result-promote",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "option_index": 2,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["selected_option"]["source_url"] == "https://ieeexplore.ieee.org/document/import-second"
    assert payload["updated_row"]["reference_state"] == "query_seed_draft"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/import-second"
    assert payload["updated_row"]["acquisition_result"]["status"] == "query_seed_result_captured"


def test_search_query_result_promote_and_resolve_uses_selected_imported_option(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})
    client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_packet": "\n---\n".join(
                [
                    "\n".join(
                        [
                            f"Candidate ID: {seed_id}",
                            "Rank: 1",
                            "URL: https://ieeexplore.ieee.org/document/import-resolve-top",
                            "Title: Imported top result",
                            "Snippet: Visible top snippet.",
                        ]
                    ),
                    "\n".join(
                        [
                            f"Candidate ID: {seed_id}",
                            "Rank: 2",
                            "URL: https://ieeexplore.ieee.org/document/import-resolve-second",
                            "Title: Imported second result",
                            "Snippet: Visible second snippet.",
                        ]
                    ),
                ]
            ),
        },
    )

    response = client.post(
        "/api/search-query-result-promote-and-resolve",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "option_index": 2,
            "reference_excerpt": "Real visible excerpt confirming the article content beyond the search-result snippet.",
            "notes": "Resolved in one step from imported option.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["selected_option"]["source_url"] == "https://ieeexplore.ieee.org/document/import-resolve-second"
    assert payload["updated_row"]["reference_state"] == "manual_text_enriched"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/import-resolve-second"
    assert payload["updated_row"]["acquisition_result"]["visible_text"].startswith("Real visible excerpt")
    assert payload["updated_row"]["acquisition_result"]["search_result_title"] == "Imported second result"


def test_search_query_result_promote_batch_promotes_visible_options(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-promote-batch-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Promote batch article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})
    client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_records": [
                {
                    "candidate_id": first_seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/promote-batch-1",
                    "search_result_title": "Promote batch result 1",
                    "search_result_snippet": "Visible promote batch snippet 1.",
                },
                {
                    "candidate_id": second_seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/promote-batch-2",
                    "search_result_title": "Promote batch result 2",
                    "search_result_snippet": "Visible promote batch snippet 2.",
                },
            ],
        },
    )

    response = client.post(
        "/api/search-query-result-promote-batch",
        json={"run_id": run_id},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["promoted_count"] == 2
    assert payload["summary"]["promotion_formats"] == ["visible_batch"]
    assert all(row["updated_row"]["reference_state"] == "query_seed_draft" for row in payload["rows"])
    assert all(
        row["updated_row"]["acquisition_result"]["status"] == "query_seed_result_captured"
        for row in payload["rows"]
    )


def test_search_query_result_promote_and_resolve_batch_resolves_visible_options(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-scopus-resolve-batch-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "scopus",
            "title": "Resolve batch article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://www.scopus.com/",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )

    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})
    client.post(
        "/api/search-query-execution-import-results",
        json={
            "run_id": run_id,
            "search_result_import_records": [
                {
                    "candidate_id": first_seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/resolve-batch-1",
                    "search_result_title": "Resolve batch result 1",
                    "search_result_snippet": "Visible resolve batch snippet 1.",
                },
                {
                    "candidate_id": second_seed_id,
                    "rank": 1,
                    "source_url": "https://www.scopus.com/record/resolve-batch-2",
                    "search_result_title": "Resolve batch result 2",
                    "search_result_snippet": "Visible resolve batch snippet 2.",
                },
            ],
        },
    )

    response = client.post(
        "/api/search-query-result-promote-and-resolve-batch",
        json={
            "run_id": run_id,
            "resolution_batch_records": [
                {
                    "candidate_id": first_seed_id,
                    "option_index": 1,
                    "reference_excerpt": "Real visible excerpt for imported batch result 1.",
                    "notes": "Resolved batch 1.",
                },
                {
                    "candidate_id": second_seed_id,
                    "option_index": 1,
                    "reference_excerpt": "Real visible excerpt for imported batch result 2.",
                    "notes": "Resolved batch 2.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["resolved_count"] == 2
    assert payload["summary"]["resolution_formats"] == ["structured_records"]
    assert all(row["updated_row"]["reference_state"] == "manual_text_enriched" for row in payload["rows"])
    assert all(
        row["updated_row"]["acquisition_result"]["visible_text"].startswith("Real visible excerpt")
        for row in payload["rows"]
    )


def test_article_reference_capture_search_result_batch_updates_multiple_drafts(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_ids = seed_payload["seeded_candidate_ids"][:2]
    for seed_id in seed_ids:
        dashboard_module.app.test_client().post(
            "/api/article-reference-read",
            json={"run_id": run_id, "candidate_id": seed_id},
        )

    batch_packet = "\n---\n".join(
        [
            "\n".join(
                [
                    f"Candidate ID: {seed_ids[0]}",
                    "URL: https://www.scopus.com/record/a",
                    "Title: Scopus result A",
                    "Snippet: Visible snippet A",
                    "Notes: Captured in batch A",
                ]
            ),
            "\n".join(
                [
                    f"Candidate ID: {seed_ids[1]}",
                    "URL: https://www.scopus.com/record/b",
                    "Title: Scopus result B",
                    "Snippet: Visible snippet B",
                    "Notes: Captured in batch B",
                ]
            ),
        ]
    )

    response = dashboard_module.app.test_client().post(
        "/api/article-reference-capture-search-result-batch",
        json={
            "run_id": run_id,
            "search_result_batch_packet": batch_packet,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["captured_count"] == 2
    assert payload["summary"]["capture_formats"] == ["packet"]
    after = dashboard_module._congruence_brain_activity(fake_run)
    updated_ids = {
        row["candidate_id"]
        for row in after["search_query_execution_register"]
        if row["execution_status"] == "result_captured_ready_for_excerpt"
    }
    assert set(seed_ids).issubset(updated_ids)


def test_article_reference_capture_search_result_batch_accepts_structured_records(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_ids = seed_payload["seeded_candidate_ids"][:2]
    for seed_id in seed_ids:
        dashboard_module.app.test_client().post(
            "/api/article-reference-read",
            json={"run_id": run_id, "candidate_id": seed_id},
        )

    response = dashboard_module.app.test_client().post(
        "/api/article-reference-capture-search-result-batch",
        json={
            "run_id": run_id,
            "search_result_batch_records": [
                {
                    "candidate_id": seed_ids[0],
                    "source_url": "https://www.scopus.com/record/structured-a",
                    "search_result_title": "Structured Scopus result A",
                    "search_result_snippet": "Structured visible snippet A",
                    "notes": "Structured capture A",
                },
                {
                    "candidate_id": seed_ids[1],
                    "url": "https://www.scopus.com/record/structured-b",
                    "title": "Structured Scopus result B",
                    "snippet": "Structured visible snippet B",
                    "notes": "Structured capture B",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["captured_count"] == 2
    assert payload["summary"]["capture_formats"] == ["structured_records"]
    after = dashboard_module._congruence_brain_activity(fake_run)
    updated_ids = {
        row["candidate_id"]
        for row in after["search_query_execution_register"]
        if row["execution_status"] == "result_captured_ready_for_excerpt"
    }
    assert set(seed_ids).issubset(updated_ids)


def test_reference_resolution_sequence_orders_pending_drafts_first() -> None:
    sequence = dashboard_module._build_reference_resolution_sequence(
        article_reference_register=[
            {
                "candidate_id": "queryseed-b",
                "provider_key": "springer",
                "title": "B draft",
                "reference_state": "query_seed_draft",
            },
            {
                "candidate_id": "resolved-a",
                "provider_key": "ieee",
                "title": "A resolved",
                "reference_state": "manual_text_enriched",
            },
            {
                "candidate_id": "queryseed-a",
                "provider_key": "ieee",
                "title": "A draft",
                "reference_state": "query_seed_draft",
            },
        ]
    )

    assert sequence["summary"]["pending"] == 2
    assert sequence["current_row"]["candidate_id"] == "queryseed-a"
    assert [row["candidate_id"] for row in sequence["next_rows"]] == ["queryseed-b"]


def test_reference_resolution_batch_plan_prefers_same_provider() -> None:
    sequence = dashboard_module._build_reference_resolution_sequence(
        article_reference_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "provider_key": "scopus",
                "source_family": "licensed_research_discovery",
                "title": "Scopus 01",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {"source_url": "", "suggested_notes": "Scopus note"},
            },
            {
                "candidate_id": "queryseed-ieee-01",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE 01",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {"source_url": "", "suggested_notes": "IEEE note 01"},
            },
            {
                "candidate_id": "queryseed-ieee-02",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE 02",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {"source_url": "", "suggested_notes": "IEEE note 02"},
            },
        ]
    )
    sequence["current_row"] = next(
        row for row in sequence["rows"] if row["candidate_id"] == "queryseed-ieee-01"
    )
    batch_plan = dashboard_module._build_reference_resolution_batch_plan(
        article_reference_register=sequence["rows"],
        reference_resolution_sequence=sequence,
    )

    assert batch_plan["available"] is True
    assert batch_plan["batch_mode"] == "same_provider"
    assert batch_plan["provider_keys"] == ["ieee"]
    assert [row["candidate_id"] for row in batch_plan["candidate_rows"]] == [
        "queryseed-ieee-01",
        "queryseed-ieee-02",
    ]


def test_reference_resolution_batch_plan_prefers_query_family_and_evidence_intent_over_provider_only() -> None:
    sequence = dashboard_module._build_reference_resolution_sequence(
        article_reference_register=[
            {
                "candidate_id": "queryseed-ieee-current",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE tariff boundary current",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "source_url": "",
                    "query_family": "tariff_boundary",
                    "evidence_targets": ["utility tariff", "lease matrix"],
                    "suggested_notes": "Current tariff boundary note",
                },
            },
            {
                "candidate_id": "queryseed-ieee-maintenance",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE maintenance candidate",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "source_url": "",
                    "query_family": "maintenance_reliability",
                    "evidence_targets": ["maintenance program", "downtime history"],
                    "suggested_notes": "Maintenance note",
                },
            },
            {
                "candidate_id": "queryseed-springer-tariff",
                "provider_key": "springer",
                "source_family": "licensed_research_fulltext",
                "title": "Springer tariff boundary candidate",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "source_url": "",
                    "query_family": "tariff_boundary",
                    "evidence_targets": ["utility tariff", "lease matrix"],
                    "suggested_notes": "Springer tariff boundary note",
                },
            },
        ]
    )
    sequence["current_row"] = next(
        row for row in sequence["rows"] if row["candidate_id"] == "queryseed-ieee-current"
    )
    batch_plan = dashboard_module._build_reference_resolution_batch_plan(
        article_reference_register=sequence["rows"],
        reference_resolution_sequence=sequence,
    )

    assert batch_plan["available"] is True
    assert batch_plan["batch_mode"] == "same_source_family_same_query_family_same_evidence_intent"
    assert [row["candidate_id"] for row in batch_plan["candidate_rows"]] == [
        "queryseed-ieee-current",
        "queryseed-springer-tariff",
    ]
    assert batch_plan["query_families"] == ["tariff_boundary"]
    assert batch_plan["evidence_targets"] == ["utility tariff", "lease matrix"]
    assert "same source family" in batch_plan["batch_reason"].lower()
    assert "# Query family: tariff_boundary" in batch_plan["packet_template"]
    assert "# Evidence targets: utility tariff, lease matrix" in batch_plan["packet_template"]


def test_reference_resolution_batch_plan_exposes_quick_and_full_templates() -> None:
    sequence = dashboard_module._build_reference_resolution_sequence(
        article_reference_register=[
            {
                "candidate_id": "queryseed-ieee-quick-01",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE tariff boundary current",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "provider_display_name": "IEEE",
                    "launch_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
                    "search_surface": "IEEE metadata + abstract + index terms",
                    "execution_hint": "Start with IEEE using metadata + abstract search.",
                    "query_family": "tariff_boundary",
                    "primary_query": "warehouse tariff demand charge",
                    "pivot_query": "owner operator split",
                    "evidence_targets": ["utility tariff", "lease matrix"],
                    "suggested_notes": "Quick template note",
                    "source_url": "",
                },
            },
            {
                "candidate_id": "queryseed-ieee-quick-02",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE tariff boundary second",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "provider_display_name": "IEEE",
                    "launch_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
                    "search_surface": "IEEE metadata + abstract + index terms",
                    "execution_hint": "Start with IEEE using metadata + abstract search.",
                    "query_family": "tariff_boundary",
                    "primary_query": "warehouse tariff demand charge",
                    "pivot_query": "owner operator split",
                    "evidence_targets": ["utility tariff", "lease matrix"],
                    "suggested_notes": "Quick template note 2",
                    "source_url": "",
                },
            },
        ]
    )
    batch_plan = dashboard_module._build_reference_resolution_batch_plan(
        article_reference_register=sequence["rows"],
        reference_resolution_sequence=sequence,
    )

    assert batch_plan["available"] is True
    assert "Title:" not in batch_plan["quick_packet_template"]
    assert "DOI:" not in batch_plan["quick_packet_template"]
    assert "Journal:" not in batch_plan["quick_packet_template"]
    assert "Year:" not in batch_plan["quick_packet_template"]
    assert "Excerpt:" in batch_plan["quick_packet_template"]
    assert "Title:" in batch_plan["full_packet_template"]
    assert "DOI:" in batch_plan["full_packet_template"]
    assert batch_plan["packet_template"] == batch_plan["quick_packet_template"]
    assert batch_plan["captured_ready"] is False


def test_reference_resolution_batch_plan_exposes_captured_quick_template_when_urls_are_present() -> None:
    sequence = dashboard_module._build_reference_resolution_sequence(
        article_reference_register=[
            {
                "candidate_id": "queryseed-ieee-captured-01",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE captured current",
                "source_url": "https://ieeexplore.ieee.org/document/captured-01",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "provider_display_name": "IEEE",
                    "launch_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
                    "query_family": "tariff_boundary",
                    "primary_query": "warehouse tariff demand charge",
                    "pivot_query": "owner operator split",
                    "evidence_targets": ["utility tariff", "lease matrix"],
                    "source_url": "https://ieeexplore.ieee.org/document/captured-01",
                },
            },
            {
                "candidate_id": "queryseed-ieee-captured-02",
                "provider_key": "ieee",
                "source_family": "licensed_research_fulltext",
                "title": "IEEE captured second",
                "source_url": "https://ieeexplore.ieee.org/document/captured-02",
                "reference_state": "query_seed_draft",
                "draft_resolution_prefill": {
                    "provider_display_name": "IEEE",
                    "launch_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
                    "query_family": "tariff_boundary",
                    "primary_query": "warehouse tariff demand charge",
                    "pivot_query": "owner operator split",
                    "evidence_targets": ["utility tariff", "lease matrix"],
                    "source_url": "https://ieeexplore.ieee.org/document/captured-02",
                },
            },
        ]
    )
    batch_plan = dashboard_module._build_reference_resolution_batch_plan(
        article_reference_register=sequence["rows"],
        reference_resolution_sequence=sequence,
    )

    assert batch_plan["captured_ready"] is True
    assert "Candidate ID: queryseed-ieee-captured-01" in batch_plan["captured_quick_packet_template"]
    assert "\nURL:" not in batch_plan["captured_quick_packet_template"]


def test_congruence_brain_exposes_current_reference_resolution_row(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    refreshed = dashboard_module._congruence_brain_activity(fake_run)

    assert refreshed["reference_resolution_queue_summary"]["pending"] >= 1
    assert refreshed["current_reference_resolution_row"]["candidate_id"] == seed_id
    assert refreshed["current_reference_resolution_row"]["reference_state"] == "query_seed_draft"
    assert refreshed["reference_resolution_batch_plan"]["available"] is True
    assert refreshed["reference_resolution_batch_plan"]["candidate_count"] >= 1


def test_article_reference_resolve_packet_can_resolve_query_seed_draft_in_one_step(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    packet = "\n".join(
        [
            "URL: https://ieeexplore.ieee.org/document/seed-456",
            "Title: Resolved IEEE article",
            "DOI: 10.1109/TIA.2026.456",
            "Journal: IEEE Transactions on Industry Applications",
            "Year: 2026",
            "Notes: Resolved from packet flow.",
            "Excerpt:",
            "This excerpt confirms the demand-charge timing mechanism and boundary leakage risk.",
        ]
    )
    response = dashboard_module.app.test_client().post(
        "/api/article-reference-resolve-packet",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "resolution_packet": packet,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["reference_state"] == "manual_text_enriched"
    assert payload["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/seed-456"
    assert payload["updated_row"]["doi"] == "10.1109/TIA.2026.456"
    assert payload["updated_row"]["journal"] == "IEEE Transactions on Industry Applications"
    assert payload["updated_row"]["published_year"] == "2026"
    assert payload["updated_row"]["acquisition_result"]["status"] == "query_seed_manual_capture"


def test_reference_resolution_queue_advances_after_packet_resolution(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": first_seed_id},
    )
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override="queryseed-ieee-extra-draft",
        record={
            "provider_key": "ieee",
            "title": "A second draft article",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary. Pivot query: owner operator split.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": "queryseed-ieee-extra-draft"},
    )

    before = dashboard_module._congruence_brain_activity(fake_run)
    current_draft_id = before["current_reference_resolution_row"]["candidate_id"]
    pending_before = before["reference_resolution_queue_summary"]["pending"]

    packet = "\n".join(
        [
            "URL: https://ieeexplore.ieee.org/document/current-draft",
            "Notes: Resolved current draft.",
            "Excerpt:",
            "This excerpt resolves the current draft and should advance the queue.",
        ]
    )
    dashboard_module.app.test_client().post(
        "/api/article-reference-resolve-packet",
        json={
            "run_id": run_id,
            "candidate_id": current_draft_id,
            "resolution_packet": packet,
        },
    )

    after = dashboard_module._congruence_brain_activity(fake_run)

    assert pending_before >= 2
    assert after["reference_resolution_queue_summary"]["pending"] == pending_before - 1
    assert after["current_reference_resolution_row"]["candidate_id"] != current_draft_id
    assert after["current_reference_resolution_row"]["reference_state"] == "query_seed_draft"


def test_reference_resolution_queue_advances_after_quick_resolution(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": first_seed_id},
    )
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override="queryseed-ieee-extra-draft-quick",
        record={
            "provider_key": "ieee",
            "title": "A second quick draft article",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary. Pivot query: owner operator split.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": "queryseed-ieee-extra-draft-quick"},
    )

    before = dashboard_module._congruence_brain_activity(fake_run)
    current_draft_id = before["current_reference_resolution_row"]["candidate_id"]
    pending_before = before["reference_resolution_queue_summary"]["pending"]

    dashboard_module.app.test_client().post(
        "/api/article-reference-quick-resolve",
        json={
            "run_id": run_id,
            "candidate_id": current_draft_id,
            "source_url": "https://ieeexplore.ieee.org/document/quick-current",
            "reference_excerpt": "Quick current excerpt.",
            "notes": "Quick queue advancement.",
        },
    )

    after = dashboard_module._congruence_brain_activity(fake_run)

    assert pending_before >= 2
    assert after["reference_resolution_queue_summary"]["pending"] == pending_before - 1
    assert after["current_reference_resolution_row"]["candidate_id"] != current_draft_id
    assert after["current_reference_resolution_row"]["reference_state"] == "query_seed_draft"


def test_article_reference_resolve_batch_can_resolve_multiple_drafts(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-ieee-batch-extra"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "ieee",
            "title": "Batch extra draft article",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary. Pivot query: owner operator split.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    batch_packet = "\n---\n".join(
        [
            "\n".join(
                [
                    f"Candidate ID: {first_seed_id}",
                    "URL: https://ieeexplore.ieee.org/document/batch-001",
                    "Notes: Batch resolved 1.",
                    "Excerpt:",
                    "This first batch excerpt confirms tariff timing.",
                ]
            ),
            "\n".join(
                [
                    f"Candidate ID: {second_seed_id}",
                    "URL: https://ieeexplore.ieee.org/document/batch-002",
                    "Title: Batch resolved title 2",
                    "Excerpt:",
                    "This second batch excerpt confirms boundary leakage.",
                ]
            ),
        ]
    )
    response = client.post(
        "/api/article-reference-resolve-batch",
        json={
            "run_id": run_id,
            "resolution_batch_packet": batch_packet,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["resolved_count"] == 2
    assert len(payload["rows"]) == 2
    assert all(row["updated_row"]["reference_state"] == "manual_text_enriched" for row in payload["rows"])
    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    assert refreshed["reference_resolution_queue_summary"]["pending"] == 0


def test_article_reference_resolve_batch_can_reuse_captured_urls(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-ieee-captured-batch-extra"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "ieee",
            "title": "Captured batch extra article",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary. Pivot query: owner operator split.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})
    client.post(
        "/api/article-reference-capture-search-result",
        json={
            "run_id": run_id,
            "candidate_id": first_seed_id,
            "source_url": "https://ieeexplore.ieee.org/document/captured-batch-001",
            "search_result_title": "Captured batch title 1",
            "search_result_snippet": "Visible result snippet batch 1.",
            "notes": "Captured from IEEE search result.",
        },
    )
    client.post(
        "/api/article-reference-capture-search-result",
        json={
            "run_id": run_id,
            "candidate_id": second_seed_id,
            "source_url": "https://ieeexplore.ieee.org/document/captured-batch-002",
            "search_result_title": "Captured batch title 2",
            "search_result_snippet": "Visible result snippet batch 2.",
            "notes": "Captured from IEEE search result.",
        },
    )

    batch_packet = "\n---\n".join(
        [
            "\n".join(
                [
                    f"Candidate ID: {first_seed_id}",
                    "Notes: Batch resolved using captured URL 1.",
                    "Excerpt:",
                    "This first batch excerpt reuses the captured article URL.",
                ]
            ),
            "\n".join(
                [
                    f"Candidate ID: {second_seed_id}",
                    "Notes: Batch resolved using captured URL 2.",
                    "Excerpt:",
                    "This second batch excerpt reuses the captured article URL too.",
                ]
            ),
        ]
    )
    response = client.post(
        "/api/article-reference-resolve-batch",
        json={
            "run_id": run_id,
            "resolution_batch_packet": batch_packet,
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["resolved_count"] == 2
    assert payload["rows"][0]["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/captured-batch-001"
    assert payload["rows"][1]["updated_row"]["source_url"] == "https://ieeexplore.ieee.org/document/captured-batch-002"
    assert "captured article URL" in payload["rows"][0]["updated_row"]["reference_excerpt"]


def test_article_reference_resolve_batch_accepts_structured_records(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-ieee-structured-batch-2"
    dashboard_module._upsert_manual_discovery_candidate(
        run_id=run_id,
        candidate_id_override=second_seed_id,
        record={
            "provider_key": "ieee",
            "title": "Structured batch article 2",
            "doi": "",
            "journal": "",
            "published_year": "",
            "source_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
            "keywords": ["tariff", "boundary"],
            "abstract": "",
            "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
            "reference_excerpt": "",
            "operator_decision": "candidate",
        },
        refresh_after=False,
    )
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})

    response = client.post(
        "/api/article-reference-resolve-batch",
        json={
            "run_id": run_id,
            "resolution_batch_records": [
                {
                    "candidate_id": first_seed_id,
                    "source_url": "https://ieeexplore.ieee.org/document/structured-batch-001",
                    "reference_excerpt": "Structured batch excerpt 1.",
                    "notes": "Structured batch note 1.",
                },
                {
                    "candidate_id": second_seed_id,
                    "url": "https://ieeexplore.ieee.org/document/structured-batch-002",
                    "excerpt": "Structured batch excerpt 2.",
                    "notes": "Structured batch note 2.",
                },
            ],
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["summary"]["resolved_count"] == 2
    assert payload["summary"]["resolution_formats"] == ["structured_records"]
    assert all(row["updated_row"]["reference_state"] == "manual_text_enriched" for row in payload["rows"])


def test_reference_resolution_queue_advances_after_batch_resolution(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    first_seed_id = seed_payload["seeded_candidate_ids"][0]
    second_seed_id = "queryseed-ieee-queue-extra-2"
    third_seed_id = "queryseed-ieee-queue-extra-3"
    for candidate_id, title in [
        (second_seed_id, "Queue extra draft article 2"),
        (third_seed_id, "Queue extra draft article 3"),
    ]:
        dashboard_module._upsert_manual_discovery_candidate(
            run_id=run_id,
            candidate_id_override=candidate_id,
            record={
                "provider_key": "ieee",
                "title": title,
                "doi": "",
                "journal": "",
                "published_year": "",
                "source_url": "https://ieeexplore.ieee.org/search/searchresult.jsp",
                "keywords": ["tariff", "boundary"],
                "abstract": "",
                "notes": f"Combination: {current_id}. Query family: tariff_boundary. Primary query: warehouse tariff boundary. Pivot query: owner operator split.",
                "reference_excerpt": "",
                "operator_decision": "candidate",
            },
            refresh_after=False,
        )
    client = dashboard_module.app.test_client()
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": first_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": second_seed_id})
    client.post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": third_seed_id})

    before = dashboard_module._congruence_brain_activity(fake_run)
    assert before["reference_resolution_queue_summary"]["pending"] >= 3
    batch_packet = "\n---\n".join(
        [
            "\n".join(
                [
                    f"Candidate ID: {before['current_reference_resolution_row']['candidate_id']}",
                    "URL: https://ieeexplore.ieee.org/document/batch-current",
                    "Excerpt:",
                    "Batch current excerpt.",
                ]
            ),
            "\n".join(
                [
                    f"Candidate ID: {before['next_reference_resolution_rows'][0]['candidate_id']}",
                    "URL: https://ieeexplore.ieee.org/document/batch-next",
                    "Excerpt:",
                    "Batch next excerpt.",
                ]
            ),
        ]
    )
    client.post(
        "/api/article-reference-resolve-batch",
        json={
            "run_id": run_id,
            "resolution_batch_packet": batch_packet,
        },
    )
    after = dashboard_module._congruence_brain_activity(fake_run)

    assert after["reference_resolution_queue_summary"]["pending"] == before["reference_resolution_queue_summary"]["pending"] - 2
    assert after["current_reference_resolution_row"]["candidate_id"] not in {
        before["current_reference_resolution_row"]["candidate_id"],
        before["next_reference_resolution_rows"][0]["candidate_id"],
    }
    assert after["current_reference_resolution_row"]["reference_state"] == "query_seed_draft"


def test_reference_resolution_batch_plan_exposes_json_templates(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post("/api/article-reference-read", json={"run_id": run_id, "candidate_id": seed_id})

    refreshed = dashboard_module._congruence_brain_activity(fake_run)
    plan = refreshed["reference_resolution_batch_plan"]

    assert plan["available"] is True
    assert "\"candidate_id\"" in plan["quick_json_template"]
    assert "\"reference_excerpt\"" in plan["quick_json_template"]


def test_article_reference_edit_can_auto_accept_and_update_identity_on_resolve(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]
    seed_payload = dashboard_module.app.test_client().post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]
    dashboard_module.app.test_client().post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/article-reference-edit",
        json={
            "run_id": run_id,
            "candidate_id": seed_id,
            "auto_accept_discovery_candidate": True,
            "patch": {
                "source_url": "https://ieeexplore.ieee.org/document/seed-456",
                "reference_excerpt": "Resolved excerpt with real IEEE evidence.",
                "notes": "Resolved and accepted from query-seed draft.",
                "resolved_title": "Resolved IEEE Article Title",
                "resolved_doi": "10.1109/RESOLVED.2026.456",
                "reference_state": "manual_text_enriched",
            },
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    discovery_rows = payload["licensed_research"]["discovery_candidate_review_register"]
    updated_candidate = next(row for row in discovery_rows if row["candidate_id"] == seed_id)
    assert updated_candidate["operator_decision"] == "accepted_for_reference_use"
    assert updated_candidate["title"] == "Resolved IEEE Article Title"
    assert updated_candidate["doi"] == "10.1109/RESOLVED.2026.456"
    assert updated_candidate["source_url"] == "https://ieeexplore.ieee.org/document/seed-456"


def test_latent_cluster_decision_endpoint_persists_batch_decisions(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    cluster_id = preview["latent_combination_cluster_register"][0]["cluster_id"]
    cluster_candidate_ids = set(preview["latent_combination_cluster_register"][0]["candidate_ids"])

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/latent-cluster-decision",
        json={
            "run_id": run_id,
            "cluster_id": cluster_id,
            "operator_decision": "rejected_for_case_use",
            "decision_reason": "Suppressed generic template in dashboard test.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    updated_ids = {row["combination_id"] for row in payload["updated_rows"]}
    assert updated_ids == cluster_candidate_ids.intersection(updated_ids)
    assert payload["updated_rows"]
    assert all(row["operator_decision"] == "rejected_for_case_use" for row in payload["updated_rows"])

    stored = json.loads((tmp_path / "combination" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    stored_ids = {row["combination_id"] for row in stored["decisions"]}
    assert updated_ids.issubset(stored_ids)


def test_latent_cluster_split_endpoint_persists_override_and_refreshes_clusters(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    source_cluster = next(row for row in preview["latent_combination_cluster_register"] if row["candidate_count"] > 1)
    split_candidate_id = source_cluster["candidate_ids"][0]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/latent-cluster-split",
        json={
            "run_id": run_id,
            "source_cluster_id": source_cluster["cluster_id"],
            "candidate_ids": [split_candidate_id],
            "cluster_label": "Forklift tariff split",
            "decision_reason": "Split dashboard cluster for a more asset-specific read.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    refreshed_clusters = payload["congruence_brain"]["latent_combination_cluster_register"]
    split_cluster = next(
        row for row in refreshed_clusters if split_candidate_id in set(row.get("candidate_ids", [])) and row.get("override_state") in {"split", "split_and_merged"}
    )
    assert split_cluster["candidate_count"] == 1
    assert split_cluster["cluster_label"] == "Forklift tariff split"
    original_cluster = next(row for row in refreshed_clusters if row["cluster_id"] == source_cluster["cluster_id"])
    assert original_cluster["candidate_count"] == source_cluster["candidate_count"] - 1

    stored = json.loads((tmp_path / "latent-cluster-overrides" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    stored_split_ids = {row["candidate_id"] for row in stored["split_assignments"]}
    assert split_candidate_id in stored_split_ids


def test_latent_cluster_merge_endpoint_persists_override_and_refreshes_clusters(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    preview = dashboard_module._congruence_brain_activity(fake_run)
    target_cluster = preview["latent_combination_cluster_register"][0]
    source_cluster = preview["latent_combination_cluster_register"][-1]

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/latent-cluster-merge",
        json={
            "run_id": run_id,
            "source_cluster_id": source_cluster["cluster_id"],
            "target_cluster_id": target_cluster["cluster_id"],
            "decision_reason": "Merge dashboard clusters into a single campaign bucket.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    refreshed_clusters = payload["congruence_brain"]["latent_combination_cluster_register"]
    merged_target = next(row for row in refreshed_clusters if row["cluster_id"] == target_cluster["cluster_id"])
    assert merged_target["candidate_count"] == target_cluster["candidate_count"] + source_cluster["candidate_count"]
    assert source_cluster["cluster_id"] not in {row["cluster_id"] for row in refreshed_clusters}

    stored = json.loads((tmp_path / "latent-cluster-overrides" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    stored_merges = {row["source_cluster_id"]: row["target_cluster_id"] for row in stored["merge_assignments"]}
    assert stored_merges[source_cluster["cluster_id"]] == target_cluster["cluster_id"]


def test_promotion_decision_endpoint_persists_and_merges(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {"pattern_id": "licensed_boundary_candidate", "promotion_state": "ready_for_registry_review"}
            ]
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-decision",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "operator_decision": "accepted_for_registry_review",
            "decision_reason": "Accepted promotion in dashboard test.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["operator_decision"] == "accepted_for_registry_review"
    assert payload["updated_row"]["decision_reason"] == "Accepted promotion in dashboard test."

    stored = json.loads((tmp_path / "promotion-decisions" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["run_id"] == run_id
    assert stored["decisions"][0]["promotion_id"] == "pattern::licensed_boundary_candidate"
    assert stored["decisions"][0]["operator_decision"] == "accepted_for_registry_review"


def test_source_family_trigger_endpoint_persists_queue_and_refreshes_brain(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/source-family-trigger",
        json={
            "run_id": run_id,
            "source_family": "licensed_research_fulltext",
            "reason": "Queue deeper IEEE and Springer full text coverage.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["source_family"] == "licensed_research_fulltext"
    assert payload["updated_row"]["status"] == "queued"
    assert "ieee" in payload["updated_row"]["recommended_provider_keys"]

    stored = json.loads((tmp_path / "research-campaign-triggers" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["run_id"] == run_id
    assert stored["triggers"][0]["source_family"] == "licensed_research_fulltext"
    assert stored["triggers"][0]["status"] == "queued"


def test_source_family_exhausted_endpoint_persists_exhausted_state(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "asset_context": {
            "solar_profile": "morning",
            "operating_rhythm": "early shift",
            "utility_tariff_context": "demand charge tariff",
            "control_boundary": "tenant operator split",
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/source-family-exhausted",
        json={
            "run_id": run_id,
            "source_family": "licensed_research_fulltext",
            "reason": "IEEE and Springer passes exhausted for this run.",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["status"] == "exhausted"
    stored = json.loads((tmp_path / "research-campaign-triggers" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["triggers"][0]["status"] == "exhausted"


def test_promotion_edit_endpoint_persists_and_updates_review_bundle(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {
                    "promotion_id": "pattern::licensed_boundary_candidate",
                    "pattern_id": "licensed_boundary_candidate",
                    "promotion_state": "ready_for_registry_review",
                    "source_basis_id": "licensed_research_public_technical_priors",
                    "document_ref": "doc::licensed::01",
                    "proposed_spec": {
                        "id": "licensed_boundary_candidate",
                        "version": "1.0.0",
                        "name": "Licensed Boundary Candidate",
                        "hypothesis": "Boundary ambiguity remains plausible.",
                        "minimum_evidence_to_activate": ["owner/operator split plausible"],
                        "minimum_evidence_to_confirm": ["lease matrix"],
                        "falsification_conditions": ["owner and operator aligned"],
                        "allowed_claim_language": "Boundary leakage remains plausible.",
                        "prohibited_claim_language": "The owner captures the savings.",
                        "financial_exposure_if_true": ["boundary leakage"],
                        "financial_exposure_if_false": ["extra diligence only"],
                        "tad_actions": ["VALIDATE_CONTROL_BOUNDARY"],
                    },
                }
            ]
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-edit",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "patch": {
                "name": "Edited Boundary Candidate",
                "hypothesis": "Edited hypothesis.",
                "minimum_evidence_to_activate": ["meter map", "lease matrix"],
                "minimum_evidence_to_confirm": ["meter map", "lease matrix", "utility responsibility"],
                "falsification_conditions": ["full alignment documented"],
                "allowed_claim_language": "Edited allowed language.",
                "prohibited_claim_language": "Edited prohibited language.",
                "financial_exposure_if_true": ["boundary leakage", "value capture ambiguity"],
                "financial_exposure_if_false": ["diligence only"],
                "tad_actions": ["VALIDATE_CONTROL_BOUNDARY", "PROHIBIT_ROI"],
            },
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["updated_row"]["subject_name"] == "Edited Boundary Candidate"
    assert payload["updated_row"]["minimum_evidence"] == ["meter map", "lease matrix"]
    assert payload["licensed_research"]["promotion_edit_store"]["stored_edit_count"] == 1

    stored = json.loads((tmp_path / "promotion-edits" / "run_oisk-dashboard.json").read_text(encoding="utf-8"))
    assert stored["edits"][0]["promotion_id"] == "pattern::licensed_boundary_candidate"
    assert stored["edits"][0]["patch"]["name"] == "Edited Boundary Candidate"


def test_discovery_candidate_decision_edit_and_reference_endpoints(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}, "licensed_research_activity": {}}
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())

    client = dashboard_module.app.test_client()
    decision_response = client.post(
        "/api/discovery-candidate-decision",
        json={
            "run_id": run_id,
            "candidate_id": "ieee-candidate-01",
            "operator_decision": "accepted_for_reference_use",
            "decision_reason": "Accepted candidate in dashboard test.",
        },
    )
    assert decision_response.status_code == 200
    decision_payload = decision_response.get_json()
    assert decision_payload["updated_row"]["operator_decision"] == "accepted_for_reference_use"

    edit_response = client.post(
        "/api/discovery-candidate-edit",
        json={
            "run_id": run_id,
            "candidate_id": "ieee-candidate-01",
            "patch": {
                "title": "Edited IEEE discovery title",
                "abstract": "Edited abstract with reactive power and compressed air.",
                "source_url": "https://ieeexplore.ieee.org/document/999003",
                "keywords": ["reactive power", "compressed air"],
                "notes": "Edited in dashboard test.",
                "expected_pdf_name": "edited-ieee.pdf",
            },
        },
    )
    assert edit_response.status_code == 200
    edit_payload = edit_response.get_json()
    assert edit_payload["updated_row"]["title"] == "Edited IEEE discovery title"
    assert edit_payload["updated_row"]["expected_pdf_name"] == "edited-ieee.pdf"

    monkeypatch.setattr(
        dashboard_module,
        "execute_licensed_document_acquisition",
        lambda **kwargs: {
            "research_document_manifest": {"provider_key": "ieee", "title": "Edited IEEE discovery title"},
            "acquisition_result": {"visible_text": "Reactive power enriched reference text.", "status": "success"},
        },
    )
    reference_response = client.post(
        "/api/article-reference-read",
        json={
            "run_id": run_id,
            "candidate_id": "ieee-candidate-01",
        },
    )
    assert reference_response.status_code == 200
    reference_payload = reference_response.get_json()
    assert reference_payload["updated_row"]["reference_state"] == "visible_text_enriched"
    assert "Reactive power" in reference_payload["updated_row"]["reference_excerpt"]
    assert reference_payload["accepted_discovery_candidate_bundle_manifest"]["exists"] is True
    assert reference_payload["reference_backed_promotion_manifest"]["exists"] is True

    batch_response = client.post(
        "/api/article-reference-read-batch",
        json={
            "run_id": run_id,
        },
    )
    assert batch_response.status_code == 200
    batch_payload = batch_response.get_json()
    assert batch_payload["summary"]["attempted_count"] == 1
    assert batch_payload["summary"]["visible_text_enriched_count"] == 1
    assert batch_payload["accepted_discovery_candidate_bundle_manifest"]["exists"] is True
    assert (
        batch_payload["licensed_research"]["accepted_discovery_candidate_bundle"]["summary"]["accepted_count"] == 1
    )
    assert (
        batch_payload["licensed_research"]["accepted_discovery_candidate_bundle"]["accepted_rows"][0]["reference_state"]
        == "visible_text_enriched"
    )

    bundle_response = client.get(
        "/api/accepted-discovery-candidates",
        query_string={"run_id": run_id},
    )
    assert bundle_response.status_code == 200
    bundle_payload = bundle_response.get_json()
    assert bundle_payload["accepted_discovery_candidate_bundle"]["summary"]["accepted_count"] == 1
    assert bundle_payload["accepted_discovery_candidate_bundle_manifest"]["exists"] is True


def test_manual_discovery_candidate_creation_builds_candidate_reference_and_promotions(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}, "licensed_research_activity": {}}
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    create_response = client.post(
        "/api/discovery-candidate-create",
        json={
            "run_id": run_id,
            "provider_key": "ieee",
            "title": "Manual reactive power and compressed air article",
            "source_url": "https://ieeexplore.ieee.org/document/999777",
            "doi": "10.1109/TIA.2026.999777",
            "journal": "IEEE Transactions on Industry Applications",
            "published_year": "2026",
            "keywords": ["reactive power", "compressed air", "manufacturing"],
            "abstract": "Reactive power exposure and compressed air leakage remain recurring hidden-loss modes in manufacturing facilities.",
            "reference_excerpt": "Visible page text confirms reactive power exposure and compressed air leakage as recurring hidden-loss modes.",
            "notes": "Manually added from dashboard.",
            "operator_decision": "accepted_for_reference_use",
        },
    )
    create_payload = create_response.get_json()

    assert create_response.status_code == 200
    assert create_payload["ok"] is True
    assert create_payload["updated_candidate_row"]["operator_decision"] == "accepted_for_reference_use"
    assert create_payload["updated_reference_row"]["reference_state"] == "manual_text_enriched"
    assert create_payload["accepted_discovery_candidate_bundle_manifest"]["exists"] is True
    assert create_payload["reference_backed_promotion_manifest"]["exists"] is True
    assert create_payload["licensed_research"]["accepted_discovery_candidate_bundle"]["summary"]["accepted_count"] == 1
    manifest = create_payload["reference_backed_promotion_manifest"]
    assert manifest["summary"]["accepted_reference_count"] == 1
    assert any(
        row["pattern_id"] == "reactive_power_exposure"
        for row in manifest["approved_pattern_promotion_register"]
    )


def test_manual_discovery_candidate_creation_preserves_explicit_source_family(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}, "licensed_research_activity": {}}
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    create_response = client.post(
        "/api/discovery-candidate-create",
        json={
            "run_id": run_id,
            "provider_key": "manual",
            "source_family": "utility_tariff_billing_guidance",
            "title": "Utility tariff guidance note",
            "source_url": "https://utility.example.com/rates/guide",
            "keywords": ["tariff", "demand charge", "billing"],
            "abstract": "Demand-charge guidance and billing interpretation for industrial customers.",
            "reference_excerpt": "Visible tariff guidance confirms demand-charge timing and billing interpretation details.",
            "notes": "Manual utility guidance capture.",
            "operator_decision": "accepted_for_reference_use",
        },
    )
    create_payload = create_response.get_json()

    assert create_response.status_code == 200
    assert create_payload["ok"] is True
    coverage_rows = create_payload["licensed_research"]["source_family_coverage_register"]
    utility_row = next(
        row
        for row in coverage_rows
        if row["source_family"] == "utility_tariff_billing_guidance"
    )
    assert utility_row["coverage_state"] == "thin"
    assert utility_row["capture_mode"] == "manual_reference_capture"
    reference_rows = create_payload["licensed_research"]["article_reference_register"]
    assert reference_rows[0]["source_family"] == "utility_tariff_billing_guidance"
    assert create_payload["licensed_research"]["source_coverage_summary"]["knowledge_atom_count"] >= 1
    assert any(
        row["source_family"] == "utility_tariff_billing_guidance"
        for row in create_payload["licensed_research"]["knowledge_atom_register"]
    )


def test_reference_backed_promotions_refresh_rebuilds_auto_drafts_from_accepted_refs(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}, "licensed_research_activity": {}}
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    dashboard_module._persist_discovery_candidate_decision_record(
        run_id,
        {
            "candidate_id": "ieee-candidate-01",
            "operator_decision": "accepted_for_reference_use",
            "decision_reason": "Accepted candidate in dashboard test.",
            "decision_timestamp": "2026-05-05T00:00:00Z",
            "decision_scope": "run",
        },
    )
    dashboard_module._persist_article_reference_record(
        run_id,
        {
            "candidate_id": "ieee-candidate-01",
            "reference_state": "visible_text_enriched",
            "acquisition_result": {
                "visible_text": (
                    "Reactive power exposure and compressed air leakage remain recurring hidden-loss modes in manufacturing "
                    "facilities, and premature sensor deployment can miss the dominant variable."
                ),
                "status": "success",
            },
            "research_document_manifest": {"provider_key": "ieee", "title": "Edited IEEE discovery title"},
            "updated_at": "2026-05-05T00:00:00Z",
        },
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/reference-backed-promotions-refresh",
        json={"run_id": run_id},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    manifest = payload["reference_backed_promotion_manifest"]
    assert manifest["summary"]["accepted_reference_count"] == 1
    assert manifest["summary"]["extraction_count"] == 1
    assert manifest["summary"]["pattern_promotion_count"] >= 2
    assert manifest["exists"] is True
    assert payload["knowledge_atom_refresh_summary"]["meaningful_delta"] is True
    assert payload["knowledge_atom_refresh_summary"]["current_atom_count"] >= 2
    assert payload["combination_rerank_summary"]["current_latent_candidate_count"] >= 1
    assert any(
        row["pattern_id"] == "reactive_power_exposure"
        for row in manifest["approved_pattern_promotion_register"]
    )
    refreshed_licensed = payload["licensed_research"]
    assert any(
        row["pattern_id"] == "reactive_power_exposure"
        for row in refreshed_licensed["approved_pattern_promotion_register"]
    )
    assert any(
        row["promotion_id"].startswith("pattern_promotion::extract::dashboard_reference::ieee-candidate-01")
        for row in refreshed_licensed["promotion_review_register"]
    )
    assert refreshed_licensed["knowledge_atom_refresh_summary"]["exists"] is True
    assert refreshed_licensed["combination_rerank_summary"]["exists"] is True


def test_article_reference_edit_manual_text_propagates_into_reference_backed_promotions(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}, "licensed_research_activity": {}}
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )
    dashboard_module._persist_licensed_discovery_queue_manifest(run_id, _fake_discovery_queue_manifest())
    dashboard_module._persist_discovery_candidate_decision_record(
        run_id,
        {
            "candidate_id": "ieee-candidate-01",
            "operator_decision": "accepted_for_reference_use",
            "decision_reason": "Accepted candidate in dashboard test.",
            "decision_timestamp": "2026-05-05T00:00:00Z",
            "decision_scope": "run",
        },
    )

    client = dashboard_module.app.test_client()
    edit_response = client.post(
        "/api/article-reference-edit",
        json={
            "run_id": run_id,
            "candidate_id": "ieee-candidate-01",
            "patch": {
                "reference_excerpt": (
                    "Manual excerpt: reactive power exposure and compressed air leakage remain hidden-loss modes, "
                    "and premature sensor deployment can still miss the dominant process variable."
                ),
                "notes": "Manually curated from provider-visible page text.",
            },
        },
    )
    edit_payload = edit_response.get_json()

    assert edit_response.status_code == 200
    assert edit_payload["ok"] is True
    assert edit_payload["updated_row"]["reference_state"] == "manual_text_enriched"
    assert "Manual excerpt" in edit_payload["updated_row"]["reference_excerpt"]
    assert edit_payload["accepted_discovery_candidate_bundle_manifest"]["exists"] is True
    assert edit_payload["reference_backed_promotion_manifest"]["exists"] is True
    manifest = edit_payload["reference_backed_promotion_manifest"]
    assert manifest["summary"]["accepted_reference_count"] == 1
    assert any(
        row["pattern_id"] == "reactive_power_exposure"
        for row in manifest["approved_pattern_promotion_register"]
    )


def test_registry_review_bundle_endpoint_returns_accepted_promotions(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {
                    "pattern_id": "licensed_boundary_candidate",
                    "promotion_state": "ready_for_registry_review",
                    "source_basis_id": "licensed_research_public_technical_priors",
                    "document_ref": "doc::licensed::01",
                    "proposed_spec": {"name": "Licensed Boundary Candidate"},
                }
            ]
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-decision",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "operator_decision": "accepted_for_registry_review",
            "decision_reason": "Accepted for export.",
        },
    )
    assert response.status_code == 200

    bundle_response = client.get(f"/api/registry-review-bundle?run_id={run_id}")
    payload = bundle_response.get_json()

    assert bundle_response.status_code == 200
    assert payload["ok"] is True
    bundle = payload["registry_review_bundle"]
    assert bundle["summary"]["accepted_total"] == 1
    assert bundle["accepted_pattern_promotions"][0]["pattern_id"] == "licensed_boundary_candidate"
    assert bundle["accepted_pattern_promotions"][0]["decision_reason"] == "Accepted for export."


def test_registry_stage_preview_endpoint_returns_candidate_file_plan(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {
                    "pattern_id": "licensed_boundary_candidate",
                    "promotion_state": "ready_for_registry_review",
                    "source_basis_id": "licensed_research_public_technical_priors",
                    "document_ref": "doc::licensed::01",
                    "proposed_spec": {
                        "id": "licensed_boundary_candidate",
                        "version": "1.0.0",
                        "name": "Licensed Boundary Candidate",
                    },
                }
            ]
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-decision",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "operator_decision": "accepted_for_registry_review",
            "decision_reason": "Accepted for staging preview.",
        },
    )
    assert response.status_code == 200

    preview_response = client.get(f"/api/registry-stage-preview?run_id={run_id}")
    payload = preview_response.get_json()

    assert preview_response.status_code == 200
    assert payload["ok"] is True
    preview = payload["registry_stage_preview"]
    assert preview["summary"]["total_rows"] == 1
    assert preview["summary"]["write_candidate_file_count"] == 1
    assert preview["stage_rows"][0]["item_type"] == "pattern"
    assert preview["stage_rows"][0]["item_id"] == "licensed_boundary_candidate"
    assert preview["stage_rows"][0]["stage_action"] == "write_candidate_file"
    assert preview["stage_rows"][0]["target_path"].endswith("patterns/licensed_boundary_candidate.v1.json")


def test_registry_stage_materialize_writes_candidate_files(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {
                    "pattern_id": "licensed_boundary_candidate",
                    "promotion_state": "ready_for_registry_review",
                    "source_basis_id": "licensed_research_public_technical_priors",
                    "document_ref": "doc::licensed::01",
                    "proposed_spec": {
                        "id": "licensed_boundary_candidate",
                        "version": "1.0.0",
                        "name": "Licensed Boundary Candidate",
                        "source_basis": ["licensed_research_public_technical_priors"],
                    },
                }
            ]
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-decision",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "operator_decision": "accepted_for_registry_review",
            "decision_reason": "Accepted for file materialization.",
        },
    )
    assert response.status_code == 200

    materialize_response = client.post(
        "/api/registry-stage-materialize",
        json={"run_id": run_id},
    )
    payload = materialize_response.get_json()

    assert materialize_response.status_code == 200
    assert payload["ok"] is True
    manifest = payload["registry_stage_candidate_manifest"]
    assert manifest["summary"]["materialized_count"] == 1
    candidate_path = manifest["rows"][0]["candidate_path"]
    assert candidate_path.endswith("patterns/licensed_boundary_candidate.v1.json")
    candidate_payload = json.loads(open(candidate_path, "r", encoding="utf-8").read())
    assert candidate_payload["id"] == "licensed_boundary_candidate"
    assert candidate_payload["name"] == "Licensed Boundary Candidate"


def test_registry_stage_materialize_uses_edited_promotion_spec(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {
                    "promotion_id": "pattern::licensed_boundary_candidate",
                    "pattern_id": "licensed_boundary_candidate",
                    "promotion_state": "ready_for_registry_review",
                    "source_basis_id": "licensed_research_public_technical_priors",
                    "document_ref": "doc::licensed::01",
                    "proposed_spec": {
                        "id": "licensed_boundary_candidate",
                        "version": "1.0.0",
                        "name": "Licensed Boundary Candidate",
                        "knowledge_type": ["FINANCIAL_TRANSLATION"],
                        "asset_types": ["warehouse_distribution"],
                        "applicable_industries": ["logistics"],
                        "applicable_contexts": ["licensed_research"],
                        "trigger_conditions": ["Owner/operator boundary remains unresolved."],
                        "anti_triggers": ["Owner/operator boundary fully documented."],
                        "physical_basis": "No direct physical basis; the pattern translates operational control into value capture risk.",
                        "operational_basis": "Owner and operator control can diverge across metering and operating boundaries.",
                        "financial_mechanism": "Savings or value can leak to the actor controlling the variable instead of the actor funding the CAPEX.",
                        "typical_false_assumption": "The CAPEX payer automatically captures the upside.",
                        "hypothesis": "Control-boundary ambiguity can distort who captures value from an intervention.",
                        "rival_hypotheses": ["Control and value capture are already aligned."],
                        "evidence_required": ["Lease matrix", "meter map"],
                        "minimum_evidence_to_activate": ["Owner/operator split plausible"],
                        "minimum_evidence_to_confirm": ["Lease and meter alignment documented"],
                        "falsification_conditions": ["Owner and operator already aligned on the driving variable."],
                        "allowed_claim_language": "Boundary leakage remains a structurally plausible risk until control evidence arrives.",
                        "prohibited_claim_language": "The owner will capture the savings.",
                        "financial_exposure_if_true": ["boundary leakage"],
                        "financial_exposure_if_false": ["extra diligence cost only"],
                        "tad_actions": ["VALIDATE_CONTROL_BOUNDARY"],
                        "stop_conditions": ["Control boundary resolved"],
                        "escalation_conditions": ["Material value capture ambiguity persists"],
                        "source_basis": ["licensed_research_public_technical_priors"],
                        "confidence_ceiling": "L2",
                        "claim_permissions_impact": ["claim_owner_capture_blocked"],
                        "example_outputs": ["If control and value capture are split, the economics can leak before reaching the sponsor."],
                        "tests": ["licensed pattern candidate should remain L2 and bounded"],
                    },
                }
            ]
        },
    }

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-decision",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "operator_decision": "accepted_for_registry_review",
            "decision_reason": "Accepted for file materialization.",
        },
    )
    assert response.status_code == 200

    edit_response = client.post(
        "/api/promotion-edit",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "patch": {
                "name": "Edited Boundary Candidate",
                "minimum_evidence_to_activate": ["meter map", "lease matrix"],
                "allowed_claim_language": "Edited allowed language.",
            },
        },
    )
    assert edit_response.status_code == 200

    materialize_response = client.post(
        "/api/registry-stage-materialize",
        json={"run_id": run_id},
    )
    payload = materialize_response.get_json()

    assert materialize_response.status_code == 200
    assert payload["ok"] is True
    manifest = payload["registry_stage_candidate_manifest"]
    assert manifest["summary"]["materialized_count"] == 1
    candidate_path = manifest["rows"][0]["candidate_path"]
    candidate_payload = json.loads(open(candidate_path, "r", encoding="utf-8").read())
    assert candidate_payload["name"] == "Edited Boundary Candidate"
    assert candidate_payload["minimum_evidence_to_activate"] == ["meter map", "lease matrix"]
    assert candidate_payload["allowed_claim_language"] == "Edited allowed language."


def test_registry_stage_merge_writes_validated_files_into_registry_root(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {
        "run_id": run_id,
        "motor_results": {},
        "licensed_research_activity": {
            "approved_pattern_promotion_register": [
                {
                    "pattern_id": "licensed_boundary_candidate",
                    "promotion_state": "ready_for_registry_review",
                    "source_basis_id": "licensed_research_public_technical_priors",
                    "document_ref": "doc::licensed::01",
                    "proposed_spec": {
                        "id": "licensed_boundary_candidate",
                        "version": "1.0.0",
                        "name": "Licensed Boundary Candidate",
                        "knowledge_type": ["FINANCIAL_TRANSLATION"],
                        "asset_types": ["warehouse_distribution"],
                        "applicable_industries": ["logistics"],
                        "applicable_contexts": ["licensed_research"],
                        "trigger_conditions": ["Owner/operator boundary remains unresolved."],
                        "anti_triggers": ["Owner/operator boundary fully documented."],
                        "physical_basis": "No direct physical basis; the pattern translates operational control into value capture risk.",
                        "operational_basis": "Owner and operator control can diverge across metering and operating boundaries.",
                        "financial_mechanism": "Savings or value can leak to the actor controlling the variable instead of the actor funding the CAPEX.",
                        "typical_false_assumption": "The CAPEX payer automatically captures the upside.",
                        "hypothesis": "Control-boundary ambiguity can distort who captures value from an intervention.",
                        "rival_hypotheses": ["Control and value capture are already aligned."],
                        "evidence_required": ["Lease matrix", "meter map"],
                        "minimum_evidence_to_activate": ["Owner/operator split plausible"],
                        "minimum_evidence_to_confirm": ["Lease and meter alignment documented"],
                        "falsification_conditions": ["Owner and operator already aligned on the driving variable."],
                        "allowed_claim_language": "Boundary leakage remains a structurally plausible risk until control evidence arrives.",
                        "prohibited_claim_language": "The owner will capture the savings.",
                        "financial_exposure_if_true": ["boundary leakage"],
                        "financial_exposure_if_false": ["extra diligence cost only"],
                        "tad_actions": ["VALIDATE_CONTROL_BOUNDARY"],
                        "stop_conditions": ["Control boundary resolved"],
                        "escalation_conditions": ["Material value capture ambiguity persists"],
                        "source_basis": ["licensed_research_public_technical_priors"],
                        "confidence_ceiling": "L2",
                        "claim_permissions_impact": ["claim_owner_capture_blocked"],
                        "example_outputs": ["If control and value capture are split, the economics can leak before reaching the sponsor."],
                        "tests": ["licensed pattern candidate should remain L2 and bounded"],
                    },
                }
            ]
        },
    }

    registry_root = tmp_path / "registry"
    real_bundle = dashboard_module.load_registry_bundle()
    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )
    monkeypatch.setattr(
        dashboard_module,
        "load_registry_bundle",
        lambda: {**real_bundle, "root": str(registry_root)},
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/promotion-decision",
        json={
            "run_id": run_id,
            "promotion_id": "pattern::licensed_boundary_candidate",
            "promotion_type": "pattern",
            "operator_decision": "accepted_for_registry_review",
            "decision_reason": "Accepted for merge test.",
        },
    )
    assert response.status_code == 200

    materialize_response = client.post(
        "/api/registry-stage-materialize",
        json={"run_id": run_id},
    )
    assert materialize_response.status_code == 200

    merge_response = client.post(
        "/api/registry-stage-merge",
        json={"run_id": run_id},
    )
    payload = merge_response.get_json()

    assert merge_response.status_code == 200
    assert payload["ok"] is True
    manifest = payload["registry_stage_merge_manifest"]
    assert manifest["summary"]["merged_count"] == 1
    target_path = manifest["rows"][0]["target_path"]
    assert target_path.endswith("patterns/licensed_boundary_candidate.v1.json")
    merged_payload = json.loads(open(target_path, "r", encoding="utf-8").read())
    assert merged_payload["id"] == "licensed_boundary_candidate"
    assert merged_payload["confidence_ceiling"] == "L2"


def test_provider_session_handoff_materialize_writes_manifest(monkeypatch, tmp_path) -> None:
    run_id = "run:oisk-dashboard"
    fake_run = {"run_id": run_id, "motor_results": {}}

    _isolate_dashboard_runtime_dirs(monkeypatch, tmp_path)
    monkeypatch.setattr(dashboard_module, "_load_run", lambda requested_run_id: fake_run if requested_run_id == run_id else {})
    monkeypatch.setattr(
        dashboard_module,
        "_load_motor_output",
        lambda run_d, motor_id: _fake_motor_output(motor_id),
    )

    client = dashboard_module.app.test_client()
    response = client.post(
        "/api/provider-session-handoff-materialize",
        json={"run_id": run_id},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is True
    manifest = payload["provider_session_handoff_manifest"]
    assert manifest["summary"]["provider_count"] >= 4
    assert manifest["provider_rows"][0]["sample_entry_url"]
    assert manifest["provider_rows"][0]["recommended_action"]
    assert "bootstrap_licensed_provider_session.py" in manifest["provider_rows"][0]["display_command"]
    stored = json.loads(open(manifest["path"], "r", encoding="utf-8").read())
    assert stored["run_id"] == run_id
    assert stored["summary"]["provider_count"] >= 4


def test_provider_session_handoff_uses_institutional_gateway_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("ZLAB_LICENSED_INSTITUTION_ENTRY_URL", "https://library.example.edu/login")
    monkeypatch.setenv("ZLAB_LICENSED_INSTITUTION_NAME", "Example University")

    result = dashboard_module._licensed_research_activity({"run_id": "run:oisk-dashboard"})

    provider_rows = list((result.get("provider_handoff_bundle", {}) or {}).get("provider_rows", []) or [])
    assert provider_rows
    licensed_rows = [row for row in provider_rows if row.get("session_required")]
    assert licensed_rows
    first = licensed_rows[0]
    assert first["access_route"] == "institutional_gateway"
    assert first["institution_name"] == "Example University"
    assert first["sample_entry_url"] == "https://library.example.edu/login"
    assert "https://library.example.edu/login" in first["display_command"]
    assert "--validate-url" in first["validate_command_argv"]
