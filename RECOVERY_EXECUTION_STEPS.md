# Recovery Execution Steps — paso a paso

> Plan operativo en checkboxes. Acompaña a `RECOVERY_ARCHITECTURE_PLAN.md`.
> Cada paso tiene: comando exacto, archivo afectado, criterio de done, y cómo verificar.

---

## Cómo usar este documento

- Trabaja una fase por sprint (semanas indicativas).
- No saltes a la siguiente fase sin que la suite esté verde y los done criteria pasen.
- Si algo falla a mitad, **no ocultes** el fallo modificando docs de cierre — la regla de oro de `AGENTS.md` sigue siendo: **manda la suite runtime**.
- Cualquier paso "destructivo" (eliminar función, mover módulo) se commitea aislado, en su propio commit, con mensaje `recovery(fase-N): <motivo>`.

Working dir asumido: `/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/`.

---

## FASE 0 — Congelación + baseline (semana 1)

### 0.1 Branch protection y baseline run
```bash
cd /Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework
git checkout -b recovery/phase-0-baseline
cd runtime-orchestrator
pytest -q | tee ../baseline_2026_05_08.txt
```
- [ ] Suite verde (esperado: `455 passed` o superior)
- [ ] Commit: `git commit -am "recovery(phase-0): freeze baseline test results"`

### 0.2 Generar 3 reportes de referencia (warehouse, manufacturing, building)
- [ ] Identificar los 3 inputs canónicos en `runtime-orchestrator/inputs/`
- [ ] Ejecutar el pipeline para cada uno (revisar `cli.py` o `dashboard.py` para el comando exacto)
- [ ] Guardar los PDFs en `RECOVERY_BASELINE/pdfs/`

### 0.3 Métricas baseline
Crear `RECOVERY_BASELINE.md` con:
- [ ] Para cada PDF: count de "NOT OBSERVED", count de evidence pack repetido, n-gram similarity por pares (usar `difflib.SequenceMatcher` sobre el texto extraído)
- [ ] Línea-a-línea de los 15 síntomas observados con file:line de origen (ya están en `RECOVERY_ARCHITECTURE_PLAN.md` §1.1)
- [ ] Snapshot de `wc -l runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py` y `pipeline_orchestrator.py`

### 0.4 Documentar god-object
Crear `RECOVERY_BASELINE/god_object_audit.md`:
- [ ] Listar los 18+ campos de `PipelineRun` mutados por `_refresh_run_semantics` con el motor origen y línea
- [ ] Identificar campos con múltiples fuentes (esperado: `recommended_report_type`, `prohibited_report_types`, `target_type_classification`, `allowed_report_classes`)

**Done Fase 0**: `RECOVERY_BASELINE.md` y `RECOVERY_BASELINE/` commiteados, suite verde, branch mergeada a `main` o `recovery/main`.

---

## FASE 1 — Layer Bundle Bus (semanas 2-3)

### 1.1 Crear el modelo `LayerBundle`
- [ ] Crear `runtime-orchestrator/src/runtime_orchestrator/layer_bundle.py`:
  ```python
  from __future__ import annotations
  from dataclasses import dataclass, field
  from typing import Any, Literal
  import hashlib, json

  LayerId = Literal["A", "B", "C", "D", "E", "F"]

  @dataclass(frozen=True)
  class LayerBundle:
      layer_id: LayerId
      bundle_version: str          # SemVer
      produced_by: str             # motor_id
      produced_at: str             # ISO8601
      payload: dict[str, Any]
      content_hash: str = field(default="")

      @classmethod
      def make(cls, layer_id, bundle_version, produced_by, produced_at, payload):
          serialized = json.dumps(payload, sort_keys=True, default=str)
          h = hashlib.sha256(serialized.encode()).hexdigest()[:16]
          return cls(layer_id, bundle_version, produced_by, produced_at, payload, h)
  ```
- [ ] Tests en `tests/test_layer_bundle.py`: instancia, hash determinista, frozen, json roundtrip

### 1.2 Layer assignment registry
- [ ] Crear `runtime-orchestrator/src/runtime_orchestrator/layer_registry.py` que mapea cada `motor_id` a su `LayerId`. Source of truth = §3.3 del plan
- [ ] Función `layer_of(motor_id) -> LayerId`
- [ ] Test: cada motor en `motor_dependencies.json` tiene un layer asignado

### 1.3 Bundle bus en el orchestrator
- [ ] Editar `pipeline_orchestrator.py:_collect_inputs` (línea 388):
  - Construir `__bundles__: dict[LayerId, LayerBundle]` además del `__runtime__` legacy
  - Schema validator: motor de capa X solo puede leer bundles de capas predecesoras (A < B < C < D < E < F)
- [ ] Marcar `__runtime__` con `DeprecationWarning` cuando un motor lo lea (logging only — no romper aún)

### 1.4 Migración del primer motor (motor_001 — Phase Contract)
- [ ] motor_001 produce ahora un `LayerBundle(layer_id="A", ...)` además de su output legacy
- [ ] motor_002 que lo consume puede leer ambos
- [ ] Test: el bundle se persiste en artifact-store con el `content_hash`

### 1.5 Eliminar `_refresh_run_semantics` motor por motor
Orden de eliminación (de menos a más acoplado):
1. [ ] motor_024 (línea 576-594) → mover su lógica a un `LayerBundle` de auditoría
2. [ ] motor_034 (línea 562-575) → mover a bundle de Capa C
3. [ ] motor_025 (línea 556-561) → mover a bundle de Capa C
4. [ ] motor_007 (línea 521-555) → mover a bundle de Capa F (quality eval) + Capa B (classification)
5. [ ] motor_006 (línea 512-518) → mover a bundle de ingesta
6. [ ] motor_003 (línea 519-520) → mover a bundle de Capa A
7. [ ] motor_001 (línea 485-511) → mover a bundle de Capa A

Cada paso = 1 commit. Tras cada paso: `pytest -q` verde.

### 1.6 Cierre Fase 1
- [ ] `grep -rn "_refresh_run_semantics" runtime-orchestrator/src/` = 0
- [ ] `grep -rn "__runtime__" runtime-orchestrator/src/runtime_orchestrator/adapters/` < 5 (queda solo en motores transversales)
- [ ] Suite verde

---

## FASE 2 — Capa A: Pattern Library aislada (semanas 4-5)

### 2.1 Crear estructura de patterns
```
governanza/asset-operational-logic-engine_050/patterns/
  warehouse.json
  manufacturing.json
  building.json
  datacenter.json
  port.json
  combinations/
  README.md  (cómo agregar un pattern nuevo)
```

### 2.2 Migrar `_CONCEPT_MARKER_MAP`
- [ ] Abrir `runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py:67`
- [ ] Para cada entry en `_CONCEPT_MARKER_MAP`, decidir a qué asset_type pertenece. Generar entries en cada `<asset>.json`:
  ```json
  {
    "pattern_id": "warehouse.logistics.tariff_orchestration",
    "asset_family": "warehouse_distribution",
    "axis": "tariff",
    "concept_markers": ["tariff", "demand", "peak", "charging"],
    "pattern_version": "1.0.0",
    "falsifiers": ["tariff_pack_evidence", "demand_curve_evidence"],
    "transferability": "asset_specific",
    "last_validated_at": "2026-05-08"
  }
  ```
- [ ] Crear `motor_039/pattern_loader.py` que carga y cachea por `asset_family`
- [ ] Eliminar `_CONCEPT_MARKER_MAP` de `executive_thesis.py`
- [ ] Tests: composer ahora pide patterns por `asset_family` y rechaza si la library no contiene ese family

### 2.3 Refactor motor_039
- [ ] motor_039 deja de aceptar `asset_id` como input. Entrega TODA la library con metadata
- [ ] Crear `motor_039a` (selector) en Capa B que recibe `asset_family` y devuelve el slice
- [ ] Update `motor_dependencies.json`: motor_039 ya no es dependido por motores de Capa B sino por motor_039a

### 2.4 Versionado
- [ ] Cada `<asset>.json` lleva un `library_version` SemVer
- [ ] CI: si `library_version` bumpea major, correr regresión sobre últimos 50 reportes en `run-registry/`

**Done Fase 2**: `grep -rn "_CONCEPT_MARKER_MAP" runtime-orchestrator/src/` = 0; el composer no importa nada de `governanza/.../patterns/`.

---

## FASE 3 — Capa C: Claim Governor sin destrucción (semana 6)

### 3.1 Introducir `epistemic_class`
- [ ] En `runtime-orchestrator/src/runtime_orchestrator/evidence_maturity/` añadir el campo `epistemic_class`:
  ```python
  EpistemicClass = Literal["local_truth", "structural_hypothesis", "archetypal_prior", "weak_signal"]
  ```
- [ ] Update motor_034:
  - Si hay evidencia local → `local_truth`
  - Si pattern tiene `confidence > 0.7` y no hay evidencia local → `archetypal_prior` (visible)
  - Si la hipótesis depende de inferencia transversal → `structural_hypothesis`
  - Else → `weak_signal` (puede suprimirse)
- [ ] Eliminar el bucket único `CONDITIONAL_HYPOTHESIS` (deprecate, mantener compat 1 release)

### 3.2 motor_054 emite verbos permitidos
- [ ] Por hipótesis, emitir:
  ```python
  {
    "hypothesis_id": "...",
    "epistemic_class": "archetypal_prior",
    "allowed_verbs": ["may", "structurally suggests"],
    "prohibited_claims": ["ROI", "savings"],
    "visibility_rule": "show_as_thesis"
  }
  ```
- [ ] Update tests

### 3.3 Única fuente de `recommended_report_type`
- [ ] Eliminar la decisión de `recommended_report_type` de motor_001 (target seed) y motor_007 (quality eval)
- [ ] Solo motor_025 decide
- [ ] motor_034 solo informa `report_type_eligibility` (no decide)

### 3.4 Composer consume `epistemic_class`
- [ ] En la sección "Conditional Intelligence Reason" del PDF: si `epistemic_class == archetypal_prior`, **no** imprimir "NOT OBSERVED". Imprimir el claim con allowed_verbs.

**Done Fase 3**: re-correr el reporte Sunrise warehouse. El cap. 1 ya no abre con "Conditional Intelligence Reason: NOT OBSERVED". El cap. 3 ya no muestra "What Confirms It: NOT OBSERVED / What Falsifies It: NOT OBSERVED" — debe mostrar el archetype evidence y los falsifiers explícitos.

---

## FASE 4 — Capa B: Hypothesis Engine + Diversity (semanas 7-8)

### 4.1 motor_046 → evidence per hypothesis
- [ ] Update `motor_046` (Minimum Evidence for Discrimination): output `evidence_pack_per_hypothesis_id` (dict)
- [ ] Composer consume el pack del hypothesis_id correspondiente, no un canónico global

### 4.2 motor_060_report_diversity_engine
- [ ] Crear adapter en `adapters/motor_060.py`
- [ ] Layer = B
- [ ] Inputs: asset_type, climate, jurisdiction, process_clues, tariff_clues, etc.
- [ ] Output: `diversity_axis_plan` (ver §6.2 del plan)
- [ ] Update `motor_dependencies.json` y `motor_registry.md`
- [ ] Update `motor-creator/companies_db.json` o el equivalente de cierre

### 4.3 Hypothesis engines consumen diversity_axis_plan
- [ ] motor_041 (Problem Framing): si `forbidden_repetition` está en el plan, no emite hypothesis con evidence pack idéntico
- [ ] motor_038 (Dominant Variable): consume `required_themes`
- [ ] motor_050 (Asset Operational Logic): consume `prohibited_themes`

### 4.4 Fair Comparison sin bloqueo
- [ ] motor_051: si `benchmark_availability < threshold` → emite `archetypal_peer` con `epistemic_class=archetypal_prior`
- [ ] motor_043 (Competitive Comparison): peer comparison se renderiza con allowed_verbs="structurally suggests"

**Done Fase 4**: warehouse y manufacturing reports ya **no** comparten ningún gold nugget literal. Cap. 8 (Peer Comparison) ya **no** muestra `What It Proves: NOT OBSERVED`.

---

## FASE 5 — Capa F: 5 validadores nuevos (semanas 9-10)

Cada validator: nuevo motor (055-059), capa F, no bloquea suite — emite `structured_error` que el orchestrator escala.

### 5.1 motor_055 Hypothesis Diversity Validator
- [ ] Lee últimos N reportes del `run-registry/` para el mismo `asset_family`
- [ ] Calcula Jaccard similarity de hypothesis_ids
- [ ] Si > 0.7 → fail con `repeated_hypotheses: [...]`

### 5.2 motor_056 Evidence Repetition Validator
- [ ] Cuenta ocurrencias de cada `evidence_pack` en el reporte actual
- [ ] Si un pack aparece en > 2 secciones → fail
- [ ] Output: `repetition_register: {pack_id: section_count}`

### 5.3 motor_057 Gold Nugget Quality Validator
- [ ] Lee `governanza/.../patterns/<asset>.json`
- [ ] Si un nugget literal === pattern_concept literal → fail (es archetype replay sin asset specificity)
- [ ] Excepción: si el nugget incluye al menos un asset-specific token (dock, GFA, charging window, BMS, PUE...)

### 5.4 motor_058 Report Uniqueness Validator
- [ ] N-gram diff (n=5) vs últimos 10 reportes mismo `asset_family`
- [ ] Score < 0.35 → fail

### 5.5 motor_059 Strategic Intelligence Validator
- [ ] Reglas: `DO NOT MODEL YET` y `Build digital twin` en mismo TAD plan → fail
- [ ] `denominator wrong` declarado pero `area_normalized_benchmark` también declarado → fail
- [ ] `tariff logic` claim sin tariff evidence o tariff archetype → fail

### 5.6 Wiring
- [ ] Update `motor_dependencies.json`: validators V1-V5 corren después de motor_016 (Report Package) y antes de motor_017 (LaTeX)
- [ ] motor_023 (Pipeline Orchestration): si un V falla, no compila el LaTeX. Devuelve a la capa origen marcada con `validator_failed: motor_055`

**Done Fase 5**: ejecutar los 3 reportes baseline. V2 (motor_056) bloquea el evidence pack repetido en Sunrise. V5 (motor_059) bloquea la combinación TAD inválida.

---

## FASE 6 — Capa E: Composer recortado (semana 11)

### 6.1 Recorte de `executive_thesis.py`
- [ ] Eliminar `_top_gold_nugget_rows` → mover a motor_054
- [ ] Eliminar `_is_semantically_redundant` → mover a motor_010 / motor_056
- [ ] Eliminar lógica de selección por `_TAD_STATUS_PRIORITY` (ya viene priorizado de motor_033)
- [ ] Composer queda ~400 líneas: solo template fill

### 6.2 Recorte de motor_015 (Output Block Composition)
- [ ] Eliminar cualquier rama `if evidence_state == "NOT OBSERVED" → ...`. El composer no debe ver ese estado.
- [ ] El composer recibe un `RenderBundle` con sections ya etiquetadas por su `visibility_rule`

### 6.3 Recorte de motor_018 (Chart Generation)
- [ ] Cada chart se construye desde su slice del LayerBundle (no desde state global)
- [ ] `chart_taxonomy.py` enforce: chart_id debe declarar de qué LayerBundle proviene

**Done Fase 6**: `wc -l runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py` < 500.

---

## FASE 7 — Verificación end-to-end (semana 12)

### 7.1 Re-generar 3 reportes
- [ ] Ejecutar pipeline para warehouse, manufacturing, building
- [ ] Guardar PDFs en `RECOVERY_AFTER/pdfs/`

### 7.2 Métricas vs baseline (§12 del plan)
- [ ] `executive_thesis.py` LOC: <500 ✅
- [ ] "NOT OBSERVED" count en PDF Sunrise: 0
- [ ] Reuso máximo de evidence pack: <=2 secciones
- [ ] n-gram similarity warehouse↔manufacturing: <0.35
- [ ] Reporte ya no abre con "BLOCKED UNTIL..."

### 7.3 Sniff test humano
- [ ] Lectura humana del cap. 1 de cada PDF — ¿se siente como cerebro operacional o como audit blocker?
- [ ] Diff side-by-side con baseline

**Done Fase 7**: tabla de métricas commiteada en `RECOVERY_AFTER.md`. Si alguna métrica no pasa, abrir issue con la fase responsable.

---

## FASE 8 — Hardening (semana 13)

### 8.1 Documentación nueva
- [ ] `ARCHITECTURE.md` (raíz repo): describir las 6 capas, el bus, los 5 validators, el Diversity Engine
- [ ] Update `AGENTS.md`: nueva sección "Layer Architecture" reemplazando la lectura monolítica
- [ ] Update `README.md` con la frase del §9 del plan

### 8.2 Tests
- [ ] Tests de capas: cada motor tiene un test que verifica que **no** lee bundles de capas no-predecesoras
- [ ] Tests de regresión sobre los 3 reportes baseline (snapshot test)

### 8.3 Limpieza
- [ ] Remover el field `__runtime__` legacy del input dict (final deprecation)
- [ ] Remover `derive_observable_clusters` y `missing_observable_clusters` de `asset_contracts.py` (la función vivirá en motor_007 como validador)
- [ ] Update `motor-creator/cli.py status` para reflejar 60 motores closed

### 8.4 Cierre formal
- [ ] PR final a `main` con título "recovery: layer architecture + diversity engine + 5 validators"
- [ ] Tag `v2.0.0-recovery`
- [ ] `pytest -q` final en verde

---

## Quick reference — ¿qué archivo toco para qué problema?

| Problema observado en PDF | Archivo a tocar |
|---|---|
| "NOT OBSERVED" en cap. 1 | `motor_034` (epistemic_class) + `motor_015` (composer no ve este estado) |
| Reporte abre con "BLOCKED UNTIL..." | `motor_017` (LaTeX) + `motor_016` (Report Package) — la portada debe venir de motor_054 governed thesis |
| Mismo evidence pack en 5 secciones | `motor_046` → `evidence_pack_per_hypothesis_id` + V2 (motor_056) |
| Gold nuggets genéricos | `motor_054` selección + V3 (motor_057) bloqueo |
| Peer comparison vacío | `motor_051` archetypal_peer + `motor_043` allowed_verbs |
| TAD contradictorio (DO NOT MODEL + Build twin) | V5 (motor_059) bloqueo |
| Charts decorativos | `motor_018` slice-per-bundle + `chart_taxonomy.py` enforcement |
| `_CONCEPT_MARKER_MAP` genérico | `governanza/.../patterns/<asset>.json` |
| Triple fuente de `recommended_report_type` | Solo `motor_025` decide |
| God-object `PipelineRun` | `pipeline_orchestrator.py:_refresh_run_semantics` eliminado, `LayerBundle` bus |

---

## Reglas de PR durante la recovery

1. **Un commit = un cambio**. No mezclar refactor con feature.
2. **No tocar `governanza/automation-base/*_certification*.md`** — esos son docs de cierre histórico, no se reescriben.
3. **No `--no-verify`** en commits.
4. **Si la suite rompe, no se mergea.** No "voy a arreglarlo en el próximo commit".
5. **Cada fase = una branch `recovery/phase-N-<topic>`**, mergeada solo cuando done criteria pasan.
6. **Documentar en `RECOVERY_BASELINE.md` cada decisión no-trivial** durante la recovery — sirve para el próximo arquitecto.

---

Total estimado: **12-13 semanas** con 1 ingeniero senior, ~6 semanas con 2 ingenieros (fases 2-3 y 4-5 paralelizables).
