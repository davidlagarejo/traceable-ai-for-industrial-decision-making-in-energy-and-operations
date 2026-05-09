"""Tests for the R-50 wiring in motor_046: evidence_pack_per_hypothesis_id."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_046 import (
    Motor046Adapter,
    _build_evidence_pack_per_hypothesis_id,
    _slugify_hypothesis,
)


def test_slugify_basic():
    assert _slugify_hypothesis("Owner-controllable base.", 0) == "owner_controllable_base"


def test_slugify_empty_uses_fallback():
    assert _slugify_hypothesis("", 7) == "hypothesis_007"


def test_slugify_strips_punctuation():
    assert _slugify_hypothesis("A — B / C!?", 0) == "a_b_c"


def test_build_indexes_each_rival_hypothesis():
    register = [
        {
            "rival_hypotheses": ["H1 dominates.", "H2 dominates."],
            "minimum_evidence": "evidence A",
            "source": "src",
            "what_it_confirms": "C",
            "what_it_falsifies": "F",
            "unlocks": ["u1"],
        }
    ]
    out = _build_evidence_pack_per_hypothesis_id(register)
    assert "h1_dominates" in out
    assert "h2_dominates" in out
    assert out["h1_dominates"]["minimum_evidence"] == "evidence A"
    assert out["h1_dominates"]["unlocks"] == ["u1"]


def test_each_hypothesis_carries_rival_text():
    register = [
        {
            "rival_hypotheses": ["Specific text about denominator."],
            "minimum_evidence": "ev",
        }
    ]
    out = _build_evidence_pack_per_hypothesis_id(register)
    only = next(iter(out.values()))
    assert only["rival_hypothesis"] == "Specific text about denominator."


def test_duplicate_slugs_keep_first():
    register = [
        {"rival_hypotheses": ["Same one"], "minimum_evidence": "first"},
        {"rival_hypotheses": ["Same one"], "minimum_evidence": "second"},
    ]
    out = _build_evidence_pack_per_hypothesis_id(register)
    assert len(out) == 1
    assert out["same_one"]["minimum_evidence"] == "first"


def test_motor_046_emits_new_dict():
    """End-to-end: running motor_046 with a known target produces both
    the legacy register AND the new dict."""
    adapter = Motor046Adapter()
    out = adapter.run(
        {
            "motor_007": {"target_definition_contract": {"target_type": "manufacturing_facility"}},
            "motor_038": {"dominant_variable_register": []},
            "motor_040": {"cross_layer_conflict_register": []},
            "motor_041": {"problem_framing_register": []},
            "motor_044": {"conditional_redesign_register": []},
        }
    )
    assert "minimum_evidence_for_discrimination_register" in out
    assert "evidence_pack_per_hypothesis_id" in out
    assert isinstance(out["evidence_pack_per_hypothesis_id"], dict)
    # Manufacturing has at least 1 row with rival hypotheses
    assert out["hypothesis_indexed_count"] >= 1
    # Each indexed entry carries a rival_hypothesis and minimum_evidence
    sample = next(iter(out["evidence_pack_per_hypothesis_id"].values()))
    assert "rival_hypothesis" in sample
    assert "minimum_evidence" in sample


def test_legacy_register_unchanged_in_shape():
    """R-50 must not modify the legacy register; only add a new field."""
    adapter = Motor046Adapter()
    out = adapter.run(
        {
            "motor_007": {"target_definition_contract": {"target_type": "manufacturing_facility"}},
            "motor_038": {"dominant_variable_register": []},
            "motor_040": {"cross_layer_conflict_register": []},
            "motor_041": {"problem_framing_register": []},
            "motor_044": {"conditional_redesign_register": []},
        }
    )
    register = out["minimum_evidence_for_discrimination_register"]
    assert isinstance(register, list)
    assert all(isinstance(row, dict) for row in register)
    # Sanity: legacy fields still present
    assert "rival_hypotheses" in register[0]
    assert "minimum_evidence" in register[0]
