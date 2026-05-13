"""V5 P2 — canonical phase-unit projection tests.

Verifies each phase's canonical projection function emits the exact
schema mandated by the constitutional master documents
(`Phases/phase-{N}/docs/es/`).
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.phase_units import (
    PHASE_8_ACTION_FAMILIES,
    derive_defer_investigate_act_map,
    to_belief_revision_event_register,
    to_claim_upgrade_candidate_register,
    to_compliance_applicability_case_register,
    to_decision_admissibility_case_register,
    to_financial_exposure_case_register,
    to_inference_case_register,
)


# ── Phase 2 — Inference Case ────────────────────────────────────────


def test_inference_case_has_six_canonical_attributes():
    record = {
        "case_id": "LC-001",
        "case_name": "Refrigeration cooling concentration",
        "base_support_traces": ["motor_012.facility_prior", "motor_028.census"],
        "inference_logic": "If cold_chain_facility and tariff exposure → tension",
        "claim_family": "tension",
        "conditional_statement": "If A then B given C",
        "dependency_assumptions": ["assumes meter granularity"],
        "validation_requirement": "Confirm utility tariff structure within 30d",
        "plausibility_score": 0.72,
        "decision_relevance_score": 0.81,
        "validation_urgency_score": 0.66,
    }
    register = to_inference_case_register([record])
    assert len(register) == 1
    case = register[0]
    # 6 canonical attributes
    assert case["base_support"] == ["motor_012.facility_prior", "motor_028.census"]
    assert case["inference_logic"].startswith("If cold_chain_facility")
    assert case["claim_type"] == "tension"
    assert case["conditional_statement"] == "If A then B given C"
    assert case["dependency_assumptions"] == ["assumes meter granularity"]
    assert case["validation_requirement"].startswith("Confirm utility tariff")
    # Scores
    assert case["plausibility_score"] == 0.72
    assert case["decision_relevance_score"] == 0.81
    assert case["validation_urgency_score"] == 0.66
    # Provenance
    assert case["__phase__"] == 2
    assert case["__canonical_unit__"] == "inference_case"


def test_inference_case_register_empty_input():
    assert to_inference_case_register([]) == []
    assert to_inference_case_register(None) == []  # type: ignore[arg-type]


# ── Phase 4 — claim_upgrade_candidate ──────────────────────────────


def test_claim_upgrade_candidate_carries_hardening_routes():
    permission_rows = [{
        "claim_id": "CL-001",
        "permission": "conditional",
        "baseline_hardening_state": "partial",
        "instrument_dependency": ["interval_meter"],
        "validity_domain": "cold_chain_facility/refrigeration",
    }]
    gaps = [{"linked_claim_id": "CL-001", "missing_evidence": "monthly bills"}]
    queue = [{"case_id": "CL-001", "validation_requirement": "measure load profile"}]
    register = to_claim_upgrade_candidate_register(permission_rows, gaps, queue)
    assert len(register) == 1
    candidate = register[0]
    assert candidate["claim_id"] == "CL-001"
    assert candidate["evidence_local_required"] == ["monthly bills"]
    assert "measure load profile" in candidate["measurement_route"]
    assert candidate["upgrade_condition"]  # non-empty
    assert candidate["__phase__"] == 4
    assert candidate["__canonical_unit__"] == "claim_upgrade_candidate"


def test_claim_upgrade_candidate_blocked_carries_hold_reason():
    permission_rows = [{"claim_id": "CL-002", "permission": "blocked"}]
    register = to_claim_upgrade_candidate_register(permission_rows)
    assert register[0]["hold_degrade_block_reason"]
    assert register[0]["upgrade_condition"] == ""


# ── Phase 5 — financial_exposure_case ──────────────────────────────


def test_financial_exposure_case_sparse_data_yields_screening_only():
    register = to_financial_exposure_case_register([
        {"case_id": "FE-001", "decision_front": "refrigeration upgrade"}
    ])
    assert register[0]["decision_finance_posture"] == "screening_only"
    assert register[0]["__phase__"] == 5
    assert register[0]["__canonical_unit__"] == "financial_exposure_case"


def test_financial_exposure_case_decision_grade_input():
    register = to_financial_exposure_case_register([{
        "case_id": "FE-002",
        "decision_front": "compressor staging",
        "support_state": "decision_grade",
    }])
    assert register[0]["decision_finance_posture"] == "decision_grade_range"


def test_financial_exposure_case_verified_input():
    register = to_financial_exposure_case_register([{
        "case_id": "FE-003",
        "support_state": "verified",
    }])
    assert register[0]["decision_finance_posture"] == "verified_finance"


# ── Phase 6 — compliance_applicability_case ────────────────────────


def test_compliance_applicability_case_relevant_only():
    flags = [{
        "flag_id": "LL84-2024",
        "jurisdiction": "NYC",
        "rule_family": "LL84",
    }]
    register = to_compliance_applicability_case_register(flags)
    assert register[0]["applicability_state"] == "rule_family_relevant"
    assert register[0]["__phase__"] == 6


def test_compliance_applicability_case_trigger_confirmed():
    flags = [{
        "flag_id": "LL97-2024",
        "jurisdiction": "NYC",
        "rule_family": "LL97",
        "trigger_confirmed": True,
    }]
    register = to_compliance_applicability_case_register(flags)
    assert register[0]["applicability_state"] == "trigger_confirmed"


def test_compliance_applicability_case_partial_trigger():
    flags = [{
        "flag_id": "LL97-2024",
        "rule_family": "LL97",
        "missing_trigger_fields": ["gross_floor_area"],
    }]
    register = to_compliance_applicability_case_register(flags)
    assert register[0]["applicability_state"] == "trigger_partially_supported"


def test_compliance_applicability_case_empty_input():
    assert to_compliance_applicability_case_register([]) == []
    assert to_compliance_applicability_case_register(None) == []


# ── Phase 7 — belief_revision_event ────────────────────────────────


def test_belief_revision_event_basic_log_entry():
    log = [{
        "event_id": "BRE-001",
        "target_object": "CL-001",
        "prior_state": "decision_grade",
        "trigger_event": "evidence_event",
        "dependency_type": "claim_dependency",
        "causal_statement": "new bill data narrows range",
        "scope_impact": "narrowed",
        "propagation_scope": ["CL-001", "CL-007"],
        "publication_consequence": "upgrade",
        "lifecycle_action": "upgrade",
    }]
    register = to_belief_revision_event_register(log)
    assert len(register) == 1
    ev = register[0]
    for k in ("target_object", "prior_state", "trigger_event", "dependency_type",
              "causal_statement", "scope_impact", "propagation_scope",
              "publication_consequence", "lifecycle_action"):
        assert k in ev
    assert ev["__phase__"] == 7


def test_belief_revision_event_includes_contradictions():
    register = to_belief_revision_event_register(
        belief_revision_log=[],
        contradiction_register=[{
            "contradiction_id": "C-1",
            "subject": "CL-001",
            "description": "benchmark says X, prior says Y",
            "affected_claims": ["CL-001", "CL-002"],
        }],
    )
    assert len(register) == 1
    assert register[0]["trigger_event"] == "contradiction_detected"
    assert register[0]["lifecycle_action"] == "hold"
    assert register[0]["propagation_scope"] == ["CL-001", "CL-002"]


# ── Phase 8 — decision_admissibility_case ──────────────────────────


def test_decision_admissibility_register_normalizes_to_8_canonical_families():
    """All 8 canonical action families recognized; unknowns default to classify."""
    inputs = [
        {"action_id": "T-1", "action": "INSPECT_FIELD"},
        {"action_id": "T-2", "action": "MEASURE_INTERVAL_DATA"},
        {"action_id": "T-3", "action": "DEFER_UNTIL_TARIFF_CONFIRMED"},
        {"action_id": "T-4", "action": "ACT_NOW"},  # → implement
        {"action_id": "T-5", "action": "PILOT_REFRIGERANT_SWAP"},
        {"action_id": "T-6", "action": "RFP_FOR_VENDOR"},  # → procure
        {"action_id": "T-7", "action": "DESIGN_BOUNDARY"},
        {"action_id": "T-8", "action": "TRIAGE_CASE"},  # → classify
    ]
    register = to_decision_admissibility_case_register(inputs)
    families = {row["target_action_family"] for row in register}
    expected = {"inspect", "measure", "defer", "implement", "pilot", "procure", "design", "classify"}
    assert families == expected
    # All 8 canonical families recognized
    assert set(PHASE_8_ACTION_FAMILIES) == expected


def test_decision_admissibility_register_no_go_signals():
    register = to_decision_admissibility_case_register(
        tad_action_plan=[],
        no_go_signals=[{"signal_id": "NG-1", "downside_class": "irreversible_capex"}],
    )
    assert len(register) == 1
    assert register[0]["target_action_family"] == "defer"
    assert register[0]["__no_go__"] is True
    assert register[0]["publication_ceiling"] == "no_go"


def test_defer_investigate_act_map_buckets_correctly():
    register = [
        {"decision_case_id": "T-1", "target_action_family": "inspect"},
        {"decision_case_id": "T-2", "target_action_family": "measure"},
        {"decision_case_id": "T-3", "target_action_family": "pilot"},
        {"decision_case_id": "T-4", "target_action_family": "classify"},
        {"decision_case_id": "T-5", "target_action_family": "implement"},
        {"decision_case_id": "T-6", "target_action_family": "procure"},
        {"decision_case_id": "T-7", "target_action_family": "design"},
        {"decision_case_id": "T-8", "target_action_family": "defer"},
    ]
    m = derive_defer_investigate_act_map(register)
    assert sorted(m["investigate"]) == ["T-1", "T-2", "T-3", "T-4"]
    assert sorted(m["act"]) == ["T-5", "T-6", "T-7"]
    assert m["defer"] == ["T-8"]
