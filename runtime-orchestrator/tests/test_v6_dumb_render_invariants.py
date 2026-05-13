"""V6 P10 — DUMB Render invariant tests.

V6 Stability prompt item 5: "RECONSTRUIR EL REPORT COMPOSER → DUMB_RENDER_LAYER".

motor_015/016/017/019 collectively form the composer / rendering layer
(Layer E in layer_registry). They MUST NOT:

  - create new logic
  - combine hypotheses
  - activate patterns
  - generate nuggets
  - change TAD
  - degrade epistemology
  - inflate claim counts

They MAY ONLY:

  - read upstream objects
  - reformulate / translate / explain (motor_019 narrator)
  - render LaTeX (motor_017)
  - assemble Output Blocks → Report Package

This test suite is the static invariant gate. Each test asserts a
contamination-resistance property by inspecting source code and
output shape.

Phase 0 anchor: "DUMB_RENDER_LAYER — solo renderiza objetos ya aprobados".
"""
from __future__ import annotations

from pathlib import Path

import pytest


_RUNTIME_SRC = Path(__file__).resolve().parents[1] / "src" / "runtime_orchestrator"
_ADAPTERS = _RUNTIME_SRC / "adapters"


def _source(motor_id: str) -> str:
    return (_ADAPTERS / f"{motor_id}.py").read_text(encoding="utf-8")


# ── motor_019 narrator — V5 P7 orphan-claim detector wired ─────────


def test_motor_019_has_orphan_claim_validator_wired():
    """motor_019._lint_text must call narrator_validator.check_orphan_claims."""
    src = _source("motor_019")
    assert "from ..narrator_validator import" in src
    assert "check_orphan_claims" in src
    assert "orphan_claim_findings" in src


def test_motor_019_carries_epistemic_law_in_docstring():
    """motor_019 must publicly declare its Phase 0 role."""
    src = _source("motor_019")
    assert "professional writer, not an analyst" in src
    assert "NOT introduce new claims" in src or "not introduce new claims" in src


def test_motor_019_forbids_underwriting_phrases():
    """motor_019 must carry the forbidden phrase list (anti-acquisition framing)."""
    src = _source("motor_019")
    assert "_FORBIDDEN_PHRASES" in src
    # At least common contamination phrases present in the forbidden set
    for phrase in ("due diligence", "underwriting"):
        assert phrase in src.lower()


def test_motor_019_has_hard_closure_phrase_list():
    """motor_019 must reject closure phrases ('verified', 'confirmed' etc.)."""
    src = _source("motor_019")
    assert "_HARD_CLOSURE_PHRASES" in src


# ── motor_017 LaTeX render — no analytical logic ───────────────────


def test_motor_017_does_NOT_import_analytical_motors():
    """motor_017 must read only motor_014/016/025/036/055-063 results.
    It must NOT import structural_intelligence, congruence_intelligence,
    or industrial_research_engine analytical helpers."""
    src = _source("motor_017")
    forbidden_imports = [
        "from ..structural_intelligence",
        "from runtime_orchestrator.structural_intelligence",
        "import structural_intelligence",
        "from runtime_orchestrator.congruence_intelligence",
        "from ..congruence_intelligence",
        "from runtime_orchestrator.industrial_research_engine",
        "from ..industrial_research_engine",
    ]
    for forbidden in forbidden_imports:
        assert forbidden not in src, (
            f"motor_017 must not import analytical helper: {forbidden}"
        )


def test_motor_017_reads_motor_016_report_package():
    """motor_017 must consume motor_016's report_package as its primary input."""
    src = _source("motor_017")
    assert 'inputs.get("motor_016"' in src or "motor_016" in src
    assert "report_package" in src


def test_motor_017_outputs_pdf_only():
    """motor_017 output dict should be primarily PDF-render metadata,
    not analytical claims."""
    src = _source("motor_017")
    # Must emit pdf_path / pdf_paths
    assert '"pdf_path"' in src
    assert '"compilation_status"' in src


# ── motor_016 Report Package — no claim invention ──────────────────


def test_motor_016_does_NOT_create_inference_cases():
    """motor_016 must NOT call motor_013/014's case-builders. It only
    assembles already-existing output blocks."""
    src = _source("motor_016")
    forbidden_calls = [
        "build_inference_case", "_build_scenario_space",
        "_compute_scores", "_score_inference_case",
    ]
    for call in forbidden_calls:
        assert call not in src, (
            f"motor_016 must not call analytical builder: {call}"
        )


def test_motor_016_reads_output_blocks_from_motor_015():
    """motor_016 must consume motor_015's output_blocks."""
    src = _source("motor_016")
    assert "motor_015" in src
    assert "output_block" in src


# ── motor_015 Output Block — passes through inference records ──────


def test_motor_015_does_NOT_invent_claim_text():
    """motor_015 must not create new claim language. It maps motor_014
    outputs into block formats."""
    src = _source("motor_015")
    # Must NOT import or call analytical case-builders from upstream layers.
    # Local _build_scenario_space_block / format helpers are render-layer
    # only and OK.
    forbidden_calls = [
        "from ..structural_intelligence",
        "from runtime_orchestrator.structural_intelligence",
        "from ..congruence_intelligence",
        "from ..industrial_research_engine import propose_knowledge",
    ]
    for call in forbidden_calls:
        assert call not in src, (
            f"motor_015 must not invoke analytical builder: {call}"
        )


def test_motor_015_reads_motor_014_records():
    """motor_015 must read motor_014's inference_records."""
    src = _source("motor_015")
    assert "motor_014" in src
    assert "inference_records" in src


# ── No composer motor imports Anthropic / OpenAI ───────────────────


def test_no_composer_motor_imports_external_llm_sdk():
    """Phase 0 anchor: LLM appears ONLY in motor_019 (via Codex CLI).
    None of motor_015/016/017 may import an LLM SDK directly."""
    for motor_id in ("motor_015", "motor_016", "motor_017"):
        src = _source(motor_id)
        for forbidden in ("import anthropic", "import openai", "from anthropic",
                          "from openai", "import ollama"):
            assert forbidden not in src, (
                f"{motor_id} must not import LLM SDK: {forbidden}"
            )


def test_motor_019_is_only_motor_with_codex_call():
    """Only motor_019 may invoke an external LLM CLI (Codex). Other
    motors must stay deterministic."""
    motor_019_src = _source("motor_019")
    assert "_call_codex" in motor_019_src or "_CODEX_CLI" in motor_019_src

    for motor_id in ("motor_015", "motor_016", "motor_017", "motor_014",
                      "motor_013", "motor_034", "motor_045", "motor_053",
                      "motor_054", "motor_033"):
        src = _source(motor_id)
        assert "_call_codex" not in src, (
            f"{motor_id} must not invoke Codex (Phase 0 violation)"
        )


# ── Composer chain reads in correct order ──────────────────────────


def test_composer_chain_ordering_motor_015_reads_motor_014():
    src = _source("motor_015")
    # motor_015 input_motor_ids should include motor_014
    assert '"motor_014"' in src


def test_composer_chain_ordering_motor_016_reads_motor_015_and_019():
    src = _source("motor_016")
    assert "motor_015" in src
    assert "motor_019" in src


def test_composer_chain_ordering_motor_017_reads_motor_016():
    src = _source("motor_017")
    # motor_017 input_motor_ids list must include motor_016
    assert '"motor_016"' in src


# ── No composer emits unsupported numeric tokens ──────────────────


def test_motor_019_lint_text_validates_numeric_tokens():
    """motor_019's lint must filter unsupported numeric tokens to
    prevent the LLM from making up numbers."""
    src = _source("motor_019")
    assert "_normalized_numeric_tokens" in src
    assert "unsupported_numeric_tokens" in src
