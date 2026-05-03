# Runtime Evidence Maturity + NYC Decision Intelligence Execution Backlog

## 1. Purpose

This backlog integrates two strategic prompts into one execution program:

1. a **framework-wide Evidence Maturity & Claim Permission Matrix**
2. a **first production vertical for NYC buildings**

The first prompt defines the constitutional layer:

- every variable must have explicit evidence maturity,
- every claim must obey that maturity,
- and downstream engines must stop overclaiming when variables are weak.

The second prompt defines the first domain pack:

- building assets,
- NYC public datasets,
- stronger screening and scenario outputs,
- bounded ROI,
- bounded compliance,
- and materially better decision-quality reports from public evidence.

This backlog does **not** treat those prompts as separate projects.
The correct architecture is:

`global maturity law -> transversal engine -> domain pack implementation -> downstream enforcement`

---

## 2. Executive Interpretation

## 2.1 What the two prompts are really asking for

The combined ask is not:

- "scrape more NYC pages",
- "add some ROI logic",
- or "make the report look smarter".

It is:

- define a **variable-level epistemic grammar**,
- make that grammar computational,
- and prove it on the first serious public-data vertical: **NYC buildings**.

## 2.2 What already exists in the runtime

The runtime already has useful foundations:

- subject / target admissibility:
  - [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)
  - [motor_001.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py>)
  - [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)
  - [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- scope / source / ingestion discipline:
  - [motor_008.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py>)
  - [motor_010.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_010.py>)
  - [motor_011.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_011.py>)
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- field admissibility and missing evidence:
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- decision and report gating:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
  - [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)

## 2.3 What is still missing

The current runtime still lacks:

- variable-level maturity levels `0-4`,
- claim permission objects,
- decision permission objects,
- explicit ROI admissibility logic by maturity,
- explicit compliance admissibility logic by maturity,
- a first-class `NYC buildings` domain pack,
- and a transversal enforcement engine consumed by downstream motors.

---

## 3. Program Goal

Build a system that can say, deterministically and traceably:

- what variable exists,
- at what maturity level it exists,
- what claim it may support,
- what claim it may not support,
- what report class is admissible,
- what decision front is blocked,
- and what exact evidence would upgrade the case.

This must work:

- globally at the constitutional level,
- concretely in the runtime,
- and first-class for NYC buildings.

---

## 4. Non-Negotiable Design Rules

These rules must never be weakened during implementation:

1. No benchmark may masquerade as local truth.
2. No Level 0-1 variable may support a Level 3-4 claim.
3. No downstream motor may silently upgrade a claim if required variable maturity is insufficient.
4. Variable maturity must be computed per variable, not per document.
5. Derived variables cannot outrun their dependency bottleneck.
6. Missing fields must stay visible as `NOT_OBSERVED`, `REQUIRES_CLIENT_INPUT`, or `BLOCKING_FIELD`.
7. NYC datasets improve maturity only when scope, authority, recency, and address match are valid.
8. Report type must downgrade before the system overclaims.
9. LLM prose may explain maturity. It may not invent it.
10. The first deep domain pack is NYC buildings; all broader domain expansion remains subordinate until that pack is solid.

---

## 5. Architecture Decision

## 5.1 New transversal engine

Create:

- `motor_034 — Evidence Maturity & Claim Permission Engine`

This motor is required because:

- `motor_012` should keep building the public prior,
- `motor_014` should keep building the decision core,
- and the same maturity logic must be consumed by finance, compliance, TAD, governance, reporting, and charts.

## 5.2 New runtime package

Create:

- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/`

Minimum files:

- `__init__.py`
- `levels.py`
- `schemas.py`
- `variable_catalog.py`
- `claim_templates.py`
- `decision_templates.py`
- `dependency_rules.py`
- `domain_packs/__init__.py`
- `domain_packs/nyc_buildings.py`

## 5.3 Primary output objects

`motor_034` must produce:

- `variable_maturity_register`
- `claim_permission_register`
- `decision_permission_register`
- `report_readiness_register`

Secondary supporting objects:

- `variable_dependency_register`
- `maturity_violation_register`
- `domain_pack_resolution`

---

## 6. Context Preservation Strategy

Implementation must avoid loss of context by using these rules:

1. One backlog, one variable catalog, one maturity scale.
2. Documentation changes must precede code changes.
3. The first implementation focus is `NYC buildings`, not global perfection.
4. Every wave closes with:
   - tests,
   - one or more real runs,
   - and an observable artifact or manifest change.
5. No more than 2-4 critical motors should change in the same wave after `motor_034` begins.
6. Golden cases remain stable across the whole program.

Golden cases:

- NYC building with LL84 + PLUTO + DOB
- NYC building with PLUTO but no LL84
- corporate HQ / mailing
- ambiguous address-only target

---

## 7. Workstreams

The program splits into two coupled workstreams:

- `WS-A`: constitutional and transversal maturity architecture
- `WS-B`: NYC buildings domain implementation

They must move in this order:

1. `WS-A constitution`
2. `WS-A schema`
3. `WS-A motor_034`
4. `WS-B NYC routing and datasets`
5. `WS-A downstream enforcement`
6. `WS-B report/product validation`

---

## 8. Wave 0 — Constitutional Freeze

### Objective

Make the maturity law explicit in the framework base before code.

### Files to update

- [0_Phase_0_Master_Document.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/Phases/phase-0/docs/en/0_Phase_0_Master_Document.md>)
- [workflow_rules.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/workflow_rules.md>)
- [quality_rules.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/quality_rules.md>)
- [5_Phase_5_Master_Document.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/Phases/phase-5/docs/en/5_Phase_5_Master_Document.md>)
- [8_Phase_8_Master_Document.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/Phases/phase-8/docs/en/8_Phase_8_Master_Document.md>)
- create [evidence_maturity_claim_permission_matrix.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/evidence_maturity_claim_permission_matrix.md>)

### Required changes

- Add `Variable Evidence Maturity Law`
- Add `Claim Permission Law`
- Add `Variable Semantic Ceiling`
- Add `Source Scope Dependency Rule`
- Add the common maturity scale `L0-L4`
- Add explicit finance and TAD dependencies on variable maturity
- Add the rule that derived variables inherit the weakest required dependency

### Acceptance criteria

- Phase 0 explicitly says that no variable may support a stronger claim than its maturity allows
- Phase 5 explicitly defines maturity-dependent financial output ceilings
- Phase 8 explicitly defines decision bottlenecks in terms of variable maturity
- `workflow_rules.md` explicitly states that outputs must consult `variable_maturity_register`
- `quality_rules.md` explicitly prohibits Level `0-1` variables from supporting strong claims

---

## 9. Wave 1 — Canonical Schema

### Objective

Create the shared technical schema before runtime integration.

### Files to create

- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/__init__.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/levels.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/schemas.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/variable_catalog.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/claim_templates.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/decision_templates.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/dependency_rules.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/domain_packs/nyc_buildings.py`

### Required changes

- Define variable families:
  - identity
  - physical
  - operational
  - energy
  - systems
  - finance
  - regulatory
  - intervention/process
- Define which variables are:
  - observed variables
  - derived variables
- Define maturity metadata fields:
  - source
  - scope
  - authority
  - recency
  - uncertainty reason
  - allowed outputs
  - forbidden outputs
  - upgrade path
  - downgrade path
- Define claim templates:
  - numeric EUI
  - savings claim
  - ROI directional / range / scenario / strong
  - LL97 penalty screening
  - compliance posture
  - process redesign recommendation
- Define decision templates:
  - underwriting
  - retrofit CAPEX
  - compliance investment
  - seller diligence request
  - process redesign

### Acceptance criteria

- The schema cleanly separates variables, claims, and decisions
- The catalog covers the minimum families from the prompts
- The NYC domain pack can override generic maturity rules with NYC-specific upgrades
- No runtime motor is modified yet

---

## 10. Wave 2 — `motor_034` Base Implementation

### Objective

Insert the maturity engine into the runtime without yet rewiring all downstream logic.

### Files to create / update

- create [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- update [adapters/__init__.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/__init__.py>)
- update [motor_dependencies.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_dependencies.json>)
- update [models.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/models.py>)
- update [pipeline_orchestrator.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py>)

### Suggested dependencies

`motor_034` should depend on:

- `motor_007`
- `motor_008`
- `motor_010`
- `motor_011`
- `motor_012`
- `motor_028`

### Required changes

- Build `variable_maturity_register`
- Build `claim_permission_register`
- Build `decision_permission_register`
- Build `report_readiness_register`
- Build `maturity_violation_register`
- Persist those objects in run manifests

### Acceptance criteria

- A run can emit maturity for at least the first NYC-critical variables:
  - `address`
  - `asset_type`
  - `GFA`
  - `year_built`
  - `EUI`
  - `emissions`
  - `tariff`
  - `HVAC_type`
  - `utility_bills`
  - `compliance_filing`
  - `CAPEX`
  - `ROI`
- A run can answer:
  - what maturity level a variable has,
  - why it has that level,
  - what outputs it allows,
  - what outputs it forbids

---

## 11. Wave 3 — NYC Dataset Routing Hardening

### Objective

Turn NYC datasets into a first-class domain pack, not ad hoc source discovery.

### Primary motors

- [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- [motor_008.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py>)

### Required NYC datasets

- LL84
- LL97 applicability / disclosure context
- PLUTO
- DOB permits / filings
- DOF / assessor / parcel / BBL anchors

### Required new objects

- `dataset_coverage_register`
- `nyc_routing_status`
- `dataset_field_coverage_map`

### Required changes

- Force NYC routing when `city=NEW YORK` and `state=NY`
- Make LL84 / PLUTO / DOB attempts mandatory for `OPERATING_ASSET` NYC cases
- Distinguish:
  - dataset found
  - dataset not found
  - dataset not applicable
  - dataset contaminated
  - dataset stale
- Connect dataset rows to variables they may mature

### Acceptance criteria

- Every NYC run includes a dataset coverage table
- The runtime can say which NYC datasets were attempted and why they matter
- NYC datasets improve maturity only when address and scope match

---

## 12. Wave 4 — NYC Variable Maturity Matrix

### Objective

Implement the first deep variable matrix for NYC buildings.

### Primary files

- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/domain_packs/nyc_buildings.py`
- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)

### Required NYC-specific maturity ladders

- `GFA`
  - `L0` not observed
  - `L1` proxy / inferred
  - `L2` listing / brochure
  - `L3` PLUTO / assessor / official public record
  - `L4` verified official / field hardened
- `EUI`
  - `L0` missing
  - `L1` benchmark only
  - `L2` estimated / owner disclosure
  - `L3` LL84
  - `L4` validated normalized baseline
- `emissions`
  - `L0` unknown
  - `L1` proxy
  - `L2` estimated
  - `L3` LL84 / LL97 public record
  - `L4` verified filing
- `tariff`
  - `L0` unknown
  - `L1` regional proxy
  - `L2` estimated rate class
  - `L3` bill-based
  - `L4` contract validated
- `HVAC_type`
  - `L0` unknown
  - `L1` archetype
  - `L2` brochure / listing
  - `L3` engineering / permit / O&M evidence
  - `L4` validated
- `compliance_posture`
  - `L0` inadmissible
  - `L1` rule-family screening
  - `L2` trigger plausible
  - `L3` applicability confirmed
  - `L4` validated / filed

### Acceptance criteria

- NYC building runs show maturity levels specific to public NYC datasets
- `GFA` can reach `L3` via PLUTO
- `EUI` can reach `L3` via LL84
- `compliance_posture` cannot exceed `L2-L3` without filing-grade support

---

## 13. Wave 5 — Claim Permission Engine

### Objective

Convert variable maturity into explicit claim permissions.

### Primary files

- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/claim_templates.py`
- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/dependency_rules.py`
- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)

### Required claim families

- `numeric_eui_claim`
- `energy_savings_claim`
- `roi_directional_claim`
- `roi_range_claim`
- `roi_scenario_claim`
- `roi_strong_bounded_claim`
- `ll97_penalty_screening_claim`
- `compliance_screening_claim`
- `compliance_posture_claim`
- `compliance_closure_claim`
- `process_hypothesis_claim`
- `process_redesign_recommendation_claim`

### Required rules

- If `GFA < L3`, prohibit:
  - numeric EUI
  - area-based LL97 penalty amount
  - area-dependent ROI
- If `EUI < L3`, prohibit:
  - energy savings claim
  - strong energy baseline claims
- If `utility_bills < L3`, prohibit:
  - numeric ROI stronger than directional / low-confidence range
- If `CAPEX = L1`, allow:
  - directional economics only
  - prohibit investment-grade ROI
- If `compliance_trigger = L1-L2`, allow:
  - screening
  - prohibit closure
- If `throughput = L0`, prohibit:
  - process redesign recommendation

### Acceptance criteria

- Claim permissions are explicit and machine-readable
- Derived claims cannot exceed the weakest dependency level
- At least one blocked claim per weak NYC case is traceably explained

---

## 14. Wave 6 — Decision Permission Engine

### Objective

Make TAD and decision fronts obey variable bottlenecks.

### Primary files

- `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/decision_templates.py`
- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)

### Required decision fronts

- acquisition underwriting
- retrofit CAPEX
- compliance investment
- energy performance claim
- refinancing / lending
- process redesign
- seller diligence request

### Required changes

- `motor_034` must emit `decision_permission_register`
- `motor_014` must use decision bottlenecks when ranking blocked fronts
- `motor_033` must surface the current variable bottleneck explicitly

### Acceptance criteria

- Each decision front can state:
  - admissibility state
  - blocking variable(s)
  - evidence needed
  - allowed action
- TAD stops behaving as a generic action queue

---

## 15. Wave 7 — Finance and Compliance Enforcement

### Objective

Make Phase 5 and Phase 6 logic obey maturity, not narrative style.

### Primary motors

- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)

### Required finance ladder

- `ROI L0` -> no ROI
- `ROI L1` -> directional economics only
- `ROI L2` -> preliminary ROI range
- `ROI L3` -> scenario-based ROI
- `ROI L4` -> strong bounded ROI

### Required compliance ladder

- `L0` -> not admissible
- `L1` -> screening only
- `L2` -> trigger plausible
- `L3` -> applicability confirmed / preliminary posture
- `L4` -> validated / filed

### Acceptance criteria

- No report can emit stronger finance or compliance language than the variable bottleneck allows
- Governance can block reports that violate maturity-based claim ceilings

---

## 16. Wave 8 — Reporting and Product Surface

### Objective

Expose maturity visibly in the report and dashboard.

### Primary files

- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_018.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py>)
- [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
- [dashboard.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py>)

### Required surfaces

- `Variable Maturity Highlights`
- `ROI Admissibility`
- `Regulatory Admissibility`
- `Decision Bottleneck Variables`
- `Minimum Evidence to Upgrade Key Variables`

### Acceptance criteria

- Readers can see why a claim is weak or strong
- The dashboard can show maturity and blocked claims without reading raw artifacts
- Charts do not render numeric confidence theater when maturity is low

---

## 17. Wave 9 — NYC Certification

### Objective

Certify the first full domain pack.

### Required golden cases

1. NYC building with LL84 + PLUTO + DOB
2. NYC building with PLUTO but no LL84
3. NYC HQ / non-asset address
4. NYC ambiguous asset candidate

### Required outputs per case

- target classification
- dataset coverage register
- variable maturity register
- claim permission register
- decision permission register
- report readiness register
- report type
- EN/ES report

### Acceptance criteria

- LL84 case can produce:
  - strong EUI maturity
  - bounded scenario economics
  - stronger compliance screening
- no-LL84 case can still produce:
  - useful uncertainty map
  - minimum evidence pack
  - bounded directional economics only
- HQ / ambiguous cases must downgrade cleanly before technical asset reporting

---

## 18. Test Backlog

### TM-001 — Missing GFA

- If `GFA = L0`:
  - prohibit numeric EUI
  - prohibit LL97 penalty amount
  - prohibit numeric ROI dependent on area

### TM-002 — Benchmark-only EUI

- If `EUI = L1`:
  - allow scenario screening
  - prohibit savings claim

### TM-003 — Utility bills available

- If `utility_bills = L3` and `CAPEX/control boundary` are sufficient:
  - allow preliminary baseline
  - allow ROI range / scenario

### TM-004 — CAPEX benchmark only

- If `CAPEX = L1`:
  - allow directional economics
  - prohibit investment-grade ROI

### TM-005 — Compliance trigger plausible only

- If `compliance_trigger = L1-L2`:
  - allow screening
  - prohibit compliance conclusion

### TM-006 — Process change without throughput

- If `throughput = L0`:
  - prohibit process redesign recommendation
  - allow process hypothesis only

### TM-007 — NYC with LL84

- If LL84 record is valid and matched:
  - `EUI >= L3`
  - emissions maturity upgraded
  - benchmark no longer sovereign

### TM-008 — NYC without LL84

- If PLUTO exists but LL84 missing:
  - `GFA` may reach `L3`
  - `EUI` must remain below `L3`
  - report may not overclaim consumption

### TM-009 — HQ or mailing

- Must prohibit technical asset report
- Must produce classification brief

---

## 19. Suggested Execution Order

Strict order:

1. Wave 0
2. Wave 1
3. Wave 2
4. Wave 3
5. Wave 4
6. Wave 5
7. Wave 6
8. Wave 7
9. Wave 8
10. Wave 9

Do not start:

- ROI enforcement,
- compliance enforcement,
- or NYC product polishing

before `motor_034` exists and the NYC variable ladders are defined.

---

## 20. Definition of Done

This program is done only when:

- the constitutional documents explicitly govern maturity and claim permissions,
- `motor_034` exists and runs,
- NYC building variables mature correctly from public datasets,
- claims are machine-blocked when variable maturity is weak,
- TAD surfaces variable bottlenecks explicitly,
- reports show maturity and upgrade paths visibly,
- governance blocks maturity violations,
- and golden NYC cases certify the full chain.

At that point, ZLab can truthfully say:

`With public evidence only, the system can produce a bounded decision brief that identifies what is known, what is not known, what can be claimed, and what evidence would materially change the decision.`
