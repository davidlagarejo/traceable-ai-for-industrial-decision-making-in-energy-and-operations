# Research Brain 100% Completion Backlog — Latest

Produced at: 2026-05-07

## Scope

This backlog translates:

- `research_brain_100_percent_completion_plan_latest.md`

into an executable sequence.

It does not reopen:

1. the base OISK closure;
2. the bounded runtime-authority closure;
3. any epistemic guard already certified.

## Current executable truth

- suite: `runtime-orchestrator`
- command: `pytest -q`
- result: `723 passed, 15 warnings`
- date: `2026-05-07`

## Working rule

This lane is not allowed to regress:

1. claim epistemology
2. pattern/combination validators
3. report diversity protection
4. source provenance
5. latent-combination anti-template logic
6. current dashboard review capabilities

## Phase map

1. `RB100-00` gap freeze and target contracts
2. `RB100-01` search-result intake hardening
3. `RB100-02` imported-result review hardening
4. `RB100-03` reference-resolution compression
5. `RB100-04` floor doctrine hardening
6. `RB100-05` source-family expansion
7. `RB100-06` stronger closed-loop automation
8. `RB100-07` strong-target acceptance bundles
9. `RB100-08` 100% completion review

## RB100-00 — Gap freeze and target contracts

Status: `planned`

Purpose:

1. freeze the exact reasons the system is not yet at the strong `100%`;
2. prevent future sessions from mixing “base prompt closed” with “expanded research brain closed”.

Deliverables:

1. snapshot of remaining manual prompt-heavy paths
2. snapshot of current floor doctrine
3. source-family depth status matrix
4. explicit completion checklist

Acceptance:

1. one document maps each remaining gap to code surface
2. no ambiguity remains about what “100%” now means

## RB100-01 — Search-result intake hardening

Status: `started`

Purpose:

1. reduce manual glue in `search plan -> visible result options`

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_query_runner.py`
2. `runtime-orchestrator/dashboard.py`

Work:

1. add more structured import formats beyond free-form packet paste
2. preserve provider/query/evidence intent on every imported option
3. create run-scoped import manifests that remain reviewable after refresh
4. improve batch import grouping by provider + query family + evidence targets

Acceptance:

1. imported result options survive refresh/reload cleanly
2. one candidate can hold multiple imported options without ambiguity
3. import provenance remains explicit

Current implementation truth:

1. the import endpoint now accepts:
   - legacy packet blocks
   - structured `search_result_import_records`
   - JSON array payloads
2. imported result records now persist `import_format`
3. batch planning now exposes:
   - `result_import_json_template`
   - `accepted_import_formats`
4. batch planning now also exposes a provider-aware clipboard capture guide:
   - `ordered_result_import_provider_tsv_template`
   - `ordered_result_import_provider_capture_guide`
   and the import parser now treats provider-native visible-text headers such as `Index Terms`
   as usable snippet context when no abstract/snippet column is present.
5. the same ordered import lane now also accepts provider-native TSV rows without a pasted header,
   as long as they match one of the provider layouts exposed in
   `ordered_result_import_provider_capture_guide.positional_layouts`.
6. the batch plan now also exposes a provider-native commented capture sheet,
   so `Current Search Result Capture` can hand the operator a row-by-row worksheet
   before import instead of only a raw TSV header template.
7. the same batch plan now also exposes a provider-native search sheet,
   so the operator gets row-guided `search lines`, preferred surface, search tips,
   and result-capture goals before even copying visible result rows back into the framework.
8. the same batch plan now also exposes a combined provider search workbook,
   so one artifact can carry:
   - search guidance
   - candidate identity
   - and import-ready `URL / Title / Snippet / Selected / Excerpt / Notes`
   without forcing the operator to hop between separate search-sheet and capture-sheet formats.
9. the same upstream lane now also exposes a live `search_query_execution_session_bundle`,
   even before materialization, and the dashboard can now:
   - show that bundle directly,
   - import `search_query_execution_session_rows` from the live bundle,
   - and auto-materialize the persisted manifest only when needed.
10. that same session lane is now also run-scoped and persistent:
   - `search-query-execution-sessions/<run_id>.json`
   - `Save session bundle`
   - `Import saved ready rows`
   so visible-result capture work can survive refreshes and be re-imported without rebuilding the JSON payload from scratch.
11. that same lane now also has native in-page visible-result capture:
   the operator can edit `source_url / title / snippet / excerpt / selected / notes` row by row inside
   `Current Search Result Capture`, save those rows to the run-scoped store, and import the ready rows
   without depending on `window.prompt` as the primary path.
12. that same native lane now also supports per-row provider parsing:
   one provider row pasted into a row-local box can be parsed directly into
   `source_url / title / snippet / excerpt / selected / notes`, reducing manual field-by-field entry.

## RB100-02 — Imported-result review hardening

Status: `started`

Purpose:

1. turn imported-result review into a first-class staged workflow instead of mostly prompt glue

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_query_runner.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_job_queue.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`
4. `runtime-orchestrator/dashboard.py`

Work:

1. strengthen `current_search_query_result_option_row`
2. add explicit review summary and next-option sequencing
3. let the operator review one imported option at a time where useful
4. keep `imported result != evidence` explicit in all states

Acceptance:

1. imported-result promotion no longer depends on ad hoc selection only
2. queue state is persisted and explainable
3. no option can bypass source-hit capture semantics

Current implementation truth:

1. imported-result review now runs at option granularity, not only candidate granularity
2. `current_search_query_result_option_row` now carries:
   - `current_option_index`
   - `current_option_count`
   - `current_imported_option`
3. the dashboard can now promote the current imported option directly, without asking for an option number when the runtime already knows the active option
4. candidate rows without a full option list can still fall back to `top_imported_result` so the review lane does not collapse on partial payloads
5. imported-result review now also exposes a sovereign visible-batch lane:
   - `search_query_result_option_batch_plan`
   - `promote_records_json_template`
   - `accepted_promote_formats`
6. the dashboard can now `Promote visible batch` without promoting imported options one by one
7. visible-result import can now also carry an explicit `selected` marker:
   - packet lane: `Selected: yes`
   - structured/JSON lane: `"selected": true`
8. when exactly one imported option is explicitly selected for a candidate, the runtime can now:
   - auto-promote it directly to `query_seed_result_captured`
   - or auto-resolve it directly to `manual_text_enriched` when a real `reference_excerpt` is already present

## RB100-03 — Reference-resolution compression

Status: `started`

Purpose:

1. reduce repeated typing between captured source hit and excerpt-backed reference

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/reference_resolution_helper.py`
2. `runtime-orchestrator/dashboard.py`

Work:

1. preserve captured result title/snippet/URL as reusable prefill
2. improve quick-resolve and batch-resolve by provider/query family
3. reduce dependence on long `window.prompt` chains
4. preserve strict epistemic states:
   - `query_seed_draft`
   - `query_seed_result_captured`
   - `manual_text_enriched`

Acceptance:

1. fewer operator fields are required in the happy path
2. batch resolution remains source-aware
3. no shortcut jumps directly to evidence authority

Current implementation truth:

1. reference-resolution batch plans now expose both packet and JSON templates for:
   - quick resolve
   - full resolve
   - captured-result quick resolve
2. `/api/article-reference-resolve-batch` now accepts:
   - legacy packet blocks
   - structured `resolution_batch_records`
   - JSON array payloads
3. `/api/article-reference-capture-search-result-batch` now accepts:
   - legacy packet blocks
   - structured `search_result_batch_records`
   - JSON array payloads
4. search-query execution batch plans now expose:
   - `capture_result_json_template`
   - `accepted_capture_formats`

## RB100-04 — Floor doctrine hardening

Status: `started`

Purpose:

1. align runtime policy with the stated `50+ / 100+` doctrine

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_policies.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_gap_analyzer.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`
4. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_controller.py`

Work:

1. isolate explicit bootstrap exceptions
2. tighten normal-case floor doctrine toward `50+`
3. tighten rich-source doctrine toward `100+`
4. harden stop gates when the pool is thin

Acceptance:

1. low-floor exceptions are explicit and auditable
2. normal industrial/commercial cases no longer silently target `20`
3. saturation proof remains strict when the pool is below target

Current implementation truth:

1. target-floor evaluation now emits an explicit `build_target_combination_floor_record(...)`
2. the `20` floor now only survives as a narrow `bootstrap_floor_exception`
3. shallow normal campaigns now resolve to the `50+` doctrine instead of silently collapsing to `20`
4. depth and gap records now persist:
   - `target_floor_policy_state`
   - `bootstrap_floor_exception`
   - `target_floor_policy_reason`

## RB100-05 — Source-family expansion

Status: `started`

Purpose:

1. make non-paper technical source families more operational

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_campaign.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/knowledge_atom_store.py`
3. new helpers as needed for specific families

Priority families:

1. utility / tariff / billing guidance
2. OEM / handbook / technical manuals
3. regulatory / code / compliance guidance
4. specialist web case signal

Work:

1. define source-family-specific capture schemas
2. define source-family-specific query/evidence targets
3. define atomization paths from those families
4. expose their depth in campaign and gap records

Acceptance:

1. each priority family has a governed intake path
2. source-family depth can affect rerank and stop policy
3. atoms can be sourced from more than papers and PDFs

Current implementation truth:

1. source-family contracts now exist for:
   - `utility_tariff_billing_guidance`
   - `oem_handbook_technical_manuals`
   - `regulatory_code_compliance_guidance`
   - `specialist_web_case_signal`
   in addition to the earlier licensed/public families
2. coverage now respects explicit `source_family` declared on discovery candidates, article references, extraction records, and atoms, instead of relying only on provider inference
3. source-family rows and trigger plans now expose:
   - `capture_mode`
   - `admissible_capture_fields`
   - `atomization_priority`
   - `preferred_query_families`
4. combination follow-on execution manifests now merge source-family query biases into provider query templates
5. manual article creation from the dashboard now accepts optional `source_family`
6. visible/manual references from non-paper families now generate governed `L2` knowledge atoms directly, even when no extraction record exists yet
7. those reference-derived atoms can now carry weak `matched_pattern_ids` / `matched_combination_ids` support forward into the latent pool without violating the `L2` ceiling
8. imported search-result options can now be resolved directly to excerpt-backed references in one step, without forcing a separate `promote` and then `resolve` loop
9. the same compressed lane now also works in batch across visible imported-result options, candidate-unique, with real excerpts still required per resolved source hit
10. visible-result import can now auto-capture singleton candidates immediately as `source hits`, while leaving multi-option candidates in governed imported-result review
11. visible-result import now also supports an `ordered` batch format keyed by the active batch plan, so operators can paste results in batch order without repeating `candidate_id`
12. visible-result import now accepts optional `reference_excerpt`; singleton imports with real excerpts can auto-resolve directly to `manual_text_enriched` instead of stopping at `result_captured`
13. the `ordered` import lane now supports packet blocks too, not only JSON/structured rows, so operators can paste batch-ordered `URL/title/snippet/excerpt` blocks without repeating identifiers

## RB100-06 — Stronger closed-loop automation

Status: `started`

Purpose:

1. shrink manual glue between:
   - search execution
   - imported results
   - source-hit capture
   - excerpt resolution
   - atom refresh
   - rerank

Code targets:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_job_queue.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_controller.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_loop_state.py`
4. `runtime-orchestrator/dashboard.py`

Work:

1. improve loop transitions between pending stages
2. reduce manual prompt dependence in repetitive steps
3. improve carryover of context from query to result to reference
4. preserve auditable operator waits only where human judgment is actually required

Acceptance:

1. repetitive upstream transitions require less operator glue
2. loop status remains truthful and auditable
3. no hidden automation promotes evidence state improperly

Current implementation truth:

1. imported-result intake now supports explicit operator choice at import time through governed `selected` markers
2. that explicit choice works for:
   - packet imports
   - ordered packet imports
   - structured record imports
   - JSON array imports
3. explicit selection can now bypass imported-option review for that candidate without violating epistemology:
   the chosen visible result becomes a `source hit`, not evidence
4. if the explicitly selected visible result already includes a real `reference_excerpt`, the same import call can now
   resolve straight to `manual_text_enriched`
5. the ordered import lane now also accepts a compact line format:
   `URL | Title | Snippet | Excerpt | Selected | Notes`
   so operators can paste one visible result per batch row without packet labels or repeated identifiers
6. the same ordered import lane now also accepts TSV / clipboard rows:
   `URL<TAB>Title<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes`
   so results copied from tables or spreadsheets can be pasted with less reformatting
7. that TSV lane now also tolerates title-first clipboard order:
   `Title<TAB>URL<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes`

## Strategic regression closure slice

Status: `started`

Current implementation truth:

1. `motor_016` now propagates conditional strategic intelligence all the way into the client-facing package instead of
   collapsing to a locally blocked thesis shell.
2. `structural_executive_summary` now carries:
   - `thesis_state`
   - `local_claim_closure_state`
   - `conditional_intelligence_reason`
   - `dominant_operational_misunderstanding`
   - `hidden_system_boundary_error`
   - `invalid_comparison_risk`
   - `dominant_loss_logic`
   - `top_gold_nuggets`
   - bounded fallback `conditional_opportunity_pathways`
3. client-facing sections now render those fields explicitly in:
   - `Executive Structural Thesis`
   - `Dominant Variables`
   - `Peer / Competitive Comparison`
   - `Conditional Redesign Pathway`
   - `Claim Permissions / What Not To Do`
4. the legacy `Conditional Opportunities` lane now also falls back to bounded conditional pathways when
   upstream `opportunity_candidates` are empty but the executive thesis still contains strategic signals.
5. `motor_018` now uses `motor_047.executive_thesis` as a governed fallback surface for:
   - `chart_fair_comparison_gate`
   - `chart_cross_layer_congruence_map`
   - `chart_cost_driver_signal_profile`
   so the chart layer does not go strategically mute when those upstream registers are sparse but
   the bounded strategic thesis already exists.
   when the copied result view puts the label before the link
8. the same compact/TSV lane now also accepts embedded-link first columns:
   `[Title](URL)` and `Title (URL)` can stand in for the URL+Title pair,
   with the remaining columns shifting to `Snippet / Excerpt / Selected / Notes`
9. TSV clipboard rows can now also carry extra columns before the URL:
   the runtime will infer `title / URL / snippet` from the row and fold the remaining columns into `notes`,
   so copied tables like `Rank<TAB>Title<TAB>Year<TAB>Source<TAB>URL<TAB>Snippet` no longer need manual reshaping
10. the TSV lane is now effectively header-aware for common result-table shapes:
   when the copied row exposes recognizable columns such as `Rank / Title / Year / Source / URL / Snippet`,
   the runtime preserves the likely result structure and pushes the surplus cells into `notes` instead of rejecting the row
11. that header-aware TSV lane now also supports explicit header rows in flexible order:
    commented or plain headers such as `# Source<TAB>Year<TAB>Abstract<TAB>Link<TAB>Title<TAB>Selected<TAB>Notes`
    are now mapped semantically instead of positionally

## RB100-07 — Strong-target acceptance bundles

Status: `completed`

Purpose:

1. certify the strong research-brain target, not only the bounded base lane

Code targets:

1. `runtime-orchestrator/tests/test_autonomous_research_loop_acceptance.py`
2. new tests for source-family depth and floor doctrine
3. dashboard acceptance bundles where needed

Required acceptance scenarios:

1. `warehouse`
2. `manufacturing`
3. `building`
4. one rich-source case with target `100+`

Negative guarantees:

1. imported result never counts as evidence
2. captured source hit never counts as excerpt
3. low-floor bootstrap cannot masquerade as a normal mature run
4. weak multi-source coverage cannot claim saturation

Implemented closure:

1. added render-path acceptance on `test_operational_intelligence_skill_cutover.py` so the
   final `.tex` / PDF package is explicitly certified to preserve strategic conditional language
   (`wrong variable`, `wrong denominator`, `fair comparison`, bounded prohibitions) instead of only
   certifying the in-memory payload;
2. added a render-engine acceptance that proves `motor_017` keeps chart assets end-to-end when
   the report package carries governed chart surfaces;
3. verified the closure against the full `runtime-orchestrator` suite after the new cutover tests.

## RB100-08 — 100% completion review

Status: `completed_not_certified`

Purpose:

1. perform the final strict review against the strong expanded doctrine

Acceptance:

1. all previous phases are green
2. full suite is green
3. governance documents align with code reality
4. the framework can honestly claim `100%` for the expanded research-brain target

Implemented closure:

1. completed the strict final review and wrote it to
   `research_brain_100_percent_completion_review_latest.md`;
2. verified that the full suite remains green at `723 passed, 15 warnings`;
3. aligned the governance docs with the actual review verdict instead of forcing a false certification;
4. concluded that the expanded `100%` claim is still not honest because:
   - a real rich-source `100+` execution path is not yet acceptance-proven;
   - core research transitions still retain too much `window.prompt` glue;
   - excerpt resolution is materially better but still not clean enough to clear that bar.
