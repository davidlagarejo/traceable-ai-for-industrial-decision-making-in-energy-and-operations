# Dynamic Congruence Prompt Execution Plan — Latest

Produced at: 2026-05-03

## Purpose

This document turns the compliance audit into an executable completion plan.

It is not a redesign-from-zero plan.
It is a surgical completion plan for the residual architectural gap between:

- behavioral closure already achieved by the current runtime;
- the stricter architectural reading of the `Dynamic Congruence Intelligence System` prompt.

## Executive decision

The prompt is already closed at behavior level, but not yet at full state-composition depth.

The remaining work is concentrated in five areas:

1. discovery still reasons from family templates more than from full evolving case state;
2. next-best-search prioritizes needs better than it prioritizes source families within each need;
3. dynamic intake is still library-first instead of case-state-first;
4. hypothesis-driven ingestion still relies on fragile string heuristics for blocked claims;
5. fair peer logic can still infer boundedness from question absence instead of affirmative evidence.

The correct strategy is:

- preserve the validator and report-integrity core;
- deepen dynamic state composition;
- add a controlled browser acquisition layer for hard public pages;
- expand tests before broadening execution.

## What must remain stable

Do not destabilize these modules unless a defect is proven:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py`

These already carry the non-negotiable rules:

- no stale charts;
- no claim-count drift;
- no empty critical sections without explanation;
- no declared input promoted to verified evidence;
- no fake ROI or unsupported strategic claim;
- no report generation when consistency gates fail.

## Final completion target

The prompt is considered fully executed only when all of the following are true:

1. discovery need activation is driven by explicit case state, not only family templates;
2. next-best-search selects the best source family with a scored reason register;
3. browser-rendered public sources can be acquired without bypassing routing, provenance, or anti-contamination rules;
4. intake prioritization is driven by dominant hypotheses, loss-pattern candidates, comparison blockers, and financial exposure consequences;
5. blocked-claim governance is structured, not string-heuristic-based;
6. fair comparison boundedness depends on affirmative evidence surfaces;
7. the warehouse/logistics acceptance bundle passes with case-specific dynamic surfaces and no forbidden claims.

## Architectural principle

The system must continue to behave like this:

`target -> classification -> routed public discovery -> evidence/gaps -> new questions -> contradictions -> minimum evidence -> TAD -> output mode`

It must not drift back toward:

`fixed asset family template -> fixed query list -> fixed report lane`

## Decision on Playwright

Playwright should be used, but only as a bounded acquisition backend.

It should not become:

- the main planner;
- a default scraper for all sources;
- a broad crawler;
- a workaround for weak source routing;
- a mechanism to click through arbitrary pages until something useful appears.

### Where Playwright helps

Playwright is justified for public sources that are genuinely JS-rendered or interaction-gated while still public and admissible, for example:

- county assessor portals rendered client-side;
- public permit portals rendered through JS forms or tables;
- GIS parcel portals where the final parcel result is public but not visible through static HTML;
- owner/operator pages with hydration-only content;
- public leasing or brochure landing pages where static fetch returns shell HTML only.

### Where Playwright must be prohibited

Playwright must not be used for:

- login walls;
- CAPTCHA bypass;
- authenticated portals;
- paywalled portals;
- aggressive crawling;
- search engine automation outside already approved routed search APIs;
- form submission that changes server state;
- any source family that routing has marked as not allowed;
- any case where `technical_scraping_allowed=false`.

### Playwright operating mode

Playwright should run only in `bounded public page acquisition` mode:

- max 1 browser context per source attempt;
- max 1-3 navigations per attempt;
- hard timeout per page;
- explicit selector plan;
- network and DOM provenance captured;
- headless by default;
- disabled by default unless capability and policy allow it.

## Target architecture

### Layer 1 — Routing and eligibility

Authority remains:

- `motor_035` for public-data routing and technical eligibility;
- upstream classification and subject gate for whether technical scraping is even allowed.

No browser layer may override routing.

### Layer 2 — Discovery case state

Create a new discovery-side state object built inside `motor_028`.

Suggested file:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py`

Suggested object:

- `DiscoveryCaseState`

Suggested fields:

- `case_fingerprint`
- `asset_fingerprint`
- `target_identifier`
- `target_type`
- `asset_family`
- `jurisdiction_scope`
- `industry_context`
- `technical_scraping_allowed`
- `route_report_type_allowed`
- `coverage_gap_types`
- `coverage_gap_severities`
- `requestable_evidence_items`
- `active_regulatory_triggers`
- `source_family_failures`
- `source_family_successes`
- `source_family_yield_memory`
- `mandatory_source_gaps`
- `budget_state`
- `identity_state`
- `operator_boundary_state`
- `schedule_state`
- `control_boundary_state`
- `utility_context_state`
- `previous_run_progress_signals`

This object must be built from existing upstream surfaces, not invented.

### Layer 3 — Discovery planning

`discovery_planner.py` should continue to emit the same public registers, but scoring must consume `DiscoveryCaseState`.

It should still use the research library as governed prior knowledge.

It should stop acting as if the library itself were the case state.

### Layer 4 — Source-family ranking

`next_best_search.py` must choose:

- the next discovery need;
- the best source family inside that need;
- the reason why that family beat the alternatives.

Add:

- `family_rank_register`
- `selected_search_family_reason`
- `family_score_components`

Do not remove current output fields.

### Layer 5 — Acquisition strategy selection

Create an acquisition strategy selector between planning and execution.

Suggested new package:

- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/`

Suggested files:

- `strategy_selector.py`
- `policy.py`
- `http_fetch.py`
- `playwright_fetch.py`
- `provenance.py`
- `render_classifier.py`

Allowed acquisition modes:

- `api_request`
- `static_http_html`
- `static_http_json`
- `pdf_download_extract`
- `search_api_query`
- `playwright_public_page`

Every attempted source must declare one mode.

### Layer 6 — Congruence case state

Create a second state object for intake and hypothesis composition after discovery surfaces exist.

Suggested object:

- `CongruenceCaseState`

Suggested fields:

- all relevant `DiscoveryCaseState` fields;
- `active_discovery_needs`
- `next_best_search_register`
- `search_failure_effect_register`
- `search_success_effect_register`
- `activated_pattern_register`
- `comparison_blocker_register`
- `financial_exposure_priority_register`
- `dominant_hypothesis_register`
- `decision_context`
- `pack_state_summary`
- `claim_blocker_summary`

This becomes the basis for `motor_049`, `hypothesis_ingestion.py`, and `peer_set_builder.py`.

## Workstream plan

## Workstream 0 — Freeze baseline and protect congruence

### Goal

Establish a no-regression baseline before touching dynamic behavior.

### Files to touch

- no behavior changes required first;
- add or update only test fixtures and planning docs.

### Actions

1. Freeze current green baseline:
   - `pytest -q`
   - record `455 passed, 15 warnings` as the pre-change truth.
2. Capture one warehouse/logistics case fixture and one manufacturing fixture as canonical dynamic-ingestion baselines.
3. Record existing output contracts for:
   - `discovery_need_register`
   - `next_best_search_register`
   - `dynamic_intake_question_register`
   - `hypothesis_discrimination_register`
   - `peer_requirement_register`
4. Add anti-regression assertions that current validator lanes do not change shape.

### Exit criteria

- full suite still green;
- new baseline fixtures committed;
- no contract ambiguity before refactor.

## Workstream 1 — Build `DiscoveryCaseState`

### Goal

Move discovery reasoning from loosely inferred context toward explicit case state.

### Files to add

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py`

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/ingestion_learning.py`
- optionally `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/schemas.py`

### Actions

1. Build a `DiscoveryCaseState` constructor fed by:
   - `target_definition`
   - routing eligibility from `motor_035`
   - `coverage_gaps`
   - `requestable_evidence_items`
   - `attempts`
   - `search_budget_register`
   - previous-run source-yield memory
   - previous-run mandatory-source gaps
2. Normalize `source_family_failures` and `source_family_successes` from the existing attempt ledger.
3. Normalize a `regulatory_trigger_register` from routed public layers and jurisdiction scope.
4. Persist `discovery_case_state` inside `motor_028` output without removing old keys.

### Tests to add

- `tests/test_dynamic_case_state_builder.py`
- ensure TX warehouse and NYC warehouse produce different jurisdiction-sensitive state.
- ensure repeated failure history is reflected in state.
- ensure routing-disabled cases set `technical_scraping_allowed=false`.

### Exit criteria

- `motor_028` emits `discovery_case_state`;
- no downstream module breaks;
- old outputs remain intact.

## Workstream 2 — Deepen discovery planning

### Goal

Keep the current discovery output schema but make activation and ranking consume explicit state.

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`

### Actions

1. Extend `build_discovery_need_register()` to accept `dynamic_case_state`.
2. Keep `_GENERIC_DISCOVERY_NEEDS` and `_FAMILY_DISCOVERY_NEEDS` as priors.
3. Add scoring inputs:
   - jurisdiction fit;
   - regulatory trigger match;
   - gap severity;
   - source-yield memory;
   - operator-escalation risk;
   - comparison relevance;
   - active evidence blocker relevance.
4. Add fields per discovery need:
   - `activation_reasons`
   - `state_signals_used`
   - `jurisdiction_fit`
   - `source_family_preference_hints`
5. Do not let discovery emit needs that violate `technical_scraping_allowed=false`.

### Tests to add

- extend `tests/test_dynamic_source_discovery_engine.py`
- TX and NYC warehouse should not have identical family ordering.
- active tariff context should elevate utility-family needs.
- failed listing-family attempts should elevate alternate assessor/operator families.

### Exit criteria

- discovery output still backward-compatible;
- activation reasons are auditable;
- source-family preference hints exist for each active need.

## Workstream 3 — Add source-family reranking

### Goal

Make `next_best_search` truly choose the next best family instead of defaulting to the first template entry.

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py`

### Actions

1. Accept either `dynamic_case_state` or an equivalent compact scoring input.
2. Score each family by:
   - jurisdiction fit;
   - evidence discriminative value;
   - prior case success;
   - prior case failure;
   - operator-vs-public likelihood;
   - hypothesis relevance;
   - comparison unlock value;
   - regulatory value;
   - expected acquisition difficulty;
   - time-budget fit.
3. Replace `search_families[0]` with scored selection.
4. Add:
   - `family_rank_register`
   - `selected_search_family_reason`
   - `selected_search_family_score`
   - `family_score_components`
5. Preserve:
   - `next_search_target`
   - `if_found`
   - `if_not_found`
   - `stop_condition`

### Tests to add

- extend `tests/test_next_best_search_engine.py`
- failure of `property_listing` should elevate `county_assessor` or `tenant_operator_page` when relevant;
- tariff hypothesis should elevate `utility_service_territory` ahead of generic listing families;
- exhausted budget should demote expensive browser-backed families.

### Exit criteria

- ranked needs still pass current tests;
- family-level selection is explicit and explainable.

## Workstream 4 — Add controlled Playwright acquisition

### Goal

Enable evidence capture from hard public pages without breaking provenance, routing, or anti-contamination rules.

### Files to modify

- `runtime-orchestrator/pyproject.toml`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/crawler_store.py`

### Files to add

- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/__init__.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/policy.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/strategy_selector.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/render_classifier.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/playwright_fetch.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/provenance.py`

### Dependency plan

Add optional dependency, not default dependency:

- `[project.optional-dependencies]`
- `browser = ["playwright>=1.54"]`

Do not make the default install depend on browsers.

### Environment controls

Add env flags:

- `ZLAB_BROWSER_DISCOVERY_ENABLED=0|1`
- `ZLAB_PLAYWRIGHT_TIMEOUT_SECONDS`
- `ZLAB_PLAYWRIGHT_MAX_NAV_STEPS`
- `ZLAB_PLAYWRIGHT_HEADLESS=1`
- `ZLAB_PLAYWRIGHT_ALLOWED_SOURCE_FAMILIES`

Default:

- browser disabled;
- static/API modes remain primary.

### Acquisition policy

Playwright may run only when all conditions are true:

1. `technical_scraping_allowed=true`
2. the source family is in the allowed policy
3. static fetch failed or render classifier marks page as JS-dependent
4. no login or CAPTCHA is required
5. current budget allows browser mode
6. the route remains public and admissible

### Provenance to capture

For every Playwright attempt capture:

- `source_key`
- `source_family`
- `attempt_id`
- `case_fingerprint`
- `asset_fingerprint`
- `requested_url`
- `final_url`
- `render_mode`
- `navigation_steps`
- `selectors_used`
- `dom_hash`
- `text_hash`
- `response_status_summary`
- `captured_at`
- `extraction_success`
- `extraction_reason`

Optional debug-only artifacts:

- screenshot hash;
- screenshot path if saved locally.

Screenshots must not become evidence by themselves.

### Execution policy

Use Playwright only for bounded, source-family-specific extractors.

Examples:

- `county_assessor_portal_result_extractor`
- `permit_portal_table_extractor`
- `hydrated_owner_page_extractor`
- `public_gis_result_extractor`

Do not create a generic “click around until useful text appears” mode.

### Tests to add

- `tests/test_source_acquisition_strategy.py`
- `tests/test_playwright_policy.py`
- `tests/test_playwright_provenance.py`

Test cases:

- browser mode blocked when `technical_scraping_allowed=false`;
- browser mode blocked for disallowed family;
- browser mode selected when static HTML is empty shell and family is allowed;
- provenance manifest always records final URL, render mode, and hashes;
- browser timeout degrades to coverage gap, never fabricated evidence.

### Exit criteria

- Playwright integrated as optional capability;
- no routing violation;
- no claim may harden from browser acquisition without normal evidence admission.

## Workstream 5 — Feed browser acquisition back into discovery learning

### Goal

Avoid expensive repeated browser attempts and keep the planner aware of source yield.

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/crawler_store.py`
- `runtime-orchestrator/src/runtime_orchestrator/ingestion_learning.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`

### Actions

1. Extend cache keying to include acquisition mode.
2. Add yield-memory distinctions:
   - `static_success`
   - `static_failure`
   - `browser_success`
   - `browser_failure`
   - `identity_only_yield`
3. Allow next runs to learn:
   - which families are low-yield in static mode;
   - which families justify browser fallback;
   - which families should be escalated to operator intake instead.

### Exit criteria

- no repeated wasteful browser attempts by default;
- source-family reranking can use browser-vs-static yield memory.

## Workstream 6 — Rebuild intake as a state-composed scorer

### Goal

Keep the governed library but stop treating it as the final question list.

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`

### Actions

1. Add `CongruenceCaseState` construction inside `motor_049`.
2. Keep `_QUESTION_LIBRARY` as candidate priors.
3. Score each question by:
   - hypothesis discrimination value;
   - claim-blocking value;
   - comparison unlock value;
   - loss-pattern falsification value;
   - tariff exposure consequence;
   - control-boundary consequence;
   - financial exposure consequence;
   - public search exhaustion relevance.
4. Add fields to each question row:
   - `question_score`
   - `question_score_components`
   - `activation_reasons`
   - `blocked_claims_if_missing`
   - `supports_hypotheses`
   - `falsifies_hypotheses`
   - `comparison_requirements_unlocked`
5. If the top cap remains `8`, emit:
   - `truncated_question_register`
   - `truncation_reason`
   - `questions_dropped_due_to_cap`

### Tests to add

- extend `tests/test_dynamic_intake_generator.py`
- active loss pattern should elevate its discriminator question;
- active tariff exposure should elevate charging/tariff questions;
- comparison blocker should elevate subtype/schedule/boundary questions;
- when more than 8 questions are triggered, truncation must be explicit and auditable.

### Exit criteria

- intake remains concise;
- every dropped question is visible and justified;
- intake is driven by case state, not only need IDs.

## Workstream 7 — Replace hypothesis heuristics with structured mappings

### Goal

Make blocked-claim and rival-hypothesis logic robust to future question additions.

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`

### Actions

1. Remove substring-based `_blocked_claims()` logic.
2. Require each question spec to explicitly carry:
   - `blocked_claims_if_missing`
   - `supports_hypotheses`
   - `falsifies_hypotheses`
   - `comparison_requirements_unlocked`
3. Add optional first-class hypothesis objects:
   - `hypothesis_id`
   - `hypothesis_text`
   - `hypothesis_class`
   - `evidence_required`
   - `evidence_that_falsifies`
   - `financial_exposure_if_true`
4. Build hypothesis registers from structured fields, not from ID naming.

### Tests to add

- extend `tests/test_hypothesis_driven_ingestion.py`
- renaming `question_id` must not weaken blocked claims;
- adding a new question family must preserve claim governance;
- missing evidence must prohibit the right claims even if wording changes.

### Exit criteria

- no blocked-claim governance depends on string coincidence.

## Workstream 8 — Harden fair peer logic to affirmative evidence

### Goal

Stop peer boundedness from loosening just because a question was not triggered.

### Files to modify

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_set_builder.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

### Actions

1. Replace question-absence inference with evidence-based derivation.
2. For each peer requirement derive state from:
   - public source evidence;
   - pack current states;
   - local binding states;
   - structured confirmation states;
   - explicit operator confirmation if present.
3. Add fields:
   - `evidence_basis`
   - `bounded_by`
   - `why_still_unbounded`
   - `evidence_state`
4. Keep hard comparison prohibition when required evidence remains missing.

### Tests to add

- extend `tests/test_fair_peer_set_builder.py`
- absent question must not auto-upgrade to `bounded`;
- explicit evidence removal must keep comparison blocked;
- subtype, schedule, charging, and control-boundary claims remain blocked until evidence exists.

### Exit criteria

- peer fairness depends on evidence surfaces only.

## Workstream 9 — Expand warehouse/logistics acceptance tests

### Goal

Prove the architecture against the original warehouse prompt, not only unit registers.

### Files to add

- `runtime-orchestrator/tests/test_warehouse_dynamic_congruence_acceptance.py`

### Acceptance assertions

1. no stale chart from foreign case;
2. no empty peer section without explanation;
3. fair peer requirements explicitly shown;
4. logistics loss patterns activated as bounded plausibility, not hallucinated fact;
5. next search targets emitted with reason, family, expected evidence, and stop condition;
6. dynamic intake questions emitted with discrimination logic;
7. declared input remains downgraded until public or operator confirmation;
8. generic EUI interpretation prohibited when subtype/schedule/dock/charging remain unbounded;
9. at least 3 gold nuggets produced;
10. expanded TAD emits more than three strategic actions;
11. no sensor recommendation before hypothesis discrimination;
12. stop vs escalate logic clearly shown.

### Exit criteria

- warehouse acceptance test passes end-to-end.

## Workstream 10 — Full certification and documentation closure

### Goal

Refresh the authoritative artifacts only after runtime truth is green.

### Actions

1. Run targeted dynamic bundle:
   - `pytest -q tests/test_dynamic_case_state_builder.py tests/test_dynamic_source_discovery_engine.py tests/test_next_best_search_engine.py tests/test_source_acquisition_strategy.py tests/test_playwright_policy.py tests/test_playwright_provenance.py tests/test_dynamic_intake_generator.py tests/test_hypothesis_driven_ingestion.py tests/test_fair_peer_set_builder.py tests/test_warehouse_dynamic_congruence_acceptance.py`
2. Run full suite:
   - `pytest -q`
3. Only if green, refresh:
   - prompt compliance audit;
   - DCI closure boundary status;
   - AGENTS reentry notes if needed.

### Exit criteria

- targeted bundle green;
- full suite green;
- updated docs reflect runtime truth, not wishful closure.

## Module change map

### Modify

- `runtime-orchestrator/pyproject.toml`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_set_builder.py`
- `runtime-orchestrator/src/runtime_orchestrator/ingestion_learning.py`
- `runtime-orchestrator/src/runtime_orchestrator/crawler_store.py`

### Add

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/__init__.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/policy.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/strategy_selector.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/render_classifier.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/playwright_fetch.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/provenance.py`

### Preserve

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py`

## Execution order

The order should be strict:

1. baseline freeze and fixtures
2. `DiscoveryCaseState`
3. discovery-planner enrichment
4. source-family reranking
5. Playwright acquisition policy and provenance
6. browser/static yield memory
7. intake scorer enrichment
8. structured hypothesis mappings
9. peer fairness hardening
10. warehouse acceptance bundle
11. full-suite rerun
12. documentation refresh

Do not start with Playwright before discovery ranking is explicit.
Otherwise the browser layer will compensate for planner weakness instead of fixing it.

## Risk controls

### Risk 1 — Browser mode widens side effects

Mitigation:

- browser disabled by default;
- policy whitelist by source family;
- no authenticated flows;
- hard timeout and navigation cap.

### Risk 2 — New state object breaks downstream contracts

Mitigation:

- additive outputs only;
- no key removals in initial implementation;
- adapter integration tests before cleanup.

### Risk 3 — Intake scorer overfits and becomes unstable

Mitigation:

- preserve governed library as prior;
- only add explicit score components;
- keep deterministic ordering and auditable reasons.

### Risk 4 — Fair peer hardening blocks too much

Mitigation:

- blocked vs conditional thresholds must be evidence-state-based;
- warehouse acceptance tests define the minimum valid behavior.

### Risk 5 — Playwright contaminates evidence provenance

Mitigation:

- explicit provenance manifest per attempt;
- final URL and asset fingerprint recorded;
- browser evidence admitted only through existing evidence governance, never directly.

## Definition of done

This prompt is truly complete when the warehouse/logistics case can produce all of the following without manual source padding:

- dynamic discovery needs with jurisdiction-aware family ranking;
- public-source search program that knows when to switch from static to browser mode;
- explicit next-best-search rows with stop, downgrade, and escalate conditions;
- intake questions prioritized by discrimination value, not by template position;
- blocked claims derived from structured mappings;
- fair peer logic blocked until subtype, service intensity, charging, and boundary are truly evidenced;
- at least 3 strong gold nuggets;
- expanded TAD;
- zero stale artifacts;
- zero claim-count inconsistencies;
- zero empty critical sections.

## Immediate next implementation slice

The first code slice should cover only these files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py`
- `runtime-orchestrator/tests/test_dynamic_case_state_builder.py`
- `runtime-orchestrator/tests/test_dynamic_source_discovery_engine.py`
- `runtime-orchestrator/tests/test_next_best_search_engine.py`

That slice gives the planner a real state backbone before any browser acquisition or intake redesign starts.
