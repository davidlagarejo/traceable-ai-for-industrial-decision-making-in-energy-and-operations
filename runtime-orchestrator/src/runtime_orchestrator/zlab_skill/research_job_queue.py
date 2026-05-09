from __future__ import annotations

from typing import Any, Mapping

from .research_query_runner import (
    build_search_query_execution_register,
    build_search_result_capture_register,
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _notes_for_candidate(candidate_row: Mapping[str, Any] | None) -> str:
    row = dict(candidate_row or {})
    return _text((row.get("metadata_payload", {}) or {}).get("notes")) or _text(row.get("notes"))


def _related_queryseed_candidates(
    *,
    combination_id: str,
    discovery_candidate_review_register: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    normalized_combination_id = _text(combination_id)
    for row in list(discovery_candidate_review_register or []):
        candidate_id = _text(row.get("candidate_id"))
        notes = _notes_for_candidate(row)
        if candidate_id.startswith("queryseed-") and normalized_combination_id and normalized_combination_id in notes:
            rows.append(dict(row))
    return rows


def build_research_loop_job_register(
    *,
    run_id: str,
    current_combination_review_row: Mapping[str, Any] | None,
    combination_follow_on_execution_manifest_register: list[dict[str, Any]] | None,
    discovery_candidate_review_register: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
    research_campaign_trigger_register: list[dict[str, Any]] | None,
    search_query_execution_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    current_row = dict(current_combination_review_row or {})
    combination_id = _text(current_row.get("combination_id"))
    current_manifest = next(
        (
            dict(row)
            for row in list(combination_follow_on_execution_manifest_register or [])
            if _text(row.get("combination_id")) == combination_id
        ),
        {},
    )
    related_queryseed_ids = {
        _text(row.get("candidate_id"))
        for row in _related_queryseed_candidates(
            combination_id=combination_id,
            discovery_candidate_review_register=discovery_candidate_review_register,
        )
        if _text(row.get("candidate_id"))
    }
    search_capture_register = build_search_result_capture_register(
        discovery_candidate_review_register=discovery_candidate_review_register,
        article_reference_register=article_reference_register,
    )
    related_capture_rows = [
        dict(row)
        for row in search_capture_register
        if _text(row.get("candidate_id")) in related_queryseed_ids
    ]
    execution_register = list(search_query_execution_register or [])
    if not execution_register:
        execution_register = build_search_query_execution_register(
            search_result_capture_register=search_capture_register,
        )
    execution_by_candidate_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in execution_register
        if _text(row.get("candidate_id"))
    }

    jobs: list[dict[str, Any]] = []

    def _append_job(
        *,
        job_id: str,
        job_type: str,
        status: str,
        priority: int,
        summary: str,
        recommended_action: str,
        provider_key: str = "",
        source_family: str = "",
        candidate_id: str = "",
        query_family: str = "",
        reasoning_flags: list[str] | None = None,
    ) -> None:
        jobs.append(
            {
                "job_id": job_id,
                "job_type": job_type,
                "status": status,
                "priority": int(priority),
                "run_id": _text(run_id),
                "combination_id": combination_id,
                "combination_name": _text(current_row.get("combination_name")) or combination_id,
                "candidate_id": _text(candidate_id),
                "provider_key": _text(provider_key),
                "source_family": _text(source_family),
                "query_family": _text(query_family),
                "summary": _text(summary),
                "recommended_action": _text(recommended_action),
                "reasoning_flags": list(reasoning_flags or []),
            }
        )

    if combination_id and current_manifest and not related_queryseed_ids:
        _append_job(
            job_id=f"job::{combination_id}::seed_query_candidates",
            job_type="seed_query_candidates",
            status="pending",
            priority=100,
            summary="Seed provider-specific research leads for the current combination.",
            recommended_action="SEED_QUERY_CANDIDATES",
            reasoning_flags=list(current_manifest.get("reasoning_flags", []) or []),
        )

    for row in related_capture_rows:
        candidate_id = _text(row.get("candidate_id"))
        provider_key = _text(row.get("provider_key"))
        source_family = _text(row.get("source_family"))
        query_family = _text(row.get("query_family"))
        next_capture_action = _text(row.get("next_capture_action"))
        ref_state = _text(row.get("reference_state")) or "metadata_only"
        execution_row = dict(execution_by_candidate_id.get(candidate_id, {}) or {})
        imported_option_count = int(execution_row.get("imported_result_option_count", 0) or 0)
        if next_capture_action == "READ_OR_DRAFT_REFERENCE":
            _append_job(
                job_id=f"job::{candidate_id}::draft_reference",
                job_type="draft_reference",
                status="pending",
                priority=90,
                summary=f"Create a query-seed draft reference for {candidate_id}.",
                recommended_action="READ_OR_DRAFT_REFERENCE",
                provider_key=provider_key,
                source_family=source_family,
                candidate_id=candidate_id,
                query_family=query_family,
            )
        elif next_capture_action == "CAPTURE_SEARCH_RESULT":
            if imported_option_count > 0:
                _append_job(
                    job_id=f"job::{candidate_id}::promote_imported_result",
                    job_type="promote_imported_result",
                    status="waiting_for_operator",
                    priority=86,
                    summary=f"Review and promote one of {imported_option_count} imported search-result option(s) for {candidate_id}.",
                    recommended_action="PROMOTE_IMPORTED_RESULT",
                    provider_key=provider_key,
                    source_family=source_family,
                    candidate_id=candidate_id,
                    query_family=query_family,
                )
            else:
                _append_job(
                    job_id=f"job::{candidate_id}::capture_search_result",
                    job_type="capture_search_result",
                    status="waiting_for_operator",
                    priority=85,
                    summary=f"Capture search-result URL and snippet for query-seed draft {candidate_id}.",
                    recommended_action="CAPTURE_SEARCH_RESULT",
                    provider_key=provider_key,
                    source_family=source_family,
                    candidate_id=candidate_id,
                    query_family=query_family,
                )
        elif next_capture_action == "RESOLVE_REFERENCE_EXCERPT":
            _append_job(
                job_id=f"job::{candidate_id}::resolve_reference_excerpt",
                job_type="resolve_reference_excerpt",
                status="waiting_for_operator",
                priority=80,
                summary=f"Resolve query-seed draft {candidate_id} with a real visible excerpt.",
                recommended_action="RESOLVE_REFERENCE_EXCERPT",
                provider_key=provider_key,
                source_family=source_family,
                candidate_id=candidate_id,
                query_family=query_family,
            )
        elif ref_state in {"manual_text_enriched", "visible_text_enriched"}:
            _append_job(
                job_id=f"job::{candidate_id}::refresh_reference_backed_promotions",
                job_type="refresh_reference_backed_promotions",
                status="ready",
                priority=70,
                summary=f"Refresh atoms and promotions after enriched reference {candidate_id}.",
                recommended_action="REFRESH_REFERENCE_BACKED_PROMOTIONS",
                provider_key=provider_key,
                source_family=source_family,
                candidate_id=candidate_id,
                query_family=query_family,
            )

    for row in list(research_campaign_trigger_register or []):
        if _text(row.get("status")) != "queued":
            continue
        _append_job(
            job_id=f"job::source_family::{_text(row.get('source_family'))}",
            job_type="trigger_deeper_source_family_search",
            status="queued",
            priority=60 if _text(row.get("importance")) == "high" else 50,
            summary=_text(row.get("reason")) or f"Expand source family {_text(row.get('source_family'))}.",
            recommended_action="TRIGGER_DEEPER_SOURCE_FAMILY_SEARCH",
            provider_key="|".join([_text(item) for item in list(row.get("recommended_provider_keys", []) or []) if _text(item)]),
            source_family=_text(row.get("source_family")),
        )

    jobs.sort(key=lambda row: (-int(row.get("priority", 0) or 0), _text(row.get("job_id"))))
    return jobs
