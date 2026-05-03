from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class MotorStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    READY_FOR_NEXT_STAGE = "ready_for_next_stage"
    WAITING = "waiting"
    BLOCKED = "blocked"
    PAUSED = "paused"
    CLOSED = "closed"


class Stage(str, Enum):
    DOCUMENTATION_BASE = "documentation_base"
    SCHEMA_TECHNICAL = "schema_technical"
    TESTS = "tests"
    FAILURE_MODES = "failure_modes"
    IMPLEMENTATION = "implementation"
    CONFORMANCE_REVIEW = "conformance_review"
    CLOSED = "closed"


STAGE_SEQUENCE: list[Stage] = [
    Stage.DOCUMENTATION_BASE,
    Stage.SCHEMA_TECHNICAL,
    Stage.TESTS,
    Stage.FAILURE_MODES,
    Stage.IMPLEMENTATION,
    Stage.CONFORMANCE_REVIEW,
]

# Artifacts required per stage (from depth_profile_policy.md)
STAGE_ARTIFACTS: dict[Stage, list[str]] = {
    Stage.DOCUMENTATION_BASE: [
        "master_concept_doc",
        "functional_contract",
        "conceptual_schema",
        "operational_rules",
        "acceptance_tests",
        "failure_modes",
        "design_done_criteria",
    ],
    Stage.SCHEMA_TECHNICAL: ["technical_schema"],
    Stage.TESTS: ["test_spec"],
    Stage.FAILURE_MODES: ["failure_modes_spec"],
    Stage.IMPLEMENTATION: ["codebase", "usage_example"],
    Stage.CONFORMANCE_REVIEW: ["conformance_review_report"],
}

# Extension per artifact name. Empty string = directory.
ARTIFACT_EXT: dict[str, str] = {
    "master_concept_doc": ".md",
    "functional_contract": ".md",
    "conceptual_schema": ".md",
    "operational_rules": ".md",
    "acceptance_tests": ".md",
    "failure_modes": ".md",
    "design_done_criteria": ".md",
    "technical_schema": ".md",
    "test_spec": ".md",
    "failure_modes_spec": ".md",
    "codebase": "",        # directory
    "usage_example": ".md",
    "conformance_review_report": ".json",
}

# Lightweight motors: governance/policy without executable code
LIGHTWEIGHT_MOTORS = {"motor_024", "motor_025"}


def motor_name_to_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"\s*\+\s*", "-", slug)
    slug = re.sub(r"\s*/\s*", "-", slug)
    slug = re.sub(r"\s*&\s*", "-", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


@dataclass
class MotorEntry:
    motor_id: str
    name: str
    group: str
    catalog_status: str
    requires: list[str]
    orchestrator_eligible: bool = True

    @property
    def slug(self) -> str:
        # e.g. "phase-contract-registry_001"
        num = self.motor_id.replace("motor_", "")
        return f"{motor_name_to_slug(self.name)}_{num}"

    @property
    def is_group_c(self) -> bool:
        return self.group == "C"

    @property
    def is_lightweight(self) -> bool:
        return self.motor_id in LIGHTWEIGHT_MOTORS


@dataclass
class GateResult:
    gate_number: int
    from_stage: Stage
    to_stage: Stage
    passed: bool
    failed_conditions: list[str] = field(default_factory=list)
    manual_checks_pending: list[str] = field(default_factory=list)

    @property
    def is_blocked_by_manual(self) -> bool:
        return bool(self.manual_checks_pending)


@dataclass
class ArtifactStatus:
    artifact_name: str
    stage: Stage
    exists: bool
    path: str
    size_bytes: int = 0
    has_markers: bool = False
    is_placeholder: bool = False


@dataclass
class DependencyCheckResult:
    motor_id: str
    eligible: bool
    missing_deps: list[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class ValidationEntry:
    validation_id: str
    stage: str
    type: str
    result: str  # pass | pass_with_warnings | fail
    notes: str


@dataclass
class CorrectionEntry:
    correction_id: str
    from_stage: str
    to_stage: str
    reason: str
    status: str  # open | resolved


@dataclass
class MotorState:
    motor_id: str
    motor_name: str
    purpose: str
    current_stage: str
    stage_sequence: list[str]
    completed_stages: list[str]
    artifacts: dict[str, Any]
    missing_artifacts: list[str]
    validations: list[dict]
    corrections: list[dict]
    status: str
    blocked: bool
    paused: bool
    waiting_on: Optional[str]
    closure: dict
    notes: str
    updated_at: str

    def to_dict(self) -> dict:
        return {
            "motor_id": self.motor_id,
            "motor_name": self.motor_name,
            "purpose": self.purpose,
            "current_stage": self.current_stage,
            "stage_sequence": self.stage_sequence,
            "completed_stages": self.completed_stages,
            "artifacts": self.artifacts,
            "missing_artifacts": self.missing_artifacts,
            "validations": self.validations,
            "corrections": self.corrections,
            "status": self.status,
            "blocked": self.blocked,
            "paused": self.paused,
            "waiting_on": self.waiting_on,
            "closure": self.closure,
            "notes": self.notes,
            "updated_at": self.updated_at,
        }


@dataclass
class OrchestratorResult:
    motor_id: str
    action: str  # advanced | blocked | paused | skipped | closed | error
    from_stage: Optional[str]
    to_stage: Optional[str]
    reason: str
    artifacts_created: list[str] = field(default_factory=list)
    dry_run: bool = False
