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
1. All 9 machinery gaps in `v3-stabilization` branch — G14 moved to V4 because routing-by-topic requires Claude to author topic priorities (content)
2. Regression 7/7 still passes
3. Test suite grows by ~100 tests (machinery tests only, no content tests)
4. `AI_SCAFFOLDING_REGISTRY.md` stays at 9 items (no expansion)
5. One real case rendered for user validation
6. Merged to `main`

## V3 CLOSURE — 2026-05-12

All 9 machinery gaps closed. Branch ready for merge.

| Gap | Type | Commit | Tests added |
|---|---|---|---|
| G1 wire 055-059 → motor_017 | machinery | ebbe825 | 11 |
| G2 motor_059 governance sync (R5/R6/R7 + R2/R3 promoted to error) | machinery | ebbe825 | 12 |
| G3 motor_061 12 families | content | — | DEFERRED to V4 |
| G4 hybrid rationale in motor_061 output | machinery | 1ddebad | 6 |
| G5 7 process patterns | content | — | DEFERRED to V4 |
| G6 report_state_machine + wire to motor_017 | machinery | dfcc359 + 2a08a57 | 28 + 8 |
| G7 combination schema v2 (7 optional fields) | machinery | dfcc359 | 15 |
| G8 motor_054 honors preconditions | machinery | dfcc359 | 8 |
| G9 28 combinations | content | — | DEFERRED to V4 |
| G10 evidence specialization | content | — | DEFERRED to V4 |
| G11 5 TAD actions | content | — | DEFERRED to V4 |
| G12 fair comparison rules | content | — | DEFERRED to V4 |
| G13 6 sources | content | — | DEFERRED to V4 |
| G14 research routing by topic | content-adjacent | — | DEFERRED to V4 |
| G15 motor_058 5 reuse dimensions | machinery | 1ddebad | 12 |
| G16 motor_057 GN4 nugget count | machinery | 1ddebad | 8 |
| G17 claim governor master invariant | machinery | 1ddebad | 7 |

### Final metrics

| Metric | Pre-V3 | Post V3 |
|---|---|---|
| Test suite | 1107 | **1224** (+117) |
| Regression cross-asset | 7/7 | **7/7** |
| Validators wired to motor_017 gate | 5 | **11** (036, 055, 056, 057, 058, 059, 061, 062, 063, scenario_review, report_state_machine) |
| Governance sync rules (motor_059) | 4 | **7** (R5/R6/R7 added) |
| Report states formalized | 0 | **8** + render gate |
| Combination schema fields | 17 required | **17 required + 7 optional V2** |
| Reuse dimensions (motor_058) | 2 | **5** (RU1-RU5) |
| Gold nugget count enforcement | none | **GN4 5-12 configurable** |
| AI scaffolding registry items | 0 | **9 frozen** |

### Definition of "merge ready"

✅ All 9 machinery gaps closed
✅ Suite 1107 → 1224
✅ Regression 7/7
✅ Scaffolding registry at 9 items (no expansion)
✅ One Wilsonart PDF rendered for user validation
⏳ User approves PDF → merge `v3-stabilization` → `main`

### V4 preview (deferred items)

V4 = Industrial Research Engine sprint. Builds the generators that
progressively replace the 9 scaffolding items + emit the 7 content gaps
naturally (G3, G5, G9, G10, G11, G12, G13, G14 above).

Replacement priority per AI_SCAFFOLDING_REGISTRY.md: S6 → S5 → S4 → S8
→ S3 → S1 → S2 → S9 → S7.

## What V3 explicitly does NOT promise

- No new patterns, combinations, hybrids, sources, TAD actions, hypothesis text, scenario fields, knowledge principles, fair comparison rules, or per-family content branches.
- No "improvement" to existing scaffolded content (S1-S9). It stays frozen at current size.
- No PDF beautification.
- No new asset families beyond the 6 already supported by motor_061.

## V4 preview (out of V3 scope, for reference)

V4 = Industrial Research Engine sprint. Builds the generators that progressively replace S1-S9. Replacement order per registry: S6 → S5 → S4 → S8 → S3 → S1 → S2 → S9 → S7.
