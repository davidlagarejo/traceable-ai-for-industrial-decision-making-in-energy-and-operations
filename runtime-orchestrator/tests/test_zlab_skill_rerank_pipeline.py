from __future__ import annotations

from runtime_orchestrator.zlab_skill import (
    build_combination_rerank_summary,
    build_knowledge_atom_refresh_summary,
)


def test_build_knowledge_atom_refresh_summary_detects_meaningful_delta() -> None:
    summary = build_knowledge_atom_refresh_summary(
        run_id="run:rerank",
        candidate_id="queryseed-01",
        previous_knowledge_atom_register=[],
        current_knowledge_atom_register=[
            {"atom_id": "atom::reactive_power", "document_ref": "doc::1"},
            {"atom_id": "atom::compressed_air", "document_ref": "doc::1"},
        ],
        previous_source_coverage_summary={"coverage_strength": "empty", "document_count": 0, "visible_reference_count": 0},
        current_source_coverage_summary={"coverage_strength": "moderate", "document_count": 1, "visible_reference_count": 1},
        previous_reference_backed_promotion_manifest={"summary": {"pattern_promotion_count": 0, "combination_promotion_count": 0, "extraction_count": 0}},
        current_reference_backed_promotion_manifest={"summary": {"pattern_promotion_count": 2, "combination_promotion_count": 1, "extraction_count": 1}},
    )

    assert summary["meaningful_delta"] is True
    assert summary["delta_atom_count"] == 2
    assert summary["current_coverage_strength"] == "moderate"
    assert summary["current_pattern_promotion_count"] == 2


def test_build_combination_rerank_summary_detects_top_change() -> None:
    summary = build_combination_rerank_summary(
        run_id="run:rerank",
        previous_latent_combination_candidate_register=[
            {"combination_id": "latent::a", "score": 5},
            {"combination_id": "latent::b", "score": 4},
        ],
        current_latent_combination_candidate_register=[
            {"combination_id": "latent::a", "score": 4},
            {"combination_id": "latent::b", "score": 7},
            {"combination_id": "latent::c", "score": 6},
        ],
        previous_admissible_combination_review_register=[
            {"combination_id": "latent::a"},
        ],
        current_admissible_combination_review_register=[
            {"combination_id": "latent::b"},
            {"combination_id": "latent::c"},
        ],
        previous_current_combination_review_row={"combination_id": "latent::a"},
        current_current_combination_review_row={"combination_id": "latent::b"},
        previous_combination_review_sequence_register=[
            {"combination_id": "latent::a"},
            {"combination_id": "latent::b"},
        ],
        current_combination_review_sequence_register=[
            {"combination_id": "latent::b"},
            {"combination_id": "latent::c"},
            {"combination_id": "latent::a"},
        ],
    )

    assert summary["rerank_changed"] is True
    assert summary["next_combination_changed"] is True
    assert summary["top_sequence_changed"] is True
    assert summary["added_combination_ids"] == ["latent::c"]
    assert "latent::a" in summary["score_changed_ids"]
    assert "latent::b" in summary["score_changed_ids"]
