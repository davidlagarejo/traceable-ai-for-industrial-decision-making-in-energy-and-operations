from __future__ import annotations

from typing import Any


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _score_map(rows: list[dict[str, Any]] | None) -> dict[str, float]:
    return {
        _text(row.get("combination_id")): float(row.get("score", 0) or 0)
        for row in list(rows or [])
        if _text(row.get("combination_id"))
    }


def build_combination_rerank_summary(
    *,
    run_id: str,
    previous_latent_combination_candidate_register: list[dict[str, Any]] | None,
    current_latent_combination_candidate_register: list[dict[str, Any]] | None,
    previous_admissible_combination_review_register: list[dict[str, Any]] | None,
    current_admissible_combination_review_register: list[dict[str, Any]] | None,
    previous_current_combination_review_row: dict[str, Any] | None,
    current_current_combination_review_row: dict[str, Any] | None,
    previous_combination_review_sequence_register: list[dict[str, Any]] | None,
    current_combination_review_sequence_register: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    previous_latent = list(previous_latent_combination_candidate_register or [])
    current_latent = list(current_latent_combination_candidate_register or [])
    previous_admissible = list(previous_admissible_combination_review_register or [])
    current_admissible = list(current_admissible_combination_review_register or [])
    previous_current = dict(previous_current_combination_review_row or {})
    current_current = dict(current_current_combination_review_row or {})
    previous_latent_ids = {_text(row.get("combination_id")) for row in previous_latent if _text(row.get("combination_id"))}
    current_latent_ids = {_text(row.get("combination_id")) for row in current_latent if _text(row.get("combination_id"))}
    previous_admissible_ids = {_text(row.get("combination_id")) for row in previous_admissible if _text(row.get("combination_id"))}
    current_admissible_ids = {_text(row.get("combination_id")) for row in current_admissible if _text(row.get("combination_id"))}
    previous_scores = _score_map(previous_latent)
    current_scores = _score_map(current_latent)
    common_ids = previous_latent_ids & current_latent_ids
    score_changed_ids = sorted(
        combination_id
        for combination_id in common_ids
        if float(previous_scores.get(combination_id, 0.0)) != float(current_scores.get(combination_id, 0.0))
    )
    previous_current_id = _text(previous_current.get("combination_id"))
    current_current_id = _text(current_current.get("combination_id"))
    previous_sequence = [_text(row.get("combination_id")) for row in list(previous_combination_review_sequence_register or []) if _text(row.get("combination_id"))]
    current_sequence = [_text(row.get("combination_id")) for row in list(current_combination_review_sequence_register or []) if _text(row.get("combination_id"))]
    next_combination_changed = previous_current_id != current_current_id and bool(previous_current_id or current_current_id)
    top_sequence_changed = previous_sequence[:3] != current_sequence[:3]
    rerank_changed = any(
        [
            bool(current_latent_ids - previous_latent_ids),
            bool(previous_latent_ids - current_latent_ids),
            bool(current_admissible_ids - previous_admissible_ids),
            bool(previous_admissible_ids - current_admissible_ids),
            bool(score_changed_ids),
            next_combination_changed,
            top_sequence_changed,
        ]
    )
    summary = (
        f"Latent pool {len(previous_latent_ids)}->{len(current_latent_ids)}; "
        f"admissible {len(previous_admissible_ids)}->{len(current_admissible_ids)}; "
        f"current review {previous_current_id or 'none'}->{current_current_id or 'none'}."
    )
    return {
        "run_id": _text(run_id),
        "rerank_changed": rerank_changed,
        "previous_latent_candidate_count": len(previous_latent_ids),
        "current_latent_candidate_count": len(current_latent_ids),
        "previous_admissible_candidate_count": len(previous_admissible_ids),
        "current_admissible_candidate_count": len(current_admissible_ids),
        "added_combination_ids": sorted(current_latent_ids - previous_latent_ids),
        "removed_combination_ids": sorted(previous_latent_ids - current_latent_ids),
        "newly_admissible_combination_ids": sorted(current_admissible_ids - previous_admissible_ids),
        "no_longer_admissible_combination_ids": sorted(previous_admissible_ids - current_admissible_ids),
        "score_changed_ids": score_changed_ids,
        "previous_current_combination_id": previous_current_id,
        "current_current_combination_id": current_current_id,
        "next_combination_changed": next_combination_changed,
        "top_sequence_changed": top_sequence_changed,
        "previous_top_sequence": previous_sequence[:5],
        "current_top_sequence": current_sequence[:5],
        "summary": summary,
    }
