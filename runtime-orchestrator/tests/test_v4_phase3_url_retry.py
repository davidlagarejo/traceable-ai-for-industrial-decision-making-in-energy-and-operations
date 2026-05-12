"""V4 Phase 3 tests — URL fetching + multi-shot retry on validation failure.

Tests use mocks throughout (no real HTTP, no real Anthropic API). The
real pieces are exercised in unit tests for parsing + scheme rejection;
network calls are blocked.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

import pytest

from runtime_orchestrator.industrial_research_engine import (
    AnthropicLLMExtractor,
    ExtractionOrchestrator,
    KNOWLEDGE_KINDS,
    KnowledgeValidationError,
    LLMExtractionRequest,
    LLMExtractionResult,
    MemoryState,
    PDFExtractionResult,
    URLFetchError,
    fetch_pdf,
    is_url,
)
from runtime_orchestrator.industrial_research_engine.url_pdf_fetcher import (
    _is_pdf_content_type,
    _slug_from_url,
)


# ── URL detection ──────────────────────────────────────────────────────


def test_is_url_recognizes_https():
    assert is_url("https://example.com/doc.pdf") is True


def test_is_url_recognizes_http():
    assert is_url("http://example.com/doc.pdf") is True


def test_is_url_rejects_local_path():
    assert is_url("/Users/davidlagarejo/foo.pdf") is False
    assert is_url("relative/path.pdf") is False
    assert is_url("") is False


def test_is_url_rejects_no_host():
    assert is_url("https://") is False


# ── Scheme allow-list ─────────────────────────────────────────────────


def test_fetch_pdf_rejects_http_scheme():
    with pytest.raises(URLFetchError, match="scheme.*not allowed"):
        fetch_pdf("http://example.com/x.pdf")


def test_fetch_pdf_rejects_file_scheme():
    with pytest.raises(URLFetchError, match="scheme.*not allowed"):
        fetch_pdf("file:///etc/passwd")


def test_fetch_pdf_rejects_ftp_scheme():
    with pytest.raises(URLFetchError, match="scheme.*not allowed"):
        fetch_pdf("ftp://example.com/x.pdf")


def test_fetch_pdf_rejects_no_host():
    with pytest.raises(URLFetchError):
        fetch_pdf("https:///x.pdf")


# ── Content-Type validation ───────────────────────────────────────────


def test_is_pdf_content_type_accepts_application_pdf():
    assert _is_pdf_content_type("application/pdf", "https://x.com/anything") is True


def test_is_pdf_content_type_accepts_octet_stream_with_pdf_ext():
    assert _is_pdf_content_type("application/octet-stream", "https://x.com/doc.pdf") is True


def test_is_pdf_content_type_rejects_html():
    assert _is_pdf_content_type("text/html", "https://x.com/doc.pdf") is False


def test_is_pdf_content_type_rejects_octet_stream_without_pdf_ext():
    assert _is_pdf_content_type("application/octet-stream", "https://x.com/data") is False


# ── Slug generation ───────────────────────────────────────────────────


def test_slug_from_url_uses_filename():
    assert _slug_from_url("https://doe.gov/path/iiar-bulletin-109.pdf").startswith("iiar-bulletin-109")


def test_slug_from_url_strips_special_chars():
    out = _slug_from_url("https://example.com/file with spaces!@#.pdf")
    assert " " not in out
    assert "@" not in out


def test_slug_from_url_ensures_pdf_suffix():
    out = _slug_from_url("https://example.com/doc")
    assert out.endswith(".pdf")


# ── HTTP mocked: max size enforcement ─────────────────────────────────


def test_fetch_pdf_rejects_oversize_content_length(monkeypatch):
    """Mock urlopen to return a Content-Length header exceeding max_bytes."""
    from runtime_orchestrator.industrial_research_engine import url_pdf_fetcher
    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/pdf", "Content-Length": str(100 * 1024 * 1024)}
    fake_response.__enter__ = lambda s: fake_response
    fake_response.__exit__ = lambda *a: None
    monkeypatch.setattr(url_pdf_fetcher.urllib.request, "urlopen", MagicMock(return_value=fake_response))
    with pytest.raises(URLFetchError, match="too large"):
        fetch_pdf("https://example.com/big.pdf", max_bytes=10 * 1024 * 1024)


def test_fetch_pdf_rejects_non_pdf_content_type(monkeypatch):
    from runtime_orchestrator.industrial_research_engine import url_pdf_fetcher
    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "text/html"}
    fake_response.__enter__ = lambda s: fake_response
    fake_response.__exit__ = lambda *a: None
    monkeypatch.setattr(url_pdf_fetcher.urllib.request, "urlopen", MagicMock(return_value=fake_response))
    with pytest.raises(URLFetchError, match="not a PDF"):
        fetch_pdf("https://example.com/page")


def test_fetch_pdf_writes_to_dest_dir(monkeypatch, tmp_path):
    from runtime_orchestrator.industrial_research_engine import url_pdf_fetcher
    pdf_bytes = b"%PDF-1.4 fake pdf content"
    fake_response = MagicMock()
    fake_response.headers = {"Content-Type": "application/pdf"}
    fake_response.read = MagicMock(side_effect=[pdf_bytes, b""])
    fake_response.__enter__ = lambda s: fake_response
    fake_response.__exit__ = lambda *a: None
    monkeypatch.setattr(url_pdf_fetcher.urllib.request, "urlopen", MagicMock(return_value=fake_response))

    result = fetch_pdf("https://example.com/test.pdf", dest_dir=tmp_path)
    assert result.local_path.exists()
    assert result.local_path.read_bytes() == pdf_bytes
    assert result.bytes_downloaded == len(pdf_bytes)
    assert result.url == "https://example.com/test.pdf"


# ── Multi-shot retry in orchestrator ──────────────────────────────────


class _BadThenGoodLLM:
    """First call returns invalid payload, second call returns valid."""

    def __init__(self, good_payload: dict) -> None:
        self.good = good_payload
        self.call_count = 0

    def extract(self, request):
        self.call_count += 1
        if self.call_count == 1:
            # Missing falsification_conditions — will be rejected
            return LLMExtractionResult(
                knowledge_payload={
                    "id": "retry_test",
                    "version": "1.0.0",
                    "knowledge_kind": "pattern",
                    "asset_families": ["manufacturing_facility"],
                    "anti_families": [],
                    "trigger_conditions": ["test"],
                    "anti_triggers": [],
                    "falsification_conditions": [],  # ← invalid
                    "evidence_required": ["test"],
                    "financial_translation": "x",
                    "tad_actions": ["VALIDATE_LOSS_PATTERN"],
                    "allowed_language": "test allowed language",
                    "prohibited_language": [],
                    "claim_ceiling": "L2",
                    "source_basis": [{"source_id": "doe_amo_best_practices", "confidence": "high"}],
                },
                model_id="test",
            )
        # Second call: corrected payload
        return LLMExtractionResult(knowledge_payload=self.good, model_id="test")


class _AlwaysBadLLM:
    """Always returns invalid payload — used to test retry exhaustion."""

    def __init__(self) -> None:
        self.call_count = 0

    def extract(self, request):
        self.call_count += 1
        return LLMExtractionResult(
            knowledge_payload={
                "id": "bad_test",
                "version": "1.0.0",
                "knowledge_kind": "pattern",
                "asset_families": [],  # ← invalid: empty
                "trigger_conditions": [],
                "falsification_conditions": [],
                "evidence_required": [],
                "tad_actions": [],
                "allowed_language": "",
                "prohibited_language": [],
                "claim_ceiling": "L2",
                "source_basis": [],
            },
            model_id="test",
        )


class _StubPDF:
    def extract(self, source_url, **opts):
        return PDFExtractionResult(source_url=source_url, text="stub text", page_count=1)


def _good_pattern_payload(combo_id="retry_recovery"):
    return {
        "id": combo_id,
        "version": "1.0.0",
        "knowledge_kind": "pattern",
        "asset_families": ["manufacturing_facility"],
        "anti_families": [],
        "trigger_conditions": ["process heat plausible"],
        "anti_triggers": [],
        "falsification_conditions": ["thermal share < 20% confirmed"],
        "evidence_required": ["thermal map", "fuel basis"],
        "financial_translation": "Capital depends on thermal duty.",
        "tad_actions": ["VALIDATE_LOSS_PATTERN"],
        "allowed_language": "Thermal duty is structurally plausible.",
        "prohibited_language": ["ROI"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "doe_amo_best_practices", "confidence": "high"}],
    }


@pytest.fixture
def tmp_pending(tmp_path, monkeypatch):
    from runtime_orchestrator.industrial_research_engine import engine, memory
    pending = tmp_path / "knowledge_pending"
    mem = tmp_path / "knowledge_memory"
    for kind in KNOWLEDGE_KINDS:
        (pending / kind).mkdir(parents=True, exist_ok=True)
    for st in MemoryState:
        (mem / st.value).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(engine, "_PENDING_ROOT", pending)
    monkeypatch.setattr(engine, "_AUDIT_LOG", pending / "log.jsonl")
    monkeypatch.setattr(memory, "_PENDING_ROOT", pending)
    monkeypatch.setattr(memory, "_MEMORY_ROOT", mem)
    monkeypatch.setattr(memory, "_AUDIT_LOG", mem / "log.jsonl")
    return tmp_path, pending, mem


def test_orchestrator_retries_on_validation_failure(tmp_pending):
    """First LLM call returns invalid, second returns valid. Orchestrator
    catches the error, sends feedback, and the second attempt succeeds."""
    tmp_path, pending, mem = tmp_pending
    good = _good_pattern_payload("retry_recovery_works")
    llm = _BadThenGoodLLM(good_payload=good)
    orch = ExtractionOrchestrator(pdf_extractor=_StubPDF(), llm_extractor=llm)
    result = orch.orchestrate(
        source_id="doe_amo_best_practices",
        source_url="dummy_path.pdf",
        topic="thermal_process",
        target_kind="pattern",
        max_retries=2,
    )
    assert result.propose_result is not None
    assert result.retry_count == 1
    assert len(result.validation_errors) == 1
    assert "falsification_conditions" in result.validation_errors[0]
    assert llm.call_count == 2  # initial + 1 retry
    assert (pending / "pattern" / "retry_recovery_works.v1.json").exists()


def test_orchestrator_exhausts_retries_and_raises(tmp_pending):
    """When the LLM never produces a valid payload, the orchestrator
    raises KnowledgeValidationError after exhausting max_retries."""
    llm = _AlwaysBadLLM()
    orch = ExtractionOrchestrator(pdf_extractor=_StubPDF(), llm_extractor=llm)
    with pytest.raises(KnowledgeValidationError, match="after .* attempt"):
        orch.orchestrate(
            source_id="doe_amo_best_practices",
            source_url="dummy_path.pdf",
            topic="thermal_process",
            target_kind="pattern",
            max_retries=2,
        )
    assert llm.call_count == 3  # initial + 2 retries


def test_orchestrator_succeeds_on_first_attempt_no_retries(tmp_pending):
    """When the LLM gets it right first try, retry_count=0 and no retry feedback prompt."""
    tmp_path, pending, mem = tmp_pending
    good = _good_pattern_payload("first_attempt_wins")

    class _GoodLLM:
        def __init__(self):
            self.call_count = 0
        def extract(self, request):
            self.call_count += 1
            return LLMExtractionResult(knowledge_payload=good, model_id="test")

    llm = _GoodLLM()
    orch = ExtractionOrchestrator(pdf_extractor=_StubPDF(), llm_extractor=llm)
    result = orch.orchestrate(
        source_id="doe_amo_best_practices",
        source_url="dummy.pdf",
        topic="thermal_process",
        target_kind="pattern",
    )
    assert result.retry_count == 0
    assert result.validation_errors == []
    assert llm.call_count == 1


# ── CLI URL handling smoke ────────────────────────────────────────────


def test_cli_accepts_url_flag_in_help():
    """The --pdf-path help text mentions URL support after V4 P3."""
    import subprocess
    script = Path(__file__).resolve().parents[1] / "scripts" / "extract_from_pdf.py"
    r = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0
    assert "URL" in r.stdout
    assert "https" in r.stdout.lower()


def test_cli_help_mentions_retry_flag():
    import subprocess
    script = Path(__file__).resolve().parents[1] / "scripts" / "extract_from_pdf.py"
    r = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert "--max-retries" in r.stdout
