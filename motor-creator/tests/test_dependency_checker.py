"""Tests for dependency_checker module."""
from __future__ import annotations

import pytest

from motor_creator.dependency_checker import check_motor_eligible, detect_cycles, get_eligible_motors
from motor_creator.models import MotorStatus

from conftest import make_entry, make_state


# ─── cycle detection ──────────────────────────────────────────────────────

def test_no_cycles_simple_chain():
    motors = {
        "m1": make_entry("m1", requires=[]),
        "m2": make_entry("m2", requires=["m1"]),
        "m3": make_entry("m3", requires=["m2"]),
    }
    assert detect_cycles(motors) == []


def test_detects_direct_cycle():
    motors = {
        "m1": make_entry("m1", requires=["m2"]),
        "m2": make_entry("m2", requires=["m1"]),
    }
    cycles = detect_cycles(motors)
    assert "m1" in cycles
    assert "m2" in cycles


def test_detects_indirect_cycle():
    motors = {
        "m1": make_entry("m1", requires=[]),
        "m2": make_entry("m2", requires=["m1", "m3"]),
        "m3": make_entry("m3", requires=["m2"]),
    }
    cycles = detect_cycles(motors)
    assert "m2" in cycles
    assert "m3" in cycles


def test_no_cycles_diamond():
    motors = {
        "m1": make_entry("m1", requires=[]),
        "m2": make_entry("m2", requires=["m1"]),
        "m3": make_entry("m3", requires=["m1"]),
        "m4": make_entry("m4", requires=["m2", "m3"]),
    }
    assert detect_cycles(motors) == []


# ─── check_motor_eligible ─────────────────────────────────────────────────

def test_eligible_no_dependencies():
    entry = make_entry("m1", requires=[])
    states = {"m1": make_state("m1")}
    result = check_motor_eligible(entry, states)
    assert result.eligible is True


def test_eligible_dependencies_satisfied():
    entry_m2 = make_entry("m2", requires=["m1"])
    states = {
        "m1": make_state("m1", status=MotorStatus.CLOSED, current_stage="closed", is_closed=True),
        "m2": make_state("m2"),
    }
    result = check_motor_eligible(entry_m2, states)
    assert result.eligible is True


def test_ineligible_dependency_not_closed():
    entry_m2 = make_entry("m2", requires=["m1"])
    states = {
        "m1": make_state("m1", status=MotorStatus.IN_PROGRESS),
        "m2": make_state("m2"),
    }
    result = check_motor_eligible(entry_m2, states)
    assert result.eligible is False
    assert "m1" in result.missing_deps[0]


def test_ineligible_dependency_not_started():
    entry_m2 = make_entry("m2", requires=["m1"])
    states = {
        "m1": make_state("m1", status=MotorStatus.NOT_STARTED),
        "m2": make_state("m2"),
    }
    result = check_motor_eligible(entry_m2, states)
    assert result.eligible is False


def test_ineligible_group_c_not_eligible():
    entry = make_entry("m26", group="C", orchestrator_eligible=False)
    states = {"m26": make_state("m26")}
    result = check_motor_eligible(entry, states)
    assert result.eligible is False
    assert "Group C" in result.reason


def test_eligible_group_c_when_promoted():
    entry = make_entry("m26", group="C", orchestrator_eligible=True, requires=[])
    states = {"m26": make_state("m26")}
    result = check_motor_eligible(entry, states)
    assert result.eligible is True


def test_ineligible_missing_state():
    entry = make_entry("m2", requires=["m1"])
    states = {}  # m1 has no state
    result = check_motor_eligible(entry, states)
    assert result.eligible is False


# ─── get_eligible_motors ──────────────────────────────────────────────────

def test_prefers_in_progress_over_not_started():
    m1 = make_entry("m1", requires=[])
    m2 = make_entry("m2", requires=[])
    s1_ip = make_state("m1", status=MotorStatus.IN_PROGRESS)
    s2_ns = make_state("m2", status=MotorStatus.NOT_STARTED)
    motors = {"m1": m1, "m2": m2}
    states = {"m1": s1_ip, "m2": s2_ns}

    eligible = get_eligible_motors(motors, states)
    assert eligible[0][0].motor_id == "m1"


def test_closed_motors_excluded_from_eligible():
    m1 = make_entry("m1", requires=[])
    s1 = make_state("m1", status=MotorStatus.CLOSED, current_stage="closed", is_closed=True)
    motors = {"m1": m1}
    states = {"m1": s1}

    eligible = get_eligible_motors(motors, states)
    assert eligible == []


def test_blocked_motors_excluded_from_eligible():
    m1 = make_entry("m1", requires=[])
    s1 = make_state("m1", status=MotorStatus.BLOCKED, blocked=True)
    motors = {"m1": m1}
    states = {"m1": s1}

    eligible = get_eligible_motors(motors, states)
    assert eligible == []
