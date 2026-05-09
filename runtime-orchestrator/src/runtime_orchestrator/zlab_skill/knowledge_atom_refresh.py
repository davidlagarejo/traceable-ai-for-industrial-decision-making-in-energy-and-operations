from __future__ import annotations

from typing import Any


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def build_knowledge_atom_refresh_summary(
    *,
    run_id: str,
    candidate_id: str = "",
    previous_knowledge_atom_register: list[dict[str, Any]] | None,
    current_knowledge_atom_register: list[dict[str, Any]] | None,
    previous_source_coverage_summary: dict[str, Any] | None,
    current_source_coverage_summary: dict[str, Any] | None,
    previous_reference_backed_promotion_manifest: dict[str, Any] | None,
    current_reference_backed_promotion_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    previous_atoms = list(previous_knowledge_atom_register or [])
    current_atoms = list(current_knowledge_atom_register or [])
    previous_ids = {_text(row.get("atom_id")) for row in previous_atoms if _text(row.get("atom_id"))}
    current_ids = {_text(row.get("atom_id")) for row in current_atoms if _text(row.get("atom_id"))}
    previous_coverage = dict(previous_source_coverage_summary or {})
    current_coverage = dict(current_source_coverage_summary or {})
    previous_manifest = dict(previous_reference_backed_promotion_manifest or {})
    current_manifest = dict(current_reference_backed_promotion_manifest or {})
    previous_manifest_summary = dict(previous_manifest.get("summary", {}) or {})
    current_manifest_summary = dict(current_manifest.get("summary", {}) or {})

    added_atom_ids = sorted(current_ids - previous_ids)
    removed_atom_ids = sorted(previous_ids - current_ids)
    previous_atom_count = len(previous_ids)
    current_atom_count = len(current_ids)
    delta_atom_count = current_atom_count - previous_atom_count
    previous_document_count = int(previous_coverage.get("document_count", 0) or 0)
    current_document_count = int(current_coverage.get("document_count", 0) or 0)
    previous_visible_reference_count = int(previous_coverage.get("visible_reference_count", 0) or 0)
    current_visible_reference_count = int(current_coverage.get("visible_reference_count", 0) or 0)
    previous_pattern_promotion_count = int(previous_manifest_summary.get("pattern_promotion_count", 0) or 0)
    current_pattern_promotion_count = int(current_manifest_summary.get("pattern_promotion_count", 0) or 0)
    previous_combination_promotion_count = int(previous_manifest_summary.get("combination_promotion_count", 0) or 0)
    current_combination_promotion_count = int(current_manifest_summary.get("combination_promotion_count", 0) or 0)
    previous_extraction_count = int(previous_manifest_summary.get("extraction_count", 0) or 0)
    current_extraction_count = int(current_manifest_summary.get("extraction_count", 0) or 0)

    meaningful_delta = any(
        [
            bool(added_atom_ids),
            bool(removed_atom_ids),
            previous_coverage.get("coverage_strength") != current_coverage.get("coverage_strength"),
            previous_document_count != current_document_count,
            previous_visible_reference_count != current_visible_reference_count,
            previous_pattern_promotion_count != current_pattern_promotion_count,
            previous_combination_promotion_count != current_combination_promotion_count,
            previous_extraction_count != current_extraction_count,
        ]
    )
    summary = (
        f"Knowledge atoms {previous_atom_count}->{current_atom_count}; "
        f"coverage { _text(previous_coverage.get('coverage_strength')) or 'empty'}"
        f"->{_text(current_coverage.get('coverage_strength')) or 'empty'}; "
        f"docs {previous_document_count}->{current_document_count}; "
        f"visible refs {previous_visible_reference_count}->{current_visible_reference_count}."
    )

    return {
        "run_id": _text(run_id),
        "candidate_id": _text(candidate_id),
        "meaningful_delta": meaningful_delta,
        "previous_atom_count": previous_atom_count,
        "current_atom_count": current_atom_count,
        "delta_atom_count": delta_atom_count,
        "added_atom_ids": added_atom_ids,
        "removed_atom_ids": removed_atom_ids,
        "previous_document_count": previous_document_count,
        "current_document_count": current_document_count,
        "previous_visible_reference_count": previous_visible_reference_count,
        "current_visible_reference_count": current_visible_reference_count,
        "previous_coverage_strength": _text(previous_coverage.get("coverage_strength")) or "empty",
        "current_coverage_strength": _text(current_coverage.get("coverage_strength")) or "empty",
        "previous_pattern_promotion_count": previous_pattern_promotion_count,
        "current_pattern_promotion_count": current_pattern_promotion_count,
        "previous_combination_promotion_count": previous_combination_promotion_count,
        "current_combination_promotion_count": current_combination_promotion_count,
        "previous_extraction_count": previous_extraction_count,
        "current_extraction_count": current_extraction_count,
        "summary": summary,
    }
