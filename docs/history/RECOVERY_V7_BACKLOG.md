# RECOVERY_V7_BACKLOG.md — Final Execution Hardening + Final Curation

**Doctrina V7**: el framework ya es inteligente. Ahora hay que ENDURECERLO. No más motores, no más patterns, no más combinations, no más prompts. Sólo:

> estabilizar · endurecer · desacoplar · bloquear · validar · especializar · sincronizar.

**Anchor del prompt Chief Execution Auditor + Final Curation Architect + Epistemic Governance Enforcer (2026-05-13).**

---

## 0. Audit honesto: qué del prompt YA está hecho en V6

| Sección del prompt | Estado real | Módulo donde vive |
|---|---|---|
| § 1.A Asset Family Contamination Validator | ✅ V6 P4 + P5 + P13.4 | motor_061 + `pattern_isolation.py` |
| § 1.B Hybrid Asset Justification Validator | ⚠️ Existe SJ1/SJ2/SJ3 pero **NO emite la frase "WHY_THIS_LOGIC_IS_ACTIVE"** | motor_062 |
| § 1.C Chart Validity Engine | ✅ V6 P4 (CV1/CV3 hard-block) | motor_063 |
| § 1.D Report Uniqueness Validator | ⚠️ RU1/RU2/RU3 existen; pack-level uniqueness parcial | motor_058 |
| § 1.E Claim/TAD Consistency Validator | ✅ V6 P8 (R1-R11) | motor_059 |
| § 1.F Fallback Visibility Validator | ✅ V6 P1 + P13.3 | `fallback_policy.py` + motor_024 |
| § 2 Asset Family Governance (16 families) | ✅ V6 P5 | `family_scope.ALL_KNOWN_ASSET_FAMILIES` |
| § 3 Hybrid Governance (dominance/subordination) | ⚠️ `hybrid_families.json` existe pero **no emite narrative-grade WHY** | `hybrid_families.py` + motor_062 |
| § 4 Combination Execution Hardening | ⚠️ Schema V6 strict existe pero las 4 combinaciones pre-V6 NO la cumplen | `validate_combination_v6_strict` |
| § 5 Evidence Specialization | ✅ V6 P4 (ER1-3) + per-combo packs en V6 schema | motor_056 |
| § 6 Client-Safe Mode | ⚠️ Existe (`render_gate.py`), pero el strict-default está **opt-in vía env flag** | `render_gate.py` |
| § 7 Report Composer Hardening | ✅ V6 P10 invariantes estáticos | `test_v6_dumb_render_invariants.py` |
| § 8 Governance Hardening | ⚠️ R8-R11 cubren digital_twin/roi/peer/savings; **faltan "local truth from archetypal prior" y "benchmark as truth"** | motor_059 |
| § 9 Output Quality Standard | Estilístico — vive en motor_019 prompt + forbidden phrases. Sin cambio mecánico. | motor_019 |

**Gaps verdaderos** (lo que V7 realmente entrega):

1. Flippear defaults: hard mode debe ser **ON por defecto**, no opt-in.
2. Migrar las 4 combinaciones pre-V6 al schema V6 strict.
3. Emisor narrative-grade del hybrid WHY (motor_062 extension).
4. Anti-asset-types explícitos por pattern (no sólo derivar del complemento).
5. Pack-level uniqueness (motor_058 RU4 nuevo).
6. R12 + R13 en motor_059 ("local truth from prior", "benchmark as truth").
7. Curación de docs (quitar lo que sobra, archivar `RECOVERY_*` viejos).

---

## 1. Plan V7 — 10 sub-fases secuenciales

Cada sub-fase es: cambio quirúrgico → tests → regression cross-asset → commit. Sin saltos.

### V7 P0 — Baseline freeze + audit (½ día)

- Confirmar 1650 tests + regression 7/7 en HEAD = `8ea9ea8`.
- Crear `RECOVERY_DONE_V7.md` esqueleto.
- **NO toca código.**

---

### V7 P1 — Hard mode defaults flippeados a ON (1 día) · RIESGO ALTO

**Cambio:**

```python
# validator_severity_policy.py
def hard_mode_active(...):
    # default antes: False
    # default después: True (V7 doctrine)
    ...
```

```python
# render_gate.py
def strict_mode_active(...):
    # ya es True por defecto desde V6 P9; nada que cambiar
    ...
```

**Riesgo**: el flip romperá tests que dependían del soft default.

**Mitigación**:
- Identificar los tests que rompen (estimado: ~10-20 tests de regresión que asumen severity=warning).
- Cambiar esos tests a usar `pipeline_inputs={"__validators_soft_mode__": True}` explícito (diagnostic mode).
- Mantener regression 7/7 cross-asset estable.

**Aceptación**:
- `pytest -q` ≥ 1650 passing tras ajuste de tests soft-mode.
- Regression cross-asset 7/7 PASS sin env flags exportadas.

---

### V7 P2 — Migrar 4 combinaciones pre-V6 al schema V6 strict (½ día)

Las 4 combinaciones en `zlab_skill/registry/combinations/`:

| Combinación | Family | TAD mapping needed | Evidence pack ID |
|---|---|---|---|
| `process_heat_unbounded_duty_combo` | thermal_process_facility | measure, inspect, classify | `process_heat_inventory_pack` |
| `manufacturing_support_utility_maintenance_combo` | manufacturing_facility | inspect, measure, design | `support_utility_pack` |
| `warehouse_tariff_boundary_area_combo` | warehouse_distribution | classify, measure | `tariff_boundary_pack` |
| `office_after_hours_phantom_load_combo` | commercial_building | measure, inspect | `phantom_load_pack` |

**Cambio**: backfill de los 6 campos V6:
- `required_asset_family`
- `allowed_claim_ceiling` (L2)
- `required_evidence_pack`
- `tad_mapping` (subset de las 8 canonical action families)
- `allowed_render_modes` (mínimo: `exploratory_prior`, `publish_bounded`)
- `forbidden_render_modes` (mínimo: `internal_debug_only` excluido si sale)

**Validación**: cada combo debe pasar `validate_combination_v6_strict()`.

**Aceptación**:
- `pytest tests/test_v6_combination_governance.py` verde.
- Las 4 combinaciones cargan via `propose_knowledge` en hard mode.

---

### V7 P3 — Anti-asset-types explícitos en pattern_isolation (½ día)

**Cambio**: extender `pattern_isolation_contract` para leer un campo opcional nuevo en cada pattern_spec — `anti_asset_types` — que declare ANTI explícito (no derivable por complemento).

Ejemplo en `refrigeration_duty.v1.json`:
```json
"asset_types": ["cold_chain_facility", "food_processing"],
"anti_asset_types": ["datacenter", "commercial_building", "infrastructure_node"]
```

Si `anti_asset_types` está presente, sustituye el `forbidden_families = complement` del V6 P5.

**No es destructivo**: si el pattern no declara `anti_asset_types`, sigue el cómputo V6 (forbidden = complement).

**Aceptación**:
- 30 pattern_specs revisados, ~10 con `anti_asset_types` explícitos.
- `pattern_isolation` tests + 4 tests nuevos para anti-list explícita.

---

### V7 P4 — Hybrid Justification Narrative Emitter (1 día)

**Cambio**: nuevo módulo `hybrid_justification.py` que emite la frase canónica:

```
"This facility activates {secondary_family} logic because {evidence_token_chain}
suggests {process_clue} beyond {primary_family}-only operation."
```

Wiring: motor_062 (Scenario Justification) llama al emitter cuando detecta un híbrido admisible y lo añade al output como `hybrid_justification_narrative`.

motor_019 (narrador) lo recibe via inputs y se le PROHIBE generar otra justificación libre. La frase de motor_062 es la única autorizada.

**Aceptación**:
- 6 tests para el emitter (1 por hybrid en `hybrid_families.json`).
- motor_019 prompt actualizado: si `hybrid_justification_narrative` está en inputs, usarla verbatim.

---

### V7 P5 — motor_059 R12 + R13 (½ día)

Añadir dos rules a la precedence ladder:

- **R12** `local_truth_from_archetypal_prior` — Bloquear claim si afirma local truth ("this facility consumes X kWh/sf") basándose sólo en archetypal prior, sin evidencia operacional.
- **R13** `benchmark_as_truth` — Bloquear claim que invoque benchmark como gold standard de eficiencia (e.g. "performs below industry benchmark therefore inefficient").

Ambos van al `_V6_BLOCKING_RULES` set de `validator_severity_policy.py`.

**Aceptación**:
- 4 tests nuevos en `test_v6_motor_059_precedence.py`.
- `_V6_BLOCKING_RULES` pasa de 14 a 16 reglas.

---

### V7 P6 — motor_058 RU4 evidence pack uniqueness (½ día)

**Cambio**: añadir rule RU4 a motor_058 que bloquea cuando ≥ 2 inference_cases referencian el mismo `evidence_pack.id` con > X% similitud en sus `evidence_items`.

Threshold inicial: 80% Jaccard.

**Aceptación**:
- 3 tests para RU4 (pack repetition entre 2 cases / 3 cases / no overlap).
- `_V6_BLOCKING_RULES` añade `("motor_058", "RU4_evidence_pack_repetition")`.

---

### V7 P7 — Chart Validity per asset family explicit (½ día)

**Cambio**: motor_063 ya bloquea decorative charts (CV1, CV3). V7 añade CV5: chart contamination cross-asset-family.

Si motor_063 ve un chart cuyo `chart_intelligence_binding.asset_family` ≠ `target.asset_family`:
- Bloquear (severity = "blocking" cuando hard mode).

**Aceptación**:
- 3 tests CV5 (chart from same family / cross family / no binding).

---

### V7 P8 — Final Stability Suite — CLIENT_SAFE end-to-end (1 día)

Nueva suite `test_v7_client_safe_end_to_end.py` que:
1. Ejecuta una pipeline en hard mode ON con inputs limpios → render OK.
2. Ejecuta la misma con un fallback PROHIBITED inyectado → `render_gate` refuses.
3. Ejecuta con claim_sync divergence inyectada → refuses.
4. Ejecuta con cross-family pattern activation inyectada → refuses.
5. Ejecuta con chart asset-family mismatch inyectada → refuses.
6. Ejecuta con archetypal-prior claim (R12) → refuses.
7. Ejecuta con benchmark-as-truth claim (R13) → refuses.
8. Ejecuta con pack repetition (RU4) → refuses.

8 escenarios. Cada uno DEBE fallar el render gate con un motivo específico.

**Aceptación**:
- 8 tests verde.
- Demuestra end-to-end que el cerebro V7 BLOQUEA por las 8 razones canónicas.

---

### V7 P9 — Documentation curation (½ día)

- `CLAUDE.md` — limpiar, dejar sólo lo vigente.
- Archivar `RECOVERY_V2_BACKLOG.md`, `V3_BACKLOG.md`, `V4_PHASE0/1/2_BACKLOG.md`, `RECOVERY_DONE.md`, `RECOVERY_EXECUTION_STEPS.md`, `RECOVERY_ARCHITECTURE_PLAN.md` → mover a `docs/history/`.
- Dejar en raíz sólo: `CLAUDE.md`, `AGENTS.md`, `README.md`, `RECOVERY_DONE_V5.md`, `RECOVERY_DONE_V6.md`, `RECOVERY_DONE_V7.md`, `RECOVERY_V7_BACKLOG.md` (este archivo).
- Update `AGENTS.md` a V7 cerrado.

---

### V7 P10 — Final regression + commit + push (¼ día)

- `pytest -q` ≥ 1650 + tests V7 nuevos (~30) → ~1680 passing.
- `bash scripts/regression_cross_asset_recovery.sh` → 7/7 PASS en **hard mode default ON**.
- Commit `recovery(v7p10): close V7 Final Execution Hardening`.
- `git push origin main`.

---

## 2. Reglas inviolables del trabajo V7

1. **NO añadir** motores, patterns, combinations nuevos. Sólo migrar / endurecer existentes.
2. **NO añadir** LLM en ningún lado que no sea motor_019.
3. **NO relajar** epistemología. Cualquier flip es hacia MÁS estricto, no menos.
4. **NO romper** la regression cross-asset 7/7 en ningún commit.
5. **NO push** sin autorización explícita al final.
6. **Commit por sub-fase**, mensajes con prefijo `recovery(v7pN):`.
7. **Hard mode default ON desde V7 P1**. Diagnostic mode es opt-out, no opt-in.

---

## 3. Estimación de esfuerzo

| Sub-fase | Esfuerzo | Riesgo |
|---|---|---|
| V7 P0 | ½ día | Bajo |
| V7 P1 (flip defaults) | 1 día | **Alto** — toca regression base |
| V7 P2 (migrate combos) | ½ día | Medio |
| V7 P3 (anti_asset_types) | ½ día | Bajo |
| V7 P4 (hybrid narrative) | 1 día | Medio |
| V7 P5 (R12+R13) | ½ día | Bajo |
| V7 P6 (RU4) | ½ día | Bajo |
| V7 P7 (CV5) | ½ día | Bajo |
| V7 P8 (stability suite) | 1 día | Medio |
| V7 P9 (docs) | ½ día | Bajo |
| V7 P10 (regression + push) | ¼ día | Bajo |
| **Total** | **~7 días** | — |

---

## 4. Aceptación final V7

El framework está V7-cerrado SOLO si:

- ✅ Hard mode default ON (env flags ya no son requeridas para producción).
- ✅ Las 4 combinaciones pre-V6 migradas al schema V6 strict.
- ✅ Cada uno de los 30 pattern_specs con anti-asset declaration revisada.
- ✅ motor_059 con 16 reglas en `_V6_BLOCKING_RULES` (R1-R11 + R12 + R13 + AF1/AF2 + GN1 + RU2 + RU4 + SJ1-3 + CV1 + CV3 + CV5 = >16 entries).
- ✅ motor_062 emite `hybrid_justification_narrative` cuando hay híbrido activo.
- ✅ motor_019 prompt prohíbe regenerar la justificación.
- ✅ 1680+ tests verde.
- ✅ Regression cross-asset 7/7 PASS en hard mode default.
- ✅ Docs limpios (raíz con ≤ 7 .md, history archivado).

---

## 5. Lo que V7 NO hace

(intencional, por doctrina)

- No añade más patterns. Quedan 30.
- No añade más combinations. Quedan 4 (migradas).
- No añade más motores. Quedan 64.
- No añade nueva inteligencia analítica.
- No cambia la constitución de las 8 fases.
- No regenera el AI_SCAFFOLDING_REGISTRY (eso es V8 si llega).
- No procesa los 105 PDFs restantes (V8).
- No regenera S4 patterns desde IIAR (V8).
- No expone dashboard QA (V8).

V7 = **endurecimiento del cerebro existente**. Nada más.
