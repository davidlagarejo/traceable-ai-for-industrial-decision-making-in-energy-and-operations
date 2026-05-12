"""LLM extraction interface (V4 P1).

Contract for the LLM-driven step that converts RAW TEXT from an
authoritative industrial source into a candidate KnowledgeObject /
CombinationObject that motor_065 then proposes via propose_knowledge.

The interface is INTENTIONALLY model-agnostic. V4 P2+ can wire
OpenAI / Anthropic / local model behind this Protocol without touching
the rest of the framework.

Inputs:
  raw_text: str               — text chunk from the PDF extractor
  topic: str                  — industrial topic (from taxonomy)
  source_id: str              — catalog source_id (Gap C catalog)
  target_kind: str            — desired knowledge_kind (pattern / etc.)
  prompt_template: str | None — optional custom prompt; otherwise the
                                framework's canonical prompt is used

Output:
  raw dict ready to be fed to validate_knowledge / validate_combination.

NEVER bypass the validator. The LLM step PRODUCES; the validator
APPROVES. AI never writes directly into pending/.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class LLMExtractionRequest:
    raw_text: str
    topic: str
    source_id: str
    target_kind: str = "pattern"
    asset_families_hint: list[str] = field(default_factory=list)
    prompt_template: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMExtractionResult:
    knowledge_payload: dict[str, Any]
    confidence_self_assessment: float = 0.0  # 0..1, LLM's own confidence
    raw_response: str = ""
    model_id: str = ""
    extraction_warnings: list[str] = field(default_factory=list)


class LLMExtractor(Protocol):
    """Any LLM-based extractor that turns raw text into a KnowledgeObject draft."""

    def extract(self, request: LLMExtractionRequest) -> LLMExtractionResult: ...


class NotImplementedLLMExtractor:
    """Default V4 P1 extractor. Raises when called. Replaced with a real
    Anthropic / OpenAI / local implementation in V4 P2."""

    def extract(self, request: LLMExtractionRequest) -> LLMExtractionResult:
        raise NotImplementedError(
            "LLM extraction is not implemented in V4 Phase 1. The contract "
            "is locked; a real extractor lands when the user chooses a "
            "provider (Anthropic / OpenAI / local model). "
            f"Requested topic: {request.topic!r}, target_kind: {request.target_kind!r}."
        )


def default_llm_extractor() -> LLMExtractor:
    """Factory — returns the NotImplemented stub today."""
    return NotImplementedLLMExtractor()
