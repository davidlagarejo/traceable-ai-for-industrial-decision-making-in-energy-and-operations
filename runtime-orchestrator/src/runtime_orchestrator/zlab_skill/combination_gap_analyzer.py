from __future__ import annotations

from typing import Any, Mapping

from .research_loop_policies import build_target_combination_floor_record


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _unique_combination_count(rows: list[dict[str, Any]] | None) -> tuple[int, int]:
    register = list(rows or [])
    unique_ids: set[str] = set()
    fallback_index = 0
    for row in register:
        combination_id = _text(row.get("combination_id"))
        if combination_id:
            unique_ids.add(combination_id)
            continue
        fallback_id = _text(row.get("combination_name")) or _text(row.get("cluster_id")) or f"row::{fallback_index}"
        unique_ids.add(fallback_id)
        fallback_index += 1
    return len(unique_ids), len(register)


def build_combination_search_gap_record(
    *,
    latent_combination_candidate_register: list[dict[str, Any]] | None,
    admissible_combination_review_register: list[dict[str, Any]] | None = None,
    source_coverage_summary: Mapping[str, Any] | None = None,
    source_family_coverage_register: list[dict[str, Any]] | None = None,
    asset_context_vector: Mapping[str, Any] | None = None,
    active_pattern_ids: list[str] | set[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    latent_rows = list(latent_combination_candidate_register or [])
    admissible_rows = list(admissible_combination_review_register or [])
    coverage = dict(source_coverage_summary or {})
    coverage_rows = [dict(row) for row in list(source_family_coverage_register or [])]
    vector = dict(asset_context_vector or {})
    active_patterns = [_text(item) for item in list(active_pattern_ids or []) if _text(item)]

    latent_count, latent_row_count = _unique_combination_count(latent_rows)
    admissible_count, admissible_row_count = _unique_combination_count(admissible_rows)
    document_count = int(coverage.get("document_count", 0) or 0)
    provider_count = int(coverage.get("provider_count", 0) or 0)
    knowledge_atom_count = int(coverage.get("knowledge_atom_count", 0) or 0)
    visible_reference_count = int(coverage.get("visible_reference_count", 0) or 0)
    supported_pattern_count = int(coverage.get("supported_pattern_count", 0) or 0)
    coverage_strength = _text(coverage.get("coverage_strength")) or "empty"
    asset_family = _text(vector.get("asset_family")) or "unknown_asset_family"

    floor_record = build_target_combination_floor_record(
        asset_context_vector=vector,
        source_coverage_summary=coverage,
    )
    target_latent_pool = int(floor_record.get("target_combination_floor", 50) or 50)
    minimum_latent_pool = min(20, target_latent_pool) if target_latent_pool <= 20 else max(target_latent_pool // 2, 20)
    raw_coverage_proof_strong = (
        coverage_strength == "strong"
        or (
            provider_count >= 2
            and document_count >= 3
            and knowledge_atom_count >= 8
        )
    )
    available_rows = [
        row for row in coverage_rows if _text(row.get("coverage_state")) != "not_available"
    ]
    strong_rows = [
        row for row in available_rows if _text(row.get("coverage_state")) == "strong"
    ]
    high_priority_rows = [
        row for row in available_rows if _text(row.get("importance")) == "high"
    ]
    touched_high_priority_rows = [
        row for row in high_priority_rows if _text(row.get("coverage_state")) in {"thin", "strong"}
    ]
    strong_high_priority_rows = [
        row for row in high_priority_rows if _text(row.get("coverage_state")) == "strong"
    ]
    minimum_strong_source_family_count = min(
        3 if target_latent_pool >= 100 else 2 if target_latent_pool >= 50 else 1,
        max(len(available_rows), 1),
    )
    minimum_touched_high_priority_count = min(
        2 if target_latent_pool >= 50 else 1,
        len(high_priority_rows),
    )
    source_depth_strong = (
        not available_rows
        or (
            len(strong_rows) >= minimum_strong_source_family_count
            and (
                not high_priority_rows
                or (
                    len(touched_high_priority_rows) >= minimum_touched_high_priority_count
                    and len(strong_high_priority_rows) >= 1
                )
            )
        )
    )
    coverage_proof_strong = raw_coverage_proof_strong and source_depth_strong

    gap_flags: list[str] = []
    recommended_actions: list[str] = []

    if latent_count == 0:
        gap_flags.append("no_latent_combinations_found")
        recommended_actions.append("Expand the source campaign before concluding that the case has no plausible combinations.")
    if latent_count < minimum_latent_pool:
        gap_flags.append("latent_pool_below_minimum")
        recommended_actions.append("Keep searching across more source families until the latent pool clears the minimum campaign threshold.")
    elif latent_count < target_latent_pool:
        gap_flags.append("latent_pool_below_target")
        recommended_actions.append("Widen source coverage and context rebinding to approach the active latent-combination floor for this campaign.")
    if provider_count < 2:
        gap_flags.append("single_provider_coverage")
        recommended_actions.append("Add at least one more provider or source family before treating the current pool as representative.")
    if document_count < 2:
        gap_flags.append("document_coverage_shallow")
        recommended_actions.append("Collect more documents or references; one document is not enough for a serious structural campaign.")
    if knowledge_atom_count < 5:
        gap_flags.append("knowledge_atom_depth_shallow")
        recommended_actions.append("Extract more reusable knowledge atoms before freezing the current latent pool.")
    if visible_reference_count < 1 and document_count > 0:
        gap_flags.append("visible_text_coverage_thin")
        recommended_actions.append("Read or curate visible text excerpts so the campaign is not running on metadata alone.")
    if coverage_rows and len(strong_rows) < minimum_strong_source_family_count:
        gap_flags.append("source_family_depth_shallow")
        recommended_actions.append("Deepen source-family coverage; the campaign still lacks enough strong source families for this case.")
    if high_priority_rows and (
        len(touched_high_priority_rows) < minimum_touched_high_priority_count
        or len(strong_high_priority_rows) < 1
    ):
        gap_flags.append("high_priority_source_families_undercovered")
        recommended_actions.append("Strengthen high-priority source families before treating the latent pool as representative.")
    if len(active_patterns) < 3 and supported_pattern_count < 3:
        gap_flags.append("pattern_surface_narrow")
        recommended_actions.append("Broaden the active/supporting pattern surface; the current combination grammar is still too narrow.")
    if not coverage_proof_strong:
        gap_flags.append("coverage_proof_not_strong")
        recommended_actions.append("Do not treat a shallow pool as complete until source coverage is demonstrably strong.")

    severity = "low"
    search_status = "complete_enough_for_review"
    if "no_latent_combinations_found" in gap_flags or (
        "latent_pool_below_minimum" in gap_flags and not coverage_proof_strong
    ):
        severity = "high"
        search_status = "incomplete_under_investigated"
    elif gap_flags:
        severity = "medium"
        search_status = "thin_but_reviewable" if coverage_proof_strong else "incomplete_under_investigated"

    summary = (
        f"{asset_family}: latent pool {latent_count} / target {target_latent_pool}, "
        f"coverage {coverage_strength}, docs {document_count}, providers {provider_count}, atoms {knowledge_atom_count}."
    )
    if search_status == "incomplete_under_investigated":
        summary += " The framework should keep researching before treating this pool as representative."
    elif search_status == "thin_but_reviewable":
        summary += " The pool is still thin, but coverage is strong enough to review it with caution."
    else:
        summary += " Coverage and pool size are strong enough for serious review."

    return {
        "asset_family": asset_family,
        "latent_candidate_count": latent_count,
        "latent_candidate_row_count": latent_row_count,
        "admissible_candidate_count": admissible_count,
        "admissible_candidate_row_count": admissible_row_count,
        "target_latent_pool": target_latent_pool,
        "target_floor_policy_state": _text(floor_record.get("policy_state")) or "normal_target",
        "bootstrap_floor_exception": bool(floor_record.get("bootstrap_floor_exception")),
        "target_floor_policy_reason": _text(floor_record.get("policy_reason")),
        "minimum_latent_pool": minimum_latent_pool,
        "coverage_strength": coverage_strength,
        "coverage_proof_strong": coverage_proof_strong,
        "provider_count": provider_count,
        "document_count": document_count,
        "knowledge_atom_count": knowledge_atom_count,
        "visible_reference_count": visible_reference_count,
        "supported_pattern_count": supported_pattern_count,
        "active_pattern_count": len(active_patterns),
        "strong_source_family_count": len(strong_rows),
        "minimum_strong_source_family_count": minimum_strong_source_family_count,
        "high_priority_source_family_count": len(high_priority_rows),
        "strong_high_priority_source_family_count": len(strong_high_priority_rows),
        "minimum_touched_high_priority_count": minimum_touched_high_priority_count,
        "search_status": search_status,
        "severity": severity,
        "gap_flags": gap_flags,
        "recommended_actions": recommended_actions,
        "summary": summary,
    }
