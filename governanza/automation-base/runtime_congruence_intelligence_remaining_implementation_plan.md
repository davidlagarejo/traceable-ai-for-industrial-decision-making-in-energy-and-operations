# Runtime Congruence Intelligence Remaining Implementation Plan

Produced at: 2026-05-01

Parent references:

- [runtime_congruence_intelligence_master_plan.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_congruence_intelligence_master_plan.md>)
- [runtime_congruence_intelligence_execution_backlog.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_congruence_intelligence_execution_backlog.md>)
- [congruence_intelligence_multicase_certification_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/congruence_intelligence_multicase_certification_latest.md>)

## Purpose

This plan captures what still remains to be implemented after `CGI-01` through `CGI-20`.

The substrate exists.
The thesis bridge exists.
The validator bridge exists.

What still remains is the hard part that the prompt was really pointing at:

- deeper asset-family research
- stronger intake and evidence binding
- richer operator-side packs
- positive operational paths for logistics / cold chain / infrastructure
- stronger escalation from `public_only_screening` to `hybrid_diligence` and `operator_integrated_congruence`

This is no longer a “build the logic” problem.
It is now a “bind the logic to richer evidence without breaking epistemic discipline” problem.

## Current State

Already implemented:

- `motor_049` research routing, source hierarchy, local binding, intake seed packs
- `motor_050` process mapping and operational logic
- `motor_051` fair comparison, peer normalization, cross-layer congruence, invalid problem-frame detection
- `motor_052` loss patterns, maintenance reality, measurement minimality, hardware minimality, power quality and leakage hypotheses
- `motor_053` regulatory-physics, finance-to-physics, climate / tariff / culture context
- `motor_054` gold nuggets, strategic TAD, congruence claim governor
- bridge into `motor_047`, `motor_048`, `motor_036`

Already certified:

- positive building path
- positive manufacturing path
- negative / degraded warehouse path
- negative / degraded cold-chain path

The key residual from the current certification is explicit:

- logistics-family and cold-chain-family cases still degrade correctly under `public_only_screening`
- they do **not** yet have a strong positive `operational_asset_candidate -> admissible_structural_thesis` path

This is the main implementation gap that remains.

## What The Prompt Still Requires In Practice

The original prompt was not asking only for more engines.
It was asking for a system that can:

1. understand how a class of asset normally works
2. bind that understanding to the actual asset
3. know when it still cannot do that
4. move from “generic public context” to “bounded local operational logic”

That means the remaining work is concentrated in five areas:

1. asset-family research library and retrieval
2. canonical operator / diligence intake
3. local document-to-evidence extraction
4. operational-bounding and mode-escalation scoring
5. stronger positive certification for logistics / cold chain / infrastructure families

## Non-Negotiables

Do not weaken:

- `motor_047` thesis sovereignty
- `motor_048` body compression
- `motor_036` anti-hallucination and validator hardening
- claim-governor discipline
- inadmissible degradation paths

Do not reopen:

- appendix sprawl
- motor-per-section rendering
- public-guidance-as-local-diagnosis
- hardware-first reflex

## Remaining Gaps

### Gap 1. Research routing exists, but the research library is still implicit

Today:

- `motor_049` knows which family to route to
- but the family corpus is still encoded mostly as runtime heuristics and seed lists

Missing:

- persistent asset-family dossiers
- explicit authoritative source packs by family
- versioned research coverage trace

Risk:

- the system knows where to look conceptually, but not yet as a governed research product

### Gap 2. Intake schemas exist, but operator-grade intake is still shallow

Today:

- `operational_intake_pack` is seeded from public context and routing logic

Missing:

- canonical ingestion for:
  - utility bills
  - tariff records
  - throughput / production records
  - equipment inventories
  - BMS / CMMS / logs
  - lease matrices
  - metering maps
  - maintenance proof packs

Risk:

- the system degrades correctly, but cannot yet climb into stronger positive paths for non-building cases

### Gap 3. Local evidence binding exists, but document extraction is still mostly conceptual

Today:

- `local_evidence_binding_register` says what evidence is needed

Missing:

- parsers / mappers that convert actual records into:
  - `control_boundary_pack`
  - `utility_and_tariff_pack`
  - `maintenance_maturity_pack`
  - `process_overview_pack`
  - `subsystem_inventory_pack`
  - `finance_driver_pack`

Risk:

- the framework can ask for the right things, but not yet absorb them systematically

### Gap 4. Mode escalation exists conceptually, but not as a scored runtime contract

Today:

- there are three modes in the plan:
  - `public_only_screening`
  - `hybrid_diligence`
  - `operator_integrated_congruence`

Missing:

- a formal scorecard that promotes or blocks a case between those modes
- section-by-section and claim-by-claim consequences of each mode

Risk:

- the framework is disciplined, but the promotion from public to hybrid to operator-integrated is not yet explicit enough

### Gap 5. Logistics / cold-chain / infrastructure positive paths are not yet certified

Today:

- logistics-family and cold-chain-family candidates are correctly detected and degraded

Missing:

- at least one positive case per family where:
  - the asset is operationally bounded
  - fair comparison activates
  - loss logic activates
  - measurement minimality activates
  - thesis promotion succeeds

Risk:

- logic is good, but those families still look “negative only” in certification

## Execution Waves

### Wave 1 — Research Library Productization

Goal:

- turn the research substrate into a durable library, not only runtime heuristics

#### `CGI-R1` Asset-Family Research Dossiers

Purpose:

- create versioned dossiers for:
  - `commercial_building`
  - `industrial_manufacturing`
  - `logistics_warehouse`
  - `cold_chain`
  - `infrastructure_node`
  - `utility_heavy_site`

Owner:

- new `congruence_intelligence/research_library.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/research_library.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- new governance directory for research coverage manifests

Outputs to add:

- `asset_family_research_dossier`
- `family_research_coverage_register`
- `family_research_gap_register`

Acceptance:

- each asset family can say:
  - dominant subsystem archetypes
  - recurrent loss patterns
  - valid normalization bases
  - typical permit/tariff concerns
  - minimum local evidence classes

#### `CGI-R2` Authoritative Source Acquisition Trace

Purpose:

- formalize the research corpus that supports each dossier

Owner:

- `motor_049.py`
- new source-trace helpers

Outputs to add:

- `authoritative_source_retrieval_register`
- `research_source_tier_summary`
- `research_source_freshness_register`

Acceptance:

- the system can show what family knowledge came from:
  - official datasets
  - official technical guidance
  - secondary technical guidance
  - vendor / implementation guidance

### Wave 2 — Operator / Diligence Intake Deepening

Goal:

- move from public candidate logic to operator-bindable logic

#### `CGI-R3` Canonical Diligence Packs

Purpose:

- formalize ingestion for the minimum evidence types that the congruence layer keeps requesting

Owner:

- `congruence_intelligence/schemas.py`
- new intake-normalization helpers under `congruence_intelligence/`
- `motor_049.py`

Packs to add:

- `utility_bill_pack`
- `utility_tariff_pack`
- `throughput_schedule_pack`
- `equipment_inventory_pack`
- `metering_boundary_pack`
- `lease_responsibility_pack`
- `maintenance_proof_pack`
- `bms_or_controls_pack`
- `cmms_or_workorder_pack`
- `permit_detail_pack`

Acceptance:

- the system can distinguish:
  - requested but absent
  - uploaded but unparsed
  - parsed but weak
  - parsed and usable

#### `CGI-R4` Zircular Form / Checklist Extractors

Purpose:

- convert the existing Zircular forms and operating templates into real canonical packs

Owner:

- new extractors / mappers
- governance mapping docs

Reference files:

- `Form_Zircular_for_Developer.xlsx`
- `Operativo plataforma/Formatos/*`

Outputs to add:

- `zircular_form_parse_trace`
- `zircular_to_canonical_pack_register`

Acceptance:

- existing forms populate canonical packs instead of remaining dead reference material

### Wave 3 — Local Document Binding

Goal:

- let the system consume the evidence it keeps requesting

#### `CGI-R5` Bill / Tariff / Permit Parsers

Purpose:

- ingest local utility, tariff and permit evidence into usable runtime objects

Owner:

- new parsers under `congruence_intelligence/`
- `motor_049.py`
- `motor_053.py`

Outputs to add:

- `utility_charge_breakdown_register`
- `tariff_exposure_register`
- `permit_to_system_register`
- `regulated_process_scope_register`

Acceptance:

- demand / PF / reactive logic can be locally upgraded from hypothesis when the records support it

#### `CGI-R6` Control Boundary and Maintenance Evidence Binder

Purpose:

- bind the most important hidden variable in many cases:
  - who controls what
  - who pays
  - who maintains

Owner:

- new binding helpers
- `motor_050.py`
- `motor_052.py`
- `motor_053.py`

Outputs to add:

- `control_boundary_evidence_register`
- `maintenance_proof_evidence_register`
- `owner_operator_tenant_responsibility_register`

Acceptance:

- the framework can upgrade from “boundary ambiguity plausible” to “boundary bounded enough for stronger thesis”

### Wave 4 — Operational Bounding and Mode Escalation

Goal:

- make mode promotion explicit and governed

#### `CGI-R7` Operational Bounding Scorecard

Purpose:

- define what it means for a case to be bounded enough for each mode

Owner:

- `motor_049.py`
- `motor_050.py`
- `motor_036.py`

Outputs to add:

- `operational_bounding_scorecard`
- `evidence_mode_state`
- `promotion_blocker_register`

Mode outcomes:

- `public_only_screening`
- `hybrid_diligence`
- `operator_integrated_congruence`

Acceptance:

- promotion and degradation are no longer only qualitative
- validator can fail or cap claims based on explicit mode state

#### `CGI-R8` Mode-Specific Claim / Thesis / TAD Policy

Purpose:

- make every mode change downstream behavior explicitly

Owner:

- `motor_047.py`
- `motor_048.py`
- `motor_054.py`
- `motor_036.py`

Effects to formalize:

- what claims are allowed in each mode
- which congruence registers can surface into thesis
- when TAD may escalate from evidence request to action

Acceptance:

- same family, different mode, different permitted thesis strength

### Wave 5 — Family-Specific Positive Paths

Goal:

- certify at least one strong positive path outside building and manufacturing

#### `CGI-R9` Logistics / Warehouse Positive Path

Purpose:

- create a real positive case for `logistics_warehouse`

Owner:

- new richer seed under `runtime-orchestrator/inputs/`
- `motor_049` to `motor_054`

Needed evidence types:

- service-level proxy
- dock / movement intensity
- utility bills or tariff logic
- schedule / occupancy / loading profile
- equipment or refrigeration / charging / handling clues if present

Acceptance:

- logistics case reaches:
  - `operational_asset_candidate`
  - `research_seeded_operational_logic` at minimum
  - bounded fair comparison
  - bounded loss / measurement / finance logic
  - positive thesis path if evidence suffices

#### `CGI-R10` Cold-Chain Positive Path

Purpose:

- create a real positive case for `cold_chain`

Needed evidence types:

- refrigeration boundary
- temperature regime
- throughput or dwell logic
- defrost / schedule clues
- tariff / demand structure

Acceptance:

- cold-chain case can cross from public family routing into bounded operational congruence

#### `CGI-R11` Infrastructure / Utility-Heavy Positive Path

Purpose:

- avoid overfitting the system to buildings + plants

Candidates:

- rail / port / intermodal node
- utility-heavy site
- infrastructure energy / duty node

Acceptance:

- at least one non-building, non-manufacturing positive case survives the full path

### Wave 6 — Final Prompt Closure

Goal:

- verify that the system now matches the full ambition of the prompt

#### `CGI-R12` Prompt Closure Audit

Purpose:

- map each prompt requirement to:
  - implemented runtime object
  - governing motor
  - test coverage
  - certification case

Deliverable:

- `industrial_asset_congruence_prompt_closure_matrix.md`

#### `CGI-R13` Multi-Mode Certification

Purpose:

- certify all three runtime evidence modes across multiple families

Must include:

- positive building
- positive manufacturing
- positive logistics or cold chain
- degraded weak address candidate
- one operator-integrated case when local evidence is available

## File Strategy

### Create

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/research_library.py`
- one or more intake extractor / parser modules
- one or more document-binding helpers
- new certification and closure docs

### Extend

- `motor_049.py`
- `motor_050.py`
- `motor_052.py`
- `motor_053.py`
- `motor_054.py`
- `motor_047.py`
- `motor_048.py`
- `motor_036.py`
- `congruence_intelligence/schemas.py`

### Protect

Do not restructure first:

- `motor_016.py`
- `motor_017.py`
- `motor_025.py`

Only touch them later if mode-specific publication behavior truly requires it.

## Highest-Signal Reading

The most important remaining implementation is not “more analysis.”

It is:

- richer evidence ingestion
- explicit mode escalation
- and at least one positive logistics-family path

That is where the prompt still has open work.

Without that, the system is already smart and disciplined, but still strongest in:

- buildings
- manufacturing

and still primarily negative / degraded in:

- logistics-family public candidates
- cold-chain public candidates

## Final Recommendation

Execute the remaining work in this order:

1. `CGI-R3` Canonical Diligence Packs
2. `CGI-R5` Bill / Tariff / Permit Parsers
3. `CGI-R7` Operational Bounding Scorecard
4. `CGI-R9` Logistics / Warehouse Positive Path
5. `CGI-R10` Cold-Chain Positive Path
6. `CGI-R12` Prompt Closure Audit

That sequence maximizes real capability gain without destabilizing thesis/render sovereignty.
