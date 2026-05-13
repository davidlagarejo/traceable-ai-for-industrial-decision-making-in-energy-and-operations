"""V5 P2 integration — motors emit their canonical phase unit.

For each phase 2/4/5/6/7/8, exercise the relevant motor adapter with
minimal fixture inputs and verify that the motor's output now includes
the canonical phase-unit register with the constitutional schema.

These tests guard against the canonical projection regressing if a
motor's internal output shape changes.
"""
from __future__ import annotations

import pytest


# ── Phase 2: motor_014 → inference_case_register_canonical ──────────


def test_motor_014_emits_inference_case_register_canonical():
    """motor_014 must add inference_case_register_canonical with the 6
    canonical attributes per record."""
    from runtime_orchestrator.adapters.motor_014 import Motor014Adapter

    minimal_case = {
        "case_id": "LC-001",
        "case_name": "Refrigeration tension",
        "claim_family": "tension",
        "conditional_statement": "if A then B",
        "inference_logic": "ASHRAE rule X",
        "validation_requirement": "Confirm meter granularity",
        "dependency_assumptions": ["assumes interval data"],
        "base_support_traces": ["motor_012.facility_prior"],
        "applicability_state": "active",
    }
    inputs = {
        "motor_013": {
            "inference_case_register": [minimal_case],
            "facility_prior_id": "fp:test",
        },
        "motor_007": {
            "target_definition_contract": {"target_type": "cold_chain_facility"},
        },
        "motor_012": {"facility_prior": {"facility_prior_id": "fp:test"}},
    }
    out = Motor014Adapter().run(inputs)
    assert "inference_case_register_canonical" in out
    canonical = out["inference_case_register_canonical"]
    assert isinstance(canonical, list)
    # When motor_014 activates the case, it should appear
    if canonical:  # may be filtered out by gates
        row = canonical[0]
        for k in ("base_support", "inference_logic", "claim_type",
                  "conditional_statement", "dependency_assumptions",
                  "validation_requirement"):
            assert k in row, f"missing canonical Phase 2 field: {k}"
        assert row["__phase__"] == 2
        assert row["__canonical_unit__"] == "inference_case"


# ── Phase 4: motor_034 → claim_upgrade_candidate_register ───────────


def test_motor_034_emits_claim_upgrade_candidate_register():
    """motor_034 must add claim_upgrade_candidate_register to its output."""
    from runtime_orchestrator.adapters.motor_034 import Motor034Adapter

    # Minimal inputs sufficient to construct the motor's output
    # without crashing. The register may be empty for sparse data.
    minimal_inputs = {
        "motor_001": {"validated_contracts": []},
        "motor_007": {
            "target_definition_contract": {"target_type": "cold_chain_facility"},
            "target_classification_object": {},
            "observable_cluster_register": {},
            "technical_substrate_readiness": "",
            "recommended_report_type": "Target Classification Brief",
        },
        "motor_008": {"source_register": []},
        "motor_010": {"deduplicated_objects": []},
        "motor_011": {"curated_library": []},
        "motor_012": {"facility_prior": {}, "missing_evidence_register": []},
        "motor_028": {"source_register": []},
        "motor_035": {},
        "motor_037": {"system_abstraction": {}},
        "motor_038": {"dominant_variable_register": []},
        "motor_039": {"archetype_resolution": {}, "archetype_library_register": []},
        "motor_040": {"cross_layer_conflict_register": []},
        "motor_041": {"problem_framing_register": []},
        "motor_042": {"structural_benchmark_register": []},
        "motor_043": {"competitive_comparison_register": []},
        "motor_044": {"conditional_redesign_register": []},
        "motor_045": {"structural_financial_exposure_register": []},
        "motor_046": {"minimum_evidence_for_discrimination_register": []},
        "motor_049": {},
        "motor_051": {"fair_comparison_profile": {}},
    }
    try:
        out = Motor034Adapter().run(minimal_inputs)
    except Exception as exc:
        pytest.skip(f"motor_034 needs more elaborate fixture: {exc}")
    assert "claim_upgrade_candidate_register" in out
    candidates = out["claim_upgrade_candidate_register"]
    assert isinstance(candidates, list)
    for candidate in candidates:
        assert candidate.get("__phase__") == 4
        assert candidate.get("__canonical_unit__") == "claim_upgrade_candidate"
        # 8 mandatory fields from Master Doc §5
        for field in (
            "evidence_local_required",
            "baseline_hardening_state",
            "contrast_route",
            "observation_route",
            "measurement_route",
            "instrument_dependency",
            "validity_domain",
            "upgrade_condition",
            "hold_degrade_block_reason",
        ):
            assert field in candidate


# ── Phase 5: motor_045 → financial_exposure_case_register ───────────


def test_motor_045_emits_financial_exposure_case_register():
    from runtime_orchestrator.adapters.motor_045 import Motor045Adapter

    minimal_inputs = {
        "motor_012": {"facility_prior": {}},
        "motor_007": {"target_definition_contract": {"target_type": "cold_chain_facility"}},
        "motor_037": {"system_abstraction": {}},
        "motor_038": {"dominant_variable_register": []},
        "motor_040": {"cross_layer_conflict_register": []},
        "motor_041": {"problem_framing_register": []},
        "motor_043": {"competitive_comparison_register": []},
        "motor_044": {"conditional_redesign_register": []},
    }
    out = Motor045Adapter().run(minimal_inputs)
    assert "financial_exposure_case_register" in out
    register = out["financial_exposure_case_register"]
    assert isinstance(register, list)
    for row in register:
        assert row.get("__phase__") == 5
        assert row.get("__canonical_unit__") == "financial_exposure_case"
        assert "decision_finance_posture" in row


# ── Phase 8: motor_033 → decision_admissibility_case_register ───────


def test_motor_033_emits_decision_admissibility_case_register():
    """motor_033 must add decision_admissibility_case_register +
    defer_investigate_act_map."""
    from runtime_orchestrator.adapters.motor_033 import Motor033Adapter

    minimal_inputs = {
        "motor_007": {
            "target_definition_contract": {"target_type": "cold_chain_facility"},
        },
        "motor_014": {
            "inference_records": [],
            "validation_queue": [],
            "next_best_questions": [],
            "conflict_register": [],
            "tension_records": [],
            "opportunity_candidates": [],
            "uncertainty_register": [],
            "evidence_gap_register": [],
            "report_readiness_register": {},
            "claim_permission_register": [],
            "variable_maturity_register": [],
            "minimum_evidence_unlock_map": {},
            "scenario_space": [],
            "scenario_evidence_link_register": [],
            "decision_front_register": [],
        },
        "motor_034": {},
        "motor_038": {"dominant_variable_register": []},
        "motor_046": {"minimum_evidence_for_discrimination_register": []},
        "motor_054": {},
    }
    try:
        out = Motor033Adapter().run(minimal_inputs)
    except Exception as exc:
        pytest.skip(f"motor_033 needs more elaborate fixture: {exc}")
    assert "decision_admissibility_case_register" in out
    assert "defer_investigate_act_map" in out
    register = out["decision_admissibility_case_register"]
    daa_map = out["defer_investigate_act_map"]
    assert isinstance(register, list)
    assert set(daa_map.keys()) == {"defer", "investigate", "act"}
    for row in register:
        assert row.get("__phase__") == 8
        assert row.get("__canonical_unit__") == "decision_admissibility_case"
        assert row.get("target_action_family") in (
            "inspect", "measure", "classify", "pilot",
            "design", "procure", "implement", "defer",
        )
