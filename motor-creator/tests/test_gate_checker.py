"""Tests for gate_checker module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from motor_creator.gate_checker import (
    evaluate_gate_1,
    evaluate_gate_2,
    evaluate_gate_3,
    evaluate_gate_6,
    file_exists,
    has_sections,
    min_items,
    no_markers,
)

from conftest import write_artifact, write_minimal_doc_base, make_entry


# ─── primitive conditions ─────────────────────────────────────────────────

def test_file_exists_true(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("x" * 600)
    assert file_exists(p) is True


def test_file_exists_too_small(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("x" * 100)
    assert file_exists(p) is False


def test_file_exists_missing(tmp_path):
    assert file_exists(tmp_path / "missing.md") is False


def test_no_markers_clean(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("## inputs\nsome content\n" + "x" * 600)
    assert no_markers(p) is True


def test_no_markers_with_todo(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("## inputs\nTODO: fix this\n" + "x" * 600)
    assert no_markers(p) is False


def test_no_markers_with_pendiente(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("[PENDIENTE]\n" + "x" * 600)
    assert no_markers(p) is False


def test_has_sections_all_present(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("## inputs\nstuff\n## outputs\nstuff\n## limits\nstuff\n")
    assert has_sections(p, ["inputs", "outputs", "limits"]) is True


def test_has_sections_missing_one(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("## inputs\nstuff\n## outputs\nstuff\n")
    assert has_sections(p, ["inputs", "outputs", "limits"]) is False


def test_has_sections_json(tmp_path):
    p = tmp_path / "report.json"
    p.write_text(json.dumps({"summary": {}, "open_items": []}))
    assert has_sections(p, ["summary", "open_items"]) is True


def test_min_items_sufficient(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("## criteria\n- item 1\n- item 2\n- item 3\n")
    assert min_items(p, "criteria", 3) is True


def test_min_items_insufficient(tmp_path):
    p = tmp_path / "f.md"
    p.write_text("## criteria\n- item 1\n- item 2\n")
    assert min_items(p, "criteria", 3) is False


# ─── gate 1 ──────────────────────────────────────────────────────────────

def test_gate_1_fails_when_files_missing(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    result = evaluate_gate_1(motor_dir)
    assert result.passed is False
    assert any("master_concept_doc" in c for c in result.failed_conditions)


def test_gate_1_passes_with_valid_artifacts(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    entry = make_entry()
    write_minimal_doc_base(motor_dir, entry)
    result = evaluate_gate_1(motor_dir)
    assert result.passed is True
    # Gate 1 always has a manual check pending
    assert len(result.manual_checks_pending) > 0


def test_gate_1_fails_with_markers_in_contract(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    entry = make_entry()
    write_minimal_doc_base(motor_dir, entry)
    # Overwrite functional_contract with marker
    p = motor_dir / "artifacts" / "documentation_base" / "functional_contract.md"
    p.write_text(
        "## inputs\nTODO: define\n## outputs\nstuff\n## limits\nstuff\n" + "x" * 600
    )
    result = evaluate_gate_1(motor_dir)
    assert result.passed is False
    assert any("no_markers(functional_contract)" in c for c in result.failed_conditions)


# ─── gate 2 ──────────────────────────────────────────────────────────────

def test_gate_2_fails_missing_technical_schema(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    result = evaluate_gate_2(motor_dir)
    assert result.passed is False


def test_gate_2_passes_with_valid_schema(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    content = (
        "# Technical Schema\n\n"
        "## entities\nE1\n## fields\nf1: str\n"
        "## relationships\nr1\n## identifiers\nid: uuid\n"
        "## versioning\nv: int\n## lineage\nsource_id: str\n"
    )
    write_artifact(motor_dir, "schema_technical", "technical_schema", content + "x" * 600)
    result = evaluate_gate_2(motor_dir)
    assert result.passed is True


# ─── gate 3 ──────────────────────────────────────────────────────────────

def test_gate_3_fails_missing_test_spec(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    result = evaluate_gate_3(motor_dir)
    assert result.passed is False


def test_gate_3_fails_missing_section(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    content = (
        "## happy_path\nTest 1\n## sparse_case\nTest 2\n"
        "## malformed_input\nTest 3\n## edge_cases\nTest 4\n"
        "## pass_criteria\nAll ok\n"
        # missing fail_criteria
    )
    write_artifact(motor_dir, "tests", "test_spec", content + "x" * 600)
    result = evaluate_gate_3(motor_dir)
    assert result.passed is False
    assert any("fail_criteria" in c for c in result.failed_conditions)


# ─── gate 6 ──────────────────────────────────────────────────────────────

def test_gate_6_fails_missing_report(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    result = evaluate_gate_6(motor_dir)
    assert result.passed is False


def test_gate_6_fails_on_fail_status(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    report = {
        "summary": {"status": "FAIL", "verdict": "violations found"},
        "open_items": [],
    }
    p = motor_dir / "artifacts" / "conformance_review" / "conformance_review_report.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report) + " " * 600)
    result = evaluate_gate_6(motor_dir)
    assert result.passed is False


def test_gate_6_passes_on_pass_status(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    report = {
        "summary": {"status": "PASS", "verdict": "all good"},
        "open_items": [],
    }
    p = motor_dir / "artifacts" / "conformance_review" / "conformance_review_report.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report) + " " * 600)
    result = evaluate_gate_6(motor_dir)
    assert result.passed is True
    assert result.manual_checks_pending == []


def test_gate_6_conditional_pass_with_unresolved_items(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    report = {
        "summary": {"status": "CONDITIONAL_PASS", "verdict": "minor issues"},
        "open_items": [
            {"id": "oi1", "resolution": "unresolved", "severity": "minor", "description": "x"}
        ],
    }
    p = motor_dir / "artifacts" / "conformance_review" / "conformance_review_report.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report) + " " * 600)
    result = evaluate_gate_6(motor_dir)
    assert result.passed is True  # structural conditions pass
    assert len(result.manual_checks_pending) > 0  # but manual check is required


def test_gate_6_conditional_pass_all_resolved(tmp_path):
    motor_dir = tmp_path / "motor"
    motor_dir.mkdir()
    report = {
        "summary": {"status": "CONDITIONAL_PASS", "verdict": "minor issues"},
        "open_items": [
            {"id": "oi1", "resolution": "accepted_risk", "severity": "minor", "description": "x"}
        ],
    }
    p = motor_dir / "artifacts" / "conformance_review" / "conformance_review_report.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report) + " " * 600)
    result = evaluate_gate_6(motor_dir)
    assert result.passed is True
    assert result.manual_checks_pending == []
