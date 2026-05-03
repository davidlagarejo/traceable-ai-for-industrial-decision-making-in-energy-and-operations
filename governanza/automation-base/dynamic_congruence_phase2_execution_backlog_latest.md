# Dynamic Congruence Phase 2 Execution Backlog — Latest

Produced at: 2026-05-03

## Current truth

This backlog does **not** reopen prompt-behavior closure.

Current truth remains:

- warehouse/logistics acceptance bundle green;
- full suite green at `502 passed, 15 warnings`;
- `DCP-01` through `DCP-10` complete;
- all required architectural closure is complete;
- optional `P2-07` capability expansion is also complete.

Primary references:

- [dynamic_congruence_phase2_architecture_closure_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_phase2_architecture_closure_latest.md>)
- [dynamic_congruence_browser_lane_operational_certification_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_browser_lane_operational_certification_latest.md>)
- [dynamic_congruence_browser_lane_family_expansion_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_browser_lane_family_expansion_latest.md>)
- [dynamic_congruence_prompt_closure_refresh_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_closure_refresh_latest.md>)
- [dynamic_congruence_prompt_completion_backlog_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_completion_backlog_latest.md>)

## Closure target

Phase 2 is considered complete when all of the following are true:

1. rival hypotheses exist as first-class upstream objects before intake composition;
2. discovery can activate from hypothesis and blocker state, not only from family templates;
3. intake composition is state-led and library-governed, not library-led and state-scored;
4. legacy blocked-claim fallback is no longer needed for current governed question families;
5. the browser lane is certified end-to-end against at least one real JS-only public source without weakening routing, policy, provenance, or case isolation.

## Do-not-break

Do not destabilize:

- `motor_018`
- `motor_036`
- `motor_052`
- `motor_053`
- `motor_054`
- chart case-isolation logic
- claim-count consistency logic
- declared-input downgrade logic
- empty-section fallback logic
- fair-comparison invalidity enforcement

Do not reintroduce:

- uncontrolled browser crawling
- benchmark-as-local-truth
- static intake as final logic
- question-absence boundedness
- string-only blocked-claim governance

## Execution order

1. `P2-00` Phase 2 baseline freeze
2. `P2-01` hypothesis backbone seed layer
3. `P2-02` discovery case-state enrichment
4. `P2-03` state-native discovery activation
5. `P2-04` intake candidate synthesis and normalization
6. `P2-05` hypothesis-ingestion cleanup and legacy fallback retirement
7. `P2-06` browser lane operational certification

Optional after closure:

8. `P2-07` browser-family generalization

---

## `P2-00` Phase 2 Baseline Freeze

Purpose:

- freeze Phase 2 contracts before changing hypothesis/discovery/intake control flow

Priority:

- `P0`

Status:

- `completed`

Main files:

- `runtime-orchestrator/tests/test_dynamic_congruence_baseline_contracts.py`
- `runtime-orchestrator/tests/fixtures/dynamic_congruence_register_contract_snapshot.json`
- `runtime-orchestrator/tests/test_warehouse_dynamic_congruence_acceptance.py`

Changes required:

- capture current register shapes for `motor_049`, `motor_051`, `motor_052`, `motor_053`, `motor_054`
- add explicit assertions around additive-only expansion of:
  - `congruence_case_state`
  - `rival_hypothesis_register`
  - `claim_impact_register`
  - `peer_requirement_register`
  - `financial_exposure_type_register`

Acceptance:

- current suite remains green
- current register shapes are snapshotted
- Phase 2 work has a no-regression baseline
- additive hypothesis-backbone surfaces are now covered by directed regression tests

Tests:

- targeted contract bundle
- warehouse acceptance bundle
- full `pytest -q`

---

## `P2-01` Hypothesis Backbone Seed Layer

Purpose:

- create first-class upstream hypothesis objects before intake composition

Priority:

- `P0`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_backbone.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/__init__.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/tests/test_hypothesis_backbone.py`
- `runtime-orchestrator/tests/test_hypothesis_driven_ingestion.py`

Outputs to add:

- `rival_hypothesis_seed_register`
- `dominant_hypothesis_register`
- `hypothesis_evidence_gap_register`
- `hypothesis_claim_blocker_register`

Suggested input basis:

- `discovery_need_register`
- `next_best_search_register`
- `search_failure_effect_register`
- `search_success_effect_register`
- `tariff_exposure_register`
- `control_boundary_evidence_register`
- `maintenance_proof_evidence_register`
- `entity_resolution_state`
- `operational_intake_pack`

Changes required:

- build governed hypothesis archetypes by asset family
- select active rival hypotheses from actual case pressure, not from question IDs
- compute dominant hypothesis candidates by evidence gap, claim risk, and financial consequence
- emit additive hypothesis objects before `build_dynamic_intake_question_register()`

Acceptance:

- `motor_049` emits hypothesis seed surfaces before intake composition
- dominant hypothesis can be derived without looking at question text or IDs
- blocked claims can be derived from hypothesis objects, not only from intake metadata
- dynamic intake now consumes dominant-hypothesis alignment as an additive score signal

Tests:

- tariff-heavy warehouse vs control-boundary-heavy warehouse yield different dominant hypotheses
- maintenance-heavy manufacturing case elevates maintenance hypothesis without changing asset family
- question ID rename does not alter hypothesis seed outputs

Do-not-break:

- keep existing downstream `rival_hypothesis_register` output shape alive during migration

---

## `P2-02` Discovery Case-State Enrichment

Purpose:

- extend discovery state so the planner can react to active hypotheses and blockers

Priority:

- `P0`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/tests/test_dynamic_case_state_builder.py`

Outputs to add:

- `active_rival_hypotheses`
- `dominant_hypothesis_ids`
- `active_comparison_blockers`
- `active_loss_pattern_candidates`
- `active_financial_exposure_candidates`
- `active_contradiction_targets`
- `source_family_failure_pressure`
- `source_family_success_pressure`

Changes required:

- thread `P2-01` hypothesis outputs into discovery-side state
- convert current success/failure summaries into planner-facing pressure signals
- keep all current `DiscoveryCaseState` fields additive and backward-compatible

Acceptance:

- `DiscoveryCaseState` exposes enough information for discovery activation without parsing downstream questions
- state fields remain serializable and snapshot-testable
- provisional upstream hypothesis, blocker, loss-pattern, finance, and contradiction pressure now emit additively

Tests:

- enriched state contains hypothesis and blocker pressure surfaces
- pressure surfaces survive previous-run memory and current-run attempts together

Do-not-break:

- do not remove current fields like `mandatory_source_gaps`, `source_family_yield_memory`, `technical_scraping_allowed`

---

## `P2-03` State-Native Discovery Activation

Purpose:

- allow discovery needs to activate from case-state pressure, not only from family templates and gap overlap

Priority:

- `P0`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py`
- `runtime-orchestrator/tests/test_dynamic_source_discovery_engine.py`
- `runtime-orchestrator/tests/test_next_best_search_engine.py`

Outputs to add:

- `activation_basis_register` per discovery need
- additive `hypothesis_pressure_score`
- additive `comparison_pressure_score`
- additive `contradiction_pressure_score`

Changes required:

- keep `_GENERIC_DISCOVERY_NEEDS` and `_FAMILY_DISCOVERY_NEEDS` as governed priors
- add state-native activation scoring above template priors
- allow discovery needs to surface because:
  - a rival hypothesis needs discrimination
  - a comparison blocker remains unresolved
  - a contradiction target is active
  - a repeated source-family failure should redirect exploration

Acceptance:

- two same-family cases can produce different discovery-need ordering due to hypothesis pressure
- repeated failure can suppress one route and promote another route in the same need family
- discovery rows explain whether activation came from family prior or state pressure
- discovery rows now expose `activation_basis_register` and explicit pressure scores without breaking existing register names

Tests:

- Dallas warehouse with tariff pressure vs Dallas warehouse with maintenance pressure
- repeated property-listing failure promotes authoritative route
- comparison blocker can activate discovery even when requestable evidence text is weak

Do-not-break:

- keep current public register names and current validator assumptions intact

---

## `P2-04` Intake Candidate Synthesis And Normalization

Purpose:

- make intake composition state-led while preserving governed question wording and metadata

Priority:

- `P0`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/tests/test_dynamic_intake_generator.py`

Outputs to add:

- `decision_context_register`
- `question_candidate_register`
- `question_normalization_register`

Changes required:

- split current intake flow into:
  - candidate synthesis from state and hypotheses
  - normalization back onto governed question specs
- drive candidates from:
  - `dominant_hypothesis_register`
  - `comparison_blocker_register`
  - `active_loss_pattern_candidates`
  - `financial_exposure_priority`
  - `decision_intent`
  - `report_intent`
- preserve current `dynamic_intake_question_register` as the normalized, governed output

Acceptance:

- intake now exposes explicit `decision_context_register`
- candidate synthesis is separated from governed normalization
- `dynamic_intake_question_register` remains the normalized governed surface
- truncation remains explicit and auditable

Tests:

- `decision_context_register` / `question_candidate_register` / `question_normalization_register` contract tests
- tariff-dominant hypothesis remains aligned through candidate synthesis and normalization
- top-cap truncation preserves `truncated_question_register`

Do-not-break:

- no arbitrary new question text in report surfaces
- no weakening of blocked-claim metadata

---

## `P2-05` Hypothesis-Ingestion Cleanup And Legacy Fallback Retirement

Purpose:

- remove the remaining dependency on string heuristics for blocked claims and hypothesis relations

Priority:

- `P1`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`
- `runtime-orchestrator/tests/test_hypothesis_driven_ingestion.py`

Changes required:

- ensure every governed question family has full structured metadata for:
  - `blocked_claims_if_missing`
  - `supports_hypotheses`
  - `falsifies_hypotheses`
  - `comparison_requirements_unlocked`
- retire `legacy_string_fallback` for active governed families
- keep compatibility only behind an explicit compatibility path if needed for old fixtures

Acceptance:

- `claim_governance_basis` resolves to structured metadata for active governed cases
- legacy string fallback survives only behind explicit compatibility
- no current warehouse/manufacturing acceptance route depends on implicit legacy fallback

Tests:

- warehouse acceptance path never emits implicit legacy fallback
- explicit compatibility flag is required to reach legacy fallback
- metadata gaps now prohibit claims instead of silently guessing blocked-claim governance

Do-not-break:

- no sudden breakage for legacy archived fixtures unless intentionally version-bumped

---

## `P2-06` Browser Lane Operational Certification

Purpose:

- prove the bounded browser lane works end-to-end on a real JS-only public source

Priority:

- `P1`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/strategy_selector.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/playwright_fetch.py`
- `runtime-orchestrator/tests/test_motor_028_browser_acquisition.py`
- `runtime-orchestrator/tests/test_source_acquisition_strategy.py`
- `runtime-orchestrator/tests/test_playwright_policy.py`
- `runtime-orchestrator/tests/test_playwright_provenance.py`
- new certification test or captured fixture

Scope:

- this ticket certifies the current bounded browser lane
- it does **not** yet generalize browser execution across more families

Changes required:

- choose one public JS-rendered portal already admissible under routing
- capture or replay a stable certification fixture
- prove:
  - static probe fails or is shell-only
  - strategy escalates to `playwright_public_page`
  - browser result yields provenance
  - source-family coverage table records browser justification cleanly

Acceptance:

- one real browser-needed public source is certified end-to-end
- policy gate still blocks login-like or non-public sources
- route-denied or `technical_scraping_allowed=false` cases never escalate

Tests:

- certification test and live certification note for one JS-only public source
- browser policy tests
- provenance stability tests
- rerun full suite

Do-not-break:

- keep browser disabled by default
- keep navigation bounded
- no broad crawling

---

## `P2-07` Optional Browser-Family Generalization

Purpose:

- generalize browser eligibility beyond `official_portal_context` only if product direction actually needs it

Priority:

- `P2`

Status:

- `completed`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/policy.py`
- `runtime-orchestrator/src/runtime_orchestrator/source_acquisition/strategy_selector.py`

Suggested additions:

- `browser_eligible`
- `selector_plan_key`
- `max_browser_navigations`
- `public_page_kind`

Implemented shape:

- source-type capability registry with explicit opt-in
- utility territory contexts expanded beyond the original family-only gate
- policy still requires either family whitelist or explicit source-type eligibility

Closure note:

- this ticket was not required for prompt closure, but it is now completed

## Final interpretation

Now that `P2-01` through `P2-06` are complete, it is reasonable to claim:

- `100%` prompt behavior closure
- `100%` governed architectural closure

`P2-07` was capability expansion, not mandatory closure, and is now also complete.
