"""Tests for V3 G15: motor_058 measures 5 reuse dimensions.

In addition to RU1 (jaccard overlap) and RU2 (verbatim nugget reuse), V3
adds:
  RU3 — TAD action set reuse
  RU4 — chart asset set reuse
  RU5 — evidence pack set reuse

This test suite injects synthetic comparisons directly into the _evaluate
helper to verify each rule fires above its threshold (>90% set overlap).
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_058 import (
    _HIGH_SET_OVERLAP_THRESHOLD,
    _collect_chart_ids,
    _collect_evidence_pack,
    _collect_tad_action_ids,
    _evaluate,
    _set_overlap_ratio,
)


def _comparison(**overrides):
    base = {
        "envelope": "envelope_abc.json",
        "similarity": 0.0,
        "verbatim_overlap_count": 0,
        "verbatim_overlap_sample": [],
        "tad_overlap_ratio": 0.0,
        "chart_overlap_ratio": 0.0,
        "evidence_overlap_ratio": 0.0,
    }
    base.update(overrides)
    return base


# ── helpers ─────────────────────────────────────────────────────────────


def test_set_overlap_ratio_returns_zero_for_empty_prior():
    assert _set_overlap_ratio({"a"}, set()) == 0.0


def test_set_overlap_ratio_full_overlap():
    assert _set_overlap_ratio({"a", "b"}, {"a", "b"}) == 1.0


def test_collect_tad_action_ids_normalizes_lowercase():
    out = _collect_tad_action_ids([
        {"action": "VALIDATE_LOSS_PATTERN"},
        {"action": "Validate_Loss_Pattern"},
        {"action": "BUILD_FAIR_PEER_SET"},
    ])
    # Both first entries dedupe via lower()
    assert out == {"validate_loss_pattern", "build_fair_peer_set"}


def test_collect_chart_ids_uses_chart_id_or_title():
    out = _collect_chart_ids([
        {"chart_id": "CHT-001"},
        {"asset_id": "CHT-002"},
        {"title": "Energy Composition"},
        {"chart_id": ""},  # empty skipped
    ])
    assert out == {"cht-001", "cht-002", "energy composition"}


def test_collect_evidence_pack_unions_minimum_evidence_strings():
    out = _collect_evidence_pack([
        {"minimum_evidence": ["leak survey", "compressor staging"]},
        {"minimum_evidence_to_activate": ["leak survey", "throughput profile"]},
    ])
    assert out == {"leak survey", "compressor staging", "throughput profile"}


# ── RU3: TAD action set reuse ───────────────────────────────────────────


def test_ru3_fires_when_tad_overlap_above_threshold():
    warnings = _evaluate([_comparison(tad_overlap_ratio=0.95)])
    rule_ids = [w["rule_id"] for w in warnings]
    assert "RU3_tad_action_set_reuse" in rule_ids
    ru3 = next(w for w in warnings if w["rule_id"] == "RU3_tad_action_set_reuse")
    assert ru3["tad_overlap_ratio"] == 0.95


def test_ru3_silent_below_threshold():
    warnings = _evaluate([_comparison(tad_overlap_ratio=0.50)])
    rule_ids = [w["rule_id"] for w in warnings]
    assert "RU3_tad_action_set_reuse" not in rule_ids


# ── RU4: Chart set reuse ────────────────────────────────────────────────


def test_ru4_fires_when_chart_overlap_above_threshold():
    warnings = _evaluate([_comparison(chart_overlap_ratio=0.95)])
    rule_ids = [w["rule_id"] for w in warnings]
    assert "RU4_chart_set_reuse" in rule_ids


def test_ru4_silent_below_threshold():
    warnings = _evaluate([_comparison(chart_overlap_ratio=0.80)])
    rule_ids = [w["rule_id"] for w in warnings]
    assert "RU4_chart_set_reuse" not in rule_ids


# ── RU5: Evidence pack set reuse ────────────────────────────────────────


def test_ru5_fires_when_evidence_overlap_above_threshold():
    warnings = _evaluate([_comparison(evidence_overlap_ratio=0.95)])
    rule_ids = [w["rule_id"] for w in warnings]
    assert "RU5_evidence_pack_set_reuse" in rule_ids


def test_ru5_silent_below_threshold():
    warnings = _evaluate([_comparison(evidence_overlap_ratio=0.85)])
    rule_ids = [w["rule_id"] for w in warnings]
    assert "RU5_evidence_pack_set_reuse" not in rule_ids


# ── All 3 new rules can fire in one comparison ──────────────────────────


def test_all_three_new_rules_fire_when_all_thresholds_exceeded():
    warnings = _evaluate([
        _comparison(
            tad_overlap_ratio=0.95,
            chart_overlap_ratio=0.95,
            evidence_overlap_ratio=0.95,
        )
    ])
    rule_ids = {w["rule_id"] for w in warnings}
    assert {"RU3_tad_action_set_reuse", "RU4_chart_set_reuse", "RU5_evidence_pack_set_reuse"}.issubset(rule_ids)


# ── Threshold sanity ────────────────────────────────────────────────────


def test_high_set_overlap_threshold_is_90_percent():
    """Locks the threshold so accidental tuning gets caught in review."""
    assert _HIGH_SET_OVERLAP_THRESHOLD == 0.90
