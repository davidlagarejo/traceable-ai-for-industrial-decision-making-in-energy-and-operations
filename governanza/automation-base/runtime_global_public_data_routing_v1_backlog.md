# Global Public Data Routing System (USA) v1

## Status

This backlog converts existing runtime components into a unified `Global Public Data Routing System (USA) v1`.

This is **not** a greenfield rewrite.
It is a structured reorganization of logic that already exists across:

- `motor_001`
- `motor_006`
- `motor_007`
- `motor_008`
- `motor_012`
- `motor_024`
- `motor_025`
- `motor_027`
- `motor_028`
- `motor_034`

The main architectural addition is:

- `motor_035 — Global Public Data Routing Engine`

This new motor becomes the sovereign routing layer between:

- target classification,
- jurisdiction resolution,
- asset-type routing,
- source selection,
- evidence gating,
- and report-type switching.

---

## Executive Decision

The correct implementation strategy is:

1. preserve the current subject admissibility and evidence maturity foundations;
2. extract routing logic out of `motor_028` into a new `motor_035`;
3. formalize USA routing tables and jurisdiction packs;
4. force `motor_028` to obey `motor_035`;
5. wire the downstream governance and report layers to the routing output.

This avoids:

- duplicate routing logic,
- source chaos,
- jurisdiction confusion,
- and hidden source substitution.

---

## What Already Exists

### Reuse As-Is

- `motor_001`
  - intake contract hardening
  - early ingestion admissibility
- `motor_006`
  - subject / asset resolution signals
- `motor_007`
  - target classification gate
  - report-type switching base
- `motor_008`
  - source register and scope/authority scaffolding
- `motor_012`
  - asset field register
  - missing evidence register
  - compliance applicability case
- `motor_024`
  - governance validation
  - contamination / strength / ceiling checks
- `motor_025`
  - publication hold/degrade enforcement
- `motor_027`
  - final package / export control
- `motor_034`
  - variable maturity / claim permission / decision permission / readiness

### Reuse But Reposition

- `motor_028`
  - keep as discovery execution layer
  - remove sovereignty over source choice
  - make it consume a routing plan

### Add New

- `motor_035`
  - target route synthesis
  - jurisdiction resolver
  - asset type router
  - source routing engine
  - critical field contract
  - disallowed substitution policy

---

## Target System

The final system should transform:

`address + asset_type + decision_type`

into:

- `target_classification_result`
- `jurisdiction_resolution`
- `asset_type_route`
- `mandatory_sources`
- `high_priority_sources`
- `optional_sources`
- `disallowed_substitutions`
- `critical_field_contract`
- `evidence_gating_plan`
- `report_type_switch_recommendation`

---

## Module Layout

Create:

- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/__init__.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/schemas.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/target_taxonomy.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/jurisdiction_resolver.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/asset_type_router.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/critical_fields.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/source_registry.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/routing_engine.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/contamination_rules.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/report_switching.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/us_layers/national.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/us_layers/nyc.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/us_layers/california.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/us_layers/texas.py`
- `runtime-orchestrator/src/runtime_orchestrator/public_data_routing/us_layers/industrial_cross_state.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py`

Also create:

- `governanza/automation-base/us_public_data_routing_matrix.md`
- `governanza/automation-base/us_public_data_routing_matrix.json`

---

## Wave 0 — Constitutional Freeze

### Goal

Make routing-before-scraping part of framework law.

### Files

- `Phases/phase-0/docs/en/0_Phase_0_Master_Document.md`
- `governanza/automation-base/workflow_rules.md`
- `governanza/automation-base/quality_rules.md`

### Required Additions

- `Public Data Routing Law`
- `Canonical Structured Source Priority Law`
- `Jurisdiction-First Routing Rule`
- `Disallowed Substitution Rule`
- `No Technical Scraping Before Asset-Type and Jurisdiction Routing`

### Acceptance

- no motor may perform technical discovery before routing eligibility exists.

---

## Wave 1 — Canonical Schemas

### Goal

Create the data contract for the routing system.

### Files

- `public_data_routing/schemas.py`
- `public_data_routing/target_taxonomy.py`
- `public_data_routing/critical_fields.py`

### Objects

- `TargetClassificationResult`
- `JurisdictionResolution`
- `AssetTypeRoute`
- `SourceRoutingEntry`
- `SourceRoutingPlan`
- `CriticalFieldRequirement`
- `EvidenceGatingPlan`
- `ReportTypeSwitchRecommendation`

### Acceptance

- every required output in the prompt has a stable schema.

---

## Wave 2 — USA Source Registry v1

### Goal

Build the master routing table.

### Files

- `public_data_routing/source_registry.py`
- `public_data_routing/us_layers/national.py`
- `public_data_routing/us_layers/nyc.py`
- `public_data_routing/us_layers/california.py`
- `public_data_routing/us_layers/texas.py`
- `public_data_routing/us_layers/industrial_cross_state.py`
- `governanza/automation-base/us_public_data_routing_matrix.md`
- `governanza/automation-base/us_public_data_routing_matrix.json`

### Minimum Coverage

#### National

- `EPA_GHGRP`
- `EIA_MECS`
- `DOE_IAC`
- `OpenEI_Industrial_Combustion`
- `ENERGY_STAR`
- `SEC_EDGAR`
- `Federal IRA / macro program layer`

#### NYC

- `NYC_LL84`
- `NYC_LL97_CBL`
- `NYC_DOF_BBL`
- `NYC_DOB`
- optional `NYC_Accelerator`
- optional `ENERGY_STAR_public_profile`
- rule: `CBECS` cannot substitute for `LL84 EUI`

#### California

- `CEC benchmarking`
- `Title 24`
- `CALGreen`
- `CPUC / utility tariff context`
- city packs for:
  - `San Francisco`
  - `Los Angeles`
  - `Berkeley`
  - `San Jose`
- utilities:
  - `PG&E`
  - `SCE`
  - `SDG&E`

#### Texas

- `ERCOT`
- `TCEQ`
- county appraisal districts
- city permits

#### Industrial Cross-State

- `EPA_GHGRP`
- `CARB / CalEPA`
- `TCEQ`
- state environmental agency slots

### Acceptance

- every `(jurisdiction + asset_type)` route returns:
  - `mandatory_sources`
  - `high_priority_sources`
  - `optional_sources`
  - `disallowed_substitutions`

---

## Wave 3 — Reuse Existing Classification Layer

### Goal

Normalize existing target admissibility logic into the new routing vocabulary.

### Existing Modules Reused

- `motor_001`
- `motor_006`
- `motor_007`

### Required Mapping

- current `CORPORATE_HEADQUARTERS`, `REGISTERED_AGENT_OR_MAILING_ADDRESS`, `AMBIGUOUS_TARGET` outputs remain valid
- add explicit mapping from current `target_type_classification` outputs into:
  - `OPERATING_ASSET`
  - `CORPORATE_HEADQUARTERS`
  - `MAILING_ADDRESS`
  - `PORTFOLIO_ENTITY`
  - `PROPERTY_LISTING`
  - `INDUSTRIAL_FACILITY`
  - `DATA_CENTER`
  - `AMBIGUOUS_TARGET`
  - `INVALID_TARGET`

### Acceptance

- HQ / mailing / ambiguous / invalid are blocked before technical routing.

---

## Wave 4 — Build `motor_035`

### Goal

Create the sovereign routing motor.

### File

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py`

### Inputs

- `motor_001`
- `motor_006`
- `motor_007`

### Outputs

- `target_classification_result`
- `jurisdiction_resolution`
- `asset_type_route`
- `source_routing_plan`
- `critical_field_contract`
- `evidence_gating_plan`
- `report_type_switch_recommendation`
- `routing_governance_notes`

### Rules

- if target is not `OPERATING_ASSET` or `INDUSTRIAL_FACILITY`, technical routing stops
- if jurisdiction is unresolved, route falls back to minimum bounded path
- routing must be deterministic and table-driven

### Acceptance

- `motor_035` can fully explain what should be searched before `motor_028` runs.

---

## Wave 5 — Make `motor_028` Obey `motor_035`

### Goal

Convert discovery from sovereign to obedient.

### Files

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `governanza/automation-base/motor_dependencies.json`

### Changes

- `motor_028` consumes:
  - `mandatory_sources`
  - `high_priority_sources`
  - `optional_sources`
  - `disallowed_substitutions`
- `motor_028` no longer decides source order on its own for covered USA routes
- web search becomes optional / fallback only
- structured public datasets must run before weak sources

### Acceptance

- no generic scraping occurs before canonical source attempts.

---

## Wave 6 — Jurisdiction Resolver

### Goal

Make USA jurisdiction routing explicit and reusable.

### Files

- `public_data_routing/jurisdiction_resolver.py`
- maybe targeted helper reuse from current `motor_028`

### Output Requirements

- `state`
- `city`
- `county`
- `utility_territory`
- `climate_zone`
- `regulatory_stack`
- `jurisdiction_class`

### Acceptance

- example output for `San Francisco`, `NYC`, `Houston` is deterministic and sourceable.

---

## Wave 7 — Asset Type Router

### Goal

Change routing strategy by asset family.

### Files

- `public_data_routing/asset_type_router.py`
- `public_data_routing/critical_fields.py`

### Required Types

- `commercial_building`
- `multifamily`
- `industrial_facility`
- `warehouse_logistics`
- `data_center`

### Required Deliverables

- per type:
  - critical field set
  - routing emphasis
  - forbidden substitutions
  - minimum reportable evidence

### Acceptance

- the system routes differently for `warehouse` vs `data_center` vs `industrial`.

---

## Wave 8 — Evidence Gating Integration

### Goal

Make routing affect admissibility, not just discovery.

### Existing Modules Reused

- `motor_012`
- `motor_024`
- `motor_025`
- `motor_027`

### Required Changes

- `motor_012` consumes `critical_field_contract`
- `motor_024` audits missing-field and substitution violations
- `motor_025` blocks publication if routing/governance fails
- `motor_027` surfaces routing + gating in the export package

### Rule

- if more than `3` critical fields are missing:
  - `report_type = Decision-Blocked`

### Acceptance

- gating is visibly linked to routed critical fields.

---

## Wave 9 — Contamination Guard Integration

### Goal

Block cross-context contamination inside the routing system itself.

### Files

- `public_data_routing/contamination_rules.py`
- `motor_024`
- `motor_027`

### Must Detect

- wrong address
- wrong city
- wrong owner
- wrong regulation
- mixed assets
- template placeholders

### Acceptance

- if contamination is high, report generation is blocked.

---

## Wave 10 — Report Switching Integration

### Goal

Unify report switching under routing + evidence gates.

### Existing Modules Reused

- `motor_007`
- `motor_016`
- `motor_025`
- `motor_027`

### Required Logic

- `target_type != OPERATING_ASSET/INDUSTRIAL_FACILITY`:
  - `Target Classification Brief`
- `asset_context_insufficient`:
  - `Decision-Blocked Brief`
- `partial_data`:
  - `Minimum Evidence Report`
- `sufficient_data`:
  - `Full Technical Report`

### Acceptance

- routing, not prose, decides the ceiling.

---

## Wave 11 — API and Report Exposure

### Goal

Make routing visible to users and downstream systems.

### Files

- `dashboard.py`
- `cli.py`
- `motor_016`

### Show

- target classification
- jurisdiction resolution
- source routing plan
- mandatory sources attempted
- optional sources skipped
- prohibited substitutions
- critical fields missing
- routing reason for report type

### Acceptance

- users can see why the system searched where it searched.

---

## Wave 12 — Certification

### Goal

Prove the routing system works.

### Mandatory Cases

1. NYC building with LL84
2. NYC building without LL84
3. HQ
4. ambiguous
5. `PIER 1 BAY 1, San Francisco, CA / Prologis`

### Prologis Expected Result

- target classified as `CORPORATE_HEADQUARTERS` or `AMBIGUOUS_TARGET`
- no technical report
- `Target Classification Brief`
- no energy / HVAC / retrofit analysis

### Acceptance

- all five cases pass in tests and live runs.

---

## Existing-to-New Mapping

| Existing Piece | New System Role |
|---|---|
| `motor_001` | intake admissibility pre-gate |
| `motor_006` | physical anchor and subject resolution signals |
| `motor_007` | target classification gate + report switching base |
| `motor_008` | source register and scope metadata |
| `motor_028` | discovery executor only |
| `motor_012` | field register and gating consumer |
| `motor_024` | routing/governance auditor |
| `motor_025` | publication blocker |
| `motor_027` | final export surface |
| `motor_034` | variable maturity / claim permission after routing |
| `motor_035` | new sovereign public data routing engine |

---

## Rules That Must Never Be Weakened

- no technical scraping before target classification
- no technical scraping before jurisdiction routing
- no entity-level substitution for asset-level truth
- no benchmark as local truth where local public record exists
- no report upgrade when critical fields are missing
- no contamination tolerance for final report generation
- structured canonical datasets first, weak web sources later
- always degrade before assuming

---

## Definition of Done

This system is done when:

- `motor_035` exists and is in the DAG
- `motor_028` obeys `motor_035`
- NYC / California / Texas / industrial cross-state routing tables exist
- mandatory vs optional vs prohibited substitution is explicit
- critical field gating is tied to routing
- report switching is tied to routing + evidence
- contamination blocks export
- `Prologis / Pier 1 Bay 1` degrades correctly
- live cases and tests certify the system

---

## Immediate First Tranche

Execute next in this exact order:

1. `Wave 0`
2. `Wave 1`
3. `Wave 2`
4. `Wave 4`
5. `Wave 5`

That sequence yields the first usable version fastest:

- constitutional freeze
- schema
- registry
- `motor_035`
- obedience wiring into `motor_028`

