"""V5 P11 — Phase 8 depth tests.

Verifies that to_decision_admissibility_case_register structurally maps
motor_033's existing rich fields to the canonical Phase 8 schema, instead
of leaving them as placeholder empty strings (V5 P2 baseline).
"""
from __future__ import annotations

from runtime_orchestrator.phase_units import (
    _derive_publication_ceiling_phase8,
    to_decision_admissibility_case_register,
)


# ── Field mapping from motor_033 row ─────────────────────────────────


def test_downside_class_maps_from_downside_profile():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "implement",
        "downside_profile": "irreversible_capex",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["downside_class"] == "irreversible_capex"


def test_irreversibility_class_maps_from_irreversibility_profile():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "implement",
        "irreversibility_profile": "high",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["irreversibility_class"] == "high"


def test_current_support_posture_from_plausibility_band():
    """High plausibility unlocks 'supported_for_decision'."""
    high = [{"case_id": "T-1", "action_family": "act_now", "plausibility": 0.85}]
    mid = [{"case_id": "T-2", "action_family": "measure", "plausibility": 0.60}]
    low = [{"case_id": "T-3", "action_family": "inspect", "plausibility": 0.30}]
    assert to_decision_admissibility_case_register(high)[0]["current_support_posture"] == "supported_for_decision"
    assert to_decision_admissibility_case_register(mid)[0]["current_support_posture"] == "supported_for_screening"
    assert to_decision_admissibility_case_register(low)[0]["current_support_posture"] == "preliminary"


def test_required_evidence_burden_handles_string_field():
    """motor_033 stores evidence_needed as STRING. Projection wraps in list."""
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "measure",
        "evidence_needed": "compressor inventory + zone setpoints",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["required_evidence_burden"] == ["compressor inventory + zone setpoints"]


def test_required_evidence_burden_handles_list_field():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "measure",
        "required_evidence_burden": ["item1", "item2"],
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["required_evidence_burden"] == ["item1", "item2"]


def test_unresolved_blockers_from_no_go_condition():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "defer",
        "no_go_condition": "compressor inventory unconfirmed",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["unresolved_blockers"] == ["compressor inventory unconfirmed"]


def test_unresolved_blockers_explicit_list_preserved():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "defer",
        "unresolved_blockers": ["blocker1", "blocker2"],
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["unresolved_blockers"] == ["blocker1", "blocker2"]


# ── regulatory_dependency inference ──────────────────────────────────


def test_regulatory_dependency_inferred_from_compliance_claim_family():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "classify",
        "claim_family": "compliance",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert "regulatory exposure" in out[0]["regulatory_dependency"]


def test_regulatory_dependency_inferred_from_regulatory_claim_family():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "inspect",
        "claim_family": "regulatory_trigger",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert "regulatory exposure" in out[0]["regulatory_dependency"]


def test_regulatory_dependency_empty_for_non_regulatory_claim():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "measure",
        "claim_family": "tension",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["regulatory_dependency"] == ""


# ── publication_ceiling derivation ───────────────────────────────────


def test_publication_ceiling_no_go_takes_precedence():
    res = _derive_publication_ceiling_phase8(
        plausibility=0.99, posture="act_now", no_go="missing_baseline",
    )
    assert res == "no_go"


def test_publication_ceiling_defer_posture_is_screening_only():
    res = _derive_publication_ceiling_phase8(
        plausibility=0.90, posture="do_not_invest_yet", no_go="",
    )
    assert res == "screening_only"


def test_publication_ceiling_low_plausibility_is_screening_only():
    assert _derive_publication_ceiling_phase8(0.40, "investigate", "") == "screening_only"


def test_publication_ceiling_mid_plausibility_is_decision_grade():
    assert _derive_publication_ceiling_phase8(0.65, "investigate", "") == "decision_grade"


def test_publication_ceiling_high_plausibility_is_bounded_decision():
    assert _derive_publication_ceiling_phase8(0.85, "act_now", "") == "bounded_decision"


def test_publication_ceiling_in_register_row():
    tad_plan = [{
        "case_id": "T-1",
        "action_family": "measure",
        "plausibility": 0.40,
        "recommended_posture": "investigate",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert out[0]["publication_ceiling"] == "screening_only"


# ── End-to-end realistic motor_033 row ──────────────────────────────


def test_full_motor_033_row_maps_completely():
    """Real motor_033 row shape: every canonical Phase 8 field
    populated, no empty placeholders."""
    tad_plan = [{
        "rank": 1,
        "case_id": "LC-REFR-01",
        "case_name": "Refrigeration duty characterization",
        "action_title": "Validate: Refrigeration duty characterization",
        "action_family": "MEASURE_INTERVAL_DATA",
        "recommended_posture": "investigate",
        "voi_score": 0.85,
        "effort_tier": "medium",
        "downside_profile": "missed_savings_window",
        "irreversibility_profile": "low",
        "burden_level": "medium",
        "decision_unlock": "refrigeration retrofit prioritization",
        "evidence_needed": "compressor count + zone setpoints + 30-day load profile",
        "claim_family": "tension",
        "plausibility": 0.72,
        "epistemic_gap": 0.28,
        "no_go_condition": "",
        "sequencing_note": "needs facility walkdown",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    assert len(out) == 1
    row = out[0]
    # 8 canonical action families mapping
    assert row["target_action_family"] == "measure"
    # Per Master Doc §4: all these fields must be populated
    assert row["downside_class"] == "missed_savings_window"
    assert row["irreversibility_class"] == "low"
    assert row["current_support_posture"] == "supported_for_screening"  # plaus 0.72
    assert row["regulatory_dependency"] == ""  # tension is not regulatory
    assert row["required_evidence_burden"]
    assert row["unresolved_blockers"] == []  # no no_go
    assert row["publication_ceiling"] == "decision_grade"  # plaus 0.72, posture investigate
    assert row["voi_score"] == 0.85
    assert row["effort_tier"] == "medium"
    assert row["__phase__"] == 8
    assert row["__canonical_unit__"] == "decision_admissibility_case"


def test_full_motor_033_row_blocked_carries_no_go():
    tad_plan = [{
        "case_id": "LC-COMPLIANCE-01",
        "action_family": "DEFER",
        "recommended_posture": "do_not_invest_yet",
        "plausibility": 0.50,
        "downside_profile": "regulatory_exposure",
        "irreversibility_profile": "irreversible_legal",
        "claim_family": "compliance",
        "no_go_condition": "trigger_field_unconfirmed",
        "evidence_needed": "audit + trigger field confirmation",
    }]
    out = to_decision_admissibility_case_register(tad_plan)
    row = out[0]
    assert row["target_action_family"] == "defer"
    assert row["publication_ceiling"] == "no_go"
    assert row["unresolved_blockers"] == ["trigger_field_unconfirmed"]
    assert "regulatory exposure" in row["regulatory_dependency"]
    assert row["downside_class"] == "regulatory_exposure"
