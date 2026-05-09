# Research Brain 100% Completion Plan — Latest

Produced at: 2026-05-07

## Purpose

This document defines the exact work required to move the framework from:

- `strong bounded OISK + governed autonomous research loop`

to:

- `the fully expanded research brain vision`

The target here is not the already-closed base Operational Intelligence Skill prompt.
The target is the stronger version later defined in execution:

1. broad multi-source investigation;
2. large latent-combination pools;
3. lower operator friction between search and excerpt;
4. stronger provider-assisted result capture;
5. a loop that keeps investigating until the case is genuinely deep enough.

## Current truth

Current executable truth remains:

- suite: `runtime-orchestrator`
- command: `pytest -q`
- result: `723 passed, 15 warnings`
- date: `2026-05-07`

What is already true:

1. the base OISK / Congruence Brain architecture is implemented;
2. the bounded runtime-authority phase is closed;
3. the autonomous research loop exists and is governed;
4. latent combinations, clustering, campaign state, rerank, and queue review all exist;
5. the remaining gap is not “brain missing”;
6. the remaining gap is `research execution depth + operator-friction reduction + stronger upstream automation`;
7. the upstream search lane now also has a live `search_query_execution_session_bundle`,
   so search-session rows can be reviewed and re-imported structurally without requiring
   a persisted manifest first;
8. that lane is now also run-scoped and persistent through a saved search-session store,
   so ready visible-result rows can survive refresh and be imported again without recreating the JSON body.
9. the dashboard now also exposes native in-page capture for those search-session rows,
   so the main save/import path of that lane can be operated row by row without falling back to
   `window.prompt` or raw JSON as the primary interface;
10. that same lane now also supports row-local provider parsing, so one provider row can prefill
    the visible-result fields directly instead of forcing manual field-by-field typing.
11. the client-facing report package no longer collapses to local silence when bounded structural
    intelligence exists: `motor_016` now preserves and renders conditional strategic fields such as
    wrong-variable risk, hidden boundary error, invalid comparison risk, dominant loss logic,
    strategic nuggets, and bounded conditional pathways even when local claim closure remains blocked.
12. the chart lane now also reads `executive_thesis` as a governed fallback surface, so the main
    congruence charts keep showing wrong-variable risk, boundary error, invalid comparison risk, and
    cost-driver reframe even when some upstream comparison or finance registers remain sparse.
13. the final render/delivery path is now acceptance-certified as well:
    `motor_016 -> motor_017 -> motor_027` preserves strategic conditional language such as wrong-variable /
    wrong-denominator / fair-comparison / bounded-prohibition logic in the rendered `.tex` / PDF package,
    and `motor_017` also preserves chart assets end-to-end when the report package carries them.
14. the final strict `RB100-08` review is now written down in
    `research_brain_100_percent_completion_review_latest.md`, and its verdict is explicit:
    the expanded research-brain target is not yet honestly certifiable as `100%`.

## Exact definition of 100%

The research brain is only considered `100% complete` when all of the following are true:

1. `search plan -> visible source-hit options` is materially assisted by runtime, not left as mostly manual paste work.
2. `visible source-hit -> excerpt-backed reference` can be completed with sharply reduced operator typing.
3. the runtime target for normal cases is no longer allowed to collapse to a floor below `50` latent combinations except under explicitly audited bootstrap rules.
4. rich-source cases can be driven toward `100+` latent combinations through real source expansion, not only policy text.
5. the campaign actively governs at least these source families:
   - licensed discovery
   - licensed full text
   - public technical guidance
   - specialist web case signal
   - local licensed artifact
   - utility / tariff / billing guidance
   - OEM / handbook / technical manuals
   - regulatory / code / compliance guidance
6. the framework can explain, for each run, whether it stopped because:
   - operator stopped it;
   - source families were exhausted;
   - saturation proof is genuinely strong;
   - or the campaign is still under-developed.
7. no run can be called “deep enough” while the system still depends too heavily on free-form `window.prompt` glue for core research transitions.

## What still blocks 100%

### 1. Upstream search execution is still too manual

Today:

1. the framework builds provider-aware search packets;
2. it can seed query candidates;
3. it can import visible results;
4. it can promote imported results;
5. but it still depends heavily on manual prompt-driven capture for:
   - result import
   - result promotion
   - source-hit capture

Target:

1. results should be importable in more structured ways;
2. imported result review should feel like a real staged workflow, not only prompt chains;
3. provider-compatible search context should carry forward automatically into the next step.

### 2. Excerpt resolution still needs too much operator typing

Today:

1. quick resolve exists;
2. full packet resolve exists;
3. batch resolve exists;
4. captured-result-assisted resolve exists;
5. but the last mile still depends too much on manual paste and prompt dialogs.

Target:

1. the operator should only add the minimal human judgment that runtime cannot infer;
2. provider/query context should prefill the rest;
3. compatible batch lanes should minimize repeated field entry.

### 3. Combination-floor enforcement is still weaker than the stated doctrine

Today:

1. the runtime can still set a floor of `20` for sparse coverage situations;
2. that is useful as a bootstrap heuristic;
3. but it is weaker than the expanded doctrine of:
   - `< 50` under-developed normal case
   - `50+` acceptable normal target
   - `100+` rich-source target

Target:

1. bootstrap exceptions must be explicit, auditable, and narrow;
2. the normal research doctrine must point the loop toward `50+`;
3. rich-source doctrine must point it toward `100+`.

### 4. Multi-source breadth is governed but not fully populated

Today:

1. source-family coverage exists;
2. source-family triggers exist;
3. campaign state exists;
4. but several families still lack strong materialized acquisition/ingestion lanes.

Target:

1. the campaign must be able to deepen beyond licensed discovery;
2. non-paper technical sources must become first-class citizens in the runtime lane.

### 5. The loop is governed, but not fully closed in execution depth

Today:

1. state, jobs, rerank, stop conditions, and queues exist;
2. but not enough of the upstream acquisition chain self-materializes.

Target:

1. new search actions should more naturally produce:
   - imported result options
   - promoted source-hit rows
   - excerpt-ready references
   - atom refresh
   - rerank
   - next combination

## Non-negotiable doctrine

Never weaken:

1. `pattern != diagnosis`
2. `latent combination != local truth`
3. `query seed != article reference`
4. `imported search result != evidence`
5. `captured source hit != excerpt-backed reference`
6. `manual_text_enriched != local asset proof`
7. `more source count != permission to claim`
8. `higher combination count != permission to fabricate combinations`
9. `UI convenience != epistemic shortcut`
10. `autonomy != hidden synthesis authority`

## Completion architecture

### Layer A — Search Execution Materialization

Goal:

1. make provider search execution more structured and less prompt-heavy;
2. preserve search intent, evidence targets, and provenance all the way through source-hit review.

Target code areas:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_query_runner.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/provider_query_seed_materializer.py`
3. `runtime-orchestrator/dashboard.py`

Required outputs:

1. `search_query_execution_register`
2. `search_query_result_option_register`
3. `search_query_result_option_review_sequence`
4. run-scoped result-import manifests
5. clearer source-hit promotion surfaces

### Layer B — Reference Resolution Compression

Goal:

1. reduce repeated operator typing;
2. preserve and reuse provider/query/result context across the whole draft-resolution lane.

Target code areas:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/reference_resolution_helper.py`
2. `runtime-orchestrator/dashboard.py`

Required outputs:

1. structured quick-resolve paths
2. structured full-resolve paths
3. source-aware batch plans
4. captured-result-aware batch promotion
5. lower-friction resolve lanes by provider/query family

### Layer C — Floor Doctrine Hardening

Goal:

1. align runtime policy with the stated `50+ / 100+` doctrine;
2. restrict low-floor exceptions to explicit bootstrap cases.

Target code areas:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_policies.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_gap_analyzer.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`

Required outputs:

1. explicit `bootstrap_floor_exception`
2. normal-case minimum doctrine tied to asset/source richness
3. stronger saturation proof requirements when the pool is thin

### Layer D — Multi-Source Family Expansion

Goal:

1. widen the live campaign beyond papers and references;
2. make source-family breadth operational rather than only declarative.

Target code areas:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_campaign.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/knowledge_atom_store.py`
3. new source-family-specific helpers where needed

Priority family lanes:

1. utility / tariff / billing guidance
2. OEM / handbook / technical manuals
3. regulatory / code / compliance guidance
4. specialist web case signal

### Layer E — True Closed-Loop Completion

Goal:

1. shrink the human glue between:
   - search plan
   - result options
   - source hit
   - excerpt
   - atom refresh
   - rerank
   - next combination

Target code areas:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_job_queue.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_controller.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`
4. `runtime-orchestrator/dashboard.py`

Required outputs:

1. fewer operator waits for structurally repetitive transitions
2. better carryover of context between review stages
3. more explicit research-lane completion logic

## Phase map

1. `RB100-00` exact gap freeze
2. `RB100-01` search-result intake hardening
3. `RB100-02` imported-result review workflow hardening
4. `RB100-03` reference-resolution compression
5. `RB100-04` floor doctrine hardening
6. `RB100-05` source-family expansion
7. `RB100-06` stronger closed-loop automation
8. `RB100-07` acceptance bundles for the strong research-brain target
9. `RB100-08` 100% certification review

## Success metrics

The lane is done only when:

1. a normal run can be driven toward `50+` latent combinations without doctrinal ambiguity;
2. a rich-source run can be driven toward `100+` latent combinations when coverage allows;
3. imported-result handling no longer feels like raw prompt glue for the critical happy path;
4. excerpt resolution uses materially less repeated typing;
5. at least the four priority source-family lanes have executable depth signals;
6. acceptance bundles certify:
   - no fake evidence promotion
   - no fake floor inflation
   - no premature stop
   - no generic-template collapse across distinct assets

## Out of scope

This plan does not require:

1. weakening epistemic gates;
2. allowing the framework to invent excerpts;
3. treating search hits as evidence;
4. claiming local truth without admissible evidence;
5. replacing human judgment in source selection where provider UX still blocks automation.

## Final interpretation

The framework is already beyond “prototype brain”.

What remains for `100%` is not another architectural rewrite.
What remains is a deliberate last-mile deepening of:

1. upstream research execution;
2. source breadth;
3. combination-floor doctrine;
4. friction reduction between source hit and excerpt-backed reference.
