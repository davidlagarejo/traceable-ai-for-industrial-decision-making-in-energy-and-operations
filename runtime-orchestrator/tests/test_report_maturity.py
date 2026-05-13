"""V5 P5 — canonical 6-type report maturity tests.

Verifies the deterministic mapping from claim_support_state ladder
(Phase 0 §5.2) to the 6 canonical deliverable types (Phase 0 §10).
"""
from __future__ import annotations

from runtime_orchestrator.report_maturity import (
    CANONICAL_REPORT_MATURITY_TYPES,
    SUPPORT_STATE_LADDER,
    aggregate_maturity_type,
    derive_report_maturity_from_motor_025,
    is_stronger_maturity,
    maturity_type_for_support_state,
    maturity_type_index,
)


# ── Canonical vocabulary ────────────────────────────────────────────


def test_canonical_types_match_master_doc():
    """Phase 0 Master Doc §10 mandates exactly these 6 types."""
    expected = (
        "Integrated Preliminary Report",
        "Decision-Grade Report",
        "Hardened Decision Report",
        "Validation-Oriented Report",
        "Verification-Supported Report",
        "Verified Report",
    )
    assert CANONICAL_REPORT_MATURITY_TYPES == expected


def test_support_state_ladder_has_9_states():
    """Phase 0 §5.2 mandates these 9 states in this order."""
    assert SUPPORT_STATE_LADDER == (
        "unsupported", "hypothesis", "indication", "screening_grade",
        "decision_grade", "partially_hardened", "verification_ready",
        "verification_supported", "verified",
    )


# ── Single-state mapping ────────────────────────────────────────────


def test_unsupported_maps_to_preliminary():
    assert maturity_type_for_support_state("unsupported") == "Integrated Preliminary Report"


def test_hypothesis_maps_to_preliminary():
    assert maturity_type_for_support_state("hypothesis") == "Integrated Preliminary Report"


def test_indication_maps_to_preliminary():
    assert maturity_type_for_support_state("indication") == "Integrated Preliminary Report"


def test_screening_grade_maps_to_decision_grade():
    assert maturity_type_for_support_state("screening_grade") == "Decision-Grade Report"


def test_decision_grade_maps_to_decision_grade():
    assert maturity_type_for_support_state("decision_grade") == "Decision-Grade Report"


def test_partially_hardened_maps_to_hardened():
    assert maturity_type_for_support_state("partially_hardened") == "Hardened Decision Report"


def test_verification_ready_maps_to_validation_oriented():
    assert maturity_type_for_support_state("verification_ready") == "Validation-Oriented Report"


def test_verification_supported_maps_to_verification_supported():
    assert maturity_type_for_support_state("verification_supported") == "Verification-Supported Report"


def test_verified_maps_to_verified():
    assert maturity_type_for_support_state("verified") == "Verified Report"


def test_unknown_state_defaults_to_preliminary():
    assert maturity_type_for_support_state("") == "Integrated Preliminary Report"
    assert maturity_type_for_support_state("nonexistent") == "Integrated Preliminary Report"


def test_state_normalization_case_insensitive():
    assert maturity_type_for_support_state("VERIFIED") == "Verified Report"
    assert maturity_type_for_support_state("  decision_grade  ") == "Decision-Grade Report"


# ── Aggregation ─────────────────────────────────────────────────────


def test_aggregate_uses_highest_state():
    """When mixed states present, the report's maturity is the strongest."""
    states = ["hypothesis", "decision_grade", "screening_grade"]
    assert aggregate_maturity_type(states) == "Decision-Grade Report"


def test_aggregate_returns_strongest_among_strong():
    states = ["partially_hardened", "verification_ready", "decision_grade"]
    # Highest is verification_ready → Validation-Oriented
    assert aggregate_maturity_type(states) == "Validation-Oriented Report"


def test_aggregate_empty_returns_preliminary():
    assert aggregate_maturity_type([]) == "Integrated Preliminary Report"
    assert aggregate_maturity_type(()) == "Integrated Preliminary Report"


def test_aggregate_only_unknown_states_returns_preliminary():
    assert aggregate_maturity_type(["nonsense", "garbage"]) == "Integrated Preliminary Report"


def test_aggregate_verified_pinnacle():
    """Even one verified claim unlocks 'Verified Report' aggregate."""
    states = ["unsupported", "hypothesis", "verified"]
    assert aggregate_maturity_type(states) == "Verified Report"


# ── Ordering / comparison ───────────────────────────────────────────


def test_maturity_type_index_ordered():
    assert maturity_type_index("Integrated Preliminary Report") == 0
    assert maturity_type_index("Decision-Grade Report") == 1
    assert maturity_type_index("Verified Report") == 5


def test_maturity_type_index_unknown():
    assert maturity_type_index("Some Other Brief") == -1


def test_is_stronger_maturity():
    assert is_stronger_maturity("Verified Report", "Hardened Decision Report")
    assert is_stronger_maturity("Decision-Grade Report", "Integrated Preliminary Report")
    assert not is_stronger_maturity("Integrated Preliminary Report", "Decision-Grade Report")
    assert not is_stronger_maturity("Decision-Grade Report", "Decision-Grade Report")


# ── motor_025 integration ───────────────────────────────────────────


def test_derive_from_motor_025_real_shape():
    motor_025_output = {
        "status_register": [
            {"output_id": "x", "claim_support_state": "decision_grade"},
            {"output_id": "y", "claim_support_state": "hypothesis"},
            {"output_id": "z", "claim_support_state": "partially_hardened"},
        ],
    }
    result = derive_report_maturity_from_motor_025(motor_025_output)
    assert result["report_maturity_type"] == "Hardened Decision Report"
    assert result["max_claim_support_state"] == "partially_hardened"
    assert "support_states_observed" in result


def test_derive_from_motor_025_empty():
    result = derive_report_maturity_from_motor_025({})
    assert result["report_maturity_type"] == "Integrated Preliminary Report"


def test_derive_from_motor_025_none():
    result = derive_report_maturity_from_motor_025(None)
    assert result["report_maturity_type"] == "Integrated Preliminary Report"
    assert "unavailable" in result["rationale"]


def test_derive_from_motor_025_verified_present():
    motor_025_output = {
        "status_register": [
            {"output_id": "v1", "claim_support_state": "verified"},
            {"output_id": "v2", "claim_support_state": "hypothesis"},
        ],
    }
    result = derive_report_maturity_from_motor_025(motor_025_output)
    assert result["report_maturity_type"] == "Verified Report"
    assert result["max_claim_support_state"] == "verified"
