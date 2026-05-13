# RECOVERY_DONE_V7.md — Final Execution Hardening (cerrado)

**Phase**: V7 Final Execution Hardening + Final Curation + Pipeline Stabilization
**Anchor**: "El cerebro ya es inteligente. Ahora hay que endurecerlo."
**Baseline**: V6 P13 (HEAD `8ea9ea8`, 1650 tests).
**Resultado**: V7 cerrado en HEAD post-`cda1edc`. **1721 tests verde, regression cross-asset 7/7 PASS bajo hard mode default ON.**

---

## Doctrina

V6 cerró la estabilidad **modular**: módulos creados, cableados al pipeline, hard mode disponible.
V7 cierra la **ejecución**: defaults flippeados, catálogo migrado, governance final.

---

## Sub-fases entregadas

| # | Sub-fase | Status | Tests | Commit |
|---|---|---|---|---|
| P0 | Baseline freeze + skeleton                      | ✅ | 1650 | `2ddc80d` |
| P1 | Hard mode defaults flippeados a ON              | ✅ | 1651 | `862d205` |
| P2 | Migrar 4 combinaciones a schema V6 strict       | ✅ | 1662 | `7e7311c` |
| P3 | `anti_asset_types` explícitos (6 patterns)      | ✅ | 1671 | `9ce7f88` |
| P4 | Hybrid Justification Narrative Emitter          | ✅ | 1681 | `dd2f9bd` |
| P5 | motor_059 R12 (archetypal-prior) + R13 (benchmark-as-truth) | ✅ | 1691 | `e6e886a` |
| P6 | motor_058 RU6 intra-run evidence pack repetition| ✅ | 1701 | `a4a3af7` |
| P7 | motor_063 CV5 chart cross-asset-family          | ✅ | 1711 | `b71b24e` |
| P8 | CLIENT_SAFE end-to-end stability suite (8)      | ✅ | 1721 | `cda1edc` |
| P9 | Docs curation (archive history)                 | ✅ | 1721 | `21267f5` |
| P10| Final regression + push                         | ✅ | 1721 | (this)    |

---

## Lo que V7 endureció (vs V6)

### 1. Defaults flippeados — ahora ON por defecto

| Flag                              | V6                  | V7                |
|-----------------------------------|---------------------|--------------------|
| `ZLAB_VALIDATORS_HARD_BLOCK`      | opt-in (default off)| **default ON**, opt-out via `=0` |
| `ZLAB_RENDER_STRICT_DEFAULT`      | default ON (since V6 P9) | mantenido |

### 2. Catálogo migrado

Las 4 combinaciones registry-level (`process_heat_unbounded_duty`, `manufacturing_support_utility_maintenance`, `warehouse_tariff_boundary_area`, `office_after_hours_phantom_load`) llevan los 6 campos governance V6:

- `required_asset_family` (1 family canonical)
- `allowed_claim_ceiling` (L2)
- `required_evidence_pack` (id único)
- `tad_mapping` (subset de 8 canonical action families)
- `allowed_render_modes` (con publish_bounded como ceiling)
- `forbidden_render_modes` (incluye `client_safe`)
- `falsification` (narrative explícita)

### 3. Nuevas reglas blocking (4 reglas nuevas en V6_BLOCKING_RULES)

| Motor | Rule | Detecta |
|---|---|---|
| motor_058 | `RU6_intra_run_evidence_pack_repetition` | 2+ cases con misma evidence pack (Jaccard > 0.80) |
| motor_059 | `R12_local_truth_from_archetypal_prior` | "this facility consumes X kWh/sf" sin evidencia local |
| motor_059 | `R13_benchmark_as_truth` | "below industry benchmark therefore inefficient" |
| motor_063 | `CV5_chart_cross_asset_family` | Chart bound a family ≠ target family |

Total V6_BLOCKING_RULES: 18 reglas canónicas (14 V6 + 4 V7).

### 4. Anti-asset-types explícitos (6 patterns)

6 patterns declaran `anti_asset_types` curado:
- `refrigeration_duty`, `defrost_profile`, `compressor_staging`, `door_cycle_losses` → anti: datacenter, commercial_building, infrastructure_node, manufacturing_facility
- `boiler_degradation_plausibility` → anti: cold_chain (2), datacenter, warehouse, fulfillment
- `hvac_schedule_drift` → anti: manufacturing, cold_chain (2), datacenter, infra, thermal_process

Cuando un pattern declara anti explícito, families neutrales (ni allowed ni anti) ya no se reportan como contamination — sólo las del anti list. Reason: `"explicit_anti_family"` en lugar de `"forbidden_family"`.

### 5. Hybrid Justification Narrative

motor_061 emite `hybrid_justification_narrative` cuando un híbrido es admitido. Forma canónica:

> "This facility activates {secondary} logic because {evidence_chain} suggests cross-system operation beyond {primary}-only deployment. {rationale}"

motor_019 (narrador) debe usar el string verbatim. **Phase 0: framework dicta la WHY, no el LLM.**

### 6. Stability suite end-to-end V7

`test_v7_client_safe_end_to_end.py` — 10 tests demuestran end-to-end que el render gate REFUSA por:
- prohibited fallback
- claim_sync divergence
- unjustified mandatory source gap
- pattern isolation violation
- CV5 (chart cross-family)
- R12 (archetypal prior)
- RU6 (pack repetition)
- state ≠ client_safe

---

## Curación documental

Movidos a `docs/history/`:
- `RECOVERY_ARCHITECTURE_PLAN.md`
- `RECOVERY_BACKLOG.md`
- `RECOVERY_DONE.md` (V1)
- `RECOVERY_EXECUTION_STEPS.md`
- `RECOVERY_V2_BACKLOG.md`
- `RECOVERY_V3_BACKLOG.md`
- `RECOVERY_V4_PHASE0/1/2_BACKLOG.md`
- `RECOVERY_V6_BACKLOG.md`
- `COMBINATION_ENGINE_AUDIT.md`
- `WIP_ANALYSIS.md`

Raíz limpia con 8 .md: `AGENTS.md`, `AI_SCAFFOLDING_REGISTRY.md`, `CLAUDE.md`, `README.md`, `RECOVERY_DONE_V5.md`, `RECOVERY_DONE_V6.md`, `RECOVERY_DONE_V7.md`, `RECOVERY_V7_BACKLOG.md`.

---

## Test count trajectory

| Phase | Tests | Delta |
|---|---|---|
| V6 P13 baseline | 1650 | — |
| V7 P1           | 1651 | +1 |
| V7 P2           | 1662 | +11 |
| V7 P3           | 1671 | +9 |
| V7 P4           | 1681 | +10 |
| V7 P5           | 1691 | +10 |
| V7 P6           | 1701 | +10 |
| V7 P7           | 1711 | +10 |
| V7 P8           | 1721 | +10 |
| V7 P9 (docs)    | 1721 | +0 |

Total V7: **+71 tests** sobre baseline V6.

Regression cross-asset 7/7 PASS en cada paso.

---

## Aceptación final V7 — cumplida

- [x] Hard mode default ON (env flags ya no requeridas en producción)
- [x] Las 4 combinaciones pre-V6 migradas al schema V6 strict
- [x] 6 patterns con `anti_asset_types` declarado
- [x] motor_059 con 18 reglas en `_V6_BLOCKING_RULES`
- [x] motor_061 emite `hybrid_justification_narrative`
- [x] 1721 tests verde
- [x] Regression cross-asset 7/7 PASS en hard mode default
- [x] Docs limpios (raíz con 8 .md, history archivado)

---

## Lo que V7 NO hizo (por doctrina, ya documentado)

- No añadió más patterns (siguen 30).
- No añadió más combinations (siguen 4 — migradas).
- No añadió más motores (siguen 64).
- No añadió LLM nuevo en ningún lado (sigue sólo motor_019).
- No regeneró el AI_SCAFFOLDING_REGISTRY.
- No procesó los 105 PDFs restantes.
- No expuso dashboard QA.

**V8 candidato** (cuando llegue):
- Phase 7 depth (motor_054 belief_revision_event)
- Cascade S1-S9 scaffolding regeneration
- Procesamiento de los 105 PDFs restantes
- Dashboard QA con QAScoreCard + RenderGateVerdict
- CI hard-mode smoke job

V7 cierra el endurecimiento. **El cerebro V7 es estable, coherente, gobernado, seguro, reproducible, client-safe y epistemológicamente consistente.**
