"""V5 P13 — Phase 5 depth tests.

Verifies `to_financial_exposure_case_register` STRUCTURALLY populates
the Master Doc §4+§7 fields from motor_045 row data, instead of leaving
them as placeholder empty strings.
"""
from __future__ import annotations

from runtime_orchestrator.phase_units import (
    _evidence_state_to_basis_state,
    _publication_ceiling_phase5,
    to_financial_exposure_case_register,
)


# ── helpers ─────────────────────────────────────────────────────────


def test_evidence_state_to_basis_state_mapping():
    assert _evidence_state_to_basis_state("OBSERVED_FACT") == "hardened"
    assert _evidence_state_to_basis_state("CONDITIONAL_HYPOTHESIS") == "preliminary"
    assert _evidence_state_to_basis_state("WEAK_SIGNAL") == "screening_only"
    assert _evidence_state_to_basis_state("ARCHETYPAL_PRIOR") == "prior_only"
    assert _evidence_state_to_basis_state("") == "unknown"
    assert _evidence_state_to_basis_state("XYZ") == "unknown"


def test_publication_ceiling_phase5_per_posture():
    assert _publication_ceiling_phase5("screening_only") == "screening_only"
    assert _publication_ceiling_phase5("decision_grade_range") == "decision_grade_range"
    assert _publication_ceiling_phase5("partially_hardened_finance") == "bounded_finance"
    assert _publication_ceiling_phase5("verified_finance") == "verified_bounded"


# ── tariff_basis_state from evidence_needed ────────────────────────


def test_tariff_basis_state_when_tariff_evidence_needed():
    register = [{
        "structural_assumption": "owner can capture savings",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "evidence_needed": ["utility bills", "tariff schedule"],
    }]
    out = to_financial_exposure_case_register(register)
    assert out[0]["tariff_basis_state"] == "evidence_required"


def test_tariff_basis_state_when_no_tariff_evidence_needed():
    register = [{
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "evidence_needed": ["compressor inventory"],
    }]
    out = to_financial_exposure_case_register(register)
    # No tariff token → defaults to basis_state mapping
    assert out[0]["tariff_basis_state"] == "preliminary"


# ── cost_basis_state ───────────────────────────────────────────────


def test_cost_basis_state_when_capex_mentioned():
    register = [{
        "evidence_state": "OBSERVED_FACT",
        "evidence_needed": ["lifecycle CAPEX schedule"],
    }]
    out = to_financial_exposure_case_register(register)
    assert out[0]["cost_basis_state"] == "evidence_required"


# ── regulatory_dependency_state ────────────────────────────────────


def test_regulatory_dependency_detects_ll97_in_assumption():
    register = [{
        "structural_assumption": "LL97 carbon pathway constraints apply",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "evidence_needed": [],
    }]
    out = to_financial_exposure_case_register(register)
    assert out[0]["regulatory_dependency_state"] == "regulatory_exposure_plausible"


def test_regulatory_dependency_detects_epa_in_exposure_text():
    register = [{
        "structural_assumption": "owner side",
        "financial_exposure_if_wrong": "EPA permit conditions can dominate",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "evidence_needed": [],
    }]
    out = to_financial_exposure_case_register(register)
    assert out[0]["regulatory_dependency_state"] == "regulatory_exposure_plausible"


def test_regulatory_dependency_not_evident_otherwise():
    register = [{
        "structural_assumption": "compressor inventory drives load",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "evidence_needed": ["bills", "schedule"],
    }]
    out = to_financial_exposure_case_register(register)
    assert out[0]["regulatory_dependency_state"] == "not_evident"


# ── benefit_driver_family from allowed_financial_output ─────────────


def test_benefit_driver_family_from_allowed_outputs():
    register = [{
        "structural_assumption": "x",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "allowed_financial_output": [
            "screening-grade savings band",
            "operational opex reduction range",
        ],
    }]
    out = to_financial_exposure_case_register(register)
    assert "screening-grade savings band" in out[0]["benefit_driver_family"]
    assert len(out[0]["benefit_driver_family"]) == 2


# ── asset_boundary uses target_asset_family ─────────────────────────


def test_asset_boundary_uses_target_asset_family():
    register = [{
        "structural_assumption": "x",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
    }]
    out = to_financial_exposure_case_register(
        register,
        target_asset_family="cold_chain_facility",
    )
    assert out[0]["asset_boundary"] == "cold_chain_facility"


# ── enum-prefixed evidence_state handling ──────────────────────────


def test_evidence_state_handles_enum_prefix():
    """motor_045 may serialize evidence_state as 'StructuralEvidenceState.CONDITIONAL_HYPOTHESIS'."""
    register = [{
        "structural_assumption": "x",
        "evidence_state": "StructuralEvidenceState.OBSERVED_FACT",
        "evidence_needed": [],
    }]
    out = to_financial_exposure_case_register(register)
    assert out[0]["baseline_dependency_state"] == "hardened"


# ── End-to-end realistic motor_045 row ──────────────────────────────


def test_full_motor_045_row_maps_completely():
    register = [{
        "structural_assumption": "owner-controllable savings exist and can be captured by owner-side retrofit economics.",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "financial_exposure_if_wrong": "Retrofit CAPEX may reduce site energy without improving owner economics because dominant loads sit in tenant space.",
        "evidence_needed": [
            "utility bills",
            "tenant metering map",
            "lease responsibility matrix",
            "central plant / BMS topology",
        ],
        "allowed_financial_output": [
            "screening-grade savings band",
            "owner-tenant boundary risk flag",
        ],
        "prohibited_financial_output": [
            "ROI claim",
            "bankable NPV",
        ],
        "support_state": "screening_grade",
    }]
    out = to_financial_exposure_case_register(
        register,
        target_asset_family="commercial_building",
    )
    assert len(out) == 1
    row = out[0]
    # 10 canonical Phase 5 fields all populated
    assert row["asset_boundary"] == "commercial_building"
    assert row["baseline_dependency_state"] == "preliminary"
    assert row["tariff_basis_state"] == "evidence_required"  # 'utility bills' triggers
    assert row["cost_basis_state"] == "preliminary"  # no CAPEX in evidence_needed (only 'lifecycle' would trigger)
    assert row["regulatory_dependency_state"] == "not_evident"  # no LL97/EPA/etc.
    assert row["benefit_driver_family"]
    assert row["publication_ceiling"] == "screening_only"
    assert row["decision_finance_posture"] == "screening_only"
    assert row["exposure_if_wrong"]  # preserved
    assert row["__phase__"] == 5
    assert row["__canonical_unit__"] == "financial_exposure_case"


def test_full_motor_045_ll97_case():
    register = [{
        "structural_assumption": "LL97 carbon-pathway compliance interacts with retrofit economics",
        "evidence_state": "OBSERVED_FACT",
        "evidence_needed": ["LL97 emissions limit schedule", "CAPEX pathway costing"],
        "allowed_financial_output": ["compliance-driven retrofit framing"],
        "support_state": "decision_grade",
    }]
    out = to_financial_exposure_case_register(
        register,
        target_asset_family="commercial_building",
    )
    row = out[0]
    assert row["regulatory_dependency_state"] == "regulatory_exposure_plausible"
    assert row["cost_basis_state"] == "evidence_required"
    assert row["baseline_dependency_state"] == "hardened"
    assert row["decision_finance_posture"] == "decision_grade_range"
    assert row["publication_ceiling"] == "decision_grade_range"


def test_empty_register_returns_empty():
    assert to_financial_exposure_case_register([]) == []
    assert to_financial_exposure_case_register(None) == []
