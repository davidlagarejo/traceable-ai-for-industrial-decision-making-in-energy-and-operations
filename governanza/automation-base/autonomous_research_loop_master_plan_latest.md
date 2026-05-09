# Autonomous Research Loop Master Plan — Latest

Produced at: 2026-05-06

## Purpose

This plan opens the next deepening phase beyond the current latent-combination lane:
turn the research system into a slower, broader, partially autonomous loop that can:

1. generate provider-specific search plans from active combinations;
2. seed research leads into the existing dashboard lane;
3. resolve those leads into real article references and excerpts;
4. convert those references into knowledge atoms;
5. rerank and expand the latent-combination pool;
6. keep doing that until the case reaches strong coverage or explicit stop conditions.

This is not a rewrite of the Operational Intelligence Skill.
It is the next phase of operationalizing the skill as a real research machine.

## Why this phase exists

The current system is already strong at:

- registry-first patterns and combinations;
- latent combination generation;
- run-scoped adjudication;
- provider-specific query templates;
- discovery candidates, query seeds, article-reference drafts, and promotion review.

But it still stops short of a true autonomous research loop.

The current limitation is not “lack of a brain”.
The current limitation is that the brain still needs too much manual glue between:

- combination hypothesis
- research action
- source hit
- excerpt capture
- knowledge atom refresh
- combination reranking

## Strategic thesis

The unique value of the framework is not only that it can hold patterns.
Its unique value is that it can:

1. investigate slowly enough to avoid shallow conclusions;
2. search across many source families;
3. keep every claim epistemically bounded;
4. produce many latent combinations, not only a few registered ones;
5. adapt that pool to the specific asset context instead of emitting templates.

The autonomous research loop exists to make that repeatable.

## Non-negotiable doctrine

Never weaken:

1. `pattern != diagnosis`
2. `latent combination != case truth`
3. `more research != permission to claim`
4. `source accumulation != L3/L4 promotion`
5. `query seed != article reference`
6. `query_seed_draft != visible_text_enriched`
7. `manual_text_enriched != local asset truth`
8. `research breadth != excuse for template contamination`
9. `combination count target != permission to fabricate combinations`
10. `LLM synthesis != authority over truth`

## Phase objective

Build a governed loop that moves a case through this state machine:

1. `combination_under_review`
2. `follow_on_research_planned`
3. `queryseed_candidates_seeded`
4. `query_seed_drafts_created`
5. `real_reference_excerpt_captured`
6. `knowledge_atoms_refreshed`
7. `latent_pool_reranked`
8. `next_combination_review_presented`

The loop may repeat several times per run.

## Definition of success

The phase is successful when the framework can, for a normal industrial/commercial case:

1. start from one active or deferred combination;
2. produce concrete provider/source search actions;
3. seed the next research candidates automatically;
4. capture draft references without pretending they are real excerpts;
5. resolve at least part of those drafts into real excerpt-backed references;
6. regenerate atoms and latent combinations from the new evidence;
7. rerank and present the next combination one by one;
8. decide whether the pool is still under-investigated;
9. stop only when coverage, gap state, and review queue justify stopping.

## The five real gaps to close

### 1. Autonomous research execution loop

Today:

- combinations create plans;
- plans create queryseed candidates;
- queryseeds create drafts;
- but the system still lacks a governed orchestrator that keeps advancing the loop.

Target:

- a run-scoped research loop controller that can advance, pause, resume, and stop the campaign.

### 2. Combination pool floor enforcement

Today:

- the system can show `combination_search_gap_record`;
- but it does not yet enforce minimum research depth strongly enough.

Target:

- no “research complete” state while the pool is still too thin unless coverage proof is strong.

Recommended targets:

- `< 20 latent combinations` => incomplete unless strong proof of saturation
- `< 50 latent combinations` => normal case still under-developed
- `50+` => acceptable normal target
- `100+` => rich-source / rich-family target

### 3. Deeper multi-source coverage

Today:

- coverage is summarized;
- source families can be queued;
- query templates exist;
- but source breadth is still too dependent on licensed papers and accepted references.

Target source families to govern explicitly:

1. licensed discovery
2. licensed full text
3. public technical guidance
4. specialist web case signal
5. local licensed artifact
6. utility / tariff / billing guidance
7. OEM / handbook / technical manuals
8. regulatory / code / compliance guidance

### 4. Lower friction reference resolution

Today:

- `queryseed-*` can become `query_seed_draft`
- `Resolve draft` can promote to `manual_text_enriched`

But:

- too much excerpt capture is still manual copy/paste.

Target:

- draft resolution should prefill as much context as possible;
- provider-compatible visible text capture should require less operator typing.

### 5. Closed-loop reranking

Today:

- follow-on research can queue the next investigation;
- but the loop does not yet automatically recompute enough of the next review state after each increment.

Target:

- new reference / excerpt / atom should automatically cascade into:
  - source coverage update
  - gap update
  - latent pool refresh
  - cluster refresh
  - admissibility refresh
  - next-combination queue update

## Target architecture

### A. Control layer

Add a new orchestration layer under:

- `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_controller.py`
- `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`
- `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_policies.py`

Responsibilities:

1. evaluate current loop state
2. decide next action
3. decide whether to seed, resolve, rerank, or stop
4. persist run-scoped campaign state

### B. Job/state layer

Add run-scoped state stores:

- `run-registry/research-loop-state/<run_id>.json`
- `run-registry/research-loop-events/<run_id>.json`
- `run-registry/research-loop-jobs/<run_id>.json`
- `run-registry/research-loop-metrics/<run_id>.json`

Each job should have:

- `job_id`
- `job_type`
- `status`
- `source_family`
- `provider_key`
- `combination_id`
- `candidate_id`
- `priority`
- `created_at`
- `updated_at`
- `parent_job_id`
- `reason`

### C. Search-template execution layer

Extend the current query-template lane with:

- `research_query_runner.py`
- `provider_query_seed_materializer.py`
- `reference_resolution_helper.py`

Responsibilities:

1. convert query templates into concrete run jobs;
2. batch-seed discovery candidates;
3. group candidates by provider/source family;
4. prefill article-resolution context.

### D. Evidence-refresh layer

Add:

- `reference_refresh_pipeline.py`
- `knowledge_atom_refresh.py`
- `combination_rerank_pipeline.py`

Responsibilities:

1. detect newly enriched references
2. regenerate extraction records where needed
3. rebuild atoms
4. refresh latent candidates
5. rerank the review queue

### E. Dashboard control-room layer

Add control surfaces to `dashboard.py`:

1. `Research Loop State`
2. `Current Research Job`
3. `Next Recommended Action`
4. `Loop Metrics`
5. `Stop Conditions`
6. `Coverage Saturation Signal`

## Core runtime objects to add

### `research_loop_state`

Required fields:

- `run_id`
- `loop_status`
- `campaign_status`
- `latent_candidate_count`
- `admissible_candidate_count`
- `reference_draft_count`
- `resolved_reference_count`
- `knowledge_atom_count`
- `search_gap_status`
- `coverage_strength`
- `stop_condition_state`
- `next_action`
- `updated_at`

### `research_loop_event`

Required fields:

- `event_id`
- `event_type`
- `entity_type`
- `entity_id`
- `combination_id`
- `summary`
- `created_at`

### `research_loop_metrics`

Required fields:

- `seeded_query_count`
- `query_seed_draft_count`
- `resolved_reference_count`
- `manual_text_enriched_count`
- `visible_text_enriched_count`
- `knowledge_atom_delta`
- `latent_candidate_delta`
- `admissible_candidate_delta`
- `suppressed_generic_cluster_count`
- `deferred_combination_count`

### `research_stop_condition_record`

Required fields:

- `stop_state`
- `reasons`
- `coverage_proof_strength`
- `combination_pool_sufficiency`
- `remaining_open_jobs`
- `remaining_high_priority_source_families`

## Loop states

### Allowed loop states

1. `not_started`
2. `planning`
3. `seeding_queries`
4. `awaiting_reference_resolution`
5. `refreshing_atoms`
6. `reranking_combinations`
7. `review_ready`
8. `paused_by_operator`
9. `stopped_by_saturation`
10. `stopped_by_operator`

## Next-action grammar

The controller should only emit actions from this list:

1. `SEED_QUERY_CANDIDATES`
2. `READ_OR_DRAFT_REFERENCE`
3. `RESOLVE_REFERENCE_DRAFT`
4. `REFRESH_REFERENCE_BACKED_PROMOTIONS`
5. `REBUILD_KNOWLEDGE_ATOMS`
6. `RERANK_LATENT_POOL`
7. `PRESENT_NEXT_COMBINATION`
8. `TRIGGER_DEEPER_SOURCE_FAMILY_SEARCH`
9. `PAUSE_FOR_OPERATOR`
10. `STOP_CAMPAIGN`

## Search-depth policy

The controller should refuse to declare completion when all these are true:

1. `latent_candidate_count < target_floor`
2. `coverage_strength != strong`
3. `remaining_high_priority_source_families > 0`
4. `unresolved_query_seed_drafts > 0`
5. `combination_search_gap_record.search_status == incomplete_under_investigated`

## Target-floor policy

Default floor by case richness:

1. `simple_low-source case`
   floor = 20

2. `normal industrial/commercial case`
   floor = 50

3. `high-complexity / high-source case`
   floor = 100

Inputs for this policy:

- asset family
- source family availability
- provider availability
- active pattern count
- atom count
- context complexity

## Provider/source expansion policy

The loop should diversify providers before concluding saturation.

Minimum attempts per relevant family:

1. `licensed_research_discovery`
   - `scopus`

2. `licensed_research_fulltext`
   - `ieee`
   - `springer`
   - `elsevier` when feasible

3. `public_technical_guidance`
   - `ashrae`
   - `doe`
   - `epa`

4. `specialist_web_case_signal`
   - specialist practitioner / case pages

5. `local licensed artifact`
   - operator-provided or manually saved PDFs/excerpts

## Draft-to-reference policy

### Query seeds

`queryseed-*` must:

- stay `candidate` in discovery
- create `query_seed_draft` references
- never count as real excerpt evidence

### Draft resolution

`query_seed_draft` may become `manual_text_enriched` only if:

1. a real article URL is supplied
2. a real visible excerpt is supplied
3. operator notes are preserved

It may become `visible_text_enriched` only through real provider-visible capture.

## Rerank policy

Reranking should happen after:

1. new accepted discovery candidate
2. new article reference read
3. draft resolved to real excerpt
4. new reference-backed promotion manifest
5. new atom count increase
6. source-family trigger completion

Reranking should refresh:

1. `knowledge_atom_register`
2. `source_coverage_summary`
3. `combination_search_gap_record`
4. `research_campaign_record`
5. `latent_combination_candidate_register`
6. `latent_combination_cluster_register`
7. `admissible_combination_review_register`
8. `combination_review_sequence_register`

## Required dashboard outcomes

The dashboard should eventually support a true one-by-one research loop:

1. review current combination
2. seed leads
3. draft references
4. resolve real reference
5. auto-refresh atoms
6. auto-rerank combinations
7. show next combination

The operator should not need to manually remember what to do next.

## Required tests

Add or extend tests for:

1. loop state transitions
2. target-floor enforcement
3. stop-condition behavior
4. queryseed seeding determinism
5. query_seed_draft resolution
6. rerank on new atom evidence
7. campaign saturation gating
8. no false promotion of drafts to truth
9. no report generation from invalid states

## Risks

1. accidental template inflation
2. accidental “50 combinations at any cost” behavior
3. false saturation
4. over-promotion of weak reference text
5. source contamination from specialist web
6. operator overload from too many low-value leads
7. runtime bloat if every refresh recomputes too much synchronously

## Rules that must never weaken

1. no pattern as diagnosis
2. no combination as diagnosis
3. no draft as evidence
4. no excerpt as local asset truth
5. no completion while under-investigated
6. no combination-count vanity metric
7. no weakening of source traceability
8. no weakening of validator authority
9. no generic-template collapse across assets
10. no LLM authority over truth
