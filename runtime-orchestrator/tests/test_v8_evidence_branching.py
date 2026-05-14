"""V8 P5 — Evidence Branching Engine tests.

V8 § Error 5 + § E: per-hypothesis evidence matrix output.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.evidence_branching import (
    EvidenceBranch,
    audit_branch_repetition,
    build_evidence_branch_from_spec,
    build_evidence_branches,
    summarize_branches,
)


# ── build_evidence_branch_from_spec ────────────────────────────────


def test_branch_built_from_full_spec():
    spec = {
        "id": "refrigeration_duty",
        "evidence_required": [
            "compressor inventory", "setpoint log", "operating schedule",
            "refrigerant type", "kWh per ton-hour",
        ],
        "minimum_evidence_to_activate": ["cold-chain confirmed"],
        "minimum_evidence_to_confirm": ["compressor staging + temperature profile"],
        "falsification_conditions": ["refrigeration duty already bounded"],
        "anti_triggers": ["no refrigerated load"],
        "tad_actions": ["DECOMPOSE_REFRIGERATION_DUTY", "DO_NOT_INVEST_YET"],
    }
    branch = build_evidence_branch_from_spec(spec)
    assert branch is not None
    assert branch.hypothesis_id == "refrigeration_duty"
    assert len(branch.minimum_evidence) == 6
    # Cheapest = first 3
    assert branch.cheapest_path == (
        "compressor inventory", "setpoint log", "operating schedule",
    )
    # Escalation = rest
    assert "refrigerant type" in branch.escalation_path
    assert "compressor staging + temperature profile" in branch.confirms_when
    assert "refrigeration duty already bounded" in branch.falsifies_when
    assert "no refrigerated load" in branch.falsifies_when
    assert "DECOMPOSE_REFRIGERATION_DUTY" in branch.tad_impact


def test_branch_none_when_spec_has_no_evidence():
    spec = {"id": "empty_hypothesis"}
    assert build_evidence_branch_from_spec(spec) is None


def test_branch_none_when_spec_lacks_id():
    spec = {"evidence_required": ["a", "b"]}
    assert build_evidence_branch_from_spec(spec) is None


def test_branch_dedupes_evidence():
    spec = {
        "id": "test",
        "evidence_required": ["a", "b", "a"],
        "minimum_evidence_to_activate": ["b", "c"],
    }
    branch = build_evidence_branch_from_spec(spec)
    assert branch.minimum_evidence == ("a", "b", "c")


# ── build_evidence_branches batch ──────────────────────────────────


def test_batch_builder_skips_malformed_specs():
    specs = [
        {"id": "valid", "evidence_required": ["x"]},
        None,
        {"id": "no_evidence"},  # skipped
        {"id": "another_valid", "evidence_required": ["y"]},
    ]
    branches = build_evidence_branches(specs)
    assert len(branches) == 2
    assert {b.hypothesis_id for b in branches} == {"valid", "another_valid"}


# ── audit_branch_repetition ────────────────────────────────────────


def test_audit_flags_identical_branches():
    b1 = EvidenceBranch(
        hypothesis_id="h1",
        minimum_evidence=("a", "b", "c"),
        cheapest_path=("a", "b", "c"), escalation_path=(),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    b2 = EvidenceBranch(
        hypothesis_id="h2",
        minimum_evidence=("a", "b", "c"),
        cheapest_path=("a", "b", "c"), escalation_path=(),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    out = audit_branch_repetition([b1, b2])
    assert len(out) == 1
    assert out[0]["jaccard"] == 1.0
    assert out[0]["rule_id"] == "EB1_branch_evidence_repetition"


def test_audit_silent_when_branches_distinct():
    b1 = EvidenceBranch(
        hypothesis_id="h1",
        minimum_evidence=("a", "b"),
        cheapest_path=("a", "b"), escalation_path=(),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    b2 = EvidenceBranch(
        hypothesis_id="h2",
        minimum_evidence=("c", "d"),
        cheapest_path=("c", "d"), escalation_path=(),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    assert audit_branch_repetition([b1, b2]) == []


def test_audit_three_branches_emits_three_pairs():
    b = lambda h: EvidenceBranch(
        hypothesis_id=h,
        minimum_evidence=("x", "y", "z"),
        cheapest_path=(), escalation_path=(),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    out = audit_branch_repetition([b("h1"), b("h2"), b("h3")])
    assert len(out) == 3  # C(3,2)


# ── summarize_branches ─────────────────────────────────────────────


def test_summary_counts_correctly():
    b1 = EvidenceBranch(
        hypothesis_id="h1",
        minimum_evidence=("a", "b"),
        cheapest_path=("a", "b"), escalation_path=(),
        confirms_when=(), falsifies_when=("falsifier1",),
        tad_impact=("INSPECT",),
    )
    b2 = EvidenceBranch(
        hypothesis_id="h2",
        minimum_evidence=("c",),
        cheapest_path=("c",), escalation_path=(),
        confirms_when=(), falsifies_when=(), tad_impact=(),
    )
    s = summarize_branches([b1, b2])
    assert s["branch_count"] == 2
    assert s["total_min_evidence_items"] == 3
    assert s["branches_with_falsifiers"] == 1
    assert s["branches_without_tad_impact"] == 1


# ── Real pattern_specs from registry produce non-empty matrix ─────


def test_real_pattern_specs_build_branches():
    from runtime_orchestrator.zlab_skill.loader import load_pattern_specs
    specs = load_pattern_specs()
    branches = build_evidence_branches(specs)
    # Most of the 30 patterns carry evidence_required; expect ≥ 20 branches.
    assert len(branches) >= 20
    # Each has a non-empty minimum_evidence.
    assert all(b.minimum_evidence for b in branches)
    # refrigeration_duty must be in there (canonical cold-chain pattern).
    assert any(b.hypothesis_id == "refrigeration_duty" for b in branches)
