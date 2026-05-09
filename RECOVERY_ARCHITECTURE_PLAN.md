# ZLab Operational Truth Framework — Recovery Architecture Plan

> Documento de auditoría arquitectónica y rediseño del framework para romper el ciclo vicioso de
> "mejorar → romper → endurecer → perder inteligencia → recuperar inteligencia → volver a romper".
>
> Autor: Chief Systems Recovery Architect
> Fecha: 2026-05-08
> Caso evaluado como evidencia: `zlab-asset-warehouse-distribution-sunrise-logistics-hub-2026_exploratory_prior_brief_en.pdf`
> Estado runtime al momento del análisis: 54 motores, suite verde (`455 passed`), `motor-creator: 54 closed`.

---

## 0. TL;DR — qué está mal y qué hay que hacer

El framework **no está roto a nivel de motor**. Está roto a nivel de **arquitectura de capas**.

Hay una sola estructura mutable (`PipelineRun` + `__runtime__` context) que **mezcla** estado epistemológico, contratos de sujeto, identidad de target, readiness de evidencia, recomendación de tipo de reporte, decisión TAD y semilla de composición. Todos los motores leen y escriben esa misma estructura. Por eso:

- la gobernanza endurece un campo y mata hipótesis útiles dos motores más arriba;
- el composer hereda decisiones epistemológicas y las imprime como párrafos;
- el mismo `evidence_register` (service-level proxy, dock activity profile, charging schedule) aparece **5+ veces** en el PDF, en secciones que deberían tener evidencia diferenciada;
- "NOT OBSERVED" inunda el reporte porque `missing_observable_clusters` se calcula al arranque y propaga sin mediación;
- `CONDITIONAL_HYPOTHESIS` es la única salida posible cuando un cluster falta, así que toda hipótesis estructural colapsa al mismo nivel epistemológico.

**Solución**: separar el sistema en **6 capas estables (A-F)**, introducir **buses de datos versionados entre capas** (no un god-state mutable), y meter **5 validadores nuevos** que bloqueen contaminación, repetición y colapso de inteligencia.

No se inventan motores nuevos. Se **reasigna responsabilidad** de los 54 existentes y se **insertan 5 validadores** + 1 motor de diversidad como capa transversal.

---

## 1. Diagnóstico arquitectónico — el ciclo vigente

### 1.1 Tabla de síntomas (auditoría sobre el PDF Sunrise Logistics Hub)

| # | Síntoma observado en el PDF | Qué lo produce | Qué intenta resolver | Cómo rompe el sistema |
|---|---|---|---|---|
| 1 | "NOT OBSERVED" aparece **9+ veces** (cap. 1, 3, 6, 8) | `derive_observable_clusters` + `missing_observable_clusters` se calculan en `pipeline_orchestrator.py:33-34, 157-159` antes de cualquier motor | Marcar gaps de evidencia para el claim governor | El composer (motor_016) imprime el literal en lugar de **mediarlo** con la capa de patrones. El reporte se vuelve una lista de huecos en lugar de inteligencia. |
| 2 | Hipótesis estructurales colapsadas a `CONDITIONAL_HYPOTHESIS` | `motor_034` (Evidence Maturity) baja todo lo no-localmente-observado al mismo bucket | Distinguir local truth vs prior arquetípico | **No** distingue: archetype prior, weak signal, structural hypothesis y conditional all viven en `CONDITIONAL_HYPOTHESIS`. Una hipótesis estructural sólida (denominator wrong) se ve igual que una conjetura débil. |
| 3 | El mismo evidence pack `service-level proxy; dock activity profile; charging schedule` aparece en cap. 1, 2, 6, 7, 9, 10, 11 (5+ secciones) | `motor_046` (Minimum Evidence for Discrimination) computa **un solo** evidence pack y todos los renderers lo heredan vía `output_block_composition_engine_015` | Un único minimum-evidence canónico | El composer **reusa** ese pack en cada slot "Evidence Needed". No hay diversidad por sección, por hipótesis ni por scenario. |
| 4 | Peer Comparison (cap. 8) vacío: `What It Proves: NOT OBSERVED`, `Source: Archetypal / bounded structural pattern only` | `motor_043` (Competitive Comparison) depende de `motor_042` (Structural Benchmarking) que requiere `fair_comparison_readiness > 0`, el cual **siempre** es 0 sin local data | Bloquear comparaciones inválidas | Bloquea **toda** comparación, incluso archetypal. Mata inteligencia transferible. |
| 5 | TAD (cap. 11) tres acciones, idénticas evidence dependencies | `motor_033` (TAD) lee del mismo `evidence_register` global | Priorizar acciones | Acciones distintas terminan con la misma evidencia base → el TAD se ve como una repetición. |
| 6 | Outputs sienten genéricos ("This may not be an energy-waste problem yet") | `executive_thesis.py:67-74` mapea conceptos genéricos (`denominator_reframe`, `boundary_reframe`, `tariff_logic`...) sin distinción por asset family | Templating cross-asset | Warehouse, manufacturing y building producen el **mismo** set de gold nuggets porque los `_CONCEPT_MARKER_MAP` son universales. |
| 7 | Charts aparecen pero no cambian la decisión (cap. 3, 7, 8, 10) | `chart-generation-engine_018` recibe el `evidence_register` ya procesado por `output-block-composition-engine_015` | Ilustrar | El chart se genera del **mismo material** que el texto → es decoración, no inteligencia. |
| 8 | "Cross-Layer Congruence Map" (cap. 3) muestra una sola fila con un solo color rojo | `motor_040` (Cross-Layer Conflict) detectó 1 conflicto y el chart literalmente lo pinta sin agregación | Mostrar conflictos | Cuando hay 1 conflicto el chart es trivial; cuando hay 0 está vacío; el chart no aporta. |
| 9 | "Decision State: ASSET CONTEXT INSUFFICIENT - blocked until clusters are clarified: boundary_cluster, geometry_size_cluster, fuel_energy_cluster, systems_cluster" como **portada** | El órgano que emite ese mensaje es `derive_subject_contract_admissibility` (asset_contracts.py) y se promueve a portada por `motor_017` (LaTeX rendering) vía `motor_016` | Indicar que falta data | Es el primer mensaje que ve el lector → el reporte se siente como un **error message** en lugar de inteligencia estructural. **Esto es exactamente lo que el prompt prohíbe**. |
| 10 | "Prohibited Output: ROI; IRR; NPV; payback; bankability; savings claim" se imprime literalmente | `motor_034` registra prohibited claims y el composer las imprime | Prevenir overclaim | Funciona pero se ve como un disclaimer legal en lugar de un razonamiento. |
| 11 | "Maturity Counts: L0=79 / L1=3 / L2=1 / L3=7 / L4=0" en cap. A | `motor_034.maturity_summary` directamente impreso | Trazabilidad | Es metadata interna del motor expuesta como contenido. Capa F (Validación) leakeando a Capa E (Composer). |
| 12 | "DO NOT MODEL YET" como TAD action (cap. 11) | `motor_033` puede emitir esta acción cuando readiness < threshold | Evitar modelado prematuro | Contradice "Build detailed system model / digital twin" que aparece en la **misma página** como Immediate Action. **Auto-contradicción del TAD engine**. |
| 13 | "Industry Adaptation Table" (apéndice H) y "Case Adaptation Memo" (apéndice P) presentes pero sin diferenciar por industria | `motor_039` (Archetype Library) entrega arquetipos pero `motor_054` (Strategic Insight) los reduce al mismo claim governor genérico | Adaptación por industria | El warehouse hub queda con la misma adaptation memo que un manufacturing site. |
| 14 | "S Evidence Maturity & Claim Permission Matrix" (apéndice S) — tabla técnica al final | `motor_034` genera matriz como output → composer la mete tal cual | Trazabilidad detallada | El reporte tiene **19 capítulos + apéndices A-S** = 19 secciones. Esto es **exactamente** "template disguised as intelligence". |
| 15 | Gold nuggets (cap. 1) son: "Area may be the wrong denominator", "If charging drives peak demand, this is a tariff orchestration problem", "Before buying equipment, determine whether the building is leaking conditioned air through its logistics interface" | `executive_thesis._top_gold_nugget_rows` con `_CONCEPT_MARKER_MAP` genérico | Diferenciación | Estos 3 nuggets aparecerán **idénticos** en cualquier warehouse porque vienen del archetype prior, no del asset analizado. **Identidad arquetípica disfrazada como insight**. |

### 1.2 El ciclo vicioso, formalmente

```
        ┌────────────────────────────────────────────┐
        │  1. Cluster faltante (geometry_size, etc.) │
        │     → asset_contracts.derive_*             │
        └────────────────────┬───────────────────────┘
                             │
                             v
        ┌────────────────────────────────────────────┐
        │  2. missing_observable_clusters propagado  │
        │     en __runtime__ a TODOS los motores     │
        └────────────────────┬───────────────────────┘
                             │
                             v
        ┌────────────────────────────────────────────┐
        │  3. motor_034 (claim_governor) baja todo   │
        │     a CONDITIONAL_HYPOTHESIS               │
        └────────────────────┬───────────────────────┘
                             │
                             v
        ┌────────────────────────────────────────────┐
        │  4. motor_054 (strategic_insight) emite    │
        │     "NOT OBSERVED" en What Confirms /      │
        │     What Falsifies para preservar pureza   │
        └────────────────────┬───────────────────────┘
                             │
                             v
        ┌────────────────────────────────────────────┐
        │  5. motor_046 (minimum_evidence) entrega   │
        │     UN solo evidence pack porque no puede  │
        │     diferenciar local vs structural        │
        └────────────────────┬───────────────────────┘
                             │
                             v
        ┌────────────────────────────────────────────┐
        │  6. motor_015/016 (composer) consume el    │
        │     mismo pack en cada slot "Evidence      │
        │     Needed" — repetición estructural       │
        └────────────────────┬───────────────────────┘
                             │
                             v
        ┌────────────────────────────────────────────┐
        │  7. PDF se siente vacío + bloqueado        │
        │     → user agrega motor / regla nueva       │
        └────────────────────┬───────────────────────┘
                             │
                             └─── vuelve a 1. ────────┐
                                                       │
                                                       v
                                       (el ciclo se reproduce)
```

---

## 2. Causa raíz arquitectónica

### 2.1 El god-object `PipelineRun`

El archivo `runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py` (líneas 484-594, método `_refresh_run_semantics`) muta **18+ campos** del mismo objeto `PipelineRun` a partir de los outputs de los motores 001, 003, 006, 007, 025, 034, 024:

```
subject_definition         ← motor_001
target_definition          ← motor_003
asset_authenticity_state   ← motor_001 / motor_006
target_type_classification ← motor_001 / motor_006 / motor_007
recommended_report_type    ← motor_001 / motor_007 / motor_025   ← TRIPLE FUENTE
prohibited_report_types    ← motor_001 / motor_007 / motor_034   ← TRIPLE FUENTE
report_identity_state      ← motor_007 / motor_025
dominant_evidence_scope    ← motor_007 / motor_025
allowed_report_classes     ← motor_007 / motor_034               ← DOBLE FUENTE
asset_context_readiness    ← motor_007
subject_gate_passed        ← motor_007
evidence_maturity_summary  ← motor_034
phase_self_evaluation      ← motor_024
ingestion_learning         ← motor_024
...
```

Y luego ese `PipelineRun.to_dict()` se inyecta como `__runtime__` (línea 437-482) en **TODO** input de motor downstream.

**Esto es la antítesis de "separation of concerns".** No hay layer boundary. Una capa puede borrar lo que escribió otra capa. El último escritor gana. Por eso "do not model yet" (TAD, motor_033) coexiste con "Build detailed system model" (también TAD, mismo motor) en la misma página: `motor_033` lee dos veces el mismo run state en momentos distintos.

### 2.2 El composer piensa

`runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py` tiene **2171 líneas**. No es un composer; es un motor de razonamiento epistemológico que:

- decide qué nugget mostrar (`_top_gold_nugget_rows`),
- aplica deduplicación semántica (`_is_semantically_redundant`),
- mapea conceptos a temas (`_CONCEPT_MARKER_MAP`),
- decide qué hipótesis "supera" semánticamente a cuál.

Esto es **lógica de Hypothesis Engine + Claim Governor metida en la Capa E (Composer)**. Cuando una regla nueva se agrega para corregir un nugget repetido, se mete aquí — y rompe la composición de OTROS reportes.

### 2.3 El governor mata el archetypal prior

`motor_034` (Evidence Maturity & Claim Permission) tiene una sola dimensión epistemológica: **observado vs no-observado**. Eso colapsa cuatro cosas que el prompt central del usuario distingue explícitamente:

| Lo que el prompt pide separar | Lo que el motor 034 hace hoy |
|---|---|
| local truth | OBSERVED_FACT |
| structural hypothesis | CONDITIONAL_HYPOTHESIS |
| archetypal prior | CONDITIONAL_HYPOTHESIS |
| weak signal | CONDITIONAL_HYPOTHESIS |

Tres categorías epistemológicamente distintas viven en la misma bandera. Por eso un "archetypal prior" sólido (un warehouse de logística terminal **siempre** depende de service level → es prior fuerte) se trata igual que un "weak signal" sin evidencia. El composer no puede diferenciarlas, así que las imprime como `NOT OBSERVED` o como `CONDITIONAL_HYPOTHESIS`. **La inteligencia estructural se destruye en la Capa C**.

### 2.4 No hay un Pattern Library aislado

`motor_039` (Industrial / Building Archetype Library Resolver) **lee el asset actual y devuelve patrones dependientes del asset**. Pero un Pattern Library bien diseñado **no debe depender** del asset que se está analizando — debe ser una librería **independiente, versionada, reutilizable**. Hoy es un **dispatcher**, no una librería.

Cuando el sistema crece (warehouse, manufacturing, building, datacenter, port), `motor_039` se vuelve un switch gigante. Cada nueva industria añade ramas. El "knowledge bloat" del prompt es exactamente esto.

### 2.5 No hay diversificación per-asset

El prompt pregunta: **"Si los reportes se sienten iguales, el sistema falló."**

Hoy no hay ningún motor que **fuerce** diversidad. No hay una capa que tome el asset_type, climate, regulation, process clues, tariff clues, etc. y produzca un set diferenciado de hipótesis. Lo que hay es:

- `motor_039` que selecciona un archetype (1 de N pre-construidos)
- `motor_041` (Problem Framing) que reformula el problema
- `motor_054` (Strategic Insight) que emite el claim final

Pero **los tres convergen al mismo `_CONCEPT_MARKER_MAP`** del composer. Por eso warehouse y manufacturing producen los mismos 3 gold nuggets si los markers coinciden. **No hay un Diversity Engine.**

---

## 3. La nueva arquitectura — 6 capas estables

### 3.1 Diagrama de capas

```
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA A — GOVERNED KNOWLEDGE LAYER                                   │
│ (estática, versionada, NO sabe qué asset se está analizando)        │
│                                                                     │
│ Contiene:                                                           │
│  • Pattern Library (warehouse, manufacturing, building, datacenter) │
│  • Archetype Catalog (con falsaciones, priors, transferabilidad)    │
│  • Correlation Library (service_level ↔ throughput, etc.)           │
│  • Comparison Rules (cuándo es válido peer-compare)                 │
│  • TAD Rules (cuándo "DO NOT MODEL YET" aplica)                     │
│  • Financial Translation Rules                                      │
│                                                                     │
│ Output: KNOWLEDGE_BUNDLE (read-only, versionado por SemVer)         │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ (read-only)
                       v
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA B — HYPOTHESIS ENGINE                                          │
│ (genera hipótesis rivales, NO produce conclusiones)                 │
│                                                                     │
│ Inputs:                                                             │
│  • asset_type, climate, jurisdiction, process clues, tariff clues   │
│  • signal evidence (lo que sí observamos)                           │
│  • patterns activados desde CAPA A                                  │
│                                                                     │
│ Produce:                                                            │
│  • HYPOTHESIS_SET = [                                               │
│       {id, claim, type: structural|archetypal|local|weak,           │
│        rivals_with: [...], variables: [...],                        │
│        falsifiers: [...], fair_comparison_requirement: {...} }      │
│       , ... ]                                                       │
│                                                                     │
│ Output: HYPOTHESIS_BUNDLE (immutable for the run)                   │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA C — CLAIM GOVERNOR                                             │
│ (decide LENGUAJE permitido, NO destruye hipótesis)                  │
│                                                                     │
│ Para cada hipótesis del HYPOTHESIS_BUNDLE asigna:                   │
│  • epistemic_class: local_truth | structural_hypothesis |           │
│                     archetypal_prior | weak_signal                  │
│  • allowed_verbs: ["may", "structurally suggests", "is"]            │
│  • prohibited_claims: ["ROI", "compliance"]                         │
│  • visibility_rule: show_as_thesis | show_as_question | suppress    │
│                                                                     │
│ INVARIANTE CRÍTICO:                                                 │
│  La falta de evidencia LOCAL **no puede** colapsar una hipótesis    │
│  archetypal_prior a "NOT OBSERVED". La hipótesis sigue visible      │
│  bajo allowed_verbs="structurally suggests".                        │
│                                                                     │
│ Output: GOVERNED_HYPOTHESIS_BUNDLE                                  │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA D — TAD ENGINE                                                 │
│ (prioridades, NO depende del composer)                              │
│                                                                     │
│ Inputs: GOVERNED_HYPOTHESIS_BUNDLE + financial_exposure_register    │
│                                                                     │
│ Output: TAD_PLAN = [{action, priority, evidence_to_unblock,         │
│         kill_condition, prohibited_action}]                         │
│                                                                     │
│ Regla anti-contradicción:                                           │
│  Si TAD contiene "DO NOT MODEL YET" no puede coexistir con          │
│  "Build digital twin" en el mismo plan. Se valida en CAPA F.        │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA E — REPORT COMPOSER                                            │
│ (organiza, NUNCA inventa lógica)                                    │
│                                                                     │
│ Solo:                                                               │
│  • selecciona qué bundle render-ear según report_type               │
│  • ordena secciones según diversity_axis (CAPA A)                   │
│  • aplica plantillas LaTeX/PDF                                      │
│  • llama al chart engine con su SLICE de datos correspondiente      │
│                                                                     │
│ NO HACE:                                                            │
│  • dedup semántico (eso es Capa F)                                  │
│  • mapeo de concepts (eso vive en Capa A)                           │
│  • degradación de hipótesis (eso es Capa C)                         │
│  • merge de evidence packs (eso es Capa B)                          │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA F — VALIDATION LAYER                                           │
│ (gate de salida, bloquea o devuelve a la capa correspondiente)      │
│                                                                     │
│ Validators (5 nuevos + 4 existentes):                               │
│  • V1 Hypothesis Diversity Validator      ← NUEVO                   │
│  • V2 Evidence Repetition Validator       ← NUEVO                   │
│  • V3 Gold Nugget Quality Validator       ← NUEVO                   │
│  • V4 Report Uniqueness Validator         ← NUEVO                   │
│  • V5 Strategic Intelligence Validator    ← NUEVO                   │
│  • V6 System Consistency (motor_036)      ← existente               │
│  • V7 Cross-Layer Conflict (motor_040)    ← existente               │
│  • V8 Conformance (motor_022)             ← existente               │
│  • V9 Claim Permission (motor_034)        ← existente, RECORTADO    │
│                                                                     │
│ Si un validator falla, devuelve a la capa origen con un             │
│ structured_error. **No** intenta arreglarlo aquí.                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 El bus entre capas — fin del god-object

Cada capa entrega **un bundle inmutable**, identificado por:

```
LayerBundle:
  layer_id: "A" | "B" | "C" | "D" | "E" | "F"
  bundle_version: SemVer
  content_hash: sha256
  produced_by: motor_id
  produced_at: ISO8601
  payload: dict (read-only desde abajo)
  consumed_by: [motor_id, ...]  (logged for audit)
```

**El `__runtime__` del orchestrator desaparece como god-object**. En su lugar el orchestrator pasa solo el `LayerBundle` de la capa **inmediatamente anterior** + un `RunContext` mínimo (run_id, asset_id, jurisdiction). Un motor de Capa D **no** puede leer el bundle de Capa A; solo lee Capa B y C. Esto se enforce con un schema validator al construir el input.

Esto rompe el ciclo en el punto 2 del diagrama de §1.2: ya no hay propagación promiscua de `missing_observable_clusters`. Esa información vive **solo** en el bundle de Capa C, accesible **solo** por las capas D-F.

### 3.3 Mapeo de los 54 motores existentes a las nuevas capas

| Capa | Motor | Justificación |
|---|---|---|
| A | motor_011 Library Curation | Genera el knowledge bundle |
| A | motor_039 Industrial Archetype Library | Pattern library → DEBE refactorizarse para no leer el asset actual |
| A | motor_052 Loss Pattern & Maintenance Reality | Catálogo de loss patterns (estable) |
| A | motor_053 Regulatory & Finance Translation | Reglas de traducción regulatoria/financiera |
| A | motor_003 Taxonomy & Canonical Entity Service | Taxonomía canónica |
| **B** | motor_041 Problem Framing | Reformula problema → genera hipótesis rivales |
| **B** | motor_038 Dominant Variable Engine | Identifica variables candidatas |
| **B** | motor_037 System Abstraction | Materializa abstracción del sistema |
| **B** | motor_050 Asset Operational Logic | Lógica operativa del asset |
| **B** | motor_013 Inference Case Activation | Activa casos de inferencia |
| **B** | motor_046 Minimum Evidence for Discrimination | Define qué evidencia distingue rivales |
| **B** | motor_051 Fair Comparison & Congruence | **Mover** la decisión "fair comparison" aquí |
| **B** | motor_042 Structural Benchmarking | Genera comparaciones estructurales |
| **C** | motor_034 Evidence Maturity & Claim Permission | **Recortar**: solo asigna `epistemic_class`, NO degrada |
| **C** | motor_054 Strategic Insight & Claim Governor | Asigna allowed_verbs, prohibited_claims |
| **C** | motor_025 Epistemic Governance Layer | Reglas de claim ceiling |
| **D** | motor_033 TAD Preliminary Prioritization | Genera TAD plan |
| **D** | motor_045 Financial Exposure Under Uncertainty | Exposición financiera condicional |
| **D** | motor_044 Conditional Redesign | Pathways condicionales |
| **D** | motor_043 Competitive Comparison | Peer comparison **archetypal-allowed** |
| **E** | motor_015 Output Block Composition | **Recortar a templating puro** |
| **E** | motor_016 Report Package Assembly | Ensambla report según diversity_axis |
| **E** | motor_017 LaTeX Compilation | Render |
| **E** | motor_018 Chart Generation | **Recortar**: chart por bundle, sin lógica |
| **E** | motor_019 LLM Writing Engine | Solo redacción, no inferencia |
| **E** | motor_047 Executive Synthesis & Thesis | **Mover lógica de _CONCEPT_MARKER_MAP a Capa A** |
| **E** | motor_048 Report Compression | Comprime narrativa |
| **F** | motor_036 System Consistency Validator | V6 |
| **F** | motor_040 Cross-Layer Conflict | V7 |
| **F** | motor_022 Evaluation/Conformance | V8 |
| **F** | motor_010 Duplicate Similarity Control | Apoyo a V2 (Evidence Repetition) |
| **F** | motor_007 Quality / Fitness Evaluation | **Recortar**: NO decide report_type ni gates |
| (transversal) | motor_001 Phase Contract Registry | Infra |
| (transversal) | motor_002 Versioning & Lineage | Infra para `LayerBundle` versioning |
| (transversal) | motor_023 Pipeline Orchestration & Observability | Infra |
| (transversal) | motor_024 Governance Event Registry | Infra |
| (transversal) | motor_026 Access Control & Execution Policy | Infra |
| (transversal) | motor_027 Artifact Export & Delivery | Infra |
| (ingestion) | motor_004, 005, 006, 008, 009, 012, 028, 030, 031, 032, 035, 049 | Capa de ingesta — antes de Capa A |
| (sopporte) | motor_014, 020, 021, 029 | Soporte cross-layer |

### 3.4 Motores nuevos a introducir

**No motores soberanos. Validadores y un Diversity Engine.**

| Nuevo motor | Capa | Función |
|---|---|---|
| `motor_055_hypothesis_diversity_validator` | F (V1) | Bloquea si dos reportes consecutivos del mismo asset_type comparten >70% de hipótesis |
| `motor_056_evidence_repetition_validator` | F (V2) | Bloquea si el mismo `evidence_pack` aparece en >2 secciones del mismo reporte |
| `motor_057_gold_nugget_quality_validator` | F (V3) | Bloquea nuggets que son re-rendering del archetype prior (matching exacto contra Capa A) |
| `motor_058_report_uniqueness_validator` | F (V4) | n-gram diff vs reportes históricos del mismo asset_type. Score <0.35 = bloqueo |
| `motor_059_strategic_intelligence_validator` | F (V5) | Verifica: contradicciones (DO NOT MODEL vs Build twin), denominator wrong, control boundary, tariff logic, peer invalidity |
| `motor_060_report_diversity_engine` | B (transversal) | Toma asset_type + clues y produce `diversity_axis_plan`: qué ejes de diversidad debe forzar el composer |

Total: **54 → 60 motores**, +6 motores donde 5 son validadores y 1 es el Diversity Engine.

---

## 4. Qué lógica MOVER, qué lógica AISLAR

### 4.1 Mover

| De | A | Por qué |
|---|---|---|
| `executive_thesis._CONCEPT_MARKER_MAP` (executive_thesis.py:67) | `governanza/asset-operational-logic-engine_050/patterns/` (Capa A) | El mapping concept→theme es conocimiento, no composición |
| `_top_gold_nugget_rows` (executive_thesis.py:251) | `motor_054` (Capa C) | Selección de nugget es claim governance, no render |
| `_is_semantically_redundant` (executive_thesis.py) | `motor_010` (Capa F V2) | Dedup semántico es validación |
| Decisión `recommended_report_type` triplemente escrita | **Solo** `motor_025` (Capa C) | Una sola fuente de verdad |
| `derive_observable_clusters` + `missing_observable_clusters` (asset_contracts.py) | `motor_007` (Capa F) | Computar gaps es validación, no contexto runtime |
| `_refresh_run_semantics` (pipeline_orchestrator.py:484) | **Eliminar** | Reemplazar por dispatch a LayerBundle |

### 4.2 Aislar

| Pieza | Acción |
|---|---|
| **Pattern Library (motor_039)** | No puede consumir el asset actual. Refactor: la library devuelve **todos** los patterns; un motor de Capa B selecciona los relevantes. |
| **Report Composer (motor_015 + motor_047)** | No puede leer `evidence_state` ni decidir epistemología. Solo recibe `GOVERNED_HYPOTHESIS_BUNDLE` ya etiquetado. |
| **Claim Engine (motor_034)** | No puede borrar hipótesis. Solo asigna `epistemic_class`. La supresión visual es decisión del composer guiada por `visibility_rule`. |
| **TAD (motor_033)** | No puede leer narrativa. Solo lee `GOVERNED_HYPOTHESIS_BUNDLE` + `financial_exposure_register`. |
| **Chart Engine (motor_018)** | No puede heredar artefactos de otros casos. Cada chart se construye desde su `LayerBundle` slice + `chart_taxonomy.py` (que ya existe pero hay que enforce-arlo). |
| **Fair Comparison (motor_051)** | No puede depender de `benchmark_availability`. Si no hay benchmark, devuelve `archetypal_only` con `epistemic_class=archetypal_prior` — **no bloquea**. |

---

## 5. Qué reglas matan inteligencia útil — corrección puntual

| Regla actual | Por qué mata inteligencia | Reemplazo |
|---|---|---|
| `motor_034`: "if observation_count==0 → CONDITIONAL_HYPOTHESIS" | Colapsa archetypal_prior con weak_signal | "if archetype_prior.confidence > 0.7 AND no_local_evidence → archetypal_prior (visible, allowed_verbs=structurally suggests)" |
| `motor_046`: "Output un evidence_pack canónico" | Composer reusa en cada slot | "Output evidence_pack_per_hypothesis_id" — composer consume el específico |
| `motor_007`: decide `recommended_report_type` | Triple fuente de verdad | Solo motor_025 decide; motor_007 hace SOLO quality scoring |
| `motor_043`: bloquea si benchmark_availability < threshold | Mata peer comparison archetypal | "if benchmark_availability < threshold → emit archetypal_peer with epistemic_class=archetypal_prior" |
| `pipeline_orchestrator._refresh_run_semantics` | God-object mutation | Eliminar; reemplazar por LayerBundle dispatch |
| `executive_thesis._CONCEPT_MARKER_MAP` genérico | Mismos themes para warehouse y manufacturing | Mover a `governanza/asset-operational-logic-engine_050/patterns/{warehouse,manufacturing,building,datacenter}.json` |
| Composer imprime "NOT OBSERVED" literalmente | El composer no debería ver ese estado | Capa C nunca emite "NOT OBSERVED" como contenido; emite `visibility_rule=show_as_question` con la pregunta correspondiente |
| TAD puede emitir "DO NOT MODEL YET" + "Build twin" | No hay validador anti-contradicción | V5 (Strategic Intelligence Validator) bloquea esta combinación |

---

## 6. Diversificación — el nuevo Diversity Engine (motor_060)

### 6.1 Cómo debe sentirse cada reporte

| Asset family | Eje dominante | Variables que deben aparecer | Hipótesis típicas |
|---|---|---|---|
| **Warehouse / Distribution** | logística + throughput | dock cycles, charging windows, refrigeration duty, service-level rhythm, movement intensity | denominator wrong (area vs throughput); thermal exchange via docks; tariff orchestration via charging |
| **Manufacturing** | process heat + power quality | process heat duty, compressed air leakage, downtime patterns, throughput, power factor, harmonics | maintenance reality dominates; process heat boundary unclear; PF/reactive penalty |
| **Office / Tenant Building** | occupancy + tenant boundary | tenant control boundary, BMS schedule, after-hours load, HVAC reheat, LL97 thresholds | control boundary mismatch; after-hours phantom load; LL97 economics |
| **Datacenter** | PUE + redundancy posture | PUE, IT load, cooling redundancy, power posture | PUE composition wrong; redundancy posture vs load |
| **Port / Logistics terminal** | continuity + dispatch | continuity duty, dispatch posture, refrigeration, charging fleet | continuity dominates; dispatch logic wrong |

Si un warehouse, un manufacturing y un building producen el **mismo** set de gold nuggets, V3 (Gold Nugget Quality Validator) bloquea el reporte. **Esa es la línea roja**.

### 6.2 Diversity Axis Plan (output de motor_060)

```yaml
diversity_axis_plan:
  asset_type: warehouse_distribution
  dominant_axis: logistics_throughput
  required_hypotheses_count: 3
  required_unique_evidence_packs_count: 5
  forbidden_repetition: ["service-level proxy; dock activity profile; charging schedule"]  # si aparece > 2x → V2 falla
  required_themes:
    - thermal_exchange_via_docks
    - tariff_orchestration_via_charging
    - continuity_duty_vs_idle_conditioning
  prohibited_themes:
    - process_heat_duty   # warehouse no tiene
    - tenant_boundary     # warehouse no es building tenant
  required_chart_types:
    - cost_driver_signal_profile
    - benchmark_trust_gate
    - charging_window_overlay   # NUEVO chart específico de warehouse
```

### 6.3 Tabla de diversificación (output del Diversity Engine)

| Diversity Axis | Current State | Risk | Required Diversification |
|---|---|---|---|
| asset_type_themes | warehouse y manufacturing comparten 60% de markers | reportes intercambiables | per-asset `_CONCEPT_MARKER_MAP` (Capa A) |
| evidence_packs_per_section | 1 pack reusado en 5+ slots | repetición visible | evidence_pack_per_hypothesis_id |
| chart_taxonomy | 19 charts con la misma forma | charts decorativos | chart_per_diversity_axis con per-asset chart types |
| nugget_themes | 3 nuggets recurren entre cases | gold nuggets genéricos | V3 anti-archetype-replay |
| TAD action variety | mismo evidence-needed por acción | TAD repetitivo | TAD_action.evidence_to_unblock per_action |
| peer_comparison_basis | bloqueado por falta de bench | peer_comparison vacío | archetypal_peer permitido |

---

## 7. Sistema de inteligencia acumulativa — cómo crecer sin degradarse

| Concern | Política |
|---|---|
| **A. Agregar patrón nuevo** | PR a `governanza/.../patterns/<asset_type>.json`. CI corre V3 sobre los últimos 50 reportes históricos para detectar conflicto con patterns existentes. |
| **B. Evitar duplicados** | El pattern_id es `<asset_family>.<axis>.<concept>`. Conflicto de id = bloqueo. |
| **C. Versionar hipótesis** | Cada `Hypothesis` lleva `pattern_version` (SemVer). Si pattern bumpea major, regression test sobre últimos N reportes. |
| **D. Validar falsaciones** | Cada hipótesis tiene `falsifiers: [evidence_check_id]`. CI verifica que `evidence_check_id` exista en el catálogo de Capa A. |
| **E. Combinar patterns** | Combinaciones declarativas en `patterns/combinations/` con `precedence_rule`. No hay combinación implícita. |
| **F. Degradar patterns obsoletos** | Cada pattern tiene `last_validated_at` + `validation_count`. Si pasa >180 días sin uso → `status=deprecated`. Si está deprecated y un reporte intenta activarlo → V5 advierte. |
| **G. Evitar knowledge bloat** | Hard cap: 200 patterns activos por asset_family. Si se excede → forzar consolidación en PR. |

---

## 8. Lo que el reporte debe sonar como (criterio de éxito)

**Hoy** (PDF auditado, cap. 1):

> Declared Problem: high energy per area means warehouse inefficiency.
> Reframed Problem: Which operational intensity variable defines a fair comparison basis.
> Conditional Intelligence Reason: NOT OBSERVED.
> Dominant Misunderstanding: The visible issue may be 'high energy per area means warehouse inefficiency', but the system should first test whether which operational intensity variable defines a fair comparison basis.
> Hidden Boundary Error: The hidden system-boundary error is comparing area-normalized outcomes before the operational-intensity boundary is normalized.

→ Suena a **explicación auto-referencial**. El lector no sabe qué hacer.

**Después de la recovery**:

> This asset may currently be evaluated through the wrong denominator.
>
> If charging windows, dock cycles, refrigeration duty or continuity posture dominate
> economics, area-normalized benchmarking becomes structurally misleading.
>
> The current risk is not simply energy waste. The risk is deploying capital against
> the wrong operational variable.
>
> Before retrofit, before instrumentation, before digital twin, the framework must
> determine what actually defines the economic duty of the node.

→ Suena a **inteligencia que entiende el sujeto**. Critical: **sigue sin ROI claim**, **sigue sin savings claim**, pero ahora tiene **agencia estructural**.

La diferencia es:
- el primer texto **describe el estado del sistema** (capa F leakeando a E);
- el segundo texto **expone una hipótesis estructural sin pedir permiso** (capa B → C → E con `epistemic_class=structural_hypothesis` y `allowed_verbs="may"`).

---

## 9. El nuevo objetivo del framework — escrito en piedra

```
┌─────────────────────────────────────────────────────────────────┐
│  El framework NO existe para:                                   │
│   • pedir datos                                                 │
│   • bloquear claims                                             │
│   • generar PDFs                                                │
│                                                                 │
│  El framework existe para:                                      │
│   "detectar dónde la lógica del sistema puede estar equivocada  │
│    antes de que se despliegue capital."                         │
└─────────────────────────────────────────────────────────────────┘
```

Esta frase debe ir en `runtime-orchestrator/src/runtime_orchestrator/__init__.py` como docstring del módulo y en `README.md`. Cualquier PR que introduzca un motor cuyo propósito sea "pedir más datos" o "bloquear más claims" sin servir al objetivo arriba — se rechaza por design review.

---

## 10. Plan de implementación por fases

### Fase 0 — Congelación y baseline (1 semana)

**Objetivo**: nada se rompe; tener evidencia objetiva.

- [ ] Bloquear PRs a `runtime-orchestrator/` excepto los de este plan.
- [ ] Capturar **baseline**: ejecutar `pytest -q` y guardar como `baseline_2026_05_08.json`.
- [ ] Generar **3 reportes de referencia** (warehouse, manufacturing, building) con la versión actual y compararlos textualmente. Calcular n-gram similarity entre los 3. **Esa es la métrica de éxito a vencer**.
- [ ] Documentar en `RECOVERY_BASELINE.md` los 15 síntomas observados con line-numbers.

### Fase 1 — Layer Bundle Bus (2 semanas)

**Objetivo**: matar el god-object sin romper la suite.

- [ ] Introducir `runtime-orchestrator/src/runtime_orchestrator/layer_bundle.py` con la dataclass `LayerBundle` (campo `layer_id` A-F, `bundle_version`, `content_hash`, `payload`).
- [ ] Refactor `pipeline_orchestrator.py:_collect_inputs` para que en lugar de pasar `__runtime__` flat, pase `__bundles__: dict[layer_id, LayerBundle]`.
- [ ] Compatibilidad temporal: mantener `__runtime__` como **vista derivada** del último bundle, marcado deprecado.
- [ ] Eliminar `_refresh_run_semantics` paso a paso, motor por motor.
- [ ] Tests: la suite sigue verde (455+).

**Done criteria**: `grep -r "_refresh_run_semantics" runtime-orchestrator/src/` = 0 hits.

### Fase 2 — Capa A: Pattern Library aislada (2 semanas)

**Objetivo**: knowledge versionado, asset-agnostic.

- [ ] Crear `governanza/asset-operational-logic-engine_050/patterns/{warehouse,manufacturing,building,datacenter,port}.json`.
- [ ] Migrar `_CONCEPT_MARKER_MAP` (executive_thesis.py:67) a esos archivos. Eliminar de executive_thesis.
- [ ] Refactor `motor_039`: deja de leer asset actual, devuelve **toda** la library con metadata.
- [ ] Crear `motor_039a` (selector): lee asset_type → selecciona slice de patterns. Pertenece a Capa B.
- [ ] Versionar bundle (SemVer).

**Done criteria**: el composer (motor_015, motor_047) **no** importa nada de `governanza/.../patterns/`.

### Fase 3 — Capa C: Claim Governor sin destrucción (1 semana)

**Objetivo**: una hipótesis archetypal_prior **nunca** se vuelve `NOT OBSERVED`.

- [ ] Refactor `motor_034`: introduce el campo `epistemic_class: local_truth | structural_hypothesis | archetypal_prior | weak_signal` por hipótesis. Eliminar el bucket único `CONDITIONAL_HYPOTHESIS`.
- [ ] Update `motor_054`: emite `allowed_verbs` y `prohibited_claims` por hipótesis.
- [ ] Update `motor_025`: única fuente de verdad de `recommended_report_type`. Eliminar la decisión de motor_007 y motor_034.
- [ ] Update composer para consumir `epistemic_class` y mapear a verbo correcto (sin reverse-engineering del estado epistemológico).

**Done criteria**: 0 ocurrencias de "NOT OBSERVED" como contenido literal en el PDF generado por un asset con archetype_prior.confidence > 0.7.

### Fase 4 — Capa B: Hypothesis Engine + Diversity (2 semanas)

**Objetivo**: hipótesis específicas por asset, evidence per-hypothesis.

- [ ] Update `motor_046`: output `evidence_pack_per_hypothesis_id` en lugar de un pack canónico.
- [ ] Crear `motor_060_report_diversity_engine`: produce `diversity_axis_plan`.
- [ ] Update `motor_041`, `motor_038`, `motor_050`: consumen `diversity_axis_plan` como restricción.
- [ ] Update `motor_051` Fair Comparison: si `benchmark_availability < threshold`, emite archetypal_peer en lugar de bloquear.

**Done criteria**: warehouse y manufacturing ya **no** comparten ningún gold nugget literal en runs separados.

### Fase 5 — Capa F: 5 Validadores nuevos (2 semanas)

**Objetivo**: gates anti-degradación.

- [ ] `motor_055_hypothesis_diversity_validator`
- [ ] `motor_056_evidence_repetition_validator`
- [ ] `motor_057_gold_nugget_quality_validator`
- [ ] `motor_058_report_uniqueness_validator`
- [ ] `motor_059_strategic_intelligence_validator` (especialmente la regla anti `DO NOT MODEL YET` + `Build twin`)

Cada validator: si falla, emite `structured_error` y devuelve a la capa origen. **No** intenta corregir.

**Done criteria**: corre los 3 reportes baseline. V2 reporta el evidence pack repetido en 5+ secciones (debe ser detectado y bloqueado).

### Fase 6 — Capa E: Composer recortado (1 semana)

**Objetivo**: el composer no piensa.

- [ ] Eliminar `_top_gold_nugget_rows`, `_is_semantically_redundant`, `_CONCEPT_MARKER_MAP` de `executive_thesis.py`. Reducir el archivo de 2171 líneas a <500.
- [ ] El composer solo recibe `GOVERNED_HYPOTHESIS_BUNDLE` y aplica template.
- [ ] Move dedup semántico a V2 (Capa F).
- [ ] Move gold nugget selection a `motor_054` (Capa C).

**Done criteria**: `wc -l runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py` < 500.

### Fase 7 — Verificación end-to-end (1 semana)

**Objetivo**: comparar output vs baseline.

- [ ] Re-generar los 3 reportes de referencia (warehouse, manufacturing, building).
- [ ] Calcular n-gram similarity. Debe bajar **en al menos 50%**.
- [ ] Pasar checklist del prompt original (cap. 8 del prompt: cómo debería sentirse Warehouse, Manufacturing, Building).
- [ ] Validar con un humano que el reporte **suena como un cerebro operacional-financiero**, no como un audit checklist.

**Done criteria**: los 3 reportes son **sustantivamente diferentes** entre sí; ningún reporte abre con "BLOCKED UNTIL clusters are clarified".

### Fase 8 — Hardening (1 semana)

- [ ] Documentar la arquitectura nueva en `ARCHITECTURE.md`.
- [ ] Update `AGENTS.md` para reflejar el nuevo modelo de capas.
- [ ] Migrar tests legacy que dependen del `__runtime__` flat.
- [ ] Cerrar.

**Total**: 12 semanas.

---

## 11. Reglas absolutas (cumplidas en este plan)

- ✅ No se propone "más IA"; se propone **separación arquitectónica**.
- ✅ No se propone "más scraping"; el problema no es ingesta.
- ✅ No se destruye gobernanza; se le **devuelve su scope correcto** (Capa C, no toda la pipeline).
- ✅ No se relajan claim permissions; se **diferencian** epistemológicamente.
- ✅ No se permite ROI/savings sin evidencia: las prohibiciones siguen vigentes y se hacen más finas (per-hypothesis).
- ✅ No se permite template contamination: el composer es restringido a templating puro.
- ✅ No se usan benchmarks como verdad local: peer comparison archetypal queda explícitamente etiquetada.
- ✅ El Report Composer **no** piensa: se mueve toda la lógica fuera.
- ✅ La epistemología **no** destruye inteligencia estructural: archetypal_prior queda visible bajo allowed_verbs.

---

## 12. Anexo — Métricas de éxito (objetivas)

| Métrica | Baseline (hoy) | Target post-recovery |
|---|---|---|
| Líneas de `executive_thesis.py` | 2171 | <500 |
| Ocurrencias de "NOT OBSERVED" en PDF Sunrise | 9+ | 0 |
| Reuso de mismo evidence pack en un reporte | 5+ veces | <=2 veces |
| n-gram similarity entre warehouse y manufacturing report | TBD (medir baseline) | <0.35 |
| Fuentes que escriben `recommended_report_type` | 3 motores | 1 motor |
| Capas en `_refresh_run_semantics` mutadas | 18+ campos | 0 (función eliminada) |
| Validators de diversidad activos | 0 | 5 |
| Patterns asset-specific catalogados | ~0 (todo genérico) | 100+ por asset_family |
| Reporte abre con "BLOCKED" | sí | no |

Si una de estas métricas no se alcanza, la Fase 7 falla y la fase responsable se reabre.

---

## 13. Cierre

El framework está cerca. Tiene 54 motores, runtime verde, gobernanza certificada. Lo que le falta no es **más** sino **fronteras**.

Las fronteras correctas son:

1. Knowledge ≠ Hypothesis ≠ Claim ≠ TAD ≠ Composition ≠ Validation.
2. Cada capa entrega un bundle inmutable; ninguna capa muta lo de otra.
3. El claim governor distingue 4 clases epistemológicas, no 2.
4. La pattern library no conoce el asset que se analiza.
5. El composer es **dumb** por diseño.
6. La diversidad es **forzada** por un motor dedicado, no esperada del azar.

Si esas 6 fronteras se respetan, el ciclo vicioso descrito en §1.2 no puede reproducirse: la información sensible (`missing_observable_clusters`) no fluye fuera de su capa, así que no contamina al composer, así que no aparece como párrafo, así que el usuario no responde con "agreguemos otra regla".

El sistema deja de auto-saborearse y empieza a juzgar al asset.
