"""V6 P8 — motor_059 hard precedence rules R8-R11 tests."""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_059 import (
    _detect_R8_digital_twin_when_dominant_unresolved,
    _detect_R9_roi_when_control_boundary_unresolved,
    _detect_R10_peer_superiority_when_normalization_incomplete,
    _detect_R11_verified_savings_when_baseline_soft,
)


# ── R8: digital twin forbidden when dominant variables unresolved ──


def test_R8_fires_when_unresolved_variable_and_digital_twin_action():
    actions = [{"action_title": "Build digital twin of refrigeration plant"}]
    dominant = [{"variable": "refrigeration_duty", "evidence_state": "CONDITIONAL_HYPOTHESIS"}]
    out = _detect_R8_digital_twin_when_dominant_unresolved(actions, dominant)
    assert len(out) == 1
    assert out[0]["rule_id"] == "R8_digital_twin_with_unresolved_dominant_variable"


def test_R8_does_not_fire_when_all_dominant_resolved():
    actions = [{"action_title": "Build digital twin model"}]
    dominant = [{"variable": "refrigeration_duty", "evidence_state": "OBSERVED_FACT"}]
    out = _detect_R8_digital_twin_when_dominant_unresolved(actions, dominant)
    assert out == []


def test_R8_does_not_fire_when_action_unrelated():
    actions = [{"action_title": "Inspect compressor inventory"}]
    dominant = [{"variable": "x", "evidence_state": "CONDITIONAL_HYPOTHESIS"}]
    out = _detect_R8_digital_twin_when_dominant_unresolved(actions, dominant)
    assert out == []


# ── R9: ROI forbidden when control boundary unresolved ──


def test_R9_fires_when_control_boundary_unresolved_and_roi_action():
    actions = [{"action_title": "Compute ROI for HVAC retrofit"}]
    dominant = [{"variable": "owner_control_boundary", "evidence_state": "CONDITIONAL_HYPOTHESIS"}]
    out = _detect_R9_roi_when_control_boundary_unresolved(actions, dominant)
    assert len(out) == 1
    assert out[0]["rule_id"] == "R9_roi_claim_with_unresolved_control_boundary"


def test_R9_does_not_fire_when_control_boundary_observed():
    actions = [{"action_title": "Compute ROI for HVAC retrofit"}]
    dominant = [{"variable": "control_boundary_tenant", "evidence_state": "OBSERVED_FACT"}]
    out = _detect_R9_roi_when_control_boundary_unresolved(actions, dominant)
    assert out == []


def test_R9_fires_on_payback_token_too():
    actions = [{"action_title": "Estimate payback period"}]
    dominant = [{"variable": "owner_tenant_boundary", "evidence_state": "WEAK_SIGNAL"}]
    out = _detect_R9_roi_when_control_boundary_unresolved(actions, dominant)
    assert len(out) == 1


# ── R10: peer superiority forbidden when normalization incomplete ──


def test_R10_fires_when_invalid_comparison_risks_exist_and_peer_action():
    actions = [{"action_title": "Demonstrate outperform vs peer"}]
    m051 = {"invalid_comparison_risk_register": [{"risk": "area_normalized"}]}
    out = _detect_R10_peer_superiority_when_normalization_incomplete(actions, m051)
    assert len(out) == 1
    assert out[0]["rule_id"] == "R10_peer_superiority_with_incomplete_normalization"


def test_R10_does_not_fire_when_normalization_clean():
    actions = [{"action_title": "Top quartile positioning analysis"}]
    m051 = {"invalid_comparison_risk_register": [], "comparison_not_yet_valid_register": []}
    out = _detect_R10_peer_superiority_when_normalization_incomplete(actions, m051)
    assert out == []


# ── R11: verified savings forbidden when baseline soft ──


def test_R11_fires_when_no_hardened_baseline_and_verified_savings_action():
    actions = [{"action_title": "Claim verified savings of 30%"}]
    exposure = [{"baseline_dependency_state": "preliminary"}]
    out = _detect_R11_verified_savings_when_baseline_soft(actions, exposure)
    assert len(out) == 1
    assert out[0]["rule_id"] == "R11_verified_savings_with_soft_baseline"


def test_R11_does_not_fire_when_baseline_hardened():
    actions = [{"action_title": "Verified savings post-retrofit"}]
    exposure = [{"baseline_dependency_state": "hardened"}]
    out = _detect_R11_verified_savings_when_baseline_soft(actions, exposure)
    assert out == []


def test_R11_does_not_fire_when_action_unrelated():
    actions = [{"action_title": "Measure interval data"}]
    exposure = [{"baseline_dependency_state": "preliminary"}]
    out = _detect_R11_verified_savings_when_baseline_soft(actions, exposure)
    assert out == []


# ── full motor_059 integration: R8-R11 surface in warnings ────────


def test_motor_059_emits_R8_R11_warnings_in_full_run():
    from runtime_orchestrator.adapters.motor_059 import Motor059Adapter
    inputs = {
        "motor_016": {"report_package": {"governance_summary": {}}},
        "motor_018": {"chart_assets": []},
        "motor_033": {"expanded_structural_tad_action_register": [
            {"action_id": "T-1", "action_title": "Build digital twin of HVAC"},
            {"action_id": "T-2", "action_title": "Estimate ROI for retrofit"},
            {"action_id": "T-3", "action_title": "Claim verified savings of 25%"},
        ]},
        "motor_038": {"dominant_variable_register": [
            {"variable": "refrigeration_duty", "evidence_state": "CONDITIONAL_HYPOTHESIS"},
            {"variable": "control_boundary", "evidence_state": "WEAK_SIGNAL"},
        ]},
        "motor_045": {"financial_exposure_case_register": [
            {"baseline_dependency_state": "preliminary"},
        ]},
        "motor_051": {"invalid_comparison_risk_register": []},
        "motor_054": {"congruence_claim_contract_register": [],
                      "strategic_gold_nugget_register": []},
    }
    out = Motor059Adapter().run(inputs)
    warnings = out["strategic_intelligence_warnings"]
    rule_ids = {w["rule_id"] for w in warnings}
    # R8, R9, R11 should all fire given the setup
    assert "R8_digital_twin_with_unresolved_dominant_variable" in rule_ids
    assert "R9_roi_claim_with_unresolved_control_boundary" in rule_ids
    assert "R11_verified_savings_with_soft_baseline" in rule_ids
