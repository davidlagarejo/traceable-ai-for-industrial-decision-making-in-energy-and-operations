from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.search_budget import (
    build_search_budget_register,
    build_search_exhaustion_register,
)


def test_search_budget_register_tracks_total_and_extended_scopes():
    attempts = [
        {"attempt_kind": "primary", "status": "found"},
        {"attempt_kind": "primary", "status": "failed"},
        {"attempt_kind": "extended", "status": "no_data"},
        {"attempt_kind": "extended", "status": "found"},
    ]
    rows = build_search_budget_register(
        target_definition={"target_type": "warehouse_distribution"},
        discovery_runtime_profile={
            "total_elapsed_seconds": 41.2,
            "extended_elapsed_seconds": 18.1,
            "total_budget_seconds": 150,
            "extended_budget_seconds": 90,
            "extended_budget_exhausted": False,
        },
        discovery_summary={"queried": 4, "found": 2},
        attempts=attempts,
    )

    by_scope = {row["budget_scope"]: row for row in rows}
    assert by_scope["total_public_discovery"]["budget_state"] == "bounded"
    assert by_scope["extended_public_discovery"]["attempt_count"] == 2
    assert by_scope["total_public_discovery"]["budget_class"] == "bounded_public_discovery"


def test_search_exhaustion_register_marks_operator_escalation_when_budget_exhausted():
    attempts = [
        {"attempt_kind": "extended", "status": "time_budget_exhausted"},
    ]
    budget_rows = build_search_budget_register(
        target_definition={"target_type": "warehouse_distribution"},
        discovery_runtime_profile={
            "total_elapsed_seconds": 150.0,
            "extended_elapsed_seconds": 90.0,
            "total_budget_seconds": 150,
            "extended_budget_seconds": 90,
            "extended_budget_exhausted": True,
        },
        discovery_summary={"queried": 12, "found": 4},
        attempts=attempts,
    )
    exhaustion = build_search_exhaustion_register(
        search_budget_register=budget_rows,
        attempts=attempts,
        gaps=[{"gap_type": "extended_source_time_budget_exhausted"}],
    )

    assert exhaustion
    assert any(row["exhaustion_reason"] == "extended_time_budget_exhausted" for row in exhaustion)
    assert any(row["escalation_path"] == "operator_or_dynamic_intake" for row in exhaustion)
