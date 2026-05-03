# Runtime Congruence Reference Mapping Matrix

Produced at: 2026-04-30

## Purpose

This matrix classifies the current Zircular reference assets into:

- canonical intake packs
- research corpus
- loss-pattern seeds
- measurement / hardware logic seeds
- operational logic seeds

The goal is to prevent a direct copy of legacy forms and checklists into the new runtime.

## Mapping Rules

- `intake` means: convert into structured case-specific inputs
- `research corpus` means: use to understand asset families and recurring logic
- `pattern seed` means: use as a bounded hypothesis source, never local diagnosis
- `measurement seed` means: use to shape minimality logic, never auto-install logic
- `do not render directly` means: this source should not appear as a client-facing section by itself

## Matrix

| Reference | Primary Role | Canonical Destination | Why It Matters | What It Must Not Become |
|---|---|---|---|---|
| `Form_Zircular_for_Developer.xlsx` | intake | `building_identity_pack`, `public_asset_intake_overlay` | Establishes building identity, typology and initial public-record framing | Universal operating model for all assets |
| `Electricidad.docx` | intake + pattern seed | `utility_and_tariff_pack`, `measurement_and_metering_pack`, `power_quality_hypothesis_register` | Captures meters, PF, peak logic, major loads | Direct recommendation engine |
| `Motores y ventilacion.docx` | intake + pattern seed | `subsystem_inventory_pack`, `equipment_dominance_pack`, `loss_pattern_library` | Seeds motor / VFD / oversizing / idle operation logic | Local diagnosis that motors are inefficient |
| `Enfriadora agua.docx` | intake + operational seed | `subsystem_inventory_pack`, `process_overview_pack`, `measurement_strategy_register` | Seeds chiller / cooling-duty context | Standalone optimization prescription |
| `Termica y aire.docx` | intake + pattern seed | `process_overview_pack`, `subsystem_inventory_pack`, `regulatory_and_permit_pack`, `loss_pattern_library` | Seeds combustion, fuel, steam, compressed-air and thermal logic | Local thermal-loss diagnosis as fact |
| `Agua y residuos.docx` | intake + pattern seed | `process_overview_pack`, `loss_hypothesis_register`, `waste_stream_context_pack` | Seeds reuse, leakage, waste and solvent / recycling logic | Unverified leak or waste claims |
| `Materia prima.docx` | intake | `logistics_pack`, `process_overview_pack`, `input_flow_pack` | Captures input flow, storage, unloading, forklift and flow friction | Generic logistics story detached from process |
| `Producto terminado.docx` | intake | `logistics_pack`, `output_flow_pack`, `storage_and_dispatch_pack` | Captures packing, storage, loading, waste and sensor-related operational context | Generic warehouse efficiency claims |
| `consumo mensual.docx` | intake | `schedule_and_utilization_pack`, `operating_schedule_proxy_pack` | Captures real start-up, breaks, Sundays, holidays, idle periods | Flat occupancy schedule assumption |
| `Subsistemas.docx` | intake | `subsystem_inventory_pack` | Captures secondary systems and operating hours | Mere appendix list of equipment |
| `Mejoras por tipo de industria.docx` | intake + comparison seed | `throughput_proxy_pack`, `fair_comparison_profile`, `peer_normalization_inputs` | Provides area, annual production, hours, cost and consumption normalization fields | Area-only benchmarking |
| `Mejoras por equipos.docx` | intake + maintenance seed | `maintenance_maturity_pack`, `subsystem_inventory_pack`, `schedule_and_utilization_pack` | Captures maintenance plan, predictive / preventive state and equipment counts | Premature equipment recommendation list |
| `selfassessment.pdf` | research corpus + pattern seed | `asset_family_research_library`, `loss_pattern_library` | Encodes IAC-style process / utility / equipment / measure logic | Direct measure recommendation engine |
| `IAC_Database.xls` | research corpus + pattern seed | `loss_pattern_library`, `gold_nugget_seed_library` | Historical industrial measure patterns and logic | Site-specific recommendation proof |
| `Hardware_ES.pdf` | measurement seed | `measurement_decision_tree`, `hardware_minimality_decision_tree` | Useful for staged measurement logic and communication-path decisions | Bias toward hardware-first thinking |
| `Dexma_Checklist_Hardware_ES.pdf` | measurement seed | `measurement_decision_tree`, `hardware_minimality_decision_tree` | Useful for minimum viable metering strategy logic | Auto-trigger for submetering or device rollout |
| `ENERGY STAR Plant Posters (Spanish).pdf` | culture / execution seed | `culture_execution_proxy_register`, `loss_pattern_library` | Can seed behavioral and ownership signals | Proof of actual discipline at a site |
| `CIRCUTOREEE.pdf` | research corpus | `sectoral_guidance_library` | Can support sectoral context and broader operational framing | Local diagnostic authority |

## Migration Priority

### Wave 1

- `Form_Zircular_for_Developer.xlsx`
- `Electricidad.docx`
- `Termica y aire.docx`
- `Subsistemas.docx`
- `consumo mensual.docx`
- `Mejoras por tipo de industria.docx`

### Wave 2

- `Materia prima.docx`
- `Producto terminado.docx`
- `Agua y residuos.docx`
- `Motores y ventilacion.docx`
- `Enfriadora agua.docx`
- `Mejoras por equipos.docx`

### Wave 3

- `selfassessment.pdf`
- `IAC_Database.xls`
- `Hardware_ES.pdf`
- `Dexma_Checklist_Hardware_ES.pdf`
- `ENERGY STAR Plant Posters (Spanish).pdf`
- `CIRCUTOREEE.pdf`

## Non-Negotiable

None of these references should be allowed to bypass:

- claim governance
- local evidence binding
- fair comparison logic
- measurement minimality
- thesis compression

They are substrate assets, not direct truth surfaces.
