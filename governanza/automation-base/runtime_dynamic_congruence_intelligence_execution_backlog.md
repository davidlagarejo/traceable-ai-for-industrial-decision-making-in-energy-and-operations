# Runtime Dynamic Congruence Intelligence Execution Backlog

Produced at: 2026-05-01

Current execution state:

- `DCI-01` through `DCI-20`: `implemented`
- closure references:
  - [dynamic_congruence_intelligence_multicase_certification_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_intelligence_multicase_certification_latest.md>)
  - [dynamic_congruence_intelligence_multicase_certification_latest.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/dynamic_congruence_intelligence_multicase_certification_latest.json>)

Parent references:

- [runtime_congruence_intelligence_master_plan.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_congruence_intelligence_master_plan.md>)
- [runtime_congruence_intelligence_execution_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_congruence_intelligence_execution_backlog.md>)
- [runtime_congruence_intelligence_100_percent_closure_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_congruence_intelligence_100_percent_closure_backlog.md>)
- [industrial_asset_congruence_prompt_closure_matrix.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/industrial_asset_congruence_prompt_closure_matrix.md>)

## Purpose

This backlog applies the new `Dynamic Congruence Intelligence System` prompt to the existing runtime without destabilizing the current framework.

This is not a greenfield redesign.

It is a controlled migration from:

- `research routing + intake normalization + congruence analysis`

to:

- `dynamic evidence-seeking orchestration + hypothesis discrimination + bounded search + strategic output governance`

The goal is to add:

- dynamic source discovery
- dynamic intake generation
- next-best-search logic
- stop-condition logic
- fair peer set construction
- stronger loss activation
- stronger financial exposure typing
- empty-section replacement logic
- harder artifact and claim consistency

without weakening:

- thesis sovereignty
- body compression
- validator authority
- claim governance
- case isolation

## Core Application Rule

Do not implement this prompt as 15 independent new adapters.

The correct runtime ownership is:

- `motor_028`: dynamic public discovery execution
- `motor_049`: dynamic evidence / gap / intake orchestration
- `motor_051` to `motor_054`: peer / loss / correlation / finance / TAD intelligence
- `motor_016`: final section and appendix materialization
- `motor_018`: chart generation only
- `motor_036`: final integrity and admissibility gate

Most of the new work belongs in:

- [congruence_intelligence](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence>)

not in new report-facing adapters.

## Do-Not-Break List

Before executing any ticket, preserve these authorities:

- [motor_047.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py): thesis sovereignty
- [motor_048.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py): body compression sovereignty
- [motor_017.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py): renderer only, not business logic
- [motor_036.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py): hard validator
- [claim_governor.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/claim_governor.py): no weakening of claim restrictions

Do not reintroduce:

- report sprawl
- generic benchmark closure
- public-guidance-as-local-truth
- hardware-first reflex
- static all-fields intake
- contaminated charts or support packages

## Risk Order

Execution must follow this order:

1. identity, contamination and search-budget safety
2. declared-input governance
3. dynamic discovery and next-best-search
4. dynamic intake and hypothesis discrimination
5. fair peer construction
6. loss / correlation / finance expansion
7. TAD / gold nugget expansion
8. empty-section and packaging policy
9. multicase certification refresh

Do not jump ahead.

## Ticket Format

Each ticket specifies:

- purpose
- owner
- main files
- new runtime objects
- changes required
- dependencies
- acceptance criteria
- tests
- do-not-break notes

---

## Wave 0 — Safety Envelope

### `DCI-01` Case Identity And Entity Resolution Firewall

Purpose:

- make sure dynamic discovery does not degrade asset identity, site boundary or case purity

Owner:

- new `congruence_intelligence/entity_resolution.py`
- `motor_028.py`
- `motor_049.py`
- `motor_036.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/entity_resolution.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/research_router.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`

New runtime objects:

- `entity_resolution_register`
- `asset_boundary_resolution_register`
- `owner_operator_tenant_resolution_register`
- `entity_conflict_register`
- `case_fingerprint`

Changes required:

- resolve whether each source row belongs to:
  - the asset
  - a campus
  - a portfolio
  - an owner only
  - a tenant only
  - an operator only
- distinguish:
  - asset identity
  - control boundary
  - economic boundary
- prevent a source from upgrading the case if the source entity is not resolved

Dependencies:

- none

Acceptance criteria:

- a listing, permit, assessor record and operator page can be attached to the same asset only if the entity register says they cohere
- unresolved entity conflict downgrades claims and blocks peer construction
- warehouse, cold-chain and infrastructure seeds do not cross-resolve to the wrong object

Tests:

- `test_entity_resolution_boundary_engine.py`
- `test_entity_resolution_negative_cross_asset.py`

Do-not-break:

- do not change report mode logic yet
- do not let unresolved sources silently pass into thesis

---

### `DCI-02` Case Isolation And Contamination Firewall

Purpose:

- prevent charts, source rows, captions, appendix assets and peer artifacts from leaking across runs

Owner:

- new `congruence_intelligence/case_isolation.py`
- `motor_016.py`
- `motor_018.py`
- `motor_036.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/case_isolation.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`

New runtime objects:

- `case_namespace_register`
- `cross_case_contamination_scan`
- `artifact_case_match_register`
- `foreign_entity_label_register`

Changes required:

- stamp support objects with:
  - `case_fingerprint`
  - `asset_id`
  - `asset_name`
  - `jurisdiction_hint`
- scan:
  - charts
  - captions
  - appendix tables
  - support text
  - promoted chart bundles

Dependencies:

- `DCI-01`

Acceptance criteria:

- any foreign label, stale chart or wrong asset reference blocks final packaging
- appendix-visible charts obey the same isolation rule as body charts

Tests:

- `test_case_isolation_firewall.py`
- `test_artifact_foreign_entity_block.py`

Do-not-break:

- do not move chart logic into `motor_017`
- keep `motor_036` as the final blocker

---

### `DCI-03` Search Budget And Evidence Attempt Ledger

Purpose:

- stop dynamic search from becoming uncontrolled recursion

Owner:

- new `congruence_intelligence/search_budget.py`
- new `congruence_intelligence/evidence_attempts.py`
- `motor_028.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/search_budget.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/evidence_attempts.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

New runtime objects:

- `search_budget_register`
- `search_attempt_ledger`
- `search_attempt_outcome_register`
- `search_exhaustion_register`

Changes required:

- define budget classes by:
  - asset family
  - report mode
  - active hypothesis count
  - blocker severity
- ledger each attempt with:
  - purpose
  - source family
  - query family
  - attempt outcome
  - evidence gained
  - blocker removed or not removed

Dependencies:

- `DCI-01`
- `DCI-02`

Acceptance criteria:

- every search wave can say what was attempted and why it stopped
- the system never keeps asking for more evidence without recording search exhaustion or escalation to intake

Tests:

- `test_search_budget_governor.py`
- `test_evidence_attempt_ledger.py`

Do-not-break:

- do not remove existing source contracts; govern them

---

### `DCI-04` Declared Input Evidence Downgrader

Purpose:

- stop declared input from masquerading as verified asset evidence

Owner:

- new `congruence_intelligence/declared_input_governor.py`
- `motor_012.py`
- `motor_034.py`
- `motor_049.py`
- `motor_036.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/declared_input_governor.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`

New runtime objects:

- `declared_input_downgrade_register`
- `evidence_confirmation_state_register`

Required states:

- `DECLARED_BY_USER`
- `PUBLICLY_CONFIRMED`
- `AUTHORITY_CONFIRMED`
- `OPERATOR_CONFIRMED`
- `FIELD_VERIFIED`

Changes required:

- add confirmation sidecar to:
  - address
  - asset type
  - year built
  - GFA
  - owner
  - operator
  - primary process clues
- make downstream engines read confirmation state before upgrading claims

Dependencies:

- `DCI-01`

Acceptance criteria:

- declared input alone cannot unlock:
  - peer validity
  - control-boundary claims
  - subtype certainty
  - tariff or maintenance conclusions

Tests:

- `test_declared_input_downgrader.py`

Do-not-break:

- do not rewrite base subject admissibility logic; augment it

---

## Wave 1 — Dynamic Discovery

### `DCI-05` Dynamic Source Discovery Planner

Purpose:

- replace fixed query routing with governed discovery needs tied to family, jurisdiction, gaps and hypotheses

Owner:

- new `congruence_intelligence/discovery_planner.py`
- `research_router.py`
- `research_library.py`
- `motor_028.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/discovery_planner.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/research_router.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/research_library.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`

New runtime objects:

- `discovery_need_register`
- `search_family_execution_plan`
- `accepted_evidence_type_register`
- `discovery_stop_condition_register`

Changes required:

- discovery planner must generate needs from:
  - asset family
  - jurisdiction
  - active evidence gaps
  - active hypotheses
  - comparison blockers
  - regulatory triggers
  - loss pattern triggers
- each need must specify:
  - why it exists
  - search families to explore
  - accepted evidence types
  - stop condition

Dependencies:

- `DCI-01`
- `DCI-03`

Acceptance criteria:

- warehouse case explicitly searches subtype, docks, dry vs cold-chain, operator/tenant, utility territory, brochure/listing, zoning/parcel clues and refrigeration clues
- manufacturing case explicitly searches permits, process clues, thermal systems, utility mix and throughput proxies

Tests:

- `test_dynamic_source_discovery_engine.py`

Do-not-break:

- keep the current baseline source contract as fallback when dynamic planner is disabled

---

### `DCI-06` Next Best Search Engine

Purpose:

- convert unresolved gaps into a prioritized next-search queue instead of static missing-data lists

Owner:

- new `congruence_intelligence/next_best_search.py`
- `motor_028.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/next_best_search.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

New runtime objects:

- `next_best_search_register`
- `search_target_priority_register`
- `search_success_effect_register`
- `search_failure_effect_register`

Changes required:

- prioritize next search targets using:
  - blocker severity
  - hypothesis leverage
  - public-source likelihood
  - remaining budget
  - report mode
- produce `if found` and `if not found` consequences

Dependencies:

- `DCI-03`
- `DCI-05`

Acceptance criteria:

- every critical gap produces a next-search target with:
  - why
  - search family
  - expected evidence
  - downgrade/escalation logic

Tests:

- `test_next_best_search_engine.py`

Do-not-break:

- do not let this engine directly modify thesis or report mode

---

### `DCI-07` Stop Condition Engine

Purpose:

- give every discovery path and intake path a clean stopping rule

Owner:

- new `congruence_intelligence/stop_conditions.py`
- `motor_028.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/stop_conditions.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

New runtime objects:

- `stop_condition_register`
- `downgrade_condition_register`
- `escalation_condition_register`
- `minimum_sufficient_evidence_register`

Changes required:

- encode for each search and intake need:
  - purpose
  - minimum sufficient evidence
  - stop condition
  - downgrade condition
  - escalation condition

Dependencies:

- `DCI-03`
- `DCI-05`
- `DCI-06`

Acceptance criteria:

- the system can explain when to stop searching and when to ask the operator
- no repeated “need more data” loops without a stop or escalation state

Tests:

- `test_stop_condition_engine.py`

Do-not-break:

- do not let search continue once budget and stop condition are both exhausted

---

### `DCI-08` Source Authority And Conflict Engine

Purpose:

- resolve conflicting public and local sources without flattening them into a single truth score

Owner:

- new `congruence_intelligence/source_authority_conflicts.py`
- `source_hierarchy.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/source_authority_conflicts.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/source_hierarchy.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

New runtime objects:

- `source_conflict_register`
- `authority_precedence_register`
- `conflict_resolution_outcome_register`

Changes required:

- rank conflicts between:
  - assessor vs broker listing
  - permit vs brochure
  - operator statement vs public listing
  - tariff text vs rate summary
- make downstream claims read conflict state before upgrading certainty

Dependencies:

- `DCI-01`
- `DCI-05`

Acceptance criteria:

- conflicting source evidence is surfaced explicitly, not silently averaged
- peer and subtype claims downgrade when high-authority conflicts remain unresolved

Tests:

- `test_source_authority_conflict_engine.py`

Do-not-break:

- do not allow lower-tier brochure text to override authority-confirmed evidence

---

## Wave 2 — Dynamic Intake And Hypothesis Discrimination

### `DCI-09` Dynamic Intake Generator

Purpose:

- generate live intake questions from active gaps and hypotheses instead of using static forms as final logic

Owner:

- new `congruence_intelligence/dynamic_intake.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/dynamic_intake.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/schemas.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

New runtime objects:

- `dynamic_intake_question_register`
- `required_from_register`
- `intake_priority_register`

Changes required:

- questions must be generated from:
  - asset family
  - active hypothesis
  - evidence missing after public search
  - peer requirement blockers
  - loss pattern triggers
- each question must specify:
  - trigger
  - why needed
  - hypothesis discriminated
  - required from
  - priority

Dependencies:

- `DCI-05`
- `DCI-06`
- `DCI-07`

Acceptance criteria:

- warehouse case produces critical questions on:
  - MHE charging
  - dock count / dock cycles
  - dry vs cold-chain
  - operating hours
  - control boundary
- manufacturing case produces critical questions on:
  - compressed air use
  - steam or thermal duty
  - throughput / product mix
  - maintenance ownership

Tests:

- `test_dynamic_intake_generator.py`

Do-not-break:

- do not reintroduce giant static questionnaires

---

### `DCI-10` Hypothesis-Driven Ingestion Engine

Purpose:

- make every requested datum justify itself against rival hypotheses

Owner:

- new `congruence_intelligence/hypothesis_ingestion.py`
- `motor_049.py`
- `motor_051.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hypothesis_ingestion.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

New runtime objects:

- `rival_hypothesis_register`
- `hypothesis_discrimination_register`
- `claim_impact_register`

Changes required:

- create rival hypotheses before asking for more data
- tie every evidence request to:
  - public search first
  - intake if missing
  - claim impact if still missing

Dependencies:

- `DCI-06`
- `DCI-09`

Acceptance criteria:

- system can state:
  - rival hypotheses
  - evidence needed to separate them
  - what public search was attempted
  - what intake is now required
  - what claim stays prohibited meanwhile

Tests:

- `test_hypothesis_driven_ingestion.py`

Do-not-break:

- do not let missing data silently degrade into generic recommendations

---

### `DCI-11` Gap Taxonomy And Evidence Need Classification

Purpose:

- distinguish why the system is blocked, not just that it is blocked

Owner:

- new `congruence_intelligence/gap_taxonomy.py`
- `motor_049.py`
- `motor_051.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/gap_taxonomy.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

New runtime objects:

- `gap_taxonomy_register`
- `evidence_need_class_register`

Mandatory gap classes:

- `missing_data`
- `missing_comparability`
- `missing_operational_context`
- `missing_control_evidence`
- `missing_tariff_evidence`
- `missing_maintenance_proof`
- `missing_identity_resolution`

Dependencies:

- `DCI-09`
- `DCI-10`

Acceptance criteria:

- every blocker can be classified into a gap class
- downstream TAD can say whether the next action is search, intake, comparison-building or claim prohibition

Tests:

- `test_gap_taxonomy_engine.py`

Do-not-break:

- do not collapse all blockers into `insufficient evidence`

---

## Wave 3 — Fair Comparison And Operational Intelligence

### `DCI-12` Fair Peer Set Builder

Purpose:

- construct comparison requirements and candidate peer logic instead of only comparison invalidity warnings

Owner:

- new `congruence_intelligence/peer_set_builder.py`
- `fair_comparison.py`
- `peer_normalization.py`
- `motor_051.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_set_builder.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/fair_comparison.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_normalization.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

New runtime objects:

- `peer_requirement_register`
- `peer_candidate_family_register`
- `comparison_blocker_register`
- `comparison_not_yet_valid_register`

Changes required:

- encode family-specific comparison requirements for:
  - warehouse / cold-chain
  - building
  - manufacturing
  - utility-heavy
  - infrastructure

Dependencies:

- `DCI-01`
- `DCI-11`

Acceptance criteria:

- if a valid peer set cannot be built:
  - superiority claims are prohibited
  - comparison requirements are still produced
  - empty peer section is replaced with explanation

Tests:

- `test_fair_peer_set_builder.py`

Do-not-break:

- no generic CBECS or ENERGY STAR benchmark may become local truth

---

### `DCI-13` Loss Pattern Activator Expansion

Purpose:

- activate asset-family-specific loss patterns with confirm/falsify logic, not generic plausibility only

Owner:

- `loss_patterns.py`
- `motor_052.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/loss_patterns.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py`

New runtime objects:

- `activated_pattern_register`
- `pattern_discrimination_register`

Changes required:

- expand pattern families for:
  - warehouse / distribution
  - cold-chain
  - manufacturing
  - commercial building
  - utility-heavy
- require:
  - applicability
  - evidence state
  - why plausible
  - what confirms
  - what falsifies
  - TAD action

Dependencies:

- `DCI-10`
- `DCI-12`

Acceptance criteria:

- warehouse case activates at least the relevant subset of:
  - dock infiltration
  - high-bay lighting waste
  - rooftop HVAC degradation
  - charging peak demand
  - poor submetering
  - schedule waste
  - door discipline
- no pattern is stated as fact without confirming evidence

Tests:

- `test_loss_pattern_activator.py`

Do-not-break:

- preserve anti-hallucination wording

---

### `DCI-14` Structural Correlation Graph Expansion

Purpose:

- build a network of correlations across physics, operations, finance, maintenance, tariff and control instead of one contradiction only

Owner:

- `correlation_engine.py`
- `congruence_engine.py`
- `motor_051.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/correlation_engine.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/congruence_engine.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

New runtime objects:

- `structural_correlation_graph`
- `correlation_priority_register`
- `gold_nugget_candidate_register`

Changes required:

- encode correlations across:
  - physics
  - logistics
  - maintenance
  - finance
  - permits
  - tariff
  - climate
  - regulation
  - culture

Dependencies:

- `DCI-10`
- `DCI-13`

Acceptance criteria:

- system can produce multiple correlations with:
  - strategic meaning
  - evidence needed
  - possible gold nugget

Tests:

- `test_structural_correlation_graph_engine.py`

Do-not-break:

- keep current dominant contradiction logic; enrich it rather than replace it

---

### `DCI-15` Financial Exposure Type Engine Expansion

Purpose:

- translate strategic risk into typed financial exposure, not generic “capital may be misallocated” language

Owner:

- `finance_to_physics.py`
- `motor_053.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/finance_to_physics.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py`

New runtime objects:

- `financial_exposure_type_register`
- `underwriting_misread_register`
- `value_leakage_register`

Required exposure types:

- `CAPEX_misallocated`
- `operational_savings_not_capturable`
- `tariff_exposure_hidden`
- `demand_charge_exposure`
- `maintenance_downtime_exposure`
- `compliance_exposure_misunderstood`
- `tenant_operator_value_leakage`
- `over_modeling_cost`
- `under_instrumentation_risk`
- `wrong_peer_valuation`
- `wrong_retrofit_sequencing`

Dependencies:

- `DCI-12`
- `DCI-14`

Acceptance criteria:

- each exposure type has:
  - trigger
  - why it matters
  - evidence needed
  - TAD consequence

Tests:

- `test_financial_exposure_type_engine.py`

Do-not-break:

- do not infer savings or ROI from exposure typing

---

## Wave 4 — Strategic Output And Composition

### `DCI-16` Expanded Strategic TAD Engine

Purpose:

- expand decision actions so the system can recommend the right strategic next move, not only a narrow trio of states

Owner:

- `strategic_tad.py`
- `motor_054.py`
- `motor_033.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/strategic_tad.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py`

New runtime objects:

- `expanded_tad_action_register`
- `prohibited_action_register`

Required actions:

- `ACT_NOW`
- `REQUEST_MINIMUM_EVIDENCE`
- `BUILD_FAIR_PEER_SET`
- `COMPARE_FAIRLY`
- `VALIDATE_LOSS_PATTERN`
- `VALIDATE_CONTROL_BOUNDARY`
- `VALIDATE_TARIFF_EXPOSURE`
- `VALIDATE_MAINTENANCE_REALITY`
- `DO_NOT_MODEL_YET`
- `DO_NOT_SENSOR_YET`
- `DO_NOT_INVEST_YET`
- `REDESIGN_HYPOTHESIS`
- `DEFER_ROI`
- `PROHIBIT_CLAIM`

Dependencies:

- `DCI-11`
- `DCI-15`

Acceptance criteria:

- TAD can explain:
  - trigger
  - why
  - evidence needed
  - prohibited action
- warehouse case expands beyond generic evidence request and can tell the user whether to build peer set, validate tariff exposure or stop modeling

Tests:

- `test_expanded_strategic_tad_engine.py`

Do-not-break:

- keep existing claim governance and inadmissibility blocks

---

### `DCI-17` Gold Nugget Generator Hardening

Purpose:

- produce 3 to 5 sharp case-specific strategic insights, not only a correct thesis

Owner:

- `gold_nuggets.py`
- `executive_thesis.py`
- `motor_047.py`
- `motor_054.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/gold_nuggets.py`
- `runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py`

New runtime objects:

- `gold_nugget_register`
- `gold_nugget_strength_register`

Changes required:

- nuggets must combine:
  - contradiction
  - loss pattern
  - financial exposure
  - fair comparison failure
  - minimum evidence
  - TAD

Dependencies:

- `DCI-14`
- `DCI-16`

Acceptance criteria:

- bounded exploratory warehouse case produces at least 3 strong non-generic insights
- nuggets must include evidence state and what to do next

Tests:

- `test_gold_nugget_generator.py`

Do-not-break:

- do not let gold nuggets bypass claim governor

---

### `DCI-18` Empty Section Policy Engine

Purpose:

- replace empty or dead sections with explicit explanatory fallbacks

Owner:

- new `congruence_intelligence/empty_section_policy.py`
- `report_compression.py`
- `motor_016.py`
- `motor_036.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/empty_section_policy.py`
- `runtime-orchestrator/src/runtime_orchestrator/report_compression.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`

New runtime objects:

- `empty_section_policy_register`
- `section_population_status_register`
- `section_explanation_fallback_register`

Dependencies:

- `DCI-12`
- `DCI-16`

Acceptance criteria:

- `Peer Comparison`, `Public Source Coverage` and similar sections never render as empty
- when blocked, the section explains:
  - why no rows exist
  - what was attempted
  - what is required
  - claim impact

Tests:

- `test_empty_section_policy_engine.py`

Do-not-break:

- do not reopen body sprawl to solve this

---

### `DCI-19` Artifact And Claim Consistency Hardening

Purpose:

- make final packaging fail closed if charts, counts, source families or report mode contradict the case

Owner:

- `motor_036.py`
- `motor_016.py`
- `motor_018.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py`

New validator checks:

- `chart_asset_case_match`
- `foreign_entity_label_block`
- `source_family_activation_match`
- `claim_summary_count_match`
- `section_nonempty_or_explained`
- `declared_input_not_overpromoted`
- `report_mode_consistency_match`

Dependencies:

- `DCI-02`
- `DCI-04`
- `DCI-18`

Acceptance criteria:

- mismatched claim counts block report generation
- foreign entity labels block report generation
- unactivated source families cannot appear in report artifacts
- empty critical sections without fallback block report generation

Tests:

- `test_artifact_consistency_validator.py`
- `test_claim_consistency_engine.py`

Do-not-break:

- keep validator as hard block, not warning-only

---

## Wave 5 — Certification And Rollout

### `DCI-20` Dynamic Congruence Multicase Certification And Prompt Closure Refresh

Purpose:

- certify the dynamic system end-to-end and refresh the closure artifacts honestly

Owner:

- governance artifacts under `governanza/automation-base/`
- focused runtime seeds under `runtime-orchestrator/inputs/`

Main files:

- `governanza/automation-base/industrial_asset_congruence_prompt_closure_matrix.md`
- `governanza/automation-base/congruence_intelligence_multicase_certification_latest.md`
- `governanza/automation-base/congruence_intelligence_multicase_certification_latest.json`
- new certification artifact:
  - `governanza/automation-base/dynamic_congruence_intelligence_multicase_certification_latest.md`
  - `governanza/automation-base/dynamic_congruence_intelligence_multicase_certification_latest.json`

Required certification cases:

- dry warehouse semistructured
- cold-chain semistructured
- office / commercial building with owner-tenant boundary
- manufacturing with compressed-air / thermal clues
- infrastructure node
- utility-heavy site
- declared-input-only negative case
- contaminated-chart negative case
- empty-peer-section negative case

Dependencies:

- `DCI-01` through `DCI-19`

Acceptance criteria:

- each critical prompt clause maps to:
  - runtime object
  - validator rule
  - certification case
- acceptance tests in the prompt are satisfied explicitly
- closure matrix states clearly what is:
  - implemented directly
  - implemented via governed compression
  - intentionally deferred

Tests:

- certification scripts and runtime reruns against the case set

Do-not-break:

- do not declare literal 100% unless the refreshed artifacts support it

Completion note:

- completed on `2026-05-02`
- refreshed:
  - `industrial_asset_congruence_prompt_closure_matrix.md`
  - `congruence_intelligence_multicase_certification_latest.md`
  - `congruence_intelligence_multicase_certification_latest.json`
  - `dynamic_congruence_intelligence_multicase_certification_latest.md`
  - `dynamic_congruence_intelligence_multicase_certification_latest.json`

---

## Cross-Ticket Module Ownership Map

Primary mutation zones:

- [motor_028.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py)
  - discovery execution
  - search budget
  - stop conditions
  - next-best-search

- [motor_049.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py)
  - gap taxonomy
  - dynamic intake
  - hypothesis ingestion
  - binding and escalation state

- [motor_051.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py)
  - peer construction
  - comparison validity
  - structural correlation enrichment

- [motor_052.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py)
  - loss pattern activation
  - maintenance-discriminated plausibility

- [motor_053.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py)
  - financial exposure typing
  - tariff / regulation / climate linkage

- [motor_054.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py)
  - expanded TAD
  - gold nugget consequence wiring

Secondary mutation zones:

- [motor_012.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py)
  - declared input provenance

- [motor_034.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py)
  - maturity and admissibility consequences

- [motor_016.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py)
  - empty-section materialization
  - appendix promotion
  - support artifact case safety

- [motor_018.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py)
  - chart metadata safety

- [motor_036.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py)
  - final block conditions

Protected zones:

- [motor_047.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py)
- [motor_048.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py)
- [motor_017.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py)

Only touch these after the runtime objects are stable and only for narrow bridges.

## Recommended Execution Sequence

Execute in this order:

1. `DCI-01`
2. `DCI-02`
3. `DCI-03`
4. `DCI-04`
5. `DCI-05`
6. `DCI-06`
7. `DCI-07`
8. `DCI-08`
9. `DCI-09`
10. `DCI-10`
11. `DCI-11`
12. `DCI-12`
13. `DCI-13`
14. `DCI-14`
15. `DCI-15`
16. `DCI-16`
17. `DCI-17`
18. `DCI-18`
19. `DCI-19`
20. `DCI-20`

## Definition Of Done

This backlog is complete only when:

- search is dynamic but bounded
- intake is dynamic but discriminative
- gaps are classified, not merely listed
- peer logic is constructive, not only prohibitive
- loss patterns are activated with falsification logic
- TAD explains what to do next and what not to do yet
- empty sections are replaced with explanatory fallbacks
- no artifact contamination survives to publication
- claim counts and claim matrices always match
- declared input never passes as verified evidence
- certification shows the system knows what it needs to know next
