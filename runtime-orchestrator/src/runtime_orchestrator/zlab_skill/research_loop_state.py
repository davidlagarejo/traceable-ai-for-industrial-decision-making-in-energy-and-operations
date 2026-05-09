from __future__ import annotations

from typing import Any, Mapping

from .research_loop_policies import (
    build_research_depth_enforcement_record,
    determine_target_combination_floor,
    evaluate_combination_pool_sufficiency,
)


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


def build_research_loop_metrics(
    *,
    discovery_candidate_review_register: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
    knowledge_atom_register: list[dict[str, Any]] | None,
    latent_combination_candidate_register: list[dict[str, Any]] | None,
    admissible_combination_review_register: list[dict[str, Any]] | None,
    combination_review_queue_summary: Mapping[str, Any] | None,
    search_query_execution_register: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    discovery_rows = list(discovery_candidate_review_register or [])
    reference_rows = list(article_reference_register or [])
    queue_summary = dict(combination_review_queue_summary or {})
    latent_candidate_count, latent_candidate_row_count = _unique_combination_count(latent_combination_candidate_register)
    admissible_candidate_count, admissible_candidate_row_count = _unique_combination_count(admissible_combination_review_register)
    queryseed_count = sum(1 for row in discovery_rows if _text(row.get("candidate_id")).startswith("queryseed-"))
    query_seed_draft_count = sum(1 for row in reference_rows if _text(row.get("reference_state")) == "query_seed_draft")
    captured_result_count = sum(
        1
        for row in reference_rows
        if _text(row.get("reference_state")) == "query_seed_draft"
        and (
            _text((row.get("acquisition_result", {}) or {}).get("status")) == "query_seed_result_captured"
            or _text((row.get("acquisition_result", {}) or {}).get("search_result_title"))
            or _text((row.get("acquisition_result", {}) or {}).get("search_result_snippet"))
        )
    )
    manual_enriched_count = sum(1 for row in reference_rows if _text(row.get("reference_state")) == "manual_text_enriched")
    visible_enriched_count = sum(1 for row in reference_rows if _text(row.get("reference_state")) == "visible_text_enriched")
    resolved_reference_count = manual_enriched_count + visible_enriched_count
    execution_rows = list(search_query_execution_register or [])
    imported_result_candidate_count = sum(
        1 for row in execution_rows if int(row.get("imported_result_option_count", 0) or 0) > 0
    )
    imported_result_option_count = sum(
        int(row.get("imported_result_option_count", 0) or 0)
        for row in execution_rows
    )
    return {
        "seeded_query_count": queryseed_count,
        "query_seed_draft_count": query_seed_draft_count,
        "captured_result_count": captured_result_count,
        "imported_result_candidate_count": imported_result_candidate_count,
        "imported_result_option_count": imported_result_option_count,
        "resolved_reference_count": resolved_reference_count,
        "manual_text_enriched_count": manual_enriched_count,
        "visible_text_enriched_count": visible_enriched_count,
        "knowledge_atom_count": len(list(knowledge_atom_register or [])),
        "latent_candidate_count": latent_candidate_count,
        "latent_candidate_row_count": latent_candidate_row_count,
        "admissible_candidate_count": admissible_candidate_count,
        "admissible_candidate_row_count": admissible_candidate_row_count,
        "deferred_combination_count": int(queue_summary.get("deferred", 0) or 0),
        "combination_queue_pending_count": int(queue_summary.get("pending", 0) or 0),
    }


def build_research_stop_condition_record(
    *,
    research_loop_metrics: Mapping[str, Any],
    source_coverage_summary: Mapping[str, Any] | None,
    combination_search_gap_record: Mapping[str, Any] | None,
    asset_context_vector: Mapping[str, Any] | None,
    source_family_coverage_register: list[dict[str, Any]] | None = None,
    research_depth_enforcement_record: Mapping[str, Any] | None = None,
    research_loop_control_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = dict(research_loop_metrics or {})
    coverage = dict(source_coverage_summary or {})
    gap = dict(combination_search_gap_record or {})
    depth = dict(research_depth_enforcement_record or {})
    control = dict(research_loop_control_record or {})
    control_state = _text(control.get("control_state")) or "active"
    control_reason = _text(control.get("control_reason"))
    target_floor = determine_target_combination_floor(
        asset_context_vector=asset_context_vector,
        source_coverage_summary=coverage,
    )
    if not depth:
        depth = build_research_depth_enforcement_record(
            research_loop_metrics=metrics,
            source_coverage_summary=coverage,
            source_family_coverage_register=source_family_coverage_register,
            combination_search_gap_record=gap,
            asset_context_vector=asset_context_vector,
        )
    sufficiency = evaluate_combination_pool_sufficiency(
        latent_candidate_count=int(metrics.get("latent_candidate_count", 0) or 0),
        target_combination_floor=target_floor,
        coverage_strength=_text(coverage.get("coverage_strength")),
        search_status=_text(gap.get("search_status")),
    )
    unresolved_jobs = (
        int(metrics.get("seeded_query_count", 0) or 0)
        + int(metrics.get("query_seed_draft_count", 0) or 0)
        - int(metrics.get("resolved_reference_count", 0) or 0)
    )
    reasons: list[str] = []
    if sufficiency["pool_sufficiency"] == "below_floor":
        reasons.append("latent combination pool remains below the target floor")
    if _text(gap.get("search_status")) == "incomplete_under_investigated":
        reasons.append("combination search gap still marks the run as under-investigated")
    for reason in list(depth.get("policy_reasons", []) or []):
        reason_text = _text(reason)
        if reason_text and reason_text not in reasons:
            reasons.append(reason_text)
    if unresolved_jobs > 0:
        reasons.append("query seeds or drafts still require resolution")
    if control_state == "paused_by_operator":
        stop_state = "paused_by_operator"
        reasons = [control_reason or "research loop paused by operator"]
    elif control_state == "stopped_by_operator":
        stop_state = "stopped_by_operator"
        reasons = [control_reason or "research loop stopped by operator"]
    elif (
        not reasons
        and (sufficiency["can_stop"] or bool(depth.get("saturation_proof_strong")))
        and not bool(depth.get("must_continue_research"))
    ):
        stop_state = "stopped_by_saturation"
        reasons.extend(
            [
                "latent combination floor is strong enough for a controlled stop",
                "coverage depth is strong enough for a controlled stop",
                "remaining high-value source families are exhausted or already strong",
                "unresolved research jobs are low enough to stop",
            ]
        )
    else:
        stop_state = "continue_research"
    return {
        "stop_state": stop_state,
        "reasons": reasons,
        "coverage_proof_strength": _text(coverage.get("coverage_strength")) or "empty",
        "combination_pool_sufficiency": _text(sufficiency.get("pool_sufficiency")),
        "target_combination_floor": int(sufficiency.get("target_combination_floor", 0) or 0),
        "remaining_open_jobs": max(unresolved_jobs, 0),
        "depth_state": _text(depth.get("depth_state")) or "unknown",
        "saturation_proof_strong": bool(depth.get("saturation_proof_strong")),
        "required_next_source_families": [
            _text(item)
            for item in list(depth.get("required_next_source_families", []) or [])
            if _text(item)
        ],
        "operator_control_state": control_state,
        "operator_control_reason": control_reason,
        "remaining_high_priority_source_families": len(
            [
                _text(item)
                for item in list(depth.get("required_next_source_families", []) or [])
                if _text(item)
            ]
        ),
    }


def build_research_loop_state(
    *,
    run_id: str,
    current_combination_review_row: Mapping[str, Any] | None,
    research_loop_metrics: Mapping[str, Any],
    source_coverage_summary: Mapping[str, Any] | None,
    combination_search_gap_record: Mapping[str, Any] | None,
    research_campaign_record: Mapping[str, Any] | None,
    research_stop_condition_record: Mapping[str, Any],
    research_loop_job_register: list[dict[str, Any]] | None,
    research_loop_control_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = dict(research_loop_metrics or {})
    coverage = dict(source_coverage_summary or {})
    gap = dict(combination_search_gap_record or {})
    campaign = dict(research_campaign_record or {})
    stop = dict(research_stop_condition_record or {})
    control = dict(research_loop_control_record or {})
    control_state = _text(control.get("control_state")) or "active"
    control_reason = _text(control.get("control_reason"))
    current_row = dict(current_combination_review_row or {})
    jobs = list(research_loop_job_register or [])
    current_job = dict(jobs[0] if jobs else {})
    next_action = _text(current_job.get("recommended_action")) or "PRESENT_NEXT_COMBINATION"

    if control_state == "paused_by_operator":
        loop_status = "paused_by_operator"
        next_action = "PAUSED_BY_OPERATOR"
    elif _text(stop.get("stop_state")) == "stopped_by_operator":
        loop_status = "stopped_by_operator"
        next_action = "STOPPED_BY_OPERATOR"
    elif _text(stop.get("stop_state")) == "stopped_by_saturation":
        loop_status = "stopped_by_saturation"
        next_action = "STOPPED_BY_SATURATION"
    elif next_action == "SEED_QUERY_CANDIDATES":
        loop_status = "seeding_queries"
    elif next_action == "CAPTURE_SEARCH_RESULT":
        loop_status = "awaiting_search_result_capture"
    elif next_action == "PROMOTE_IMPORTED_RESULT":
        loop_status = "awaiting_imported_result_promotion"
    elif next_action in {"READ_OR_DRAFT_REFERENCE", "RESOLVE_REFERENCE_DRAFT", "RESOLVE_REFERENCE_EXCERPT"}:
        loop_status = "awaiting_reference_resolution"
    elif next_action in {"REFRESH_REFERENCE_BACKED_PROMOTIONS", "RERANK_LATENT_POOL"}:
        loop_status = "reranking_combinations"
    elif _text(current_row.get("combination_id")):
        loop_status = "review_ready"
    else:
        loop_status = "planning"

    return {
        "run_id": _text(run_id),
        "loop_status": loop_status,
        "campaign_status": _text(campaign.get("campaign_status")) or "coverage_building",
        "latent_candidate_count": int(metrics.get("latent_candidate_count", 0) or 0),
        "admissible_candidate_count": int(metrics.get("admissible_candidate_count", 0) or 0),
        "reference_draft_count": int(metrics.get("query_seed_draft_count", 0) or 0),
        "captured_result_count": int(metrics.get("captured_result_count", 0) or 0),
        "imported_result_candidate_count": int(metrics.get("imported_result_candidate_count", 0) or 0),
        "imported_result_option_count": int(metrics.get("imported_result_option_count", 0) or 0),
        "resolved_reference_count": int(metrics.get("resolved_reference_count", 0) or 0),
        "knowledge_atom_count": int(metrics.get("knowledge_atom_count", 0) or 0),
        "search_gap_status": _text(gap.get("search_status")) or "unknown",
        "coverage_strength": _text(coverage.get("coverage_strength")) or "empty",
        "stop_condition_state": _text(stop.get("stop_state")) or "continue_research",
        "operator_control_state": control_state,
        "operator_control_reason": control_reason,
        "next_action": next_action,
        "current_combination_id": _text(current_row.get("combination_id")),
        "current_job_id": _text(current_job.get("job_id")),
    }
