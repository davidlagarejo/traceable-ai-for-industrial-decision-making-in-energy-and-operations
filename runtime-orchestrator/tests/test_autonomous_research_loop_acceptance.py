from __future__ import annotations

import dashboard as dashboard_module

from runtime_orchestrator.zlab_skill import (
    build_combination_search_gap_record,
    build_research_loop_snapshot,
)


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
        }
    if motor_id == "motor_052":
        return {
            "activated_pattern_register": [
                {
                    "pattern_name": "forklift_charging_and_demand_spike_plausible",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                }
            ],
            "pattern_authority_state": "skill_primary",
            "pattern_authority_summary": {"pattern_authority_state": "skill_primary"},
            "authoritative_pattern_activation_register": [
                {
                    "pattern_id": "warehouse_mhe_charging_demand_peak",
                    "activation_state": "structurally_plausible",
                },
                {
                    "pattern_id": "value_boundary_leakage_owner_operator",
                    "activation_state": "structurally_plausible",
                },
                {
                    "pattern_id": "fair_comparison_invalid_area_metric",
                    "activation_state": "candidate",
                },
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
    monkeypatch.setattr(dashboard_module, "_RESEARCH_CAMPAIGN_TRIGGER_DIR", tmp_path / "research-campaign-triggers")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_STATE_DIR", tmp_path / "research-loop-state")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_EVENT_DIR", tmp_path / "research-loop-events")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_JOB_DIR", tmp_path / "research-loop-jobs")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_METRIC_DIR", tmp_path / "research-loop-metrics")
    monkeypatch.setattr(dashboard_module, "_RESEARCH_LOOP_CONTROL_DIR", tmp_path / "research-loop-controls")
    monkeypatch.setattr(dashboard_module, "_REGISTRY_STAGE_CANDIDATE_DIR", tmp_path / "registry-stage-candidates")
    monkeypatch.setattr(dashboard_module, "_PROVIDER_SESSION_HANDOFF_DIR", tmp_path / "provider-session-handoffs")


def _latent_rows(prefix: str, unique_count: int, duplicate_count: int = 1) -> list[dict]:
    rows: list[dict] = []
    for idx in range(unique_count):
        for copy_idx in range(duplicate_count):
            rows.append(
                {
                    "combination_id": f"{prefix}::{idx:03d}",
                    "combination_name": f"{prefix} combination {idx}",
                    "copy_marker": copy_idx,
                }
            )
    return rows


def _strong_source_family_rows() -> list[dict]:
    return [
        {
            "source_family": "licensed_research_discovery",
            "display_name": "Licensed discovery",
            "coverage_state": "strong",
            "importance": "high",
        },
        {
            "source_family": "licensed_research_fulltext",
            "display_name": "Licensed full text",
            "coverage_state": "strong",
            "importance": "high",
        },
        {
            "source_family": "public_technical_guidance",
            "display_name": "Public technical guidance",
            "coverage_state": "strong",
            "importance": "medium",
        },
    ]


def _thin_source_family_rows() -> list[dict]:
    return [
        {
            "source_family": "licensed_research_discovery",
            "display_name": "Licensed discovery",
            "coverage_state": "thin",
            "importance": "high",
        },
        {
            "source_family": "licensed_research_fulltext",
            "display_name": "Licensed full text",
            "coverage_state": "untouched",
            "importance": "high",
        },
    ]


def _follow_on_manifest(combination_id: str) -> list[dict]:
    return [
        {
            "combination_id": combination_id,
            "combination_name": "Current latent combination",
            "reasoning_flags": ["tariff_gap", "boundary_gap"],
            "execution_rows": [
                {
                    "source_family": "licensed_research_discovery",
                    "provider_targets": ["scopus"],
                    "query_families": ["tariff_boundary"],
                }
            ],
            "provider_query_template_count": 1,
        }
    ]


def test_warehouse_acceptance_keeps_query_seed_out_of_evidence_until_resolved(monkeypatch, tmp_path) -> None:
    run_id = "run:arl-08-warehouse"
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
    monkeypatch.setattr(dashboard_module, "_load_motor_output", lambda run_d, motor_id: _fake_motor_output(motor_id))

    preview = dashboard_module._congruence_brain_activity(fake_run)
    current_id = preview["current_combination_review_row"]["combination_id"]

    client = dashboard_module.app.test_client()
    seed_payload = client.post(
        "/api/combination-follow-on-seed-candidates",
        json={"run_id": run_id, "combination_id": current_id},
    ).get_json()
    seed_id = seed_payload["seeded_candidate_ids"][0]

    reference_payload = client.post(
        "/api/article-reference-read",
        json={"run_id": run_id, "candidate_id": seed_id},
    ).get_json()
    refreshed = dashboard_module._congruence_brain_activity(fake_run)

    assert reference_payload["updated_row"]["reference_state"] == "query_seed_draft"
    assert reference_payload["updated_row"]["reference_state"] != "visible_text_enriched"
    assert refreshed["research_loop_state"]["loop_status"] in {
        "awaiting_search_result_capture",
        "awaiting_reference_resolution",
    }
    assert refreshed["current_research_job"]["job_type"] in {
        "draft_reference",
        "capture_search_result",
        "resolve_reference_excerpt",
    }
    assert any(
        row.get("job_type") == "capture_search_result"
        for row in refreshed["research_loop_job_register"]
    )
    assert refreshed["research_loop_metrics"]["query_seed_draft_count"] == 1
    assert refreshed["research_loop_metrics"]["captured_result_count"] == 0
    assert refreshed["research_loop_metrics"]["visible_text_enriched_count"] == 0
    assert refreshed["research_loop_metrics"]["resolved_reference_count"] == 0
    assert refreshed["research_stop_condition_record"]["stop_state"] == "continue_research"


def test_manufacturing_acceptance_allows_stop_only_with_strong_depth_and_unique_floor() -> None:
    latent_rows = _latent_rows("latent::manufacturing", unique_count=55, duplicate_count=2)
    admissible_rows = _latent_rows("admissible::manufacturing", unique_count=14, duplicate_count=2)
    source_coverage_summary = {
        "coverage_strength": "strong",
        "provider_count": 3,
        "document_count": 6,
        "knowledge_atom_count": 14,
        "visible_reference_count": 3,
        "supported_pattern_count": 5,
    }
    gap = build_combination_search_gap_record(
        latent_combination_candidate_register=latent_rows,
        admissible_combination_review_register=admissible_rows,
        source_coverage_summary=source_coverage_summary,
        source_family_coverage_register=_strong_source_family_rows(),
        asset_context_vector={"asset_family": "manufacturing_facility"},
        active_pattern_ids=[
            "compressed_air_leak_plausibility",
            "process_load_vs_waste",
            "maintenance_hidden_value_driver",
            "reactive_power_exposure",
        ],
    )

    snapshot = build_research_loop_snapshot(
        run_id="run:arl-08-manufacturing",
        current_combination_review_row={},
        combination_follow_on_execution_manifest_register=[],
        discovery_candidate_review_register=[],
        article_reference_register=[],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[{"atom_id": f"atom::{idx}"} for idx in range(14)],
        latent_combination_candidate_register=latent_rows,
        admissible_combination_review_register=admissible_rows,
        combination_review_queue_summary={"pending": 0, "deferred": 0},
        source_coverage_summary=source_coverage_summary,
        source_family_coverage_register=_strong_source_family_rows(),
        combination_search_gap_record=gap,
        research_campaign_record={"campaign_status": "reviewable_but_expand_sources"},
        asset_context_vector={"asset_family": "manufacturing_facility"},
    )

    assert gap["search_status"] == "complete_enough_for_review"
    assert gap["latent_candidate_count"] == 55
    assert gap["latent_candidate_row_count"] == 110
    assert snapshot["metrics"]["latent_candidate_count"] == 55
    assert snapshot["metrics"]["latent_candidate_row_count"] == 110
    assert snapshot["depth_enforcement"]["must_continue_research"] is False
    assert snapshot["stop_condition"]["stop_state"] == "stopped_by_saturation"
    assert snapshot["state"]["loop_status"] == "stopped_by_saturation"


def test_building_acceptance_rejects_duplicate_inflation_and_keeps_research_open() -> None:
    current_combination_id = "latent::building::001"
    latent_rows = _latent_rows("latent::building", unique_count=3, duplicate_count=20)
    admissible_rows = _latent_rows("admissible::building", unique_count=1, duplicate_count=10)
    source_coverage_summary = {
        "coverage_strength": "weak",
        "provider_count": 1,
        "document_count": 1,
        "knowledge_atom_count": 2,
        "visible_reference_count": 0,
        "supported_pattern_count": 2,
    }
    gap = build_combination_search_gap_record(
        latent_combination_candidate_register=latent_rows,
        admissible_combination_review_register=admissible_rows,
        source_coverage_summary=source_coverage_summary,
        source_family_coverage_register=_thin_source_family_rows(),
        asset_context_vector={
            "asset_family": "commercial_building",
            "solar_profile": "afternoon_solar_peak",
        },
        active_pattern_ids=["hvac_schedule_drift", "benchmark_denominator_error"],
    )

    snapshot = build_research_loop_snapshot(
        run_id="run:arl-08-building",
        current_combination_review_row={
            "combination_id": current_combination_id,
            "combination_name": "Building solar + schedule latent combination",
        },
        combination_follow_on_execution_manifest_register=_follow_on_manifest(current_combination_id),
        discovery_candidate_review_register=[],
        article_reference_register=[],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[{"atom_id": "atom::building::01"}, {"atom_id": "atom::building::02"}],
        latent_combination_candidate_register=latent_rows,
        admissible_combination_review_register=admissible_rows,
        combination_review_queue_summary={"pending": 1, "deferred": 0},
        source_coverage_summary=source_coverage_summary,
        source_family_coverage_register=_thin_source_family_rows(),
        combination_search_gap_record=gap,
        research_campaign_record={"campaign_status": "coverage_building"},
        asset_context_vector={
            "asset_family": "commercial_building",
            "solar_profile": "afternoon_solar_peak",
        },
    )

    assert gap["latent_candidate_count"] == 3
    assert gap["latent_candidate_row_count"] == 60
    assert gap["search_status"] == "incomplete_under_investigated"
    assert snapshot["metrics"]["latent_candidate_count"] == 3
    assert snapshot["metrics"]["latent_candidate_row_count"] == 60
    assert snapshot["depth_enforcement"]["must_continue_research"] is True
    assert snapshot["stop_condition"]["stop_state"] == "continue_research"
    assert snapshot["state"]["loop_status"] == "seeding_queries"
    assert snapshot["state"]["next_action"] == "SEED_QUERY_CANDIDATES"
