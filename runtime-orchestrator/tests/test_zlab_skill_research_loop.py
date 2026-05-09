from __future__ import annotations

from runtime_orchestrator.zlab_skill import (
    build_research_loop_event_records,
    build_research_loop_snapshot,
)


def _base_follow_on_manifest() -> list[dict]:
    return [
        {
            "combination_id": "latent::combo::warehouse::01",
            "combination_name": "Warehouse latent combo",
            "reasoning_flags": ["tariff_gap", "boundary_gap"],
            "execution_rows": [
                {
                    "source_family": "licensed_research_discovery",
                    "provider_targets": ["scopus"],
                    "query_families": ["tariff_boundary"],
                }
            ],
        }
    ]


def _base_current_combination() -> dict:
    return {
        "combination_id": "latent::combo::warehouse::01",
        "combination_name": "Warehouse latent combo",
    }


def test_research_loop_snapshot_seeds_queries_when_none_exist() -> None:
    snapshot = build_research_loop_snapshot(
        run_id="run:research-loop",
        current_combination_review_row=_base_current_combination(),
        combination_follow_on_execution_manifest_register=_base_follow_on_manifest(),
        discovery_candidate_review_register=[],
        article_reference_register=[],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[],
        latent_combination_candidate_register=[{"combination_id": "latent::combo::warehouse::01"}],
        admissible_combination_review_register=[{"combination_id": "latent::combo::warehouse::01"}],
        combination_review_queue_summary={"pending": 1, "deferred": 0},
        source_coverage_summary={"coverage_strength": "weak", "provider_count": 1, "document_count": 1, "knowledge_atom_count": 0},
        source_family_coverage_register=[
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
        ],
        combination_search_gap_record={"search_status": "incomplete_under_investigated"},
        research_campaign_record={"campaign_status": "coverage_building"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
    )

    assert snapshot["state"]["loop_status"] == "seeding_queries"
    assert snapshot["state"]["next_action"] == "SEED_QUERY_CANDIDATES"
    assert snapshot["current_job"]["job_type"] == "seed_query_candidates"
    assert snapshot["metrics"]["latent_candidate_count"] == 1
    assert snapshot["depth_enforcement"]["must_continue_research"] is True
    assert snapshot["stop_condition"]["stop_state"] == "continue_research"


def test_research_loop_snapshot_waits_for_reference_resolution() -> None:
    snapshot = build_research_loop_snapshot(
        run_id="run:research-loop",
        current_combination_review_row=_base_current_combination(),
        combination_follow_on_execution_manifest_register=_base_follow_on_manifest(),
        discovery_candidate_review_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "provider_key": "scopus",
                "metadata_payload": {
                    "notes": "Combination: latent::combo::warehouse::01. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
                },
            }
        ],
        article_reference_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "reference_state": "query_seed_draft",
            }
        ],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[],
        latent_combination_candidate_register=[{"combination_id": "latent::combo::warehouse::01"}],
        admissible_combination_review_register=[{"combination_id": "latent::combo::warehouse::01"}],
        combination_review_queue_summary={"pending": 1, "deferred": 0},
        source_coverage_summary={"coverage_strength": "weak", "provider_count": 1, "document_count": 1, "knowledge_atom_count": 0},
        source_family_coverage_register=[
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
        ],
        combination_search_gap_record={"search_status": "incomplete_under_investigated"},
        research_campaign_record={"campaign_status": "coverage_building"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
    )

    assert snapshot["state"]["loop_status"] == "awaiting_search_result_capture"
    assert snapshot["state"]["next_action"] == "CAPTURE_SEARCH_RESULT"
    assert snapshot["current_job"]["job_type"] == "capture_search_result"
    assert snapshot["current_job"]["candidate_id"] == "queryseed-scopus-01"
    assert snapshot["metrics"]["query_seed_draft_count"] == 1
    assert snapshot["metrics"]["captured_result_count"] == 0
    assert snapshot["depth_enforcement"]["required_next_source_families"]


def test_research_loop_snapshot_waits_for_imported_result_promotion_when_options_exist() -> None:
    snapshot = build_research_loop_snapshot(
        run_id="run:research-loop",
        current_combination_review_row=_base_current_combination(),
        combination_follow_on_execution_manifest_register=_base_follow_on_manifest(),
        discovery_candidate_review_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "provider_key": "scopus",
                "metadata_payload": {
                    "notes": "Combination: latent::combo::warehouse::01. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
                },
            }
        ],
        article_reference_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "reference_state": "query_seed_draft",
            }
        ],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[],
        latent_combination_candidate_register=[{"combination_id": "latent::combo::warehouse::01"}],
        admissible_combination_review_register=[{"combination_id": "latent::combo::warehouse::01"}],
        combination_review_queue_summary={"pending": 1, "deferred": 0},
        source_coverage_summary={"coverage_strength": "weak", "provider_count": 1, "document_count": 1, "knowledge_atom_count": 0},
        source_family_coverage_register=[
            {
                "source_family": "licensed_research_discovery",
                "display_name": "Licensed discovery",
                "coverage_state": "thin",
                "importance": "high",
            },
        ],
        combination_search_gap_record={"search_status": "incomplete_under_investigated"},
        research_campaign_record={"campaign_status": "coverage_building"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
        search_query_execution_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "provider_key": "scopus",
                "source_family": "licensed_research_discovery",
                "queue_status": "pending",
                "execution_status": "search_ready_capture_pending",
                "next_capture_action": "CAPTURE_SEARCH_RESULT",
                "query_family": "tariff_boundary",
                "imported_result_option_count": 2,
                "top_imported_result": {"search_result_title": "Imported result 1"},
            }
        ],
    )

    assert snapshot["state"]["loop_status"] == "awaiting_imported_result_promotion"
    assert snapshot["state"]["next_action"] == "PROMOTE_IMPORTED_RESULT"
    assert snapshot["current_job"]["job_type"] == "promote_imported_result"
    assert snapshot["metrics"]["imported_result_candidate_count"] == 1
    assert snapshot["metrics"]["imported_result_option_count"] == 2


def test_research_loop_snapshot_waits_for_excerpt_resolution_after_result_capture() -> None:
    snapshot = build_research_loop_snapshot(
        run_id="run:research-loop",
        current_combination_review_row=_base_current_combination(),
        combination_follow_on_execution_manifest_register=_base_follow_on_manifest(),
        discovery_candidate_review_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "provider_key": "scopus",
                "metadata_payload": {
                    "notes": "Combination: latent::combo::warehouse::01. Query family: tariff_boundary. Primary query: warehouse tariff boundary.",
                },
            }
        ],
        article_reference_register=[
            {
                "candidate_id": "queryseed-scopus-01",
                "reference_state": "query_seed_draft",
                "acquisition_result": {
                    "status": "query_seed_result_captured",
                    "search_result_title": "Scopus result title",
                    "search_result_snippet": "A visible result snippet.",
                },
            }
        ],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[],
        latent_combination_candidate_register=[{"combination_id": "latent::combo::warehouse::01"}],
        admissible_combination_review_register=[{"combination_id": "latent::combo::warehouse::01"}],
        combination_review_queue_summary={"pending": 1, "deferred": 0},
        source_coverage_summary={"coverage_strength": "weak", "provider_count": 1, "document_count": 1, "knowledge_atom_count": 0},
        source_family_coverage_register=[
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
        ],
        combination_search_gap_record={"search_status": "incomplete_under_investigated"},
        research_campaign_record={"campaign_status": "coverage_building"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
    )

    assert snapshot["state"]["loop_status"] == "awaiting_reference_resolution"
    assert snapshot["state"]["next_action"] == "RESOLVE_REFERENCE_EXCERPT"
    assert snapshot["current_job"]["job_type"] == "resolve_reference_excerpt"
    assert snapshot["metrics"]["query_seed_draft_count"] == 1
    assert snapshot["metrics"]["captured_result_count"] == 1


def test_research_loop_event_records_capture_state_and_job_change() -> None:
    snapshot = {
        "state": {
            "run_id": "run:research-loop",
            "loop_status": "awaiting_reference_resolution",
            "current_combination_id": "latent::combo::warehouse::01",
            "stop_condition_state": "continue_research",
            "operator_control_state": "paused_by_operator",
        },
        "current_job": {
            "job_id": "job::queryseed-scopus-01::resolve_reference_draft",
            "combination_id": "latent::combo::warehouse::01",
            "summary": "Resolve query seed draft.",
        },
    }
    events = build_research_loop_event_records(
        previous_state={
            "run_id": "run:research-loop",
            "loop_status": "seeding_queries",
            "stop_condition_state": "paused_by_operator",
            "operator_control_state": "active",
        },
        previous_current_job={"job_id": "job::latent::seed_query_candidates"},
        snapshot=snapshot,
        event_timestamp="2026-05-06T12:00:00Z",
    )

    assert len(events) == 4
    assert {row["event_type"] for row in events} == {
        "loop_state_transition",
        "current_job_changed",
        "stop_condition_changed",
        "operator_control_changed",
    }


def test_research_loop_snapshot_can_stop_when_saturation_proof_is_strong() -> None:
    snapshot = build_research_loop_snapshot(
        run_id="run:research-loop",
        current_combination_review_row={},
        combination_follow_on_execution_manifest_register=[],
        discovery_candidate_review_register=[],
        article_reference_register=[],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[{"atom_id": f"atom::{idx}"} for idx in range(12)],
        latent_combination_candidate_register=[{"combination_id": f"latent::{idx}"} for idx in range(35)],
        admissible_combination_review_register=[{"combination_id": f"latent::{idx}"} for idx in range(10)],
        combination_review_queue_summary={"pending": 0, "deferred": 0},
        source_coverage_summary={
            "coverage_strength": "strong",
            "provider_count": 3,
            "document_count": 6,
            "knowledge_atom_count": 12,
        },
        source_family_coverage_register=[
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
        ],
        combination_search_gap_record={"search_status": "thin_but_reviewable"},
        research_campaign_record={"campaign_status": "reviewable_but_expand_sources"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
    )

    assert snapshot["depth_enforcement"]["saturation_proof_strong"] is True
    assert snapshot["depth_enforcement"]["must_continue_research"] is False
    assert snapshot["stop_condition"]["stop_state"] == "stopped_by_saturation"
    assert snapshot["state"]["loop_status"] == "stopped_by_saturation"


def test_research_loop_snapshot_respects_operator_pause() -> None:
    snapshot = build_research_loop_snapshot(
        run_id="run:research-loop",
        current_combination_review_row=_base_current_combination(),
        combination_follow_on_execution_manifest_register=_base_follow_on_manifest(),
        discovery_candidate_review_register=[],
        article_reference_register=[],
        research_campaign_trigger_register=[],
        knowledge_atom_register=[],
        latent_combination_candidate_register=[{"combination_id": "latent::combo::warehouse::01"}],
        admissible_combination_review_register=[{"combination_id": "latent::combo::warehouse::01"}],
        combination_review_queue_summary={"pending": 1, "deferred": 0},
        source_coverage_summary={"coverage_strength": "weak", "provider_count": 1, "document_count": 1, "knowledge_atom_count": 0},
        source_family_coverage_register=[
            {
                "source_family": "licensed_research_discovery",
                "display_name": "Licensed discovery",
                "coverage_state": "thin",
                "importance": "high",
            },
        ],
        combination_search_gap_record={"search_status": "incomplete_under_investigated"},
        research_campaign_record={"campaign_status": "coverage_building"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
        research_loop_control_record={
            "control_state": "paused_by_operator",
            "control_reason": "waiting for manual adjudication",
        },
    )

    assert snapshot["stop_condition"]["stop_state"] == "paused_by_operator"
    assert snapshot["state"]["loop_status"] == "paused_by_operator"
    assert snapshot["state"]["next_action"] == "PAUSED_BY_OPERATOR"
