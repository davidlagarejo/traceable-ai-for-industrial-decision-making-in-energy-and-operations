# Runtime Executive Thesis & Report Hierarchy Correction Plan

Generated on: `2026-04-30`

## Objective

Correct the current ZLab reporting system so it stops behaving like:

`many motors -> many sections -> final PDF`

and starts behaving like:

`many motors -> executive synthesis / thesis -> compression / hierarchy -> client-facing report -> appendices -> final consistency validation -> render`

This plan is not about style.
It is about narrative sovereignty, section authority, compression discipline, client-facing product quality, and validator hardening.

---

## Current Honest Diagnosis

The framework already contains most of the right analytical primitives:

- screening admissibility
- canonical problem frame
- system abstraction
- dominant variables
- cross-layer contradictions
- scenario space
- financial exposure under uncertainty
- peer comparison
- conditional redesign
- minimum evidence for discrimination
- structural TAD
- claim permissions
- source traceability

But the system still has one major architectural flaw:

- the main report is still assembled primarily in `motor_016` from many upstream registers
- there is no sovereign `executive_thesis` object
- there is no sovereign compression layer
- validator strength is high on logic, but still too shallow on narrative hierarchy and client-facing product quality

So the report still feels partly like:

- “all engines wrote their section”

instead of:

- “all engines fed one thesis, and only the most decision-relevant material survived into the main body”

---

## Non-Negotiables

Do **not** weaken:

- no fake ROI
- no fake savings
- no compliance closure without evidence
- no benchmark as local truth
- no peer superiority without evidence
- no final redesign recommendation without implementation-grade evidence
- no digital twin before dominant variables are bounded
- no generic template output
- no claim without evidence state
- no TAD action disconnected from evidence or claim permission
- no structural-first narrative that outruns claim permissions

---

## Pipeline Ownership Table

| Section | Current Motor / Module | Key Input Objects | Current Output Object | Rendered Where Today |
|---|---|---|---|---|
| Executive Structural Brief | `motor_016` | `canonical_problem_frame`, structural registers, claims, governance | section body | main body |
| Problem Reframe | `motor_041` -> `motor_016` | `problem_framing_register` | rendered section | main body |
| System Abstraction Map | `motor_037` -> `motor_016` | `system_abstraction` | rendered section | main body |
| Dominant Variables | `motor_038` -> `motor_016` | `dominant_variable_register` | rendered section | main body |
| Evidence State by Layer | `motor_045` -> `motor_016` | `evidence_state_by_layer_register` | rendered section | main body / appendix by mode |
| Cross-Layer Contradictions | `motor_040` -> `motor_016` | `cross_layer_conflict_register` | rendered section | main body |
| Scenario Space | `motor_014` + `motor_016` | legacy scenario outputs + structural scenario surfaces | rendered section | main body |
| Financial Exposure Under Uncertainty | `motor_045` -> `motor_016` | `financial_exposure_register` | rendered section | main body |
| Peer / Competitive Comparison | `motor_043` -> `motor_016` | `peer_comparison_register` | rendered section | main body |
| Conditional Redesign | `motor_044` -> `motor_016` | `conditional_redesign_register` | rendered section | main body |
| Minimum Evidence for Discrimination | `motor_046` -> `motor_016` | `minimum_evidence_for_discrimination_register` | rendered section | main body |
| TAD — Action Priority | `motor_033` -> `motor_016` | `expanded_structural_tad_action_register`, `tad_preliminary` | rendered section | main body |
| Claim Permissions / What Not To Do | `motor_034` + `motor_016` | `claim_permission_register`, `claim_contract_register` | rendered section | main body / appendix |
| Legacy Inference Case Map | legacy path in `motor_016` | inference objects from `motor_013/014` | rendered section | appendix / legacy surfaces |
| Validation Architecture | legacy path in `motor_016` | validation and evidence agenda objects | rendered section | appendix / legacy surfaces |
| Governance Status | `motor_036`, `motor_027`, `motor_016` | consistency register, governance summary | rendered section | body + appendix |
| Appendices | `motor_016` | multiple upstream registers | appendix map | appendices |

---

## Narrative Authority Audit

| Narrative Authority | Current Role | Desired Role | Current Problem |
|---|---|---|---|
| Structural Intelligence Lane | strongest content source but not sovereign narrator | sovereign narrator of the client-facing report | still shares authority with legacy decision and assembly logic |
| Decision Core | still a visible co-narrator | technical support and appendix input | can still compete with the structural thesis |
| TAD Engine | partly action layer, partly explainer | action layer subordinated to one thesis | client-facing TAD can still inherit too much legacy detail |
| Validation Architecture | still visible explanatory surface | appendix / support | dilutes executive force |
| Claim Permission Engine | narrative guardrail plus content source | guardrail and bounded support | useful, but should not narrate the main thesis |
| Reporting Engine (`motor_016`) | de facto narrative arbiter | renderer of a prior thesis and outline | still decides too much of the report story locally |

### Required authority rule

The client-facing report must be governed by:

1. `Executive Synthesis / Thesis Engine`
2. `Report Compression Engine`
3. `System Consistency Validator`

Not directly by raw plurality of upstream motors.

---

## Legacy vs New Section Conflict Audit

| Legacy Section | Duplicates Which New Section | Keep / Move to Appendix / Remove | Reason |
|---|---|---|---|
| Blocking Conflicts | Cross-Layer Contradictions | Move to appendix | the structural contradiction model is now superior |
| Validation Architecture | Minimum Evidence / TAD / Claim Permissions | Move to appendix | technical support, not thesis |
| Inference Case Map | Scenario Space | Move to appendix | pipeline-facing, not executive-facing |
| Tension Map | Cross-Layer Contradictions / Problem Framing | Move to appendix | conceptual duplication |
| Conditional Opportunities | Conditional Redesign | Summarize or move to appendix | redesign engine should own that logic |
| Evidence & Source Traceability | Source Traceability | Keep as appendix | necessary but not body-dominant |
| Asset Context Prior | System Abstraction / Evidence State by Layer | Move to appendix | historical trace, not client thesis |

---

## Target Architecture

### Correct high-level flow

`all_motor_outputs`
`-> executive thesis synthesis`
`-> narrative compression / hierarchy`
`-> client-facing outline`
`-> technical appendix map`
`-> final validator`
`-> render`

### New engines required

1. `motor_047` — Executive Synthesis / Thesis Engine
2. `motor_048` — Report Compression Engine

### Existing engines to extend

3. `motor_016` — render from `executive_thesis` and `main_report_outline`, not directly from raw motor plurality
4. `motor_036` — add narrative, redundancy, peer, redesign, TAD, rendering-quality, and thesis-strength checks
5. `render_section_contract.py` — align report mode section policy with thesis/outline outputs
6. `motor_017` — render only approved main outline + appendix map

---

## P0 — Required For Product-Level Correction

## RHC-01 — Add Executive Synthesis / Thesis Engine

### Problem

There is no sovereign thesis object.
The nearest object today is `canonical_problem_frame`, but that is still a structural summary, not a client-facing thesis contract.

### Owner

- new `motor_047`

### Files

- new:
  - `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py`
  - `runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py`
- extend:
  - [adapters/__init__.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/__init__.py>)
  - [motor_dependencies.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_dependencies.json>)

### Inputs

- `problem_framing_register`
- `system_abstraction`
- `dominant_variable_register`
- `cross_layer_conflict_register`
- `scenario_register`
- `financial_exposure_register`
- `peer_comparison_register`
- `conditional_redesign_register`
- `minimum_evidence_for_discrimination_register`
- `expanded_structural_tad_action_register`
- `claim_permission_register`
- `evidence_maturity_register`
- `report_output_mode_classifier_table`
- `canonical_problem_frame`
- `claim_contract_register`

### Required outputs

`executive_thesis = {`
- `declared_problem`
- `reframed_problem`
- `dominant_contradiction`
- `why_it_matters`
- `dominant_risk`
- `what_is_admissible_now`
- `what_is_not_admissible`
- `minimum_discriminating_evidence`
- `conditional_redesign`
- `evidence_state`
- `report_mode`
- `confidence_level`
- `top_dominant_variables`
- `top_scenarios`
- `top_actions`
- `dominant_lens`
- `supporting_modes`
`}`

### Hard hierarchy rules

- max 1 reframed problem
- max 1 dominant contradiction
- max 3 dominant variables
- max 3 primary scenarios
- max 3 client-facing TAD actions
- max 1 primary redesign path
- max 1 minimum evidence pack

### Type

- `architecture`
- `logic`
- `integration`

### Done when

- `executive_thesis` exists as a first-class runtime object
- `One Vanderbilt` gets one thesis, one contradiction, one evidence discriminator, one bounded redesign path
- downstream report assembly can run from `executive_thesis` without re-deciding the thesis locally

### Tests to add

- `test_executive_thesis_contains_dominant_contradiction_reframed_problem_and_evidence_discriminator`
- `test_executive_thesis_limits_primary_lists_to_allowed_cardinality`
- `test_one_vanderbilt_executive_thesis_matches_regulation_vs_control_boundary_logic`

---

## RHC-02 — Add Report Compression Engine

### Problem

There is no sovereign semantic compression layer.
`render_section_contract.py` governs placement, not thesis-driven compression.

### Owner

- new `motor_048`

### Files

- new:
  - `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py`
  - `runtime-orchestrator/src/runtime_orchestrator/report_compression.py`
- extend:
  - [adapters/__init__.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/__init__.py>)
  - [motor_dependencies.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_dependencies.json>)

### Inputs

- `executive_thesis`
- `report_output_mode_classifier_table`
- `canonical_problem_frame`
- full section candidate map from `motor_016` helpers or a shared section registry
- legacy section inventory

### Required outputs

- `main_report_outline`
- `appendix_map`
- `section_authority_map`
- `deduplicated_claim_map`
- `client_facing_tad`
- `supporting_modes`

### Compression rules

- if an idea appears in multiple sections, it is fully stated once
- other sections reference it or move to appendix
- long registers default to appendix:
  - inference case map
  - full claim matrix
  - full source traceability
  - full maturity register
  - full validation question set
- each main section must answer:
  - what is the point
  - why does it matter
  - what evidence supports it
  - what action follows

### Type

- `architecture`
- `logic`
- `product`

### Done when

- `main_report_outline` exists as a first-class runtime object
- the body is capped to the intended client-facing section count
- legacy sections are formally demoted unless they add unique technical detail
- `client_facing_tad` is distinct from technical appendix TAD

### Tests to add

- `test_compression_engine_moves_legacy_sections_to_appendix_when_structural_equivalent_exists`
- `test_client_facing_tad_is_capped_to_five_actions`
- `test_main_report_outline_has_no_duplicate_primary_claims`

---

## RHC-03 — Re-anchor `motor_016` To Thesis + Outline

### Problem

`motor_016` still behaves as a partially sovereign narrative assembler.

### Owners

- `motor_016`
- `render_section_contract.py`

### Files

- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [render_section_contract.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/render_section_contract.py>)

### Required change

- `motor_016` must consume:
  - `executive_thesis`
  - `main_report_outline`
  - `appendix_map`
  - `client_facing_tad`
- it must stop deriving the thesis locally from many registers
- it must assemble:
  - body sections from `main_report_outline`
  - appendix sections from `appendix_map`
- it may still render raw registers, but only where the outline explicitly places them

### Type

- `integration`
- `flow`
- `rendering`

### Done when

- the main body can be fully explained from `executive_thesis` + `main_report_outline`
- legacy sections no longer appear in the body by default
- supporting modes are surfaced as supporting lenses, not co-equal main headings

### Tests to add

- `test_motor_016_renders_main_body_from_executive_thesis_outline_only`
- `test_supporting_modes_do_not_render_as_equal_primary_modes`

---

## RHC-04 — Upgrade `motor_036` Into Product-Quality Validator

### Problem

`motor_036` is already strong on structural and logical consistency, but still too weak on:

- narrative hierarchy
- redundancy
- peer quality
- redesign completeness
- TAD product discipline
- rendering-quality language
- structural thesis strength

### Owner

- `motor_036`

### Files

- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

### Required new check families

#### Logical consistency

- report type matches executive state
- claim permissions match governance summary
- maturity register matches operational identity
- screening admissible does not equal fully blocked
- public asset evidence not ignored

#### Narrative hierarchy

- one dominant thesis exists
- one dominant contradiction exists
- executive brief references it
- TAD references it
- financial exposure references it
- minimum evidence references it

#### Redundancy

- fail if same paragraph or claim appears in more than 2 main sections
- fail if legacy sections repeat new sections without extra technical detail

#### Client-facing quality

- truncated sentence
- placeholder
- empty field without explicit meaning
- internal motor language
- “this section is rendered”
- “LLM prose”
- “Use the chart”
- raw object names in client-facing body

#### Peer comparison

- fail or downgrade if peer comparison lacks `evidence_state`
- if peer is generic, it must say `archetypal peer pattern`
- if peer is real, it must include source

#### Conditional redesign

- fail if redesign path lacks:
  - trigger hypothesis
  - conflict resolved
  - evidence needed
  - kill condition
  - economic logic

#### TAD discipline

- fail if client-facing TAD has more than 5 actions
- fail if a TAD action does not map to:
  - dominant contradiction
  - evidence discriminator
  - claim permission

#### Report hierarchy

- fail if main body exceeds target section count without explicit justification
- fail if more than one visible report mode is presented as primary

### Type

- `validation`
- `product`
- `quality`

### Done when

- validator can fail a report for hierarchy/redundancy/product-quality issues, not only logical incoherence
- a thesis-free or duplicated report cannot pass to render

### Tests to add

- `test_validator_fails_when_no_dominant_thesis_exists`
- `test_validator_fails_when_executive_tad_financial_and_minimum_evidence_do_not_reference_same_contradiction`
- `test_validator_fails_when_client_facing_tad_exceeds_five_actions`
- `test_validator_fails_when_peer_comparison_lacks_evidence_state`
- `test_validator_fails_when_redesign_path_is_incomplete`
- `test_validator_fails_when_duplicate_claim_is_repeated_across_too_many_main_sections`
- `test_validator_fails_on_truncated_or_internal_motor_language_in_body`

---

## RHC-05 — Rewrite Render Order Around Thesis

### Problem

Even with section contracts, rendering still assumes section-first assembly rather than thesis-first assembly.

### Owners

- `motor_017`
- `render_section_contract.py`

### Files

- [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
- [render_section_contract.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/render_section_contract.py>)

### Required change

- renderer must render from:
  - `executive_thesis`
  - `main_report_outline`
  - `appendix_map`
  - `render_section_contract`
- supporting modes must appear as:
  - lens
  - supporting mode
  - appendix framing

Not as equal primary report types.

### Type

- `rendering`
- `integration`

### Done when

- there is only one visible primary report mode
- supporting modes are clearly subordinate
- rendering order follows thesis hierarchy, not raw motor order

### Tests to add

- `test_only_one_visible_report_mode_is_primary_in_client_facing_render`
- `test_supporting_modes_render_as_lenses_not_equal_primary_headings`

---

## P1 — Required For One Vanderbilt Product Quality Closure

## RHC-06 — Harden Executive Opening

### Problem

The executive opening must always contain:

- reframed problem
- dominant contradiction
- immediate action
- prohibited action
- financial exposure if wrong

### Owners

- `motor_047`
- `motor_016`
- `motor_036`

### Done when

- One Vanderbilt opens with regulation vs control-boundary thesis
- no executive opening can pass without the five required fields

---

## RHC-07 — Bound Peer Comparison Properly

### Problem

Peer comparison is still at risk of sounding stronger than evidence supports.

### Owners

- `motor_043`
- `motor_047`
- `motor_036`

### Required change

Each peer row must include:

- `peer_type`
- `evidence_state`
- `transferability`
- `what_it_proves`
- `what_it_does_not_prove`
- `source` when observed

### Done when

- archetypal peers are explicitly labeled as archetypal
- no real competitive superiority is implied without source

---

## RHC-08 — Deepen Conditional Redesign

### Problem

Redesign paths are still too shallow unless explicitly tied to conflict, trigger, economics, and kill condition.

### Owners

- `motor_044`
- `motor_047`
- `motor_036`

### Required redesign row contract

- `redesign_path`
- `trigger_hypothesis`
- `conflict_resolved`
- `economic_logic`
- `evidence_needed`
- `kill_condition`

### Done when

- One Vanderbilt can express:
  - tenant-control architecture redesign
  - triggered by tenant-driven load dominance
  - resolving regulation vs owner-control conflict
  - bounded by economic capture logic
  - killed by owner-controlled central-plant dominance

---

## RHC-09 — Split Client-Facing TAD From Technical TAD

### Problem

TAD still risks mixing client-priority action with legacy technical validation detail.

### Owners

- `motor_033`
- `motor_048`
- `motor_016`

### Required change

- `client_facing_tad`
  - max 5 actions
  - must map to contradiction or evidence discriminator or claim permission
- `appendix_tad`
  - may contain VoI, inference rank, technical validation records

### Done when

- client-facing body never shows the long technical action list
- appendix keeps the technical trace

---

## P2 — Certification And No-Regression

## RHC-10 — One Vanderbilt Before/After Certification

### Deliverables

- one certification pack with:
  - before/after main-section count
  - before/after executive thesis strength
  - before/after TAD action count
  - before/after peer comparison evidence bounding
  - before/after redesign completeness
  - before/after validator pass/fail reasons

### Files

- new:
  - `governanza/automation-base/runtime_executive_thesis_report_hierarchy_certification_latest.md`
  - `governanza/automation-base/runtime_executive_thesis_report_hierarchy_certification_latest.json`

### Done when

- One Vanderbilt shows:
  - fewer main sections
  - no duplicated legacy material in body
  - stronger executive thesis
  - peer comparison properly bounded
  - redesign path structurally complete
  - client-facing TAD <= 5

---

## Recommended Implementation Order

1. `RHC-01` Executive Synthesis / Thesis Engine
2. `RHC-02` Report Compression Engine
3. `RHC-03` Re-anchor `motor_016`
4. `RHC-04` Upgrade `motor_036`
5. `RHC-09` Split client-facing vs appendix TAD
6. `RHC-07` Bound peer comparison
7. `RHC-08` Deepen conditional redesign
8. `RHC-05` Rewrite render order around thesis
9. `RHC-10` One Vanderbilt certification

---

## Acceptance Gate

The plan is complete only if all of the following are true:

1. `executive_thesis` exists as a first-class runtime object
2. `main_report_outline` exists as a first-class runtime object
3. exactly one visible report mode is primary
4. supporting modes are subordinate lenses, not equal report identities
5. no client-facing report can pass without one dominant contradiction
6. no client-facing report can pass without one minimum evidence discriminator
7. client-facing TAD is capped to 5 actions
8. peer comparison is always evidence-bounded
9. redesign paths are complete or blocked
10. legacy sections do not dominate the body
11. validator can fail reports for hierarchy/redundancy/client-facing quality
12. One Vanderbilt after-state matches the intended thesis:
   - screening admissible
   - retrofit economics prohibited
   - dominant contradiction = regulation vs control boundary
   - immediate action = tenant metering + utility + LL97 + BMS / central-plant topology

---

## Remaining Risks

- over-compression may hide useful technical nuance
- executive synthesis may overstep evidence if not tied tightly to claim contracts
- deduplication can accidentally erase necessary support context
- report-mode hierarchy can become too rigid for unusual cases
- supporting modes may still leak into the body unless `motor_016` is fully re-anchored
- validator expansion can become brittle if phrased as template matching instead of semantic contract checks

---

## Final Position

The correct next evolution is **not** “more sections.”

It is:

- one thesis
- one dominant contradiction
- one bounded evidence discriminator
- one client-facing action stack
- one governed primary report mode

Everything else should support that thesis or move to appendix.
