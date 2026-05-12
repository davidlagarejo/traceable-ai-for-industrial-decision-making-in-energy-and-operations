# V4 Phase 0 — Industrial Research Engine Infrastructure

**Branch:** `v4-phase0-infrastructure`
**Started:** 2026-05-12
**Scope:** INFRASTRUCTURE ONLY — no real scraping, no LLM extraction, no content authorship.

## Mantra

> Build the rails. Stop the AI from authoring intelligence. Make every
> piece of knowledge enter the framework through an auditable approval
> pipeline whose contracts are stable BEFORE we plug in real extraction.

## Reglas absolutas (enforced by code, not by docs)

1. **No patterns/combinations without `falsification_conditions`** → schema validator rejects
2. **No combinations without `evidence_pack`** → schema validator rejects
3. **No claim_ceiling above L2** → schema validator caps at L2
4. **No cross-family contamination** → `asset_families` + `anti_families` enforced
5. **No ROI / savings closure language** → `prohibited_language` defaults include savings/ROI tokens; schema rejects if `allowed_language` contains them
6. **No direct ingestion into production memory** → all entries go through `knowledge_pending/` → dashboard approval → `knowledge_memory/approved/`
7. **No AI auto-promotion** → CLI rejects writes to `approved/` directly; only dashboard `/api/knowledge/approve` moves items

## Items (matches user spec)

| # | Item | File(s) | Day |
|---|---|---|---|
| 1 | `industrial_research_engine` module skeleton | `src/runtime_orchestrator/industrial_research_engine/` | 1 |
| 2 | `propose_knowledge.py` CLI | `scripts/propose_knowledge.py` | 3 |
| 3 | `knowledge_pending/` directory tree | `zlab_skill/registry/knowledge_pending/<12 subdirs>/` | 2 |
| 4 | `knowledge_schema_validator` | `industrial_research_engine/validators.py` | 1 |
| 5 | `asset_family_scope` enforcement | `industrial_research_engine/family_scope.py` | 1 |
| 6 | `combination_registry` structure | `zlab_skill/registry/combination_registry/<7 subdirs>/` | 2 |
| 7 | `source_confidence_registry` | `industrial_research_engine/source_confidence.py` | 2 |
| 8 | `industrial_research_registry` (taxonomy) | `industrial_research_engine/taxonomy.py` | 2 |
| 9 | `research_routing_engine` skeleton | `industrial_research_engine/routing.py` | 3 |
| 10 | Dashboard hooks for approve/reject/promote/deprecate | `dashboard.py` + new `/knowledge` page | 3 |
| 11 | `knowledge_memory/` (approved/deprecated/superseded/rejected) | `zlab_skill/registry/knowledge_memory/<4 subdirs>/` | 2 |
| 12 | NOT IMPLEMENTED YET | n/a — explicit non-goals | — |

## Non-goals (explicit, NOT in scope)

- ❌ Real scraping (no HTTP, no PDF parsing, no LLM calls)
- ❌ Embeddings / vector DB
- ❌ Autonomous AI promotion
- ❌ PDF optimization
- ❌ Refactoring V3 patterns / combinations

## Execution order

| Day | Tasks |
|---|---|
| 0 | Branch + backlog + directory trees (item 3, 6, 11) |
| 1 | Module skeleton + schemas + validators + family_scope (items 1, 4, 5) |
| 2 | source_confidence + taxonomy (items 7, 8) |
| 3 | propose_knowledge.py CLI + research_routing skeleton + dashboard hooks (items 2, 9, 10) |
| 4 | Tests + final commit + merge back to main |

## Validation gates

After each day:
- `python3 -m pytest tests/ -q` must pass (target: 1224 → ~1300)
- `bash scripts/regression_cross_asset_recovery.sh` must show 7/7
- `AI_SCAFFOLDING_REGISTRY.md` stays at 9 frozen items (NO new content from Claude)

## Definition of done

V4 Phase 0 closes when:
1. All 11 items in branch
2. Regression 7/7
3. AI_SCAFFOLDING_REGISTRY.md not expanded
4. Real extraction = `NotImplementedError` (proves the rails are in place but engine is dormant)
5. User can:
   - Drop a JSON into `knowledge_pending/<type>/`
   - See it in dashboard `/knowledge`
   - Click approve → moves to `knowledge_memory/approved/`
   - Click reject → moves to `knowledge_memory/rejected/`
6. Merged to `main`

## Architecture preview

```
External source (PDF / paper / handbook)
        │
        ▼
[motor_028 discovery] ──► source_confidence_registry
        │
        ▼
[research_routing_engine] decides what to investigate
        │
        ▼
[industrial_research_engine.extract()] ◄── STUB in V4 P0; real impl later
        │
        ▼
extracted_knowledge_object (passes knowledge_schema_validator)
        │
        ▼
knowledge_pending/<type>/<id>.v1.json
        │
        ▼
Dashboard /knowledge → human approve/reject
        │           │
        │           ▼
        │       knowledge_memory/rejected/  (audit only)
        ▼
knowledge_memory/approved/<id>.v1.json
        │
        ▼
Available for combination_engine + motor_054 to activate
```

The engine is dormant in V4 Phase 0 — but the rails are stable. When V4 Phase 1 plugs in real extraction (PDFs, LLMs, embeddings), nothing downstream needs to change.
