"""V9 P1 — Fair Comparison Engine 10-dimensional tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.fair_comparison import (
    CANONICAL_PEER_DIMENSIONS,
    PeerComparabilityContract,
    build_peer_contract,
    evaluate_peer_set,
    peer_set_admissible,
    summarize_for_motor_output,
)
from runtime_orchestrator.validator_severity_policy import is_v6_blocking_rule


# Helper to build a complete 10-dim profile
def _full_profile(id_: str = "x", **overrides) -> dict:
    base = {
        "id": id_,
        "asset_family": "cold_chain_facility",
        "process_family": "refrigeration",
        "thermal_regime": "refrigerated",
        "throughput_band": "medium",
        "operating_hours": "24x7",
        "dock_density": "high",
        "charging_profile": "overnight",
        "tariff_profile": "demand_billed",
        "control_boundary": "owner_operator",
        "regulatory_context": "iiar",
    }
    base.update(overrides)
    return base


# ── 10 canonical dimensions defined ──────────────────────────────


def test_ten_canonical_dimensions():
    assert len(CANONICAL_PEER_DIMENSIONS) == 10
    assert "asset_family" in CANONICAL_PEER_DIMENSIONS
    assert "process_family" in CANONICAL_PEER_DIMENSIONS
    assert "thermal_regime" in CANONICAL_PEER_DIMENSIONS
    assert "throughput_band" in CANONICAL_PEER_DIMENSIONS
    assert "operating_hours" in CANONICAL_PEER_DIMENSIONS
    assert "dock_density" in CANONICAL_PEER_DIMENSIONS
    assert "charging_profile" in CANONICAL_PEER_DIMENSIONS
    assert "tariff_profile" in CANONICAL_PEER_DIMENSIONS
    assert "control_boundary" in CANONICAL_PEER_DIMENSIONS
    assert "regulatory_context" in CANONICAL_PEER_DIMENSIONS


# ── build_peer_contract ─────────────────────────────────────────


def test_identical_profiles_score_1():
    c = build_peer_contract(_full_profile("a"), _full_profile("b"))
    assert c.comparability_score == 1.0
    assert c.all_dimensions_declared is True
    assert c.admissible is True
    assert len(c.matched_dimensions) == 10
    assert len(c.mismatched_dimensions) == 0
    assert len(c.missing_dimensions) == 0


def test_one_mismatch_drops_score():
    c = build_peer_contract(
        _full_profile("a", thermal_regime="frozen"),
        _full_profile("b", thermal_regime="refrigerated"),
    )
    assert c.comparability_score == 0.9
    assert "thermal_regime" in c.mismatched_dimensions
    assert c.all_dimensions_declared is True
    assert c.admissible is True  # 0.9 ≥ 0.70


def test_below_threshold_inadmissible():
    """5 mismatches → score=0.5 < 0.70 → not admissible."""
    peer = _full_profile(
        "b",
        thermal_regime="frozen",
        throughput_band="large",
        operating_hours="8x5",
        dock_density="low",
        charging_profile="opportunity",
    )
    c = build_peer_contract(_full_profile("a"), peer)
    assert c.comparability_score == 0.5
    assert c.admissible is False


def test_missing_dimension_blocks_admissibility():
    """Even if all OTHER dims match, missing one → not admissible."""
    peer = _full_profile("b")
    del peer["regulatory_context"]
    c = build_peer_contract(_full_profile("a"), peer)
    assert "regulatory_context" in c.missing_dimensions
    assert c.all_dimensions_declared is False
    assert c.admissible is False


# ── evaluate_peer_set ────────────────────────────────────────────


def test_mixed_peer_set_categorizes_correctly():
    candidate = _full_profile("candidate")
    peers = [
        _full_profile("good_peer"),
        _full_profile("bad_peer", thermal_regime="frozen",
                       throughput_band="large", operating_hours="8x5",
                       dock_density="low", charging_profile="opportunity"),
    ]
    verdict = evaluate_peer_set(candidate, peers)
    assert "good_peer" in verdict.admissible_peers
    assert "bad_peer" in verdict.rejected_peers
    assert verdict.peer_set_admissible is True


def test_empty_peer_set_inadmissible():
    verdict = evaluate_peer_set(_full_profile("c"), [])
    assert verdict.peer_set_admissible is False
    assert verdict.admissible_peers == ()


def test_all_peers_incomplete_inadmissible():
    candidate = _full_profile("c")
    incomplete_peer = _full_profile("p")
    del incomplete_peer["regulatory_context"]
    verdict = evaluate_peer_set(candidate, [incomplete_peer])
    assert verdict.peer_set_admissible is False
    assert peer_set_admissible(verdict) is False


# ── summarize_for_motor_output ──────────────────────────────────


def test_summary_carries_admissibility_flags():
    candidate = _full_profile("c")
    peers = [_full_profile("p1"), _full_profile("p2", thermal_regime="frozen")]
    verdict = evaluate_peer_set(candidate, peers)
    s = summarize_for_motor_output(verdict)
    assert s["peer_set_admissible"] is True
    assert s["admissible_peer_count"] == 2
    assert s["rejected_peer_count"] == 0
    assert s["threshold"] == 0.70


# ── R14 in V6 blocking set + detector ────────────────────────────


def test_R14_in_v6_blocking_rules():
    assert is_v6_blocking_rule(
        "motor_059", "R14_peer_ranking_with_incomplete_comparability"
    )


def test_R14_fires_when_peer_set_inadmissible(monkeypatch):
    from runtime_orchestrator.adapters.motor_059 import Motor059Adapter
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")
    out = Motor059Adapter().run({
        "motor_016": {}, "motor_018": {},
        "motor_033": {"expanded_structural_tad_action_register": [
            {"action_id": "A1", "action_title": "Rank against peer set on EUI"},
        ]},
        "motor_038": {}, "motor_045": {},
        "motor_051": {"fair_comparison_summary": {
            "peer_set_admissible": False,
            "admissible_peer_count": 0,
            "incomplete_peer_count": 3,
        }},
        "motor_054": {},
    })
    r14 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R14_peer_ranking_with_incomplete_comparability"]
    assert len(r14) == 1


def test_R14_silent_when_peer_set_admissible(monkeypatch):
    from runtime_orchestrator.adapters.motor_059 import Motor059Adapter
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")
    out = Motor059Adapter().run({
        "motor_016": {}, "motor_018": {},
        "motor_033": {"expanded_structural_tad_action_register": [
            {"action_id": "A1", "action_title": "Rank against peer set"},
        ]},
        "motor_038": {}, "motor_045": {},
        "motor_051": {"fair_comparison_summary": {
            "peer_set_admissible": True,
            "admissible_peer_count": 3,
        }},
        "motor_054": {},
    })
    r14 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R14_peer_ranking_with_incomplete_comparability"]
    assert r14 == []
