"""Knowledge proposal infrastructure tests (post V5 cleanup).

Originally V4 P1 introduced an LLM-extractor scaffold; V5 P0 removed it
because the Phase 0 constitution forbids the LLM from being the
analytical engine. The path that SURVIVES from V4 P1 is the manual /
hand-authored draft path: a human reads an authoritative source, types
the JSON, and the framework validates + lands it in
knowledge_pending/<kind>/ for human approval at the dashboard.

This test file exercises that surviving path plus the motor_065
surface reporter and the extract_knowledge CLI.

Constitutional anchor: motor_019 is the ONLY LLM in the framework; it
is a narrator, not an analyst. The IRE here is schema + write path.
Automated extraction lives in `runtime_orchestrator.zlab_skill`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from runtime_orchestrator.industrial_research_engine import (
    KNOWLEDGE_KINDS,
    KnowledgeValidationError,
    MemoryState,
    NotImplementedExtractor,
    extract_knowledge,
    propose_knowledge_from_manual_text,
)


# ── Stubs / fail-loud entrypoints ─────────────────────────────────────


def test_extract_knowledge_is_fail_loud_stub():
    """extract_knowledge() is intentionally a stub that redirects to zlab_skill."""
    with pytest.raises(NotImplementedError, match=r"zlab_skill"):
        extract_knowledge("https://example.com/x.pdf", "refrigeration")


def test_not_implemented_extractor_redirects_to_zlab_skill():
    with pytest.raises(NotImplementedError, match=r"zlab_skill"):
        NotImplementedExtractor().extract("http://x", "refrigeration")


# ── Manual / paste-in path WORKS end-to-end ──────────────────────────


@pytest.fixture
def tmp_pending(tmp_path, monkeypatch):
    """Redirect pending + memory roots so tests don't pollute the repo."""
    from runtime_orchestrator.industrial_research_engine import engine, memory
    pending = tmp_path / "knowledge_pending"
    mem = tmp_path / "knowledge_memory"
    for kind in KNOWLEDGE_KINDS:
        (pending / kind).mkdir(parents=True, exist_ok=True)
    for st in MemoryState:
        (mem / st.value).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(engine, "_PENDING_ROOT", pending)
    monkeypatch.setattr(engine, "_AUDIT_LOG", pending / "knowledge_proposal_log.jsonl")
    monkeypatch.setattr(memory, "_PENDING_ROOT", pending)
    monkeypatch.setattr(memory, "_MEMORY_ROOT", mem)
    monkeypatch.setattr(memory, "_AUDIT_LOG", mem / "knowledge_memory_log.jsonl")
    return tmp_path, pending, mem


def _good_pattern_payload() -> dict:
    return {
        "id": "manual_extracted_pattern_a",
        "version": "1.0.0",
        "knowledge_kind": "pattern",
        "asset_families": ["cold_chain_facility"],
        "anti_families": [],
        "trigger_conditions": ["test trigger"],
        "anti_triggers": [],
        "falsification_conditions": ["test falsification"],
        "evidence_required": ["test evidence"],
        "financial_translation": "Test financial framing.",
        "tad_actions": ["VALIDATE_LOSS_PATTERN"],
        "allowed_language": "Test claim language for V5 manual path.",
        "prohibited_language": ["ROI"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "iiar_bulletin_109", "confidence": "high"}],
    }


def test_manual_path_lands_in_pending(tmp_pending):
    _tmp, pending, _mem = tmp_pending
    payload = _good_pattern_payload()
    proposed = propose_knowledge_from_manual_text(
        source_id="iiar_bulletin_109",
        topic="refrigeration",
        target_kind="pattern",
        knowledge_payload=payload,
        proposed_by="test_extractor",
    )
    assert proposed is not None
    file_path = pending / "pattern" / "manual_extracted_pattern_a.v1.json"
    assert file_path.exists()
    on_disk = json.loads(file_path.read_text(encoding="utf-8"))
    assert on_disk["__proposed_by__"] == "test_extractor"


def test_manual_path_stamps_source_basis_when_missing(tmp_pending):
    """If the caller omitted source_basis entirely, the engine
    auto-stamps it with the source_id passed in."""
    payload = _good_pattern_payload()
    payload["id"] = "manual_no_sourcebasis"
    # Wipe source_basis so the auto-stamp is what proves the test
    payload["source_basis"] = []
    proposed = propose_knowledge_from_manual_text(
        source_id="iiar_bulletin_109",
        topic="refrigeration",
        target_kind="pattern",
        knowledge_payload=payload,
    )
    assert any(
        s.get("source_id") == "iiar_bulletin_109"
        for s in proposed.get("source_basis", [])
    )


def test_manual_path_stamps_extraction_metadata(tmp_pending):
    payload = _good_pattern_payload()
    payload["id"] = "manual_meta_check"
    proposed = propose_knowledge_from_manual_text(
        source_id="iiar_bulletin_109",
        topic="refrigeration",
        target_kind="pattern",
        knowledge_payload=payload,
    )
    em = proposed.get("extraction_metadata", {})
    assert em.get("source_id") == "iiar_bulletin_109"
    assert em.get("topic") == "refrigeration"
    assert em.get("extraction_path") == "manual"


def test_manual_path_validates_payload(tmp_pending):
    payload = _good_pattern_payload()
    payload["falsification_conditions"] = []  # invalid — schema requires
    with pytest.raises(KnowledgeValidationError):
        propose_knowledge_from_manual_text(
            source_id="iiar_bulletin_109",
            topic="refrigeration",
            target_kind="pattern",
            knowledge_payload=payload,
        )


def test_manual_path_rejects_unknown_source_id(tmp_pending):
    payload = _good_pattern_payload()
    payload["id"] = "manual_unknown_source"
    with pytest.raises(ValueError, match="not in the industrial_source_catalog"):
        propose_knowledge_from_manual_text(
            source_id="unicorn_handbook",
            topic="refrigeration",
            target_kind="pattern",
            knowledge_payload=payload,
        )


# ── motor_065 surface reporter ───────────────────────────────────────


def test_motor_065_reports_deterministic_extraction_path():
    from runtime_orchestrator.adapters.motor_065 import Motor065Adapter
    out = Motor065Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "cold_chain_facility"}},
        "motor_035": {},
    })
    assert out["motor_065_phase"] == "phase_1_surface_reporter"
    assert out["asset_family_evaluated"] == "cold_chain_facility"
    status = out["extractor_status"]
    assert status["llm_in_extraction"] is False
    assert status["extraction_path"] == "deterministic_via_zlab_skill"
    assert "zlab_skill.local_pdf_autodraft" in status["pdf_pattern_matcher"]


def test_motor_065_surfaces_research_priority_plan():
    from runtime_orchestrator.adapters.motor_065 import Motor065Adapter
    out = Motor065Adapter().run({
        "motor_007": {"target_definition_contract": {
            "target_type": "manufacturing_facility",
            "process_evidence_tokens": ["process_heat_signature"],
        }},
        "motor_035": {},
    })
    plan = out["research_priority_plan"]
    assert plan["asset_family"] == "manufacturing_facility"
    assert len(plan["topics_ordered"]) > 0


def test_motor_065_emits_pending_summary_per_kind():
    from runtime_orchestrator.adapters.motor_065 import Motor065Adapter
    out = Motor065Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "cold_chain_facility"}},
        "motor_035": {},
    })
    summary = out["knowledge_pending_summary"]
    for kind in KNOWLEDGE_KINDS:
        assert kind in summary


def test_motor_065_emits_memory_counts_per_state():
    from runtime_orchestrator.adapters.motor_065 import Motor065Adapter
    out = Motor065Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "cold_chain_facility"}},
        "motor_035": {},
    })
    counts = out["knowledge_memory_counts"]
    for state in MemoryState:
        assert state.value in counts


# ── motor_065 wired into layer_registry ─────────────────────────────


def test_motor_065_is_layer_a():
    from runtime_orchestrator.layer_registry import layer_of
    assert layer_of("motor_065") == "A"


# ── CLI smoke test ──────────────────────────────────────────────────


def test_extract_knowledge_cli_help_exits_clean():
    import subprocess
    script = Path(__file__).resolve().parents[1] / "scripts" / "extract_knowledge.py"
    r = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0
    assert "Manual knowledge extraction" in r.stdout
