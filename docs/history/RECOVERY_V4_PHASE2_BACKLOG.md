# V4 Phase 2 — Real PDF + LLM Extraction

**Branch:** `v4-phase2-llm-extractor`
**Started:** 2026-05-12

## What this phase delivers

Replaces V4 P1's stub extractors with real implementations:
- **PDFPlumberExtractor** — uses `pdfplumber` (already installed) to read PDFs into structured text
- **AnthropicLLMExtractor** — wraps `anthropic` SDK to turn text → KnowledgeObject draft via a carefully-crafted prompt template
- **`extract_from_pdf.py` CLI** — chains PDF → LLM → propose_knowledge

## What stays the same

All V4 P0 + P1 contracts. The new extractors implement the same Protocols
(`PDFExtractor`, `LLMExtractor`), so:
- `ExtractionOrchestrator` doesn't change
- `motor_065` doesn't change
- Validation (`validate_knowledge`) still gates everything
- Output still lands in `knowledge_pending/` (NOT direct to approved)
- Dashboard `/knowledge` review is still the only path to approved memory

## Activation gates (graceful degradation)

The new extractors require:
- For PDF: `pdfplumber` package (✅ already installed)
- For LLM: `anthropic` package + `ANTHROPIC_API_KEY` env var

If either is missing:
- The class instantiates fine
- But `.extract()` raises a clear error: "install anthropic / set API key"
- Tests use mocks so they pass without keys/SDK

## Reglas absolutas (still enforced)

1. LLM output must pass `validate_knowledge` / `validate_combination` — no exception.
2. The prompt template explicitly forbids ROI/savings language in `allowed_language`.
3. The prompt requires `falsification_conditions`, `evidence_required`, `source_basis`.
4. The LLM output goes to `knowledge_pending/` always — never directly to approved.
5. The CLI surfaces the proposal URL for human review.
6. AI does NOT auto-promote — only dashboard /api/knowledge/approve does.

## What is NOT in V4 P2

- ❌ Automated motor_028 → motor_065 → extraction cycle (V4 P3)
- ❌ Fine-tuned or specialized prompts per knowledge_kind (V4 P3)
- ❌ Embedding-based source ranking (V4 P3)
- ❌ Multi-shot extraction with self-correction (V4 P3)

## Execution

| Day | Tasks |
|---|---|
| 0 | Branch + this backlog |
| 1 | PDFPlumberExtractor + AnthropicLLMExtractor + tests |
| 2 | `extract_from_pdf.py` CLI + smoke tests + commit + merge |

## Definition of done

V4 P2 closes when:
1. PDFPlumberExtractor implements `PDFExtractor` Protocol and works on a real PDF
2. AnthropicLLMExtractor implements `LLMExtractor` Protocol; raises cleanly without SDK/key; works when both present
3. `extract_from_pdf.py` CLI orchestrates the full path
4. Mocked tests pass (no API calls)
5. Regression 7/7
6. AI_SCAFFOLDING_REGISTRY.md unchanged (still 9 frozen)
7. Merged to main

## How user activates real extraction

```bash
# 1. Install Anthropic SDK
pip install anthropic

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run on a real PDF
python3 scripts/extract_from_pdf.py \
  --pdf-path "/path/to/IIAR-Bulletin-109.pdf" \
  --source-id iiar_bulletin_109 \
  --topic refrigeration \
  --kind pattern \
  --page-range 1-5

# 4. Review in dashboard
open http://localhost:7474/knowledge
```
