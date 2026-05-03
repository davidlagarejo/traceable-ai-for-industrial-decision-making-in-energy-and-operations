# Runtime Congruence Intelligence Master Plan

Produced at: 2026-04-30

## Purpose

This plan defines how ZLab should evolve from:

- structural intelligence with strong thesis discipline

to:

- a broader **Industrial & Asset Congruence Intelligence System**

without breaking the logic that is already working in:

- `motor_033` TAD
- `motor_034` claim governance and output-mode sovereignty
- `motor_036` consistency validation
- `motor_047` executive thesis
- `motor_048` report compression
- `motor_016/017/025` governed render and publication path

The goal is not to build a bigger report.
The goal is to build a wider and more operationally truthful substrate that can detect:

- wrong comparisons
- wrong problem framing
- wrong dominant loss assumptions
- wrong measurement strategy
- wrong capital logic
- wrong regulatory interpretation
- wrong owner / operator / maintenance / logistics / process boundary assumptions

## Executive Reading

The next system needs three things that the current framework only has partially:

1. a stronger **intake and ingestion structure**
2. a dedicated **asset operational logic layer**
3. a transversal **congruence layer** that ties physics, operations, finance, maintenance, regulation, climate, logistics, procurement, culture and market logic together

It also needs a fourth thing that must be made explicit:

4. a governed **asset-family research layer** that can investigate how a class of asset normally works without turning public guidance into fake local diagnosis

The critical architectural decision is:

- **do not replace the current structural thesis layer**
- **do not push this directly into the renderer**
- **do not explode the DAG into 20 sovereign motors**

Instead:

- add a new package and lane called `congruence_intelligence`
- use it to enrich the current `executive_thesis`
- keep `motor_047/048/036` as sovereign downstream arbiters

## Research Principle

The system should investigate deeply, but in a governed way.

It must distinguish between:

1. **asset-family research**
   - what this type of asset typically looks like
   - what systems usually dominate
   - what loss patterns are recurrent
   - what measurement usually discriminates hypotheses
   - what regulatory / tariff / maintenance issues are common

2. **local asset truth**
   - what is actually evidenced for this specific case

The rule is:

- research widely for structural context
- claim narrowly for local diagnosis

Internet and technical literature are valid inputs for:

- archetypes
- structural patterns
- weak signals
- comparison logic
- measurement logic
- loss libraries

They are not sufficient by themselves for:

- local savings claims
- local leak diagnosis
- local retrofit economics
- local compliance closure
- local peer superiority

## Research Modes

The system should operate in three modes:

### 1. Public-only screening

Uses:

- public datasets
- permits
- standards
- technical guides
- tariffs
- public records

Can do:

- structural screening
- hypothesis formation
- comparability screening
- bounded thesis generation

Cannot do:

- implementation-grade diagnosis
- strong local economics

### 2. Hybrid diligence

Uses:

- public research
- structured intake
- basic operational documents
- bills
- equipment lists

Can do:

- operational logic hypotheses
- stronger fair comparison
- bounded subsystem dominance logic
- stronger measurement minimality logic

### 3. Operator-integrated congruence

Uses:

- public research
- structured intake
- local operational records
- maintenance proof
- metering data
- logs / BMS / CMMS / lease / permit detail

Can do:

- stronger congruence analysis
- stronger finance-to-physics translation
- better loss discrimination
- more confident strategic redesign hypotheses

## Why This Is Necessary

The Zircular reference materials reveal the real problem.

### What the references already contain

The source materials are not just “energy forms.”
They already encode a hidden operating model:

- raw material entry
- subsystems
- motors
- thermal systems
- water and waste
- finished product
- monthly schedule
- equipment hours
- peak timing
- power-factor concerns
- maintenance questions
- production hours
- annual throughput proxies
- logistics and loading questions

Examples:

- `Electricidad.docx` already points to:
  - meters
  - factor de potencia
  - tarifas por picos
  - equipos de mayor consumo
- `Termica y aire.docx` already points to:
  - fuel
  - chimneys
  - boilers / furnaces
  - combustion air
  - vapor
- `Agua y residuos.docx` already points to:
  - reuse
  - leaks
  - solvent segregation
  - metals recycling
- `Mejoras por tipo de industria.docx` already contains:
  - area
  - annual production
  - annual production hours
  - annual electricity and fuel cost / consumption
- `consumo mensual.docx` contains:
  - shift schedule
  - start-up times
  - breaks
  - Sundays / holidays

### What is missing

That knowledge is still fragmented as:

- forms
- equipment checklists
- hardware guides
- self-assessment workbooks
- measure libraries

It is **not** yet organized as:

- a universal asset logic model
- a fair-comparison engine
- a process / subsystem map
- a congruence detector
- a finance-to-physics reasoning substrate

### Key insight

The current system is already strong at:

- structural contradiction
- claim discipline
- bounded report modes
- compressed thesis-first rendering

But it is still too weak at:

- understanding how a specific asset actually works
- deciding which equipment or subsystems dominate
- knowing when a benchmark is invalid
- deciding whether measurement or hardware is warranted
- tying cost structure to physical drivers
- translating permits into physical-system hypotheses

## Non-Negotiables

The following must not weaken:

- no fake ROI
- no fake savings
- no compliance closure without evidence
- no peer superiority without comparability
- no local diagnosis from archetypal pattern alone
- no measurement recommendation without hypothesis
- no benchmark as local truth
- no report inflation back toward appendix-style sprawl
- no loss of current thesis sovereignty

## Architecture Decision

## Keep As Sovereign

These stay sovereign:

- `motor_047` executive thesis
- `motor_048` report compression
- `motor_034` claim / mode governance
- `motor_036` consistency validator
- `motor_016/017/025` packaging, render, publication

## Add As New Substrate

Add:

- `runtime_orchestrator/congruence_intelligence/`

This package becomes a sibling of:

- `structural_intelligence/`

It should not initially own the visible report.
It should first enrich the reasoning substrate that the thesis layer consumes.

## Runtime Grouping

The 20 conceptual engines from the prompt should not become 20 runtime adapters.

They should be grouped into 6 runtime motors, with research folded explicitly into the first one:

### `motor_049` Research Router & Congruence Intake Normalization

Owns:

- asset-family research routing
- authoritative source family selection
- source hierarchy enforcement
- source-to-intake mapping
- public-context extraction for asset-family understanding
- intake normalization
- family-specific intake packs
- operational intake schemas
- local-evidence binding prerequisites

### `motor_050` Asset Operational Logic

Owns:

- Asset/System Abstraction extension
- Universal Process Mapping
- subsystem logic
- control boundary map
- maintenance dependency map
- operational equipment dominance

### `motor_051` Fair Comparison & Congruence

Owns:

- Fair Comparison Engine
- Peer Normalization Engine
- Structural Correlation Engine
- Cross-Layer Congruence Engine

### `motor_052` Loss / Maintenance / Measurement Reality

Owns:

- Industrial Common-Sense
- Loss Pattern Library
- Maintenance Reality
- Measurement Strategy
- Hardware Minimality
- Power Quality / Reactive
- Leakage & Hidden Waste

### `motor_053` Finance / Regulation / Culture Translation

Owns:

- Climate & Location Context
- Regulatory-Permit-Physics
- Finance-to-Physics Translation
- Culture / Execution Discipline Proxy

### `motor_054` Strategic Congruence Synthesis

Owns:

- Strategic Gold Nugget Finder
- congruence-side strategic TAD enrichments
- congruence claim register
- bridge into `motor_047`

## Data Model Strategy

Do not replace the current evidence-state enum immediately.

Current enum in `structural_intelligence/schemas.py` remains:

- `OBSERVED_FACT`
- `ARCHETYPAL_PRIOR`
- `CONDITIONAL_HYPOTHESIS`
- `INADMISSIBLE_CLAIM`
- `NOT_OBSERVED`

Instead, extend with metadata fields:

- `evidence_origin`
- `signal_class`
- `pattern_class`
- `source_class`

Safe mapping:

- `PUBLIC_RECORD` -> `OBSERVED_FACT` + `evidence_origin=public_record`
- `STRUCTURAL_PATTERN` -> `ARCHETYPAL_PRIOR` + `pattern_class=structural_pattern`
- `WEAK_SIGNAL` -> `CONDITIONAL_HYPOTHESIS` + `signal_class=weak_signal`

This avoids breaking:

- `motor_034`
- `motor_036`
- existing claim contracts
- tests already tied to current enums

## Source Hierarchy

Research must be ordered by source quality.

### Tier 1 — authoritative public technical / regulatory / utility sources

Examples:

- DOE / Better Buildings / Better Plants sourcebooks
- EPA / ENERGY STAR
- official permits and regulatory texts
- utility tariffs and official utility documentation
- local government property / permit / compliance data
- official technical standards where accessible

Use for:

- structural patterns
- benchmarking constraints
- permit-to-physics logic
- measurement strategy context

### Tier 2 — strong sectoral technical guidance

Examples:

- recognized industry associations
- established technical manuals
- public industrial assessment guides
- maintenance and operations guidance with clear provenance

Use for:

- subsystem logic
- common-sense loss patterns
- maintenance maturity expectations

### Tier 3 — vendor / implementation / secondary guidance

Examples:

- OEM brochures
- product guides
- integrator blogs
- checklist vendors

Use for:

- implementation possibilities
- communication / hardware options

Do not use alone for:

- structural truth
- peer superiority
- local diagnosis

## Research Output Objects

### 0. `asset_family_research_profile`

```json
{
  "asset_family": "",
  "research_mode": "",
  "authoritative_source_families": [],
  "typical_processes": [],
  "typical_subsystems": [],
  "typical_loss_patterns": [],
  "typical_regulatory_signals": [],
  "typical_measurement_paths": [],
  "typical_invalid_comparisons": []
}
```

### 0A. `authoritative_source_trace_register`

```json
[
  {
    "source_family": "",
    "source_tier": "",
    "url_or_reference": "",
    "used_for": [],
    "allowed_inference_class": [],
    "prohibited_inference_class": []
  }
]
```

### 0B. `local_evidence_binding_register`

```json
[
  {
    "research_claim": "",
    "asset_family_context": "",
    "local_binding_needed": [],
    "current_local_binding_state": "",
    "if_unbound_then_only_allow": []
  }
]
```

## New Canonical Intake Objects

### 1. `operational_intake_pack`

```json
{
  "asset_family": "",
  "asset_identity_pack": {},
  "process_overview_pack": {},
  "subsystem_inventory_pack": {},
  "equipment_dominance_pack": {},
  "schedule_and_utilization_pack": {},
  "control_boundary_pack": {},
  "maintenance_maturity_pack": {},
  "measurement_and_metering_pack": {},
  "utility_and_tariff_pack": {},
  "regulatory_and_permit_pack": {},
  "finance_driver_pack": {},
  "logistics_pack": {},
  "procurement_pack": {},
  "culture_execution_pack": {},
  "climate_location_pack": {}
}
```

### 2. `process_map`

```json
{
  "inputs": [],
  "transformations": [],
  "support_systems": [],
  "loss_points": [],
  "outputs": [],
  "market_value_link": [],
  "human_control_points": [],
  "automatic_control_points": [],
  "regulatory_friction_points": []
}
```

### 3. `subsystem_register`

```json
[
  {
    "subsystem_name": "",
    "subsystem_role": "",
    "primary_equipment_classes": [],
    "dominant_energy_forms": [],
    "control_mode": "",
    "maintenance_dependency": "",
    "evidence_state": "",
    "why_it_may_matter": ""
  }
]
```

### 4. `fair_comparison_profile`

```json
{
  "asset_type": "",
  "process_type": "",
  "climate_zone": "",
  "size_basis": "",
  "operating_schedule": "",
  "throughput_proxy": "",
  "fuel_mix": "",
  "control_boundary": "",
  "regulatory_context": "",
  "maintenance_maturity": "",
  "technology_level": "",
  "operator_tenant_structure": "",
  "logistics_complexity": "",
  "cultural_execution_signal": ""
}
```

### 5. `loss_hypothesis_register`

```json
[
  {
    "loss_pattern": "",
    "system_family": "",
    "hypothesis_state": "",
    "why_plausible": "",
    "economic_materiality_potential": "",
    "minimum_discriminating_evidence": [],
    "kill_condition": ""
  }
]
```

### 6. `maintenance_reality_register`

```json
{
  "maintenance_maturity_state": "",
  "evidenced_programs": [],
  "missing_proofs": [],
  "recurrent_failure_signals": [],
  "downtime_dependency_hypotheses": [],
  "claimable_language": [],
  "prohibited_language": []
}
```

### 7. `measurement_strategy_register`

```json
[
  {
    "hypothesis": "",
    "minimum_measurement": "",
    "cheapest_valid_source": "",
    "why": "",
    "if_confirmed": "",
    "if_falsified": "",
    "upgrade_path": ""
  }
]
```

### 8. `regulatory_physics_register`

```json
[
  {
    "permit_or_rule": "",
    "jurisdiction": "",
    "physical_signal": "",
    "why_it_matters": "",
    "what_it_does_not_prove": "",
    "evidence_state": "",
    "follow_up_evidence": []
  }
]
```

### 9. `finance_physics_dependency_register`

```json
[
  {
    "financial_assumption": "",
    "physical_dependency": "",
    "operational_dependency": "",
    "regulatory_dependency": "",
    "evidence_state": "",
    "risk_if_wrong": "",
    "evidence_needed": []
  }
]
```

### 10. `strategic_gold_nugget_register`

```json
[
  {
    "gold_nugget": "",
    "why_surprising": "",
    "why_true_if_true": "",
    "what_would_change_if_acted_on": "",
    "evidence_state": "",
    "bounded_use": ""
  }
]
```

## Intake Expansion Strategy

## Principle

Do not build one giant universal form.

Build:

- a universal core intake
- plus family-specific overlays

### Universal Core Intake

Applies to all assets:

- identity
- business function
- schedule
- value output proxy
- utility / tariff
- control boundary
- maintenance proof
- metering state
- permits / obligations
- cost drivers

### Family Overlay: Building

Based on:

- `Form_Zircular_for_Developer.xlsx`
- building public records
- owner / tenant boundary
- LL84 / LL97 / DOB / DOF / PLUTO / utility structure
- BMS / central plant / submetering / after-hours logic

### Family Overlay: Manufacturing

Based on:

- `Materia prima.docx`
- `Subsistemas.docx`
- `Termica y aire.docx`
- `Electricidad.docx`
- `Mejoras por tipo de industria.docx`
- `consumo mensual.docx`
- `Agua y residuos.docx`

### Family Overlay: Logistics / Warehousing

Derived from:

- raw-material flow questions
- finished-product flow questions
- loading / unloading logic
- storage temperature logic
- movement, picking and layout logic
- vehicle / forklift / charging / dispatch patterns

### Family Overlay: Utility / Process-Heavy Site

Derived from:

- thermal
- compressed air
- large motor
- demand / PF / harmonic
- combustion / permit
- water / waste / emissions

## Reference Migration Plan

### Migrate Into Canonical Intake Packs

- `Form_Zircular_for_Developer.xlsx` -> building identity / public-asset intake
- `Electricidad.docx` -> utility / tariff / PF / meter / major-load intake
- `Motores y ventilacion.docx` -> motor / VFD / oversizing / ventilation intake
- `Enfriadora agua.docx` -> chiller / cooling-process intake
- `Termica y aire.docx` -> combustion / boiler / furnace / compressed-air intake
- `Agua y residuos.docx` -> water reuse / leaks / waste-flow intake
- `Materia prima.docx` -> input logistics / storage / forklift / flow intake
- `Producto terminado.docx` -> output logistics / packing / storage / dispatch intake
- `consumo mensual.docx` -> schedule / start-up / nonproductive load timing intake
- `Mejoras por tipo de industria.docx` -> throughput / normalization input
- `Subsistemas.docx` -> subsystem inventory intake

### Migrate Into Pattern Libraries, Not Direct Output

- `selfassessment.pdf`
- `IAC_Database.xls`
- `Hardware_ES.pdf`
- `Dexma_Checklist_Hardware_ES.pdf`

These should become:

- `loss_pattern_library`
- `measurement_decision_tree`
- `hardware_minimality_decision_tree`
- `asset_family_research_library`

They must **not** remain direct recommendation surfaces.

### Migrate Into Research Corpus

- DOE Better Plants sourcebooks
- ENERGY STAR benchmarking and whole-building data guidance
- EPA leak / LDAR guidance where relevant
- tariff and utility official guidance by jurisdiction
- local regulatory and permit documentation families

These should become:

- `authoritative_source_library`
- `asset_family_research_profiles`
- `permit_to_physics_signal_library`
- `measurement_logic_library`

## Where To Improve vs Where Not To Touch

## Improve / Extend

- `structural_intelligence/system_abstraction.py`
  - extend with process / subsystem / maintenance / climate / control fields
- `structural_intelligence/benchmarking.py`
  - refactor into fair comparison logic source
- `structural_intelligence/competitive_comparison.py`
  - strengthen comparability and transferability logic
- `structural_intelligence/cross_layer_conflicts.py`
  - evolve toward cross-layer congruence
- `structural_intelligence/financial_exposure_structural.py`
  - bridge into finance-to-physics dependencies
- `executive_thesis.py`
  - enrich with congruence signals after the substrate is stable
- `report_compression.py`
  - only later, if new signals deserve body priority
- `motor_036.py`
  - later, add congruence quality checks

## Do Not Touch First

- `motor_016`
- `motor_017`
- `motor_025`
- `render_section_contract.py`
- `output_taxonomy.py`

These are presentation / publication surfaces.
They should not absorb congruence logic early.

## Do Not Replace

- existing `claim_contract_register`
- existing `report_output_mode_classifier_table`
- existing `executive_thesis`
- existing `client_facing_tad`

Only enrich them after the congruence substrate proves stable.

## Runtime Integration Order

## Phase 0 — Research & Intake Mapping Audit

Deliverables:

- authoritative source hierarchy
- asset-family research routing matrix
- source-to-intake mapping table
- reference migration map
- missing-data heatmap by asset family

Touch:

- new governance docs only

Do not touch:

- runtime DAG

## Phase 1 — Research Router & Canonical Intake Schemas

Deliverables:

- `asset_family_research_profile`
- `authoritative_source_trace_register`
- `local_evidence_binding_register`
- `operational_intake_pack`
- family overlays
- ingestion normalization rules

Likely files:

- new `congruence_intelligence/schemas.py`
- new adapter `motor_049.py`

Acceptance:

- the system can state what it knows from research vs what remains locally unbound
- Zircular forms can map into canonical intake objects
- missing fields degrade explicitly rather than silently disappearing

## Phase 2 — Asset Operational Logic Engine

Deliverables:

- process map
- subsystem register
- equipment dominance profile
- control boundary map
- maintenance dependency map

Likely files:

- `congruence_intelligence/operational_logic.py`
- `congruence_intelligence/process_mapping.py`
- `motor_050.py`

Acceptance:

- one building case
- one manufacturing case
- one logistics-like case
  each produce an operational logic object without inventing local facts
- each case also shows which parts came from authoritative asset-family research and which parts remain local hypotheses

## Phase 3 — Fair Comparison & Congruence

Deliverables:

- fair comparison profile
- comparable / non-comparable decisions
- normalization requirements
- structural correlation register
- congruence contradiction register

Likely files:

- `congruence_intelligence/fair_comparison.py`
- `congruence_intelligence/peer_normalization.py`
- `congruence_intelligence/correlation_engine.py`
- `congruence_intelligence/congruence_engine.py`
- `motor_051.py`

Acceptance:

- invalid comparison is explicitly blocked
- same-area comparison without throughput normalization fails in manufacturing
- owner/tenant mismatch is surfaced in buildings
- research-derived comparison logic cannot be promoted to local peer truth without binding evidence

## Phase 4 — Loss / Maintenance / Measurement Reality

Deliverables:

- loss pattern library
- maintenance reality register
- leakage hypothesis register
- power-quality hypothesis register
- measurement strategy register
- hardware minimality register

Likely files:

- `congruence_intelligence/loss_patterns.py`
- `congruence_intelligence/maintenance_reality.py`
- `congruence_intelligence/measurement_strategy.py`
- `congruence_intelligence/hardware_minimality.py`
- `congruence_intelligence/power_quality.py`
- `congruence_intelligence/leakage_hidden_waste.py`
- `motor_052.py`

Acceptance:

- system can say:
  - “reactive / PF is strategically plausible”
  - “compressed-air leakage is plausible”
  - “maintenance maturity not evidenced”
  - “do not install hardware yet”

without overclaiming
- and can cite whether that plausibility comes from:
  - asset-family research
  - public local signals
  - local operational evidence

## Phase 5 — Finance / Regulation / Culture Translation

Deliverables:

- regulatory-physics register
- finance-to-physics dependency register
- climate and tariff context register
- culture / execution proxy register

Likely files:

- `congruence_intelligence/regulatory_physics.py`
- `congruence_intelligence/finance_to_physics.py`
- `congruence_intelligence/climate_location.py`
- `congruence_intelligence/culture_proxy.py`
- `motor_053.py`

Acceptance:

- permits translate to physical hypotheses, not fake diagnoses
- financial assumptions are linked to physical and operational dependencies
- culture remains weak-signal bounded
- public technical guidance cannot be misrendered as local observation

## Phase 6 — Strategic Congruence Synthesis

Deliverables:

- strategic gold nugget register
- congruence-side TAD enrichment
- congruence claim register

Likely files:

- `congruence_intelligence/gold_nuggets.py`
- `congruence_intelligence/strategic_tad.py`
- `congruence_intelligence/claim_governor.py`
- `motor_054.py`

Acceptance:

- outputs contain uncomfortable but bounded takeaways
- TAD actions map to congruence contradictions, evidence discriminators and claim permissions

## Phase 7 — Bridge Into Thesis

Deliverables:

- `motor_047` enriched with congruence-side fields
- `motor_048` body selection rules updated only where justified

Touch carefully:

- `executive_thesis.py`
- `motor_047.py`
- `report_compression.py`
- `motor_048.py`

Do not over-expand body.

Acceptance:

- stronger thesis without increasing body sprawl
- `gold nugget` style insights appear in the executive thesis
- no loss of client-facing compression

## Phase 8 — Validator Hardening

Deliverables:

- congruence checks in `motor_036`

Examples:

- fair comparison missing but peer claim visible -> fail
- measurement recommendation without hypothesis -> fail
- hardware recommendation before minimal-source path considered -> fail
- loss diagnosis presented as local fact from pattern only -> fail
- finance claim missing physical dependency -> fail
- permit inference presented as proof of current operation -> fail

## Integration With Current Thesis System

The current `executive_thesis` should be extended, not replaced.

New optional fields:

- `dominant_operational_misunderstanding`
- `hidden_system_boundary_error`
- `invalid_comparison_risk`
- `dominant_loss_logic`
- `measurement_minimality_take`
- `regulatory_physics_take`
- `finance_to_physics_take`
- `maintenance_reality_take`

Only promote to visible body after:

- stability
- test coverage
- multi-case proof

## TAD Expansion Strategy

Current TAD stays sovereign.

Add new action families, not a second TAD system:

- `REQUEST_PROCESS_MAP`
- `REQUEST_SUBSYSTEM_INVENTORY`
- `REQUEST_FAIR_PEER_SET`
- `REQUEST_TARIFF_AND_PF_EVIDENCE`
- `REQUEST_MAINTENANCE_PROOF`
- `REQUEST_CONTROL_BOUNDARY`
- `MEASURE_ONLY_IF_MATERIAL`
- `DO_NOT_COMPARE_YET`
- `DO_NOT_SUBMETER_YET`

These should enrich:

- `motor_033`

not replace it.

## Finance and Regulation Coverage

This expansion must explicitly cover:

- NOI / EBITDA / DSCR / CAPEX relevance
- tariff structure
- demand charges
- PF / reactive exposure
- permit-driven physical constraints
- owner / tenant / operator liability boundaries
- utility / regional cost structure
- local regulatory burden
- insurance / downtime / maintenance economics where observable

The key design rule:

- finance is not a separate lane
- regulation is not a separate lane
- both must be translated into physical and operational dependencies
- research is not a separate narrative lane either; it is a context-building substrate that must be explicitly bound or explicitly limited

## Acceptance Test Plan

The system is acceptable only if it can pass the following:

1. building case:
   - recognizes owner / tenant / LL97 control-boundary problem
2. manufacturing case:
   - blocks naive energy-intensity comparison without throughput normalization
3. logistics case:
   - identifies movement / storage / schedule / layout as possible dominant losses
4. PF / reactive case:
   - raises bounded hypothesis when inductive loads and tariff signals exist
5. leakage case:
   - raises bounded leakage hypothesis without diagnosing local leaks as fact
6. measurement case:
   - recommends bills / tariff / demand profile before broad sensor installation
7. maintenance case:
   - says “maintenance maturity not evidenced” without inventing failure
8. permit case:
   - translates permit to physical hypothesis, not proof of current operation
9. fair comparison case:
   - fails comparison if process / climate / throughput / control boundary mismatch
10. thesis case:
   - congruence signals sharpen the thesis without increasing body beyond the current compression budget
11. research binding case:
   - the system can cite authoritative asset-family guidance without presenting it as local diagnosis
12. public-only case:
   - the system remains bounded when only internet/public-record context exists

## Automatic Tests To Add

- `test_operational_intake_normalization.py`
- `test_asset_operational_logic_engine.py`
- `test_fair_comparison_engine.py`
- `test_congruence_correlation_engine.py`
- `test_loss_pattern_and_measurement_minimality.py`
- `test_regulatory_finance_translation.py`
- `test_asset_family_research_router.py`
- `test_local_evidence_binding.py`
- `test_congruence_gold_nuggets.py`
- `test_congruence_claim_governor.py`
- `test_executive_thesis_congruence_bridge.py`
- `test_system_consistency_validator_congruence.py`

## Sharp Implementation Guidance

### Cut

Cut from legacy forms:

- direct recommendation behavior
- implicit assumption that “more hardware” is the right next step
- subsystem-by-subsystem question flow that does not connect to value creation
- any assumption that public guidance alone is enough to close a local diagnosis

### Paste

Paste into new substrate:

- question prompts
- common equipment families
- maintenance prompts
- throughput and schedule fields
- tariff / PF prompts
- waste / water / logistics prompts
- asset-family research routes
- authoritative technical source families
- local-binding requirements for every research-derived pattern

### Restructure

Restructure all of it around:

- process
- subsystem
- boundary
- comparability
- dominant loss logic
- evidence minimality
- research context vs local truth

## Remaining Risks

- intake bloat if forms are copied too literally
- accidental reversion to equipment-checklist thinking
- accidental conversion of internet research into fake local certainty
- renderer contamination if congruence logic leaks too early into `motor_016`
- enum instability if evidence-state taxonomy is rewritten too aggressively
- report inflation if every new register fights for body visibility

## What Must Not Change

- thesis-first publication logic
- compressed client-facing body
- strong claim contracts
- validator sovereignty
- mode classifier sovereignty
- anti-hallucination discipline

## Final Recommendation

Proceed as:

- new substrate first
- bridge second
- renderer last

Do **not** implement this as:

- 20 new visible report sections
- 20 sovereign adapters
- more forms without canonical objects
- direct migration of checklists into recommendations

The correct evolution is:

- from energy-efficiency questionnaires
- to operational logic
- to congruence detection
- to stronger thesis

That is the safest path to make the framework broader without making it noisier or less disciplined.
