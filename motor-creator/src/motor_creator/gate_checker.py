from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .config import ARTIFACTS_DIR, MIN_FILE_SIZE_BYTES, OPEN_MARKERS
from .models import ARTIFACT_EXT, GateResult, MotorEntry, Stage


# ─── Primitive conditions (from stage_gates.md) ────────────────────────────

def file_exists(artifact_path: Path) -> bool:
    """File or directory exists and has size > MIN_FILE_SIZE_BYTES.
    For directories: exists and is non-empty."""
    if artifact_path.is_dir():
        return any(artifact_path.iterdir())
    if not artifact_path.is_file():
        return False
    return artifact_path.stat().st_size > MIN_FILE_SIZE_BYTES


def no_markers(artifact_path: Path) -> bool:
    """File contains none of the open-work markers."""
    if not artifact_path.is_file():
        return False
    content = artifact_path.read_text(encoding="utf-8", errors="replace")
    for marker in OPEN_MARKERS:
        if marker in content:
            return False
    return True


def has_sections(artifact_path: Path, sections: list[str]) -> bool:
    """File contains all listed section titles (## section) for .md,
    or all listed top-level keys for .json."""
    if not artifact_path.is_file():
        return False
    if artifact_path.suffix == ".json":
        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
            return all(s in data for s in sections)
        except json.JSONDecodeError:
            return False
    content = artifact_path.read_text(encoding="utf-8", errors="replace").lower()
    for section in sections:
        # Accept ## section or # section
        if f"## {section.lower()}" not in content and f"# {section.lower()}" not in content:
            return False
    return True


def min_items(artifact_path: Path, section: str, n: int) -> bool:
    """Section in markdown has at least n list items (lines starting with - or * or digit.)."""
    if not artifact_path.is_file():
        return False
    content = artifact_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    in_section = False
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith(f"## {section.lower()}") or \
           stripped.lower().startswith(f"# {section.lower()}"):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("#"):  # new section
                break
            if stripped.startswith(("-", "*")) or (stripped and stripped[0].isdigit() and "." in stripped[:3]):
                count += 1
    return count >= n


def json_valid(artifact_path: Path) -> bool:
    """File is parseable JSON."""
    if not artifact_path.is_file():
        return False
    try:
        json.loads(artifact_path.read_text(encoding="utf-8"))
        return True
    except (json.JSONDecodeError, OSError):
        return False


def field_not_empty(artifact_path: Path, field_path: str) -> bool:
    """JSON field (dot-separated path) is not null and not empty string."""
    if not artifact_path.is_file():
        return False
    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        parts = field_path.split(".")
        val = data
        for part in parts:
            val = val[part]
        return val is not None and val != ""
    except (json.JSONDecodeError, KeyError, TypeError):
        return False


def field_value_in(artifact_path: Path, field_path: str, allowed: list[str]) -> bool:
    """JSON field value is one of the allowed values."""
    if not artifact_path.is_file():
        return False
    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        parts = field_path.split(".")
        val = data
        for part in parts:
            val = val[part]
        return val in allowed
    except (json.JSONDecodeError, KeyError, TypeError):
        return False


def all_open_items_resolved(artifact_path: Path) -> bool:
    """All open_items in conformance_review_report have resolved != 'unresolved'."""
    if not artifact_path.is_file():
        return False
    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        open_items = data.get("open_items", [])
        return all(item.get("resolution") != "unresolved" for item in open_items)
    except (json.JSONDecodeError, KeyError, TypeError):
        return False


# ─── Artifact path helpers ─────────────────────────────────────────────────

def artifact_path(motor_dir: Path, stage: Stage, artifact_name: str) -> Path:
    ext = ARTIFACT_EXT.get(artifact_name, ".md")
    return motor_dir / ARTIFACTS_DIR / stage.value / f"{artifact_name}{ext}"


# ─── Gate evaluators ───────────────────────────────────────────────────────

def evaluate_gate_1(motor_dir: Path) -> GateResult:
    """documentation_base → schema_technical"""
    failed: list[str] = []
    manual: list[str] = []
    stage = Stage.DOCUMENTATION_BASE

    required_files = [
        "master_concept_doc", "functional_contract", "conceptual_schema",
        "operational_rules", "acceptance_tests", "failure_modes", "design_done_criteria",
    ]
    for name in required_files:
        p = artifact_path(motor_dir, stage, name)
        if not file_exists(p):
            failed.append(f"file_exists({name})")

    for name in ("functional_contract", "conceptual_schema", "operational_rules"):
        p = artifact_path(motor_dir, stage, name)
        if file_exists(p) and not no_markers(p):
            failed.append(f"no_markers({name})")

    fc = artifact_path(motor_dir, stage, "functional_contract")
    if file_exists(fc) and not has_sections(fc, ["inputs", "outputs", "limits"]):
        failed.append("has_sections(functional_contract, [inputs, outputs, limits])")

    ddc = artifact_path(motor_dir, stage, "design_done_criteria")
    if file_exists(ddc) and not min_items(ddc, "criteria", 3):
        failed.append("min_items(design_done_criteria, criteria, 3)")

    manual.append(
        "functional_contract has no material ambiguities in inputs/outputs "
        "(approve with: python cli.py approve --motor {id} --gate gate_1)"
    )

    return GateResult(
        gate_number=1,
        from_stage=Stage.DOCUMENTATION_BASE,
        to_stage=Stage.SCHEMA_TECHNICAL,
        passed=len(failed) == 0,
        failed_conditions=failed,
        manual_checks_pending=manual,
    )


def evaluate_gate_2(motor_dir: Path) -> GateResult:
    """schema_technical → tests"""
    failed: list[str] = []
    stage = Stage.SCHEMA_TECHNICAL

    ts = artifact_path(motor_dir, stage, "technical_schema")
    if not file_exists(ts):
        failed.append("file_exists(technical_schema)")
    else:
        if not no_markers(ts):
            failed.append("no_markers(technical_schema)")
        required_sections = ["entities", "fields", "relationships", "identifiers", "versioning", "lineage"]
        if not has_sections(ts, required_sections):
            failed.append(f"has_sections(technical_schema, {required_sections})")

    return GateResult(
        gate_number=2,
        from_stage=Stage.SCHEMA_TECHNICAL,
        to_stage=Stage.TESTS,
        passed=len(failed) == 0,
        failed_conditions=failed,
    )


def evaluate_gate_3(motor_dir: Path) -> GateResult:
    """tests → failure_modes"""
    failed: list[str] = []
    stage = Stage.TESTS

    ts = artifact_path(motor_dir, stage, "test_spec")
    if not file_exists(ts):
        failed.append("file_exists(test_spec)")
    else:
        if not no_markers(ts):
            failed.append("no_markers(test_spec)")
        for section in ("happy_path", "sparse_case", "malformed_input", "edge_cases"):
            if not has_sections(ts, [section]):
                failed.append(f"has_sections(test_spec, [{section}])")
        for section in ("pass_criteria", "fail_criteria"):
            if not has_sections(ts, [section]):
                failed.append(f"has_sections(test_spec, [{section}])")

    return GateResult(
        gate_number=3,
        from_stage=Stage.TESTS,
        to_stage=Stage.FAILURE_MODES,
        passed=len(failed) == 0,
        failed_conditions=failed,
    )


def evaluate_gate_4(motor_dir: Path) -> GateResult:
    """failure_modes → implementation"""
    failed: list[str] = []

    fms = artifact_path(motor_dir, Stage.FAILURE_MODES, "failure_modes_spec")
    if not file_exists(fms):
        failed.append("file_exists(failure_modes_spec)")
    else:
        if not no_markers(fms):
            failed.append("no_markers(failure_modes_spec)")
        for section in ("failure_modes_list", "anti_patterns", "degradation_signals", "expensive_errors"):
            if not has_sections(fms, [section]):
                failed.append(f"has_sections(failure_modes_spec, [{section}])")

    # Also re-check technical_schema has no markers (from stage_gates.md gate 4)
    ts = artifact_path(motor_dir, Stage.SCHEMA_TECHNICAL, "technical_schema")
    if file_exists(ts) and not no_markers(ts):
        failed.append("no_markers(technical_schema) [re-check at gate 4]")

    return GateResult(
        gate_number=4,
        from_stage=Stage.FAILURE_MODES,
        to_stage=Stage.IMPLEMENTATION,
        passed=len(failed) == 0,
        failed_conditions=failed,
    )


def evaluate_gate_5(motor_dir: Path) -> GateResult:
    """implementation → conformance_review"""
    failed: list[str] = []

    codebase = artifact_path(motor_dir, Stage.IMPLEMENTATION, "codebase")
    if not file_exists(codebase):
        failed.append("file_exists(codebase) [directory or file with executable code]")

    ue = artifact_path(motor_dir, Stage.IMPLEMENTATION, "usage_example")
    if not file_exists(ue):
        failed.append("file_exists(usage_example)")
    elif not no_markers(ue):
        failed.append("no_markers(usage_example)")

    return GateResult(
        gate_number=5,
        from_stage=Stage.IMPLEMENTATION,
        to_stage=Stage.CONFORMANCE_REVIEW,
        passed=len(failed) == 0,
        failed_conditions=failed,
    )


def evaluate_gate_6(motor_dir: Path) -> GateResult:
    """conformance_review → closed"""
    failed: list[str] = []
    manual: list[str] = []

    crr = artifact_path(motor_dir, Stage.CONFORMANCE_REVIEW, "conformance_review_report")

    if not file_exists(crr):
        failed.append("file_exists(conformance_review_report)")
    else:
        if not json_valid(crr):
            failed.append("json_valid(conformance_review_report)")
        elif not field_not_empty(crr, "summary.status"):
            failed.append("field_not_empty(summary.status)")
        elif not field_value_in(crr, "summary.status", ["PASS", "CONDITIONAL_PASS"]):
            failed.append("field_value_in(summary.status, [PASS, CONDITIONAL_PASS])")
        else:
            # Check if CONDITIONAL_PASS has unresolved items
            if not all_open_items_resolved(crr):
                manual.append(
                    "CONDITIONAL_PASS with unresolved open_items — human review required "
                    "(approve with: python cli.py approve --motor {id} --gate gate_6)"
                )

    return GateResult(
        gate_number=6,
        from_stage=Stage.CONFORMANCE_REVIEW,
        to_stage=Stage.CLOSED,
        passed=len(failed) == 0,
        failed_conditions=failed,
        manual_checks_pending=manual,
    )


# ─── Main gate evaluation dispatcher ──────────────────────────────────────

GATE_EVALUATORS = {
    1: evaluate_gate_1,
    2: evaluate_gate_2,
    3: evaluate_gate_3,
    4: evaluate_gate_4,
    5: evaluate_gate_5,
    6: evaluate_gate_6,
}


def evaluate_current_gate(motor_dir: Path, current_stage: Stage) -> Optional[GateResult]:
    """
    Evaluate the gate that applies to the current stage.
    Returns None if current_stage is 'closed' (no gate applies).
    """
    gate_map = {
        Stage.DOCUMENTATION_BASE: 1,
        Stage.SCHEMA_TECHNICAL: 2,
        Stage.TESTS: 3,
        Stage.FAILURE_MODES: 4,
        Stage.IMPLEMENTATION: 5,
        Stage.CONFORMANCE_REVIEW: 6,
    }
    gate_num = gate_map.get(current_stage)
    if gate_num is None:
        return None
    evaluator = GATE_EVALUATORS[gate_num]
    return evaluator(motor_dir)
