# Runtime Congruence Intelligence Execution Backlog

Produced at: 2026-04-30

Parent plan:

- [runtime_congruence_intelligence_master_plan.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/runtime_congruence_intelligence_master_plan.md>)

## Execution Rule

This backlog must be executed in sequence.

Do not jump to thesis/render integration before:

- research routing
- intake normalization
- operational logic
- fair comparison
- loss / maintenance / measurement logic
- finance / regulation translation

have each produced governed runtime objects with tests.

## Priority Bands

- `P0`: substrate and epistemic safety
- `P1`: operational intelligence depth
- `P2`: strategic integration into thesis and validator

## Ticket Format

Each ticket specifies:

- purpose
- owner
- main files
- changes required
- dependencies
- acceptance criteria
- tests

---

## P0 — Research / Intake / Safety Foundation

### `CGI-01` Research Routing Matrix

Purpose:

- create the governed routing logic that decides what asset-family research corpus applies to a case

Owner:

- new `congruence_intelligence/research_router.py`
- adapter `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/research_router.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `governanza/automation-base/runtime_congruence_intelligence_master_plan.md`

Changes required:

- define asset families:
  - `commercial_building`
  - `industrial_manufacturing`
  - `logistics_warehouse`
  - `cold_chain`
  - `thermal_process_site`
  - `utility_heavy_site`
  - `generic_operational_asset`
- map each family to:
  - source families
  - typical subsystem families
  - likely loss domains
  - measurement families
  - invalid comparison risks

Dependencies:

- none

Acceptance criteria:

- case routing works for:
  - One Vanderbilt
  - Wilsonart
  - weak address-first case
- output is explicit about:
  - selected asset family
  - research mode
  - source families selected
  - source families rejected

Tests:

- `test_asset_family_research_router.py`

---

### `CGI-02` Authoritative Source Hierarchy

Purpose:

- codify source tiers and allowed inference strength

Owner:

- `congruence_intelligence/source_hierarchy.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/source_hierarchy.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`
- `runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/schemas.py`

Changes required:

- define:
  - `source_tier`
  - `source_class`
  - `allowed_inference_class`
  - `prohibited_inference_class`
- create canonical handling for:
  - DOE / EPA / ENERGY STAR / official permits / tariffs / official public data
  - association / technical guidance
  - vendor / implementation sources

Dependencies:

- `CGI-01`

Acceptance criteria:

- any research-derived claim can state:
  - where it comes from
  - how far it is allowed to go
- vendor material cannot directly support strong local diagnosis

Tests:

- `test_authoritative_source_hierarchy.py`

---

### `CGI-03` Local Evidence Binding Register

Purpose:

- ensure every research-derived pattern or signal states what local evidence would bind it to the case

Owner:

- `congruence_intelligence/local_binding.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/local_binding.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

Changes required:

- emit `local_evidence_binding_register`
- for each research-derived claim, define:
  - local binding needed
  - current binding state
  - allowed use while unbound

Dependencies:

- `CGI-01`
- `CGI-02`

Acceptance criteria:

- system can cleanly say:
  - “plausible from asset-family research”
  - “not yet locally bound”

Tests:

- `test_local_evidence_binding.py`

---

### `CGI-04` Canonical Operational Intake Schemas

Purpose:

- formalize the new intake objects and family overlays

Owner:

- `congruence_intelligence/schemas.py`
- `motor_049.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/schemas.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

Changes required:

- add:
  - `operational_intake_pack`
  - `asset_family_research_profile`
  - `authoritative_source_trace_register`
  - `process_overview_pack`
  - `subsystem_inventory_pack`
  - `utility_and_tariff_pack`
  - `maintenance_maturity_pack`
  - `regulatory_and_permit_pack`
  - `finance_driver_pack`
  - `control_boundary_pack`

Dependencies:

- `CGI-01`
- `CGI-02`

Acceptance criteria:

- schemas can represent:
  - building intake
  - manufacturing intake
  - logistics intake

Tests:

- `test_congruence_intake_schemas.py`

---

### `CGI-05` Zircular Reference Migration Pack

Purpose:

- convert the current forms/checklists into canonical intake and pattern assets

Owner:

- governance mapping + `motor_049`

Main files:

- new governance doc:
  - `runtime_congruence_reference_mapping_matrix.md`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py`

Changes required:

- map:
  - `Form_Zircular_for_Developer.xlsx`
  - `Electricidad.docx`
  - `Termica y aire.docx`
  - `Agua y residuos.docx`
  - `Subsistemas.docx`
  - `Materia prima.docx`
  - `Producto terminado.docx`
  - `consumo mensual.docx`
  - `Mejoras por tipo de industria.docx`
- separate:
  - intake fields
  - loss-pattern seeds
  - measurement logic seeds
  - maintenance prompts

Dependencies:

- `CGI-04`

Acceptance criteria:

- no source stays as “just a form”
- every reference is classified as:
  - intake
  - pattern library
  - measurement logic
  - research corpus

Tests:

- `test_reference_mapping_matrix.py`

---

## P1 — Operational Logic / Comparison / Loss Logic

### `CGI-06` Asset Operational Logic Engine

Purpose:

- infer how the asset likely works at the level needed for congruence analysis

Owner:

- `congruence_intelligence/operational_logic.py`
- `congruence_intelligence/process_mapping.py`
- adapter `motor_050.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/operational_logic.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/process_mapping.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_050.py`

Changes required:

- emit:
  - `process_map`
  - `subsystem_register`
  - `equipment_dominance_register`
  - `maintenance_dependency_map`
  - `control_boundary_map`
  - `operational_value_flow_register`

Dependencies:

- `CGI-01` through `CGI-05`

Acceptance criteria:

- One Vanderbilt:
  - central plant / tenants / BMS / owner-control boundary logic appears
- Wilsonart:
  - process / thermal / support-system / throughput logic appears
- warehouse case:
  - movement / storage / schedule / loading logic appears where bounded

Tests:

- `test_asset_operational_logic_engine.py`

---

### `CGI-07` Fair Comparison & Peer Normalization

Purpose:

- prevent invalid comparisons before any peer logic is used

Owner:

- `congruence_intelligence/fair_comparison.py`
- `congruence_intelligence/peer_normalization.py`
- adapter `motor_051.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/fair_comparison.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_normalization.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

Changes required:

- emit:
  - `fair_comparison_profile`
  - `comparison_validity_register`
  - `normalization_requirements_register`
  - `invalid_comparison_risk_register`

Dependencies:

- `CGI-06`

Acceptance criteria:

- manufacturing comparison fails without throughput normalization
- building comparison fails if control boundary mismatch is ignored
- logistics comparison fails if service-level / complexity mismatch is ignored

Tests:

- `test_fair_comparison_engine.py`

---

### `CGI-08` Structural Correlation & Cross-Layer Congruence

Purpose:

- connect subsystems, patterns, costs, regulation and control structures into explicit congruence logic

Owner:

- `congruence_intelligence/correlation_engine.py`
- `congruence_intelligence/congruence_engine.py`
- adapter `motor_051.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/correlation_engine.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/congruence_engine.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py`

Changes required:

- emit:
  - `structural_correlation_register`
  - `cross_layer_congruence_register`
  - `invalid_problem_frame_register`

Dependencies:

- `CGI-06`
- `CGI-07`

Acceptance criteria:

- can detect:
  - regulation vs control mismatch
  - benchmark vs process mismatch
  - procurement vs maintenance mismatch
  - finance vs physical dependency mismatch

Tests:

- `test_congruence_correlation_engine.py`

---

### `CGI-09` Loss Pattern Library & Common-Sense Engine

Purpose:

- formalize recurrent loss patterns without converting them to fake local diagnoses

Owner:

- `congruence_intelligence/loss_patterns.py`
- adapter `motor_052.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/loss_patterns.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py`

Changes required:

- encode initial libraries for:
  - compressed air
  - steam / boilers
  - electrical / demand / PF
  - HVAC / chillers
  - logistics / layout / movement
  - procurement / lifecycle cost
  - culture / governance / “nobody owns the data”

Dependencies:

- `CGI-05`
- `CGI-06`

Acceptance criteria:

- system emits:
  - `STRUCTURAL_PATTERN`-style bounded hypotheses
  - never local leak diagnosis as fact

Tests:

- `test_loss_pattern_library.py`

---

### `CGI-10` Maintenance Reality Engine

Purpose:

- represent maintenance maturity and its decision consequences without overclaiming

Owner:

- `congruence_intelligence/maintenance_reality.py`
- adapter `motor_052.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/maintenance_reality.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py`

Changes required:

- emit:
  - `maintenance_reality_register`
  - `maintenance_proof_gap_register`
  - `downtime_dependency_register`

Dependencies:

- `CGI-06`
- `CGI-09`

Acceptance criteria:

- can say:
  - `maintenance maturity not evidenced`
  - `reactive-maintenance risk plausible`
  - `downtime economics may dominate`

Tests:

- `test_maintenance_reality_engine.py`

---

### `CGI-11` Measurement Strategy / Hardware Minimality / Power Quality / Leakage

Purpose:

- ensure the system asks for the minimum measurement and minimum hardware needed to discriminate what matters

Owner:

- `congruence_intelligence/measurement_strategy.py`
- `congruence_intelligence/hardware_minimality.py`
- `congruence_intelligence/power_quality.py`
- `congruence_intelligence/leakage_hidden_waste.py`
- adapter `motor_052.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/measurement_strategy.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/hardware_minimality.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/power_quality.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/leakage_hidden_waste.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py`

Changes required:

- emit:
  - `measurement_strategy_register`
  - `hardware_minimality_register`
  - `power_quality_hypothesis_register`
  - `leakage_hypothesis_register`

Dependencies:

- `CGI-06`
- `CGI-09`
- `CGI-10`

Acceptance criteria:

- no broad sensor recommendation without hypothesis
- bills / tariff / PF / demand path is considered before hardware sprawl
- power-quality hypotheses appear only where system family and tariff context justify them
- leakage hypotheses appear only where system family and materiality justify them

Tests:

- `test_measurement_and_hardware_minimality.py`

---

## P1.5 — Finance / Regulation / Climate / Culture

### `CGI-12` Regulatory-Permit-Physics Translation

Purpose:

- translate rules and permits into physical hypotheses and system implications

Owner:

- `congruence_intelligence/regulatory_physics.py`
- adapter `motor_053.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/regulatory_physics.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py`

Changes required:

- emit:
  - `regulatory_physics_register`
  - `permit_signal_register`
  - `regulatory_constraint_register`

Dependencies:

- `CGI-01`
- `CGI-02`
- `CGI-06`

Acceptance criteria:

- permit implies bounded physical signal
- permit never treated as proof of current operation

Tests:

- `test_regulatory_physics_translation.py`

---

### `CGI-13` Finance-to-Physics Translation

Purpose:

- tie costs, margin, CAPEX logic and financial risk to physical and operational dependencies

Owner:

- `congruence_intelligence/finance_to_physics.py`
- adapter `motor_053.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/finance_to_physics.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py`

Changes required:

- emit:
  - `finance_physics_dependency_register`
  - `cost_driver_dependency_register`
  - `capital_logic_register`

Dependencies:

- `CGI-06`
- `CGI-08`
- `CGI-11`
- `CGI-12`

Acceptance criteria:

- can explain:
  - what physical variable moves the cost
  - what operational variable moves the margin
  - what regulatory condition moves CAPEX
  - what maintenance issue moves downtime economics

Tests:

- `test_finance_to_physics_translation.py`

---

### `CGI-14` Climate / Tariff / Culture Context

Purpose:

- include regional context and execution discipline without overclaiming

Owner:

- `congruence_intelligence/climate_location.py`
- `congruence_intelligence/culture_proxy.py`
- adapter `motor_053.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/climate_location.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/culture_proxy.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py`

Changes required:

- emit:
  - `climate_location_context_register`
  - `utility_tariff_context_register`
  - `culture_execution_proxy_register`

Dependencies:

- `CGI-01`
- `CGI-02`
- `CGI-04`

Acceptance criteria:

- climate is treated as structural context
- tariff is translated into plausible cost logic
- culture stays bounded as weak signal or proxy

Tests:

- `test_climate_tariff_culture_context.py`

---

## P2 — Strategic Integration

### `CGI-15` Strategic Gold Nugget Finder

Purpose:

- generate bounded but uncomfortable strategic takeaways from congruence signals

Owner:

- `congruence_intelligence/gold_nuggets.py`
- `congruence_intelligence/strategic_tad.py`
- adapter `motor_054.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/gold_nuggets.py`
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/strategic_tad.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py`

Changes required:

- emit:
  - `strategic_gold_nugget_register`
  - `congruence_tad_enrichment_register`
  - `congruence_action_priority_register`

Dependencies:

- `CGI-08`
- `CGI-11`
- `CGI-13`
- `CGI-14`

Acceptance criteria:

- can produce insights such as:
  - wrong benchmark basis
  - wrong control boundary
  - wrong capital target
  - wrong measurement instinct

Tests:

- `test_congruence_gold_nuggets.py`

---

### `CGI-16` Congruence Claim Governor

Purpose:

- govern all new congruence-side claims with the same rigor as the structural lane

Owner:

- `congruence_intelligence/claim_governor.py`
- `motor_054.py`
- `motor_034.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/claim_governor.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py`

Changes required:

- produce congruence-side claim contracts
- bridge them into the universal `claim_contract_register`

Dependencies:

- `CGI-15`

Acceptance criteria:

- no congruence claim can appear without:
  - evidence state
  - source tier
  - falsification condition
  - minimum evidence
  - allowed / prohibited language

Tests:

- `test_congruence_claim_governor.py`

---

### `CGI-17` Bridge Into Executive Thesis

Purpose:

- let congruence intelligence sharpen the thesis without breaking compression or output-mode logic

Owner:

- `executive_thesis.py`
- `motor_047.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py`

Changes required:

- add optional thesis fields:
  - `dominant_operational_misunderstanding`
  - `hidden_system_boundary_error`
  - `invalid_comparison_risk`
  - `dominant_loss_logic`
  - `measurement_minimality_take`
  - `regulatory_physics_take`
  - `finance_to_physics_take`
  - `maintenance_reality_take`

Dependencies:

- `CGI-06` through `CGI-16`

Acceptance criteria:

- One Vanderbilt thesis becomes sharper without adding body sprawl
- Wilsonart thesis becomes sharper without generic “efficiency” flattening
- weak case remains bounded and does not gain fake operational certainty

Tests:

- `test_executive_thesis_congruence_bridge.py`

---

### `CGI-18` Congruence-Aware Report Compression

Purpose:

- selectively promote only the most decision-useful congruence outputs into the body

Owner:

- `report_compression.py`
- `motor_048.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/report_compression.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py`

Changes required:

- map new congruence signals into existing compressed body budget
- do not exceed current body discipline

Dependencies:

- `CGI-17`

Acceptance criteria:

- body remains bounded
- no return to appendix-style sprawl
- only thesis-relevant congruence insights become visible

Tests:

- `test_congruence_report_compression.py`

---

### `CGI-19` Congruence Validator Hardening

Purpose:

- make the system fail if congruence logic is present but epistemically or narratively malformed

Owner:

- `motor_036.py`

Main files:

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py`

Changes required:

- add fail checks for:
  - invalid comparison used as peer evidence
  - measurement recommendation without hypothesis
  - hardware recommendation before cheapest valid source path
  - loss pattern presented as local fact
  - permit signal presented as operational proof
  - finance claim missing physical dependency
  - research-derived claim missing local binding state

Dependencies:

- `CGI-16`
- `CGI-17`
- `CGI-18`

Acceptance criteria:

- congruence lane cannot overreach
- public-only screening stays bounded
- operator-integrated cases can become stronger without violating claim discipline

Tests:

- `test_system_consistency_validator_congruence.py`

---

### `CGI-20` Multi-Case Congruence Certification

Purpose:

- certify the lane across multiple families, not just one flagship case

Owner:

- governance + runtime certification scripts

Main files:

- new certification docs in `governanza/automation-base/`

Changes required:

- certify:
  - One Vanderbilt
  - Wilsonart
  - weak address-first case
  - one logistics / warehouse case
  - one PF / reactive-sensitive case

Dependencies:

- `CGI-19`

Acceptance criteria:

- all five case classes pass their intended posture:
  - strong screening
  - structural redesign
  - weak degraded classification
  - logistics congruence
  - power-quality bounded hypothesis

Tests:

- certification bundle

---

## Recommended Execution Order

### Wave 1

- `CGI-01`
- `CGI-02`
- `CGI-03`
- `CGI-04`
- `CGI-05`

### Wave 2

- `CGI-06`
- `CGI-07`
- `CGI-08`

### Wave 3

- `CGI-09`
- `CGI-10`
- `CGI-11`

### Wave 4

- `CGI-12`
- `CGI-13`
- `CGI-14`

### Wave 5

- `CGI-15`
- `CGI-16`
- `CGI-17`
- `CGI-18`
- `CGI-19`
- `CGI-20`

## Stop Conditions

Pause and review architecture if any of these happen:

- `motor_016/017/025` need major rewrite before `CGI-17`
- current body compression starts expanding materially
- evidence-state enums need breaking changes
- public research starts being used as fake local truth
- the new lane begins to duplicate `structural_intelligence` instead of enriching it

## Final Closure Standard

This backlog is closed only if:

1. the system can investigate asset families deeply without overclaiming locally
2. the system can bind research context to local evidence explicitly
3. the system can reason about process, subsystem, finance, maintenance and regulation together
4. the system can block unfair comparisons and bad measurement instinct
5. the current thesis-first publication model remains intact
