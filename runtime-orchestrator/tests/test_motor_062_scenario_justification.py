"""Tests for motor_062 — Scenario Justification Validator (Layer F).

Validates that every active scenario in scenario_space carries the 5
required justification fields per RECOVERY_2026-05-10 §11.B.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_062 import Motor062Adapter


def _run(motor_007=None, motor_014=None, motor_047=None, pipeline=None):
    adapter = Motor062Adapter()
    return adapter.run({
        "motor_007": motor_007 or {},
        "motor_014": motor_014 or {},
        "motor_047": motor_047 or {},
        "__pipeline__": pipeline or {},
    })


def _scenario(plausibility="Plausible but unsupported", **extras):
    base = {
        "scenario": "A. Energy intensity is structurally tied to throughput",
        "plausibility_status": plausibility,
        "financial_meaning": "Bounded upside",
        "what_would_make_it_true": "Operating evidence",
        "what_would_falsify_it": "Controls dominate",
        "evidence_needed": "Operating schedule",
    }
    base.update(extras)
    return base


_FULL_JUSTIFICATION = {
    "trigger": "Utility bill shows night baseload at 60% of peak",
    "source": "DOE Better Plants 2023 baseline study",
    "process_clue": "Refrigeration duty cycles continuously regardless of throughput",
    "industrial_reason": "Refrigeration is the dominant load in cold-chain assets",
    "asset_family_reason": "Cold-chain facility — refrigeration is structural",
}


# ── Baseline behavior ────────────────────────────────────────────────────────


def test_no_inputs_returns_no_warnings():
    out = _run()
    assert out["warning_count"] == 0
    assert out["scenario_justification_failed"] is False
    assert out["total_scenario_count"] == 0


def test_active_scenario_missing_all_fields_emits_critical_warning():
    out = _run(motor_014={"scenario_space": [_scenario()]})
    assert out["warning_count"] == 1
    assert out["critical_count"] == 1
    assert out["active_scenario_count"] == 1
    warn = out["scenario_justification_warnings"][0]
    assert warn["severity"] == "critical"
    assert set(warn["missing_fields"]) == {
        "trigger",
        "source",
        "process_clue",
        "industrial_reason",
        "asset_family_reason",
    }


def test_active_scenario_with_full_justification_passes():
    out = _run(motor_014={"scenario_space": [_scenario(**_FULL_JUSTIFICATION)]})
    assert out["warning_count"] == 0
    assert out["critical_count"] == 0
    assert out["scenario_justification_failed"] is False


def test_partial_justification_emits_non_critical_warning():
    partial = {"trigger": "x", "source": "y"}  # 3 missing
    out = _run(motor_014={"scenario_space": [_scenario(**partial)]})
    assert out["warning_count"] == 1
    assert out["critical_count"] == 0
    warn = out["scenario_justification_warnings"][0]
    assert warn["severity"] == "warning"
    assert set(warn["missing_fields"]) == {
        "process_clue",
        "industrial_reason",
        "asset_family_reason",
    }


# ── Active vs inactive scenarios ─────────────────────────────────────────────


def test_falsified_scenario_excluded_from_audit():
    out = _run(motor_014={"scenario_space": [
        _scenario(plausibility="Falsified by current evidence"),
        _scenario(plausibility="Reduced"),
    ]})
    assert out["warning_count"] == 0
    assert out["active_scenario_count"] == 0
    assert out["total_scenario_count"] == 2


def test_currently_dominant_scenario_is_active():
    out = _run(motor_014={"scenario_space": [
        _scenario(plausibility="Currently dominant"),
    ]})
    assert out["active_scenario_count"] == 1
    assert out["warning_count"] == 1


def test_possible_and_not_ruled_out_are_active():
    out = _run(motor_014={"scenario_space": [
        _scenario(plausibility="Possible but unsupported"),
        _scenario(plausibility="Not ruled out"),
    ]})
    assert out["active_scenario_count"] == 2
    assert out["warning_count"] == 2


# ── Fallback to motor_047 ────────────────────────────────────────────────────


def test_falls_back_to_motor_047_scenario_register_when_m014_missing():
    out = _run(motor_047={
        "executive_thesis": {
            "scenario_register": [_scenario()],
        }
    })
    assert out["total_scenario_count"] == 1
    assert out["warning_count"] == 1


# ── Mode toggle (warn vs block) ──────────────────────────────────────────────


def test_default_mode_is_warn_and_does_not_block():
    scenarios = [_scenario() for _ in range(5)]  # 5 critical
    out = _run(motor_014={"scenario_space": scenarios})
    assert out["mode"] == "warn"
    assert out["critical_count"] == 5
    assert out["scenario_justification_failed"] is False


def test_block_mode_above_threshold_marks_failed():
    scenarios = [_scenario() for _ in range(3)]  # exactly threshold
    out = _run(
        motor_014={"scenario_space": scenarios},
        pipeline={"scenario_justification_mode": "block"},
    )
    assert out["mode"] == "block"
    assert out["scenario_justification_failed"] is True


def test_block_mode_below_threshold_does_not_fail():
    scenarios = [_scenario() for _ in range(2)]  # below threshold
    out = _run(
        motor_014={"scenario_space": scenarios},
        pipeline={"scenario_justification_mode": "block"},
    )
    assert out["mode"] == "block"
    assert out["scenario_justification_failed"] is False


# ── Asset family threading ───────────────────────────────────────────────────


def test_asset_family_is_threaded_into_warnings():
    out = _run(
        motor_007={"target_definition_contract": {"asset_family": "cold_chain_facility"}},
        motor_014={"scenario_space": [_scenario()]},
    )
    assert out["asset_family_evaluated"] == "cold_chain_facility"
    assert out["scenario_justification_warnings"][0]["asset_family"] == "cold_chain_facility"
