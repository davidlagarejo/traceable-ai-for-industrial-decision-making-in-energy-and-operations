from __future__ import annotations

from runtime_orchestrator.zlab_skill import (
    build_research_depth_enforcement_record,
    build_target_combination_floor_record,
)


def test_research_depth_enforcement_blocks_shallow_campaigns() -> None:
    record = build_research_depth_enforcement_record(
        research_loop_metrics={"latent_candidate_count": 8},
        source_coverage_summary={
            "coverage_strength": "thin",
            "provider_count": 1,
            "document_count": 1,
            "knowledge_atom_count": 2,
        },
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
            {
                "source_family": "public_technical_guidance",
                "display_name": "Public technical guidance",
                "coverage_state": "untouched",
                "importance": "medium",
            },
        ],
        combination_search_gap_record={"search_status": "incomplete_under_investigated"},
        asset_context_vector={"asset_family": "warehouse_distribution"},
    )

    assert record["depth_state"] == "under_floor"
    assert record["target_combination_floor"] == 50
    assert record["bootstrap_floor_exception"] is False
    assert record["must_continue_research"] is True
    assert record["saturation_proof_strong"] is False
    assert "Licensed full text" in record["required_next_source_families"]


def test_research_depth_enforcement_allows_review_when_saturation_proof_is_strong() -> None:
    record = build_research_depth_enforcement_record(
        research_loop_metrics={"latent_candidate_count": 35},
        source_coverage_summary={
            "coverage_strength": "strong",
            "provider_count": 3,
            "document_count": 6,
            "knowledge_atom_count": 14,
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
        asset_context_vector={"asset_family": "warehouse_distribution"},
    )

    assert record["target_combination_floor"] == 50
    assert record["depth_state"] == "thin_but_reviewable"
    assert record["saturation_proof_strong"] is True
    assert record["must_continue_research"] is False


def test_target_combination_floor_record_marks_zero_coverage_as_bootstrap_exception() -> None:
    record = build_target_combination_floor_record(
        asset_context_vector={"asset_family": "warehouse_distribution"},
        source_coverage_summary={
            "provider_count": 0,
            "document_count": 0,
            "knowledge_atom_count": 0,
            "visible_reference_count": 0,
        },
    )

    assert record["target_combination_floor"] == 20
    assert record["policy_state"] == "bootstrap_floor_exception"
    assert record["bootstrap_floor_exception"] is True
