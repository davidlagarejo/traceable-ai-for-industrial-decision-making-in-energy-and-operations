"""Tests for R-58 + R-59: archetypal-peer admissibility (motor_051) and
peer-comparison allowed_verbs enrichment (motor_043).
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_043 import (
    Motor043Adapter,
    _allowed_verbs_for_state,
)


# ── R-59: allowed_verbs by evidence_state ──────────────────────────────────


def test_allowed_verbs_observed_fact():
    assert _allowed_verbs_for_state("OBSERVED_FACT") == ["is", "shows"]


def test_allowed_verbs_conditional_hypothesis():
    assert _allowed_verbs_for_state("CONDITIONAL_HYPOTHESIS") == ["may", "is consistent with"]


def test_allowed_verbs_archetypal_prior():
    assert _allowed_verbs_for_state("ARCHETYPAL_PRIOR") == [
        "structurally suggests",
        "archetypally implies",
    ]


def test_allowed_verbs_weak_signal():
    assert _allowed_verbs_for_state("WEAK_SIGNAL") == [
        "might",
        "is loosely consistent with",
    ]


def test_allowed_verbs_unknown_state_falls_back_to_may():
    assert _allowed_verbs_for_state("UNKNOWN") == ["may"]
    assert _allowed_verbs_for_state("") == ["may"]


def test_motor_043_attaches_allowed_verbs_to_each_row():
    adapter = Motor043Adapter()
    out = adapter.run({})
    # If register is empty (no benchmarks), the adapter still emits a list.
    register = out["competitive_comparison_register"]
    assert isinstance(register, list)
    for row in register:
        # Each row must carry allowed_verbs
        assert "allowed_verbs" in row
        assert isinstance(row["allowed_verbs"], list)
        assert len(row["allowed_verbs"]) >= 1


# ── R-58: archetypal-peer admissibility flows from motor_051 to motor_043 ──


def test_motor_043_surfaces_archetypal_peer_fallback_register():
    adapter = Motor043Adapter()
    fallback = [
        {
            "comparison_basis": "warehouse_area_normalized",
            "archetypal_admissibility": "allowed_under_archetypal_prior",
            "evidence_state": "ARCHETYPAL_PRIOR",
            "allowed_use": ["Bounded peer warning"],
            "prohibited_use": ["Peer superiority claim"],
        }
    ]
    out = adapter.run(
        {"motor_051": {"archetypal_peer_admissibility_register": fallback}}
    )
    assert out["archetypal_peer_fallback_available"] is True
    assert len(out["archetypal_peer_fallback_register"]) == 1
    assert (
        out["archetypal_peer_fallback_register"][0]["evidence_state"]
        == "ARCHETYPAL_PRIOR"
    )


def test_motor_043_no_motor_051_yields_empty_fallback():
    adapter = Motor043Adapter()
    out = adapter.run({})
    assert out["archetypal_peer_fallback_available"] is False
    assert out["archetypal_peer_fallback_register"] == []
