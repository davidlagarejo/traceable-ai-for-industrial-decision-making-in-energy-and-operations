"""Extraction orchestrator (V4 P1 item 2).

Glues the four extraction stages:

  1. SOURCE — identify catalog source_id (via source_catalog / motor_028)
  2. PDF    — extract raw text from the source (pdf_extraction_interface)
  3. LLM    — structure the text into KnowledgeObject candidate (llm_extraction_interface)
  4. PROPOSE — validate + land in knowledge_pending/<kind>/ via engine.propose_knowledge

The orchestrator is INTENTIONALLY THIN. Each stage delegates to a
swappable component (Protocol-based) so V4 P2 can replace any of them
without rewriting orchestrator code.

In V4 P1:
  - Stage 1 works (uses source_catalog)
  - Stage 2 returns NotImplementedError when called
  - Stage 3 returns NotImplementedError when called
  - Stage 4 works (uses V4 P0 propose_knowledge)

So orchestrate(...) ends up raising NotImplementedError UNTIL stages
2+3 are replaced with real implementations. That's the design.

A separate `orchestrate_from_manual_text(...)` path skips stages 1+2
(user supplies text + source_id directly) — this is what the CLI uses
for V4 P1 manual proposals.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..source_catalog import source_by_id
from .engine import propose_knowledge
from .llm_extraction_interface import (
    LLMExtractor,
    LLMExtractionRequest,
    default_llm_extractor,
)
from .pdf_extraction_interface import (
    PDFExtractor,
    PDFExtractionResult,
    default_pdf_extractor,
)


@dataclass
class ExtractionPlan:
    """What the orchestrator decided to do for a given request."""
    source_id: str
    source_url: str
    topic: str
    target_kind: str
    asset_families_hint: list[str] = field(default_factory=list)
    pdf_extractor_class: str = ""
    llm_extractor_class: str = ""


@dataclass
class ExtractionResult:
    plan: ExtractionPlan
    pdf_result: PDFExtractionResult | None = None
    llm_payload: dict[str, Any] | None = None
    propose_result: dict[str, Any] | None = None
    error: str = ""


class ExtractionOrchestrator:
    """The framework's extraction conductor.

    Configurable extractors so V4 P2+ swaps stubs for real implementations:

        orch = ExtractionOrchestrator(
            pdf_extractor=my_pdfminer_extractor,
            llm_extractor=my_anthropic_extractor,
        )
        result = orch.orchestrate(source_id="iiar_bulletin_109",
                                   source_url="...", topic="refrigeration",
                                   target_kind="pattern")
    """

    def __init__(
        self,
        *,
        pdf_extractor: PDFExtractor | None = None,
        llm_extractor: LLMExtractor | None = None,
    ) -> None:
        self.pdf_extractor: PDFExtractor = pdf_extractor or default_pdf_extractor()
        self.llm_extractor: LLMExtractor = llm_extractor or default_llm_extractor()

    # ── Stage 1: source identification ──────────────────────────────

    def _plan(
        self,
        *,
        source_id: str,
        source_url: str,
        topic: str,
        target_kind: str,
        asset_families_hint: list[str] | None = None,
    ) -> ExtractionPlan:
        catalog_entry = source_by_id(source_id)
        if not catalog_entry:
            raise ValueError(
                f"source_id {source_id!r} is not in the industrial_source_catalog. "
                "Add it to the catalog (or propose it as new knowledge of kind "
                "'source') before requesting extraction."
            )
        return ExtractionPlan(
            source_id=source_id,
            source_url=source_url or "",
            topic=topic,
            target_kind=target_kind,
            asset_families_hint=list(asset_families_hint or []),
            pdf_extractor_class=type(self.pdf_extractor).__name__,
            llm_extractor_class=type(self.llm_extractor).__name__,
        )

    # ── Full orchestration: source → pdf → llm → propose ────────────

    def orchestrate(
        self,
        *,
        source_id: str,
        source_url: str,
        topic: str,
        target_kind: str = "pattern",
        asset_families_hint: list[str] | None = None,
        proposed_by: str = "industrial_research_engine",
    ) -> ExtractionResult:
        plan = self._plan(
            source_id=source_id,
            source_url=source_url,
            topic=topic,
            target_kind=target_kind,
            asset_families_hint=asset_families_hint,
        )

        # Stage 2: PDF
        pdf_result = self.pdf_extractor.extract(source_url)  # raises in V4 P1

        # Stage 3: LLM
        llm_result = self.llm_extractor.extract(
            LLMExtractionRequest(
                raw_text=pdf_result.text,
                topic=topic,
                source_id=source_id,
                target_kind=target_kind,
                asset_families_hint=plan.asset_families_hint,
            )
        )

        # Stage 4: validate + propose
        propose_result = propose_knowledge(
            llm_result.knowledge_payload,
            kind=target_kind,
            proposed_by=proposed_by,
        )

        return ExtractionResult(
            plan=plan,
            pdf_result=pdf_result,
            llm_payload=llm_result.knowledge_payload,
            propose_result=propose_result,
        )

    # ── Manual / paste-in path (used by the CLI in V4 P1) ─────────

    def orchestrate_from_manual_text(
        self,
        *,
        source_id: str,
        topic: str,
        target_kind: str,
        knowledge_payload: dict[str, Any],
        asset_families_hint: list[str] | None = None,
        proposed_by: str = "manual_extraction",
    ) -> ExtractionResult:
        """Skip stages 2+3. Caller has already produced a validated-shape
        knowledge_payload (typically a human reading the source and typing
        the JSON, or a test fixture). The orchestrator validates and
        proposes it normally.
        """
        plan = self._plan(
            source_id=source_id,
            source_url="",
            topic=topic,
            target_kind=target_kind,
            asset_families_hint=asset_families_hint,
        )
        # source provenance auto-stamped if missing
        sb = list(knowledge_payload.get("source_basis", []) or [])
        if not any(s.get("source_id") == source_id for s in sb if isinstance(s, dict)):
            sb.append({"source_id": source_id, "confidence": "manual"})
            knowledge_payload = {**knowledge_payload, "source_basis": sb}
        # extraction_metadata stamp
        em = dict(knowledge_payload.get("extraction_metadata", {}) or {})
        em.setdefault("topic", topic)
        em.setdefault("source_id", source_id)
        em.setdefault("extraction_path", "manual_orchestrator")
        knowledge_payload = {**knowledge_payload, "extraction_metadata": em}

        propose_result = propose_knowledge(
            knowledge_payload, kind=target_kind, proposed_by=proposed_by
        )
        return ExtractionResult(
            plan=plan,
            llm_payload=knowledge_payload,
            propose_result=propose_result,
        )
