# Runtime Asset-First Hardening Backlog

## 1. Propósito

Este backlog define la re-arquitectura operativa necesaria para que el framework:

- evalúe **activos físicos** y no principalmente compañías,
- pueda arrancar desde una **dirección** o identificador físico mínimo,
- construya un **prior técnico asset-first** antes de amplificar contexto financiero,
- y deje de emitir entregables que aparentan completitud cuando Fases 1–3 siguen materialmente débiles.

Este documento no redefine la constitución de las 8 fases. Implementa su endurecimiento en el runtime.

## 2. Diagnóstico que gobierna este backlog

El problema actual no es solo de copy o layout. Es un fallo de gobernanza runtime:

1. El sujeto real del caso no está suficientemente fijado como `asset`.
2. El intake puede quedar casi vacío en observables físicos y aun así avanzar.
3. Las fuentes `issuer-level` y SEC/XBRL entran densas y estructuradas.
4. Las fases físicas y operativas salen pobres.
5. El Decision Core y el reporte amplifican el frente financiero porque es el más poblado.
6. El sistema publica un producto con apariencia de TDIR cuando el activo todavía no ha sido ganado epistemológicamente.

## 3. Leyes de implementación

Estas leyes deben volverse enforcement runtime:

### 3.1 Asset-target precedence

Cuando `target_scope = asset`, ninguna evidencia `issuer-level` puede compensar insuficiencia material `asset-level`.

### 3.2 No-compensation rule

SEC, XBRL, earnings, debt, revenue, governance o filings corporativos pueden alimentar contexto de Fase 5 o ciertos frentes de Fase 8, pero no pueden poblar Fases 1–3 por sustitución.

### 3.3 Synthetic completeness prohibition

Si Fases 1–3 no están materialmente pobladas, el sistema no puede emitir `TDIR` como clase documental principal.

### 3.4 Scope parity rule

Ninguna sección `issuer-level` puede tener más fuerza narrativa, visual o numérica que la capa `asset-level` cuando el caso es `asset-first`.

### 3.5 Technical entitlement rule

El lenguaje técnico-operativo fuerte solo es admisible cuando el activo ya tiene observables mínimos suficientes.

### 3.6 Report identity rule

El runtime debe decidir primero qué tipo de documento es admisible y solo después componerlo.

## 4. Estado objetivo

Al final de este backlog, el runtime debe poder:

- iniciar un `asset_case` con una dirección,
- clasificar el tipo de activo,
- enrutar familias de fuentes correctas por tipología e industria,
- construir un `preliminary_physical_prior` útil,
- distinguir claramente entre evidencia `asset-level`, `jurisdiction-level`, `benchmark-level` e `issuer-level`,
- degradar el reporte cuando el activo esté subcaracterizado,
- y producir TAD que priorice comprender el activo antes de interpretar financieramente.

## 5. Nuevos contratos obligatorios

## 5.1 `target_definition_contract`

Campos mínimos:

- `target_scope`
- `target_type`
- `target_identifier`
- `target_name`
- `address_raw`
- `geocode_status`
- `jurisdiction_scope`
- `owner_entity`
- `operator_entity`
- `report_intent`
- `decision_intent`
- `case_mode`

## 5.2 `asset_context_readiness_contract`

Estados mínimos:

- `issuer_context_only`
- `location_only`
- `asset_context_insufficient`
- `asset_context_minimal`
- `asset_context_operable`
- `asset_context_hardened`

## 5.3 `scope_lineage_contract`

Cada objeto, fuente, evidencia, inferencia, gráfico y bloque de reporte debe declarar:

- `scope_level`
- `subject_binding`
- `phase_eligibility`
- `semantic_ceiling`

## 5.4 `report_identity_state_contract`

Clases documentales mínimas:

- `Issuer Context Memo`
- `Target Ambiguity Memo`
- `Asset Context Seed Brief`
- `Asset Context Insufficiency Brief`
- `Pre-Verification Asset Brief`
- `TDIR Preliminary`
- `Decision-Grade TDIR`
- `Verification-Supported Report`

## 6. Observable clusters obligatorios

El runtime debe medir cobertura mínima por cluster:

- `location_cluster`
- `jurisdiction_cluster`
- `geometry_size_cluster`
- `vintage_structure_cluster`
- `use_program_cluster`
- `operating_regime_cluster`
- `fuel_energy_cluster`
- `systems_cluster`
- `regulatory_cluster`
- `benchmark_mapping_cluster`

Reglas mínimas:

- Si menos de 4 clusters están poblados, no puede salir `TDIR`.
- Si `geometry_size_cluster`, `use_program_cluster` y `fuel_energy_cluster` están vacíos, el caso debe degradarse a `Asset Context Insufficiency Brief`.
- Si solo hay `location + issuer`, el sistema debe producir `location_only` o `issuer_context_only`.

## 7. Taxonomía de activos objetivo

`target_type` mínimo:

- `commercial_building`
- `multifamily_building`
- `hospital`
- `hotel`
- `warehouse_distribution`
- `data_center`
- `industrial_plant`
- `manufacturing_facility`
- `food_processing_facility`
- `cold_chain_facility`
- `oil_gas_upstream_site`
- `oil_gas_midstream_facility`
- `oil_gas_downstream_facility`
- `water_wastewater_facility`
- `campus`
- `infrastructure_node`

## 8. Taxonomía de familias de fuentes

El discovery debe enrutar por familia:

- `geospatial_public_record`
- `parcel_assessor_record`
- `building_permitting_record`
- `benchmarking_disclosure_record`
- `climate_normals_record`
- `utility_tariff_record`
- `code_regulation_record`
- `facility_directory_record`
- `engineering_specification_record`
- `sustainability_disclosure_record`
- `industrial_process_reference`
- `sector_energy_intensity_reference`
- `technology_archetype_reference`
- `equipment_typology_reference`
- `emissions_compliance_record`
- `issuer_financial_record`

Orden de precedencia para `asset_case`:

1. localización y registros físicos
2. tipología y uso
3. clima y jurisdicción
4. tamaño, vintage y configuración
5. clues de fuel y sistemas
6. benchmarking local o sectorial
7. regulación aplicable
8. tarifas y costos
9. contexto financiero del issuer

## 9. Priors técnicos por tipología e industria

Debe crearse el objeto `asset_energy_behavior_prior` con:

- `sector_energy_intensity_band`
- `end_use_split_hypothesis`
- `load_shape_hypothesis`
- `operating_regime_expectation`
- `system_typology_expectation`
- `climate_sensitivity_expectation`
- `peak_behavior_expectation`
- `anomaly_candidates`

Este prior debe enrutar según `target_type` y, cuando aplique, `subsector`.

Ejemplos mínimos:

- edificios: oficina, multifamily, hotel, hospital, data center, retail, warehouse
- manufactura: alimentos, bebidas, cold storage, metales, químicos, pharma, electrónica, textiles
- oil & gas: upstream, gathering, compression, processing, LNG, refining, terminal/storage

## 10. Secuencia de implementación

El orden correcto es:

1. gobernanza runtime
2. intake y sujeto
3. readiness y clusters
4. routing de fuentes
5. prior físico
6. Decision Core
7. packaging y gráficos
8. belief update / publication freeze
9. TAD

No debe invertirse este orden.

## 11. Backlog ejecutable por etapa

## 11.1 Etapa A — Gobernanza base del runtime

### Epic A1 — Introducir contratos de sujeto, scope y clase documental

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/models.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_002.py`
- `runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py`
- `governanza/automation-base/motor_dependencies.json`

**Tareas**

- A1.1 Añadir `target_definition_contract` al modelo runtime.
- A1.2 Añadir `report_identity_state` al estado del run.
- A1.3 Añadir `dominant_evidence_scope` al manifiesto runtime.
- A1.4 Hacer obligatorio `target_scope`.
- A1.5 Rechazar o degradar casos que no declaren sujeto analítico válido.

**Criterios de aceptación**

- Un caso sin `target_scope` no puede entrar como `asset_case`.
- Un caso con `target_scope = asset` queda marcado como tal desde el inicio del grafo.
- El run manifiesta explícitamente `report_identity_state`.

**Dependencias**

- Ninguna.

### Epic A2 — Enforce de leyes de no compensación

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/base.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py`

**Tareas**

- A2.1 Añadir `asset_target_precedence`.
- A2.2 Añadir `no_compensation_violation`.
- A2.3 Añadir `synthetic_completeness_violation`.
- A2.4 Añadir `scope_parity_violation`.

**Criterios de aceptación**

- El runtime puede detectar cuando evidencia `issuer-level` domina un `asset_case`.
- La gobernanza puede degradar o congelar publicación por esta razón.

**Dependencias**

- A1.

## 11.2 Etapa B — Intake y asset context readiness

### Epic B1 — Parse asset-first del intake

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_003.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_004.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_005.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py`
- `runtime-orchestrator/inputs/*.json`

**Tareas**

- B1.1 Separar claramente `issuer_entity`, `asset_entity`, `site_entity`, `subsystem_entity`.
- B1.2 Extraer `address_raw`, `city`, `state`, `country`, `jurisdiction_codes` como núcleo físico.
- B1.3 Añadir inferencia preliminar de `target_type`.
- B1.4 Medir cobertura de los 10 observable clusters.
- B1.5 Emitir `asset_context_readiness`.

**Criterios de aceptación**

- Un input con solo dirección queda clasificado como `location_only` o `asset_context_minimal`, no como caso completo.
- El sistema informa exactamente qué clusters faltan.

**Dependencias**

- A1.

### Epic B2 — Preparar intake por dirección como primer modo legítimo

**Motores / archivos**

- `runtime-orchestrator/cli.py`
- `runtime-orchestrator/dashboard.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_004.py`

**Tareas**

- B2.1 Soportar `address_first` como `case_mode`.
- B2.2 Permitir crear caso sin ticker ni CIK.
- B2.3 Mostrar en UI que el caso es `asset-first`.

**Criterios de aceptación**

- Se puede iniciar un caso solo con dirección y `target_scope = asset`.

**Dependencias**

- B1.

## 11.3 Etapa C — Routing de fuentes y benchmark families

### Epic C1 — Source family registry

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_009.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_010.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_011.py`

**Tareas**

- C1.1 Añadir `source_family`.
- C1.2 Añadir `scope_level`.
- C1.3 Añadir `phase_eligibility`.
- C1.4 Añadir `technical_value`, `regulatory_value`, `financial_value`.
- C1.5 Hacer dedupe sin mezclar `issuer-level` y `asset-level`.

**Criterios de aceptación**

- Cada fuente queda etiquetada por family y scope.
- El pipeline puede distinguir claramente una fuente física local de un filing SEC.

**Dependencias**

- B1.

### Epic C2 — Discovery asset-first en `motor_028`

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py`
- `runtime-orchestrator/src/runtime_orchestrator/crawler_store.py`
- `runtime-orchestrator/src/runtime_orchestrator/config.py`

**Tareas**

- C2.1 Introducir `benchmark_routing_register`.
- C2.2 Introducir `source_scope_register`.
- C2.3 Priorizar geospatial, parcel, permit, local benchmark, climate, tariff.
- C2.4 Mover SEC/XBRL a contexto secundario.
- C2.5 Enrutar distinta familia de referencias para edificios, manufactura, alimentos y oil & gas.

**Criterios de aceptación**

- En un `asset_case`, SEC nunca aparece como fuente primaria de Fase 1.
- El artifact de `motor_028` muestra claramente qué familias de fuentes fueron usadas.

**Dependencias**

- C1.

## 11.4 Etapa D — Rehacer Phase 1 runtime

### Epic D1 — Nuevo `facility_prior` asset-first

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py`
- `governanza/public-data-engine_012/motor_state.json`

**Tareas**

- D1.1 Añadir `asset_identity_bundle`.
- D1.2 Añadir `climate_bundle`.
- D1.3 Añadir `geometry_proxy_bundle`.
- D1.4 Añadir `use_program_bundle`.
- D1.5 Añadir `operating_archetype_bundle`.
- D1.6 Añadir `asset_energy_behavior_prior`.
- D1.7 Añadir `system_typology_prior`.
- D1.8 Añadir `missing_physical_observables_register`.
- D1.9 Añadir `technical_prior_ceiling`.

**Criterios de aceptación**

- El prior físico no sale como “silenciosamente rico” cuando no lo es.
- El artifact distingue claramente lo observado, lo inferido, lo benchmark-only y lo faltante.
- Si el activo está pobre, el output principal de Phase 1 es la insuficiencia técnica, no el benchmark.

**Dependencias**

- B1, C2.

### Epic D2 — Priors energéticos por tipología/industria

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py`
- `runtime-orchestrator/src/runtime_orchestrator/config.py`

**Tareas**

- D2.1 Crear routing por `target_type`.
- D2.2 Crear routing por `subsector` cuando aplique.
- D2.3 Definir priors mínimos para:
  - edificios
  - manufactura
  - alimentos
  - oil & gas
- D2.4 Emitir `load_shape_hypothesis`, `end_use_split_hypothesis`, `system_typology_expectation`.

**Criterios de aceptación**

- Una oficina y una planta de alimentos ya no usan el mismo comportamiento energético implícito.
- El prior energético depende del activo, no del owner.

**Dependencias**

- D1.

## 11.5 Etapa E — Rehacer activación e inferencias

### Epic E1 — Activation by scope

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_013.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py`

**Tareas**

- E1.1 Separar casos:
  - `asset_physical_cases`
  - `asset_operational_cases`
  - `regulatory_cases`
  - `issuer_context_cases`
- E1.2 Evitar que casos issuer-level dominen la activación de `asset_case`.
- E1.3 Introducir `asset technical insufficiency` como inference case legítimo.

**Criterios de aceptación**

- Si Fase 1 está vacía, el sistema activa el frente correcto: insuficiencia del activo.
- No puede quedar un caso con blocker financiero cuando el verdadero blocker es técnico.

**Dependencias**

- D1.

### Epic E2 — Blocking logic corregida

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py`

**Tareas**

- E2.1 Añadir prioridad de bloqueo:
  - `target ambiguity`
  - `asset technical insufficiency`
  - `insufficient system observability`
  - `classification uncertainty`
- E2.2 Relegar leverage ambiguity cuando sea un frente secundario.

**Criterios de aceptación**

- El Decision Core refleja el verdadero límite epistemológico del caso.

**Dependencias**

- E1.

## 11.6 Etapa F — Rehacer packaging del reporte

### Epic F1 — Section eligibility y report identity

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_015.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py`

**Tareas**

- F1.1 Crear `section_eligibility_register`.
- F1.2 Crear `phase_population_map`.
- F1.3 Crear `report_identity_state`.
- F1.4 Reglas:
  - `C2` no sale normal si está vacío
  - `C5` no sustituye física por benchmark
  - `C9` pasa a apéndice cuando el activo sigue débil
- F1.5 Render específico por clase documental.

**Criterios de aceptación**

- Un `asset_context_insufficient` no se ve como `TDIR`.
- El reporte deja visible qué parte del activo no está comprendida.

**Dependencias**

- E2.

### Epic F2 — Rediseño de charts y prose

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py`

**Tareas**

- F2.1 Priorizar charts:
  - `asset context completeness`
  - `source scope map`
  - `climate/jurisdiction exposure`
  - `system hypothesis map`
  - `verification path by subsystem`
- F2.2 Reducir centralidad de:
  - revenue
  - debt
  - consolidated balance sheet
- F2.3 Mover la mejor prose a:
  - identidad física
  - sistema probable
  - incertidumbre técnica
  - verification path

**Criterios de aceptación**

- El informe deja de sentirse como memo financiero aunque exista contexto financiero.

**Dependencias**

- F1.

## 11.7 Etapa G — Endurecimiento de gobernanza y publicación

### Epic G1 — Belief revision por mismatch de scope

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_020.py`

**Tareas**

- G1.1 Añadir triggers:
  - `scope_mismatch_detected`
  - `issuer_dominance_detected`
  - `technical_underpopulation_detected`
  - `synthetic_completeness_detected`
- G1.2 Añadir consecuencias:
  - `degrade_report_identity`
  - `hold_for_asset_clarification`
  - `freeze_publication`

**Criterios de aceptación**

- El framework puede registrar formalmente este patrón como evento epistemológico.

**Dependencias**

- F1.

### Epic G2 — Publication freeze y delivery honesty

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py`
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py`

**Tareas**

- G2.1 Añadir chequeos de:
  - `issuer_dominance`
  - `scope_parity_violation`
  - `technical_phase_underpopulation`
  - `document_identity_violation`
- G2.2 Bajar `publication_ceiling` cuando esos triggers se encienden.
- G2.3 Exportar en el manifest:
  - `target_scope`
  - `report_identity_state`
  - `dominant_evidence_scope`
  - `phase_population_summary`

**Criterios de aceptación**

- El sistema puede bloquear un falso TDIR aunque el PDF sea renderizable.

**Dependencias**

- G1.

## 11.8 Etapa H — TAD corregido

### Epic H1 — Reordenar TAD hacia comprensión del activo

**Motores / archivos**

- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py`

**Tareas**

- H1.1 Priorizar:
  - `classify`
  - `retrieve_docs`
  - `confirm_use`
  - `confirm_systems`
  - `measure`
  - `seek_regulatory_review`
- H1.2 Relegar análisis financiero y capex cuando el activo sigue opaco.
- H1.3 Elevar `asset technical insufficiency` como driver de prioridad.

**Criterios de aceptación**

- TAD deja de parecer diligencia financiera prematura.

**Dependencias**

- E2, G2.

## 12. Backlog complementario de UI

## 12.1 Dashboard

**Archivos**

- `runtime-orchestrator/dashboard.py`

**Tareas**

- Mostrar `target_scope`.
- Mostrar `asset_context_readiness`.
- Mostrar `report_identity_state`.
- Mostrar `dominant_evidence_scope`.
- Mostrar `missing observable clusters`.
- Mostrar si el caso es `asset-first` o `issuer-context-only`.

**Criterios de aceptación**

- El usuario sabe antes de abrir el PDF si está viendo un caso técnico real o un caso degradado.

## 12.2 Inputs UX

**Archivos**

- `runtime-orchestrator/dashboard.py`
- `runtime-orchestrator/cli.py`

**Tareas**

- Permitir iniciar caso con dirección sola.
- Permitir declarar `target_type`.
- Permitir declarar `industry/subsector`.

**Criterios de aceptación**

- El workflow mínimo ya no requiere ticker.

## 13. Definition of Done

El programa está suficientemente corregido cuando se cumplen todos estos puntos:

- El runtime puede abrir un caso solo con dirección.
- El sistema puede decir honestamente que aún no entiende el activo.
- El prior técnico depende del tipo de activo e industria.
- SEC deja de dominar la composición del caso.
- Las fases 1–3 tienen prioridad epistemológica sobre Fase 5.
- El reporte se degrada automáticamente cuando el activo está pobremente caracterizado.
- TAD prioriza comprensión del activo antes de cualquier lectura de capital.
- El dashboard expone claramente el estado real del caso.

## 14. Riesgos que este backlog debe evitar

- Reemplazar el sesgo company-first por un benchmark-first igualmente superficial.
- Tratar geocodificación como si fuera comprensión del activo.
- Reescribir el reporte sin arreglar intake, prior y activación.
- Mantener SEC como fuente primaria “porque es más fácil”.
- Dejar que el pipeline siga llamando TDIR a un memo insuficiente.

## 15. Orden mínimo de implementación recomendado

1. Etapa A
2. Etapa B
3. Etapa C
4. Etapa D
5. Etapa E
6. Etapa F
7. Etapa G
8. Etapa H

No empezar por `motor_019` ni por el PDF. El problema nace antes.
