"""Adapter for motor_065 — Industrial Knowledge Extractor surface (Phase 1).

motor_065 is the Phase 1 surface motor that reports the EXTRACTION
SURFACE of a case to downstream consumers (dashboard, motor_054):

  - which research topics are prioritised for the case's asset family
    (via industrial_research_engine.routing.research_priority_for)
  - the source catalogue priority list per topic
  - the count of knowledge proposals currently pending human review
  - the count of approved/rejected/deprecated knowledge entries

motor_065 does NOT itself perform extraction during a pipeline run.
Extraction is deterministic and lives in `runtime_orchestrator.zlab_skill`
(local_pdf_autodraft / extractor / research_loop_controller). Those
modules run out-of-band; their outputs land in `knowledge_pending/<kind>/`
and are reviewed via the dashboard `/revisar` page.

This decoupling matters constitutionally: human approval of knowledge
happens ONCE at the dashboard, never per case. The case pipeline only
reads APPROVED knowledge (already in `knowledge_memory/approved/`).
"""
from __future__ import annotations

from typing import Any

from ..industrial_research_engine import (
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

        # Stage 1: routing plan (uses the catalog + taxonomy).
        research_plan = research_priority_for(
            asset_family,
            process_clues=process_clues + facility_clues,
        ) if asset_family else {
            "asset_family": "",
            "topics_ordered": [],
            "sources_per_topic": {},
            "clue_weights": {},
        }

        # Stage 2: extraction surface status. The actual extraction is
        # done by zlab_skill (deterministic) out-of-band, not here.
        extractor_status = {
            "extraction_path": "deterministic_via_zlab_skill",
            "pdf_pattern_matcher": "zlab_skill.local_pdf_autodraft",
            "extraction_seed_builder": "zlab_skill.extractor",
            "research_loop": "zlab_skill.research_loop_controller",
            "llm_in_extraction": False,
        }

        # Stage 3: pending knowledge by kind (so dashboard / motor_054
        # can see what's queued for human review).
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
            "motor_065_phase": "phase_1_surface_reporter",
        }
