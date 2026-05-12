"""Adapter for motor_065 — Industrial Knowledge Extractor (Layer A).

V4 Phase 1 wires the industrial_research_engine.ExtractionOrchestrator
into the pipeline. motor_065 is Layer A (knowledge production) and
emits an extraction REPORT (what would be extracted, what stub status
is, what pending proposals exist) — but does NOT itself call the real
PDF/LLM extractors during a pipeline run.

Real extraction happens out-of-band (via the CLI or future motor_028
+ motor_065 + extraction_orchestrator chain). motor_065's role in V4
P1 is to surface the EXTRACTION SURFACE of the case: which sources
the case touches, which topics would be investigated, what's pending
in knowledge_pending/ that the dashboard should review.

This adapter is intentionally low-touch in V4 P1: it does NOT inject
extracted knowledge into the case run. That decoupling matters — the
human approves knowledge ONCE at the dashboard, not per case.
"""
from __future__ import annotations

from typing import Any

from ..industrial_research_engine import (
    ExtractionOrchestrator,
    KNOWLEDGE_KINDS,
    MemoryState,
    list_in_state,
)
from ..industrial_research_engine.memory import list_pending
from ..industrial_research_engine.routing import research_priority_for
from .base import BaseMotorAdapter


def _text(value: Any) -> str:
    return str(value or "").strip()


class Motor065Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_065"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_035"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
        m035 = inputs.get("motor_035", {}) if isinstance(inputs.get("motor_035", {}), dict) else {}

        target_definition = m007.get("target_definition_contract", {}) if isinstance(m007.get("target_definition_contract", {}), dict) else {}
        asset_family = _text(target_definition.get("target_type") or target_definition.get("asset_family"))

        # Reuse motor_007's evidence tokens as research clues (no new content).
        facility_clues = list(target_definition.get("facility_evidence_tokens", []) or [])
        process_clues = list(target_definition.get("process_evidence_tokens", []) or [])

        # Stage 1: routing plan (uses V4 P0 routing + source catalog).
        research_plan = research_priority_for(
            asset_family,
            process_clues=process_clues + facility_clues,
        ) if asset_family else {
            "asset_family": "",
            "topics_ordered": [],
            "sources_per_topic": {},
            "clue_weights": {},
        }

        # Stage 2: extraction orchestrator status. Real extractor stubs in V4 P1.
        orchestrator = ExtractionOrchestrator()
        extractor_status = {
            "pdf_extractor": type(orchestrator.pdf_extractor).__name__,
            "llm_extractor": type(orchestrator.llm_extractor).__name__,
            "real_extraction_enabled": False,  # flips to True in V4 P2
        }

        # Stage 3: pending knowledge by kind (so dashboard / motor_054 see
        # what's queued for human review).
        pending_summary: dict[str, int] = {}
        pending_total = 0
        for kind in KNOWLEDGE_KINDS:
            try:
                rows = list_pending(kind)
            except Exception:  # noqa: BLE001
                rows = []
            pending_summary[kind] = len(rows)
            pending_total += len(rows)

        # Stage 4: approved knowledge memory snapshot (counts per state).
        memory_counts: dict[str, int] = {}
        for state in MemoryState:
            try:
                memory_counts[state.value] = len(list_in_state(state))
            except Exception:  # noqa: BLE001
                memory_counts[state.value] = 0

        return {
            "asset_family_evaluated": asset_family,
            "research_priority_plan": research_plan,
            "extractor_status": extractor_status,
            "knowledge_pending_summary": pending_summary,
            "knowledge_pending_total": pending_total,
            "knowledge_memory_counts": memory_counts,
            "motor_065_phase": "v4_phase_1_infrastructure_only",
            "real_extraction_invocations": 0,  # increments when V4 P2 wires real run-time extraction
        }
