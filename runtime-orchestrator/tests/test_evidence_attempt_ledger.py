from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.evidence_attempts import (
    build_search_attempt_ledger,
    build_search_attempt_outcome_register,
)


def test_search_attempt_ledger_normalizes_attempt_rows():
    ledger = build_search_attempt_ledger(
        attempts=[
            {
                "attempt_kind": "primary",
                "round_id": "round_1_identity",
                "source_type": "census_geocoder_validation",
                "source_family": "geospatial_public_record",
                "discovery_reason": "Bound the asset address.",
                "locator": "census://address",
                "status": "found",
                "lifecycle_stage": "admitted_candidate",
                "produced_at": "2026-05-02T12:00:00Z",
            },
            {
                "attempt_kind": "extended",
                "round_id": "round_5_extended",
                "source_type": "county_assessor_property_record",
                "source_family": "geospatial_public_record",
                "discovery_reason": "Find parcel-level confirmation.",
                "locator": "county://parcel",
                "status": "time_budget_exhausted",
                "lifecycle_stage": "deferred_budget_exhausted",
                "produced_at": "2026-05-02T12:00:01Z",
            },
        ]
    )

    assert ledger[0]["outcome_class"] == "evidence_found"
    assert ledger[0]["blocker_removed"] is True
    assert ledger[1]["outcome_class"] == "deferred_budget_exhausted"
    assert ledger[1]["blocker_removed"] is False


def test_search_attempt_outcome_register_aggregates_by_kind_and_outcome():
    outcome_rows = build_search_attempt_outcome_register(
        search_attempt_ledger=[
            {"attempt_kind": "primary", "outcome_class": "evidence_found"},
            {"attempt_kind": "primary", "outcome_class": "attempt_failed"},
            {"attempt_kind": "extended", "outcome_class": "attempt_failed"},
            {"attempt_kind": "extended", "outcome_class": "attempt_failed"},
        ]
    )

    by_key = {(row["attempt_kind"], row["outcome_class"]): row["attempt_count"] for row in outcome_rows}
    assert by_key[("primary", "evidence_found")] == 1
    assert by_key[("primary", "attempt_failed")] == 1
    assert by_key[("extended", "attempt_failed")] == 2
