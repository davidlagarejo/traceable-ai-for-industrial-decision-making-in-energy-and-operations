# Dynamic Congruence Prompt Compliance Audit — Latest

Produced at: 2026-05-03

## Purpose

This audit evaluates whether the long-form `Dynamic Congruence Intelligence System` prompt was truly satisfied.

It separates three different questions:

1. did the framework close the prompt behaviorally;
2. did it preserve the non-negotiable anti-hallucination and report-integrity rules;
3. did it implement the prompt with the same architectural depth originally requested.

This distinction matters because the current runtime is functionally strong, but parts of the dynamic layer are still implemented through governed family libraries and compositional heuristics rather than through a fully state-driven dynamic search brain.

## Executive verdict

### Behavioral verdict

Behaviorally, the prompt is substantially implemented.

The runtime now does all of the following:

- blocks stale charts and foreign case artifacts;
- blocks mismatched claim counts;
- downgrades declared input;
- replaces empty critical sections with explicit explanatory fallbacks;
- builds search, stop, intake, hypothesis, peer, loss, correlation, finance, TAD and gold-nugget surfaces;
- keeps those surfaces under claim governance and validator control;
- passes the current certification and regression bundles;
- passes the warehouse/logistics acceptance bundle and the current full suite truth of `490 passed, 15 warnings`.

### Architectural verdict

Architecturally, the prompt is materially fulfilled under a governed dynamic-planner design.

The framework does not behave as a fully open-ended autonomous planner.
It behaves as a governed family-aware dynamic system whose decisions are mediated by explicit libraries, state composition, and validator-bounded reasoning surfaces.

That is now an implementation choice, not an open closure blocker for this prompt.

## What is already solid and should not be rewritten

These areas are already aligned with the prompt and should be preserved:

- artifact consistency and case-isolation firewall;
- claim-count consistency blocking;
- declared-input evidence downgrading;
- empty-section replacement policy;
- bounded stop / downgrade / escalate surfaces;
- fair-comparison invalidity enforcement;
- loss-pattern anti-hallucination framing;
- financial exposure boundedness;
- expanded TAD;
- gold nugget governance;
- hard validator authority in `motor_036`.

Those lanes are not the right place for a rewrite.

## Findings

### 1. High — discovery is still family-template driven rather than full-state driven

Relevant code:

- [discovery_planner.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py:359)
- [motor_028.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py:1110)

Current reality:

- `build_discovery_need_register()` receives `target_definition`, `coverage_gaps`, `requestable_evidence_items`, `attempts`, and budget.
- It derives family from `target_type` and then selects from `_GENERIC_DISCOVERY_NEEDS + _FAMILY_DISCOVERY_NEEDS`.
- activation is based on gap intersection plus support-token overlap in requestable evidence and attempt text.

What is still missing relative to the prompt:

- jurisdiction-specific discovery mutation;
- active hypothesis input;
- comparison blocker input;
- regulatory trigger input;
- loss-pattern trigger input;
- source-failure-aware reranking.

Practical consequence:

The discovery surface is dynamic in activation, but not yet fully dynamic in reasoning basis.
It is still a governed family-template planner, not a case-state planner.

### 2. Closed — next-best-search now reranks source families dynamically

Relevant code:

- [next_best_search.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py:55)

Current reality:

- `build_next_best_search_register()` now emits a per-need `family_rank_register`.
- selected families are reranked by jurisdiction fit, discriminative value, source-yield memory, acquisition memory, regulatory relevance, comparison unlock value, and budget fit.

Current consequence:

This earlier gap is closed for the governed runtime path.

### 3. Closed — fair peer logic now requires affirmative evidence surfaces

Relevant code:

- [peer_set_builder.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_set_builder.py:35)

Current reality:

- peer requirements now expose `evidence_basis`, `bounded_by`, `why_still_unbounded`, and `peer_requirement_evidence_state`.
- boundedness now depends on affirmative evidence surfaces instead of question absence.

Current consequence:

This earlier comparability-risk gap is closed for the governed runtime path.

### 4. Medium — dynamic intake is still a governed question library, not a state-composed generator

Relevant code:

- [dynamic_intake.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py:438)
- [motor_049.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py:352)

Current reality:

- the question generator selects from `_QUESTION_LIBRARY` plus generic pack fallbacks;
- triggering depends on active need IDs and unresolved pack states;
- the result is useful and discriminating, but still library-centered.

What is still missing relative to the prompt:

- direct use of dominant hypothesis;
- direct use of decision type;
- direct use of active loss-pattern register;
- direct use of peer blocker state;
- direct use of financial exposure priority.

Practical consequence:

The system asks good questions, but the question composer is not yet truly driven by the full downstream state of the case.

### 5. Medium — hypothesis-driven ingestion remains downstream of the governed question layer

Relevant code:

- [hypothesis_ingestion.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py:68)

Current reality:

- rival hypotheses are pulled from the question rows;
- evidence needed is derived from stop-condition rows;
- blocked claims now default to structured question metadata, with legacy string fallback preserved only for compatibility.

What is still missing relative to the prompt:

- explicit independent rival-hypothesis generation;
- evidence ranking across competing hypotheses;
- a first-class hypothesis object independent of the governed intake library.

Practical consequence:

The hypothesis layer is operationally useful, but it is still downstream of the question library instead of being a first-class reasoning object.

### 6. Closed — the intake cap is now explicit and auditable

Relevant code:

- [dynamic_intake.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py:475)

Current reality:

- `build_dynamic_intake_question_register()` now emits scored questions plus `truncation_reason` and `questions_dropped_due_to_cap`.
- `build_truncated_question_register()` preserves dropped rows explicitly for auditability.

Current consequence:

This earlier silent-cap gap is closed.

## What this means overall

The prompt is closed at behavior level and at the acceptance level used by the governed runtime.

The only meaningful residual is optional state-composition depth beyond the current governed family libraries.

## Surgical implementation plan

The correct next step is not a rewrite.
The correct next step is to enrich the existing contracts while preserving validator sovereignty.

### Preserve

Do not destabilize these modules:

- `motor_034`
- `motor_036`
- `motor_047`
- `motor_048`
- `motor_052`
- `motor_053`
- `motor_054`

Their behavior already encodes the boundedness rules that the prompt wanted.

### Modify first

#### 1. `motor_028` + `discovery_planner.py`

Add a new structured dynamic state input to discovery planning.

Suggested new input object:

- `dynamic_case_state`

Suggested fields:

- `asset_family`
- `jurisdiction_scope`
- `industry_context`
- `coverage_gap_types`
- `coverage_gap_severities`
- `active_comparison_blockers`
- `active_regulatory_triggers`
- `active_loss_pattern_candidates`
- `active_rival_hypotheses`
- `source_family_failures`
- `source_family_successes`
- `requestable_evidence_items`
- `budget_state`

Do not remove existing discovery outputs.
Extend the scoring basis.

#### 2. `next_best_search.py`

Keep the existing output schema, but replace first-family selection with scored family ranking.

Suggested scoring inputs per family:

- jurisdiction fit;
- prior success/failure in this case;
- evidence discriminative value;
- public-vs-operator likelihood;
- hypothesis relevance;
- comparison relevance;
- regulatory relevance.

Add optional fields:

- `selected_search_family_reason`
- `family_rank_register`

#### 3. `motor_049` + `dynamic_intake.py`

Keep the question library as governed priors, but stop treating it as the final composer.

Add new optional inputs:

- `dominant_hypothesis_register`
- `activated_pattern_register`
- `comparison_blocker_register`
- `financial_exposure_priority_register`
- `decision_context`

Then score question specs by:

- hypothesis discrimination value;
- claim-blocking impact;
- comparison unlock value;
- loss-pattern falsification value;
- tariff / control-boundary consequence.

If the cap stays at `8`, emit an explicit `truncated_question_register` with reasons.

#### 4. `hypothesis_ingestion.py`

Replace substring-based blocked-claim logic with structured mappings carried in each question spec.

Each intake question should explicitly carry:

- `blocked_claims_if_missing`
- `supports_hypotheses`
- `falsifies_hypotheses`
- `comparison_requirements_unlocked`

This reduces fragility when new questions are added.

#### 5. `peer_set_builder.py`

Stop inferring boundedness from question absence.

Instead, derive each peer requirement state from affirmative evidence surfaces such as:

- source-backed subtype evidence;
- pack evidence states;
- local binding states;
- explicit confirmation states;
- control-boundary evidence register;
- schedule / throughput evidence register.

Add:

- `evidence_basis`
- `bounded_by`
- `why_still_unbounded`

for every peer requirement row.

## Tests to add before touching behavior

### Discovery

- TX warehouse and NYC warehouse should not surface identical family ordering when jurisdiction-specific public routes differ.
- repeated failure of one source family should rerank the next candidate family.
- active tariff hypothesis should push tariff-relevant discovery families upward.

### Intake

- active loss-pattern candidate should elevate its discriminating question even when it was not top-ranked before.
- decision type changes should alter priority order without changing question integrity.
- when more than `8` questions are triggered, truncated questions must be explicit and auditable.

### Hypothesis

- renaming a question ID must not silently weaken blocked-claim governance.
- structured blocked-claim maps must survive new question families.

### Peer fairness

- absent question should not auto-upgrade requirement to `bounded`.
- explicit evidence removal should keep comparison blocked even if the question library did not trigger.

## Recommended implementation order

1. preserve the current governed planner contracts
2. treat further work as optional depth enrichment, not prompt-blocking closure work
3. rerun acceptance / certification only when runtime logic changes again

## Final interpretation

If the question is:

“Did we close the prompt enough for the framework to behave as a dynamic congruence system?”

the answer is yes.

If the question is:

“Did we implement the prompt in the most open-ended architecturally maximal way possible?”

the answer is still no.

The framework is already congruent enough to preserve.
Any next work should be optional enrichment of state composition depth, not a redesign from zero.
