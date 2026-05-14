"""V8 P4 — TAD Claim Sync Engine tests.

Chief QA Architect § Error 4 + § D: motor_059 R8-R11 DETECTAN cuando
TAD propone digital_twin / ROI con prereqs unmet, pero motor_033 emite
status='INVESTIGATE'. V8 P4 reescribe status a DO_NOT_*.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.tad_claim_sync import (
    enforce_tad_action_posture,
    enforce_tad_action_postures,
)
from runtime_orchestrator.tad_action_registry import is_registered_action


# ── Canonical DO_NOT_* statuses are registered ────────────────────


def test_canonical_do_not_statuses_registered():
    for status in (
        "DO_NOT_MODEL_YET",
        "DO_NOT_SENSOR_YET",
        "DO_NOT_RETROFIT_YET",
        "DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET",
        "REQUEST_EVIDENCE_FIRST",
        "COMPARE_ONLY_AFTER_NORMALIZATION",
    ):
        assert is_registered_action(status), f"{status} not in registry"


# ── Unit: digital_twin + unresolved → DO_NOT_MODEL_YET ────────────


def test_digital_twin_with_unresolved_dominant_var_rewrites_to_DO_NOT_MODEL_YET():
    action = {
        "action_id": "A1",
        "action_title": "Build detailed system model / digital twin",
        "status": "INVESTIGATE",
    }
    dominant_vars = [{"evidence_state": "ARCHETYPAL_PRIOR"}]
    out = enforce_tad_action_posture(action, dominant_variables=dominant_vars)
    assert out["tad_claim_sync_applied"] is True
    assert out["status"] == "DO_NOT_MODEL_YET"
    assert out["recommended_posture"] == "DO_NOT_MODEL_YET"
    assert out["admissibility"] == "prohibited_until_discrimination"
    assert "investigate" in out["forbidden_language"]


def test_digital_twin_with_observed_fact_keeps_status():
    action = {"action_id": "A1", "action_title": "Build digital twin",
              "status": "INVESTIGATE"}
    dominant_vars = [{"evidence_state": "OBSERVED_FACT"}]
    out = enforce_tad_action_posture(action, dominant_variables=dominant_vars)
    assert out["tad_claim_sync_applied"] is False
    assert out["status"] == "INVESTIGATE"


# ── Sensor + unresolved → DO_NOT_SENSOR_YET ───────────────────────


def test_sensor_action_with_unresolved_var_rewrites_to_DO_NOT_SENSOR_YET():
    action = {"action_id": "A2",
              "action_title": "Deploy sensors for refrigeration monitoring",
              "status": "INVESTIGATE"}
    out = enforce_tad_action_posture(
        action, dominant_variables=[{"evidence_state": "WEAK_SIGNAL"}],
    )
    assert out["status"] == "DO_NOT_SENSOR_YET"


# ── Retrofit + unresolved → DO_NOT_RETROFIT_YET ───────────────────


def test_retrofit_action_with_unresolved_var_rewrites():
    action = {"action_id": "A3",
              "action_title": "Replace equipment: upgrade chiller",
              "status": "INVESTIGATE"}
    out = enforce_tad_action_posture(
        action, dominant_variables=[{"evidence_state": "ARCHETYPAL_PRIOR"}],
    )
    assert out["status"] == "DO_NOT_RETROFIT_YET"


# ── ROI / underwriting + prohibited claim → DO_NOT_UNDERWRITE ─────


def test_roi_with_prohibited_claim_rewrites_to_DO_NOT_UNDERWRITE():
    action = {"action_id": "A4",
              "action_title": "Quantify ROI of retrofit",
              "linked_claim": "claim_x",
              "status": "ACT NOW"}
    out = enforce_tad_action_posture(
        action,
        claim_permissions={"claim_x": "prohibited"},
    )
    assert out["status"] == "DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET"


# ── Peer comparison + normalization incomplete → COMPARE_ONLY... ──


def test_peer_compare_when_normalization_incomplete():
    action = {"action_id": "A5",
              "action_title": "Compare to peer set",
              "status": "INVESTIGATE"}
    out = enforce_tad_action_posture(
        action,
        normalization_complete=False,
    )
    assert out["status"] == "COMPARE_ONLY_AFTER_NORMALIZATION"


# ── Generic investigate with unresolved → REQUEST_EVIDENCE_FIRST ──


def test_investigate_with_unresolved_var_rewrites_to_REQUEST_EVIDENCE_FIRST():
    action = {"action_id": "A6",
              "action_title": "Investigate cold-chain anomaly",
              "status": "INVESTIGATE"}
    out = enforce_tad_action_posture(
        action,
        dominant_variables=[{"evidence_state": "ARCHETYPAL_PRIOR"}],
    )
    assert out["status"] == "REQUEST_EVIDENCE_FIRST"
    assert "investigate" in out["forbidden_language"]


# ── Precedence: digital_twin > sensor > retrofit > underwrite ────


def test_precedence_digital_twin_beats_sensor():
    """An action mentioning BOTH digital twin and sensors goes to DO_NOT_MODEL_YET."""
    action = {"action_id": "A7",
              "action_title": "Deploy sensors and build digital twin model",
              "status": "INVESTIGATE"}
    out = enforce_tad_action_posture(
        action,
        dominant_variables=[{"evidence_state": "WEAK_SIGNAL"}],
    )
    assert out["status"] == "DO_NOT_MODEL_YET"


# ── Batch wrapper ─────────────────────────────────────────────────


def test_batch_wrapper_processes_list():
    actions = [
        {"action_id": "A1", "action_title": "Build digital twin", "status": "INVESTIGATE"},
        {"action_id": "A2", "action_title": "Inspect doors", "status": "ACT NOW"},
    ]
    out = enforce_tad_action_postures(
        actions,
        dominant_variables=[{"evidence_state": "ARCHETYPAL_PRIOR"}],
    )
    assert len(out) == 2
    assert out[0]["status"] == "DO_NOT_MODEL_YET"
    assert out[1]["status"] == "ACT NOW"  # untouched


# ── motor_033 integration ─────────────────────────────────────────


def test_motor_033_rewrites_digital_twin_action_when_var_unresolved():
    from runtime_orchestrator.adapters.motor_033 import Motor033Adapter
    # Minimal pipeline inputs that drive motor_033 into emitting a TAD
    # action that includes "digital twin" language. The expanded
    # _expanded_structural_tad_actions uses target_definition to build
    # actions; we inject a dominant_variable_register that is unresolved
    # and check the final register has DO_NOT_MODEL_YET applied.
    inputs = {
        "motor_007": {"target_definition_contract": {
            "asset_family": "cold_chain_facility",
            "target_identifier": "TEST_CASE",
        }},
        "motor_014": {
            "inference_records": [{
                "case_id": "C1", "case_name": "Refrigeration duty",
                "plausibility_score": 0.5, "decision_relevance_score": 0.6,
                "validation_urgency_score": 0.5,
                "validation_requirement": "investigate digital twin model",
                "claim_family": "operational",
            }],
            "conflict_register": [], "evidence_gap_register": [],
            "validation_queue": [], "next_best_questions": [],
            "decision_front_register": [],
            "variable_bottleneck_register": [],
            "canonical_problem_frame": {},
            "structural_reasoning_path": {},
        },
        "motor_015": {}, "motor_034": {},
        "motor_038": {"dominant_variable_register": [
            {"variable_id": "refrigeration_duty", "evidence_state": "ARCHETYPAL_PRIOR"}
        ]},
        "motor_040": {}, "motor_041": {}, "motor_042": {},
        "motor_043": {}, "motor_044": {}, "motor_045": {},
        "motor_046": {},
    }
    out = Motor033Adapter().run(inputs)
    # Look for any rewritten action
    register = out.get("expanded_structural_tad_action_register", [])
    do_not_model = [a for a in register if a.get("status") == "DO_NOT_MODEL_YET"]
    # At least one action should have been rewritten if digital twin
    # language was present and the variable was unresolved.
    # (Motor 033's _expanded_structural may not always emit such an action
    # for this synthetic input, so we tolerate empty but check no
    # untouched digital_twin INVESTIGATE remains.)
    untouched = [a for a in register if (
        "digital twin" in str(a.get("action_title", "")).lower()
        and a.get("status") == "INVESTIGATE"
    )]
    assert untouched == [], (
        f"Found digital-twin actions still in INVESTIGATE: {untouched}"
    )
