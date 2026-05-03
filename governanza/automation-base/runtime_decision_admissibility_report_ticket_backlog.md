# Runtime Decision-Admissibility Report Ticket Backlog

## 1. Purpose

This backlog converts the current runtime report from a degraded technical report into a product-native deliverable:

- `Decision-Blocked Asset Brief`
- `Asset Decision-Admissibility Brief`
- `Minimum Evidence Report for Asset Investment Uncertainty`

It does **not** redefine the 8 phases.
It operationalizes them in the reporting and decision surface so the final artifact:

- does not fake completeness,
- does not let issuer context dominate asset truth,
- does not present empty fields as data,
- does not emit a normal technical report when the case is blocked,
- and does not confuse "lack of evidence" with "system failure".

This backlog complements:

- [runtime_asset_first_hardening_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_asset_first_hardening_backlog.md>)
- [runtime_subject_admissibility_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_subject_admissibility_backlog.md>)

Those documents fix the subject and asset-first foundation.
This document fixes the **product-facing report** and the motors that shape it.

---

## 2. Governing standard

The report must make the reader feel:

`Good thing we did not move forward blindly.`

It must **not** make the reader feel:

`The AI failed to find enough data.`

The artifact must behave like a deliberate product of decision governance, not like an incomplete or broken report.

---

## 3. Product states the runtime must support

The report layer must explicitly support these classes:

- `Issuer Context Memo`
- `Address Candidate Brief`
- `Site Candidate Brief`
- `Decision-Blocked Asset Brief`
- `Asset Decision-Admissibility Brief`
- `Pre-Verification Asset Brief`
- `TDIR Preliminary`

Rules:

- `asset_context_insufficient` cannot render as `TDIR`.
- `address_candidate_only` cannot render as `Pre-Verification Asset Brief`.
- `issuer_context_only` cannot render as an asset report.

---

## 4. Mandatory report sections for blocked / low-evidence cases

The new product spine must support these sections as first-class output blocks:

1. Cover Page
2. Executive Decision-Admissibility Brief
3. Investment Uncertainty Map
4. Minimum Evidence Pack
5. Scenario Space Under Current Uncertainty
6. Asset Context Readiness
7. Blocking Conflicts
8. Inference Case Register
9. Validation Architecture
10. Financial Exposure Under Uncertainty
11. Regulatory / Normative Screening
12. TAD — Decision-Admissibility Layer
13. Next Best Questions
14. Appendices

---

## 5. Execution order

The implementation order is strict:

1. `motor_014`
2. `motor_015`
3. `motor_016`
4. `motor_019`
5. `motor_018`
6. `motor_024`
7. `motor_025`
8. `motor_027`
9. `motor_012`
10. `motor_028`
11. `motor_033`
12. `motor_005`
13. `motor_006`
14. `motor_007`
15. `motor_002`
16. `motor_010`
17. `motor_020`
18. `motor_022`

Reason:

- first change the decision core and report assembly,
- then enforce governance and export guards,
- then improve upstream seeds and evidence routing,
- then harden propagation and conformance.

---

## 6. Ticket format

Each ticket includes:

- `Ticket ID`
- `Priority`
- `Owner motor(s)`
- `Primary file(s)`
- `Objective`
- `Required changes`
- `Dependencies`
- `Acceptance criteria`

---

## 7. Wave A — Product identity and decision state

### Ticket RPT-001

- `Priority`: P0
- `Owner motor(s)`: `motor_014`
- `Primary file(s)`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- `Objective`:
  Reframe the Decision Core around `decision blocked by what`, not just around generic conflicts and validation urgency.
- `Required changes`:
  - Add `decision_front_register`.
  - Add `blocked_decision_register`.
  - Add `primary_block_reason`.
  - Add `minimum_evidence_unlock_map`.
  - Add `information_deficit_score`.
  - Add `scenario_space`.
  - Force `LC-ASSET-01` or equivalent asset-insufficiency case to become primary blocker when critical clusters are missing.
- `Dependencies`:
  - existing `motor_007` subject gate
  - existing `motor_012` physical prior outputs
- `Acceptance criteria`:
  - Every run can answer:
    - what decision is blocked,
    - why it is blocked,
    - what evidence unlocks it.
  - `information_deficit_score` cannot be `LOW` when `geometry_size`, `operating_regime`, and `systems` are missing.

### Ticket RPT-002

- `Priority`: P0
- `Owner motor(s)`: `motor_033`
- `Primary file(s)`:
  - [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
- `Objective`:
  Make TAD close the product around decision fronts, not around loosely grouped inference actions.
- `Required changes`:
  - Add explicit `decision_front` taxonomy:
    - acquisition underwriting
    - energy retrofit CAPEX
    - compliance investment
    - energy performance claim
    - refinancing / lending
    - seller diligence request
  - Map each front to:
    - `current_status`
    - `why_blocked`
    - `required_evidence`
    - `admissible_action`
  - Force posture values:
    - `act_now`
    - `validate_first`
    - `investigate_then_decide`
    - `defer`
    - `no_go`
- `Dependencies`:
  - `RPT-001`
- `Acceptance criteria`:
  - TAD table is no longer a generic action queue.
  - Each row names a concrete decision front and its admissible action.

### Ticket RPT-003

- `Priority`: P0
- `Owner motor(s)`: `motor_007`
- `Primary file(s)`:
  - [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- `Objective`:
  Promote report admissibility to a first-class runtime gate.
- `Required changes`:
  - Add `report_admissibility_state`.
  - Add `decision_block_state`.
  - Add `allowed_report_identities_by_state`.
  - Enforce:
    - `asset_context_insufficient -> Decision-Blocked Asset Brief`
    - `address_candidate_only -> Address Candidate Brief`
    - `issuer_context_only -> Issuer Context Memo`
- `Dependencies`:
  - subject admissibility changes already in place
- `Acceptance criteria`:
  - No blocked or insufficient case can silently render as `TDIR`.

---

## 8. Wave B — Output blocks and report structure

### Ticket RPT-004

- `Priority`: P0
- `Owner motor(s)`: `motor_015`
- `Primary file(s)`:
  - [motor_015.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_015.py>)
- `Objective`:
  Replace legacy report blocks with product-native decision blocks.
- `Required changes`:
  - Replace the current effective spine with output blocks for:
    - cover
    - executive decision brief
    - uncertainty map
    - minimum evidence pack
    - scenario space
    - asset context readiness
    - blocking conflicts
    - inference case register
    - validation architecture
    - financial exposure
    - regulatory screening
    - TAD
    - next best questions
    - appendices
  - Create `section_eligibility_register` for each block.
  - Mark blocks as:
    - `body_allowed`
    - `appendix_only`
    - `blocked`
- `Dependencies`:
  - `RPT-001`
  - `RPT-003`
- `Acceptance criteria`:
  - No low-evidence case uses the old `C1–C9` body structure as its dominant visible identity.

### Ticket RPT-005

- `Priority`: P0
- `Owner motor(s)`: `motor_016`
- `Primary file(s)`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- `Objective`:
  Rebuild the report package as a `Decision-Admissibility` product, not a degraded TDIR.
- `Required changes`:
  - Replace legacy chapter framing with document-type-specific assembly.
  - Make the cover show:
    - report type
    - epistemic grade
    - publication ceiling
    - decision state
    - primary warning
  - Make executive brief open with:
    - decision evaluated
    - current state
    - main block reason
    - minimum evidence required
    - admissible next action
  - Move finance to appendix automatically when asset context is insufficient.
  - Ensure `Asset Context Readiness` and `Minimum Evidence Pack` are early body sections, not buried.
- `Dependencies`:
  - `RPT-004`
- `Acceptance criteria`:
  - A blocked case reads as a deliberate `Decision-Blocked Asset Brief`.
  - Finance never dominates the first half of a blocked report.

### Ticket RPT-006

- `Priority`: P0
- `Owner motor(s)`: `motor_017`
- `Primary file(s)`:
  - [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
- `Objective`:
  Render different report classes distinctly enough that the document no longer looks like a failed technical report.
- `Required changes`:
  - Distinct cover templates by `report_identity_state`.
  - Distinct subtitle lines and `Use / Not Use` box.
  - Appendix partitioning for traceability, governance, and issuer context.
  - Bilingual rendering must preserve document class.
- `Dependencies`:
  - `RPT-005`
- `Acceptance criteria`:
  - `Decision-Blocked Asset Brief` looks intentional and productized.
  - `TDIR Preliminary` remains visually distinct from blocked briefs.

---

## 9. Wave C — LLM and language discipline

### Ticket RPT-007

- `Priority`: P0
- `Owner motor(s)`: `motor_019`
- `Primary file(s)`:
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Restrict the LLM to product-native sections and remove all instruction leakage and pseudo-template text.
- `Required changes`:
  - Redefine section packets for:
    - executive brief
    - scenario framing
    - blocked decision explanation
    - validation path
    - TAD framing
  - Ban internal strings from output:
    - `The prose should`
    - `Use in text`
    - `The chart should`
    - any instruction-style residue
  - Add hard lints for:
    - instruction leakage
    - unsupported certainty
    - fake closure
  - Keep bilingual EN/ES output.
- `Dependencies`:
  - `RPT-004`
  - `RPT-005`
- `Acceptance criteria`:
  - No internal prompt or instruction text survives into report artifacts.
  - Language remains simple, forceful, and subordinate to structured objects.

### Ticket RPT-008

- `Priority`: P1
- `Owner motor(s)`: `motor_019`
- `Primary file(s)`:
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Rewrite the executive narrative so it sells the product truthfully.
- `Required changes`:
  - Replace any weak "report incomplete" framing with:
    - decision blocked,
    - minimum evidence required,
    - good reason not to move forward blindly.
  - Introduce reusable executive framing aligned to the product thesis.
- `Dependencies`:
  - `RPT-007`
- `Acceptance criteria`:
  - The reader understands immediately that the product succeeded by blocking premature commitment.

---

## 10. Wave D — Visual system and tables

### Ticket RPT-009

- `Priority`: P0
- `Owner motor(s)`: `motor_018`
- `Primary file(s)`:
  - [motor_018.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py>)
- `Objective`:
  Promote product-native charts and demote legacy financial charts for blocked / low-evidence cases.
- `Required changes`:
  - Make these charts mandatory for blocked cases:
    - `Asset Context Completeness`
    - `Investment Uncertainty Map`
    - `Minimum Evidence Pack`
    - `Validation Unlock Map`
    - `Decision Front Status`
    - `Scenario Space`
  - Keep revenue, debt, and LL97 charts appendix-only unless report class and jurisdiction justify them.
  - Make chart eligibility depend on `report_identity_state` and `asset_context_readiness`.
- `Dependencies`:
  - `RPT-001`
  - `RPT-005`
- `Acceptance criteria`:
  - The visual center of gravity becomes asset uncertainty and required evidence, not issuer finance.

### Ticket RPT-010

- `Priority`: P1
- `Owner motor(s)`: `motor_015`, `motor_018`
- `Primary file(s)`:
  - [motor_015.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_015.py>)
  - [motor_018.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py>)
- `Objective`:
  Add canonical product tables as structured outputs instead of prose-only sections.
- `Required changes`:
  - Define canonical table schemas for:
    - `Investment Uncertainty Map`
    - `Minimum Evidence Pack`
    - `Scenario Space`
    - `Asset Context Readiness`
    - `Decision Fronts`
    - `Financial Exposure Under Uncertainty`
    - `Regulatory Screening`
- `Dependencies`:
  - `RPT-004`
  - `RPT-009`
- `Acceptance criteria`:
  - Each of those sections exists as a structured object that can render as both table and chart.

---

## 11. Wave E — Governance and export guards

### Ticket RPT-011

- `Priority`: P0
- `Owner motor(s)`: `motor_024`
- `Primary file(s)`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- `Objective`:
  Add product-specific governance checks before export.
- `Required changes`:
  - Add events for:
    - `instruction_leakage_detected`
    - `empty_field_misrepresented`
    - `deficit_score_inconsistency`
    - `issuer_dominance_in_report`
    - `mandatory_section_missing`
    - `context_contamination_detected`
  - Distinguish:
    - source quality gate
    - subject gate
    - asset context gate
    - report product gate
- `Dependencies`:
  - `RPT-005`
  - `RPT-007`
  - `RPT-009`
- `Acceptance criteria`:
  - Governance can fail the report even when runtime execution succeeded.

### Ticket RPT-012

- `Priority`: P0
- `Owner motor(s)`: `motor_025`
- `Primary file(s)`:
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- `Objective`:
  Make publication ceiling enforce the product class and evidence strength.
- `Required changes`:
  - Degrade or hold publication when:
    - report identity exceeds allowed class,
    - mandatory sections are absent,
    - empty fields are presented as facts,
    - contamination exists,
    - issuer-dominant context visually outranks asset truth.
  - Add explicit deliverable restrictions:
    - `do_not_use_for_investment_recommendation`
    - `do_not_use_for_compliance_conclusion`
    - `do_not_use_for_savings_estimate`
- `Dependencies`:
  - `RPT-011`
- `Acceptance criteria`:
  - The system cannot export a misleading report just because motors finished.

### Ticket RPT-013

- `Priority`: P0
- `Owner motor(s)`: `motor_027`
- `Primary file(s)`:
  - [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
- `Objective`:
  Add preflight export enforcement and correct document naming.
- `Required changes`:
  - Block export if contamination is detected.
  - Block export if report identity and filename diverge.
  - Export manifest must include:
    - `report_identity_state`
    - `decision_block_state`
    - `primary_block_reason`
    - `allowed_use`
    - `prohibited_use`
  - Ensure EN and ES variants preserve the same report class.
- `Dependencies`:
  - `RPT-011`
  - `RPT-012`
- `Acceptance criteria`:
  - No PDF ships with the wrong document type or contaminated case identity.

---

## 12. Wave F — Upstream evidence seeds and data hygiene

### Ticket RPT-014

- `Priority`: P1
- `Owner motor(s)`: `motor_012`
- `Primary file(s)`:
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- `Objective`:
  Make Fase 1 produce product-ready evidence seeds instead of generic facility prior only.
- `Required changes`:
  - Add:
    - `investment_uncertainty_map_seed`
    - `minimum_evidence_pack_seed`
    - `asset_context_readiness_table_seed`
    - `financial_boundary_seed`
    - `regulatory_screening_seed`
  - Ensure `missing_physical_observables_register` maps directly into evidence requests.
- `Dependencies`:
  - asset-first and subject admissibility changes already implemented
- `Acceptance criteria`:
  - The product can state exact missing evidence from `motor_012` outputs, not from prose inference alone.

### Ticket RPT-015

- `Priority`: P1
- `Owner motor(s)`: `motor_028`
- `Primary file(s)`:
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- `Objective`:
  Convert discovery into seller/operator evidence request intelligence.
- `Required changes`:
  - Add `requestable_evidence_items`.
  - Tag each missing item with:
    - likely owner
    - likely source
    - why needed
    - which decision front it unlocks
  - Preserve distinction between:
    - public evidence consulted
    - private evidence requested
- `Dependencies`:
  - `RPT-014`
- `Acceptance criteria`:
  - The report can produce a concrete data request pack instead of vaguely asking for more diligence.

### Ticket RPT-016

- `Priority`: P1
- `Owner motor(s)`: `motor_005`
- `Primary file(s)`:
  - [motor_005.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_005.py>)
- `Objective`:
  Stop empty or placeholder values from masquerading as measurements.
- `Required changes`:
  - Normalize to explicit missingness states:
    - `NOT_OBSERVED`
    - `NOT_DECLARED`
    - `BLOCKING_IF_USED`
    - `OUT_OF_SCOPE`
  - Remove silent numeric placeholders where semantics are missing.
- `Dependencies`:
  - none
- `Acceptance criteria`:
  - No report section can print `0 sqft` or equivalent nonsense as if it were a valid observation.

---

## 13. Wave G — Contamination and consistency

### Ticket RPT-017

- `Priority`: P1
- `Owner motor(s)`: `motor_006`
- `Primary file(s)`:
  - [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)
- `Objective`:
  Provide a stable resolved identity surface for contamination scanning.
- `Required changes`:
  - Emit:
    - `resolved_asset_name`
    - `resolved_address`
    - `resolved_jurisdiction`
    - `resolved_rule_scope`
    - `resolved_owner_context`
  - Separate candidate identity from resolved identity clearly.
- `Dependencies`:
  - subject admissibility tranche already implemented
- `Acceptance criteria`:
  - Downstream motors can compare visible report content against resolved case identity.

### Ticket RPT-018

- `Priority`: P1
- `Owner motor(s)`: `motor_022`
- `Primary file(s)`:
  - [motor_022.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_022.py>)
- `Objective`:
  Turn conformance into a product QA layer.
- `Required changes`:
  - Validate:
    - mandatory sections exist
    - section order is valid
    - report class matches state
    - contamination absent
    - empty fields handled correctly
    - instruction leakage absent
    - finance not visually dominant when blocked
- `Dependencies`:
  - `RPT-011`
  - `RPT-013`
- `Acceptance criteria`:
  - The report product has a formal QA pass/fail layer, not just runtime success.

---

## 14. Wave H — Propagation and lineage

### Ticket RPT-019

- `Priority`: P2
- `Owner motor(s)`: `motor_002`, `motor_020`
- `Primary file(s)`:
  - [motor_002.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_002.py>)
  - [motor_020.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_020.py>)
- `Objective`:
  Ensure new report objects re-evaluate correctly when upstream evidence changes.
- `Required changes`:
  - Add lineage for:
    - uncertainty rows
    - evidence pack rows
    - scenario rows
    - decision-front rows
  - Add propagation triggers when:
    - cluster status changes
    - subject admissibility changes
    - regulatory trigger status changes
    - private evidence arrives
- `Dependencies`:
  - `RPT-001`
  - `RPT-014`
- `Acceptance criteria`:
  - New evidence updates report class, scenario plausibility, and TAD without silent drift.

### Ticket RPT-020

- `Priority`: P2
- `Owner motor(s)`: `motor_010`
- `Primary file(s)`:
  - [motor_010.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_010.py>)
- `Objective`:
  Prevent issuer-level facts and benchmark-level facts from being deduped into asset facts.
- `Required changes`:
  - Scope-aware dedupe.
  - Explicit semantic guard between:
    - asset observation
    - benchmark proxy
    - issuer context
- `Dependencies`:
  - `scope_lineage` already in progress elsewhere
- `Acceptance criteria`:
  - No report table can mistake benchmark or issuer context for local asset observation.

---

## 15. Definition of done

This backlog is done only when all of the following are true:

- The report title reflects actual admissibility state.
- The executive brief states what decision is blocked and why.
- `Investment Uncertainty Map` is always present.
- `Minimum Evidence Pack` is always present.
- `Scenario Space` is always present.
- `Decision Fronts` / TAD is concrete and decision-specific.
- Empty critical fields are shown as missing/blocking, not as fake values.
- Finance is subordinated when asset context is weak.
- Issuer context never dominates blocked reports.
- No instruction leakage reaches the artifact.
- Contaminated reports are blocked before export.
- EN and ES variants preserve the same product class and claims.

---

## 16. Suggested implementation tranche

The first implementation tranche should be:

1. `RPT-001`
2. `RPT-004`
3. `RPT-005`
4. `RPT-007`
5. `RPT-009`
6. `RPT-011`
7. `RPT-012`
8. `RPT-013`
9. `RPT-002`

That tranche is the minimum needed to make the artifact look and behave like a product rather than a degraded template.

