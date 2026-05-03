# Runtime Scraping Admissibility Redesign Backlog

## 1. Purpose

This backlog redesigns scraping as an **admissibility layer**, not a volume crawler.

The goal is not:

- to find more pages,
- to maximize source count,
- or to populate more fields by force.

The goal is:

- to decide whether the target is a real evaluable operating asset,
- to separate asset truth from issuer context,
- to admit only evidence with usable authority and scope,
- to reject contamination early,
- and to produce a bounded evidence pack that can feed the framework without fabrication.

This document complements:

- [runtime_asset_first_hardening_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_asset_first_hardening_backlog.md>)
- [runtime_subject_admissibility_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_subject_admissibility_backlog.md>)
- [runtime_decision_admissibility_report_ticket_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_decision_admissibility_report_ticket_backlog.md>)

Those backlogs harden subject admission and final reporting.
This backlog hardens the **web intelligence and public-ingestion spine**.

---

## 2. Executive Diagnosis

### Final classification

The current problem is:

`E) all of the above`

But the order of causality matters:

1. `B) bad entity resolution`
2. `C) weak source filtering`
3. `D) missing report-type switching at scraping time`
4. `A) insufficient scraping architecture`

### Practical failure mode

Today the runtime already has meaningful subject and report gates, mainly in:

- [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)
- [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)
- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)

But the discovery layer still has structural weaknesses:

- [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>) still mixes identity confirmation and broad discovery.
- SEC remains in the primary contract, which is wrong for asset identity.
- [motor_008.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py>) is still too thin on scope, authority, recency, and rejection logic.
- [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>) still builds priors before a strict field-admissibility layer exists.
- [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>) and [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>) govern well, but too late in the ingestion path.

### Core breach

The system can still perform:

`subject candidate -> partial discovery -> prior construction -> product downgrade`

when the correct order must be:

`subject candidate -> asset identity gate -> scope separation gate -> contamination guard -> field admissibility -> only then prior construction`

---

## 3. Governing Principles

### 3.1 Mother rule

`NO SCRAPE FOR CONTENT UNTIL THE TARGET HAS BEEN CLASSIFIED.`

### 3.2 Asset precedence

If the target is intended as an asset case, only `ASSET_LEVEL` evidence may populate asset-critical fields.

### 3.3 Conservative rejection

Reject more than you accept.
Prefer `NOT_OBSERVED` to weak inference.

### 3.4 No substitution rule

`ENTITY_LEVEL`, `PORTFOLIO_LEVEL`, `JURISDICTION_LEVEL`, and `BENCHMARK_LEVEL` may contextualize.
They may not fill missing `ASSET_LEVEL` fields.

### 3.5 Contamination blocks asset truth

If contamination risk is high, the source must be rejected for asset-level use and optionally preserved only in `discarded_source_log`.

### 3.6 Missing data is not failure

Missing data must become:

- `NOT_OBSERVED`
- `NOT_PUBLICLY_AVAILABLE`
- `REQUIRES_CLIENT_INPUT`
- `BLOCKING_FIELD`

Never:

- `0`
- blank
- `unspecified`
- implicit default

---

## 4. Target Classification Taxonomy

Every target must classify first into one of these:

- `OPERATING_ASSET`
- `CORPORATE_HEADQUARTERS`
- `REGISTERED_AGENT_OR_MAILING_ADDRESS`
- `PORTFOLIO_ENTITY`
- `PROPERTY_LISTING`
- `REGULATORY_ENTITY`
- `AMBIGUOUS_TARGET`
- `INVALID_TARGET`

This taxonomy must coexist with, and extend, the current runtime subject model:

- `issuer`
- `address_candidate`
- `site_candidate`
- `asset_candidate`
- `bounded_asset`

Mapping rule:

- `subject_kind` remains the runtime contract object.
- `target_type_classification` becomes the public-ingestion verdict.

---

## 5. New Ingestion Architecture

## 5.1 Layer A — Subject Contract Layer

**Current owners**

- [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)
- [motor_001.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py>)
- [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)

**Role**

- declare the intended subject,
- anchor the case physically if possible,
- refuse silent promotion from company to asset.

## 5.2 Layer B — Asset Identity Gate

**Current owner to harden**

- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)

**Role**

- decide if the target is really an operating asset,
- decide whether discovery may continue beyond identity confirmation.

## 5.3 Layer C — Scope-Separated Source Intake

**Current owners to rebuild**

- [motor_008.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py>)
- [motor_010.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_010.py>)
- [motor_011.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_011.py>)

**Role**

- register every source,
- classify scope,
- score authority,
- track rejection reasons.

## 5.4 Layer D — Search Rounds

**Primary owner**

- [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)

**Role**

- run targeted rounds in order,
- stop when the identity gate fails,
- stop before technical scraping if the target is not an operating asset.

## 5.5 Layer E — Field Admissibility

**Primary owners**

- [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)

**Role**

- materialize only admissible fields,
- convert missing fields into explicit evidence requests,
- feed priors without invention.

## 5.6 Layer F — Governance and Delivery Guard

**Current owners**

- [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)

**Role**

- reject contamination,
- reject invalid report type,
- block export when ingest output violates admissibility.

---

## 6. Gates

## 6.1 Gate 1 — Asset Identity Gate

### Objective

Answer:

- Is the target a physical operating asset?
- Is the address operational, administrative, or ambiguous?
- Is there asset-level public evidence at all?

### Output object

`target_classification_object`

Required fields:

- `target_type`
- `classification_confidence`
- `asset_identity_status`
- `reason`
- `supporting_sources`
- `rejected_sources`

### Required evidence to pass as `OPERATING_ASSET`

At least one strong physical anchor plus corroboration:

- assessor / parcel / property record
- official benchmark record
- permit record
- registry record
- official property page with address match
- technical brochure with address and asset-type match

### Hard rule

If:

- `target_type != OPERATING_ASSET`
- and `asset_level_evidence_found = false`

Then:

- prohibit technical report generation
- recommend:
  - `Target Classification Brief`
  - `Decision-Blocked Address Brief`
  - or `Entity Address Classification Brief`

## 6.2 Gate 2 — Scope Separation Gate

### Scopes

- `ASSET_LEVEL`
- `ENTITY_LEVEL`
- `PORTFOLIO_LEVEL`
- `JURISDICTION_LEVEL`
- `BENCHMARK_LEVEL`

### Hard rule

Only `ASSET_LEVEL` may populate:

- `GFA`
- `floor_count`
- `year_built`
- `fuel`
- `HVAC`
- `utility`
- `EUI`
- `tenant_control_boundary`
- `systems`
- `asset compliance filing`

All other scopes may only add context.

## 6.3 Gate 3 — Contamination Guard

### Match requirements

Each accepted source must be validated against:

- address
- city
- state
- owner/entity
- jurisdiction
- property name
- asset class

### Rejection flag

If mismatch is material:

- `CONTEXT_CONTAMINATION_RISK`

### Hard rule

`high contamination risk -> reject for asset-level use`

## 6.4 Gate 4 — Source Authority Scoring

### Authority classes

- `high`
- `medium`
- `low`

### Hard rule

`low-authority` sources cannot support high-weight claims.

## 6.5 Gate 5 — Field Admissibility Matrix

### Admissibility states

- `CONFIRMED_ASSET_LEVEL`
- `OBSERVED_PUBLIC_ASSET_LEVEL`
- `INFERRED_ASSET_LEVEL`
- `ENTITY_CONTEXT_ONLY`
- `PORTFOLIO_CONTEXT_ONLY`
- `JURISDICTION_CONTEXT_ONLY`
- `BENCHMARK_ONLY`
- `NOT_OBSERVED`
- `NOT_PUBLICLY_AVAILABLE`
- `REQUIRES_CLIENT_INPUT`
- `BLOCKING_FIELD`
- `REJECTED_CONTAMINATION`

### Hard rule

No critical field may render as blank, `0`, `null`, or `unspecified`.

---

## 7. Search Strategy by Round

## Round 1 — Identity Confirmation

### Objective

Confirm whether the target is an evaluable operating asset.

### Query families

- `[address] property record`
- `[address] assessor`
- `[address] parcel`
- `[address] building`
- `[address] owner`
- `[address] property brochure`
- `[address] ENERGY STAR`
- `[address] benchmarking`

### Stop condition

If identity remains ambiguous:

- do not proceed to energy, HVAC, compliance, finance, or benchmarks

## Round 2 — Asset Physical Substrate

### Objective

Populate minimum physical clusters.

### Query families

- `[address] gross floor area`
- `[address] square feet`
- `[address] year built`
- `[address] HVAC`
- `[address] permits`
- `[address] tenant`
- `[address] property brochure PDF`

## Round 3 — Energy / Utility / Compliance

### Objective

Find asset-level energy and compliance evidence.

### Query families

- `[address] energy benchmarking`
- `[address] EUI`
- `[address] ENERGY STAR score`
- `[address] building emissions`
- `[address] compliance report`
- `[address] utility`

## Round 4 — Owner / Issuer Context

### Objective

Add issuer context only after the asset is classified.

### Query families

- `[owner] SEC filings`
- `[owner] annual report`
- `[owner] sustainability report`
- `[owner] debt schedule`

## Round 5 — Benchmarks

### Objective

Route only after asset class is confirmed.

### Query families

- `CBECS`
- `DOE`
- `ASHRAE`
- sector benchmark
- climate adjustment

---

## 8. Report-Type Switching Logic

The ingestion layer must emit `report_type_recommendation` before Phase 1 prior construction.

- `OPERATING_ASSET + sufficient` -> `Full Technical Decision Intelligence Report`
- `OPERATING_ASSET + partial` -> `Exploratory Prior / Minimum Evidence Report`
- `OPERATING_ASSET + insufficient` -> `Decision-Blocked Asset Brief`
- `CORPORATE_HEADQUARTERS` -> `Entity Address Classification Brief`
- `AMBIGUOUS_TARGET` -> `Target Clarification Brief`
- `INVALID_TARGET` -> no technical asset report

This logic must become enforceable in:

- [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)

---

## 9. Required Structured Outputs

The scraper / ingestion layer must output:

- `target_classification_object`
- `source_register`
- `asset_field_register`
- `missing_evidence_register`
- `contamination_log`
- `report_type_recommendation`

These objects should become first-class runtime artifacts, not transient local variables.

---

## 10. Execution Order

Implementation order is strict:

1. `asset_contracts.py`
2. `motor_001`
3. `motor_006`
4. `motor_007`
5. `motor_008`
6. `motor_028`
7. `motor_010`
8. `motor_011`
9. `motor_012`
10. `motor_014`
11. `motor_024`
12. `motor_025`
13. `motor_027`
14. `tests`

Reason:

- subject and target contract first,
- discovery second,
- field admissibility third,
- governance last.

---

## 11. Ticket Backlog

### SCRAPE-001

- `Priority`: P0
- `Owner`: `asset_contracts.py`
- `Files`:
  - [asset_contracts.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/asset_contracts.py>)
- `Objective`:
  Add the public-ingestion target classification taxonomy alongside the existing subject model.
- `Required changes`:
  - add `target_type_classification`
  - add `asset_identity_status`
  - add `classification_confidence`
  - add `report_type_recommendation` seed
  - extend `subject_kind` bridging so address-only seeds default to ambiguity, not pseudo-asset confidence
- `Acceptance criteria`:
  - an address can remain `AMBIGUOUS_TARGET` without pressure to become `asset`
  - `target_type_classification` is persisted in runtime state

### SCRAPE-002

- `Priority`: P0
- `Owner`: `motor_001`
- `Files`:
  - [motor_001.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py>)
- `Objective`:
  Validate subject and ingestion admissibility separately.
- `Required changes`:
  - emit `ingestion_contract_status`
  - emit `identity_gate_preconditions`
  - emit `prohibited_scrape_rounds`
- `Acceptance criteria`:
  - a bad or ambiguous subject can be stopped before discovery expands

### SCRAPE-003

- `Priority`: P0
- `Owner`: `motor_006`
- `Files`:
  - [motor_006.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py>)
- `Objective`:
  Make address semantics and site-vs-issuer disambiguation a stronger evidence object.
- `Required changes`:
  - add `target_classification_hypothesis`
  - add `issuer_vs_asset_signals`
  - add `physical_anchor_strength`
  - distinguish:
    - `corporate_hq_signal`
    - `mailing_signal`
    - `operating_asset_signal`
- `Acceptance criteria`:
  - HQ-like addresses are explicitly identified as such before motor_028

### SCRAPE-004

- `Priority`: P0
- `Owner`: `motor_007`
- `Files`:
  - [motor_007.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py>)
- `Objective`:
  Turn the current subject gate into a full Asset Identity Gate.
- `Required changes`:
  - emit `target_classification_object`
  - emit `asset_level_evidence_found`
  - emit `issuer_only_evidence_found`
  - emit `technical_substrate_readiness`
  - emit `recommended_report_type`
  - emit `prohibited_report_types`
- `Acceptance criteria`:
  - target classification is explicit before technical scraping
  - `report_type_recommendation` can block technical report generation

### SCRAPE-005

- `Priority`: P0
- `Owner`: `motor_008`
- `Files`:
  - [motor_008.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py>)
- `Objective`:
  Rebuild the source registry around authority, scope, recency, and rejection.
- `Required changes`:
  - add `scope`
  - add `authority_score`
  - add `recency`
  - add `accepted`
  - add `rejection_reason`
  - add `source_family`
  - add `asset_level_eligible`
- `Acceptance criteria`:
  - every source can be audited by authority and scope
  - non-asset sources cannot silently populate asset truth

### SCRAPE-006

- `Priority`: P0
- `Owner`: `motor_028`
- `Files`:
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- `Objective`:
  Replace broad discovery with round-based admissibility scraping.
- `Required changes`:
  - split into rounds 1–5
  - remove SEC from primary identity tier
  - stop after Round 1 if target is not `OPERATING_ASSET`
  - emit `discarded_source_log`
  - emit `contamination_log`
  - emit `identity_evidence_bundle`
- `Acceptance criteria`:
  - discovery does less when identity is weak
  - SEC only appears after asset identity is classified

### SCRAPE-007

- `Priority`: P1
- `Owner`: `motor_010`
- `Files`:
  - [motor_010.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_010.py>)
- `Objective`:
  Prevent de-duplication from merging issuer facts into asset facts.
- `Required changes`:
  - dedupe by `scope + field + source family + jurisdiction`
  - preserve parallel facts when scope differs
- `Acceptance criteria`:
  - `ENTITY_LEVEL GFA-like claim` cannot overwrite an `ASSET_LEVEL` field

### SCRAPE-008

- `Priority`: P1
- `Owner`: `motor_011`
- `Files`:
  - [motor_011.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_011.py>)
- `Objective`:
  Curate evidence objects with explicit epistemic boundaries.
- `Required changes`:
  - add `field_target`
  - add `admissibility_default`
  - add `scope_boundary`
  - add `contamination_sensitivity`
- `Acceptance criteria`:
  - downstream motors can tell if an object is asset-usable or context-only

### SCRAPE-009

- `Priority`: P0
- `Owner`: `motor_012`
- `Files`:
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- `Objective`:
  Build Phase 1 priors only from admissible field objects.
- `Required changes`:
  - add `asset_field_register`
  - add `missing_evidence_register`
  - add `field_admissibility_matrix`
  - block prior inflation when only issuer or benchmark context exists
- `Acceptance criteria`:
  - no facility prior can materialize critical asset fields from issuer context

### SCRAPE-010

- `Priority`: P1
- `Owner`: `motor_014`
- `Files`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- `Objective`:
  Convert missing asset fields into precise evidence requests.
- `Required changes`:
  - consume `missing_evidence_register`
  - enforce `Missing Field / Why It Matters / Decision It Blocks / Minimum Evidence Needed / Suggested Source`
- `Acceptance criteria`:
  - missing data yields evidence requests, not weak fallback narrative

### SCRAPE-011

- `Priority`: P0
- `Owner`: `motor_024`
- `Files`:
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- `Objective`:
  Audit ingestion breaches as first-class governance events.
- `Required changes`:
  - add events:
    - `asset_identity_gate_failed`
    - `scope_separation_breach`
    - `contamination_detected`
    - `low_authority_claim_breach`
    - `asset_field_substitution_attempt`
- `Acceptance criteria`:
  - governance log explains exactly why a source or field was rejected

### SCRAPE-012

- `Priority`: P0
- `Owner`: `motor_025`
- `Files`:
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
- `Objective`:
  Turn ingestion failures into report-type downgrade or publication block.
- `Required changes`:
  - consume `report_type_recommendation`
  - block technical report if target classification forbids it
  - downgrade outputs when critical fields are benchmark-only or entity-only
- `Acceptance criteria`:
  - no technical asset report can escape a failed identity gate

### SCRAPE-013

- `Priority`: P0
- `Owner`: `motor_027`
- `Files`:
  - [motor_027.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py>)
- `Objective`:
  Enforce delivery guard at export time.
- `Required changes`:
  - require `target_classification_object`
  - require `source_register`
  - require `asset_field_register`
  - require `missing_evidence_register`
  - block PDF if contamination is unresolved
- `Acceptance criteria`:
  - the manifest proves why the chosen report type was allowed

### SCRAPE-014

- `Priority`: P0
- `Owner`: `tests`
- `Files`:
  - [test_target_seed_workflow.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_target_seed_workflow.py>)
  - [test_report_conformance.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_report_conformance.py>)
  - new ingestion tests under `tests/`
- `Objective`:
  Freeze the new ingestion behavior with end-to-end conformance.
- `Required changes`:
  - add Prologis / Pier 1 Bay 1 identity test
  - add HQ-address rejection test
  - add contamination rejection test
  - add benchmark-cannot-fill-asset-field test
  - add source-authority claim ceiling test
- `Acceptance criteria`:
  - `PIER 1 BAY 1, SAN FRANCISCO, CA 94111 / Prologis` classifies as `CORPORATE_HEADQUARTERS` or `AMBIGUOUS_TARGET`
  - normal technical report is prohibited for that case

---

## 12. Test Plan

### Golden negative test

Target:

- `PIER 1 BAY 1, SAN FRANCISCO, CA 94111`
- owner: `Prologis`

Expected:

- `target_type = CORPORATE_HEADQUARTERS` or `AMBIGUOUS_TARGET`
- `asset_level_evidence_found = false` or weak
- `issuer_only_evidence_found = true`
- `recommended_report_type = Entity Address Classification Brief` or `Target Clarification Brief`
- `prohibited_report_types` includes technical asset reports
- no EUI, HVAC, GFA, retrofit, or compliance claims attempted

### Positive test families

- commercial building with assessor + benchmark record
- warehouse with brochure + property page + benchmarking record
- industrial facility with permit + operator page
- infrastructure node with topology or substation record
- oil & gas facility with facility registry or permit trail

### Contamination tests

- wrong city source
- wrong jurisdiction source
- wrong owner source
- wrong regulation source
- template leakage source

---

## 13. Likely New Modules

These modules should probably be added under:

`src/runtime_orchestrator/ingestion/`

- `identity_gate.py`
- `source_scoring.py`
- `scope_classification.py`
- `field_admissibility.py`
- `contamination_guard.py`
- `search_rounds.py`
- `schemas.py`

They should remain small and be used by existing motors, not replace the motor architecture.

---

## 14. Rules That Must Never Be Weakened

- A company is not an asset.
- An address is not yet an asset.
- SEC is never asset-physical evidence.
- Portfolio ESG metrics are never asset performance.
- Benchmarks are never local measured truth.
- Low-authority sources cannot support strong claims.
- Missing critical fields must remain visibly missing.
- High contamination blocks asset-level use.
- Failed identity gate prohibits technical report generation.
- The LLM must never fill missing physical fields.

---

## 15. Definition of Done

This backlog is done when:

- identity confirmation runs before technical scraping
- SEC no longer sits in the primary asset identity tier
- every source has scope, authority, recency, accepted/rejected status
- every critical field has admissibility state
- missing fields generate explicit evidence requests
- contamination can block export
- Prologis / Pier 1 Bay 1 no longer produces a normal technical asset report
- the framework produces less evidence volume but better admissibility decisions

