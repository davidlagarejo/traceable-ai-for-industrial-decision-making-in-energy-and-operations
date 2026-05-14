"""Tests for curation_layer.py — human review persistence."""
from __future__ import annotations

import json

import pytest

from runtime_orchestrator import curation_layer as cl


@pytest.fixture
def isolated_root(tmp_path, monkeypatch):
    """Isolate curation writes to a temp dir per test."""
    monkeypatch.setenv("ZLAB_CURATION_ROOT", str(tmp_path / "curation"))
    return tmp_path


# ── combination decisions ─────────────────────────────────────────


def test_record_accept_decision(isolated_root):
    rec = cl.record_combination_decision(
        run_id="run-1",
        combination_id="combo-x",
        decision="accept",
        curator="alice",
    )
    assert rec.decision == "accept"
    assert rec.run_id == "run-1"
    decisions = cl.load_combination_decisions("run-1")
    assert len(decisions) == 1
    assert decisions[0]["decision"] == "accept"
    assert decisions[0]["curator"] == "alice"


def test_record_modify_with_instruction(isolated_root):
    rec = cl.record_combination_decision(
        run_id="run-1",
        combination_id="combo-x",
        decision="modify",
        modify_instruction="Cambia el peer set a manufacturing-only",
    )
    assert rec.modify_instruction == "Cambia el peer set a manufacturing-only"


def test_invalid_decision_rejected(isolated_root):
    with pytest.raises(ValueError, match="decision must be"):
        cl.record_combination_decision(
            run_id="r", combination_id="c", decision="maybe",
        )


def test_missing_ids_rejected(isolated_root):
    with pytest.raises(ValueError, match="required"):
        cl.record_combination_decision(
            run_id="", combination_id="c", decision="accept",
        )


def test_multiple_decisions_accumulate(isolated_root):
    cl.record_combination_decision(
        run_id="run-1", combination_id="c", decision="accept",
    )
    cl.record_combination_decision(
        run_id="run-1", combination_id="c", decision="modify",
        modify_instruction="overrides previous",
    )
    rows = cl.load_combination_decisions("run-1")
    assert len(rows) == 2
    # Latest helper returns the most recent per combination_id
    latest = cl.latest_combination_decisions("run-1")
    assert latest["c"]["decision"] == "modify"


def test_load_returns_empty_when_no_file(isolated_root):
    assert cl.load_combination_decisions("nonexistent") == []
    assert cl.latest_combination_decisions("nonexistent") == {}


# ── PDF annotations ────────────────────────────────────────────────


def test_record_pdf_annotation_minimal(isolated_root):
    rec = cl.record_pdf_annotation(
        run_id="run-1",
        pdf_path="output/x.pdf",
        page=3,
        region={"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.05},
        comment="This claim needs a falsifier",
    )
    assert rec.page == 3
    assert rec.comment == "This claim needs a falsifier"
    annots = cl.load_pdf_annotations("run-1")
    assert len(annots) == 1


def test_record_pdf_annotation_with_suggested_change(isolated_root):
    rec = cl.record_pdf_annotation(
        run_id="run-1", pdf_path="x.pdf", page=1, region={},
        comment="Remove tenant chart",
        suggested_change="Eliminar gráfico CHT-002 (no aplica a cold-chain)",
    )
    assert rec.suggested_change.startswith("Eliminar")


def test_pdf_annotation_requires_comment(isolated_root):
    with pytest.raises(ValueError, match="comment is required"):
        cl.record_pdf_annotation(
            run_id="r", pdf_path="x.pdf", page=1, region={}, comment="",
        )


def test_pdf_annotation_invalid_page(isolated_root):
    with pytest.raises(ValueError, match="page must be"):
        cl.record_pdf_annotation(
            run_id="r", pdf_path="x.pdf", page=0, region={}, comment="x",
        )
    with pytest.raises(ValueError, match="page must be"):
        cl.record_pdf_annotation(
            run_id="r", pdf_path="x.pdf", page="abc", region={}, comment="x",
        )


def test_delete_pdf_annotation(isolated_root):
    a = cl.record_pdf_annotation(
        run_id="r", pdf_path="x.pdf", page=1, region={}, comment="kill me",
    )
    assert cl.delete_pdf_annotation("r", a.annotation_id) is True
    assert cl.load_pdf_annotations("r") == []
    # Deleting again returns False (idempotent)
    assert cl.delete_pdf_annotation("r", a.annotation_id) is False


def test_delete_nonexistent_annotation(isolated_root):
    assert cl.delete_pdf_annotation("never", "fake-id") is False


# ── Export bundle ──────────────────────────────────────────────────


def test_export_bundle_aggregates_everything(isolated_root):
    # Combo decisions
    cl.record_combination_decision(run_id="r", combination_id="c1", decision="accept")
    cl.record_combination_decision(run_id="r", combination_id="c2", decision="reject")
    cl.record_combination_decision(
        run_id="r", combination_id="c3", decision="modify",
        modify_instruction="tighten the peer set",
    )
    # PDF annotations
    cl.record_pdf_annotation(
        run_id="r", pdf_path="p.pdf", page=1, region={}, comment="A",
    )
    cl.record_pdf_annotation(
        run_id="r", pdf_path="p.pdf", page=2, region={}, comment="B",
    )
    bundle = cl.export_curation_bundle("r")
    assert bundle["run_id"] == "r"
    assert bundle["accept_count"] == 1
    assert bundle["reject_count"] == 1
    assert bundle["modify_count"] == 1
    assert bundle["annotation_count"] == 2
    assert len(bundle["combination_decisions"]) == 3
    assert "c1" in bundle["latest_per_combination"]
    assert "c3" in bundle["latest_per_combination"]


def test_export_empty_run_returns_zeroes(isolated_root):
    bundle = cl.export_curation_bundle("never-touched")
    assert bundle["accept_count"] == 0
    assert bundle["reject_count"] == 0
    assert bundle["modify_count"] == 0
    assert bundle["annotation_count"] == 0
    assert bundle["combination_decisions"] == []
    assert bundle["pdf_annotations"] == []


# ── Audit trail ───────────────────────────────────────────────────


def test_audit_log_appends_each_event(isolated_root):
    cl.record_combination_decision(run_id="r", combination_id="c1", decision="accept")
    cl.record_pdf_annotation(
        run_id="r", pdf_path="x.pdf", page=1, region={}, comment="z",
    )
    log_path = cl.curation_root() / "curation_log.jsonl"
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    kinds = [json.loads(l)["kind"] for l in lines]
    assert "combination_decision" in kinds
    assert "pdf_annotation" in kinds


# ── Custom root via env ───────────────────────────────────────────


def test_curation_root_respects_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ZLAB_CURATION_ROOT", str(tmp_path / "custom_curation"))
    assert cl.curation_root() == tmp_path / "custom_curation"


def test_curation_root_default_when_no_env(monkeypatch):
    monkeypatch.delenv("ZLAB_CURATION_ROOT", raising=False)
    root = cl.curation_root()
    # Should be runtime-orchestrator/curation/
    assert root.name == "curation"
    assert root.parent.name == "runtime-orchestrator"
