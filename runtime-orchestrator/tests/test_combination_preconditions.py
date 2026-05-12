"""Tests for V3 G8: build_combination_activation_register honors preconditions.

A combination_spec.preconditions list (v2 schema) requires every listed
pattern_id to be in bounded_pattern_ids before the combination activates.
Unbounded preconditions hold the combination as latent.
"""
from __future__ import annotations

from runtime_orchestrator.zlab_skill.combination_engine import (
    build_combination_activation_register,
)


def _spec(combo_id="combo_x", pattern_ids=("p_a", "p_b"), preconditions=None, anti_triggers=()):
    s = {
        "id": combo_id,
        "name": combo_id,
        "pattern_ids": list(pattern_ids),
        "trigger_logic": ["t"],
        "anti_triggers": list(anti_triggers),
        "combined_hypothesis": "h",
        "strategic_risk": "r",
        "minimum_evidence": ["e"],
        "financial_exposure": ["x"],
        "tad_action": "VALIDATE_LOSS_PATTERN",
        "prohibited_claims": ["bad"],
        "allowed_language": "ok",
        "source_basis": ["src"],
        "confidence_ceiling": "L2",
        "adjudication_required": True,
        "tests": ["t"],
    }
    if preconditions is not None:
        s["preconditions"] = list(preconditions)
    return s


def _bundle(*specs):
    return {"combinations": list(specs)}


# ── No preconditions (V1/V2 retro-compat) ──────────────────────────────


def test_combination_without_preconditions_activates_normally():
    rows = build_combination_activation_register(
        registry_bundle=_bundle(_spec("c1")),
        active_pattern_ids=["p_a", "p_b"],
    )
    assert len(rows) == 1
    assert rows[0]["activation_state"] == "candidate"
    assert rows[0]["preconditions_state"] == "n/a"
    assert rows[0]["validator_state"] == "not_run"


# ── Preconditions present, all bounded ─────────────────────────────────


def test_satisfied_preconditions_let_combination_activate():
    rows = build_combination_activation_register(
        registry_bundle=_bundle(_spec("c2", preconditions=["thermal_duty", "uptime_econ"])),
        active_pattern_ids=["p_a", "p_b"],
        bounded_pattern_ids=["thermal_duty", "uptime_econ"],
    )
    assert len(rows) == 1
    assert rows[0]["activation_state"] == "candidate"
    assert rows[0]["preconditions_state"] == "satisfied"
    assert rows[0]["preconditions_unbounded"] == []


# ── Preconditions present, NOT all bounded ─────────────────────────────


def test_unbounded_precondition_holds_combination_as_latent():
    rows = build_combination_activation_register(
        registry_bundle=_bundle(_spec("c3", preconditions=["thermal_duty", "uptime_econ"])),
        active_pattern_ids=["p_a", "p_b"],
        bounded_pattern_ids=["thermal_duty"],  # uptime_econ NOT bounded
    )
    assert len(rows) == 1
    assert rows[0]["activation_state"] == "latent"
    assert rows[0]["validator_state"] == "precondition_unbounded"
    assert rows[0]["preconditions_state"] == "unbounded"
    assert rows[0]["preconditions_unbounded"] == ["uptime_econ"]


def test_no_preconditions_bounded_holds_combination_as_latent():
    rows = build_combination_activation_register(
        registry_bundle=_bundle(_spec("c4", preconditions=["thermal_duty"])),
        active_pattern_ids=["p_a", "p_b"],
        bounded_pattern_ids=[],  # nothing bounded
    )
    # Empty bounded_pattern_ids → unevaluable state
    assert rows[0]["preconditions_state"] == "unevaluable"
    assert rows[0]["validator_state"] == "precondition_unevaluable"
    assert rows[0]["activation_state"] == "candidate"


# ── Preconditions ignored when bounded_pattern_ids not passed ──────────


def test_bounded_pattern_ids_default_none_unevaluable():
    """Callers that don't pass bounded_pattern_ids see preconditions as
    unevaluable — the combination is still emitted, just flagged."""
    rows = build_combination_activation_register(
        registry_bundle=_bundle(_spec("c5", preconditions=["thermal_duty"])),
        active_pattern_ids=["p_a", "p_b"],
    )
    assert rows[0]["preconditions_state"] == "unevaluable"
    assert rows[0]["activation_state"] == "candidate"


# ── Preconditions case-insensitive normalization ───────────────────────


def test_preconditions_normalized_lowercase():
    rows = build_combination_activation_register(
        registry_bundle=_bundle(_spec("c6", preconditions=["Thermal_Duty"])),
        active_pattern_ids=["p_a", "p_b"],
        bounded_pattern_ids=["THERMAL_DUTY"],
    )
    assert rows[0]["preconditions_state"] == "satisfied"


# ── Mixed bundle: one combo unblocked, one held latent ─────────────────


def test_mixed_bundle_one_active_one_latent():
    bundle = _bundle(
        _spec("active_combo"),  # no preconditions
        _spec("latent_combo", preconditions=["uptime_econ"]),
    )
    rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=["p_a", "p_b"],
        bounded_pattern_ids=["thermal_duty"],  # uptime_econ NOT bounded
    )
    states = {r["combination_id"]: r["activation_state"] for r in rows}
    assert states["active_combo"] == "candidate"
    assert states["latent_combo"] == "latent"


# ── Real 4 approved combinations still work (no preconditions declared) ─


def test_existing_4_combinations_activate_without_preconditions_field():
    from runtime_orchestrator.zlab_skill.loader import load_registry_bundle
    bundle = load_registry_bundle()
    # All 4 existing combinations have no preconditions field → no holds
    all_active_patterns = set()
    for combo in bundle.get("combinations", []):
        all_active_patterns.update(combo.get("pattern_ids", []))
    rows = build_combination_activation_register(
        registry_bundle=bundle,
        active_pattern_ids=list(all_active_patterns),
    )
    # All 4 combinations should be candidates (no precondition gating)
    assert len(rows) == 4
    assert all(r["activation_state"] == "candidate" for r in rows)
    assert all(r["preconditions_state"] == "n/a" for r in rows)
