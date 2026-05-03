# Dynamic Congruence Prompt Completion Backlog — Latest

Produced at: 2026-05-03

## Current backlog state

Behavioral closure already achieved:

- dynamic congruence runtime behavior is functionally closed;
- full runtime suite last known truth: `502 passed, 15 warnings`;
- prompt-compliance audit exists;
- execution plan exists.
- baseline fixtures and contract tests for dynamic registers exist;
- `DiscoveryCaseState` now exists and is emitted additively by `motor_028`.
- `discovery_need_register` now consumes `DiscoveryCaseState` and emits activation reasons, state signals, jurisdiction fit, and source-family preference hints.
- `next_best_search_register` now reranks source families explicitly and emits `family_rank_register`, `selected_search_family_reason`, `selected_search_family_score`, and `family_score_components`.
- controlled browser acquisition now exists as an optional public-page backend for `official_portal_context` sources, with policy gating, render classification, and provenance manifests.
- browser/static yield memory now exists, feeds back into state and reranking, and exposes browser-justified vs browser-waste families.
- `motor_049` now emits `congruence_case_state`, rescored intake questions, and explicit `truncated_question_register` surfaces.
- hypothesis and claim-governance registers now read structured question metadata instead of substring heuristics by default.
- peer boundedness now requires affirmative evidence surfaces and no longer auto-upgrades merely because a discriminator question did not appear.

Residual architectural nuance, now non-blocking:

- discovery is not yet fully state-driven;
- dynamic intake is still library-first;
- prompt-completion acceptance is now green end-to-end for the warehouse/logistics path.

Optional future evolution only:

- deeper open-ended planner generalization beyond the current governed family libraries.

Queue state:

- `DCP-01`: `completed`
- `DCP-02`: `completed`
- `DCP-03`: `completed`
- `DCP-04`: `completed`
- `DCP-05`: `completed`
- `DCP-06`: `completed`
- `DCP-07`: `completed`
- `DCP-08`: `completed`
- `DCP-09`: `completed`
- `DCP-10`: `completed`

Parent references:

- [dynamic_congruence_prompt_compliance_audit_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_compliance_audit_latest.md>)
- [dynamic_congruence_prompt_execution_plan_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_execution_plan_latest.md>)
- [runtime_may_2_closure_boundary_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_may_2_closure_boundary_latest.md>)
- [runtime_reentry_status_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_reentry_status_latest.md>)

## Purpose

This backlog closes the remaining architectural gap against the `Dynamic Congruence Intelligence System` prompt.

It is not:

- a growth backlog;
- a report-improvement backlog;
- a May 2 runtime-closure backlog reopen;
- a documentation-only queue.

It is a post-closure hardening backlog whose job is to make the runtime satisfy the strictest reading of the prompt without weakening current governance.

## Non-negotiables

Do not weaken:

- `motor_035` routing authority
- `motor_036` hard validation authority
- `motor_047` thesis sovereignty
- `motor_048` compression sovereignty
- `motor_052` / `motor_053` / `motor_054` bounded strategic logic
- claim governance
- case isolation
- declared-input downgrading
- empty-section fallback policy

Do not reintroduce:

- static query-list behavior as final discovery logic
- benchmark-as-local-truth
- stale chart reuse
- sensor-first recommendation behavior
- report sections rendered empty
- uncontrolled scraping
- generic Playwright crawling

## Execution rule

Do not start with Playwright.

The planner must be fixed before browser acquisition exists.
Otherwise browser automation will compensate for weak discovery logic instead of solving it.

## Ticket format

Each ticket specifies:

- purpose
- priority
- status
- owner
- main files
- outputs to add
- changes required
- dependencies
- acceptance
- tests
- do-not-break

---

## Wave 0 — Baseline Freeze

### `DCP-01` Dynamic Planner Baseline Freeze

Purpose:

- freeze a no-regression baseline before changing discovery or intake logic

Priority:

- `P0`

Status:

- `completed`

Owner:

- `runtime-orchestrator/tests`
- `governanza/automation-base`

Main files:

- `runtime-orchestrator/tests/test_dynamic_source_discovery_engine.py`
- `runtime-orchestrator/tests/test_next_best_search_engine.py`
- `runtime-orchestrator/tests/test_dynamic_intake_generator.py`
- `runtime-orchestrator/tests/test_hypothesis_driven_ingestion.py`
- `runtime-orchestrator/tests/test_fair_peer_set_builder.py`

Outputs to add:

- warehouse baseline fixture
- manufacturing baseline fixture
- contract snapshot for key dynamic registers

Changes required:

- freeze current register shapes and current green suite truth
- capture canonical positive-case fixtures for warehouse and manufacturing
- add anti-regression assertions around register shape, not just content

Dependencies:

- none

Acceptance:

- current full suite remains green
- fixtures exist for later refactor work
- current dynamic register contracts are explicit and test-backed

Tests:

- existing dynamic bundle plus new fixture/contract tests

Do-not-break:

- no runtime behavior change in this ticket

---

## Wave 1 — Discovery Backbone

### `DCP-02` Discovery Case State Backbone

Purpose:

- move discovery from loosely inferred context to explicit evolving case state

Priority:

- `P0`

Status:

- `completed`

Owner:

- `motor_028`
- `congruence_intelligence/dynamic_case_state.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py`
- `runtime-orchestrator/src/runtime_orchestrator/ingestion_learning.py`

Outputs to add:

- `discovery_case_state`
- `regulatory_trigger_register`
- `source_family_failure_summary`
- `source_family_success_summary`

Changes required:

- derive an explicit state object from target definition, routing readiness, coverage gaps, requestable evidence, attempts, budget state, and prior-run yield memory
- persist the state additively in `motor_028`
- normalize discovery-relevant history without changing existing registers yet

Dependencies:

- `DCP-01`

Acceptance:

- `motor_028` emits `discovery_case_state`
- TX and NYC warehouse states differ materially where jurisdiction differs
- routing-disabled cases cannot look technically discoverable

Tests:

- `test_dynamic_case_state_builder.py`
- extend discovery tests for jurisdiction-specific state

Do-not-break:

- do not remove current `motor_028` outputs

---

### `DCP-03` Discovery Need Activation Enrichment

Purpose:

- make discovery need activation consume real case state instead of family-template overlap alone

Priority:

- `P0`

Status:

- `completed`

Owner:

- `congruence_intelligence/discovery_planner.py`
- `motor_028`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`

Outputs to add:

- `activation_reasons`
- `state_signals_used`
- `jurisdiction_fit`
- `source_family_preference_hints`

Changes required:

- preserve `_GENERIC_DISCOVERY_NEEDS` and `_FAMILY_DISCOVERY_NEEDS` as governed priors
- extend scoring with jurisdiction, gap severity, source-yield memory, operator-escalation risk, comparison relevance, and regulatory triggers
- keep current output schema stable while enriching rows

Dependencies:

- `DCP-02`

Acceptance:

- discovery needs remain backward-compatible
- rows explain why they were activated
- warehouse discovery ordering is not jurisdiction-agnostic anymore

Tests:

- extend `test_dynamic_source_discovery_engine.py`

Do-not-break:

- do not let discovery emit technically inadmissible routes

---

### `DCP-04` Next-Best Search Family Reranking

Purpose:

- make next-best-search choose the best family within a discovery need, not just the first template family

Priority:

- `P0`

Status:

- `completed`

Owner:

- `congruence_intelligence/next_best_search.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py`

Outputs to add:

- `family_rank_register`
- `selected_search_family_reason`
- `selected_search_family_score`
- `family_score_components`

Changes required:

- rank families by jurisdiction fit, discriminative value, prior success/failure, public-vs-operator likelihood, regulatory relevance, comparison unlock value, and budget fit
- preserve existing surface fields such as `if_found`, `if_not_found`, and `stop_condition`
- remove the implicit `search_families[0]` assumption

Dependencies:

- `DCP-03`

Acceptance:

- repeated failure of one family can elevate alternatives
- tariff-sensitive cases elevate tariff-relevant families
- expensive families can be demoted when budget is tight

Tests:

- extend `test_next_best_search_engine.py`

Do-not-break:

- do not destabilize current ranking of needs unless the new evidence basis justifies it

---

## Wave 2 — Controlled Browser Acquisition

### `DCP-05` Playwright Public-Page Acquisition Layer

Purpose:

- add a bounded browser acquisition backend for public JS-rendered pages without weakening routing or evidence provenance

Priority:

- `P1`

Status:

- `completed`

Owner:

- new `source_acquisition/*`
- `motor_028`
- `crawler_store`

Main files:

- `runtime-orchestrator/pyproject.toml`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/crawler_store.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/policy.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/strategy_selector.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/render_classifier.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/playwright_fetch.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/provenance.py`

Outputs to add:

- acquisition mode selector
- browser provenance manifest
- Playwright policy gate
- render-mode classification

Changes required:

- add Playwright as optional dependency only
- support `playwright_public_page` as one allowed acquisition mode
- allow browser mode only when `technical_scraping_allowed=true`, source family is whitelisted, page is public, and static mode is insufficient
- capture final URL, DOM/text hashes, selector lineage, and attempt outcome

Dependencies:

- `DCP-06`

Acceptance:

- browser mode is disabled by default
- browser mode never bypasses routing policy
- timeout or render failure degrades to coverage gap instead of fabricated evidence

Tests:

- `test_source_acquisition_strategy.py`
- `test_playwright_policy.py`
- `test_playwright_provenance.py`

Do-not-break:

- no login walls
- no CAPTCHA bypass
- no arbitrary crawl loops

---

### `DCP-06` Browser And Static Yield Memory

Purpose:

- teach discovery which families justify static fetch, browser fallback, or operator escalation

Priority:

- `P1`

Status:

- `completed`

Owner:

- `crawler_store`
- `ingestion_learning`
- `motor_028`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/crawler_store.py`
- `runtime-orchestrator/src/runtime_orchestrator/ingestion_learning.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`

Outputs to add:

- `source_acquisition_yield_memory`
- `browser_success_failure_summary`
- `static_success_failure_summary`

Changes required:

- distinguish static success/failure from browser success/failure
- include acquisition mode in cache/yield reasoning
- expose low-yield and browser-justified families back to planner state

Dependencies:

- `DCP-05`

Acceptance:

- planner can learn that some sources are poor static targets but viable browser targets
- repeated browser waste is visible and penalized

Tests:

- extend source-acquisition and ingestion-learning tests

Do-not-break:

- no change to current cache behavior for purely static sources unless required

---

## Wave 3 — Intake And Hypothesis Hardening

### `DCP-07` Congruence Case State And Intake Rescoring

Purpose:

- make dynamic intake driven by case state, not only by question-library membership

Priority:

- `P0`

Status:

- `completed`

Owner:

- `motor_049`
- `congruence_intelligence/dynamic_intake.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`

Outputs to add:

- `congruence_case_state`
- `question_score`
- `question_score_components`
- `activation_reasons`
- `truncated_question_register`

Changes required:

- compose intake state from discovery, loss patterns, comparison blockers, financial exposure priority, hypothesis state, and decision context
- keep `_QUESTION_LIBRARY` as governed prior
- rescore questions by discrimination value, claim-blocking value, comparison-unlock value, falsification value, tariff consequence, and boundary consequence
- make truncation explicit if the cap remains

Dependencies:

- `DCP-06`

Acceptance:

- active loss patterns and comparison blockers can elevate questions
- truncation is explicit and auditable
- intake remains compact but no longer silently positional

Tests:

- extend `test_dynamic_intake_generator.py`

Do-not-break:

- do not turn intake into an unbounded questionnaire

---

### `DCP-08` Structured Hypothesis And Claim-Governance Mapping

Purpose:

- replace substring heuristics with structured blocked-claim and hypothesis mappings

Priority:

- `P0`

Status:

- `completed`

Owner:

- `congruence_intelligence/hypothesis_ingestion.py`
- `congruence_intelligence/dynamic_intake.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`

Outputs to add:

- `blocked_claims_if_missing`
- `supports_hypotheses`
- `falsifies_hypotheses`
- `comparison_requirements_unlocked`
- structured hypothesis objects

Changes required:

- move blocked-claim governance into explicit question specs
- build rival hypothesis surfaces from structured fields rather than naming coincidences
- preserve current output registers while swapping their source logic

Dependencies:

- `DCP-07`

Acceptance:

- renaming a question ID does not weaken governance
- new question families can be added without fragile string-coupling

Tests:

- extend `test_hypothesis_driven_ingestion.py`

Do-not-break:

- no relaxation of claim ceilings while migrating logic

---

## Wave 4 — Fair Comparison Hardening

### `DCP-09` Evidence-Based Peer Boundedness

Purpose:

- force fair-peer logic to depend on affirmative evidence surfaces rather than question absence

Priority:

- `P0`

Status:

- `completed`

Owner:

- `congruence_intelligence/peer_set_builder.py`
- `motor_051`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_set_builder.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

Outputs to add:

- `evidence_basis`
- `bounded_by`
- `why_still_unbounded`
- `peer_requirement_evidence_state`

Changes required:

- derive boundedness from public evidence, pack states, local binding state, and explicit confirmation surfaces
- remove any auto-upgrade caused by non-triggered question IDs
- preserve hard comparison invalidity when required evidence remains absent

Dependencies:

- `DCP-08`

Acceptance:

- absent question cannot produce `bounded`
- explicit evidence removal keeps comparison blocked
- warehouse subtype, schedule, charging, and control-boundary remain hard blockers until evidenced

Tests:

- extend `test_fair_peer_set_builder.py`

Do-not-break:

- do not soften `comparison_not_yet_valid` language

---

## Wave 5 — Acceptance And Closure

### `DCP-10` Warehouse Acceptance Bundle And Certification Refresh

Purpose:

- prove the strict prompt behavior end-to-end against the warehouse/logistics path and then refresh closure artifacts

Priority:

- `P0`

Status:

- `completed`

Owner:

- `runtime-orchestrator/tests`
- `governanza/automation-base`

Main files:

- new `runtime-orchestrator/tests/test_warehouse_dynamic_congruence_acceptance.py`
- certification docs under `governanza/automation-base`

Outputs to add:

- warehouse acceptance test
- refreshed compliance audit if runtime truth changes
- refreshed closure note if full suite stays green

Changes required:

- assert no stale charts, no empty comparison section, valid next-best-search, valid stop/escalate logic, dynamic intake discrimination, claim prohibition, at least 3 gold nuggets, expanded TAD, and no premature sensor recommendation
- rerun targeted bundle
- rerun full suite

Dependencies:

- `DCP-09`

Acceptance:

- targeted warehouse acceptance bundle green
- full suite green
- updated docs reflect runtime truth rather than intended architecture

Tests:

- `test_warehouse_dynamic_congruence_acceptance.py`
- `pytest -q`

Do-not-break:

- do not refresh docs unless runtime truth is green

## Practical execution order

Execute strictly in this order:

1. `DCP-01`
2. `DCP-02`
3. `DCP-03`
4. `DCP-04`
5. `DCP-05`
6. `DCP-06`
7. `DCP-07`
8. `DCP-08`
9. `DCP-09`
10. `DCP-10`

## First active slice

The first slice that should be implemented now is:

- none

The prompt-completion backlog is closed.
