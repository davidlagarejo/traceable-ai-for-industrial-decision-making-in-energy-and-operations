# Runtime Report System Precision Hardening Backlog

## Status

This backlog operationalizes the report-system correction prompt without rewriting the framework or moving truth logic into prompts.

It is a **precision hardening program**, not a cosmetic report refresh.

It targets these failures:

1. over-blocking cases with strong public evidence
2. weak differentiation between report identities
3. generic template behavior
4. weak industry adaptation
5. underuse of canonical public sources
6. weak financial exposure translation
7. weak value-of-evidence prioritization
8. contradictions between summary, claim matrix, and TAD
9. duplicate items in Minimum Evidence Pack
10. visible pipeline garbage in client-facing output
11. no mandatory coherence self-check before PDF generation

This backlog must preserve:

- no hallucinated certainty
- no ROI without evidence
- no compliance closure without official filing / verified baseline
- no savings claim without utility/system/control evidence
- no benchmark as local truth
- no LLM-generated certainty
- no final recommendation when evidence is missing
- no over-auditing before minimum evidence request

It complements, but does not replace:

- [runtime_decision_admissibility_report_ticket_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_decision_admissibility_report_ticket_backlog.md>)
- [runtime_evidence_maturity_nyc_execution_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_evidence_maturity_nyc_execution_backlog.md>)
- [runtime_global_public_data_routing_v1_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_global_public_data_routing_v1_backlog.md>)

---

## Sovereign Motor Map

The current architecture is already close to correct. The hardening strategy must respect sovereignty:

- `motor_007`
  - target admissibility
  - `asset_context_readiness`
  - `recommended_report_type`
- `motor_012`
  - asset field register
  - missing evidence register
  - field-level support semantics
- `motor_014`
  - minimum evidence unlock map
  - scenario space
  - decision front inputs
- `motor_028`
  - discovery execution layer
- `motor_033`
  - TAD / decision admissibility presentation layer
- `motor_034`
  - variable maturity
  - claim permission register
  - decision permission register
  - report readiness register
- `motor_035`
  - routing plan synthesis
- `motor_016`
  - report package assembly
- `motor_019`
  - narrative rendering
- `motor_024`
  - governance summary and consistency audit
- `motor_025`
  - hard publication hold / degrade enforcement
- `motor_027`
  - manifest and delivery

Rules:

- do **not** move report-type sovereignty out of `motor_007`
- do **not** move claim-permission sovereignty out of `motor_034`
- do **not** move routing sovereignty out of `motor_035`
- do **not** move discovery execution into `motor_035`
- do **not** let `motor_019` become a truth engine
- do **not** merge GTM overlays into the technical runtime brief

---

## Problem Map

| Problem | Primary owner | Secondary owner | Correction class |
|---|---|---|---|
| over-blocking strong public-evidence cases | `motor_007` | `motor_034` | `weak logic` |
| weak report-type differentiation | `motor_007` | `motor_034` | `missing logic` |
| generic template behavior | `motor_016` | `motor_019` | `prompt/template issue` |
| weak industry adaptation | `motor_035` | `motor_028`, `motor_012`, `motor_014`, `motor_033` | `missing logic` |
| weak canonical source leverage | `motor_035` | `motor_028` | `source routing issue` |
| weak financial exposure translation | `motor_014` | `motor_033`, `motor_019` | `weak logic` |
| weak value-of-evidence prioritization | `motor_014` | `motor_034` | `weak logic` |
| contradictions between summary, claim matrix and TAD | `motor_024` | `motor_034`, `motor_033`, `motor_025` | `governance inconsistency` |
| duplicated Minimum Evidence Pack | `motor_014` | `motor_019` | `weak logic` |
| visible pipeline garbage | `motor_016` | `motor_019`, `motor_025` | `report rendering issue` |
| missing mandatory pre-PDF coherence check | `motor_024` | `motor_025`, `motor_016`, `motor_019` | `bad orchestration` |
| template contamination across cases | `motor_016` | `motor_019`, `motor_024`, `motor_025` | `prompt/template issue` |

---

## Target Outcome

The runtime must support materially different outputs:

- `Target Classification Brief`
- `Entity Address Classification Brief`
- `Decision-Blocked Asset Brief`
- `Exploratory Prior Brief`
- `Compliance / Investment Screening Brief`
- `Full Technical Decision Intelligence Report`

And it must distinguish:

- blocked because the asset is not sufficiently identified
- blocked because multiple critical clusters are missing
- screening admissible because public evidence is strong
- verification blocked because internal data is still missing

---

## New Helper Modules

Prefer adding helpers instead of new sovereign motors.

Create or extend:

- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/cluster_scoring.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/report_type_classifier.py`
- `runtime-orchestrator/src/runtime_orchestrator/decision_intelligence/financial_exposure.py`
- `runtime-orchestrator/src/runtime_orchestrator/decision_intelligence/scenario_contracts.py`
- `runtime-orchestrator/src/runtime_orchestrator/reporting/case_adaptation.py`
- `runtime-orchestrator/src/runtime_orchestrator/reporting/report_preflight.py`

---

## Execution Order

The execution order is strict:

1. freeze test fixtures and current diagnosis
2. add cluster maturity scoring
3. enrich report-type classification
4. harden source routing by decision and industry
5. reconcile claims and governance counts
6. graduate TAD states
7. harden evidence pack, value of information, financial exposure, and scenario contracts
8. add case adaptation memo and template contamination control
9. add pre-PDF report preflight and hard blocking
10. run certification against Wilsonart, One Vanderbilt, and HQ/address cases

---

## Ticket Format

Each ticket includes:

- `Ticket ID`
- `Priority`
- `Owner motor(s)`
- `Primary file(s)`
- `Objective`
- `Required changes`
- `Dependencies`
- `Tests`
- `Acceptance criteria`

---

## Wave A — Freeze Diagnosis and Certification Fixtures

### Ticket RSH-001

- `Priority`: P0
- `Owner motor(s)`: `motor_007`, `motor_014`, `motor_033`, `motor_034`, `motor_035`
- `Primary file(s)`:
  - `runtime-orchestrator/tests/`
- `Objective`:
  Freeze current failure modes before touching logic.
- `Required changes`:
  - Add snapshot-style tests for:
    - `One Vanderbilt`
    - `Wilsonart Temple North Laminate Facility`
    - `Prologis / PIER 1 BAY 1`
  - Assert current undesired equivalence where applicable before fixing it.
- `Dependencies`:
  - existing real runs and manifests
- `Tests`:
  - `test_report_type_classifier_one_vanderbilt_vs_wilsonart.py`
  - `test_case_adaptation_fixture_baselines.py`
- `Acceptance criteria`:
  - the suite captures the exact before-state and can prove later improvement

---

## Wave B — Cluster Maturity Scoring

### Ticket RSH-002

- `Priority`: P0
- `Owner motor(s)`: `motor_034`
- `Primary file(s)`:
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
  - `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/cluster_scoring.py`
- `Objective`:
  Add cluster-level maturity scoring that can distinguish strong public screening readiness from verification-grade readiness.
- `Required changes`:
  - Create `cluster_maturity_register`
  - Create `cluster_report_readiness_profile`
  - Score these clusters:
    - `identity_cluster`
    - `boundary_cluster`
    - `geometry_size_cluster`
    - `vintage_structure_cluster`
    - `operating_regime_cluster`
    - `fuel_energy_cluster`
    - `systems_cluster`
    - `control_boundary_cluster`
    - `regulatory_cluster`
    - `financial_boundary_cluster`
- `Dependencies`:
  - `motor_012`
  - `motor_028`
  - `motor_035`
- `Tests`:
  - `test_cluster_maturity_allows_screening_without_utility_bills.py`
- `Acceptance criteria`:
  - One Vanderbilt can show multiple `L3` public clusters without forcing `systems` or `utility_bills` to `L3`

### Ticket RSH-003

- `Priority`: P0
- `Owner motor(s)`: `motor_012`
- `Primary file(s)`:
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- `Objective`:
  Separate identity support from operating substrate support.
- `Required changes`:
  - Add field-support semantics:
    - `identity_supported`
    - `physical_substrate_supported`
    - `operating_substrate_supported`
    - `regulatory_supported`
  - Add explicit downgrade language:
    - `source confirms identity only, not physical operating substrate`
- `Dependencies`:
  - existing `asset_field_register`
- `Tests`:
  - `test_field_support_semantics_do_not_overpromote_identity_sources.py`
- `Acceptance criteria`:
  - no source can confirm `address` and accidentally imply `GFA`, `systems`, or `energy`

---

## Wave C — Report Type Classifier Hardening

### Ticket RSH-004

- `Priority`: P0
- `Owner motor(s)`: `motor_007`
- `Primary file(s)`:
  - [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
  - `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/report_type_classifier.py`
- `Objective`:
  Replace coarse blocked/not-blocked logic with multidimensional report-type logic.
- `Required changes`:
  - keep `motor_007` as sovereign owner of `recommended_report_type`
  - consume `cluster_report_readiness_profile`
  - support:
    - `Target Classification Brief`
    - `Decision-Blocked Asset Brief`
    - `Exploratory Prior Brief`
    - `Compliance / Investment Screening Brief`
    - `Full Technical Decision Intelligence Report`
- `Dependencies`:
  - `RSH-002`
- `Tests`:
  - `test_report_type_classifier_one_vanderbilt_vs_wilsonart.py`
  - `test_report_type_classifier_hq_remains_nontechnical.py`
- `Acceptance criteria`:
  - One Vanderbilt is no longer classified with the same severity as Wilsonart
  - HQ/address cases still degrade early and correctly

---

## Wave D — Routing by Jurisdiction, Industry, and Decision Type

### Ticket RSH-005

- `Priority`: P0
- `Owner motor(s)`: `motor_035`
- `Primary file(s)`:
  - [motor_035.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py>)
- `Objective`:
  Make routing sensitive to decision front and dominant missing cluster.
- `Required changes`:
  - expand `source_routing_plan` to include:
    - `decision_type`
    - `dominant_missing_cluster`
    - `source_family_coverage_requirements`
  - for NYC commercial:
    - require `PLUTO`, `DOF`, `DOB`, `LL84`, `LL97`, `ENERGY STAR` when relevant
  - for Texas manufacturing:
    - require `TCEQ`, `EPA ECHO`, `TRI`, `GHGRP`, `county appraisal`, `utility/tariff context`, `NAICS/SIC`, `facility pages`
- `Dependencies`:
  - `motor_007`
  - `motor_034`
- `Tests`:
  - `test_routing_plan_changes_by_decision_type.py`
  - `test_texas_manufacturing_routing_uses_industrial_mandatories.py`
- `Acceptance criteria`:
  - routing plan differs materially between office tower compliance screening and manufacturing process-capex screening

### Ticket RSH-006

- `Priority`: P0
- `Owner motor(s)`: `motor_028`
- `Primary file(s)`:
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- `Objective`:
  Emit source-family coverage in a form consumable by maturity, report type, and narrative layers.
- `Required changes`:
  - add `source_family_coverage_register`
  - add per-source consequences:
    - `identity_only`
    - `substrate_partial`
    - `regulatory_context_only`
    - `asset_level_public_strong`
- `Dependencies`:
  - `RSH-005`
- `Tests`:
  - `test_source_family_coverage_register_differentiates_identity_vs_substrate.py`
- `Acceptance criteria`:
  - downstream motors can tell the difference between identity confirmation and screening-grade technical context

---

## Wave E — Claim Permission Reconciliation

### Ticket RSH-007

- `Priority`: P0
- `Owner motor(s)`: `motor_034`
- `Primary file(s)`:
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- `Objective`:
  Normalize explicit claim permission states and summary counts.
- `Required changes`:
  - ensure every claim has:
    - `permission`
    - `reason`
    - `required_evidence`
    - `dependency_variables`
    - `upgrade_path`
  - emit canonical counts:
    - `allowed_count`
    - `conditional_count`
    - `prohibited_count`
- `Dependencies`:
  - existing `claim_permission_register`
- `Tests`:
  - `test_claim_permission_counts_match_summary.py`
- `Acceptance criteria`:
  - claim summary and matrix counts are identical for every run

### Ticket RSH-008

- `Priority`: P0
- `Owner motor(s)`: `motor_024`, `motor_025`
- `Primary file(s)`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- `Objective`:
  Enforce hard blocking when summary counts diverge from the matrix.
- `Required changes`:
  - add check:
    - `governance_claim_counts == matrix_claim_counts`
  - if false:
    - hold PDF generation
    - register governance inconsistency
- `Dependencies`:
  - `RSH-007`
- `Tests`:
  - `test_pdf_is_blocked_when_claim_counts_diverge.py`
- `Acceptance criteria`:
  - PDF cannot generate with mismatched claim counts

---

## Wave F — TAD Graduation

### Ticket RSH-009

- `Priority`: P0
- `Owner motor(s)`: `motor_033`
- `Primary file(s)`:
  - [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
- `Objective`:
  Replace flat TAD posture with differentiated decision admissibility.
- `Required changes`:
  - force TAD states:
    - `ACT NOW`
    - `VALIDATE FIRST`
    - `INVESTIGATE`
    - `DEFER`
    - `NO-GO`
  - define separate decision fronts for:
    - `commercial building`
    - `industrial / manufacturing`
- `Dependencies`:
  - `motor_014`
  - `motor_034`
- `Tests`:
  - `test_tad_has_differentiated_states.py`
  - `test_one_vanderbilt_tad_not_equal_wilsonart_tad.py`
- `Acceptance criteria`:
  - One Vanderbilt and Wilsonart no longer collapse into identical TAD posture

---

## Wave G — Minimum Evidence Pack, Value of Information, Financial Exposure, Scenario Contracts

### Ticket RSH-010

- `Priority`: P0
- `Owner motor(s)`: `motor_014`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- `Objective`:
  Upgrade the Minimum Evidence Pack from list-of-missing-items to unlock-prioritized evidence architecture.
- `Required changes`:
  - dedupe by:
    - semantic equivalence
    - unlock equivalence
    - asset-type overlap
  - max `7–10` items
  - add:
    - `priority`
    - `effort`
    - `value_of_information`
    - `unlocks`
- `Dependencies`:
  - existing `minimum_evidence_unlock_map`
- `Tests`:
  - `test_minimum_evidence_pack_dedupes_unlock_equivalents.py`
- `Acceptance criteria`:
  - no duplicate or near-duplicate evidence items remain

### Ticket RSH-011

- `Priority`: P0
- `Owner motor(s)`: `motor_014`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - `runtime-orchestrator/src/runtime_orchestrator/decision_intelligence/financial_exposure.py`
- `Objective`:
  Translate uncertainty into downside exposure without inventing ROI.
- `Required changes`:
  - create `financial_exposure_assumption_register`
  - require columns:
    - `assumption`
    - `current_support`
    - `downside_if_wrong`
    - `evidence_needed`
    - `financial_consequence`
- `Dependencies`:
  - `motor_034`
  - `motor_033`
- `Tests`:
  - `test_financial_exposure_requires_downside_translation.py`
- `Acceptance criteria`:
  - every financial exposure item names a concrete downside and evidence path

### Ticket RSH-012

- `Priority`: P0
- `Owner motor(s)`: `motor_014`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - `runtime-orchestrator/src/runtime_orchestrator/decision_intelligence/scenario_contracts.py`
- `Objective`:
  Force scenarios to be evidence-linked, financially meaningful, and falsifiable.
- `Required changes`:
  - for every scenario require:
    - `financial_meaning`
    - `what_makes_it_true`
    - `what_falsifies_it`
    - `evidence_needed`
    - linked `decision_front`
- `Dependencies`:
  - `RSH-010`
  - `RSH-011`
- `Tests`:
  - `test_every_scenario_has_financial_meaning_and_falsification.py`
- `Acceptance criteria`:
  - no scenario can render if it lacks financial meaning or falsification condition

---

## Wave H — Industry-Specific Adaptation

### Ticket RSH-013

- `Priority`: P0
- `Owner motor(s)`: `motor_035`, `motor_028`, `motor_012`, `motor_014`, `motor_033`
- `Primary file(s)`:
  - [motor_035.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py>)
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
- `Objective`:
  Activate materially different industrial/manufacturing logic from commercial office logic.
- `Required changes`:
  - manufacturing-specific needs:
    - `NAICS/SIC`
    - `process lines`
    - `presses`
    - `curing / thermal process`
    - `compressed air`
    - `dust collection`
    - `VOC emissions`
    - `steam / boilers / thermal oil`
    - `throughput`
    - `downtime`
    - `TCEQ/EPA/ECHO/TRI/GHGRP`
  - office-tower needs:
    - `GFA`
    - `LL84/LL97`
    - `BMS`
    - `HVAC`
    - `tenant metering`
    - `lease responsibility`
    - `occupancy / use mix`
    - `ENERGY STAR`
    - `DOB permits`
- `Dependencies`:
  - routing and maturity waves
- `Tests`:
  - `test_industry_specific_logic_is_materially_different.py`
- `Acceptance criteria`:
  - manufacturing and office-tower cases no longer reuse the same dominant risks, evidence pack, or TAD fronts

---

## Wave I — Case Adaptation Memo and Template Contamination Control

### Ticket RSH-014

- `Priority`: P0
- `Owner motor(s)`: `motor_016`
- `Primary file(s)`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - `runtime-orchestrator/src/runtime_orchestrator/reporting/case_adaptation.py`
- `Objective`:
  Make case adaptation explicit before rendering.
- `Required changes`:
  - add `case_adaptation_memo`
  - required dimensions:
    - `asset type`
    - `jurisdiction`
    - `industry`
    - `public sources found`
    - `evidence maturity`
    - `decision evaluated`
    - `dominant risks`
    - `allowed/prohibited claims`
    - `dominant scenario`
    - `specific evidence gaps`
- `Dependencies`:
  - all upstream structured outputs
- `Tests`:
  - `test_case_adaptation_memo_blocks_template_contamination.py`
- `Acceptance criteria`:
  - the memo proves substantive differences between similar cases

### Ticket RSH-015

- `Priority`: P0
- `Owner motor(s)`: `motor_024`, `motor_025`
- `Primary file(s)`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- `Objective`:
  Block parametrized look-alike outputs.
- `Required changes`:
  - if `case_adaptation_memo` is weak or missing:
    - register `TEMPLATE_CONTAMINATION_FAILURE`
    - hold PDF generation
- `Dependencies`:
  - `RSH-014`
- `Tests`:
  - `test_template_contamination_failure_blocks_pdf.py`
- `Acceptance criteria`:
  - report generation stops if adaptation is superficial

---

## Wave J — Report Rendering Cleanup and Preflight

### Ticket RSH-016

- `Priority`: P0
- `Owner motor(s)`: `motor_019`
- `Primary file(s)`:
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Restrict narrative generation to structured truth and remove visible pipeline garbage.
- `Required changes`:
  - lint against:
    - `Use the chart`
    - `The prose should`
    - `Reader takeaway` if disallowed
    - `This section should`
    - placeholders
    - internal instruction residues
  - no narrative may invent stronger claims than registers permit
- `Dependencies`:
  - `motor_034`
  - `motor_014`
  - `motor_033`
- `Tests`:
  - `test_report_narrative_rejects_internal_instruction_residue.py`
- `Acceptance criteria`:
  - no internal pipeline instruction text appears in client-facing content

### Ticket RSH-017

- `Priority`: P0
- `Owner motor(s)`: `motor_024`, `motor_025`, `motor_027`
- `Primary file(s)`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
  - [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
  - `runtime-orchestrator/src/runtime_orchestrator/reporting/report_preflight.py`
- `Objective`:
  Add a mandatory pre-PDF report preflight.
- `Required changes`:
  - create `report_preflight_register`
  - include checks for:
    - duplicate evidence items
    - inconsistent claim counts
    - wrong asset name
    - wrong jurisdiction
    - wrong regulation
    - `0 sqft`
    - blank fields presented as data
    - missing adaptation memo
  - if any critical check fails:
    - `DO NOT GENERATE PDF`
- `Dependencies`:
  - `RSH-007`
  - `RSH-014`
  - `RSH-016`
- `Tests`:
  - `test_report_preflight_blocks_pdf_on_critical_lint_failure.py`
- `Acceptance criteria`:
  - PDF generation is impossible when critical lint or consistency checks fail

---

## Wave K — Self-Evaluation

### Ticket RSH-018

- `Priority`: P0
- `Owner motor(s)`: `motor_024`
- `Primary file(s)`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- `Objective`:
  Emit mandatory per-run self-evaluation after report generation logic completes.
- `Required changes`:
  - add `phase_self_evaluation_register`
  - for each wave/fix area record:
    - `change_implemented`
    - `test_run`
    - `result`
    - `remaining_gap`
- `Dependencies`:
  - all upstream waves
- `Tests`:
  - `test_self_evaluation_register_is_present.py`
- `Acceptance criteria`:
  - every run can state whether a problem is resolved, partially resolved, or unresolved

---

## Wave L — Mandatory Certification Cases

### Ticket RSH-019

- `Priority`: P0
- `Owner motor(s)`: end-to-end
- `Primary file(s)`:
  - `runtime-orchestrator/tests/`
- `Objective`:
  Certify the corrected system against required cases.
- `Required changes`:
  - run and compare at minimum:
    - `Wilsonart Temple Manufacturing Facility`
    - `One Vanderbilt NYC`
    - `Corporate HQ / Mailing Address`
- `Dependencies`:
  - all previous waves
- `Tests`:
  - `test_wilsonart_expected_behavior.py`
  - `test_one_vanderbilt_expected_behavior.py`
  - `test_hq_expected_behavior.py`
- `Acceptance criteria`:
  - Wilsonart and One Vanderbilt no longer receive identical treatment
  - claim permissions, TAD, financial exposure, and evidence pack behave as expected by case

---

## Definition of Done

The implementation is complete only if:

1. One Vanderbilt and Wilsonart no longer receive identical treatment
2. report type changes based on evidence maturity, not a single missing field
3. Minimum Evidence Pack contains no duplicates
4. claim permission summary matches matrix exactly
5. TAD shows differentiated states
6. financial exposure is explicit and downside-oriented
7. regulatory routing is jurisdiction and industry specific
8. no internal pipeline text appears in final report
9. PDF generation blocks on critical preflight failure
10. self-evaluation artifact exists after each run
11. case adaptation memo proves substantive adaptation

---

## What Must Not Be Weakened

- no hallucinated certainty
- no ROI without evidence
- no compliance closure without official filing / verified baseline
- no savings claim without utility/system/control evidence
- no benchmark as local truth
- no LLM-generated certainty
- no final recommendation when evidence is missing
- no over-auditing before minimum evidence request
- no report identity promotion just to make the output look stronger
- no template parametrization disguised as case adaptation
