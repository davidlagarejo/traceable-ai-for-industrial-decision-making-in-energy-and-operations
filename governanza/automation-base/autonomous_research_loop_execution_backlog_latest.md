# Autonomous Research Loop Execution Backlog — Latest

Produced at: 2026-05-06

## Scope

This backlog translates:

- `autonomous_research_loop_master_plan_latest.md`

into an executable implementation sequence.

It does not reopen the already completed OISK phase.
It opens a new deepening lane focused on:

1. autonomous research control
2. research-depth enforcement
3. lower-friction reference capture
4. closed-loop reranking

## Current executable truth

- suite: `runtime-orchestrator`
- command: `pytest -q`
- result: `678 passed, 15 warnings`
- date: `2026-05-06`

## Working rule

This lane is not allowed to regress:

1. epistemic guards
2. report diversity guards
3. pattern/combination validators
4. existing dashboard review paths
5. licensed-lane provenance

## Phase map

1. `ARL-00` baseline and contracts
2. `ARL-01` research loop state model
3. `ARL-02` queryseed job orchestration
4. `ARL-03` draft-resolution acceleration
5. `ARL-04` atom refresh + rerank loop
6. `ARL-05` source-depth enforcement
7. `ARL-06` stop conditions and saturation gates
8. `ARL-07` dashboard control room
9. `ARL-08` acceptance bundles and certification

## ARL-00 — Baseline and contracts

Status: `started`

Purpose:

- freeze the current latent-research loop behavior before deeper automation.

Deliverables:

1. capture payload snapshots for:
   - `combination_follow_on_execution_manifest_register`
   - `discovery_candidate_review_register`
   - `article_reference_register`
   - `combination_review_sequence_register`
2. capture a real `queryseed-* -> query_seed_draft -> manual_text_enriched` sample artifact chain
3. write a baseline note for current manual steps

Files:

- `runtime-orchestrator/tests/fixtures/`
- `governanza/automation-base/autonomous_research_loop_execution_backlog_latest.md`

Acceptance:

1. one fixture bundle for warehouse-like case
2. one fixture bundle for manufacturing-like case
3. one fixture bundle for building-like case

## ARL-01 — Research loop state model

Status: `started`

Purpose:

- give the loop a sovereign run-scoped controller state instead of implicit UI behavior.

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_controller.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_policies.py`

Stores:

1. `run-registry/research-loop-state/<run_id>.json`
2. `run-registry/research-loop-events/<run_id>.json`
3. `run-registry/research-loop-jobs/<run_id>.json`
4. `run-registry/research-loop-metrics/<run_id>.json`

Core objects:

1. `research_loop_state`
2. `research_loop_event`
3. `research_loop_metrics`
4. `research_stop_condition_record`

Acceptance:

1. every run gets a stable `loop_status`
2. every loop action creates an event
3. state survives refresh/reload

Current implementation truth:

1. sovereign modules now exist:
   - `research_loop_policies.py`
   - `research_job_queue.py`
   - `research_loop_state.py`
   - `research_loop_controller.py`
2. dashboard now persists:
   - `research-loop-state/<run_id>.json`
   - `research-loop-events/<run_id>.json`
   - `research-loop-jobs/<run_id>.json`
   - `research-loop-metrics/<run_id>.json`
3. `congruence_brain` now exposes:
   - `research_loop_state`
   - `research_loop_job_register`
   - `current_research_job`
   - `research_loop_metrics`
   - `research_stop_condition_record`
4. dashboard now renders `Research Loop State`

## ARL-02 — Queryseed job orchestration

Status: `started`

Purpose:

- turn seeded research leads into explicit jobs instead of isolated candidate rows.

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_job_queue.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/provider_query_seed_materializer.py`
3. `runtime-orchestrator/dashboard.py`

Work:

1. materialize jobs from `provider_query_templates`
2. attach each `queryseed-*` to:
   - `combination_id`
   - `query_family`
   - `provider_key`
   - `source_family`
   - `job_id`
3. expose those jobs in dashboard

Acceptance:

1. every `queryseed-*` maps back to exactly one job
2. repeated seeding does not duplicate equivalent jobs
3. job status transitions are visible

Current implementation truth:

1. the sovereign loop now emits explicit jobs:
   - `seed_query_candidates`
   - `draft_reference`
   - `resolve_reference_draft`
   - `refresh_reference_backed_promotions`
   - `trigger_deeper_source_family_search`
2. those jobs are now visible in dashboard payload and persisted stores
3. `Current Combination Review` can now coexist with a run-scoped `Current Research Job`
4. `provider_query_seed_materializer.py` now owns deterministic `queryseed-*` construction from
   follow-on provider query templates, instead of leaving that assembly inline in `dashboard.py`
5. `research_query_runner.py` now owns the sovereign `search_result_capture_register` /
   `search_result_capture_sequence`, so `needs_draft -> capture_search_result -> resolve_reference_excerpt`
   is explicit runtime state instead of only a UI convention

## ARL-03 — Draft-resolution acceleration

Status: `started`

Purpose:

- reduce operator friction between `query_seed_draft` and `manual_text_enriched`.

Code targets:

1. `runtime-orchestrator/dashboard.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/reference_resolution_helper.py`

Work:

1. prefill `Resolve draft` with:
   - provider
   - original query
   - search brief
   - expected evidence targets
2. support optional resolved title / DOI / URL update
3. support one-shot “resolve and accept for reference use” behavior where valid
4. preserve epistemic state:
   - `query_seed_draft` remains not-enriched
   - resolved excerpt becomes `manual_text_enriched`

Acceptance:

1. resolving a draft requires fewer prompts than current generic edit flow
2. no resolved draft can skip `manual_text_enriched`
3. no resolved draft can silently become `visible_text_enriched`

Current implementation truth:

1. sovereign helper now exists:
   - `reference_resolution_helper.py`
2. article-reference rows now expose `draft_resolution_prefill`
3. `Resolve draft` now preloads:
   - provider
   - query family
   - primary query
   - evidence targets
4. resolving a draft can now also:
   - update `source_url`
   - optionally update `title`
   - optionally update `doi`
   - auto-accept the discovery candidate for reference use
5. the dashboard now also exposes:
   - `reference_resolution_sequence_register`
   - `current_reference_resolution_row`
   - `next_reference_resolution_rows`
   - `reference_resolution_queue_summary`
6. `Current Reference Draft Review` now presents `query_seed_draft` rows one at a time and advances
   implicitly to the next pending draft after each refresh
7. resolving a draft no longer requires a chain of prompts:
   the dashboard now supports a packet-based one-step resolution path through
   `POST /api/article-reference-resolve-packet`
8. the packet parser now accepts:
   - `URL`
   - `Title`
   - `DOI`
   - `Journal`
   - `Year`
   - `Notes`
   - `Excerpt`
   and resolves the draft into `manual_text_enriched` plus auto-accept when excerpt is present
9. the dashboard now also supports `Resolve visible batch` through
   `POST /api/article-reference-resolve-batch`, using multiple packet blocks separated by `---`
10. the batch resolver validates every block up front and then advances the draft-resolution queue by
    multiple items in one operator step when the packets are valid
11. batch resolution is no longer a blind “current + next rows” shortcut:
    the framework now builds a sovereign `reference_resolution_batch_plan`
12. that plan prefers:
    - same provider first
    - then same `source_family`
    before falling back to a mixed pending slice
13. the dashboard now also renders a distinct `Current Search Result Capture` lane, driven by the
    sovereign register above, so query-seed search work is visible before the excerpt-resolution queue
14. the lane now also exposes a sovereign `search_query_execution_register` /
    `search_query_execution_sequence`, carrying provider-specific search packets, query variants,
    capture packet templates, and explicit execution states before result capture
15. that execution lane can now be materialized per run and captured in batch:
    the dashboard persists `search-query-execution-manifests/<run_id>.json` and supports
    batch search-result capture packets before excerpt resolution
16. excerpt resolution no longer has to restate a URL when the source hit was already captured:
    the same resolve paths now hydrate missing `source_url` / title / notes defaults from the
    stored capture context before promoting to `manual_text_enriched`
17. the reference-resolution batch planner now exposes a `captured_quick_packet_template` and
    `captured_ready` flag, so compatible drafts can be resolved in groups with `Candidate ID +
    Excerpt` while reusing the captured article URLs
18. the search-execution lane now also supports imported source-hit options:
    `search-query-result-imports/<run_id>.json` stores visible provider results per candidate,
    the execution register surfaces imported option counts, and the dashboard can promote a selected
    imported result directly into `query_seed_result_captured` without retyping URL/title/snippet
19. imported result promotion is now its own sovereign review lane:
    the framework exposes `current_search_query_result_option_row` /
    `search_query_result_option_summary`, and the research loop can move into
    `PROMOTE_IMPORTED_RESULT` / `awaiting_imported_result_promotion` before falling back to manual
    search-result capture

## ARL-04 — Atom refresh and rerank loop

Status: `started`

Purpose:

- close the core loop:
  reference improvement -> atom refresh -> latent pool rerank.

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/knowledge_atom_refresh.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_rerank_pipeline.py`
3. `runtime-orchestrator/dashboard.py`

Work:

1. detect when a reference moved from:
   - `metadata_only`
   - `query_seed_draft`
   to:
   - `manual_text_enriched`
   - `visible_text_enriched`
2. refresh:
   - `reference_backed_promotion_manifest`
   - `knowledge_atom_register`
   - `source_coverage_summary`
   - `combination_search_gap_record`
   - `latent_combination_candidate_register`
   - `latent_combination_cluster_register`
   - `admissible_combination_review_register`
   - `combination_review_sequence_register`

Acceptance:

1. one resolved draft changes atom counts when excerpt is meaningful
2. rerank happens automatically after reference enrichment
3. next combination can change after new evidence

Current implementation truth:

1. sovereign modules now exist:
   - `knowledge_atom_refresh.py`
   - `combination_rerank_pipeline.py`
2. the refresh helper now persists:
   - `knowledge-atom-refresh/<run_id>.json`
   - `combination-rerank/<run_id>.json`
3. `licensed_research` now exposes:
   - `knowledge_atom_refresh_summary`
   - `combination_rerank_summary`
4. `Congruence Brain` now renders `Atom Refresh And Rerank`

## ARL-05 — Source-depth enforcement

Status: `started`

Purpose:

- prevent the loop from stopping just because a few combinations already exist.

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_policies.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_campaign.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_gap_analyzer.py`

Work:

1. implement target floors:
   - `20`
   - `50`
   - `100`
2. bind those floors to case richness
3. require more source-family depth if the pool is still thin
4. emit explicit policy reasons when the loop cannot stop

Acceptance:

1. `search complete` is blocked when pool floor is not met and coverage is weak
2. `search complete` is allowed when pool is thin only if saturation proof is strong
3. policy outputs are visible in dashboard

Current implementation truth:

1. `combination_gap_analyzer.py` now binds latent-pool expectations to the real target floor instead of a fixed `50`,
   and now also inspects source-family depth and high-priority-family coverage before declaring coverage strong.
2. `research_loop_policies.py` now exposes a sovereign `build_research_depth_enforcement_record(...)` with:
   - `depth_state`
   - `must_continue_research`
   - `saturation_proof_strong`
   - `required_next_source_families`
   - explicit policy reasons
3. `research_loop_controller.py` now persists that depth gate inside the sovereign loop snapshot and feeds it into
   the stop-condition logic.
4. `research_loop_state.py` now blocks premature stop unless either:
   - the normal sufficiency gate passes, or
   - saturation proof is explicitly strong,
   and in both cases only if the depth-enforcement gate is no longer asking to continue research.
5. `dashboard.py` now exposes and renders `research_depth_enforcement_record` plus stored `depth_state`,
   so operators can see why the loop must continue even when some combinations already exist.

## ARL-06 — Stop conditions and saturation gates

Status: `started`

Purpose:

- make the controller know when to continue and when to stop.

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_controller.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_policies.py`

Work:

1. implement:
   - `paused_by_operator`
   - `stopped_by_saturation`
   - `stopped_by_operator`
2. create explicit stop reasons:
   - enough combinations
   - enough coverage
   - unresolved jobs too low
   - remaining high-value source families exhausted
3. keep the stop decision auditable

Acceptance:

1. every stop state carries reasons
2. every stop state can be explained from payload only
3. no run silently “just ends”

Current implementation truth:

1. the loop now has a sovereign `research_loop_control_record` persisted under:
   - `run-registry/research-loop-controls/<run_id>.json`
2. `dashboard.py` now exposes `POST /api/research-loop-control` with:
   - `resume`
   - `pause`
   - `stop`
3. `research_loop_state.py` now supports:
   - `paused_by_operator`
   - `stopped_by_operator`
   - `stopped_by_saturation`
   and keeps explicit reasons in `research_stop_condition_record`.
4. `research_loop_controller.py` now persists operator control and stop-state transitions as auditable event changes
   instead of leaving them implicit in UI refresh order.
5. `Congruence Brain` now surfaces:
   - `research_loop_control_record`
   - operator control reason
   - explicit stop state
   - explicit stop reasons


## ARL-07 — Dashboard control room

Status: `ready`

Purpose:

- turn `Congruence Brain` into a true research campaign control room.

Code targets:

1. `runtime-orchestrator/dashboard.py`
2. `runtime-orchestrator/tests/test_operational_intelligence_dashboard_congruence_brain.py`

UI surfaces to add:

1. `Research Loop State`
2. `Current Research Job`
3. `Next Recommended Action`
4. `Loop Metrics`
5. `Stop Conditions`
6. `Campaign Saturation`

Interactions to add:

1. `Advance loop`
2. `Pause loop`
3. `Resume loop`
4. `Force rerank`
5. `Mark source family exhausted`

Acceptance:

1. operator always sees next recommended action
2. operator sees why loop is paused or blocked
3. queue and campaign metrics are visible in one place

Current implementation truth:

1. `dashboard.py` now exposes control-room endpoints:
   - `POST /api/research-loop-advance`
   - `POST /api/research-loop-control`
   - `POST /api/research-loop-force-rerank`
   - `POST /api/source-family-exhausted`
2. `Advance loop` only executes epistemically safe jobs automatically:
   - `seed_query_candidates`
   - `draft_reference`
   - `refresh_reference_backed_promotions`
   and explicitly reports when the next step still requires human resolution or external research.
3. `Congruence Brain` now renders real control-room actions:
   - `Advance loop`
   - `Pause loop`
   - `Resume loop`
   - `Stop loop`
   - `Force rerank`
   - `Mark exhausted`
4. source-family cards can now persist `exhausted` as a sovereign trigger status instead of leaving that judgment implicit.
5. the loop-control payload now travels with:
   - current operator control state
   - operator reason
   - explicit stop state
   - explicit stop reasons

## ARL-08 — Acceptance bundles and certification

Status: `completed`

Purpose:

- certify the loop across real case families and protect epistemology.

Tests to add:

1. `warehouse`:
   - seed from tariff/boundary combination
   - draft
   - resolve
   - rerank
2. `manufacturing`:
   - maintenance/reactive/process combination
   - multi-source atom refresh
3. `building`:
   - schedule/boundary/solar-sensitive divergence
4. negative:
   - query seed never treated as evidence
   - draft never treated as visible text
   - no stop while under-investigated
   - no false `50+` inflation through duplicates

Acceptance:

1. all bundles green
2. no epistemic regression
3. no template collapse across assets

Current implementation truth:

1. a dedicated acceptance bundle now exists in:
   - `runtime-orchestrator/tests/test_autonomous_research_loop_acceptance.py`
2. `warehouse` certification now proves:
   - `query_seed_draft` does not count as visible text
   - unresolved query seeds keep the loop open
   - the loop moves into `awaiting_reference_resolution`, not false evidence closure
3. `manufacturing` certification now proves:
   - a controlled stop only happens when the latent floor is satisfied by unique combinations
   - strong source-family depth and strong high-priority coverage are both present
4. `building` certification now proves:
   - duplicate rows cannot fake a `50+` latent pool
   - under-investigated runs stay open even when raw row count is inflated
   - the next action remains `SEED_QUERY_CANDIDATES` when the campaign is still shallow
5. both the loop metrics and the combination-gap analyzer now deduplicate by `combination_id` before
   evaluating latent/admissible pool sufficiency, while still exposing raw row counts for audit

## Suggested implementation order

1. `ARL-01`
2. `ARL-02`
3. `ARL-04`
4. `ARL-05`
5. `ARL-06`
6. `ARL-07`
7. `ARL-03`
8. `ARL-08`

Reason:

- state and jobs first
- rerank loop second
- policy and stop control third
- UX acceleration after the loop is governed

## What not to do

Do not:

1. rewrite the current discovery/reference/promotions lane
2. create a parallel research lane outside dashboard stores
3. let loop automation bypass operator sovereignty
4. promote combination count targets into vanity metrics
5. confuse query planning with evidence capture

## Exit criteria

This phase is done when:

1. the loop has sovereign state
2. query seeds become jobs
3. resolved references refresh atoms automatically
4. latent combinations rerank automatically
5. stop conditions are explicit
6. dashboard shows next action clearly
7. the system can sustain a longer research campaign without devolving into manual glue

## Latest incremental progress

- `Current Reference Draft Review` now uses a guided batch plan that prioritizes:
  - same provider + same `query_family` + same evidence intent
  - then same `source_family` + same `query_family` + same evidence intent
  - only then broader provider/family fallback
- `reference_resolution_batch_plan` now exposes:
  - `query_families`
  - `evidence_targets`
  - `batch_reason`
- this keeps reference-resolution batches aligned to research intent instead of mixing drafts that belong to
  different evidence hunts under the same provider.
- `query_seed_draft` resolution packets are now preseeded with provider-aware hints:
  - `launch_url`
  - `search_surface`
  - `execution_hint`
  - `primary_query` / `pivot_query`
- both single-draft and batch resolution now surface those hints before `URL:` in the packet template, so the operator
  can resolve a real article with less reconstruction from memory.
- there is now also a `quick resolve` path for `query_seed_draft` that only requires:
  - real article URL
  - visible excerpt
  - optional notes
- `Resolve full packet` remains available for richer metadata correction, but the default UI path is now the shorter
  excerpt-first flow.
- the same split now exists for batches:
  - `Resolve source batch` uses the short template
  - `Resolve full source batch` keeps the richer packet with title/DOI/journal/year
- both still reuse the same sovereign batch endpoint and reference-edit/rerank path underneath.
- a new governed intermediate step now exists before excerpt resolution:
  `Capture result`
- it stores:
  - real article URL
  - result title
  - result snippet
  while keeping the reference in `query_seed_draft`
- this reduces later excerpt-resolution friction without promoting search-result text into evidence.
- the research loop now also recognizes that intermediate step explicitly:
  - `capture_search_result`
  - then `resolve_reference_excerpt`
- so search-result capture and real excerpt resolution are no longer collapsed into one generic draft-resolution job.
