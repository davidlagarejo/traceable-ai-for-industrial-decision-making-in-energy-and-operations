from __future__ import annotations

from typing import Any

from .schemas import text


def build_search_budget_register(
    *,
    target_definition: dict[str, Any],
    discovery_runtime_profile: dict[str, Any],
    discovery_summary: dict[str, Any],
    attempts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = text(target_definition.get("target_type")) or "unknown_target_type"
    total_elapsed_seconds = float(discovery_runtime_profile.get("total_elapsed_seconds", 0.0) or 0.0)
    total_budget_seconds = float(discovery_runtime_profile.get("total_budget_seconds", 0.0) or 0.0)
    extended_elapsed_seconds = float(discovery_runtime_profile.get("extended_elapsed_seconds", 0.0) or 0.0)
    extended_budget_seconds = float(discovery_runtime_profile.get("extended_budget_seconds", 0.0) or 0.0)
    query_attempt_count = int(discovery_summary.get("queried", 0) or 0)
    found_count = int(discovery_summary.get("found", 0) or 0)
    budget_class = (
        "identity_only_screening"
        if query_attempt_count <= 3
        else "bounded_public_discovery"
        if query_attempt_count <= 20
        else "expanded_public_discovery"
    )

    return [
        {
            "budget_scope": "total_public_discovery",
            "budget_class": budget_class,
            "target_type": target_type,
            "elapsed_seconds": round(total_elapsed_seconds, 3),
            "budget_seconds": round(total_budget_seconds, 3),
            "budget_state": (
                "exhausted"
                if bool(discovery_runtime_profile.get("extended_budget_exhausted", False)) and total_elapsed_seconds >= total_budget_seconds > 0
                else "bounded"
            ),
            "attempt_count": len(list(attempts or [])),
            "queried_count": query_attempt_count,
            "found_count": found_count,
            "why_it_stopped": (
                "time_budget_exhausted" if total_elapsed_seconds >= total_budget_seconds > 0 else "registry_or_routing_completed"
            ),
        },
        {
            "budget_scope": "extended_public_discovery",
            "budget_class": budget_class,
            "target_type": target_type,
            "elapsed_seconds": round(extended_elapsed_seconds, 3),
            "budget_seconds": round(extended_budget_seconds, 3),
            "budget_state": (
                "exhausted"
                if bool(discovery_runtime_profile.get("extended_budget_exhausted", False))
                else "bounded"
            ),
            "attempt_count": sum(1 for row in list(attempts or []) if text(row.get("attempt_kind")) == "extended"),
            "queried_count": sum(
                1
                for row in list(attempts or [])
                if text(row.get("attempt_kind")) == "extended"
                and text(row.get("status")) in {"found", "failed", "no_data"}
            ),
            "found_count": sum(
                1
                for row in list(attempts or [])
                if text(row.get("attempt_kind")) == "extended" and text(row.get("status")) == "found"
            ),
            "why_it_stopped": (
                "extended_time_budget_exhausted"
                if bool(discovery_runtime_profile.get("extended_budget_exhausted", False))
                else "extended_registry_or_routing_completed"
            ),
        },
    ]


def build_search_exhaustion_register(
    *,
    search_budget_register: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    exhaustion_rows: list[dict[str, Any]] = []
    exhaustion_gap_types = {
        text(row.get("gap_type"))
        for row in list(gaps or [])
        if text(row.get("gap_type"))
    }
    for row in list(search_budget_register or []):
        budget_scope = text(row.get("budget_scope"))
        budget_state = text(row.get("budget_state"))
        if budget_state != "exhausted":
            continue
        exhaustion_rows.append(
            {
                "budget_scope": budget_scope,
                "exhaustion_reason": text(row.get("why_it_stopped")) or "time_budget_exhausted",
                "attempt_count": int(row.get("attempt_count", 0) or 0),
                "queried_count": int(row.get("queried_count", 0) or 0),
                "gap_types": sorted(exhaustion_gap_types),
                "escalation_path": "operator_or_dynamic_intake" if any(text(attempt.get("status")) == "time_budget_exhausted" for attempt in list(attempts or [])) else "none_required",
            }
        )
    return exhaustion_rows
