# Dynamic Congruence Phase 2 Architecture Closure — Latest

Produced at: 2026-05-03

## Purpose

This document records the architectural work that was required to claim `100%` closure of the `Dynamic Congruence Intelligence System` prompt under the strictest reading.

It does **not** reopen the prompt-completion backlog.

Current runtime truth remains:

- warehouse/logistics acceptance bundle green;
- full suite green at `502 passed, 15 warnings`;
- prompt behavior closed;
- strict architectural closure is complete;
- optional capability expansion under `P2-07` is also complete.

Primary references:

- [dynamic_congruence_prompt_closure_refresh_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_closure_refresh_latest.md>)
- [dynamic_congruence_prompt_compliance_audit_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_compliance_audit_latest.md>)
- [dynamic_congruence_prompt_completion_backlog_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_prompt_completion_backlog_latest.md>)
- [dynamic_congruence_browser_lane_operational_certification_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_browser_lane_operational_certification_latest.md>)
- [dynamic_congruence_browser_lane_family_expansion_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_browser_lane_family_expansion_latest.md>)

## Current truth

The framework already satisfies the prompt at behavior level.

The narrower question this document resolved was:

Where does the reasoning live?

Today the runtime behaves broadly like this:

`target -> governed family priors + state modulation -> discovery -> intake -> hypothesis surfaces -> governance`

The strictest architectural reading of the prompt would prefer:

`target -> explicit rival hypotheses + evolving case state -> discovery generation -> minimum discriminating evidence -> intake only where needed -> contradiction graph -> governance`

That gap is now small enough to isolate into four architectural closure tickets.

## Ticket P2-01 — Hypothesis Backbone Upstream Of Intake

### Why it still matters

`motor_049` currently builds `congruence_case_state`, then builds the dynamic intake, and only afterward derives:

- `rival_hypothesis_register`
- `hypothesis_discrimination_register`
- `claim_impact_register`

This means the hypothesis object is still downstream of the governed question layer.

Relevant current seam:

- [motor_049.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py:354)
- [hypothesis_ingestion.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py:109)

### Minimal correct change

Add a new upstream hypothesis lane inside `motor_049`, before dynamic intake composition.

Suggested new outputs:

- `rival_hypothesis_seed_register`
- `dominant_hypothesis_register`
- `hypothesis_evidence_gap_register`
- `hypothesis_claim_blocker_register`

Suggested new module:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_backbone.py`

Suggested input basis:

- `discovery_need_register`
- `next_best_search_register`
- `search_failure_effect_register`
- `search_success_effect_register`
- `operational_intake_pack`
- `tariff_exposure_register`
- `control_boundary_evidence_register`
- `maintenance_proof_evidence_register`
- `entity_resolution_state`

### Non-negotiable rule

Do not generate free-text hypotheses from scratch.

Hypotheses must still be assembled from governed archetypes, but they must become first-class runtime objects before intake composition.

### Acceptance

- `motor_049` emits a first-class hypothesis seed layer before intake composition.
- `dynamic_intake.py` can consume `dominant_hypothesis_register`.
- `hypothesis_ingestion.py` becomes a renderer / normalizer of upstream hypothesis objects, not their birthplace.
- `legacy_string_fallback` becomes removable or isolated behind an explicit compatibility flag.

### Tests

- hypothesis seeds differ between a tariff-heavy warehouse and a maintenance-heavy warehouse even if family is identical;
- blocked claims can be derived without reading question IDs;
- renaming a question ID cannot change dominant hypothesis or blocked-claim governance.

## Ticket P2-02 — State-Native Discovery Activation

### Why it still matters

Discovery now uses `dynamic_case_state`, but activation still begins from governed templates:

- [discovery_planner.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py:588)
- [dynamic_case_state.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_case_state.py:145)

Current state modulation is strong but still secondary.

### Minimal correct change

Extend `DiscoveryCaseState` so that the planner can activate discovery needs from explicit case-state drivers, not only from family templates and gap overlap.

Suggested new `DiscoveryCaseState` fields:

- `active_rival_hypotheses`
- `dominant_hypothesis_ids`
- `active_comparison_blockers`
- `active_loss_pattern_candidates`
- `active_financial_exposure_candidates`
- `active_contradiction_targets`
- `source_family_failure_pressure`
- `source_family_success_pressure`

Suggested new planner behavior:

- each discovery need row should expose whether it was activated by:
  - family prior;
  - hypothesis pressure;
  - comparison blocker pressure;
  - loss-pattern pressure;
  - regulatory pressure;
  - contradiction pressure.

### Non-negotiable rule

Do not delete `_GENERIC_DISCOVERY_NEEDS` or `_FAMILY_DISCOVERY_NEEDS`.

Demote them to governed priors.
Do not replace them with unconstrained search generation.

### Acceptance

- two same-family cases with different active hypotheses produce different discovery activation reasons;
- comparison blockers can activate discovery even when requestable evidence text is weak;
- source-family failures can suppress one discovery route while promoting another route in the same need cluster.

### Tests

- tariff-dominant Dallas warehouse vs maintenance-dominant Dallas warehouse;
- NYC benchmarking-heavy building vs Texas logistics node;
- repeated county-assessor failure shifts identity anchoring toward alternate authoritative families without breaking routing.

## Ticket P2-03 — Library-Demoted Intake Composer

### Why it still matters

Dynamic intake is no longer static, but it still composes from `_QUESTION_LIBRARY`:

- [dynamic_intake.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py:735)

The scoring layer already uses:

- comparison blockers
- loss-pattern tags
- financial exposure priority

But the library remains the primary origin of the questions.

### Minimal correct change

Split intake into two layers:

1. `question_candidate_synthesis`
2. `governed_question_normalization`

The first layer should assemble candidate questions from:

- `dominant_hypothesis_register`
- `comparison_blocker_register`
- provisional `loss_pattern_candidate_register`
- `decision_context`
- `financial_exposure_priority_register`

The second layer should map those candidates back onto governed question specs and validation metadata.

Suggested new objects:

- `decision_context_register`
- `question_candidate_register`
- `question_normalization_register`

### Non-negotiable rule

Do not allow arbitrary new question text into the report lane.

Question wording and governance metadata must still resolve to governed specs.

### Acceptance

- the same warehouse case under `underwriting` vs `operator_triage` changes question order and cap allocation;
- a dominant tariff hypothesis can elevate a tariff discriminator even if that question was not top-ranked under family defaults;
- the intake cap remains explicit and auditable with no silent drops.

### Tests

- decision-intent reranking;
- hypothesis-led question promotion;
- truncation audit remains stable;
- no change in governed claim blocking after question normalization.

## Ticket P2-04 — Browser Lane Generalization And Operational Certification

### Why it still matters

Playwright exists, but two limits remain:

1. it is currently wired only through `_maybe_enrich_official_portal_payload()`;
2. the warehouse acceptance bundle does not depend on a real JS-only public source.

Relevant seams:

- [motor_028.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py:6098)
- [motor_028.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py:6114)
- [strategy_selector.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/source_acquisition/strategy_selector.py:8)
- [playwright_fetch.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/source_acquisition/playwright_fetch.py:6)

### Minimal correct change

Split this into two sub-steps.

#### Step A — certify existing bounded browser lane

Create one real end-to-end certification against a public JS-rendered portal that:

- is allowed by routing;
- is public;
- cannot be adequately read from static HTML;
- produces stable provenance manifests.

This closes the operational truth gap without widening scope yet.

#### Step B — optional browser-lane generalization

Generalize browser eligibility from `official_portal_context` to explicit routed public families carrying browser metadata, for example:

- `county_assessor`
- `permit_record`
- `parcel_gis`
- `utility_service_territory`

Only do this through explicit eligibility metadata such as:

- `browser_eligible`
- `selector_plan_key`
- `max_browser_navigations`
- `public_page_kind`

### Non-negotiable rule

Do not turn Playwright into broad crawling.

Browser execution must remain:

- disabled by default;
- policy-gated;
- routing-gated;
- public-only;
- provenance-traced;
- bounded in navigation count and timeout.

### Acceptance

- at least one JS-only public portal is certified end-to-end;
- browser escalation happens only when static probe is insufficient and policy allows it;
- source-family coverage tables show browser provenance cleanly;
- case isolation and chart/report integrity remain unchanged.

### Tests

- real portal certification fixture or captured-response replay;
- browser-justified vs browser-waste memory learning;
- policy block on login-like or non-public URLs;
- route-denied sources never escalate.

## Safe implementation order

1. `P2-01` Hypothesis Backbone
2. `P2-02` State-Native Discovery
3. `P2-03` Library-Demoted Intake
4. `P2-04A` Browser Operational Certification
5. `P2-04B` Browser Lane Generalization only if still needed

This order matters because browser automation should remain subordinate to planner quality.

## What should not be touched first

Do not destabilize these modules in the first pass:

- `motor_018`
- `motor_036`
- `motor_052`
- `motor_053`
- `motor_054`

They already encode the anti-hallucination and report-integrity victories that the prompt required.

## Closure rule

Now that `P2-01` through `P2-04A` are complete, it is reasonable to claim:

- `100% behavior closure`
- `100% architectural closure under governed dynamic planning`

`P2-04B` was always capability expansion, not mandatory prompt closure, and the later `P2-07` expansion now closed that optional lane as well.
