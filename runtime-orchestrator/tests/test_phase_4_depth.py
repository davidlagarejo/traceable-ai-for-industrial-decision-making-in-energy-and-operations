"""V5 P10 — Phase 4 depth tests.

Verifies that `to_claim_upgrade_candidate_register` STRUCTURALLY computes
`baseline_hardening_state`, `instrument_dependency`, and `validity_domain`
from variable_maturity_register + target_asset_family — instead of
leaving them as placeholder empty strings (V5 P2 baseline).
"""
from __future__ import annotations

from runtime_orchestrator.phase_units import to_claim_upgrade_candidate_register


# ── baseline_hardening_state computation ───────────────────────────


def test_baseline_hardening_uses_weakest_required_variable():
    """The baseline is bounded by the WEAKEST required variable
    (Phase 4 §5: hardening is gated by the weakest link)."""
    permissions = [{
        "claim_id": "CL-001",
        "claim_name": "CL-001",
        "required_variables": ["var_a", "var_b", "var_c"],
        "current_permission": "conditional",
    }]
    variables = [
        {"variable_name": "var_a", "maturity_level": "verified"},
        {"variable_name": "var_b", "maturity_level": "hypothesis"},  # weakest
        {"variable_name": "var_c", "maturity_level": "decision_grade"},
    ]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=variables,
    )
    assert len(out) == 1
    # weakest = hypothesis → preliminary
    assert out[0]["baseline_hardening_state"] == "preliminary"


def test_baseline_hardening_all_verified():
    permissions = [{
        "claim_id": "CL-001",
        "required_variables": ["v1", "v2"],
        "current_permission": "permitted",
    }]
    variables = [
        {"variable_name": "v1", "maturity_level": "verified"},
        {"variable_name": "v2", "maturity_level": "verified"},
    ]
    out = to_claim_upgrade_candidate_register(permissions, variable_maturity_register=variables)
    assert out[0]["baseline_hardening_state"] == "verified_baseline"


def test_baseline_hardening_no_required_variables_returns_unsupported():
    permissions = [{
        "claim_id": "CL-orphan",
        "required_variables": [],
        "current_permission": "blocked",
    }]
    out = to_claim_upgrade_candidate_register(permissions)
    assert out[0]["baseline_hardening_state"] == "unsupported"


def test_baseline_hardening_unknown_variable_treated_as_unsupported():
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": ["var_missing"],
        "current_permission": "conditional",
    }]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=[],  # no maturity rows
    )
    assert out[0]["baseline_hardening_state"] == "unsupported"


def test_baseline_hardening_partially_hardened_input():
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": ["v1"],
    }]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=[
            {"variable_name": "v1", "maturity_level": "partially_hardened"},
        ],
    )
    assert out[0]["baseline_hardening_state"] == "partially_hardened"


# ── instrument_dependency computation ──────────────────────────────


def test_instrument_dependency_collects_evidence_sources():
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": ["v1", "v2", "v3"],
    }]
    variables = [
        {"variable_name": "v1", "maturity_level": "decision_grade",
         "evidence_source": "interval_meter"},
        {"variable_name": "v2", "maturity_level": "decision_grade",
         "evidence_source": "bms_log"},
        {"variable_name": "v3", "maturity_level": "decision_grade",
         "evidence_source": "interval_meter"},  # dup
    ]
    out = to_claim_upgrade_candidate_register(permissions, variable_maturity_register=variables)
    deps = out[0]["instrument_dependency"]
    assert "interval_meter" in deps
    assert "bms_log" in deps
    assert len(deps) == 2  # dedup


def test_instrument_dependency_empty_when_no_evidence_source():
    permissions = [{"claim_id": "CL-1", "required_variables": ["v1"]}]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=[{"variable_name": "v1", "maturity_level": "hypothesis"}],
    )
    assert out[0]["instrument_dependency"] == []


# ── validity_domain computation ────────────────────────────────────


def test_validity_domain_combines_family_and_target():
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": [],
        "variable_family": "refrigeration",
    }]
    out = to_claim_upgrade_candidate_register(
        permissions,
        target_asset_family="cold_chain_facility",
    )
    assert out[0]["validity_domain"] == "cold_chain_facility/refrigeration"


def test_validity_domain_falls_back_to_target_only():
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": [],
    }]
    out = to_claim_upgrade_candidate_register(
        permissions,
        target_asset_family="manufacturing_facility",
    )
    assert out[0]["validity_domain"] == "manufacturing_facility"


def test_validity_domain_falls_back_to_case_scoped():
    permissions = [{"claim_id": "CL-1", "required_variables": []}]
    out = to_claim_upgrade_candidate_register(permissions)
    assert out[0]["validity_domain"] == "case-scoped"


# ── End-to-end: motor_034 row shape ────────────────────────────────


def test_full_phase4_unit_with_realistic_motor_034_inputs():
    """End-to-end with claim_name field (motor_034 uses claim_name, not claim_id)."""
    permissions = [{
        "claim_name": "refrigeration_duty_dominant_load",
        "required_variables": ["compressor_inventory", "setpoint_evidence"],
        "current_permission": "conditional",
        "required_evidence": ["compressor count and type", "zone temperature setpoints"],
    }]
    variables = [
        {"variable_name": "compressor_inventory", "maturity_level": "decision_grade",
         "evidence_source": "facility_walkdown"},
        {"variable_name": "setpoint_evidence", "maturity_level": "indication",
         "evidence_source": "operator_interview"},
    ]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=variables,
        target_asset_family="cold_chain_facility",
    )
    assert len(out) == 1
    row = out[0]
    assert row["claim_id"] == "refrigeration_duty_dominant_load"
    # weakest = indication → preliminary
    assert row["baseline_hardening_state"] == "preliminary"
    assert "facility_walkdown" in row["instrument_dependency"]
    assert "operator_interview" in row["instrument_dependency"]
    assert row["validity_domain"] == "cold_chain_facility"  # no variable_family in row
    assert "compressor count and type" in row["evidence_local_required"]
    assert row["__phase__"] == 4
    assert row["__canonical_unit__"] == "claim_upgrade_candidate"


def test_full_phase4_unit_blocked_claim_carries_hold_reason():
    permissions = [{
        "claim_id": "CL-blocked",
        "required_variables": ["var_critical"],
        "current_permission": "blocked",
    }]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=[{"variable_name": "var_critical", "maturity_level": "absent"}],
    )
    row = out[0]
    assert row["baseline_hardening_state"] == "unsupported"
    assert row["hold_degrade_block_reason"]
    assert "cannot upgrade" in row["hold_degrade_block_reason"]


def test_upgrade_path_appended_to_upgrade_condition():
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": ["v1"],
        "current_permission": "conditional",
        "upgrade_path": ["confirm_compressor_count", "measure_zone_temps"],
    }]
    out = to_claim_upgrade_candidate_register(
        permissions,
        variable_maturity_register=[{"variable_name": "v1", "maturity_level": "decision_grade"}],
    )
    cond = out[0]["upgrade_condition"]
    assert "confirm_compressor_count" in cond
    assert "measure_zone_temps" in cond


# ── Backwards compat: V5 P2 baseline behavior preserved ─────────────


def test_works_without_variable_maturity_register():
    """When motor doesn't pass variable_maturity_register, the projection
    still produces canonical-shape rows (just with unsupported baseline)."""
    permissions = [{
        "claim_id": "CL-1",
        "required_variables": ["v1"],
        "current_permission": "permitted",
    }]
    out = to_claim_upgrade_candidate_register(permissions)  # no extra args
    assert len(out) == 1
    assert "baseline_hardening_state" in out[0]
    assert "instrument_dependency" in out[0]
    assert "validity_domain" in out[0]
