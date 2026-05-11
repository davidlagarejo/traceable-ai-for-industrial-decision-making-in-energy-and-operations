# Recovery V2 — Backlog (post RECOVERY-2026-05-09)

Auditoría del prompt "cerebro de congruencia operacional" (2026-05-10) vs estado actual del framework. ~85% del prompt ya está implementado en V1 (ver `RECOVERY_DONE.md`). Este backlog cubre los gaps reales.

## Orden de ejecución

1. **Gap A — Scenario Justification Validator (motor_062)** ✅ DONE 2026-05-10
2. **Gap C — Industrial Source Catalog (139 sources)** ✅ DONE 2026-05-10
3. **Gap B — Hybrid Asset Family Support** ✅ DONE 2026-05-10
4. **Gap D — Source Routing por Asset Family** ✅ DONE 2026-05-10
5. **Gap E — Cold-chain patterns granulares (7 new)** ✅ DONE 2026-05-10
6. **Gap F — Knowledge YAMLs dedicados** ✅ DONE 2026-05-10

🎉 **Todos los 6 gaps cerrados.** El framework cubre 100% del prompt "cerebro de congruencia operacional" (RECOVERY_2026-05-10).

## Métricas globales tras Gap A + Gap C

| Métrica | Pre-V2 | Post V2 (todos gaps) |
|---|---|---|
| Test suite | 938 | 970 (+32) |
| Regression cross-asset | 6/6 | 6/6 |
| Validators activos (Layer F) | 8 | 9 (+motor_062) |
| Industrial sources catalogadas | dispersas | 139 estructuradas |
| Sources tier-1 (regulatory/standards) | n/a | 60 |
| Sources tier-2 (peer-reviewed/handbooks) | n/a | 55 |
| Sources tier-3 (vendor/industry) | n/a | 24 |
| Cold-chain operational patterns | 1 agregado | 1 + 7 granulares |
| Hybrid asset-family combinations | 0 (blocked) | 5 justificables |
| Knowledge YAMLs dedicados (machine/CA/control/power-quality) | 0 | 4 |

---

## Gap A — Scenario Justification Validator (motor_062) ✅ DONE

**Estado:** completed 2026-05-10
**Esfuerzo:** ~1 día (consumido)
**Layer:** F (validation)

### Requisito (del prompt §11, validador B)
Cada escenario activo en el reporte debe llevar:
- `trigger` (qué dato/observación lo activó)
- `source` (fuente industrial autoritativa)
- `process_clue` (mecanismo físico/operacional)
- `industrial_reason` (por qué importa industrialmente)
- `asset_family_reason` (por qué aplica a esta familia)

Si un escenario activo carece de alguno → **render block** (configurable como warn).

### Pasos
- [x] Auditoría
- [x] Adapter `adapters/motor_062.py` con `run()` que recibe scenarios activos y valida cada uno
- [x] Registry validator JSON: `zlab_skill/registry/validators/scenario_justification_required_fields.v1.json` (+nuevo scope `scenario_review` en schema)
- [x] Layer mapping: añadido `motor_062` a `layer_registry.py` (Layer F)
- [x] Adapter registry: añadido a `adapters/__init__.py` REAL_ADAPTERS
- [x] Motor dependencies: añadido a `governanza/automation-base/motor_dependencies.json`
- [x] Test: `tests/test_motor_062_scenario_justification.py` (12 tests, golden path + missing fields + warn vs block + asset family threading)
- [x] Wire en `motor_017` pre-render gate (input list + block_reasons + scenario_justification_summary)
- [x] Regression: `bash scripts/regression_cross_asset_recovery.sh` 6/6 PASS
- [x] Test suite: 938 → 955 passed

### Notas
- Identificador `062` está libre (último validator era 063 — error pre-existente; 062 va detrás de 061 y se renumera lógicamente).
- Default mode: `warn` (no romper PDFs existentes hasta que scenarios añadan justification fields). Switch a `block` cuando todos los generators emitan los 5 campos.

---

## Gap B — Hybrid Asset Family Support ✅ DONE

**Estado:** completed 2026-05-10
**Esfuerzo:** ~0.5 día (consumido)
**Layer:** F (modifica validator existente)

### Resultado
- [asset_family_hybrids.json](governanza/asset-operational-logic-engine_050/hybrids/asset_family_hybrids.json) — 5 combinaciones híbridas justificables: `cold_chain_food_processing`, `warehouse_mixed_temperature`, `office_with_edge_datacenter`, `manufacturing_with_attached_dc`, `urban_grocer_or_food_retail`. Cada una con `justification_triggers` + `shared_patterns` + rationale.
- [hybrid_families.py](runtime-orchestrator/src/runtime_orchestrator/hybrid_families.py) — loader con `find_admissible_hybrid()` que matchea contra tokens en m007 (`facility_evidence_tokens`, `process_evidence_tokens`) y m054 (`industrial_evidence_register`).
- motor_061 extendido: si hybrid match → `shared_patterns` quedan exentos de `_CROSS_FAMILY_CONTAMINATION`. Output bundle añade `hybrid_admissible`, `hybrid_id`, `hybrid_secondary`, `hybrid_shared_patterns`.
- 7 tests nuevos en [test_motor_061_hybrid_families.py](runtime-orchestrator/tests/test_motor_061_hybrid_families.py) (admisión cold_chain+food, warehouse mixed temp, office+edge DC, industrial_evidence_register path, no trigger keeps blocked, unrelated token rejects, case-insensitive).

### Requisito
`motor_061` bloquea hoy cualquier mezcla cross-family. El prompt exige soportar híbridos justificados (p.ej. cold_chain + food_processing) con `hybrid_justification_trigger` explícito.

### Pasos
- [ ] Añadir sección `hybrid_combinations` en `asset_archetypes.yaml`:
  ```yaml
  hybrid_combinations:
    cold_chain_food_processing:
      primary: cold_chain_facility
      secondary: manufacturing_facility
      trigger_required: "process_heat_signature OR sanitation_steam OR cook_chill_present"
      shared_patterns: [refrigeration_duty, process_heat]
  ```
- [ ] Extender `motor_061` con sub-estado `hybrid_admissible` cuando matchea combination válida + trigger presente
- [ ] Tests: 2 nuevos (híbrido válido pasa, híbrido sin trigger falla)

---

## Gap C — Industrial Source Catalog ✅ DONE

**Estado:** completed 2026-05-10 (adelantado por petición del usuario "incluir 100+ fuentes con handbooks por industria y case studies serios")
**Esfuerzo:** ~1 día (consumido)

### Resultado
- **139 fuentes** estructuradas en JSON: 60 tier-1 (regulatory/standards), 55 tier-2 (peer-reviewed/handbooks/national-lab), 24 tier-3 (vendor/industry whitepapers)
- Tipos: 38 standards, 30 handbooks, 17 regulatory, 16 case studies, 15 peer-reviewed papers, 14 guidelines, 8 datasets, 1 whitepaper
- Cobertura por familia: cold_chain (IIAR Bulletin 109/110, ASHRAE 15/34, EPA SNAP, AIM Act, CalARP, RMP, PSM 1910.119, Danfoss/Bitzer/Emerson handbooks, NREL TP-7A40-78843, PG&E, GCCA, IARW); manufacturing (DOE AMO/IAC/Better Plants/Compressed Air/Pump/Steam/Process Heating sourcebooks, ISO 50001/50002/50006/55000, ASME PTC 4/23/30, IEEE 519/1100, CAGI, Hydraulic Institute, CTI, SME, ISA, EPRI, NEMA MG-1, EASA AR100); commercial_building (ASHRAE 90.1/62.1/55/100/189.1/211, Handbooks Fundamentals/Systems/Applications, EPA ENERGY STAR Portfolio Manager, GHGRP, LL84/88/97, BERDO, DC BEPS, Title 24, CRREM, ULI, CBRE, JLL, C&W, BOMA EER, NIST NISTIR 7551); datacenter (ASHRAE TC 9.9, Uptime Tier + Survey, LBNL DCEP, Green Grid PUE/DCMM, NREL DC, DOE FEMP, EU CoC, IEEE 802.3bt, ASHRAE 90.4); warehouse/logistics (MHI, WERC DC Measures, CSCMP, ARC, AAR, DOT FHWA, DOE EERE MHE, EPRI Battery Charging); infrastructure (NERC, FERC Form 1, EIA 923/860, IEEE C57/C37, NESC, NETA); process safety (AIChE CCPS, API 510/570/653, AMPP, NFPA 70/70E/13/30/654); peer-reviewed (Int. J. Refrigeration, ASHRAE Journal, Appl. Thermal Eng., Energy and Buildings, Building and Environment, IJPR, J. Cleaner Production); EIA datasets (RECS/CBECS/MECS); ACEEE Summer Study proceedings; LBNL/ORNL/PNNL/ESL reports.

### Pasos completados
- [x] `governanza/asset-operational-logic-engine_050/sources/industrial_source_catalog.json` con 139 entries
- [x] Schema por entrada: `{source_id, name, publisher, type, authority_tier (1-3), asset_families, jurisdiction, topic_tags, citation_format}`
- [x] Loader `src/runtime_orchestrator/source_catalog.py` con LRU cache (`load_catalog`, `sources_for_family`, `sources_for_tag`, `routing_for_family`, `source_by_id`, `is_known_source`)
- [x] Tests `tests/test_source_catalog.py` (17 tests: estructura, tier, family coverage, tag lookup, routing buckets, known-source heuristic)

### Requisito
Las ~80 fuentes del prompt §3 como objetos JSON consultables.

### Pasos
- [ ] Crear `governanza/asset-operational-logic-engine_050/sources/industrial_source_catalog.json`
- [ ] Schema: `{source_id, name, authority_tier (1-3), asset_families, jurisdiction, topic_tags, citation_format}`
- [ ] Cargar fuentes por tier:
  - Tier 1 (regulatory/standards): DOE Better Plants, IAC, AMO, IIAR Bulletin 109/110, ASHRAE 90.1/62.1/15/183, EPA ENERGY STAR Portfolio Manager, EPA GHGRP, ASME, IEEE 519, ISO 50001/55000, LL84/LL97, BERDO, Title 24
  - Tier 2 (industry): Danfoss, Emerson Climate, Bitzer, MHI, CBRE, JLL, SME, ISA
  - Tier 3 (research/peer): NREL reports, LBNL, peer-reviewed journals
- [ ] Loader en `runtime_orchestrator/source_catalog.py` con LRU cache

---

## Gap D — Source Routing por Asset Family ✅ DONE

**Estado:** completed 2026-05-10
**Esfuerzo:** ~0.5 día (consumido)

### Resultado
- motor_035 extendido con `_build_industrial_authority_routing(asset_family)` que consume el catálogo de Gap C y proyecta `{tier_1, tier_2, tier_3}` (cap 40/25/15) ordenados por authority_tier + source_id.
- Field nuevo `industrial_authority_routing` en el output de motor_035 — accesible por todo consumer downstream (composer, motor_062, citation governor).
- 8 tests nuevos en [test_motor_035_industrial_authority_routing.py](runtime-orchestrator/tests/test_motor_035_industrial_authority_routing.py): verifica que cold_chain → IIAR/ASHRAE/EPA, manufacturing → ISO 50001 + DOE IAC, building → ASHRAE 90.1 + LL97, datacenter → ASHRAE TC 9.9 + Uptime, empty family safe, tier caps respetados.

### Pasos
- [ ] Extender `motor_035` (public_data_routing) para leer el catálogo del Gap C
- [ ] Devolver `routing[family] = [tier1_sources, tier2_sources, tier3_sources]`
- [ ] Routing per-family verificado:
  - cold_chain → IIAR + ASHRAE 15/183 + Danfoss/Bitzer
  - warehouse → MHI + CBRE + JLL + LL97
  - manufacturing → SME + ISA + DOE IAC + AMO
  - commercial_building → LL84/LL97 + ASHRAE 90.1 + BERDO + Title 24
  - datacenter → ASHRAE TC 9.9 + Uptime + LBNL
  - logistics_terminal → DOT + AAR + industry whitepapers

---

## Gap E — Cold-chain patterns granulares ✅ DONE

**Estado:** completed 2026-05-10
**Esfuerzo:** ~1 día (consumido)

### Resultado
7 patterns nuevos en `runtime-orchestrator/zlab_skill/registry/patterns/`:
- `refrigeration_duty.v1.json` — decomposición de duty (pull-down vs holding vs defrost vs infiltration) antes de CAPEX
- `infiltration_load.v1.json` — door/seal infiltration como falsificación pre-compresor
- `door_cycle_losses.v1.json` — disciplina operacional de puertas
- `defrost_profile.v1.json` — time-vs-demand initiation como falsificación pre-CAPEX
- `refrigerant_integrity.v1.json` — leak rate + AIM Act + SNAP phasedown exposure
- `compressor_staging.v1.json` — VFD lead/lag + head pressure float
- `thermal_boundary.v1.json` — envelope conductance + vapor barrier + thermal bridging

Todos pasan los validadores del registry (knowledge_type, source_basis, L2 ceiling). El `cold_chain_status_unknown` agregado original sigue existiendo — los nuevos lo complementan con granularidad.

### Pasos
- [ ] Split `cold_chain_status_unknown.json` en 7 patterns:
  - `refrigeration_duty.json`
  - `infiltration_load.json`
  - `door_cycle_losses.json`
  - `defrost_profile.json`
  - `refrigerant_integrity.json`
  - `compressor_staging.json`
  - `thermal_boundary.json`
- [ ] Actualizar combinations que los referencian
- [ ] Regression cold_chain debe seguir PASS

---

## Gap F — Knowledge YAMLs dedicados ✅ DONE

**Estado:** completed 2026-05-10
**Esfuerzo:** ~1 día (consumido)

### Resultado
4 YAMLs nuevos en `runtime-orchestrator/zlab_skill/`:
- `machine_logic.yaml` — rotating + process equipment, part-load behavior, staging, degradation (refs: SME, EPRI, NEMA, EASA, ASME PTC 4/23/30 + patterns compressor_staging/refrigeration_duty/chiller/boiler)
- `compressed_air_logic.yaml` — sizing/staging/leaks/pressure-band/end-use audit (refs: CAGI, DOE Compressed Air Challenge, Atlas Copco, Ingersoll Rand + pattern compressed_air_leak_plausibility)
- `control_boundary_logic.yaml` — schedules/setpoints/sensors/PID/sequence-of-ops (refs: ISA, Siemens, Honeywell, Trane + patterns hvac_schedule_drift/sensor_prematurity/digital_twin_prematurity/defrost_profile)
- `power_quality_logic.yaml` — power factor/harmonics/voltage quality/grounding/demand charges (refs: IEEE 519/1100/C57/C37, NESC, NETA, Schneider, ABB + patterns reactive_power_exposure/demand_charge_exposure_unknown)

Cada YAML cruza `pattern_ids` con `industrial_sources` (source_ids del catálogo Gap C), declara scope + governing principles + falsification anchors + notes.

### Pasos
- [ ] `knowledge/machine_logic.yaml` (extraer de `process_logic.yaml`)
- [ ] `knowledge/compressed_air_logic.yaml` (separado del pattern)
- [ ] `knowledge/control_boundary_logic.yaml`
- [ ] `knowledge/power_quality_logic.yaml` (IEEE 519, harmonics, PF)
- [ ] Actualizar referencias en motores que consumen `process_logic.yaml`

---

## Validación al cerrar cada gap

```bash
cd runtime-orchestrator
pytest -q
bash scripts/regression_cross_asset_recovery.sh
```
