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
| Active phase | **F0 → F1 unlocked** (WIP consolidated 2026-05-09) |
| Last suite run | 2026-05-09: **897 passed**, 15 warnings, 46.90s |
| Last PDF run | (pendiente baseline + post) |
| Blocking issues | none — working tree clean, all WIP consolidated into themed commits (`810844d` zlab_skill, `71c3dea` governance docs, `b58d4d3` congruence refactor, `e3a04fe` composer, `dfb6a1f` auditor, `b2206ac` phases, `c84ab1d` wiki, `22fed1e` apply scripts, `f9c66ca` gitignore PDFs). |
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
| R-00 | Crear branch `recovery/phase-0-baseline` y proteger | `done` | — | Claude | ✅ **Desbloqueada 2026-05-09**: WIP consolidado en 8 commits temáticos. Working tree limpio. Recovery puede proceder con R-W01..R-W03 (cableado composer al `congruence_claim_contract_register`) — eso destrabará el PDF visiblemente. |
| R-01 | Capturar baseline de `pytest -q` | `todo` | R-00 | — | `cd runtime-orchestrator && pytest -q \| tee ../RECOVERY_BASELINE/pytest_2026_05_08.txt` |
| R-02 | Generar 3 PDFs baseline (warehouse, manufacturing, building) | `todo` | R-01 | — | Identificar inputs canónicos en `runtime-orchestrator/inputs/`. Guardar en `RECOVERY_BASELINE/pdfs/` |
| R-03 | Crear `RECOVERY_BASELINE.md` con métricas | `todo` | R-02 | — | Para cada PDF: count "NOT OBSERVED", count evidence-pack repetido, n-gram similarity por pares (`difflib.SequenceMatcher`) |
| R-04 | Audit del god-object — listar 18+ campos | `todo` | R-00 | — | `grep -n "run\." runtime-orchestrator/src/runtime_orchestrator/pipeline_orchestrator.py` líneas 484-594. Output a `RECOVERY_BASELINE/god_object_audit.md` |

**Done Fase 0**: R-00..R-04 todos `done`, branch mergeada, baseline commiteado.

---

### FASE 1 — Layer Bundle Bus (semanas 2-3)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-10 | Crear `layer_bundle.py` con dataclass `LayerBundle` | `done` | R-04 | Claude | ✅ commit `97fa711` (2026-05-08). 97 LOC. Frozen, content-hashed, `is_readable_from` enforce. |
| R-11 | Tests de `LayerBundle` | `done` | R-10 | Claude | ✅ commit `97fa711` (2026-05-08). 9 tests, 149 LOC. |
| R-12 | Crear `layer_registry.py` con mapa motor→capa | `done` | R-10 | Claude | ✅ commit `609e838` (2026-05-08). 155 LOC. 32 motores en A-F, 22 en None (infra/ingest/support). |
| R-13 | Test: cada motor en `motor_dependencies.json` tiene capa asignada | `done` | R-12 | Claude | ✅ commit `609e838` (2026-05-08). 22 tests, 117 LOC. Coverage completo + paritioning. |
| R-14 | `pipeline_orchestrator._collect_inputs` produce `__bundles__` | `in_progress` | R-12 | Claude | **R-14a done** ✅ commit `72d6da1` (2026-05-08): bus vacío expuesto en `_collect_inputs`. **R-14b pendiente**: poblar bundles desde motores ya migrados a producir `LayerBundle`. Bloqueada por la decisión de migrar el primer producer (probablemente motor_001 → Capa A, ver R-16). |
| R-15 | Schema validator: motor solo lee bundles de capas predecesoras | `done` | R-14 | Claude | ✅ commit `3c20793` (2026-05-08). Helper `visible_bundles_for` en `layer_registry.py`. 6 tests. 778 passed. Aún no enforce-ado en pipeline_orchestrator (eso vendrá cuando los consumers empiecen a leer bundles). |
| R-16 | Orchestrator auto-build de LayerBundle para motores con capa | `done` | R-15 | Claude | ✅ commit `cc8d564` (2026-05-08). **Cambio de scope**: opción (c) de diseño — el orchestrator construye bundles **automáticamente** desde el output, sin tocar adapters. Los 32 motores con capa A-F ya producen bundle al ejecutarse. 9 tests, 787 passed. Cache estable garantizada via `_stable_inputs_for_hash` exclusión de produced_at/produced_by. |
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
| R-30 | Crear estructura `governanza/.../patterns/` | `done` | R-24 | Claude | ✅ commit `635a162` (2026-05-09). 5 asset families: warehouse, manufacturing, building, datacenter, logistics_terminal. |
| R-31 | Migrar `_CONCEPT_MARKER_MAP` a `<asset>.json` | `partial` | R-30 | Claude | ⚠️ JSON files creados; el `_CONCEPT_MARKER_MAP` legacy en `executive_thesis.py:67` sigue ahí (su eliminación es R-33, parte del composer slim que no se hizo). |
| R-32 | Crear `pattern_library.py` loader | `done` | R-31 | Claude | ✅ commit `635a162`. Loader en `runtime_orchestrator/pattern_library.py` con caché LRU. |
| R-33 | Eliminar `_CONCEPT_MARKER_MAP` de `executive_thesis.py` | `todo` | R-32 | — | Pendiente con composer slim (R-70..R-74). Hoy hay redundancia: pattern_library JSON + map legacy. |
| R-34 | Refactor motor_039 → entrega TODA la library | `todo` | R-33 | — | No hecho. motor_039 sigue como dispatcher actual. |
| R-35 | Crear motor_039a (selector) en Capa B | `cancelled` | R-34 | Claude | ❌ Cancelada — motor_060 (Diversity Engine) absorbe la responsabilidad de selector via Pattern Library loader. |
| R-36 | Update `motor_dependencies.json` con nuevos motores | `done` | R-35 | Claude | ✅ commit `d0eacab` (motor_060) y `7ddbcdf` (validators 055-058). |
| R-37 | Versionado: cada `<asset>.json` con `library_version` SemVer | `done` | R-31 | Claude | ✅ commit `635a162`. v1.0.0 en cada archivo. |

**Done Fase 2**: composer no importa nada de `governanza/.../patterns/`, library asset-agnostic.

---

### FASE 3 — Capa C: Claim Governor sin destrucción (semana 6)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-40 | Definir `EpistemicClass` Literal en `evidence_maturity/` | `todo` | R-24 | — | local_truth, structural_hypothesis, archetypal_prior, weak_signal. **Reutilizar vocabulario existente** de `congruence_intelligence/local_binding.py` (`bounded_strong_local_truth` → `local_truth`, `bounded_partial_local_truth` → `structural_hypothesis`, `weak_signal_only` → `weak_signal`). Solo `archetypal_prior` es bucket nuevo. |
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
| R-50 | motor_046 output `evidence_pack_per_hypothesis_id` | `done` | R-46 | Claude | ✅ commit `6bb4c37` (2026-05-09). Indexa cada rival_hypothesis a su evidence pack. Legacy register intacto. |
| R-51 | Composer consume pack del hypothesis_id correspondiente | `todo` | R-50 | — | Pendiente con composer slim. |
| R-52 | Crear adapter motor_060 (Diversity Engine) | `done` | R-37 | Claude | ✅ commit `d0eacab` (2026-05-09). |
| R-53 | motor_060 produce `diversity_axis_plan` | `done` | R-52 | Claude | ✅ commit `d0eacab`. Grounded en Pattern Library JSON. |
| R-54 | Update `motor_dependencies.json` con motor_060 | `done` | R-53 | Claude | ✅ commit `d0eacab`. |
| R-55 | motor_041 consume `forbidden_repetition` del plan | `done` | R-53 | Claude | ✅ commit `994bbe3` (2026-05-09). Surface diversity_axis_plan + required_themes. |
| R-56 | motor_038 consume `required_themes` | `done` | R-53 | Claude | ✅ commit `994bbe3`. |
| R-57 | motor_050 consume `prohibited_themes` | `done` | R-53 | Claude | ✅ commit `994bbe3`. Computa prohibited_themes desde axes universe minus required. |
| R-58 | motor_051 fair comparison: archetypal_peer permitido | `done` | R-42 | Claude | ✅ commit `577354d` (2026-05-09). archetypal_peer_admissibility_register con allowed_use/prohibited_use/falsification_condition. |
| R-59 | motor_043: peer comparison con allowed_verbs | `done` | R-58 | Claude | ✅ commit `577354d`. Verb mapping for 4 estados; forwards motor_051 fallback. |
| R-5A | Verificar: warehouse y manufacturing no comparten gold nuggets | `todo` | R-59 | — | Re-correr 2 reportes y diff |

**Done Fase 4**: cap. 8 (Peer Comparison) ya no muestra "What It Proves: NOT OBSERVED". Reportes diferenciados.

---

### FASE 5 — Capa F: 5 validadores nuevos (semanas 9-10)

| ID | Título | Estado | Depends on | Owner | Resume from / Notes |
|---|---|---|---|---|---|
| R-60 | Crear motor_055 Hypothesis Diversity Validator | `done` | R-5A | Claude | ✅ commit `7ddbcdf` (2026-05-08). HD1/HD2/HD3 implementados; emite warnings no bloqueantes. |
| R-61 | Crear motor_056 Evidence Repetition Validator | `done` | R-50 | Claude | ✅ commit `7ddbcdf` (2026-05-08). ER1 detecta el pack repetido del PDF Sunrise. |
| R-62 | Crear motor_057 Gold Nugget Quality Validator | `done` | R-46 | Claude | ✅ commit `7ddbcdf` (2026-05-08). GN1 archetype-replay con tokens conservadores (a reemplazar por Pattern Library R-30+). |
| R-63 | Crear motor_058 Report Uniqueness Validator | `done` | R-60 | Claude | ✅ commit `7ddbcdf` (2026-05-08). Best-effort cross-run scan en artifact-store; silente sin runs previos. |
| R-64 | Crear motor_059 Strategic Intelligence Validator | `done` | R-59 | Claude | ✅ commit `6d8f10f` (2026-05-08). 4 reglas R1-R4 incluido R3 (DO NOT MODEL + redesign concurrente). |
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

## 3.bis Hallazgo de re-auditoría 2026-05-08 — trabajo parcial ya hecho por WIP

> Esta sección documenta lo que el WIP del usuario (sin commit, working tree) **ya construyó**
> y que **acelera** o **modifica** las fases del plan original. No invalida el plan; lo afina.

### Trabajo parcial detectado (existe en working tree, sin commit)

| Componente | Ubicación | Estado | Implica para fases |
|---|---|---|---|
| 4 estados epistemológicos (`OBSERVED_FACT`, `CONDITIONAL_HYPOTHESIS`, `WEAK_SIGNAL`, `ARCHETYPAL_PRIOR`) | `congruence_intelligence/claim_governor.py:24`, motor_034:1959, motor_034:1252 | ✅ implementado parcialmente | **R-40, R-41, R-42 ya casi hechos.** Solo falta extender a TODOS los adapters que filtran por `{OBSERVED_FACT, CONDITIONAL_HYPOTHESIS}` |
| `allowed_use` / `prohibited_use` / `falsification_condition` por claim | `congruence_intelligence/claim_governor.py` (function `_contract`) | ✅ implementado | **R-42 prácticamente done** para los claims tratados por congruence_engine |
| `local_truth_confidence_register` (vocabulario `bounded_strong_local_truth`, `bounded_partial_local_truth`, `screening_only`, `weak_signal_only`, `inadmissible`) | `congruence_intelligence/local_binding.py:480-502` | ✅ implementado | Vocabulario alterno paralelo a `EpistemicClass` — decidir si converger o mantener dos |
| Pattern Library (loss_patterns, maintenance_reality, process_mapping, regulatory_physics, climate_location, finance_to_physics, culture_proxy) | `congruence_intelligence/*.py` (45 archivos / 14,225 LOC) | ✅ existe como módulo plano | **R-30..R-37 (Capa A) parcialmente hechos.** Falta **separación formal**: estos archivos no están versionados, no están en `governanza/.../patterns/`, se importan libremente entre sí |
| Hypothesis backbone (`hypothesis_backbone`, `hypothesis_ingestion`, `dynamic_case_state`) | `congruence_intelligence/` | ✅ existe | **R-50..R-57 (Capa B) parcialmente hechos.** Falta Diversity Engine (motor_060) y wiring a `evidence_pack_per_hypothesis_id` |
| Strategic TAD (`strategic_tad.py`) | `congruence_intelligence/strategic_tad.py` (385 LOC) | ✅ existe | Capa D parcialmente cubierta (paralelo a motor_033) |
| Cross-layer conflict / stop conditions / case isolation | `congruence_intelligence/{cross_layer_conflicts,stop_conditions,case_isolation}.py` | ✅ existe | **R-60..R-64 (validators) parcialmente cubiertos** — al menos V6 y V7 ya tienen base |

### Lo que NO está hecho (sigue siendo trabajo neto de la recovery)

| Componente | Estado |
|---|---|
| `LayerBundle` y bus formal entre capas | ❌ no existe — Fase 1 íntegra |
| **Cableado del nuevo `claim_governor` al composer** (motor_015/016/047 + executive_thesis.py: **0 referencias** a `ARCHETYPAL_PRIOR` y `congruence_claim_contract_register`) | ❌ no existe — **bloqueante crítico**: por eso el PDF Sunrise sigue saliendo idéntico aunque la lógica nueva esté disponible |
| Eliminación del viejo path: motor_014, motor_033, motor_038 (y otros) filtran por `{OBSERVED_FACT, CONDITIONAL_HYPOTHESIS}` ignorando `ARCHETYPAL_PRIOR` y `WEAK_SIGNAL` | ❌ — dualidad activa |
| `_refresh_run_semantics` god-object eliminado | ❌ — sigue intacto |
| `executive_thesis.py` <500 LOC | ❌ — sigue 2171 LOC |
| Diversity Engine (motor_060) | ❌ no existe |
| 5 validators nuevos (motor_055-059) | ❌ no existen como motores formales |
| Pattern Library promovida a `governanza/.../patterns/<asset>.json` | ❌ — sigue como módulo plano |

### Cronograma re-escalado

Original: 12-13 semanas. Re-escalado tras hallazgo:

| Fase | Trabajo restante | Estimación |
|---|---|---|
| F0 Baseline | igual | 1 semana |
| F1 LayerBundle | igual (no tocado) | 2 semanas |
| F2 Capa A | **mucho menor** — promover archivos que ya existen | 1 semana |
| F3 Capa C epistemic_class | **menor** — solo unificar vocabulario y extender a adapters legacy | 1 semana |
| F4 Capa B + Diversity | **menor** — hypothesis backbone existe; falta Diversity Engine | 1.5 semanas |
| F5 Validators | **menor** — V6/V7 ya tienen base; faltan V1-V5 reales | 1.5 semanas |
| **F6 Composer + cableado** | **mayor / crítico** — wire executive_thesis a `congruence_claim_contract_register` y eliminar viejo path | 2 semanas |
| F7 Verificación | igual | 1 semana |
| F8 Hardening | igual | 1 semana |
| **Total re-escalado** | | **~12 semanas → ~7-8 semanas** |

El bloqueante crítico es **F6 (cableado)**. Es lo que explica por qué el PDF Sunrise no mejora pese a que la lógica nueva ya existe.

### Wiring Map — receta atómica para destrabar F6

> Trazado punto-a-punto del flujo orphan. Estimación: 5-7 ediciones puntuales, ~80-150 LOC.

**Productor (ya existe, OK)**:
- `motor_054.py:247` llama `build_congruence_claim_contract_register(...)`
- `motor_054.py:287` lo expone en el output: `"congruence_claim_contract_register": congruence_claim_contract_register`

**Consumidor 1 — `motor_047` (Executive Synthesis)**:
- `motor_047.py:32` declara `motor_054` como input ✅
- `motor_047.py:42` extrae `m54 = inputs.get("motor_054", {})` ✅
- `motor_047.py:50-56` **solo lee** `gold_nugget_authority_state`, `authoritative_gold_nugget_register`, `strategic_gold_nugget_register`, `gold_nugget_register` ❌
- **Acción**: extender el extract a `congruence_claim_contract_register = list(m54.get("congruence_claim_contract_register", []) or [])` y pasarlo a `build_executive_thesis(...)` (líneas 57-59).

**Consumidor 2 — `executive_thesis.build_executive_thesis`**:
- Hoy **no acepta** `congruence_claim_contract_register` como parámetro.
- `executive_thesis.py:1048` ya soporta `evidence_state == "ARCHETYPAL_PRIOR"` en `_confidence_level` ✅ (solo 1 punto)
- **Acción**: agregar parámetro `congruence_claim_contract_register` y un `_render_claim_permissions_section` nuevo que reemplace el path actual basado en `{OBSERVED_FACT, CONDITIONAL_HYPOTHESIS}`.

**Consumidor 3 — `motor_016` (Report Package Assembly)**:
- `motor_016.py:6579` lee `m54` ✅
- `motor_016.py:6588, 6597, 6969` pasa `motor_054_output=m54` a 3 helpers ✅
- **Acción**: en cada helper que renderice "Claim Permissions / What Not To Do" (cap. 12 del PDF) y "Evidence & Source Traceability" (apéndice B), preferir `congruence_claim_contract_register` sobre el path legacy.

**Adapters legacy a actualizar (eliminar dualidad)**:

| Archivo | Línea | Filtro actual | Filtro correcto |
|---|---|---|---|
| `motor_014.py` | 1613 | `{"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS"}` | `{"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "WEAK_SIGNAL"}` con guards por `permission` |
| `motor_033.py` | 332, 378-379 | igual | igual |
| `motor_034.py` | 1604, 1683, 1698, 1913 | igual | igual |
| `motor_038.py` | 48 | igual | igual |

**Tareas backlog derivadas (a insertar como subtarea de F6)**:

| ID | Título | LOC estimadas |
|---|---|---|
| R-W01 | motor_047: extraer `congruence_claim_contract_register` de m54 y pasarlo a `build_executive_thesis` | ~10 | ✅ **DONE** commit `4a13590` (2026-05-09) |
| R-W02a | `executive_thesis.build_executive_thesis`: aceptar el parámetro + emitir en thesis output | ~30 | ✅ **DONE** commit `4a13590` (2026-05-09) |
| R-W02b | Cap. 12 muestra governed prohibitions del nuevo register | ~30 | ✅ **DONE** commit `ddcdb06` (2026-05-09) |
| R-W03 | motor_016 merges legacy + governed claim registers | ~70 | ✅ **DONE** commit `87c8879` (2026-05-09). Cap. 12 + apéndice B rinden governed register completo |
| R-W04 | motor_014, 033, 034, 038: extender filtros `{OBSERVED, CONDITIONAL}` a 4 estados con guards por `permission` | ~20 | ✅ **DONE** commit `1524ac0` (2026-05-08) |
| R-W05 | Tests de regresión end-to-end del flujo governed-claim | ~100 | ✅ **DONE** commit `c17c806` (2026-05-09) |

Total: **~160 LOC en 4-5 archivos**. Esto **destraba el 80% del problema visible en el PDF**.

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
| 2026-05-08 | Re-auditoría sobre working tree (no HEAD): plan central sigue válido. Hallazgo: WIP del usuario ya introdujo `local_truth_confidence_register` en motor_049 + `congruence_intelligence/local_binding.py` con valores `bounded_strong_local_truth`, `bounded_partial_local_truth`, `weak_signal_only`, `screening_only`. Fase 3 (R-40, R-41) **debe reutilizar** ese vocabulario en lugar de inventar uno nuevo — solo extender a 4 clases con `archetypal_prior` como nuevo bucket. | Recovery Architect |

---

## 6. Métricas vivas — actualizar al cierre de cada sesión

| Métrica | Baseline | Actual | Target | Última medición |
|---|---|---|---|---|
| `pytest -q` passed | 455 | 741 | ≥741 | 2026-05-08 (working tree con WIP) |
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
