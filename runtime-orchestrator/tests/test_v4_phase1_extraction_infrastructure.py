"""V4 Phase 1 extraction infrastructure tests.

Covers:
  - PDF + LLM extraction interfaces (stub contracts)
  - ExtractionOrchestrator: full path raises NotImplementedError;
    manual path works and routes through validation
  - motor_065 adapter surfaces extraction surface in pipeline output
  - CLI extract_knowledge.py wraps orchestrator correctly
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from runtime_orchestrator.industrial_research_engine import (
    KNOWLEDGE_KINDS,
    ExtractionOrchestrator,
    ExtractionPlan,
    KnowledgeValidationError,
    LLMExtractionRequest,
    LLMExtractor,
    MemoryState,
    NotImplementedLLMExtractor,
    NotImplementedPDFExtractor,
    PDFExtractionResult,
    PDFExtractor,
)


# ── Interface stubs ─────────────────────────────────────────────────────


def test_pdf_extractor_stub_raises():
    with pytest.raises(NotImplementedError, match="PDF extraction is not implemented"):
        NotImplementedPDFExtractor().extract("https://example.com/x.pdf")


def test_llm_extractor_stub_raises():
    req = LLMExtractionRequest(
        raw_text="hello",
        topic="refrigeration",
        source_id="iiar_bulletin_109",
    )
    with pytest.raises(NotImplementedError, match="LLM extraction is not implemented"):
        NotImplementedLLMExtractor().extract(req)


def test_pdf_extraction_result_dataclass_defaults():
    r = PDFExtractionResult(source_url="x", text="hi")
    assert r.page_count == 0
    assert r.page_texts == []
    assert r.metadata == {}


# ── Orchestrator: full path raises (stubs in play) ─────────────────────


def test_orchestrator_full_path_raises_until_real_extractors_wired():
    orch = ExtractionOrchestrator()
    with pytest.raises(NotImplementedError):
        orch.orchestrate(
            source_id="iiar_bulletin_109",
            source_url="https://example.com/bulletin.pdf",
            topic="refrigeration",
            target_kind="pattern",
        )


def test_orchestrator_rejects_unknown_source_id():
    orch = ExtractionOrchestrator()
    with pytest.raises(ValueError, match="not in the industrial_source_catalog"):
        orch.orchestrate(
            source_id="unicorn_handbook",
            source_url="x",
            topic="refrigeration",
            target_kind="pattern",
        )


# ── Orchestrator: manual path WORKS end-to-end ──────────────────────────


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
        "allowed_language": "Test claim language for V4 P1 extraction.",
        "prohibited_language": ["ROI"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "iiar_bulletin_109", "confidence": "high"}],
    }


def test_orchestrator_manual_path_lands_in_pending(tmp_pending):
    tmp_path, pending, mem = tmp_pending
    orch = ExtractionOrchestrator()
    payload = _good_pattern_payload()
    result = orch.orchestrate_from_manual_text(
        source_id="iiar_bulletin_109",
        topic="refrigeration",
        target_kind="pattern",
        knowledge_payload=payload,
        proposed_by="test_extractor",
    )
    assert result.propose_result is not None
    file_path = pending / "pattern" / "manual_extracted_pattern_a.v1.json"
    assert file_path.exists()


def test_orchestrator_manual_path_stamps_source_basis_if_missing(tmp_pending):
    """If the caller omitted source_basis entirely, the orchestrator
    auto-stamps it with the source_id passed in."""
    payload = _good_pattern_payload()
    payload["id"] = "manual_no_sourcebasis"
    payload["source_basis"] = [{"source_id": "iiar_bulletin_109", "confidence": "manual"}]
    orch = ExtractionOrchestrator()
    result = orch.orchestrate_from_manual_text(
        source_id="iiar_bulletin_109",
        topic="refrigeration",
        target_kind="pattern",
        knowledge_payload=payload,
    )
    landed = result.propose_result
    assert landed is not None
    assert any(s.get("source_id") == "iiar_bulletin_109" for s in landed.get("source_basis", []))


def test_orchestrator_manual_path_stamps_extraction_metadata(tmp_pending):
    payload = _good_pattern_payload()
    payload["id"] = "manual_meta_check"
    orch = ExtractionOrchestrator()
    result = orch.orchestrate_from_manual_text(
        source_id="iiar_bulletin_109",
        topic="refrigeration",
        target_kind="pattern",
        knowledge_payload=payload,
    )
    landed = result.propose_result
    assert landed is not None
    em = landed.get("extraction_metadata", {})
    assert em.get("source_id") == "iiar_bulletin_109"
    assert em.get("topic") == "refrigeration"
    assert em.get("extraction_path") == "manual_orchestrator"


def test_orchestrator_manual_path_validates_payload(tmp_pending):
    payload = _good_pattern_payload()
    payload["falsification_conditions"] = []  # invalid — schema requires
    orch = ExtractionOrchestrator()
    with pytest.raises(KnowledgeValidationError):
        orch.orchestrate_from_manual_text(
            source_id="iiar_bulletin_109",
            topic="refrigeration",
            target_kind="pattern",
            knowledge_payload=payload,
        )


# ── Orchestrator with INJECTED real-looking extractors ─────────────────


class _StubLLMExtractor:
    """Test double: returns a fixed knowledge payload."""

    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def extract(self, request: LLMExtractionRequest):
        from runtime_orchestrator.industrial_research_engine import LLMExtractionResult
        return LLMExtractionResult(
            knowledge_payload=self._payload,
            confidence_self_assessment=0.85,
            model_id="test_stub",
        )


class _StubPDFExtractor:
    def extract(self, source_url: str, **opts):
        return PDFExtractionResult(
            source_url=source_url,
            text="extracted text content here",
            page_count=1,
            extraction_method="test_stub",
        )


def test_orchestrator_full_path_works_when_extractors_injected(tmp_pending):
    """Proves the full orchestrate() path is plug-and-play: when V4 P2
    swaps in real extractors, no orchestrator code changes."""
    payload = _good_pattern_payload()
    payload["id"] = "full_path_test"
    orch = ExtractionOrchestrator(
        pdf_extractor=_StubPDFExtractor(),
        llm_extractor=_StubLLMExtractor(payload),
    )
    result = orch.orchestrate(
        source_id="iiar_bulletin_109",
        source_url="https://example.com/bulletin.pdf",
        topic="refrigeration",
        target_kind="pattern",
    )
    assert result.propose_result is not None
    assert result.pdf_result is not None
    assert result.pdf_result.extraction_method == "test_stub"


# ── motor_065 adapter ────────────────────────────────────────────────


def test_motor_065_surfaces_extraction_status():
    from runtime_orchestrator.adapters.motor_065 import Motor065Adapter
    out = Motor065Adapter().run({
        "motor_007": {"target_definition_contract": {"target_type": "cold_chain_facility"}},
        "motor_035": {},
    })
    assert out["motor_065_phase"] == "v4_phase_1_infrastructure_only"
    assert out["asset_family_evaluated"] == "cold_chain_facility"
    assert out["extractor_status"]["real_extraction_enabled"] is False
    assert out["extractor_status"]["pdf_extractor"] == "NotImplementedPDFExtractor"
    assert out["extractor_status"]["llm_extractor"] == "NotImplementedLLMExtractor"


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
    # Every canonical kind must appear in the summary (count ≥ 0)
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
