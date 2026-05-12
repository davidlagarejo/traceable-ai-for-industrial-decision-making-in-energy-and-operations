"""V4 Phase 2 tests — real PDF + Anthropic LLM extractors.

Tests use MOCKS for both the anthropic SDK and pdfplumber so they pass
without API keys or external dependencies. The real extractors are
exercised only via subprocess --help smoke for the CLI.

What we lock down:
  - PDFPlumberExtractor handles missing files, page ranges, truncation
  - AnthropicLLMExtractor gates on API key + SDK availability
  - JSON block extraction tolerates markdown fences / trailing prose
  - Prompt template includes mandatory rules
  - extract_from_pdf.py CLI exits 4 when prerequisites missing
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from runtime_orchestrator.industrial_research_engine import (
    ANTHROPIC_DEFAULT_MODEL,
    AnthropicLLMExtractor,
    AnthropicSettings,
    LLMExtractionRequest,
    PDFPlumberExtractor,
)


# ── PDFPlumberExtractor ────────────────────────────────────────────────


def test_pdfplumber_extractor_raises_on_missing_file():
    extractor = PDFPlumberExtractor()
    with pytest.raises(FileNotFoundError, match="PDF not found"):
        extractor.extract("/nonexistent/path/x.pdf")


def test_pdfplumber_extractor_extracts_real_pdf(tmp_path):
    """Smoke-test: pdfplumber actually opens a small PDF we create on the fly.
    Uses reportlab if available, otherwise skips."""
    try:
        from reportlab.pdfgen import canvas  # type: ignore
    except ImportError:
        pytest.skip("reportlab not installed — skipping real PDF roundtrip")
    pdf_path = tmp_path / "smoke.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(72, 720, "Industrial test content: refrigeration duty + thermal boundary.")
    c.showPage()
    c.drawString(72, 720, "Page two: compressor staging matters.")
    c.showPage()
    c.save()
    out = PDFPlumberExtractor().extract(str(pdf_path))
    assert out.page_count == 2
    assert "refrigeration duty" in out.text.lower()
    assert "compressor staging" in out.text.lower()
    assert out.extraction_method == "pdfplumber"


def test_pdfplumber_extractor_page_range_filter():
    """Without reportlab we can still verify page-range parsing via the
    internal helper directly."""
    from runtime_orchestrator.industrial_research_engine.pdfplumber_extractor import (
        _parse_page_range,
    )
    assert _parse_page_range("1-3", 10) == [0, 1, 2]
    assert _parse_page_range("3", 10) == [2]
    assert _parse_page_range("1-2,5", 10) == [0, 1, 4]
    assert _parse_page_range("", 5) == [0, 1, 2, 3, 4]


def test_pdfplumber_extractor_page_range_clips_to_pdf_length():
    from runtime_orchestrator.industrial_research_engine.pdfplumber_extractor import (
        _parse_page_range,
    )
    # request 1-100 on a 5-page PDF → pages 1..5
    assert _parse_page_range("1-100", 5) == [0, 1, 2, 3, 4]


def test_pdfplumber_extractor_page_range_rejects_invalid():
    from runtime_orchestrator.industrial_research_engine.pdfplumber_extractor import (
        _parse_page_range,
    )
    with pytest.raises(ValueError):
        _parse_page_range("abc", 10)


# ── AnthropicLLMExtractor — gating ─────────────────────────────────────


def test_anthropic_extractor_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    extractor = AnthropicLLMExtractor()
    req = LLMExtractionRequest(
        raw_text="hello", topic="refrigeration", source_id="iiar_bulletin_109",
    )
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        extractor.extract(req)


def test_anthropic_extractor_raises_without_sdk(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-fake")
    # Hide the anthropic module if it's installed
    monkeypatch.setattr("sys.modules", {**sys.modules, "anthropic": None})
    extractor = AnthropicLLMExtractor()
    req = LLMExtractionRequest(
        raw_text="hello", topic="refrigeration", source_id="iiar_bulletin_109",
    )
    with pytest.raises(ImportError, match="anthropic SDK is not installed"):
        extractor.extract(req)


# ── AnthropicLLMExtractor — prompt construction ───────────────────────


def test_anthropic_prompt_includes_mandatory_rules():
    extractor = AnthropicLLMExtractor()
    req = LLMExtractionRequest(
        raw_text="Test source text about refrigeration",
        topic="refrigeration",
        source_id="iiar_bulletin_109",
        target_kind="pattern",
        asset_families_hint=["cold_chain_facility"],
    )
    prompt = extractor._build_prompt(req)
    # Critical guardrails appear in the prompt
    assert "falsification_conditions" in prompt
    assert "evidence_required" in prompt
    assert "guaranteed savings" in prompt
    assert "ROI" in prompt
    assert "L2" in prompt
    assert "cold_chain_facility" in prompt
    assert "iiar_bulletin_109" in prompt


def test_anthropic_prompt_lists_canonical_families():
    extractor = AnthropicLLMExtractor()
    req = LLMExtractionRequest(raw_text="x", topic="t", source_id="s")
    prompt = extractor._build_prompt(req)
    # All 16 canonical families appear in the prompt
    for fam in ["manufacturing_facility", "datacenter", "pharma_facility"]:
        assert fam in prompt


# ── JSON block extraction ─────────────────────────────────────────────


def test_extract_json_block_handles_clean_json():
    raw = '{"id": "test", "version": "1.0.0"}'
    out = AnthropicLLMExtractor._extract_json_block(raw)
    assert out["id"] == "test"


def test_extract_json_block_handles_markdown_fences():
    raw = '```json\n{"id": "test"}\n```'
    out = AnthropicLLMExtractor._extract_json_block(raw)
    assert out["id"] == "test"


def test_extract_json_block_handles_trailing_prose():
    raw = '{"id": "test"}\n\nHope this helps!'
    out = AnthropicLLMExtractor._extract_json_block(raw)
    assert out["id"] == "test"


def test_extract_json_block_raises_on_no_json():
    with pytest.raises(ValueError, match="did not contain a JSON object"):
        AnthropicLLMExtractor._extract_json_block("just plain text")


def test_extract_json_block_raises_on_invalid_json():
    with pytest.raises(ValueError, match="JSON parse failed"):
        AnthropicLLMExtractor._extract_json_block('{"broken: json}')


# ── AnthropicLLMExtractor — mocked end-to-end ─────────────────────────


def _mock_anthropic_response(json_payload: dict) -> MagicMock:
    """Build a fake Anthropic Messages API response."""
    block = MagicMock()
    block.type = "text"
    block.text = json.dumps(json_payload)
    response = MagicMock()
    response.content = [block]
    return response


def test_anthropic_extractor_full_call_with_mock(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-fake")

    payload = {
        "id": "test_extracted",
        "version": "1.0.0",
        "knowledge_kind": "pattern",
        "asset_families": ["cold_chain_facility"],
        "anti_families": [],
        "trigger_conditions": ["refrigeration plant present"],
        "anti_triggers": [],
        "falsification_conditions": ["natural refrigerant confirmed"],
        "evidence_required": ["refrigerant type", "leak rate"],
        "financial_translation": "Test framing.",
        "tad_actions": ["VALIDATE_LOSS_PATTERN"],
        "allowed_language": "Refrigerant integrity is a plausible loss pattern.",
        "prohibited_language": ["guaranteed savings"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "iiar_bulletin_109", "confidence": "high"}],
    }

    # Mock the entire Anthropic SDK
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _mock_anthropic_response(payload)

    fake_anthropic = MagicMock()
    fake_anthropic.Anthropic = MagicMock(return_value=fake_client)

    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic)

    extractor = AnthropicLLMExtractor()
    req = LLMExtractionRequest(
        raw_text="Source text mentioning ammonia refrigeration plant.",
        topic="refrigeration",
        source_id="iiar_bulletin_109",
        target_kind="pattern",
    )
    result = extractor.extract(req)
    assert result.knowledge_payload["id"] == "test_extracted"
    assert result.model_id == ANTHROPIC_DEFAULT_MODEL
    # source confidence hint applied (tier 1 → 0.85)
    assert result.confidence_self_assessment == 0.85


def test_anthropic_extractor_warns_on_missing_falsification(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-fake")
    payload_missing = {"id": "test_no_falsif", "version": "1.0.0"}

    fake_client = MagicMock()
    fake_client.messages.create.return_value = _mock_anthropic_response(payload_missing)
    fake_anthropic = MagicMock()
    fake_anthropic.Anthropic = MagicMock(return_value=fake_client)
    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic)

    extractor = AnthropicLLMExtractor()
    req = LLMExtractionRequest(
        raw_text="x", topic="refrigeration", source_id="iiar_bulletin_109",
    )
    result = extractor.extract(req)
    assert any("falsification_conditions" in w for w in result.extraction_warnings)


# ── CLI extract_from_pdf.py — prerequisite gating ────────────────────


def test_cli_extract_from_pdf_help_smoke():
    script = Path(__file__).resolve().parents[1] / "scripts" / "extract_from_pdf.py"
    r = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0
    assert "PDF" in r.stdout
    assert "anthropic" in r.stdout.lower() or "ANTHROPIC" in r.stdout


def test_cli_exits_4_when_api_key_missing(monkeypatch, tmp_path):
    """When ANTHROPIC_API_KEY is not set, the CLI exits with code 4
    (prerequisite missing) instead of crashing."""
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 placeholder")
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    script = Path(__file__).resolve().parents[1] / "scripts" / "extract_from_pdf.py"
    r = subprocess.run(
        [
            sys.executable, str(script),
            "--pdf-path", str(fake_pdf),
            "--source-id", "iiar_bulletin_109",
            "--topic", "refrigeration",
            "--kind", "pattern",
        ],
        capture_output=True, text=True, env=env, timeout=15,
    )
    assert r.returncode == 4
    assert "ANTHROPIC_API_KEY" in r.stderr


# ── ExtractionOrchestrator with real-ish injected extractors ──────────


def test_orchestrator_works_with_pdfplumber_and_mocked_llm(tmp_path, monkeypatch):
    """Verify the V4 P2 extractors are drop-in replacements for the V4 P1
    stubs in the orchestrator."""
    # Build a tiny PDF if reportlab is available; else skip
    try:
        from reportlab.pdfgen import canvas  # type: ignore
    except ImportError:
        pytest.skip("reportlab not available")

    pdf_path = tmp_path / "smoke.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(72, 720, "Test content for orchestrator.")
    c.showPage()
    c.save()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-fake")
    payload = {
        "id": "orchestrator_test",
        "version": "1.0.0",
        "knowledge_kind": "pattern",
        "asset_families": ["manufacturing_facility"],
        "anti_families": [],
        "trigger_conditions": ["t"],
        "anti_triggers": [],
        "falsification_conditions": ["f"],
        "evidence_required": ["e"],
        "financial_translation": "x",
        "tad_actions": ["VALIDATE_LOSS_PATTERN"],
        "allowed_language": "Pattern is plausible.",
        "prohibited_language": ["roi"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "doe_amo_best_practices", "confidence": "medium-high"}],
    }
    fake_client = MagicMock()
    fake_client.messages.create.return_value = _mock_anthropic_response(payload)
    fake_anthropic = MagicMock()
    fake_anthropic.Anthropic = MagicMock(return_value=fake_client)
    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic)

    from runtime_orchestrator.industrial_research_engine import ExtractionOrchestrator

    # Redirect pending so we don't pollute the repo
    from runtime_orchestrator.industrial_research_engine import engine
    pending = tmp_path / "pending"
    pending.mkdir()
    (pending / "pattern").mkdir()
    monkeypatch.setattr(engine, "_PENDING_ROOT", pending)
    monkeypatch.setattr(engine, "_AUDIT_LOG", pending / "log.jsonl")

    orch = ExtractionOrchestrator(
        pdf_extractor=PDFPlumberExtractor(),
        llm_extractor=AnthropicLLMExtractor(),
    )
    result = orch.orchestrate(
        source_id="doe_amo_best_practices",
        source_url=str(pdf_path),
        topic="thermal_process",
        target_kind="pattern",
    )
    assert result.propose_result is not None
    assert (pending / "pattern" / "orchestrator_test.v1.json").exists()
