"""Research routing — structural topic + source priority planner.

Decides what to investigate given:
  - asset_family
  - process clues (tokens from motor_007)
  - thermal clues
  - emissions clues
  - utility clues
  - logistics clues

The routing returns a structural priority list (topics + sources to
consult) but does NOT perform extraction itself. Real extraction is
deterministic and lives in `runtime_orchestrator.zlab_skill`:
  - local_pdf_autodraft (rule-based PDF pattern matcher)
  - extractor (seed builder)
  - research_loop_controller (loop policies, stop conditions)

Phase 0 law: the LLM is never the analytical engine. The extraction
machinery is deterministic. The LLM only appears in motor_019 as a
post-framework narrator.

The skeleton is testable: given inputs, returns deterministic ordered
topic lists + source recommendations from the catalog.
"""
from __future__ import annotations

from typing import Any

from ..source_catalog import sources_for_family, sources_for_tag
from .taxonomy import INDUSTRIAL_TAXONOMY, topics_for_family


class NotImplementedExtractor:
    """Fail-loud placeholder — redirects callers to the real extractors.

    Deterministic extraction lives in `runtime_orchestrator.zlab_skill`:
      - `local_pdf_autodraft.py` — rule-based PDF pattern matching
      - `extractor.py` — extraction seed builder
      - `research_loop_controller.py` — loop policies + stop conditions

    This stub exists so any code path that wrongly assumes an
    LLM-driven extractor sits behind the Industrial Research Engine
    fails loud and gets redirected. Phase 0 law: the LLM is never the
    analytical engine."""

    def extract(self, source_url: str, topic: str, source_type: str = "pdf") -> dict[str, Any]:
        raise NotImplementedError(
            "industrial_research_engine.extract_knowledge is intentionally a stub. "
            "Automated extraction is deterministic and lives in "
            "runtime_orchestrator.zlab_skill (local_pdf_autodraft / extractor / "
            "research_loop_controller). "
            f"Caller asked to extract from {source_url!r} on topic {topic!r}."
        )


def research_priority_for(
    asset_family: str,
    process_clues: list[str] | None = None,
    thermal_clues: list[str] | None = None,
    emissions_clues: list[str] | None = None,
    utility_clues: list[str] | None = None,
    logistics_clues: list[str] | None = None,
) -> dict[str, Any]:
    """Return a research-priority plan for an asset family + case clues.

    The plan is purely STRUCTURAL — it lists what to investigate, not
    what conclusions to reach. Real extraction would walk this plan.

    Output:
      {
        "asset_family": ...,
        "topics_ordered": [...],   # topic IDs in research priority
        "sources_per_topic": {topic: [source_id, ...]},
        "clue_weights": {clue_type: list of keywords},
      }
    """
    process_clues = process_clues or []
    thermal_clues = thermal_clues or []
    emissions_clues = emissions_clues or []
    utility_clues = utility_clues or []
    logistics_clues = logistics_clues or []

    # 1. Start from family priority (if registered) or canonical taxonomy
    base_topics = topics_for_family(asset_family) or list(INDUSTRIAL_TAXONOMY.keys())

    # 2. Re-rank topics by clue weight. A topic that matches a clue keyword
    #    bubbles up in the priority list. Same family-priority is preserved
    #    among unmatched topics.
    clue_text = " ".join(
        process_clues + thermal_clues + emissions_clues + utility_clues + logistics_clues
    ).lower()

    def topic_match_score(topic: str) -> int:
        info = INDUSTRIAL_TAXONOMY.get(topic, {})
        score = 0
        for kw in info.get("keywords", []) or []:
            if kw.lower() in clue_text:
                score += 2
        for m in info.get("machines", []) or []:
            if m.replace("_", " ").lower() in clue_text:
                score += 1
        for s in info.get("systems", []) or []:
            if s.replace("_", " ").lower() in clue_text:
                score += 1
        return score

    ranked = sorted(
        base_topics,
        key=lambda t: (-topic_match_score(t), base_topics.index(t)),
    )

    # 3. Per topic, pick sources from the catalog. Prefer family + topic
    #    intersection; fall back to topic-only or family-only.
    family_source_ids = {e["source_id"] for e in sources_for_family(asset_family)}
    sources_per_topic: dict[str, list[str]] = {}
    for topic in ranked:
        topic_sources = {e["source_id"] for e in sources_for_tag(topic)}
        overlap = sorted(family_source_ids & topic_sources)
        if overlap:
            sources_per_topic[topic] = overlap
        elif topic_sources:
            sources_per_topic[topic] = sorted(topic_sources)
        else:
            # No catalog source bound to this topic yet — leave empty.
            sources_per_topic[topic] = []

    return {
        "asset_family": asset_family,
        "topics_ordered": ranked,
        "sources_per_topic": sources_per_topic,
        "clue_weights": {
            "process": process_clues,
            "thermal": thermal_clues,
            "emissions": emissions_clues,
            "utility": utility_clues,
            "logistics": logistics_clues,
        },
    }
