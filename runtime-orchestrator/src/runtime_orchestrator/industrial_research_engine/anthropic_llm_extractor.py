"""Anthropic LLM extractor for industrial knowledge (V4 P2).

Implements the V4 P1 LLMExtractor Protocol using Anthropic's Claude API.

Activation requires BOTH:
  - `pip install anthropic` (the SDK is NOT a hard dependency of the
    framework; the import is gated so the framework still loads cleanly
    without it)
  - `ANTHROPIC_API_KEY` environment variable

Without either, the extractor raises a clear error pointing at what's
missing. The framework's default extractor (NotImplementedLLMExtractor)
stays the no-op until the user activates this one explicitly.

Prompt design rules (enforced):
  1. Output MUST be valid JSON parseable as a KnowledgeObject.
  2. `falsification_conditions` non-empty.
  3. `evidence_required` non-empty.
  4. `source_basis` includes the provided source_id.
  5. `allowed_language` MUST NOT contain ROI / savings / guarantee tokens.
  6. `claim_ceiling` ∈ {L0, L1, L2} (never L3 or above).
  7. `asset_families` from the canonical taxonomy only.

The downstream `validate_knowledge` enforces these as the second gate —
if the LLM violates any rule, the validator rejects and the proposal
never reaches `knowledge_pending/`.

V4 P3 will extend with:
  - retry-on-validation-failure (re-prompting the LLM with the error)
  - per-kind specialized prompts (combination vs pattern vs archetype)
  - self-consistency checking via multiple samples
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from .family_scope import ALL_KNOWN_ASSET_FAMILIES
from .llm_extraction_interface import LLMExtractionRequest, LLMExtractionResult
from .source_confidence import source_confidence_for


DEFAULT_MODEL = "claude-sonnet-4-20250514"


_PROMPT_TEMPLATE = """\
You are an Industrial Knowledge Extractor for the ZLab Operational
Truth Framework. Read the SOURCE TEXT below (from an authoritative
industrial document) and propose ONE knowledge_kind={target_kind}
object that follows the schema below. Output ONLY a single JSON
object — no commentary, no markdown fences.

SOURCE
======
source_id: {source_id}
topic: {topic}
target_kind: {target_kind}
asset_families_hint: {asset_families_hint}

SOURCE TEXT
===========
{raw_text}

SCHEMA (mandatory fields shown)
================================
{{
  "id": "snake_case_descriptive_id",
  "version": "1.0.0",
  "knowledge_kind": "{target_kind}",
  "asset_families": ["..."],            // ONE OR MORE from the canonical list
  "anti_families": ["..."],             // families this knowledge does NOT apply to
  "trigger_conditions": ["..."],        // when this knowledge activates (non-empty)
  "anti_triggers": ["..."],
  "falsification_conditions": ["..."],  // MANDATORY — what would prove this wrong
  "evidence_required": ["..."],         // MANDATORY — what evidence would confirm
  "financial_translation": "string",
  "tad_actions": ["VALIDATE_LOSS_PATTERN", "..."],
  "allowed_language": "string",         // MUST NOT contain savings/ROI/guarantee
  "prohibited_language": ["..."],
  "claim_ceiling": "L2",                // L0, L1, or L2 — NEVER higher
  "source_basis": [
    {{"source_id": "{source_id}", "confidence": "high|medium-high|medium"}}
  ]
}}

CANONICAL ASSET FAMILIES (use only these in asset_families and anti_families):
{canonical_families}

HARD RULES (the framework rejects if you violate any):
- falsification_conditions and evidence_required must be non-empty.
- allowed_language must NOT contain "guaranteed savings", "% savings",
  "ROI will be", "guaranteed ROI", "payback within", "this will reduce",
  "this saves", or "definite savings".
- claim_ceiling must be "L0", "L1", or "L2".
- asset_families and anti_families must be disjoint.
- source_basis must include the source_id {source_id}.

Output the JSON object now:
"""


@dataclass
class AnthropicSettings:
    api_key_env: str = "ANTHROPIC_API_KEY"
    model_id: str = DEFAULT_MODEL
    max_output_tokens: int = 4096
    temperature: float = 0.2  # low temp for structured output


class AnthropicLLMExtractor:
    """Real LLM extractor backed by Anthropic Claude."""

    def __init__(self, settings: AnthropicSettings | None = None) -> None:
        self.settings = settings or AnthropicSettings()
        self._client = None  # lazily constructed

    def _client_or_raise(self):
        if self._client is not None:
            return self._client
        api_key = os.environ.get(self.settings.api_key_env, "").strip()
        if not api_key:
            raise RuntimeError(
                f"{self.settings.api_key_env} is not set. AnthropicLLMExtractor "
                "requires the API key. Either export it or pass a different "
                "LLMExtractor to the orchestrator."
            )
        try:
            from anthropic import Anthropic  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "anthropic SDK is not installed. Run: pip install anthropic"
            ) from exc
        self._client = Anthropic(api_key=api_key)
        return self._client

    def _build_prompt(self, request: LLMExtractionRequest) -> str:
        families_hint = request.asset_families_hint or []
        return _PROMPT_TEMPLATE.format(
            source_id=request.source_id,
            topic=request.topic,
            target_kind=request.target_kind,
            asset_families_hint=", ".join(families_hint) or "(none provided)",
            raw_text=request.raw_text[:50_000],  # safety truncation
            canonical_families=", ".join(sorted(ALL_KNOWN_ASSET_FAMILIES)),
        )

    @staticmethod
    def _extract_json_block(text: str) -> dict[str, Any]:
        """Pull the first JSON object out of an LLM response. Tolerates
        accidental markdown fences or trailing prose."""
        # Strip markdown fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```\s*$", "", cleaned, flags=re.MULTILINE)
        # Find the first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError(
                "LLM response did not contain a JSON object. "
                f"First 200 chars: {text[:200]!r}"
            )
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM response JSON parse failed: {exc}. "
                f"First 200 chars: {match.group(0)[:200]!r}"
            ) from exc

    def extract(self, request: LLMExtractionRequest) -> LLMExtractionResult:
        client = self._client_or_raise()

        # Inject source confidence as a hint to the LLM (helps it pick
        # the right claim_ceiling without authoring it for us).
        confidence_hint = source_confidence_for(request.source_id) or {}
        prompt = self._build_prompt(request)
        if confidence_hint:
            prompt += (
                f"\n\nSOURCE CONFIDENCE HINT: tier {confidence_hint.get('authority_tier')}, "
                f"band {confidence_hint.get('confidence_band')}, "
                f"permits_closure={confidence_hint.get('permits_closure')}.\n"
            )

        response = client.messages.create(
            model=self.settings.model_id,
            max_tokens=self.settings.max_output_tokens,
            temperature=self.settings.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Anthropic SDK returns content as list of blocks; we want the text.
        text_blocks = [
            block.text for block in response.content
            if getattr(block, "type", "") == "text"
        ]
        raw_response = "\n".join(text_blocks).strip()

        knowledge_payload = self._extract_json_block(raw_response)

        # Self-assessed confidence (LLM doesn't know; use the source confidence as a proxy)
        self_confidence = 0.0
        band = (confidence_hint.get("confidence_band") if confidence_hint else "") or ""
        if band == "high":
            self_confidence = 0.85
        elif band == "medium-high":
            self_confidence = 0.7
        elif band == "medium":
            self_confidence = 0.55

        warnings: list[str] = []
        # Surface obvious issues without doing full validation (validator
        # does that). These warnings are diagnostic, not blocking.
        if "falsification_conditions" not in knowledge_payload:
            warnings.append("LLM output missing falsification_conditions")
        if "source_basis" not in knowledge_payload:
            warnings.append("LLM output missing source_basis")

        return LLMExtractionResult(
            knowledge_payload=knowledge_payload,
            confidence_self_assessment=self_confidence,
            raw_response=raw_response,
            model_id=self.settings.model_id,
            extraction_warnings=warnings,
        )


def make_anthropic_extractor(**settings: Any) -> AnthropicLLMExtractor:
    return AnthropicLLMExtractor(AnthropicSettings(**settings))
