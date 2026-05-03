# Runtime Structural Intelligence — Completion Plan

Generated on: `2026-04-30`

## Objective

Close the remaining gap between the **implemented structural-intelligence lane** and the **full literal requirements** of the large structural-intelligence prompt.

This plan is **not** the original expansion plan.
It is the **closure backlog** for the remaining delta after implementation and real runtime validation.

Current honest state:

- structural lane exists: `motor_037` to `motor_046`
- structural primary output modes are certified from official fixtures
- sovereign promotion gate exists and is working
- consistency blocking exists
- but the system is **not yet 100% literal** against the full prompt

The remaining gaps are mainly:

1. structural lane is still **subordinate by default**
2. the report body is not yet restructured into the **ideal report architecture**
3. there is no **universal claim contract register**
4. output-mode classification is still split across old and new lanes
5. output taxonomy still mixes legacy and new labels
6. `motor_036` still misses some literal prompt checks
7. there is no canonical `evidence_state_by_layer_register`
8. the final deliverable for this prompt does not yet exist as one package

---

## Non-Negotiables

Do **not** weaken:

- no hallucinated certainty
- no fake ROI
- no fake savings
- no compliance closure without evidence
- no benchmark as local truth
- no technology-first recommendation
- no digital twin worship
- no generic template output
- no final recommendation with missing evidence
- no claim without evidence state
- no scenario without falsification condition
- no TAD action disconnected from claim permission
- no accidental structural-primary override without explicit governance

---

## P0 — Required For 100%

## SIEC-01 — Make Structural Reasoning Sovereign By Default

### Problem

The structural lane is implemented, but it is still **secondary by default**.
Today it enriches the system and can promote explicitly, but the prompt requires the framework to evolve from:

`data -> inference -> validation -> decision`

to:

`data -> system abstraction -> dominant variables -> cross-layer contradictions -> problem reframing -> conditional redesign -> financial exposure -> TAD`

### Owners

- `motor_014`
- `motor_033`
- `motor_034`
- `motor_025`
- `motor_036`

### Files

- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)
- [motor_dependencies.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_dependencies.json>)

### Required change

- define a **canonical structural reasoning path** that downstream decision logic must read first
- `motor_014` must consume:
  - `system_abstraction`
  - `dominant_variable_register`
  - `cross_layer_conflict_register`
  - `problem_framing_register`
  - `minimum_evidence_for_discrimination_register`
- `motor_033` must treat structural TAD states as first-class, not sidecar
- `motor_034` must expose a single `canonical_problem_frame`
- `motor_025` must stop requiring a manual promotion gate for structural relevance in normal cases
- explicit override should still exist, but structural reasoning should no longer be “appendix-first”

### Type

- `priority`
- `integration`
- `flow`

### Done when

- a normal `One Vanderbilt` run without explicit override still produces a structural-first interpretation path
- `motor_014` and `motor_033` no longer need legacy-only inputs to frame the case
- structural reasoning is present upstream of TAD and not only in appendices

### Tests to add

- `test_structural_lane_is_default_reasoning_path_for_nyc_screening_case`
- `test_structural_lane_is_default_reasoning_path_for_manufacturing_case`

---

## SIEC-02 — Create Universal Claim Contract Register

### Problem

The prompt requires **every claim** to follow this contract:

- `statement`
- `evidence_state`
- `supporting_sources`
- `assumptions`
- `falsification_condition`
- `minimum_evidence_required`
- `allowed_use`
- `prohibited_use`

Today the system has this information **fragmented** across:

- structural statements
- claim permissions
- financial exposure rows
- redesign rows

But there is no single universal register.

### Owners

- `motor_034`
- structural-intelligence schemas/helpers
- `motor_036`

### Files

- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [schemas.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/schemas.py>)
- [__init__.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/__init__.py>)
- new helper recommended:
  - `runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/claim_contracts.py`
- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

### Required change

- add a canonical `claim_contract_register`
- each row must include:
  - `claim_id`
  - `statement`
  - `evidence_state`
  - `supporting_sources`
  - `assumptions`
  - `falsification_condition`
  - `minimum_evidence_required`
  - `allowed_use`
  - `prohibited_use`
  - `permission`
  - `current_evidence_summary`
- map both legacy and structural claims into that register

### Type

- `schema`
- `logic`
- `validation`

### Done when

- every claim class in the prompt is represented in `claim_contract_register`
- no visible claim appears without a matching claim-contract row
- `motor_036` blocks missing claim-contract fields

### Tests to add

- `test_every_visible_claim_has_full_claim_contract`
- `test_prohibited_claims_cannot_render_without_contract`

---

## SIEC-03 — Restructure The Main Report Body To Match The Prompt

### Problem

The system contains the structural content, but the **body architecture** still does not match the ideal report structure required by the prompt.

Missing as formal sections:

- `What the Client Thinks the Problem Is`
- `What the System Thinks the Problem Might Actually Be`
- `Evidence State by Layer`
- `What Not To Do Yet`
- `System Consistency Check`

### Owners

- `motor_015`
- `motor_016`
- `motor_017`

### Files

- [motor_015.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_015.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)

### Required change

- promote structural sections from appendix-only into the governed body
- body order should follow the prompt’s ideal structure
- `A9-A16` may remain as appendices, but the body must reflect the same semantic structure
- add explicit `What Not To Do Yet` block derived from:
  - prohibited claims
  - deferred TAD actions
  - blocked redesign recommendations
- add explicit `System Consistency Check` section derived from `motor_036`

### Type

- `flow`
- `report_structure`

### Done when

- the visible report body contains the prompt’s major sections by name or exact semantic equivalent
- `System Consistency Check` appears as a governed visible section
- `What Not To Do Yet` is explicit and sourced from structured state

### Tests to add

- `test_report_body_matches_structural_prompt_architecture`
- `test_what_not_to_do_yet_section_is_sourced_from_prohibited_claims_and_tad`

---

## SIEC-04 — Create Canonical Evidence State By Layer Register

### Problem

The prompt requires a layer-based reading of the system:

- physics
- operation
- energy
- finance
- regulation
- maintenance
- logistics
- procurement
- commercial
- culture
- control/responsibility
- market/competitiveness

Today the system has layer-related content, but no canonical `evidence_state_by_layer_register`.

### Owners

- `motor_040`
- `motor_041`
- `motor_045`
- `motor_043`
- `motor_016`

### Files

- new helper recommended:
  - `runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/evidence_by_layer.py`
- [motor_040.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_040.py>)
- [motor_041.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_041.py>)
- [motor_045.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_045.py>)
- [motor_043.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_043.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)

### Required change

- create a layer register with:
  - `layer`
  - `evidence_state`
  - `dominant_open_questions`
  - `observed_support`
  - `structural_risk_if_wrong`
- use it in:
  - contradictions
  - reframing
  - report rendering
  - validator

### Type

- `schema`
- `integration`

### Done when

- all 12 required layers appear, even if some are `NOT_OBSERVED`
- the report can render `Evidence State by Layer`
- contradictions and reframing can point back to layer-level evidence state

### Tests to add

- `test_evidence_state_by_layer_register_is_complete_for_building_case`
- `test_evidence_state_by_layer_register_is_complete_for_manufacturing_case`

---

## SIEC-05 — Add Literal Prompt Checks To System Consistency Validator

### Problem

`motor_036` is strong, but it still misses some literal checks from the structural prompt.

Critical missing checks:

- if `asset_type = manufacturing`, regulation cannot collapse to a building-only rule frame
- if `asset_type = NYC commercial building`, `LL84 / LL97 / PLUTO / DOB / DOF` must be activated
- if structural report body is used, required structural sections must be present
- if a claim is rendered, `claim_contract_register` must exist for it

### Owners

- `motor_036`

### Files

- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

### Required change

- add checks:
  - `manufacturing_regulatory_frame_not_building_only`
  - `nyc_commercial_required_public_datasets_active`
  - `structural_report_sections_present`
  - `rendered_claims_have_claim_contracts`

### Type

- `validation`

### Done when

- `motor_036` blocks a manufacturing run framed only by building logic
- `motor_036` blocks NYC commercial structural mode if domain pack did not activate
- `motor_036` blocks structural rendering without the required sections and claim contracts

### Tests to add

- `test_motor_036_blocks_building_only_regulatory_logic_for_manufacturing`
- `test_motor_036_blocks_nyc_structural_screening_without_ll84_ll97_pluto_dob_dof`
- `test_motor_036_blocks_missing_structural_body_sections`

---

## P1 — Strongly Recommended To Call It Closed Cleanly

## SIEC-06 — Unify Output Mode Classification

### Problem

There are still two coordinated layers:

- legacy report-type classifier
- structural output-mode classifier + sovereign promotion gate

That works, but it is not one classifier.

### Owners

- `motor_034`
- `motor_025`

### Files

- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)

### Required change

- replace dual classification with one `report_output_mode_classifier`
- every mode must be classified in one table:
  - `Target Classification Brief`
  - `Decision-Blocked Asset Brief`
  - `Exploratory Prior Brief`
  - `Compliance / Investment Screening Brief`
  - `Structural Contradiction Brief`
  - `System Redesign Hypothesis Brief`
  - `Competitive Positioning Brief`
  - `TAD Action Priority Brief`
  - `Full Technical Decision Intelligence Report`

### Done when

- `motor_025` no longer needs to merge two independent classifiers
- `motor_036` validates only one canonical output-mode table

### Tests to add

- `test_single_output_mode_classifier_covers_all_nine_modes`

---

## SIEC-07 — Normalize Output Taxonomy And Alias Policy

### Problem

The prompt’s output taxonomy and the runtime’s legacy labels still coexist.

Examples:

- `Entity Address Classification Brief`
- `Target Clarification Brief`
- `Target Classification Brief`

### Owners

- `motor_007`
- `motor_025`
- `motor_016`
- taxonomy helpers

### Files

- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- public-data routing taxonomy helpers under:
  - `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/`

### Required change

- define explicit alias policy:
  - which labels are canonical
  - which labels are compatibility aliases only
- visible surface should render the canonical label set only

### Done when

- the visible runtime/report/manifest taxonomy is internally normalized
- aliases remain allowed only at ingest/compat layer

### Tests to add

- `test_visible_output_taxonomy_uses_only_canonical_labels`

---

## SIEC-08 — Final Structural Prompt Deliverable

### Problem

The implementation exists, but the final prompt-specific package does not yet exist as one artifact.

### Owners

- governance docs
- certification scripts if needed

### Files

- new required docs in:
  - `governanza/automation-base/`

### Required change

- create a final package containing:
  1. updated architecture
  2. new motors
  3. changes to existing motors
  4. required schemas
  5. anti-hallucination rules
  6. output modes
  7. report structure
  8. manufacturing example
  9. building example
  10. tests
  11. implementation phases
  12. technical risks
  13. what must not change

### Done when

- one final doc/json pair exists
- it references real runs, tests, and files
- it can be shown as the closure artifact for this prompt

---

## P2 — Cleanups That Make The System More Defensible

## SIEC-09 — Make Structural Sections First-Class In The Render Contract

### Problem

Structural content is still partly carried as appendix-governed surfaces.

### Owners

- `motor_016`
- `motor_017`

### Done when

- structural sections have explicit body/appendix policy by output mode
- `Structural Contradiction Brief` and `TAD Action Priority Brief` can reorder the report body cleanly without ad hoc branching

---

## SIEC-10 — Certify Default Non-Override Behavior After Sovereignty Shift

### Problem

Once the structural lane becomes sovereign by default, the framework needs explicit non-regression proof that cases do not overpromote.

### Owners

- tests
- governance certification

### Done when

- `One Vanderbilt` normal still does not become `Full Technical`
- `Wilsonart` normal still does not become a false redesign recommendation
- address/HQ cases still degrade correctly

---

## Recommended Execution Order

1. `SIEC-02` — universal claim contract register
2. `SIEC-04` — evidence state by layer
3. `SIEC-05` — literal validator checks
4. `SIEC-03` — report body restructure
5. `SIEC-01` — make structural reasoning sovereign by default
6. `SIEC-06` — unify output mode classifier
7. `SIEC-07` — normalize taxonomy
8. `SIEC-08` — final prompt deliverable
9. `SIEC-09` and `SIEC-10` — cleanup and certification

Reason:

- first close schema and validator contracts
- then restructure the body
- only then promote sovereignty and collapse classifiers

---

## Final 100% Acceptance Gate

The large structural-intelligence prompt is only **100% complete** when all of the following are true:

1. structural reasoning is the default reasoning path, not a side lane
2. every rendered claim has a full universal claim contract
3. the visible report body matches the prompt’s structural architecture
4. `Evidence State by Layer` exists as a canonical register and visible section
5. `motor_036` enforces the literal remaining checks from the prompt
6. output-mode classification is unified
7. visible output taxonomy is normalized
8. a final structural prompt certification artifact exists

Until then, the correct statement remains:

- **implemented strongly**
- **not yet 100% literal**

