"""V5 P12 — Phase 6 depth tests.

Verifies that `to_compliance_applicability_case_register` now consumes
the richer `regulatory_physics_register` from motor_053 and STRUCTURALLY
populates jurisdiction, rule_family, applicability_state, publication_ceiling.
"""
from __future__ import annotations

from runtime_orchestrator.phase_units import (
    _map_evidence_state_to_applicability,
    _parse_jurisdiction,
    _publication_ceiling_phase6,
    to_compliance_applicability_case_register,
)


# ── Jurisdiction parsing ────────────────────────────────────────────


def test_parse_jurisdiction_nyc():
    assert _parse_jurisdiction("NYC benchmarking and building performance") == "US/NY/NYC"


def test_parse_jurisdiction_epa():
    assert _parse_jurisdiction("EPA Clean Air Act applicability") == "US/Federal/EPA"


def test_parse_jurisdiction_california():
    assert _parse_jurisdiction("California Title 24 efficiency standards") == "US/CA"


def test_parse_jurisdiction_falls_through():
    assert _parse_jurisdiction("Some unrelated text about widgets") == ""


def test_parse_jurisdiction_empty_input():
    assert _parse_jurisdiction("") == ""
    assert _parse_jurisdiction(None) == ""  # type: ignore[arg-type]


# ── evidence_state → applicability mapping ──────────────────────────


def test_observed_fact_maps_to_trigger_confirmed():
    assert _map_evidence_state_to_applicability("OBSERVED_FACT") == "trigger_confirmed"


def test_conditional_hypothesis_maps_to_trigger_plausible():
    assert _map_evidence_state_to_applicability("CONDITIONAL_HYPOTHESIS") == "trigger_plausible"


def test_weak_signal_maps_to_trigger_plausible():
    assert _map_evidence_state_to_applicability("WEAK_SIGNAL") == "trigger_plausible"


def test_archetypal_prior_maps_to_rule_family_relevant():
    assert _map_evidence_state_to_applicability("ARCHETYPAL_PRIOR") == "rule_family_relevant"


def test_unknown_state_defaults_to_rule_family_relevant():
    assert _map_evidence_state_to_applicability("") == "rule_family_relevant"
    assert _map_evidence_state_to_applicability("XYZ") == "rule_family_relevant"


# ── publication_ceiling per applicability state ─────────────────────


def test_publication_ceiling_per_state():
    assert _publication_ceiling_phase6("rule_family_relevant") == "screening_only"
    assert _publication_ceiling_phase6("trigger_confirmed") == "decision_grade"
    assert _publication_ceiling_phase6("applicability_confirmed") == "bounded_compliance"
    assert _publication_ceiling_phase6("compliance_open") == "screening_only"


# ── End-to-end with regulatory_physics_register (V5 P12 path) ──────


def test_phase6_from_regulatory_physics_register_nyc():
    """A real motor_053 regulatory_physics_register row — NYC building
    performance — must produce a full Phase 6 case with jurisdiction,
    applicability state, and publication ceiling."""
    physics_register = [{
        "regulatory_signal": "NYC benchmarking and building performance obligations",
        "physical_implication": "Owner-facing compliance attaches to whole-building performance and can collide with unresolved tenant or control boundaries.",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
        "what_it_supports": ["screening-grade compliance context"],
        "what_it_does_not_support": ["compliance closure", "owner-capturable retrofit ROI"],
    }]
    out = to_compliance_applicability_case_register(
        regulatory_flag_bundle=None,
        regulatory_physics_register=physics_register,
        target_asset_family="commercial_building",
    )
    assert len(out) == 1
    row = out[0]
    assert row["jurisdiction"] == "US/NY/NYC"
    assert row["applicability_state"] == "trigger_plausible"
    assert row["publication_ceiling"] == "screening_only"
    assert row["asset_boundary"] == "commercial_building"
    assert "NYC" in row["rule_family"]
    assert any("compliance closure" in mtf for mtf in row["missing_trigger_fields"])
    assert row["__phase__"] == 6
    assert row["__canonical_unit__"] == "compliance_applicability_case"


def test_phase6_observed_fact_unlocks_trigger_confirmed():
    physics_register = [{
        "regulatory_signal": "EPA Clean Air Act stack monitoring",
        "physical_implication": "Stack monitoring is a confirmed regulatory obligation.",
        "evidence_state": "OBSERVED_FACT",
        "what_it_supports": ["regulatory closure pathway"],
        "what_it_does_not_support": [],
    }]
    out = to_compliance_applicability_case_register(
        regulatory_flag_bundle=None,
        regulatory_physics_register=physics_register,
    )
    row = out[0]
    assert row["jurisdiction"] == "US/Federal/EPA"
    assert row["applicability_state"] == "trigger_confirmed"
    assert row["publication_ceiling"] == "decision_grade"


def test_phase6_default_jurisdiction_when_unparsable():
    physics_register = [{
        "regulatory_signal": "Industrial environmental permit context",  # no jurisdiction token
        "physical_implication": "Permits imply combustion, thermal or emissions relevance.",
        "evidence_state": "CONDITIONAL_HYPOTHESIS",
    }]
    out = to_compliance_applicability_case_register(
        regulatory_flag_bundle=None,
        regulatory_physics_register=physics_register,
        default_jurisdiction="US",
    )
    assert out[0]["jurisdiction"] == "US"


def test_phase6_empty_inputs_return_empty_list():
    assert to_compliance_applicability_case_register(None) == []
    assert to_compliance_applicability_case_register([], regulatory_physics_register=[]) == []


# ── Backwards compat: regulatory_flag_bundle path still works ──────


def test_phase6_legacy_regulatory_flag_bundle_path():
    flags = [{
        "flag_id": "LL84-2024",
        "jurisdiction": "NYC",
        "rule_family": "LL84",
        "trigger_confirmed": True,
    }]
    out = to_compliance_applicability_case_register(flags)
    assert len(out) == 1
    assert out[0]["applicability_state"] == "trigger_confirmed"
    assert out[0]["jurisdiction"] == "NYC"


def test_phase6_legacy_flag_default_jurisdiction():
    """When legacy flag has no jurisdiction field, default applies."""
    flags = [{
        "flag_id": "x",
        "rule_family": "X",
    }]
    out = to_compliance_applicability_case_register(flags, default_jurisdiction="US")
    assert out[0]["jurisdiction"] == "US"


def test_phase6_both_paths_merged_in_output():
    """When BOTH inputs provided, projection emits rows from both."""
    physics_register = [{
        "regulatory_signal": "NYC benchmarking",
        "physical_implication": "...",
        "evidence_state": "OBSERVED_FACT",
    }]
    flags = [{
        "flag_id": "LL97-2024",
        "rule_family": "LL97",
        "missing_trigger_fields": ["gross_floor_area"],
    }]
    out = to_compliance_applicability_case_register(
        flags,
        regulatory_physics_register=physics_register,
        target_asset_family="commercial_building",
    )
    assert len(out) == 2
    sources = {row["authority_source"] for row in out}
    assert "regulatory_physics_register" in sources  # the V5 P12 row
