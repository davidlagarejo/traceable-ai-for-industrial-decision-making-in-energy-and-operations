"""Tests for V3 G6: Report State Machine.

Verifies the 8 formal states + strict client_safe gate + state derivation
from motor outputs.
"""
from __future__ import annotations

import pytest

from runtime_orchestrator.report_state_machine import (
    DEFAULT_ALLOWED_RENDER_STATES,
    ReportStateDiagnosis,
    STATES,
    derive_state,
    diagnosis_from_motor_outputs,
)


# ── Schema integrity ────────────────────────────────────────────────────


def test_states_constant_includes_all_8_states():
    expected = {
        "exploratory_prior", "structural_hypothesis", "bounded_peer_analysis",
        "evidence_discrimination", "decision_blocked", "publish_bounded",
        "client_safe", "internal_debug_only",
    }
    assert set(STATES) == expected


def test_default_render_gate_only_allows_client_safe():
    """Strict default per user decision: only client_safe renders."""
    assert DEFAULT_ALLOWED_RENDER_STATES == ("client_safe",)


# ── Terminal contamination states ───────────────────────────────────────


def test_family_contamination_routes_to_internal_debug_only():
    diag = ReportStateDiagnosis(contamination_detected=True)
    out = derive_state(diag)
    assert out.state == "internal_debug_only"
    assert out.can_render is False  # default gate excludes internal_debug
    assert "asset_family_contamination_detected" in out.signals


def test_chart_contamination_routes_to_internal_debug_only():
    diag = ReportStateDiagnosis(chart_contamination_detected=True)
    out = derive_state(diag)
    assert out.state == "internal_debug_only"
    assert out.can_render is False


def test_contamination_overrides_otherwise_green_state():
    """Even if every other validator is clean, contamination wins."""
    diag = ReportStateDiagnosis(
        contamination_detected=True,
        nugget_count=8,
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        total_warning_count=0,
    )
    out = derive_state(diag)
    assert out.state == "internal_debug_only"


# ── Decision-blocked states ─────────────────────────────────────────────


def test_consistency_failure_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(can_render_pdf=False, consistency_critical_failures=2)
    out = derive_state(diag)
    assert out.state == "decision_blocked"
    assert "consistency_critical_failures" in out.signals


def test_strategic_intelligence_error_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(strategic_intelligence_error_count=1)
    out = derive_state(diag)
    assert out.state == "decision_blocked"


def test_scenario_review_pending_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(scenario_review_ready=False, scenario_review_pending_count=3)
    out = derive_state(diag)
    assert out.state == "decision_blocked"
    assert "scenario_review_pending" in out.signals
    assert "3 scenarios" in out.reason


def test_duplicate_claim_signature_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(duplicate_claim_signature=True)
    out = derive_state(diag)
    assert out.state == "decision_blocked"


def test_evidence_pack_repetition_above_threshold_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(pack_repetition_count=2)
    out = derive_state(diag)
    assert out.state == "decision_blocked"


def test_evidence_pack_single_repetition_does_not_block():
    """Threshold is >=2."""
    diag = ReportStateDiagnosis(
        pack_repetition_count=1,
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        nugget_count=8,
    )
    out = derive_state(diag)
    assert out.state in ("client_safe", "publish_bounded")


def test_archetype_replay_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(archetype_replay=True)
    out = derive_state(diag)
    assert out.state == "decision_blocked"


def test_verbatim_nugget_reuse_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(verbatim_nugget_reuse=True)
    out = derive_state(diag)
    assert out.state == "decision_blocked"


def test_scenario_justification_failed_routes_to_decision_blocked():
    diag = ReportStateDiagnosis(scenario_justification_failed=True)
    out = derive_state(diag)
    assert out.state == "decision_blocked"


# ── In-progress states (insufficient evidence, no failure) ─────────────


def test_low_cluster_count_routes_to_exploratory_prior():
    diag = ReportStateDiagnosis(cluster_count=2, minimum_cluster_count_for_peer_analysis=3)
    out = derive_state(diag)
    assert out.state == "exploratory_prior"


def test_unvalidated_peer_set_routes_to_structural_hypothesis():
    diag = ReportStateDiagnosis(
        cluster_count=4,
        minimum_cluster_count_for_peer_analysis=3,
        peer_set_valid=False,
    )
    out = derive_state(diag)
    assert out.state == "structural_hypothesis"


def test_peer_set_valid_but_evidence_pack_not_ready_routes_to_bounded_peer_analysis():
    diag = ReportStateDiagnosis(
        cluster_count=4,
        peer_set_valid=True,
        minimum_evidence_pack_ready=False,
    )
    out = derive_state(diag)
    assert out.state == "bounded_peer_analysis"


def test_evidence_pack_ready_but_clusters_below_discrimination_threshold():
    diag = ReportStateDiagnosis(
        cluster_count=4,
        minimum_cluster_count_for_discrimination=5,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
    )
    out = derive_state(diag)
    assert out.state == "evidence_discrimination"


# ── Green states ────────────────────────────────────────────────────────


def test_fully_clean_with_nugget_in_range_is_client_safe():
    diag = ReportStateDiagnosis(
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        nugget_count=8,
        total_warning_count=0,
    )
    out = derive_state(diag)
    assert out.state == "client_safe"
    assert out.can_render is True
    assert "all_validators_clean" in out.signals


def test_warnings_present_routes_to_publish_bounded_not_client_safe():
    diag = ReportStateDiagnosis(
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        nugget_count=8,
        total_warning_count=5,
    )
    out = derive_state(diag)
    assert out.state == "publish_bounded"
    # Default gate doesn't allow publish_bounded
    assert out.can_render is False


def test_nugget_count_outside_range_routes_to_publish_bounded():
    diag = ReportStateDiagnosis(
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        nugget_count=2,  # < min of 5
        total_warning_count=0,
    )
    out = derive_state(diag)
    assert out.state == "publish_bounded"
    assert "nugget_count=2_outside_[5,12]" in out.signals


def test_nugget_count_too_high_routes_to_publish_bounded():
    diag = ReportStateDiagnosis(
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        nugget_count=20,
        total_warning_count=0,
    )
    out = derive_state(diag)
    assert out.state == "publish_bounded"


# ── Configurable render gate ────────────────────────────────────────────


def test_caller_can_widen_render_gate():
    """Pipeline can opt into accepting publish_bounded for render."""
    diag = ReportStateDiagnosis(
        cluster_count=10,
        peer_set_valid=True,
        minimum_evidence_pack_ready=True,
        nugget_count=8,
        total_warning_count=5,
    )
    out = derive_state(diag, allowed_render_states=("client_safe", "publish_bounded"))
    assert out.state == "publish_bounded"
    assert out.can_render is True


# ── diagnosis_from_motor_outputs ────────────────────────────────────────


def test_diagnosis_builder_extracts_contamination_signals():
    motor_outputs = {
        "motor_061": {"contamination_detected": True, "warning_count": 1},
        "motor_063": {"chart_contamination_detected": False, "warning_count": 0},
    }
    diag = diagnosis_from_motor_outputs(motor_outputs)
    assert diag.contamination_detected is True
    out = derive_state(diag)
    assert out.state == "internal_debug_only"


def test_diagnosis_builder_aggregates_total_warnings():
    motor_outputs = {
        "motor_055": {"warning_count": 2},
        "motor_056": {"warning_count": 1},
        "motor_057": {"warning_count": 1, "nugget_count_evaluated": 6},
        "motor_058": {"warning_count": 0},
        "motor_059": {"warning_count": 0, "warning_count_by_severity": {"error": 0}},
        "motor_061": {"warning_count": 0},
        "motor_062": {"warning_count": 0},
        "motor_063": {"warning_count": 0},
    }
    diag = diagnosis_from_motor_outputs(motor_outputs)
    assert diag.total_warning_count == 4


def test_diagnosis_builder_extracts_strategic_intelligence_errors():
    motor_outputs = {
        "motor_059": {
            "warning_count": 3,
            "warning_count_by_severity": {"error": 2, "warning": 1, "info": 0},
        },
    }
    diag = diagnosis_from_motor_outputs(motor_outputs)
    assert diag.strategic_intelligence_error_count == 2
    out = derive_state(diag)
    assert out.state == "decision_blocked"


def test_diagnosis_builder_extracts_scenario_review_readiness():
    motor_outputs = {
        "scenario_review_summary": {"ready_to_render": False, "pending_count": 4},
    }
    diag = diagnosis_from_motor_outputs(motor_outputs)
    assert diag.scenario_review_ready is False
    assert diag.scenario_review_pending_count == 4


def test_diagnosis_builder_handles_missing_keys():
    """An empty motor_outputs should default to all-clean assumption."""
    diag = diagnosis_from_motor_outputs({})
    assert diag.contamination_detected is False
    assert diag.total_warning_count == 0
    assert diag.scenario_review_ready is True
