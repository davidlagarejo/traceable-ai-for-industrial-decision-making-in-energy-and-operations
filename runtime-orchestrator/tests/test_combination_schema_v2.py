"""Tests for V3 G7: combination schema v2 — 7 optional retro-compatible fields.

Existing combinations without v2 fields must continue to validate. New v2
fields, when present, are typed and checked.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.zlab_skill.schema import (
    RegistryValidationError,
    validate_combination_spec,
)


def _base():
    """Minimal valid v1 combination (all required fields present)."""
    return {
        "id": "test_combo_v1",
        "version": "1.0.0",
        "name": "Test Combo",
        "pattern_ids": ["pattern_a", "pattern_b"],
        "trigger_logic": ["trigger A", "trigger B"],
        "anti_triggers": ["anti A"],
        "combined_hypothesis": "Test hypothesis text",
        "strategic_risk": "Test risk text",
        "minimum_evidence": ["evidence 1"],
        "financial_exposure": ["risk 1"],
        "tad_action": "VALIDATE_LOSS_PATTERN",
        "prohibited_claims": ["bad claim"],
        "allowed_language": "Test allowed language",
        "source_basis": ["licensed_research_public_technical_priors"],
        "confidence_ceiling": "L2",
        "adjudication_required": True,
        "tests": ["test 1"],
    }


# ── Retro-compatibility ─────────────────────────────────────────────────


def test_v1_combination_still_validates_without_v2_fields():
    out = validate_combination_spec(_base())
    assert out["id"] == "test_combo_v1"
    assert "evidence_pack" not in out
    assert "falsification" not in out
    assert "preconditions" not in out


# ── evidence_pack (dict) ────────────────────────────────────────────────


def test_evidence_pack_dict_passes():
    payload = _base() | {
        "evidence_pack": {
            "cheapest_valid_path": "leak survey",
            "escalation_path": "ultrasonic audit",
            "stop_condition": "leak rate < 5%",
            "local_intake_trigger": "utility bill spike",
        }
    }
    out = validate_combination_spec(payload)
    assert out["evidence_pack"]["cheapest_valid_path"] == "leak survey"


def test_evidence_pack_must_be_dict():
    payload = _base() | {"evidence_pack": "not a dict"}
    with pytest.raises(RegistryValidationError, match="evidence_pack must be a dict"):
        validate_combination_spec(payload)


# ── falsification (str) ─────────────────────────────────────────────────


def test_falsification_text_passes():
    payload = _base() | {"falsification": "If thermal duty < 30% of total energy"}
    out = validate_combination_spec(payload)
    assert out["falsification"] == "If thermal duty < 30% of total energy"


def test_falsification_must_be_non_empty():
    payload = _base() | {"falsification": ""}
    with pytest.raises(RegistryValidationError):
        validate_combination_spec(payload)


# ── gold_nugget (str) ───────────────────────────────────────────────────


def test_gold_nugget_text_passes():
    payload = _base() | {"gold_nugget": "Process thermal duty likely dominates energy intensity"}
    out = validate_combination_spec(payload)
    assert "thermal duty" in out["gold_nugget"]


# ── comparison_impact (str) ─────────────────────────────────────────────


def test_comparison_impact_text_passes():
    payload = _base() | {"comparison_impact": "Disables NAICS-only peer comparison"}
    out = validate_combination_spec(payload)
    assert "NAICS-only" in out["comparison_impact"]


# ── preconditions (list[str]) ───────────────────────────────────────────


def test_preconditions_list_passes():
    payload = _base() | {"preconditions": ["thermal_duty_bounded", "uptime_economics_bounded"]}
    out = validate_combination_spec(payload)
    assert out["preconditions"] == ["thermal_duty_bounded", "uptime_economics_bounded"]


def test_preconditions_must_be_list_not_string():
    payload = _base() | {"preconditions": "not_a_list"}
    with pytest.raises(RegistryValidationError, match="must be a list"):
        validate_combination_spec(payload)


# ── conditional_clause (str) ────────────────────────────────────────────


def test_conditional_clause_text_passes():
    payload = _base() | {
        "conditional_clause": "Compressed air matters only if thermal duty is bounded."
    }
    out = validate_combination_spec(payload)
    assert "thermal duty is bounded" in out["conditional_clause"]


# ── layers_combined (list[str], validated against allow-list) ───────────


def test_layers_combined_valid_layers_pass():
    payload = _base() | {"layers_combined": ["physics", "ops", "maintenance", "finance"]}
    out = validate_combination_spec(payload)
    assert "physics" in out["layers_combined"]


def test_layers_combined_unknown_layer_rejected():
    payload = _base() | {"layers_combined": ["physics", "thermodynamics"]}
    with pytest.raises(RegistryValidationError, match="layers_combined contains unknown"):
        validate_combination_spec(payload)


def test_all_8_allowed_layers_accepted():
    payload = _base() | {
        "layers_combined": [
            "physics", "ops", "maintenance", "finance",
            "tariffs", "reliability", "control", "regulation",
        ]
    }
    out = validate_combination_spec(payload)
    assert len(out["layers_combined"]) == 8


# ── Full v2 combination (all 7 optional fields) ─────────────────────────


def test_full_v2_combination_with_all_optional_fields():
    payload = _base() | {
        "evidence_pack": {
            "cheapest_valid_path": "thermal map",
            "escalation_path": "full energy audit",
            "stop_condition": "thermal energy bounded < 20%",
            "local_intake_trigger": "NAICS in {3274, 3273}",
        },
        "falsification": "Thermal share < 20% of total kWh",
        "gold_nugget": "Process thermal duty governs energy structure",
        "comparison_impact": "Disables generic kWh/sf peer comparison",
        "preconditions": ["throughput_bounded"],
        "conditional_clause": "Combination matters only when throughput is characterized",
        "layers_combined": ["physics", "ops", "finance"],
    }
    out = validate_combination_spec(payload)
    assert out["evidence_pack"]["cheapest_valid_path"] == "thermal map"
    assert out["falsification"]
    assert out["gold_nugget"]
    assert out["comparison_impact"]
    assert out["preconditions"] == ["throughput_bounded"]
    assert out["conditional_clause"]
    assert out["layers_combined"] == ["physics", "ops", "finance"]


# ── Verify all 4 existing approved combinations still validate ──────────


def test_existing_4_approved_combinations_still_validate_under_v2_schema():
    """Critical retro-compatibility check: V3 schema upgrade must NOT
    break the 4 combinations already in zlab_skill/registry/combinations/."""
    from runtime_orchestrator.zlab_skill.loader import load_combination_specs
    combos = load_combination_specs()
    assert len(combos) == 4
    ids = sorted(c["id"] for c in combos)
    assert ids == [
        "manufacturing_support_utility_maintenance_combo",
        "office_after_hours_phantom_load_combo",
        "process_heat_unbounded_duty_combo",
        "warehouse_tariff_boundary_area_combo",
    ]
