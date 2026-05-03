"""Shared fixtures for motor-creator tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from motor_creator.models import MotorEntry, MotorState, MotorStatus, Stage, STAGE_SEQUENCE


# ─── Motor entry builders ─────────────────────────────────────────────────

def make_entry(
    motor_id: str = "motor_001",
    name: str = "Phase Contract Registry",
    group: str = "A",
    catalog_status: str = "documented",
    requires: list[str] | None = None,
    orchestrator_eligible: bool = True,
) -> MotorEntry:
    return MotorEntry(
        motor_id=motor_id,
        name=name,
        group=group,
        catalog_status=catalog_status,
        requires=requires or [],
        orchestrator_eligible=orchestrator_eligible,
    )


def make_state(
    motor_id: str = "motor_001",
    status: str = MotorStatus.NOT_STARTED,
    current_stage: str = Stage.DOCUMENTATION_BASE.value,
    completed_stages: list[str] | None = None,
    blocked: bool = False,
    paused: bool = False,
    waiting_on: str | None = None,
    is_closed: bool = False,
) -> MotorState:
    from datetime import datetime, timezone
    stages = [s.value for s in STAGE_SEQUENCE]
    return MotorState(
        motor_id=motor_id,
        motor_name="Test Motor",
        purpose="",
        current_stage=current_stage,
        stage_sequence=stages,
        completed_stages=completed_stages or [],
        artifacts={s.value: {"exists": False, "items": []} for s in STAGE_SEQUENCE},
        missing_artifacts=[],
        validations=[],
        corrections=[],
        status=status,
        blocked=blocked,
        paused=paused,
        waiting_on=waiting_on,
        closure={"is_closed": is_closed, "closed_at": None, "closure_notes": ""},
        notes="",
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


# ─── File system helpers ─────────────────────────────────────────────────

def write_artifact(motor_dir: Path, stage: str, name: str, content: str, ext: str = ".md") -> Path:
    """Write a file to motor_dir/artifacts/{stage}/{name}{ext}."""
    p = motor_dir / "artifacts" / stage / f"{name}{ext}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def write_minimal_doc_base(motor_dir: Path, entry: MotorEntry) -> None:
    """Write all 7 documentation_base artifacts with valid (no-marker) content."""
    from motor_creator.artifact_manager import STAGE_ARTIFACTS, Stage as S
    templates = {
        "functional_contract": (
            "# Functional Contract\n\n"
            "## inputs\n- input_a: str\n\n"
            "## outputs\n- output_b: str\n\n"
            "## limits\n- Does not process nulls.\n\n"
            "## validations\n- All inputs must be non-empty.\n"
        ),
        "conceptual_schema": (
            "# Conceptual Schema\n\n"
            "## entities\n- Entity A\n\n"
            "## relationships\n- A has B\n\n"
            "## key_fields\n- id: str\n"
        ),
        "operational_rules": (
            "# Operational Rules\n\n"
            "## rules\n- Rule 1: validate before processing.\n\n"
            "## invariants\n- ID must be stable.\n\n"
            "## forbidden_operations\n- Do not mutate raw input.\n"
        ),
        "master_concept_doc": (
            "# Master Concept Doc\n\n"
            "## purpose\nManage contracts.\n\n"
            "## what_it_does\nValidates inputs.\n\n"
            "## what_it_does_not_do\nDoes not store.\n\n"
            "## why_it_exists\nFoundational.\n"
        ),
        "acceptance_tests": (
            "# Acceptance Tests\n\n"
            "## happy_path\nValid input is accepted.\n\n"
            "## edge_cases\nEmpty list is rejected.\n\n"
            "## rejection_criteria\nNull input raises error.\n"
        ),
        "failure_modes": (
            "# Failure Modes\n\n"
            "## failure_modes_list\n- Input null\n\n"
            "## anti_patterns\n- Monolith growth\n\n"
            "## degradation_signals\n- Response latency spike\n"
        ),
        "design_done_criteria": (
            "# Design Done Criteria\n\n"
            "## criteria\n"
            "- Contract is unambiguous.\n"
            "- Objects are defined.\n"
            "- Limits are explicit.\n"
        ),
    }
    stage = "documentation_base"
    for name, content in templates.items():
        # Pad to > 500 bytes
        content = content + ("." * max(0, 600 - len(content)))
        write_artifact(motor_dir, stage, name, content)


@pytest.fixture
def motor_dir(tmp_path: Path) -> Path:
    entry = make_entry("motor_001")
    d = tmp_path / entry.slug  # "001_phase-contract-registry"
    d.mkdir()
    return d


@pytest.fixture
def entry_001() -> MotorEntry:
    return make_entry(motor_id="motor_001", requires=[])


@pytest.fixture
def entry_002() -> MotorEntry:
    return make_entry(motor_id="motor_002", name="Versioning Engine", requires=["motor_001"])


@pytest.fixture
def state_001_not_started() -> MotorState:
    return make_state(motor_id="motor_001", status=MotorStatus.NOT_STARTED)


@pytest.fixture
def state_001_closed() -> MotorState:
    stages = [s.value for s in STAGE_SEQUENCE]
    return make_state(
        motor_id="motor_001",
        status=MotorStatus.CLOSED,
        current_stage=Stage.CLOSED.value,
        completed_stages=stages,
        is_closed=True,
    )
