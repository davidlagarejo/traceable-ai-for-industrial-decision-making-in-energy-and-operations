"""Tests for state_machine module."""
from __future__ import annotations

import pytest

from motor_creator.models import MotorStatus, Stage, STAGE_SEQUENCE
from motor_creator.state_machine import (
    advance_to_next_stage,
    is_final_stage,
    next_stage,
    open_correction,
    transition_to_blocked,
    transition_to_closed,
    transition_to_in_progress,
    transition_to_paused,
    transition_to_ready,
    validate_state,
)

from conftest import make_state


# ─── validate_state ──────────────────────────────────────────────────────

def test_valid_not_started():
    s = make_state(status=MotorStatus.NOT_STARTED)
    assert validate_state(s) == []


def test_valid_in_progress():
    s = make_state(status=MotorStatus.IN_PROGRESS)
    assert validate_state(s) == []


def test_valid_closed():
    s = make_state(
        status=MotorStatus.CLOSED,
        current_stage=Stage.CLOSED.value,
        is_closed=True,
    )
    assert validate_state(s) == []


def test_invalid_closed_wrong_stage():
    s = make_state(
        status=MotorStatus.CLOSED,
        current_stage=Stage.DOCUMENTATION_BASE.value,
        is_closed=True,
    )
    violations = validate_state(s)
    assert any("current_stage" in v for v in violations)


def test_invalid_blocked_and_paused():
    s = make_state(status=MotorStatus.BLOCKED, blocked=True, paused=True)
    violations = validate_state(s)
    assert any("blocked" in v and "paused" in v for v in violations)


def test_invalid_waiting_without_waiting_on():
    s = make_state(status=MotorStatus.WAITING, waiting_on=None)
    violations = validate_state(s)
    assert any("waiting_on is null" in v for v in violations)


def test_invalid_closed_with_blocked():
    s = make_state(
        status=MotorStatus.CLOSED,
        current_stage=Stage.CLOSED.value,
        is_closed=True,
        blocked=True,
    )
    violations = validate_state(s)
    assert len(violations) > 0


def test_invalid_closed_with_waiting_on():
    s = make_state(
        status=MotorStatus.CLOSED,
        current_stage=Stage.CLOSED.value,
        is_closed=True,
        waiting_on="something",
    )
    violations = validate_state(s)
    assert any("waiting_on" in v for v in violations)


# ─── next_stage ──────────────────────────────────────────────────────────

def test_next_stage_sequence():
    assert next_stage(Stage.DOCUMENTATION_BASE) == Stage.SCHEMA_TECHNICAL
    assert next_stage(Stage.SCHEMA_TECHNICAL) == Stage.TESTS
    assert next_stage(Stage.TESTS) == Stage.FAILURE_MODES
    assert next_stage(Stage.FAILURE_MODES) == Stage.IMPLEMENTATION
    assert next_stage(Stage.IMPLEMENTATION) == Stage.CONFORMANCE_REVIEW


def test_next_stage_final_returns_none():
    assert next_stage(Stage.CONFORMANCE_REVIEW) is None


def test_is_final_stage():
    assert is_final_stage(Stage.CONFORMANCE_REVIEW) is True
    assert is_final_stage(Stage.IMPLEMENTATION) is False


# ─── transitions ─────────────────────────────────────────────────────────

def test_transition_to_in_progress():
    s = make_state(status=MotorStatus.NOT_STARTED)
    s2 = transition_to_in_progress(s)
    assert s2.status == MotorStatus.IN_PROGRESS
    assert s2.blocked is False
    assert s2.paused is False


def test_advance_to_next_stage():
    s = make_state(
        status=MotorStatus.READY_FOR_NEXT_STAGE,
        current_stage=Stage.DOCUMENTATION_BASE.value,
    )
    s2 = advance_to_next_stage(s)
    assert s2.current_stage == Stage.SCHEMA_TECHNICAL.value
    assert Stage.DOCUMENTATION_BASE.value in s2.completed_stages
    assert s2.status == MotorStatus.IN_PROGRESS


def test_advance_does_not_skip_stages():
    s = make_state(current_stage=Stage.DOCUMENTATION_BASE.value)
    s2 = advance_to_next_stage(s)
    assert s2.current_stage == Stage.SCHEMA_TECHNICAL.value


def test_advance_from_final_raises():
    s = make_state(current_stage=Stage.CONFORMANCE_REVIEW.value)
    with pytest.raises(ValueError, match="final stage"):
        advance_to_next_stage(s)


def test_transition_to_closed():
    s = make_state(
        status=MotorStatus.READY_FOR_NEXT_STAGE,
        current_stage=Stage.CONFORMANCE_REVIEW.value,
    )
    s2 = transition_to_closed(s)
    assert s2.status == MotorStatus.CLOSED
    assert s2.current_stage == Stage.CLOSED.value
    assert s2.closure["is_closed"] is True
    assert s2.blocked is False
    assert s2.paused is False
    assert s2.waiting_on is None
    assert Stage.CONFORMANCE_REVIEW.value in s2.completed_stages


def test_transition_to_blocked():
    s = make_state(status=MotorStatus.IN_PROGRESS)
    s2 = transition_to_blocked(s, reason="dep not satisfied")
    assert s2.status == MotorStatus.BLOCKED
    assert s2.blocked is True
    assert any("dep not satisfied" in v.get("notes", "") for v in s2.validations)


def test_transition_to_paused():
    s = make_state(status=MotorStatus.IN_PROGRESS)
    s2 = transition_to_paused(s, waiting_on="manual_approval:gate_1")
    assert s2.status == MotorStatus.PAUSED
    assert s2.paused is True
    assert s2.waiting_on == "manual_approval:gate_1"


# ─── correction ──────────────────────────────────────────────────────────

def test_open_correction_schema_to_doc_base():
    s = make_state(
        current_stage=Stage.SCHEMA_TECHNICAL.value,
        completed_stages=[Stage.DOCUMENTATION_BASE.value],
    )
    s2 = open_correction(s, Stage.DOCUMENTATION_BASE, reason="ambiguous contract")
    assert s2.current_stage == Stage.DOCUMENTATION_BASE.value
    assert Stage.DOCUMENTATION_BASE.value not in s2.completed_stages
    assert len(s2.corrections) == 1
    assert s2.corrections[0]["status"] == "open"


def test_open_correction_invalid_path_raises():
    s = make_state(current_stage=Stage.DOCUMENTATION_BASE.value)
    with pytest.raises(ValueError, match="not a permitted correction path"):
        open_correction(s, Stage.IMPLEMENTATION, reason="bad jump")


def test_open_correction_removes_subsequent_completed_stages():
    s = make_state(
        current_stage=Stage.IMPLEMENTATION.value,
        completed_stages=[
            Stage.DOCUMENTATION_BASE.value,
            Stage.SCHEMA_TECHNICAL.value,
            Stage.TESTS.value,
            Stage.FAILURE_MODES.value,
        ],
    )
    s2 = open_correction(s, Stage.SCHEMA_TECHNICAL, reason="test revealed schema gap")
    assert Stage.DOCUMENTATION_BASE.value in s2.completed_stages
    assert Stage.SCHEMA_TECHNICAL.value not in s2.completed_stages
    assert Stage.TESTS.value not in s2.completed_stages
