# Runtime System Integrity Consistency Correction Plan

## Status

The framework is materially stronger than before, but it is not yet internally
consistent end-to-end.

The remaining failures are not cosmetic. They are structural conflicts between:

- early asset-context gating
- refined report readiness
- inference activation
- visible report packaging
- governance summaries
- final PDF rendering

This plan closes those conflicts without weakening the framework's conservative
epistemology.

---

## Scope

This plan corrects the inconsistencies still observable in the fresh
`One Vanderbilt` run:

- `run:4c0ba8a8f5f19e1b`
- report type trace says `Compliance / Investment Screening Brief`
- visible executive layers still read like full `Decision-Blocked`
- public source coverage shows strong asset-level geometry support
- operational identity still shows geometry as `NOT OBSERVED`
- governance summary claim counts diverge from the claim matrix
- PDF still compiles non-governed LaTeX template chapters

This is a system-integrity plan, not a writing-improvement plan.

---

## Structural Diagnosis

### Active inconsistency classes

1. `report_type` vs `executive narrative`
2. `public data found` vs `operational identity rendered`
3. `claim matrix` vs `governance summary`
4. `screening-ready clusters` vs `blocking inference core`
5. `approved report package` vs `compiled PDF inventory`
6. `source scope semantics` vs `support note wording`

### Root cause pattern

The dominant failure is:

- refined downstream state exists,
- but legacy upstream state still dominates the visible report.

In practice:

- `motor_007` still dominates too much downstream
- `motor_013` and `motor_014` still activate around stale readiness
- `motor_016` still renders legacy asset-context logic
- `motor_017` still compiles scaffolding beyond the governed package
- `motor_024` still does not validate all cross-motor contradictions

---

## Non-Negotiables

Do not weaken:

- no hallucinated certainty
- no ROI without evidence
- no compliance closure without official filing or verified baseline
- no savings claim without utility, systems, and control-boundary evidence
- no benchmark as local truth
- no LLM narrative overriding structured governance
- no asset-level support claimed from entity-level source scope
- no PDF delivery if package and render inventory diverge

---

## Closure Strategy

The correct fix is:

1. reconcile canonical asset context after public-data execution
2. re-anchor inference and validation logic to that reconciled state
3. make final report identity authoritative for visible narrative
4. make operational identity render from supported fields, not legacy priors
5. add a dedicated consistency validator before PDF generation
6. block template/scaffold leakage at render time

---

## Ticket Format

Each ticket below includes:

- `Priority`
- `Owner motor(s)`
- `Files`
- `Objective`
- `Implementation`
- `Acceptance`

---

## Wave SI-A — Canonical Asset Context Reconciliation

### Ticket SIC-01

- `Priority`: P0
- `Owner motor(s)`: `motor_012`, `motor_034`
- `Files`:
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
  - [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
  - helper module under `runtime_orchestrator/evidence_maturity/`
- `Objective`:
  Create one canonical post-routing asset-context state that reflects
  actual supported fields, not only the early `motor_007` seed.
- `Implementation`:
  - derive:
    - `canonical_asset_context_state`
    - `canonical_missing_clusters`
    - `canonical_supported_field_register`
  - compute them from:
    - `asset_field_register`
    - `cluster_maturity_register`
    - `source_family_coverage_table`
  - preserve early `motor_007` state as historical gate, but stop using it
    as the sole downstream truth once public evidence is reconciled
- `Acceptance`:
  - `One Vanderbilt` canonical geometry is not missing if PLUTO-support rows
    carry `GFA`, `floor_count`, or `year_built`
  - canonical state is exported for downstream motors

---

## Wave SI-B — Inference Re-anchoring

### Ticket SIC-02

- `Priority`: P0
- `Owner motor(s)`: `motor_013`, `motor_014`
- `Files`:
  - [motor_013.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_013.py>)
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- `Objective`:
  Stop activating blocking inference logic from stale readiness when
  canonical public evidence already supports screening.
- `Implementation`:
  - rebase `LC-ASSET-01` and related evidence-gap logic on:
    - `canonical_asset_context_state`
    - `canonical_missing_clusters`
  - split:
    - `identity/geometry resolved but technical verification incomplete`
    - from
    - `identity/geometry genuinely missing`
  - ensure the minimum evidence agenda stops requesting already supported
    geometry/identity fields
- `Acceptance`:
  - `One Vanderbilt` no longer asks first for identity/geometry confirmation
    if those fields are already canonically supported
  - `Wilsonart` remains blocked where canonical support is still weak

---

## Wave SI-C — Final Report Identity Authority

### Ticket SIC-03

- `Priority`: P0
- `Owner motor(s)`: `motor_025`, `motor_016`, `motor_019`
- `Files`:
  - [motor_025.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py>)
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_019.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py>)
- `Objective`:
  Make the final published report identity authoritative for visible
  narrative posture.
- `Implementation`:
  - emit one `canonical_report_state` object from `motor_025`
  - include:
    - `early_gate`
    - `maturity_refinement`
    - `final_published_report_type`
    - `screening_capabilities`
    - `verification_blockers`
  - make `motor_016` and `motor_019` consume this canonical object instead of
    composing visible posture from raw `asset_context_insufficient`
- `Acceptance`:
  - if final type is `Compliance / Investment Screening Brief`,
    executive sections cannot describe total technical blockage
  - narrative may still block ROI, closure, and retrofit recommendation

---

## Wave SI-D — Operational Identity Rendering Authority

### Ticket SIC-04

- `Priority`: P0
- `Owner motor(s)`: `motor_016`, `motor_012`, `motor_028`
- `Files`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
  - [motor_028.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py>)
- `Objective`:
  Make visible operational identity render from supported fields, not from
  legacy prior placeholders.
- `Implementation`:
  - rebuild `C2` from `asset_field_register` and canonical support semantics
  - define precedence:
    - `asset_field_register` supported value
    - then reconciled field
    - then blank
    - never `NOT OBSERVED` if canonically supported
  - fix source-scope note wording so `ENTITY_LEVEL` sources do not claim
    `asset-level support`
- `Acceptance`:
  - `One Vanderbilt` C2 shows populated `GFA`, `floor_count`, `year_built`
    when A6 says those fields were extracted from PLUTO
  - support note language matches actual `Scope`

---

## Wave SI-E — Claim Summary / Governance Consistency

### Ticket SIC-05

- `Priority`: P0
- `Owner motor(s)`: `motor_014`, `motor_016`, `motor_024`
- `Files`:
  - [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- `Objective`:
  Eliminate claim-count divergence between matrix and governance summary.
- `Implementation`:
  - normalize claim summary contract to one schema only:
    - either `allowed/conditional/prohibited`
    - or `allowed_count/conditional_count/prohibited_count`
  - remove cross-motor field-name mismatch
  - add hard preflight:
    - summary counts must equal matrix counts
- `Acceptance`:
  - `A0` and `A5` counts always match exactly
  - PDF blocks on mismatch

---

## Wave SI-F — New System Consistency Validator

### Ticket SIC-06

- `Priority`: P0
- `Owner motor(s)`: new `motor_036`
- `Files`:
  - new [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)
  - [adapters/__init__.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/__init__.py>)
  - [motor_dependencies.json](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/motor_dependencies.json>)
  - [pipeline_orchestrator.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py>)
- `Objective`:
  Add one dedicated validator for inter-motor coherence before render.
- `Implementation`:
  - run after `012/014/016/033/034/025`
  - validate:
    - asset context vs public data found
    - claim summary vs claim matrix
    - report type vs executive posture
    - source coverage vs operational identity
    - decision permissions vs visible narrative
    - missing fields vs available data
  - emit:
    - `consistency_register`
    - `critical_failures`
    - `canonical_report_state`
    - `can_render_pdf`
- `Acceptance`:
  - report rendering blocked when any critical inconsistency exists
  - validator produces exact failing dimension and owner motor

---

## Wave SI-G — Render Inventory Governance

### Ticket SIC-07

- `Priority`: P0
- `Owner motor(s)`: `motor_016`, `motor_017`, `motor_024`
- `Files`:
  - [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
  - [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
  - [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- `Objective`:
  Stop compiling non-governed template chapters into client-facing PDFs.
- `Implementation`:
  - `motor_016` emits `planned_chapter_inventory`
  - `motor_017` only renders approved governed chapters
  - `motor_024` or `motor_036` verifies compiled inventory matches planned
  - block if any of these appear in final inventory:
    - template abstract
    - template intro
    - template user guide
    - template latex tutorial
- `Acceptance`:
  - final PDF inventory equals approved report package inventory
  - no template scaffold chapter survives in final artifacts

---

## Wave SI-H — Tests and Real-Run Closure

### Ticket SIC-08

- `Priority`: P0
- `Owner motor(s)`: tests + certification
- `Files`:
  - new tests under `runtime-orchestrator/tests/`
  - update certification snapshot docs in `governanza/automation-base/`
- `Objective`:
  Freeze these consistency fixes with both unit-level and full-run proof.
- `Implementation`:
  - add tests:
    - `if PLUTO/GFA present -> C2 geometry not missing`
    - `if report_type = screening -> C1 not fully blocked`
    - `if A0 counts != A5 counts -> fail`
    - `if compiled inventory contains template chapters -> fail`
    - `if source scope = ENTITY_LEVEL -> support note cannot say asset-level`
  - rerun:
    - `One Vanderbilt`
    - `Wilsonart`
    - `HQ/mailing`
  - produce updated acceptance artifact
- `Acceptance`:
  - all new tests pass
  - `One Vanderbilt` output is internally coherent end-to-end
  - `Wilsonart` remains correctly blocked
  - `HQ/mailing` remains classification-only

---

## Correct Execution Order

1. `SIC-01` canonical asset-context reconciliation
2. `SIC-02` inference re-anchoring
3. `SIC-03` final report identity authority
4. `SIC-04` operational identity rendering authority
5. `SIC-05` claim/governance count normalization
6. `SIC-06` new consistency validator
7. `SIC-07` render inventory governance
8. `SIC-08` tests and real-run closure

Do not invert this order.

If `motor_036` is added before `SIC-01` to `SIC-05`, it will only validate
stale contradictions and not a corrected state model.

---

## Acceptance Criteria

This plan is complete only if all of the following are true:

1. `One Vanderbilt` no longer presents total blockage when final type is screening
2. `C2` no longer shows geometry fields as missing when A6 shows them as asset-level extracted
3. `A0` claim counts exactly match `A5`
4. `LC-ASSET-01` no longer blocks identity/geometry that are already canonically supported
5. final PDF contains only governed chapters
6. entity-level source scope never claims asset-level support
7. the new validator blocks report generation on any critical inter-motor contradiction

---

## What Must Not Be Weakened

- no optimism inflation just to remove contradictions
- no downgrade of claim controls
- no weakening of ROI gates
- no weakening of compliance-closure gates
- no weakening of template-contamination blocking
- no weakening of source-scope semantics
- no bypass of consistency failures at render time
