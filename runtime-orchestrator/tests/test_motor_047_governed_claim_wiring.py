"""Tests for the R-W01+R-W02a wiring: motor_047 propagates
congruence_claim_contract_register from motor_054 → executive_thesis output.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_047 import Motor047Adapter
from runtime_orchestrator.executive_thesis import build_executive_thesis


def _minimal_kwargs():
    return {
        "system_abstraction": {},
        "canonical_problem_frame": {},
        "problem_framing_register": [],
        "dominant_variable_register": [],
        "cross_layer_conflict_register": [],
        "scenario_register": [],
        "structural_financial_exposure_register": [],
        "competitive_comparison_register": [],
        "conditional_redesign_register": [],
        "minimum_evidence_for_discrimination_register": [],
        "expanded_structural_tad_action_register": [],
        "claim_contract_register": [],
        "report_output_mode_classifier_table": [],
    }


def test_executive_thesis_accepts_congruence_claim_contract_register_kwarg():
    out = build_executive_thesis(
        **_minimal_kwargs(),
        congruence_claim_contract_register=[
            {
                "claim_id": "demo_claim",
                "permission": "allowed",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "falsification_condition": "test",
            }
        ],
    )
    assert "governed_claim_contract_register" in out
    assert out["governed_claim_contract_count"] == 1
    assert out["governed_claim_contract_register"][0]["claim_id"] == "demo_claim"


def test_executive_thesis_default_is_empty_list():
    out = build_executive_thesis(**_minimal_kwargs())
    assert out["governed_claim_contract_register"] == []
    assert out["governed_claim_contract_count"] == 0


def test_motor_047_propagates_register_from_m54():
    adapter = Motor047Adapter()
    inputs = {
        "motor_054": {
            "congruence_claim_contract_register": [
                {
                    "claim_id": "claim_a",
                    "permission": "allowed",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "falsification_condition": "evidence shows X",
                },
                {
                    "claim_id": "claim_b",
                    "permission": "prohibited",
                    "evidence_state": "WEAK_SIGNAL",
                },
            ]
        }
    }
    result = adapter.run(inputs)
    assert result["governed_claim_contract_count"] == 2
    thesis = result["executive_thesis"]
    assert thesis["governed_claim_contract_count"] == 2
    ids = [c.get("claim_id") for c in thesis["governed_claim_contract_register"]]
    assert ids == ["claim_a", "claim_b"]


def test_motor_047_handles_missing_m54_gracefully():
    adapter = Motor047Adapter()
    result = adapter.run({})
    assert result["governed_claim_contract_count"] == 0
    assert result["executive_thesis"]["governed_claim_contract_register"] == []


def test_motor_047_handles_m54_without_register_key():
    adapter = Motor047Adapter()
    result = adapter.run({"motor_054": {"unrelated_key": "value"}})
    assert result["governed_claim_contract_count"] == 0
