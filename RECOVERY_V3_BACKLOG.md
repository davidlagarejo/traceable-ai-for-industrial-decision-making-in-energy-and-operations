# Recovery V3 — Stabilization Backlog

**Branch:** `v3-stabilization`
**Started:** 2026-05-11
**Course correction:** AI builds machinery only. Content/intelligence generation deferred to V4 Industrial Research Engine. See `AI_SCAFFOLDING_REGISTRY.md`.

## Mantra

> If a gap requires Claude to write a pattern, combination, hybrid, source, justification, or per-family content — **drop it**. That's V4 work. V3 is **only** machinery (validators, gates, state machines, schemas, interfaces).

## In-scope (machinery only — Claude can do this)

| Gap | Type | File | Effort |
|---|---|---|---|
| **G1** Wire motor_055-059 to motor_017 block_reasons | validator wiring | `adapters/motor_017.py` | 0.3d |
| **G2** Extend motor_059 with R5/R6/R7 governance sync rules | validator code | `adapters/motor_059.py` | 0.5d |
| **G4** Surface hybrid `rationale` in composer when admissible | display logic | `adapters/motor_016.py` (composer) | 0.3d |
| **G6** Report State Machine — 8 formal states, `client_safe` blocks strictly | new module | `src/runtime_orchestrator/report_state_machine.py` | 0.5d |
| **G7** Combination schema v2 (optional fields: evidence_pack, falsification, gold_nugget, comparison_impact, preconditions, conditional_clause, layers_combined) | schema code | `zlab_skill/schema.py` | 0.25d |
| **G8** motor_054 honors `preconditions` before activating a combination | activation code | `adapters/motor_054.py` / `zlab_skill/combination_engine.py` | 0.3d |
| **G14** motor_035 emits `research_priority_by_topic` (routing order, not curation) | routing code | `adapters/motor_035.py` | 0.4d |
| **G15** motor_058 measures 5 reuse dimensions (RU3 TAD, RU4 chart, RU5 evidence_pack) | validator code | `adapters/motor_058.py` | 0.4d |
| **G16** motor_057 enforces nugget count 5-12 (GN4 rule) | validator rule | `adapters/motor_057.py` | 0.1d |
| **G17** Claim Governor master invariant test ("lack of certainty blocks closure, not reasoning") | test | `tests/test_claim_governor_master_invariant.py` | 0.25d |

**Total: ~3.3 days of machinery.**

## Out of V3 (would require Claude to author content — deferred to V4)

- ~~G3~~ Expand motor_061 to 12 families with contamination sets → V4 derives from asset_archetypes + observed contamination
- ~~G5~~ 7 new process family patterns → V4 extracts from sources
- ~~G9~~ 28 multi-layer combinations → V4 `combination_engine` proposes from co-occurrence + dashboard approval
- ~~G10~~ Evidence specialization (hypothesis → evidence_pack) → V4 derives per-hypothesis pack from active patterns
- ~~G11~~ 5 new TAD actions hardcoded in patterns → V4 TAD engine derives from claim governor + dominant variables
- ~~G12~~ Fair comparison rules enriched → V4 derives from NAICS + process taxonomy
- ~~G13~~ 6 sources added to catalog → V4 motor_028 discovers, framework assigns tier/family

## Execution order

| Day | Tasks |
|---|---|
| **0** | ✓ Branch + `AI_SCAFFOLDING_REGISTRY.md` (9 items frozen) + scaffolding headers in S1-S9 + this backlog |
| **1** | G1 + G2 (validator gate + governance sync) |
| **2** | G6 (state machine) + G7 (combination schema v2) + G8 (preconditions) |
| **3** | G15 + G16 + G17 + G4 + G14 |
| **4** | Regression 7/7 validation + generate client-safe PDF + merge to main |

## Validation gates

After each gap:
- `python3 -m pytest tests/ -q` must pass (expected: grows from 1107 to ~1140)
- `bash scripts/regression_cross_asset_recovery.sh` must show 7/7 (with `ZLAB_AUTO_APPROVE_SCENARIOS=1`)
- `AI_SCAFFOLDING_REGISTRY.md` must not gain new entries

## Definition of done

V3 closes when:
1. All 10 gaps (G1, G2, G4, G6, G7, G8, G14, G15, G16, G17) are in `v3-stabilization` branch
2. Regression 7/7 still passes
3. Test suite grows by ~30-40 tests (machinery tests only, no content tests)
4. `AI_SCAFFOLDING_REGISTRY.md` stays at 9 items (no expansion)
5. One real case rendered as `client_safe` PDF, approved by user
6. Merged to `main`

## What V3 explicitly does NOT promise

- No new patterns, combinations, hybrids, sources, TAD actions, hypothesis text, scenario fields, knowledge principles, fair comparison rules, or per-family content branches.
- No "improvement" to existing scaffolded content (S1-S9). It stays frozen at current size.
- No PDF beautification.
- No new asset families beyond the 6 already supported by motor_061.

## V4 preview (out of V3 scope, for reference)

V4 = Industrial Research Engine sprint. Builds the generators that progressively replace S1-S9. Replacement order per registry: S6 → S5 → S4 → S8 → S3 → S1 → S2 → S9 → S7.
