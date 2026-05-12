# V4 Phase 1 — Extraction Infrastructure

**Branch:** `v4-phase1-extraction-infrastructure`
**Started:** 2026-05-12
**Scope:** EXTRACTION INFRASTRUCTURE. Contracts and orchestration for when real PDFs / sources arrive. Real implementations stay stub until user supplies sources + chooses LLM provider.

## Mantra

> V4 P0 built the rails for knowledge to FLOW through approval into memory.
> V4 P1 builds the rails for knowledge to BE PRODUCED from real sources.
> The actual production (PDF parsing, LLM structuring) waits for real
> inputs — Claude does NOT author the content the framework should derive.

## What lands in V4 P1

| # | Item | File | Why |
|---|---|---|---|
| 1 | `motor_065 — Industrial Knowledge Extractor` adapter | `adapters/motor_065.py` | Wires extraction into the pipeline as Layer A motor |
| 2 | `extraction_orchestrator.py` | `industrial_research_engine/extraction_orchestrator.py` | Glues discovery → routing → extract → propose |
| 3 | `pdf_extraction_interface.py` | `industrial_research_engine/pdf_extraction_interface.py` | Protocol for PDF parsers; stub raises until pdfminer/poppler wiring |
| 4 | `llm_extraction_interface.py` | `industrial_research_engine/llm_extraction_interface.py` | Protocol for LLM-driven structuring; stub raises until provider chosen |
| 5 | `scripts/extract_knowledge.py` CLI | `scripts/extract_knowledge.py` | Manual text-paste extraction path (user supplies text + metadata) |
| 6 | Tests | `tests/test_v4_phase1_extraction_infrastructure.py` | Locks contracts |

## What does NOT land in V4 P1

- ❌ Actual PDF parsing (pdfminer / pdfplumber integration) — waits for first real PDF
- ❌ Actual LLM calls — waits for user choice of provider (OpenAI / Anthropic / local)
- ❌ Autonomous discovery + extraction cycle — that's V4 P2
- ❌ Content (no patterns/combinations/sources authored by Claude)

## Reglas absolutas (still enforced)

1. Extraction OUTPUT must pass `validate_knowledge` / `validate_combination` from V4 P0.
2. Everything lands in `knowledge_pending/<kind>/` — never directly in approved memory.
3. NotImplementedError stays the default for the real extractors; tests verify this.
4. The CLI / manual path is the ONLY way to land content from sources in V4 P1; LLM extraction can be enabled later by replacing the stub.

## Execution

| Day | Tasks |
|---|---|
| 0 | Branch + backlog (this doc) |
| 1 | motor_065 + extraction_orchestrator + interfaces (items 1-4) |
| 2 | CLI + tests + commit + merge (items 5-6) |

## Definition of done

V4 P1 closes when:
1. motor_065 in layer_registry + pipeline (Layer A)
2. extraction_orchestrator orchestrates 4 stages: source identification → routing → extraction → proposal
3. Both extraction interfaces raise NotImplementedError (testable contract)
4. CLI accepts text input + metadata, validates, lands proposal in knowledge_pending/
5. Regression 7/7
6. AI_SCAFFOLDING_REGISTRY.md unchanged (9 frozen — no content added)
7. Merged to main
