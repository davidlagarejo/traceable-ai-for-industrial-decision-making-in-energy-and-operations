"""V7 P5 — motor_059 R12 (local_truth_from_archetypal_prior) +
R13 (benchmark_as_truth) governance guardrails."""
from __future__ import annotations

import pytest

from runtime_orchestrator.adapters.motor_059 import Motor059Adapter
from runtime_orchestrator.validator_severity_policy import (
    is_v6_blocking_rule,
)


@pytest.fixture(autouse=True)
def _force_soft_mode(monkeypatch):
    """Use soft mode so we can assert the default 'warning' severity.
    Hard-mode promotion to 'blocking' is covered separately."""
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "0")


def _run(**overrides):
    base = {
        "motor_016": {}, "motor_018": {}, "motor_033": {},
        "motor_038": {}, "motor_045": {}, "motor_051": {}, "motor_054": {},
    }
    base.update(overrides)
    return Motor059Adapter().run(base)


# ── R12 local truth from archetypal prior ──────────────────────────


def test_R12_local_truth_with_archetypal_evidence_blocks():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "c1",
                    "claim_text": "This facility consumes 35 kWh/sf — well above peers.",
                    "evidence_state": "ARCHETYPAL_PRIOR",
                },
            ],
        },
    )
    r12 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R12_local_truth_from_archetypal_prior"]
    assert len(r12) == 1
    assert r12[0]["claim_id"] == "c1"
    assert r12[0]["evidence_state"] == "ARCHETYPAL_PRIOR"


def test_R12_local_truth_with_observed_fact_does_not_block():
    """Same local-truth language is allowed when backed by OBSERVED_FACT."""
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "c1",
                    "claim_text": "This facility consumes 35 kWh/sf based on 12 months of metered data.",
                    "evidence_state": "OBSERVED_FACT",
                },
            ],
        },
    )
    r12 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R12_local_truth_from_archetypal_prior"]
    assert r12 == []


def test_R12_local_truth_on_TAD_action():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {
                    "action_id": "a1",
                    "action_title": "This site is 30% inefficient versus peers.",
                    "evidence_state": "WEAK_SIGNAL",
                },
            ],
        },
    )
    r12 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R12_local_truth_from_archetypal_prior"]
    assert len(r12) == 1
    assert r12[0]["action_id"] == "a1"


def test_R12_silent_when_no_local_truth_language():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1", "claim_text": "Refrigeration duty unresolved.",
                 "evidence_state": "ARCHETYPAL_PRIOR"},
            ],
        },
    )
    r12 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R12_local_truth_from_archetypal_prior"]
    assert r12 == []


# ── R13 benchmark as truth ─────────────────────────────────────────


def test_R13_benchmark_as_truth_blocks():
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {
                    "claim_id": "c2",
                    "claim_text": "This site performs below industry benchmark — savings opportunity confirmed.",
                },
            ],
        },
    )
    r13 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R13_benchmark_as_truth"]
    assert len(r13) == 1
    assert r13[0]["claim_id"] == "c2"


def test_R13_silent_on_neutral_benchmark_reference():
    """Mentioning the existence of a benchmark is fine; using it as
    a truth oracle is not."""
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c2",
                 "claim_text": "ENERGY STAR benchmark is the reference distribution for office buildings."},
            ],
        },
    )
    r13 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R13_benchmark_as_truth"]
    assert r13 == []


def test_R13_TAD_action_detection():
    out = _run(
        motor_033={
            "expanded_structural_tad_action_register": [
                {"action_id": "a2",
                 "action_title": "Implement retrofit — facility is below median benchmark."},
            ],
        },
    )
    r13 = [w for w in out["strategic_intelligence_warnings"]
           if w["rule_id"] == "R13_benchmark_as_truth"]
    assert len(r13) == 1
    assert r13[0]["action_id"] == "a2"


# ── R12 + R13 in V6 blocking set (hard mode would promote them) ────


def test_R12_in_v6_blocking_rules():
    assert is_v6_blocking_rule("motor_059", "R12_local_truth_from_archetypal_prior")


def test_R13_in_v6_blocking_rules():
    assert is_v6_blocking_rule("motor_059", "R13_benchmark_as_truth")


def test_R12_R13_promote_to_blocking_in_hard_mode(monkeypatch):
    """Override the autouse soft-mode fixture for THIS test only."""
    monkeypatch.setenv("ZLAB_VALIDATORS_HARD_BLOCK", "1")
    out = _run(
        motor_054={
            "congruence_claim_contract_register": [
                {"claim_id": "c1",
                 "claim_text": "This facility consumes 40 kWh/sf — below industry benchmark.",
                 "evidence_state": "ARCHETYPAL_PRIOR"},
            ],
        },
    )
    warns = out["strategic_intelligence_warnings"]
    r12 = next((w for w in warns if w["rule_id"] == "R12_local_truth_from_archetypal_prior"), None)
    r13 = next((w for w in warns if w["rule_id"] == "R13_benchmark_as_truth"), None)
    assert r12 and r12["severity"] == "blocking"
    assert r13 and r13["severity"] == "blocking"
