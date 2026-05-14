"""V9 P3 — Industry Onboarding Workflow tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.industry_onboarding import (
    CANONICAL_INDUSTRY_REQUIREMENTS,
    IndustrySpec,
    OnboardingVerdict,
    industry_onboarding_summary,
    validate_industry_readiness,
)


def _ready_thermal_process_spec() -> dict:
    """Synthetic 'thermal_process_demo' industry that's complete."""
    return {
        "industry_id": "thermal_process_demo",
        "process_taxonomy": ["cook", "pasteurize", "retort", "sanitation_steam"],
        "machine_taxonomy": ["boiler", "steam_trap", "heat_exchanger"],
        "dominant_variables": ["process_heat_duty", "steam_pressure", "throughput"],
        "failure_modes": [
            "boiler_degradation", "steam_trap_failure",
            "condensate_loss", "envelope_loss",
        ],
        "evidence_map": {
            "boiler_degradation_plausibility": ["boiler runtime log", "stack temp"],
            "steam_trap_failure": ["ultrasonic survey", "thermal imaging"],
            "process_load_vs_waste": ["production schedule", "steam meter"],
        },
        "financial_translation": (
            "Process heat costs scale with production volume — mis-characterized "
            "duty leads to wrong CAPEX target."
        ),
        "regulatory_triggers": ["EPA NESHAP boilers", "state air permit"],
        "combinations": ["process_heat_unbounded_duty_combo"],
        "tad_mapping": [
            "VALIDATE_PROCESS_HEAT_DUTY",
            "INSPECT_STEAM_TRAPS",
            "MEASURE_BOILER_EFFICIENCY",
        ],
        "qa_tests": ["thermal_process_acceptance_v1"],
    }


# ── 10 canonical requirements declared ────────────────────────────


def test_ten_canonical_requirements():
    assert len(CANONICAL_INDUSTRY_REQUIREMENTS) == 10
    for required in (
        "process_taxonomy", "machine_taxonomy", "dominant_variables",
        "failure_modes", "evidence_map", "financial_translation",
        "regulatory_triggers", "combinations", "tad_mapping", "qa_tests",
    ):
        assert required in CANONICAL_INDUSTRY_REQUIREMENTS


# ── Complete spec → ready ─────────────────────────────────────────


def test_complete_spec_is_ready():
    verdict = validate_industry_readiness(_ready_thermal_process_spec())
    assert verdict.ready is True
    assert verdict.industry_id == "thermal_process_demo"
    assert verdict.missing_requirements == ()
    assert verdict.blocking_reasons == ()


# ── Incomplete specs ──────────────────────────────────────────────


def test_missing_process_taxonomy_blocks():
    spec = _ready_thermal_process_spec()
    spec["process_taxonomy"] = []
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "process_taxonomy" in v.missing_requirements


def test_missing_combinations_blocks():
    spec = _ready_thermal_process_spec()
    spec["combinations"] = []
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "combinations" in v.missing_requirements


def test_insufficient_tad_mapping_blocks():
    """TAD mapping requires ≥3 canonical actions."""
    spec = _ready_thermal_process_spec()
    spec["tad_mapping"] = ["VALIDATE_PROCESS_HEAT_DUTY"]  # only 1
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "tad_mapping" in v.missing_requirements


def test_empty_evidence_map_blocks():
    spec = _ready_thermal_process_spec()
    spec["evidence_map"] = {}
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "evidence_map" in v.missing_requirements


def test_evidence_map_with_empty_lists_blocks():
    """A hypothesis with no evidence is the same as no evidence."""
    spec = _ready_thermal_process_spec()
    spec["evidence_map"] = {"boiler_degradation": []}
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "evidence_map" in v.missing_requirements


def test_missing_financial_translation_blocks():
    spec = _ready_thermal_process_spec()
    spec["financial_translation"] = ""
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "financial_translation" in v.missing_requirements


def test_missing_qa_tests_blocks():
    spec = _ready_thermal_process_spec()
    spec["qa_tests"] = []
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert "qa_tests" in v.missing_requirements


# ── Multiple gaps ────────────────────────────────────────────────


def test_multiple_gaps_all_listed():
    spec = _ready_thermal_process_spec()
    spec["combinations"] = []
    spec["tad_mapping"] = []
    spec["qa_tests"] = []
    v = validate_industry_readiness(spec)
    assert v.ready is False
    assert set(v.missing_requirements) == {"combinations", "tad_mapping", "qa_tests"}
    assert len(v.blocking_reasons) == 3


# ── IndustrySpec dataclass acceptance ─────────────────────────────


def test_industryspec_dataclass_accepted():
    spec = IndustrySpec(
        industry_id="x",
        process_taxonomy=("a",), machine_taxonomy=("b",),
        dominant_variables=("v",), failure_modes=("f",),
        evidence_map={"h": ("e",)},
        financial_translation="...",
        regulatory_triggers=(), combinations=("c",),
        tad_mapping=("T1", "T2", "T3"),
        qa_tests=("t1",),
    )
    v = validate_industry_readiness(spec)
    assert v.ready is True


# ── Aggregated summary ───────────────────────────────────────────


def test_summary_counts_ready_and_incomplete():
    ready_v = validate_industry_readiness(_ready_thermal_process_spec())
    spec_bad = _ready_thermal_process_spec()
    spec_bad["industry_id"] = "incomplete_demo"
    spec_bad["combinations"] = []
    bad_v = validate_industry_readiness(spec_bad)
    summary = industry_onboarding_summary([ready_v, bad_v])
    assert summary["industry_count"] == 2
    assert summary["ready_count"] == 1
    assert summary["incomplete_count"] == 1
    assert summary["incomplete_industries"] == ["incomplete_demo"]
