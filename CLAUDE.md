# CLAUDE.md — ZLab Operational Truth Framework

> **Ancla constitucional para sesiones de Claude trabajando en este repo.**
> Leer ENTERO antes de tocar código.

**Última actualización: 2026-05-13 (entrando V7 — Final Execution Hardening)**

---

## 0. Doctrina actual: V7 — FINAL EXECUTION HARDENING

V6 cerrado. Ver `RECOVERY_DONE_V6.md`. El cerebro está estabilizado modularmente y los módulos están **cableados** al pipeline en caliente (P13).

**V7 no añade inteligencia. V7 endurece la EJECUCIÓN.**

V7 transforma el framework de:
> "sistema inteligente pero frágil"

a:
> "sistema operacionalmente confiable y epistemológicamente endurecido".

**El objetivo final NO es hacer PDFs. Es detectar cuándo una organización está comparando mal, midiendo mal, modelando mal, invirtiendo mal, o interpretando mal la economía física de su activo.**

Plan completo: `RECOVERY_V7_BACKLOG.md` (10 sub-fases · ~7 días).

---

## 1. Reglas inviolables V7 (NUNCA romper)

1. **El LLM aparece en EXACTAMENTE UN motor** (`motor_019` — narrador, no analista).
2. **Extracción de PDFs es DETERMINISTA** (`zlab_skill/local_pdf_autodraft.py` + V5 P9). No Anthropic/OpenAI/Ollama en el path analítico.
3. **AI NO autoría contenido.** `AI_SCAFFOLDING_REGISTRY.md` FROZEN en 9 items.
4. **AI NO aprueba combinations.** Sólo el usuario en `/combinations` o `/revisar`.
5. **NUNCA escribir JSON a `combinations/` directo.** Usar `scripts/propose_combination.py`.
6. **NUNCA meter metadata de review en el PDF.** PDF = deliverable final limpio.
7. **NUNCA `git add -A`** con WIP del usuario sin consolidar.
8. **SIEMPRE responder en español al usuario.**
9. **SIEMPRE contrastar cambios contra los Master Docs.** Phase 0 gobierna.
10. **V7 doctrine**: cada flip de defaults es hacia MÁS estricto, no menos. Diagnostic mode es opt-out.
11. **No relajar epistemología jamás.** Cualquier validator promovido a blocking no vuelve a warning.
12. **No silent fallback.** Todo fallback registrado, clasificado, gobernado.
13. **No client-facing output con state ≠ client_safe** en hard mode.

---

## 2. Ancla constitucional permanente

**8 fases canónicas** (`Phases/phase-0..8/docs/es/`):

| Fase | Unidad canónica | Motor productor | Status depth |
|---|---|---|---|
| 0 | constitutional rules + 9-state ladder | motor_001/002/024/025/026 | ✅ |
| 1 | `facility_prior` | motor_012 + motor_028 (discovery US-only) | ✅ |
| 2 | `inference_case` | motor_014 | ✅ V5 P2 |
| 3 | `output_block` + `report_package` | motor_015/016/017/019 | ✅ V5 P5/P6 |
| 4 | `claim_upgrade_candidate` | motor_034 | ✅ V5 P10 |
| 5 | `financial_exposure_case` | motor_045 | ✅ V5 P13 |
| 6 | `compliance_applicability_case` | motor_053 | ✅ V5 P12 |
| 7 | `belief_revision_event` | motor_054 | ⚠️ V5 P2 superficial (depth = V8) |
| 8 | `decision_admissibility_case` | motor_033 | ✅ V5 P11 |

Phase 0 GOBIERNA cualquier conflicto. **El LLM NO es soberano — sólo motor_019 (narrador).**

---

## 3. Doble registro: cada motor en DOS clasificaciones paralelas

| Registro | Eje | Archivo |
|---|---|---|
| `layer_registry.py` | Bus técnico A-F | A:Knowledge / B:Hypothesis / C:Claim Governor / D:TAD / E:Composer / F:Validators |
| `phase_registry.py` (V5) | Constitucional 0-8 | 0:Governance / 1:PIML / 2:Decision Core / 3:Reporting / 4:Verification / 5:Finance / 6:Regulatory / 7:Cognitive / 8:TAD |

APIs: `phase_of(motor_id)`, `motors_in_phase(n)`, `PHASE_CANONICAL_UNIT`.

---

## 4. Estado entrando V7 (2026-05-13)

- **64 motores** · **30 patterns** · **4 combinations approved** (a migrar en V7 P2) · **144 approved knowledge**
- **1650 tests passing** · regression cross-asset **7/7 PASS**
- **31 commits V5+V6+V6P13** pusheados a `origin/main`
- **Jurisdicción**: US-only para case discovery; combinations universales
- **192 fuentes industriales** en catálogo (78/87/27 tier-1/2/3)

**Módulos V6 vivos en el pipeline (P13 cableados):**

| Módulo | Verdict emitido en | Hard-block opt-in actual |
|---|---|---|
| `validator_severity_policy.py` | motor_055..063 wired | `ZLAB_VALIDATORS_HARD_BLOCK=1` |
| `fallback_policy.py` | motor_024 → `fallback_policy_verdict` | autoclasifica |
| `source_execution_auditor.py` | motor_028 → `source_audit_verdict` | autoclasifica |
| `claim_synchronization_auditor.py` | motor_016 → `claim_sync_verdict` | autoclasifica |
| `pattern_isolation.py` | motor_061 → `pattern_isolation_violations` | autoclasifica |
| `qa_score.py` | callable (qa_card) | — |
| `render_gate.py` | motor_017 → `render_gate_verdict` | `ZLAB_RENDER_STRICT_DEFAULT=1` |
| `validate_combination_v6_strict` | engine.py write-path | flag-gated |

**Gap V7 principal**: ambos env flags son **opt-in**. V7 P1 los flippea a default ON.

---

## 5. V7 — 10 sub-fases (resumen)

Detalle completo en `RECOVERY_V7_BACKLOG.md`.

| # | Trabajo | Riesgo |
|---|---|---|
| P0 | Baseline freeze + audit | Bajo |
| P1 | **Hard mode defaults flippeados a ON** | **Alto** |
| P2 | Migrar 4 combinaciones pre-V6 al schema V6 strict | Medio |
| P3 | Anti-asset-types explícitos en pattern_isolation | Bajo |
| P4 | Hybrid Justification Narrative Emitter | Medio |
| P5 | motor_059 R12 (`local_truth_from_archetypal_prior`) + R13 (`benchmark_as_truth`) | Bajo |
| P6 | motor_058 RU4 evidence pack uniqueness | Bajo |
| P7 | motor_063 CV5 chart cross-asset-family | Bajo |
| P8 | Final stability suite — CLIENT_SAFE end-to-end (8 escenarios) | Medio |
| P9 | Documentation curation (archivar histórico) | Bajo |
| P10 | Final regression + commit + push | Bajo |

**Aceptación V7**: hard mode default ON, 1680+ tests verde, regression 7/7 en hard mode default, docs limpios.

---

## 6. Cómo correr el framework

```bash
cd runtime-orchestrator
python3 cli.py run --pipeline-id <id> --inputs inputs/<case>.json --no-cache

# Dashboard:   http://localhost:7474/revisar
# Regression:  bash scripts/regression_cross_asset_recovery.sh
```

**Hard mode hoy (opt-in hasta V7 P1)**:
```bash
export ZLAB_VALIDATORS_HARD_BLOCK=1   # warn → BLOCK en 14 reglas
export ZLAB_RENDER_STRICT_DEFAULT=1   # refuse render si state ≠ client_safe
```

**Hard mode tras V7 P1**: activo por defecto. Diagnostic se opta vía:
```bash
export ZLAB_VALIDATORS_HARD_BLOCK=0
export ZLAB_RENDER_STRICT_DEFAULT=0
```

---

## 7. Fuente de verdad (orden estricto)

1. `Phases/phase-{N}/docs/es/` — constitución (gobierna conflictos)
2. `CLAUDE.md` (este archivo) — doctrina operativa actual
3. `RECOVERY_V7_BACKLOG.md` — plan de trabajo actual
4. `RECOVERY_DONE_V6.md` · `RECOVERY_DONE_V5.md` — cierres históricos
5. `AGENTS.md` — guía operativa (subordinado a CLAUDE.md)
6. `runtime-orchestrator/` + suite de tests
7. `phase_registry.py` + `phase_units.py` (V5)
8. `AI_SCAFFOLDING_REGISTRY.md` (FROZEN en 9 items)

---

## 8. Pendiente post-V7 (V8 candidato)

V7 cierra el endurecimiento. V8 (cuando llegue) puede retomar:

- **Phase 7 depth**: motor_054 belief_revision_event desde eventos reales (única fase superficial).
- **Cascade S1-S9**: regenerar AI_SCAFFOLDING_REGISTRY items desde extracción determinista (143 approved + V4 extractor).
- **Procesar 105 PDFs restantes** de la library.
- **Dashboard QA**: exponer QAScoreCard + RenderGateVerdict en `/revisar`.
- **CI smoke hard mode**: job que corra la suite con flags ON.

---

## 9. Lo que V7 NO hace (por doctrina)

- No añade más patterns, combinations, motores o prompts.
- No añade LLM en ningún lado que no sea motor_019.
- No regenera el AI_SCAFFOLDING_REGISTRY.
- No procesa los 105 PDFs restantes.
- No expone dashboard QA.

**V7 = endurecimiento del cerebro existente. Nada más.**
