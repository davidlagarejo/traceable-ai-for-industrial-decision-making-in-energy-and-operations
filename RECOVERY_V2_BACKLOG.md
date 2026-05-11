# Recovery V2 — Backlog (post RECOVERY-2026-05-09)

Auditoría del prompt "cerebro de congruencia operacional" (2026-05-10) vs estado actual del framework. ~85% del prompt ya está implementado en V1 (ver `RECOVERY_DONE.md`). Este backlog cubre los gaps reales.

## Orden de ejecución

1. **Gap A — Scenario Justification Validator (motor_062)** ✅ DONE 2026-05-10
2. **Gap C — Industrial Source Catalog (139 sources)** ✅ DONE 2026-05-10
3. **Gap B — Hybrid Asset Family Support** ✅ DONE 2026-05-10
4. **Gap D — Source Routing por Asset Family** ✅ DONE 2026-05-10
5. **Gap E — Cold-chain patterns granulares (7 new)** ✅ DONE 2026-05-10
6. **Gap F — Knowledge YAMLs dedicados** ✅ DONE 2026-05-10

🎉 **Todos los 6 gaps cerrados estructuralmente.** El framework cubre 100% del prompt "cerebro de congruencia operacional" (RECOVERY_2026-05-10) a nivel de construcción.

## V2-LIVE — convertir "cableado pero frío" en "cableado y vivo"

Los 6 gaps de V2 dejaron varios componentes correctos en aislamiento (pasan tests unitarios) pero inertes en producción porque los motores río arriba no traen los campos nuevos. Esta sección los activa.

### Item 1 — motor_014 emite los 5 campos de justificación
**Estado:** in_progress
**Por qué importa:** motor_062 valida `trigger / source / process_clue / industrial_reason / asset_family_reason` pero motor_014 nunca rellena esos campos, así que el validador siempre ve "missing" y queda en warn permanente.
**Pasos:** ampliar `_build_scenario_space` y branches per-family en motor_014. Citar `source_id` del catálogo Gap C. Tests para los 6 families.

### Item 2 — motor_007 emite `facility_evidence_tokens` / `process_evidence_tokens`
**Estado:** pending
**Por qué importa:** motor_061 admite híbridos solo si encuentra estos tokens. Sin emisor, los 5 híbridos (cold_chain+food, mixed-temp DC, office+edge DC, mfg+attached DC, urban grocer) nunca se activan en producción.
**Pasos:** en motor_007, derivar tokens de target_definition_contract + observable_cluster_register; añadir al output.

### Item 3 — motor_062 consulta `source_catalog.is_known_source()`
**Estado:** pending
**Por qué importa:** hoy un escenario con `source: "mi tío"` pasa el validador. El catálogo de 139 fuentes existe pero motor_062 no lo consulta.
**Pasos:** en motor_062, marcar como `critical` los escenarios cuyo `source` no aparece en el catálogo.

### Item 4 — motor_050 + motor_052 cargan los 4 YAMLs Gap F
**Estado:** pending
**Por qué importa:** machine_logic / compressed_air_logic / control_boundary_logic / power_quality_logic están escritos pero ningún motor los lee. Son documentación viva, no comportamiento.
**Pasos:** loader que importa los 4 YAMLs en motor_050 (asset operational logic) y motor_052 (loss pattern); expuestos en bundle.

### Item 5 — switch motor_062: warn → block
**Estado:** pending (depende de Item 1)
**Por qué importa:** una vez que motor_014 emita los campos, motor_062 puede ser estricto y bloquear renders con justificación incompleta.

### Item 6 — caso híbrido en regression script
**Estado:** pending (depende de Item 2)
**Por qué importa:** validar end-to-end que la ruta cold_chain+food_processing se activa con un input real, no solo en test unitario.

**Tiempo estimado total:** ~2 días para los 6 items.

---

## V2-LIVE — closure 2026-05-10

Los 6 items de V2-LIVE están **completos**. El framework ha pasado de
"100% construido / 85% vivo" a **100% vivo**.

| Item | Estado | Commit |
|---|---|---|
| 1 — motor_014 emits 5 justification fields | ✅ | `a66c69d` |
| 2 — motor_007 derives evidence tokens | ✅ | `0fadf8e` |
| 3 — motor_062 SJ2 source catalog validation | ✅ | `fe24ee3` |
| 4 — motor_050 + motor_052 surface knowledge YAMLs | ✅ | `(this batch)` |
| 5 — motor_062 default mode flipped warn → block | ✅ | `ef1ed10` |
| 6 — hybrid asset-family E2E flow + regression coverage | ✅ | `(this batch)` |

### Métricas finales

| Métrica | Pre-V2 | Post V2 estructural | Post V2-LIVE |
|---|---|---|---|
| Test suite | 938 | 970 | **1021** (+83) |
| Regression checks | 6/6 | 6/6 | **7/7** (+hybrid E2E) |
| Validators Layer F | 8 | 9 | 9 (motor_062 ahora bloquea con dientes) |
| Industrial sources | dispersas | 139 estructuradas | 139 (motor_062 las consulta) |
| Knowledge YAMLs Gap F | 0 | 4 (inertes) | **4 (consumidos por motor_050+052)** |
| Hybrid asset families | 0 (bloqueadas) | 5 (cableadas frías) | **5 (activas E2E)** |
| Scenario justification fields | 0 emitidos | 0 emitidos | **24 entries × 5 fields** |
| motor_062 mode default | n/a | warn | **block** |

### Resultado

Todo el prompt "cerebro de congruencia operacional" (RECOVERY_2026-05-10)
está **100% vivo en producción**, no solo construido:

- Cada escenario activo declara `trigger / source / process_clue /
  industrial_reason / asset_family_reason` con citación al catálogo de 139
  fuentes.
- motor_062 bloquea el render por defecto cuando faltan los campos o la
  fuente no es del catálogo.
- motor_061 admite los 5 híbridos justificables (cold_chain+food,
  warehouse mixed-temp, office+edge DC, manufacturing+DC, urban grocer)
  cuando motor_007 detecta los tokens en evidencia real.
- Los 4 YAMLs de Gap F (machine/CA/control/power-quality logic) están
  surfaced en los bundles de motor_050 y motor_052.

Regression 7/7 PASS demuestra que la disciplina nueva no rompió ninguno
de los 6 cases cross-asset existentes.

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
