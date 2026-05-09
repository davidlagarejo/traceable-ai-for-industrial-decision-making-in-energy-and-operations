# Recovery Backlog — fuente de verdad para reanudar la recovery

> **Si te perdiste, lee este archivo primero.**
>
> Este documento es la **única** fuente de estado de la recovery. Cada tarea tiene un ID estable
> (`R-XX`), un estado (`todo` / `in_progress` / `done` / `blocked`), un owner, y todo el contexto
> necesario para retomarla en frío.
>
> **Reglas de actualización**:
> - Solo se cambia un estado cuando el done criteria pasa.
> - Si una tarea queda `blocked`, escribir el motivo en `Notes`.
> - Si abandonas a media tarea, deja `in_progress` con `Resume from:` apuntando al próximo paso concreto.
> - Nunca borres una tarea — márcala `cancelled` con motivo.
> - Commitea este archivo en cada cambio de estado.
>
> **Documentos hermanos** (no duplican estado, dan contexto):
> - `RECOVERY_ARCHITECTURE_PLAN.md` — el diseño arquitectónico (qué y por qué)
> - `RECOVERY_EXECUTION_STEPS.md` — los comandos detallados (cómo)
> - **Este archivo** — el estado vivo (dónde estamos)

---

## 0. Cómo reanudar (3 pasos)

1. `cd /Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework && cat RECOVERY_BACKLOG.md | grep -E "^\| R-|^## "`
2. Buscar la primera tarea `in_progress`. Si no hay ninguna, tomar la primera `todo` cuyas dependencias estén `done`.
3. Leer el `Resume from:` de esa tarea y ejecutar.

Si la suite está roja al reanudar, congelar el backlog y arreglar runtime primero (regla de oro de `AGENTS.md`).

---

## 1. Estado global

| Campo | Valor |
|---|---|
| Recovery start | 2026-05-08 |
| Active phase | F0 — Baseline (BLOQUEADA en R-00) |
| Last suite run | (pendiente — completar al reanudar) |
| Last PDF run | (pendiente) |
| Blocking issues | **R-00 blocked**: 54 archivos modificados + 40 untracked en `main` sin commit (54 files / +20,594 / −2,146 LOC). Trabajo previo del usuario no consolidado. |
| Branch convention | `recovery/<phase>-<task-id>` |

### Cómo desbloquear R-00 (cuando vuelvas)

1. Decide qué hacer con tu trabajo previo en `main` (4 ejes detectados: `zlab_skill/`, refactor `congruence_intelligence`, cambios en `executive_thesis.py` ~947 LOC, regeneración del compliance_auditor).
2. Commitea a tu ritmo y con tus mensajes — Claude no toca tu working tree.
3. **Importante**: el plan original (`RECOVERY_ARCHITECTURE_PLAN.md`) se redactó contra `HEAD`, **no** contra el working tree. Si tus cambios pendientes ya tocan `executive_thesis.py` o `_refresh_run_semantics`, parte del diagnóstico puede estar desactualizado. Cuando termines de commitear, dile a Claude **"re-audita"** antes de empezar la recovery, para que vuelva a leer el código real y actualice el plan si hace falta.
4. Untracked que pertenecen a esta recovery (no son tuyos): `RECOVERY_ARCHITECTURE_PLAN.md`, `RECOVERY_EXECUTION_STEPS.md`, `RECOVERY_BACKLOG.md`. Esos los commiteo yo cuando arranque, en su propio commit `docs(recovery): add plan + backlog`.

Actualizar este bloque al final de cada sesión.

---

## 2. Estados posibles

| Estado | Significado |
|---|---|
| `todo` | No iniciada. Sus dependencias pueden o no estar listas (ver `Depends on`). |
| `in_progress` | Alguien la está trabajando o la dejó a medias. Mirar `Resume from:`. |
| `done` | Done criteria verificado. Commit hash registrado. |
| `blocked` | Detenida por causa externa. Motivo en `Notes`. |
| `cancelled` | Decidida no necesaria. Motivo en `Notes`. |

---

## 3. Backlog por fases

### FASE 0 — Baseline (semana 1)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-00 | Crear branch `recovery/phase-0-baseline` y proteger | `blocked` | — | — | **Bloqueada 2026-05-08**: working tree sucio (54 files modified + 40 untracked, +20,594/−2,146 LOC). Esperando que el usuario consolide su trabajo previo en `main`. Ver §1 "Cómo desbloquear R-00". |
| R-01 | Capturar baseline de `pytest -q` | `todo` | R-00 | — | `cd runtime-orchestrator && pytest -q \| tee ../RECOVERY_BASELINE/pytest_2026_05_08.txt` |
| R-02 | Generar 3 PDFs baseline (warehouse, manufacturing, building) | `todo` | R-01 | — | Identificar inputs canónicos en `runtime-orchestrator/inputs/`. Guardar en `RECOVERY_BASELINE/pdfs/` |
| R-03 | Crear `RECOVERY_BASELINE.md` con métricas | `todo` | R-02 | — | Para cada PDF: count "NOT OBSERVED", count evidence-pack repetido, n-gram similarity por pares (`difflib.SequenceMatcher`) |
| R-04 | Audit del god-object — listar 18+ campos | `todo` | R-00 | — | `grep -n "run\." runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py` líneas 484-594. Output a `RECOVERY_BASELINE/god_object_audit.md` |

**Done Fase 0**: R-00..R-04 todos `done`, branch mergeada, baseline commiteado.

---

### FASE 1 — Layer Bundle Bus (semanas 2-3)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-10 | Crear `layer_bundle.py` con dataclass `LayerBundle` | `todo` | R-04 | — | Ver §1.1 de `RECOVERY_EXECUTION_STEPS.md` |
| R-11 | Tests de `LayerBundle` | `todo` | R-10 | — | `tests/test_layer_bundle.py`: instancia, hash determinista, frozen, json roundtrip |
| R-12 | Crear `layer_registry.py` con mapa motor→capa | `todo` | R-10 | — | Source of truth: §3.3 de `RECOVERY_ARCHITECTURE_PLAN.md` |
| R-13 | Test: cada motor en `motor_dependencies.json` tiene capa asignada | `todo` | R-12 | — | Test paramétrico — falla si falta alguno |
| R-14 | `pipeline_orchestrator._collect_inputs` produce `__bundles__` | `todo` | R-12 | — | Línea 388. Mantener `__runtime__` legacy con DeprecationWarning |
| R-15 | Schema validator: motor solo lee bundles de capas predecesoras | `todo` | R-14 | — | A<B<C<D<E<F. Test que dispara violation |
| R-16 | Migrar motor_001 a producir `LayerBundle(layer_id="A")` | `todo` | R-15 | — | Adapter en `adapters/motor_001.py` |
| R-17 | Eliminar `_refresh_run_semantics` para motor_024 | `todo` | R-16 | — | `pipeline_orchestrator.py:576-594` |
| R-18 | Eliminar `_refresh_run_semantics` para motor_034 | `todo` | R-17 | — | Líneas 562-575 |
| R-19 | Eliminar `_refresh_run_semantics` para motor_025 | `todo` | R-18 | — | Líneas 556-561 |
| R-20 | Eliminar `_refresh_run_semantics` para motor_007 | `todo` | R-19 | — | Líneas 521-555. **Crítico** — motor_007 hoy decide 9 campos |
| R-21 | Eliminar `_refresh_run_semantics` para motor_006 | `todo` | R-20 | — | Líneas 512-518 |
| R-22 | Eliminar `_refresh_run_semantics` para motor_003 | `todo` | R-21 | — | Líneas 519-520 |
| R-23 | Eliminar `_refresh_run_semantics` para motor_001 | `todo` | R-22 | — | Líneas 485-511 |
| R-24 | Verificar `grep _refresh_run_semantics` = 0 hits | `todo` | R-23 | — | Si queda algo → no cerrar fase |

**Done Fase 1**: R-10..R-24 `done`, suite verde, `_refresh_run_semantics` eliminado.

---

### FASE 2 — Capa A: Pattern Library aislada (semanas 4-5)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-30 | Crear estructura `governanza/.../patterns/` | `todo` | R-24 | — | warehouse.json, manufacturing.json, building.json, datacenter.json, port.json + README |
| R-31 | Migrar `_CONCEPT_MARKER_MAP` a `<asset>.json` | `todo` | R-30 | — | `executive_thesis.py:67`. Cada entry tiene asset_family, axis, concept_markers, pattern_version, falsifiers |
| R-32 | Crear `motor_039/pattern_loader.py` | `todo` | R-31 | — | Carga + cachea por asset_family |
| R-33 | Eliminar `_CONCEPT_MARKER_MAP` de `executive_thesis.py` | `todo` | R-32 | — | `grep _CONCEPT_MARKER_MAP runtime-orchestrator/src/` debe ser 0 |
| R-34 | Refactor motor_039 → entrega TODA la library | `todo` | R-33 | — | Deja de leer asset actual |
| R-35 | Crear motor_039a (selector) en Capa B | `todo` | R-34 | — | Recibe asset_family, devuelve slice |
| R-36 | Update `motor_dependencies.json` con motor_039a | `todo` | R-35 | — | Bumpear `motor_count` a 55 |
| R-37 | Versionado: cada `<asset>.json` con `library_version` SemVer | `todo` | R-31 | — | CI: si bumpea major, regresión sobre últimos 50 reportes |

**Done Fase 2**: composer no importa nada de `governanza/.../patterns/`, library asset-agnostic.

---

### FASE 3 — Capa C: Claim Governor sin destrucción (semana 6)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-40 | Definir `EpistemicClass` Literal en `evidence_maturity/` | `todo` | R-24 | — | local_truth, structural_hypothesis, archetypal_prior, weak_signal |
| R-41 | Update motor_034: asignar `epistemic_class` por hipótesis | `todo` | R-40 | — | Ver §3.1 `RECOVERY_EXECUTION_STEPS.md` |
| R-42 | Update motor_054: emitir allowed_verbs + prohibited_claims | `todo` | R-41 | — | Por hypothesis_id |
| R-43 | Eliminar decisión de `recommended_report_type` de motor_001 | `todo` | R-23 | — | Solo motor_025 decide |
| R-44 | Eliminar decisión de `recommended_report_type` de motor_007 | `todo` | R-43 | — | Solo motor_025 decide |
| R-45 | motor_034 emite `report_type_eligibility` (no decide) | `todo` | R-44 | — | Información, no decisión |
| R-46 | Composer consume `epistemic_class` (sin reverse engineering) | `todo` | R-45 | — | Si archetypal_prior → no imprimir "NOT OBSERVED" |
| R-47 | Verificar: PDF Sunrise no tiene "NOT OBSERVED" en cap. 1, 3 | `todo` | R-46 | — | Re-correr el reporte. Si queda → reabrir R-41 |

**Done Fase 3**: 0 ocurrencias de "NOT OBSERVED" como contenido en PDF de un asset con archetype_prior.confidence > 0.7.

---

### FASE 4 — Capa B: Hypothesis Engine + Diversity (semanas 7-8)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-50 | motor_046 output `evidence_pack_per_hypothesis_id` | `todo` | R-46 | — | En lugar de pack canónico |
| R-51 | Composer consume pack del hypothesis_id correspondiente | `todo` | R-50 | — | Update motor_015/047 |
| R-52 | Crear adapter motor_060 (Diversity Engine) | `todo` | R-37 | — | Capa B. Inputs: asset_type, climate, jurisdiction, clues |
| R-53 | motor_060 produce `diversity_axis_plan` | `todo` | R-52 | — | Schema: ver §6.2 plan |
| R-54 | Update `motor_dependencies.json` con motor_060 | `todo` | R-53 | — | motor_count → 56 |
| R-55 | motor_041 consume `forbidden_repetition` del plan | `todo` | R-53 | — | Problem framing diversificado |
| R-56 | motor_038 consume `required_themes` | `todo` | R-53 | — | Dominant variable |
| R-57 | motor_050 consume `prohibited_themes` | `todo` | R-53 | — | Asset operational logic |
| R-58 | motor_051 fair comparison: archetypal_peer permitido | `todo` | R-42 | — | No bloquear si no hay benchmark |
| R-59 | motor_043: peer comparison con allowed_verbs | `todo` | R-58 | — | "structurally suggests" |
| R-5A | Verificar: warehouse y manufacturing no comparten gold nuggets | `todo` | R-59 | — | Re-correr 2 reportes y diff |

**Done Fase 4**: cap. 8 (Peer Comparison) ya no muestra "What It Proves: NOT OBSERVED". Reportes diferenciados.

---

### FASE 5 — Capa F: 5 validadores nuevos (semanas 9-10)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-60 | Crear motor_055 Hypothesis Diversity Validator | `todo` | R-5A | — | Jaccard similarity de hypothesis_ids vs últimos N |
| R-61 | Crear motor_056 Evidence Repetition Validator | `todo` | R-50 | — | Bloquea si pack en >2 secciones |
| R-62 | Crear motor_057 Gold Nugget Quality Validator | `todo` | R-46 | — | Bloquea si nugget == archetype literal |
| R-63 | Crear motor_058 Report Uniqueness Validator | `todo` | R-60 | — | N-gram diff <0.35 → fail |
| R-64 | Crear motor_059 Strategic Intelligence Validator | `todo` | R-59 | — | Anti `DO NOT MODEL YET` + `Build twin` simultáneo |
| R-65 | Update `motor_dependencies.json` con motors 055-059 | `todo` | R-64 | — | motor_count → 60 |
| R-66 | Wiring: validators corren post motor_016, pre motor_017 | `todo` | R-65 | — | Si V falla → no compila LaTeX |
| R-67 | Test: V2 bloquea evidence pack repetido en Sunrise | `todo` | R-61 | — | Reporte baseline debe disparar V2 |
| R-68 | Test: V5 bloquea TAD inválido | `todo` | R-64 | — | DO NOT MODEL + Build twin |

**Done Fase 5**: los 5 validators activos, wired, los 3 reportes baseline disparan al menos un validator (esperado).

---

### FASE 6 — Capa E: Composer recortado (semana 11)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-70 | Mover `_top_gold_nugget_rows` de executive_thesis → motor_054 | `todo` | R-42 | — | `executive_thesis.py:251` |
| R-71 | Mover `_is_semantically_redundant` → motor_010 / motor_056 | `todo` | R-61 | — | Dedup semántico es validación |
| R-72 | Eliminar lógica `_TAD_STATUS_PRIORITY` (ya viene priorizado) | `todo` | R-70 | — | motor_033 ya prioriza |
| R-73 | Verificar `wc -l executive_thesis.py` < 500 | `todo` | R-72 | — | Hoy: 2171 |
| R-74 | Eliminar ramas `if evidence_state == "NOT OBSERVED"` de motor_015 | `todo` | R-46 | — | Composer no debe ver ese estado |
| R-75 | motor_018 chart per LayerBundle slice | `todo` | R-24 | — | `chart_taxonomy.py` enforce origen |

**Done Fase 6**: composer es dumb por diseño, <500 LOC, no piensa.

---

### FASE 7 — Verificación end-to-end (semana 12)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-80 | Re-generar 3 PDFs (warehouse, manufacturing, building) | `todo` | R-75 | — | Guardar en `RECOVERY_AFTER/pdfs/` |
| R-81 | Métrica: executive_thesis.py LOC <500 | `todo` | R-80 | — | Si no pasa → reabrir Fase 6 |
| R-82 | Métrica: 0 ocurrencias "NOT OBSERVED" en PDF Sunrise | `todo` | R-80 | — | Si no pasa → reabrir Fase 3 |
| R-83 | Métrica: max reuso evidence pack ≤2 secciones | `todo` | R-80 | — | Si no pasa → reabrir Fase 4 (R-50) |
| R-84 | Métrica: n-gram similarity warehouse↔manufacturing <0.35 | `todo` | R-80 | — | Si no pasa → reabrir Fase 4 (Diversity Engine) |
| R-85 | Métrica: ningún PDF abre con "BLOCKED UNTIL..." | `todo` | R-80 | — | Si no pasa → reabrir Fase 3 |
| R-86 | Sniff test humano de cap. 1 de cada PDF | `todo` | R-85 | — | ¿Cerebro o checklist? |
| R-87 | Commit `RECOVERY_AFTER.md` con tabla métrica vs baseline | `todo` | R-86 | — | Side-by-side con baseline |

**Done Fase 7**: tabla en verde, sniff test humano OK.

---

### FASE 8 — Hardening (semana 13)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-90 | Crear `ARCHITECTURE.md` describiendo 6 capas + bus + 5 validators | `todo` | R-87 | — | En raíz repo |
| R-91 | Update `AGENTS.md` con sección "Layer Architecture" | `todo` | R-90 | — | Reemplaza lectura monolítica |
| R-92 | Update `README.md` con frase del §9 plan | `todo` | R-90 | — | "El framework existe para detectar dónde la lógica del sistema puede estar equivocada antes de que se despliegue capital" |
| R-93 | Tests de capas: cada motor verifica que no lee bundles non-pred | `todo` | R-15 | — | Test paramétrico |
| R-94 | Snapshot tests sobre los 3 reportes baseline | `todo` | R-87 | — | Regresión |
| R-95 | Remover field `__runtime__` legacy del input dict | `todo` | R-24 | — | Final deprecation |
| R-96 | Remover `derive_observable_clusters` y `missing_observable_clusters` | `todo` | R-46 | — | Mover a motor_007 como validador |
| R-97 | Update `motor-creator/cli.py status` → 60 motores closed | `todo` | R-65 | — | Sincronizar con catalog |
| R-98 | Tag `v2.0.0-recovery` y PR final a main | `todo` | R-97 | — | Cierre formal |

**Done Fase 8**: tag creado, suite verde, todos los docs alineados.

---

## 4. Tareas transversales (no fase-specific)

Ítems que pueden surgir en cualquier momento. Mantener separados para no contaminar las fases.

| ID | Título | Estado | Notes |
|---|---|---|---|
| R-T01 | Documentar cualquier regresión de suite en `RECOVERY_REGRESSIONS.md` | `todo` | Si pytest baja de 455 passed |
| R-T02 | Limpiar `run-registry/` viejo cada cierre de fase | `todo` | Para que el uniqueness validator no se confunda con runs pre-recovery |
| R-T03 | Mantener `MEMORY.md` (auto-memoria) actualizado con progreso | `todo` | Cada cierre de fase |

---

## 5. Decisiones tomadas — log irreversible

> Append-only. No se edita, no se borra. Solo se agregan filas con la decisión y la fecha.

| Fecha | Decisión | Motivo | Quien |
|---|---|---|---|
| 2026-05-08 | Adoptar arquitectura de 6 capas A-F | Ver §3 `RECOVERY_ARCHITECTURE_PLAN.md` | Recovery Architect |
| 2026-05-08 | No crear motores soberanos nuevos; solo 5 validadores + 1 Diversity Engine | Regla absoluta del prompt original | Recovery Architect |
| 2026-05-08 | `recommended_report_type` decidido solo por motor_025 | Triple fuente actual genera contradicciones | Recovery Architect |
| 2026-05-08 | `executive_thesis.py` debe quedar <500 LOC | Composer no piensa | Recovery Architect |

---

## 6. Métricas vivas — actualizar al cierre de cada sesión

| Métrica | Baseline | Actual | Target | Última medición |
|---|---|---|---|---|
| `pytest -q` passed | 455 | — | ≥455 | — |
| `executive_thesis.py` LOC | 2171 | — | <500 | — |
| `_refresh_run_semantics` referencias | 1 (la def) | — | 0 | — |
| `_CONCEPT_MARKER_MAP` referencias | 1 | — | 0 | — |
| "NOT OBSERVED" count en PDF Sunrise | 9+ | — | 0 | — |
| Max reuso evidence pack en un PDF | 5+ | — | ≤2 | — |
| n-gram sim warehouse↔manufacturing | TBD | — | <0.35 | — |
| Motores en catalog | 54 | — | 60 | — |
| Validators de diversidad | 0 | — | 5 | — |

---

## 7. Si algo se pierde — recovery del recovery

Caso: vuelves después de N semanas y no recuerdas qué hiciste.

1. Lee §1 (estado global). El campo `Active phase` te dice dónde estabas.
2. `git log --oneline --grep="recovery(" | head -30` te da los commits que pertenecen a la recovery.
3. Mira las tareas marcadas `in_progress` en §3 — esas son las que dejaste a medias.
4. Si no hay nada `in_progress`, toma la primera `todo` cuyo `Depends on` esté `done`.
5. Si la suite está roja: arregla la suite primero. **No avances la recovery con suite roja.**
6. Si encuentras código incongruente con el plan (ej: `_CONCEPT_MARKER_MAP` aún en `executive_thesis.py` pero R-33 marcado `done`): el código manda. Reabre la tarea, márcala `in_progress`, anota en `Notes` "regresión detectada en sesión <fecha>".

---

## 8. Reglas inviolables durante la recovery

1. **No tocar** `governanza/automation-base/*_certification*.md`. Esos son docs de cierre histórico.
2. **No `--no-verify`** en commits.
3. **No mergear** con suite roja.
4. **Un commit = un cambio** (refactor, test, feature separados).
5. **Cada cambio de estado de tarea = commit**, mensaje `recovery(R-XX): <transition>`.
6. Si el plan original (`RECOVERY_ARCHITECTURE_PLAN.md`) entra en conflicto con la realidad descubierta durante la implementación: **la realidad gana**, pero documenta la divergencia en §5 (Decisiones).
7. La regla de oro de `AGENTS.md` sigue vigente: si conflicto entre certificación y suite, **manda la suite**.
