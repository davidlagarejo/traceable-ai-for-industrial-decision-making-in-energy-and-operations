from __future__ import annotations

from typing import Any, Mapping

from .research_job_queue import build_research_loop_job_register
from .research_loop_policies import build_research_depth_enforcement_record
from .research_loop_state import (
    build_research_loop_metrics,
    build_research_loop_state,
    build_research_stop_condition_record,
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def build_research_loop_snapshot(
    *,
    run_id: str,
    current_combination_review_row: Mapping[str, Any] | None,
    combination_follow_on_execution_manifest_register: list[dict[str, Any]] | None,
    discovery_candidate_review_register: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
    research_campaign_trigger_register: list[dict[str, Any]] | None,
    knowledge_atom_register: list[dict[str, Any]] | None,
    latent_combination_candidate_register: list[dict[str, Any]] | None,
    admissible_combination_review_register: list[dict[str, Any]] | None,
    combination_review_queue_summary: Mapping[str, Any] | None,
    source_coverage_summary: Mapping[str, Any] | None,
    source_family_coverage_register: list[dict[str, Any]] | None,
    combination_search_gap_record: Mapping[str, Any] | None,
    research_campaign_record: Mapping[str, Any] | None,
    asset_context_vector: Mapping[str, Any] | None,
    research_loop_control_record: Mapping[str, Any] | None = None,
    search_query_execution_register: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    jobs = build_research_loop_job_register(
        run_id=run_id,
        current_combination_review_row=current_combination_review_row,
        combination_follow_on_execution_manifest_register=combination_follow_on_execution_manifest_register,
        discovery_candidate_review_register=discovery_candidate_review_register,
        article_reference_register=article_reference_register,
        research_campaign_trigger_register=research_campaign_trigger_register,
        search_query_execution_register=search_query_execution_register,
    )
    metrics = build_research_loop_metrics(
        discovery_candidate_review_register=discovery_candidate_review_register,
        article_reference_register=article_reference_register,
        knowledge_atom_register=knowledge_atom_register,
        latent_combination_candidate_register=latent_combination_candidate_register,
        admissible_combination_review_register=admissible_combination_review_register,
        combination_review_queue_summary=combination_review_queue_summary,
        search_query_execution_register=search_query_execution_register,
    )
    depth_record = build_research_depth_enforcement_record(
        research_loop_metrics=metrics,
        source_coverage_summary=source_coverage_summary,
        source_family_coverage_register=source_family_coverage_register,
        combination_search_gap_record=combination_search_gap_record,
        asset_context_vector=asset_context_vector,
    )
    stop_record = build_research_stop_condition_record(
        research_loop_metrics=metrics,
        source_coverage_summary=source_coverage_summary,
        combination_search_gap_record=combination_search_gap_record,
        asset_context_vector=asset_context_vector,
        source_family_coverage_register=source_family_coverage_register,
        research_depth_enforcement_record=depth_record,
        research_loop_control_record=research_loop_control_record,
    )
    state = build_research_loop_state(
        run_id=run_id,
        current_combination_review_row=current_combination_review_row,
        research_loop_metrics=metrics,
        source_coverage_summary=source_coverage_summary,
        combination_search_gap_record=combination_search_gap_record,
        research_campaign_record=research_campaign_record,
        research_stop_condition_record=stop_record,
        research_loop_job_register=jobs,
        research_loop_control_record=research_loop_control_record,
    )
    return {
        "state": state,
        "jobs": jobs,
        "current_job": dict(jobs[0] if jobs else {}),
        "metrics": metrics,
        "depth_enforcement": depth_record,
        "control": dict(research_loop_control_record or {}),
        "stop_condition": stop_record,
    }


def build_research_loop_event_records(
    *,
    previous_state: Mapping[str, Any] | None,
    previous_current_job: Mapping[str, Any] | None,
    snapshot: Mapping[str, Any] | None,
    event_timestamp: str,
) -> list[dict[str, Any]]:
    prior_state = dict(previous_state or {})
    prior_job = dict(previous_current_job or {})
    snap = dict(snapshot or {})
    current_state = dict(snap.get("state", {}) or {})
    current_job = dict(snap.get("current_job", {}) or {})
    rows: list[dict[str, Any]] = []

    if _text(prior_state.get("loop_status")) != _text(current_state.get("loop_status")):
        rows.append(
            {
                "event_id": f"event::{_text(current_state.get('run_id'))}::loop_status::{event_timestamp}",
                "event_type": "loop_state_transition",
                "entity_type": "research_loop_state",
                "entity_id": _text(current_state.get("run_id")),
                "combination_id": _text(current_state.get("current_combination_id")),
                "summary": (
                    f"Loop status changed from {_text(prior_state.get('loop_status')) or 'unset'} "
                    f"to {_text(current_state.get('loop_status')) or 'unset'}."
                ),
                "created_at": event_timestamp,
            }
        )

    if _text(prior_job.get("job_id")) != _text(current_job.get("job_id")) and _text(current_job.get("job_id")):
        rows.append(
            {
                "event_id": f"event::{_text(current_state.get('run_id'))}::current_job::{event_timestamp}",
                "event_type": "current_job_changed",
                "entity_type": "research_job",
                "entity_id": _text(current_job.get("job_id")),
                "combination_id": _text(current_job.get("combination_id")),
                "summary": _text(current_job.get("summary")) or "Current research job changed.",
                "created_at": event_timestamp,
            }
        )
    if _text(prior_state.get("stop_condition_state")) != _text(current_state.get("stop_condition_state")):
        rows.append(
            {
                "event_id": f"event::{_text(current_state.get('run_id'))}::stop_condition::{event_timestamp}",
                "event_type": "stop_condition_changed",
                "entity_type": "research_loop_stop_condition",
                "entity_id": _text(current_state.get("run_id")),
                "combination_id": _text(current_state.get("current_combination_id")),
                "summary": (
                    f"Stop condition changed from {_text(prior_state.get('stop_condition_state')) or 'unset'} "
                    f"to {_text(current_state.get('stop_condition_state')) or 'unset'}."
                ),
                "created_at": event_timestamp,
            }
        )
    if _text(prior_state.get("operator_control_state")) != _text(current_state.get("operator_control_state")):
        rows.append(
            {
                "event_id": f"event::{_text(current_state.get('run_id'))}::operator_control::{event_timestamp}",
                "event_type": "operator_control_changed",
                "entity_type": "research_loop_control",
                "entity_id": _text(current_state.get("run_id")),
                "combination_id": _text(current_state.get("current_combination_id")),
                "summary": (
                    f"Operator control changed from {_text(prior_state.get('operator_control_state')) or 'unset'} "
                    f"to {_text(current_state.get('operator_control_state')) or 'unset'}."
                ),
                "created_at": event_timestamp,
            }
        )
    return rows
