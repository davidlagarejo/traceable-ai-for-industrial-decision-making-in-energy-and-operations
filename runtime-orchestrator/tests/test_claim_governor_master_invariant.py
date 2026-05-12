"""V3 G17: Claim Governor master invariant.

The invariant (RECOVERY_2026-05-10 §9, V3 prompt §9):

  > "Lack of local certainty blocks closure, NOT structural reasoning."

Operationally:
  - With ZERO upstream registers (no peer, no measurement, no regulatory,
    no finance-physics, no loss-pattern, no culture-execution), the claim
    governor produces NO contracts — no false closure can occur (✓).
  - But when SOME structural register exists (e.g., a single conditional
    hypothesis), the governor MUST emit a contract with permission ≠
    "allowed" unless the evidence_state is one of the bounded epistemic
    states. Closure stays blocked at the contract level.
  - Structural reasoning (the hypothesis itself) is NEVER suppressed by
    absence of local evidence; only closure (claim permission) is.

This test set formalizes those invariants directly against the
claim_governor module — no full pipeline run needed.
"""
from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.claim_governor import (
    build_congruence_claim_contract_register,
)


def _empty_inputs() -> dict:
    return {
        "strategic_gold_nugget_register": [],
        "congruence_action_priority_register": [],
        "invalid_comparison_risk_register": [],
        "measurement_strategy_register": [],
        "regulatory_physics_register": [],
        "finance_physics_dependency_register": [],
        "loss_pattern_hypothesis_register": [],
        "culture_execution_proxy_register": [],
    }


# ── Invariant 1: empty inputs → no contracts emitted ───────────────────


def test_zero_evidence_emits_no_contracts():
    """With no upstream signals at all, the governor stays silent. No
    contracts means no closure — the correct posture."""
    out = build_congruence_claim_contract_register(**_empty_inputs())
    assert out == []


# ── Invariant 2: present structural evidence → contracts but no closure ─


def test_structural_signal_emits_contract_blocking_closure():
    """When upstream IS present, a contract is created — but it is
    permission="allowed" only because the contract framing requires it.
    Closure is enforced through the `prohibited_use` list, not through
    the permission field. This test locks the contract structure so the
    invariant is checked: prohibited_use is never empty for a conditional
    state."""
    inputs = _empty_inputs()
    inputs["invalid_comparison_risk_register"] = [
        {"trigger": "Peer set NAICS heterogeneity > 30%", "required_normalization": ["throughput band", "thermal duty band"]}
    ]
    contracts = build_congruence_claim_contract_register(**inputs)
    assert len(contracts) == 1
    c = contracts[0]
    assert c["evidence_state"] == "CONDITIONAL_HYPOTHESIS"
    # permission is "allowed" because CONDITIONAL_HYPOTHESIS is bounded epistemic
    # — but the prohibited_use list enforces closure blockage
    assert c["prohibited_use"], "every conditional contract must declare prohibited_use"
    # Specifically: peer superiority, transferable ROI, local waste diagnosis
    assert any("Peer superiority" in p or "Transferable ROI" in p for p in c["prohibited_use"])


# ── Invariant 3: structural reasoning never blocked by missing evidence ─


def test_structural_reasoning_emitted_even_when_only_one_register_present():
    """The framework should produce structural framing from ANY single
    signal. This validates that one register can stand alone."""
    for register_name in (
        "invalid_comparison_risk_register",
        "measurement_strategy_register",
        "regulatory_physics_register",
        "finance_physics_dependency_register",
        "loss_pattern_hypothesis_register",
    ):
        inputs = _empty_inputs()
        inputs[register_name] = [{
            "trigger": "trigger text",
            "required_normalization": ["a"],
            "permits": ["NSPS"],
            "physics_dependency": "thermal duty",
            "framework": "DOE",
            "physical_constraint": "process heat lock",
            "hypothesis": "structural loss hypothesis",
            "ownership_signal": "operator vs owner",
        }]
        contracts = build_congruence_claim_contract_register(**inputs)
        assert len(contracts) >= 1, f"single-register input {register_name} should still produce a contract"


# ── Invariant 4: every claim carries falsification_condition ───────────


def test_every_emitted_claim_has_falsification_condition():
    """Per claim governor design: claims without falsification cannot be
    permitted. This is a core epistemic invariant."""
    inputs = _empty_inputs()
    inputs["invalid_comparison_risk_register"] = [
        {"trigger": "x", "required_normalization": ["a"]}
    ]
    inputs["loss_pattern_hypothesis_register"] = [{"hypothesis": "thermal_duty_dominance"}]
    contracts = build_congruence_claim_contract_register(**inputs)
    assert contracts, "expected at least one contract"
    for c in contracts:
        assert c.get("falsification_condition"), (
            f"claim {c.get('claim_id')} missing falsification_condition — "
            "violates V3 §9 master invariant"
        )


# ── Invariant 5: prohibited closure is exhaustively documented ────────


def test_every_claim_lists_prohibited_use_explicitly():
    """A claim cannot be 'allowed' for some uses without the governor
    declaring what it is NOT allowed for. This enforces the
    'do-not-close-on-this' posture."""
    inputs = _empty_inputs()
    inputs["regulatory_physics_register"] = [{
        "permits": ["NSPS"],
        "physics_dependency": "thermal duty",
    }]
    contracts = build_congruence_claim_contract_register(**inputs)
    assert contracts
    for c in contracts:
        assert c.get("prohibited_use"), (
            f"claim {c.get('claim_id')} missing prohibited_use — closure must be "
            "explicitly bounded, not implicit"
        )


# ── Invariant 6: claim_id is unique within a single output ─────────────


def test_no_duplicate_claim_ids_in_a_single_register():
    """When multiple structural signals fire, each must produce a distinct
    claim_id. Duplicates would corrupt downstream gating."""
    inputs = _empty_inputs()
    inputs["invalid_comparison_risk_register"] = [
        {"trigger": "x", "required_normalization": ["a"]},
        {"trigger": "y", "required_normalization": ["b"]},
    ]
    inputs["measurement_strategy_register"] = [
        {"hypothesis": "h1"},
        {"hypothesis": "h2"},
    ]
    contracts = build_congruence_claim_contract_register(**inputs)
    ids = [c["claim_id"] for c in contracts]
    # Each lane should produce at most one contract (claim governor
    # collapses to the first signal per lane). Verify no duplicates.
    assert len(set(ids)) == len(ids), f"duplicate claim_ids: {ids}"


# ── Invariant 7: evidence_state is always one of the bounded epistemic states ─


def test_evidence_state_is_always_bounded_epistemic():
    """Per claim_governor:24, permission='allowed' only when evidence_state
    is in {OBSERVED_FACT, CONDITIONAL_HYPOTHESIS, WEAK_SIGNAL, ARCHETYPAL_PRIOR}.
    No claim should emit with a state outside this set."""
    BOUNDED_STATES = {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "WEAK_SIGNAL", "ARCHETYPAL_PRIOR"}
    inputs = _empty_inputs()
    inputs["invalid_comparison_risk_register"] = [{"trigger": "x", "required_normalization": ["a"]}]
    inputs["measurement_strategy_register"] = [{"hypothesis": "h"}]
    inputs["regulatory_physics_register"] = [{"permits": ["NSPS"]}]
    inputs["finance_physics_dependency_register"] = [{"physics_dependency": "thermal"}]
    inputs["loss_pattern_hypothesis_register"] = [{"hypothesis": "thermal_dominance"}]
    inputs["culture_execution_proxy_register"] = [{"ownership_signal": "operator"}]
    contracts = build_congruence_claim_contract_register(**inputs)
    assert contracts
    for c in contracts:
        assert c["evidence_state"] in BOUNDED_STATES, (
            f"claim {c['claim_id']} has invalid evidence_state {c['evidence_state']}"
        )
