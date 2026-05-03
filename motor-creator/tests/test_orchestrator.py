"""Integration tests for the orchestrator."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from motor_creator.models import MotorStatus, Stage
from motor_creator.orchestrator import Orchestrator

from conftest import make_entry, make_state, write_minimal_doc_base, write_artifact


def _make_deps_file(tmp_path: Path, motors: dict) -> Path:
    """Write a minimal motor_dependencies.json to tmp_path."""
    deps = {
        "_meta": {"description": "test", "validation_status": "confirmed", "last_updated": "2026-01-01"},
        "_rules": {},
        "motors": motors,
    }
    p = tmp_path / "motor_dependencies.json"
    p.write_text(json.dumps(deps))
    return p


def _make_governanza(tmp_path: Path) -> Path:
    g = tmp_path / "governanza"
    g.mkdir()
    return g


# ─── startup: cycle detection ─────────────────────────────────────────────

def test_orchestrator_aborts_on_cycle(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "M1", "group": "A", "catalog_status": "planned", "requires": ["motor_002"]},
        "motor_002": {"name": "M2", "group": "A", "catalog_status": "planned", "requires": ["motor_001"]},
    })
    gov = _make_governanza(tmp_path)
    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=True)
    result = orc.run_one("motor_001")
    assert result.action == "error"
    assert "cycle" in result.reason.lower()


# ─── motor blocked by dependency ─────────────────────────────────────────

def test_motor_blocked_by_unmet_dependency(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
        "motor_002": {"name": "Versioning Engine", "group": "A",
                      "catalog_status": "documented", "requires": ["motor_001"]},
    })
    gov = _make_governanza(tmp_path)
    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=True)
    # motor_001 is not_started (no state file), so motor_002 is blocked
    result = orc.run_one("motor_002")
    assert result.action == "blocked"
    assert "motor_001" in result.reason


# ─── eligible motor proceeds ──────────────────────────────────────────────

def test_motor_001_activates_no_dependencies(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
    })
    gov = _make_governanza(tmp_path)
    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=False)
    result = orc.run_one("motor_001")
    # Motor starts and creates placeholders; gate 1 will fail (empty artifacts)
    assert result.action in ("blocked", "advanced")
    assert result.motor_id == "motor_001"


# ─── motor advances through gate ─────────────────────────────────────────

def test_motor_advances_when_gate_passes(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
    })
    gov = _make_governanza(tmp_path)
    motor_dir = gov / make_entry("motor_001").slug
    motor_dir.mkdir(parents=True)

    # Pre-write valid doc_base artifacts so gate 1 passes automatically
    entry = make_entry("motor_001")
    write_minimal_doc_base(motor_dir, entry)

    # Write existing state as in_progress at doc_base
    state = make_state("motor_001", status=MotorStatus.IN_PROGRESS)
    state_path = motor_dir / "motor_state.json"
    state_path.write_text(json.dumps(state.to_dict()))

    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=False)
    result = orc.run_one("motor_001")

    # Gate 1 passes for automatic conditions but has manual check pending
    assert result.action in ("advanced", "paused")


# ─── Group C motor not eligible ───────────────────────────────────────────

def test_group_c_motor_not_eligible(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
        "motor_026": {"name": "Access Control Layer", "group": "C",
                      "catalog_status": "recommended", "requires": ["motor_001"],
                      "orchestrator_eligible": False},
    })
    gov = _make_governanza(tmp_path)
    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=True)
    result = orc.run_one("motor_026")
    assert result.action == "blocked"
    assert "Group C" in result.reason


# ─── invalid state is detected ───────────────────────────────────────────

def test_invalid_state_is_blocked(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
    })
    gov = _make_governanza(tmp_path)
    motor_dir = gov / make_entry("motor_001").slug
    motor_dir.mkdir(parents=True)

    # Write a deliberately invalid state: status=closed but current_stage != closed
    bad_state = make_state(
        "motor_001",
        status=MotorStatus.CLOSED,
        current_stage=Stage.DOCUMENTATION_BASE.value,
        is_closed=True,
    )
    state_path = motor_dir / "motor_state.json"
    state_path.write_text(json.dumps(bad_state.to_dict()))

    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=False)
    result = orc.run_one("motor_001")
    assert result.action == "blocked"
    assert "Invalid state" in result.reason


# ─── already closed motor is skipped ─────────────────────────────────────

def test_closed_motor_is_skipped(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
    })
    gov = _make_governanza(tmp_path)
    motor_dir = gov / make_entry("motor_001").slug
    motor_dir.mkdir(parents=True)

    closed_state = make_state(
        "motor_001",
        status=MotorStatus.CLOSED,
        current_stage=Stage.CLOSED.value,
        is_closed=True,
    )
    state_path = motor_dir / "motor_state.json"
    state_path.write_text(json.dumps(closed_state.to_dict()))

    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=True)
    result = orc.run_one("motor_001")
    assert result.action == "skipped"
    assert "already closed" in result.reason


# ─── motor closes correctly when all gates pass ───────────────────────────

def test_motor_closes_when_gate_6_passes(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
    })
    gov = _make_governanza(tmp_path)
    motor_dir = gov / make_entry("motor_001").slug
    motor_dir.mkdir(parents=True)

    # Write state at conformance_review stage
    state = make_state(
        "motor_001",
        status=MotorStatus.IN_PROGRESS,
        current_stage=Stage.CONFORMANCE_REVIEW.value,
        completed_stages=[
            Stage.DOCUMENTATION_BASE.value,
            Stage.SCHEMA_TECHNICAL.value,
            Stage.TESTS.value,
            Stage.FAILURE_MODES.value,
            Stage.IMPLEMENTATION.value,
        ],
    )
    (motor_dir / "motor_state.json").write_text(json.dumps(state.to_dict()))

    # Write a passing conformance_review_report
    report = {
        "summary": {"status": "PASS", "verdict": "all good"},
        "open_items": [],
    }
    p = motor_dir / "artifacts" / "conformance_review" / "conformance_review_report.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(report) + " " * 600)

    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=False)
    result = orc.run_one("motor_001")
    assert result.action == "closed"
    assert result.to_stage == Stage.CLOSED.value

    # Verify state file was updated
    saved = json.loads((motor_dir / "motor_state.json").read_text())
    assert saved["status"] == MotorStatus.CLOSED
    assert saved["closure"]["is_closed"] is True


# ─── artifact missing blocks advancement ──────────────────────────────────

def test_missing_artifact_blocks_gate(tmp_path):
    deps_file = _make_deps_file(tmp_path, {
        "motor_001": {"name": "Phase Contract Registry", "group": "A",
                      "catalog_status": "documented", "requires": []},
    })
    gov = _make_governanza(tmp_path)
    motor_dir = gov / make_entry("motor_001").slug
    motor_dir.mkdir(parents=True)

    # State is in_progress at schema_technical but no technical_schema file
    state = make_state(
        "motor_001",
        status=MotorStatus.IN_PROGRESS,
        current_stage=Stage.SCHEMA_TECHNICAL.value,
        completed_stages=[Stage.DOCUMENTATION_BASE.value],
    )
    (motor_dir / "motor_state.json").write_text(json.dumps(state.to_dict()))

    orc = Orchestrator(governanza=gov, dependencies_file=deps_file, dry_run=False)
    result = orc.run_one("motor_001")
    assert result.action == "blocked"
    assert "technical_schema" in result.reason
