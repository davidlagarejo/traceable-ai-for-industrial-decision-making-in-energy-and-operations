# CLAUDE.md — ZLab Operational Truth Framework

> **Ancla constitucional para sesiones de Claude trabajando en este repo.**
> Leer ENTERO antes de tocar código.

**Última actualización: 2026-05-13 (entrando V8 — Final Release Hardening · ajuste fino final)**

---

## 0. Doctrina actual: V8 — FINAL RELEASE HARDENING (en curso)

V7 cerrado (1721 tests, regression 7/7 hard mode default). Ver `RECOVERY_DONE_V7.md`.
V8 arranca con el prompt Chief QA Architect / Epistemic Governance Engineer / Final-Release Auditor.

**V8 lleva el framework de ~85-90% post-V7 a 98-99% client-deliverable.**
No reinventa, no añade inteligencia, no añade motores nuevos. Sólo cierra 8 gaps concretos:

1. `template_contamination_failure` flag detectado pero NO bloqueado por render_gate → conectar como hard block.
2. Chart sin `source_case_id` ⇒ no se detectan charts heredados de otro caso → CV6 nuevo.
3. Hybrid Justification narrative (V7) ⇒ falta el objeto estructurado de 10 campos del prompt → extender `hybrid_justification.py` + JSON.
4. TAD detecta digital_twin prematuro pero NO reescribe status → enforce `DO_NOT_MODEL_YET` real.
5. Evidence packs repetidos detectados (RU6) pero NO se emite per-hypothesis matrix → evidence_branching_engine nuevo.
6. Source audit 3 channels ⇒ falta authority tier (identity/permit/emissions/benchmark) → extender auditor.
7. Fallback tri-modal pero NO section-level ⇒ Executive Thesis downgrade silenciosa no bloquea client_safe → high-value sections.
8. render_gate verdict en dict pero NO YAML block visible en PDF → embed `final_delivery_gate` block.

Plan completo: `RECOVERY_V8_BACKLOG.md` (10 sub-fases · ~7 días).

**Objetivo V8**: cero gráficos contaminados, cero secciones heredadas, cero TAD incompatible con claim permissions, cero fallback en sección crítica que se publique como client-safe.

**El objetivo final NO es hacer PDFs. Es detectar cuándo una organización está comparando mal, midiendo mal, modelando mal, invirtiendo mal, o interpretando mal la economía física de su activo.**

---

## 1. Reglas inviolables V8 (NUNCA romper)

1. **El LLM aparece en EXACTAMENTE UN motor** (`motor_019` — narrador, no analista).
2. **Extracción de PDFs es DETERMINISTA** (`zlab_skill/local_pdf_autodraft.py` + V5 P9). No Anthropic/OpenAI/Ollama en el path analítico.
3. **AI NO autoría contenido.** `AI_SCAFFOLDING_REGISTRY.md` FROZEN en 9 items.
4. **AI NO aprueba combinations.** Sólo el usuario en `/combinations` o `/revisar`.
5. **NUNCA escribir JSON a `combinations/` directo.** Usar `scripts/propose_combination.py`.
6. **NUNCA meter metadata de review en el PDF.** PDF = deliverable final limpio.
7. **NUNCA `git add -A`** con WIP del usuario sin consolidar.
8. **SIEMPRE responder en español al usuario.**
9. **SIEMPRE contrastar cambios contra los Master Docs.** Phase 0 gobierna.
10. **Cada flip de defaults es hacia MÁS estricto, no menos.** Diagnostic mode es opt-out.
11. **No relajar epistemología jamás.** Cualquier validator promovido a blocking no vuelve a warning.
12. **No silent fallback.** Todo fallback registrado, clasificado, gobernado.
13. **No client-facing output con state ≠ client_safe** en hard mode.

### Reglas V8 nuevas (Chief QA Architect)

14. **template_contamination_failure ⇒ hard block.** Si detectado y strict mode → render refused, no "publish_with_degradation".
15. **Cada chart debe declarar `source_case_id`.** Chart con case_id distinto al actual sin `reusable_generic=True` ⇒ blocked.
16. **Hybrid asset logic requiere objeto estructurado completo** (10 campos: primary, secondary, trigger, why_allowed, scope_allowed, scope_prohibited, evidence_to_confirm, evidence_to_falsify, sections_allowed, sections_blocked, tad_impact). Sin él ⇒ no se activa lógica secundaria.
17. **TAD ↔ Claim Governor sync enforced.** Si dominant_variables unresolved AND action = digital_twin/sensor/retrofit → motor_033 reescribe status a `DO_NOT_MODEL_YET` / `DO_NOT_SENSOR_YET` / `DO_NOT_UNDERWRITE_*`. No "INVESTIGATE" prematuro.
18. **Source authority tier gobierna client_safe.** Identity/Permit/Emissions tier unqueried ⇒ client_safe=False. Benchmark unqueried ⇒ allowed sólo en screening.
19. **High-value section downgrades bloquean client_safe.** {Executive Thesis, TAD, Financial Exposure, Peer Comparison, Conditional Redesign, Case Adaptation Memo}. Si > 0 downgraded ⇒ refuse client_safe.
20. **PRESERVAR sin tocar** (lista del prompt): reframing estratégico, combination intelligence, peer logic, capital allocation logic, no-false-closure (no ROI/savings/bankability/peer superiority/final redesign).

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

## 4. Estado post-V7 (2026-05-13)

- **64 motores** · **30 patterns** (6 con `anti_asset_types` explícitos) · **4 combinations V6-strict-migradas** · **144 approved knowledge**
- **1721 tests passing** · regression cross-asset **7/7 PASS bajo hard mode default ON**
- **43 commits V5+V6+V7** pusheados a `origin/main`
- **Jurisdicción**: US-only para case discovery; combinations universales
- **192 fuentes industriales** en catálogo

**Módulos V6/V7 vivos en el pipeline (cableados + hard-by-default):**

| Módulo | Verdict emitido en | Default V7 |
|---|---|---|
| `validator_severity_policy.py` | motor_055..063 wired | **hard ON** (env=0 opt-out) |
| `fallback_policy.py` | motor_024 → `fallback_policy_verdict` | always |
| `source_execution_auditor.py` | motor_028 → `source_audit_verdict` | always |
| `claim_synchronization_auditor.py` | motor_016 → `claim_sync_verdict` | always |
| `pattern_isolation.py` | motor_061 → `pattern_isolation_violations` + anti-asset | always |
| `hybrid_justification.py` | motor_061 → `hybrid_justification_narrative` | always |
| `qa_score.py` | callable (qa_card) | always |
| `render_gate.py` | motor_017 → `render_gate_verdict` | **strict ON** |
| `validate_combination_v6_strict` | engine.py write-path en hard mode | hard mode gated |

**V6 blocking set V7 = 18 reglas**: R1/R2/R4 + R8-R13 (motor_059), AF1/AF2 (motor_061), GN1 (motor_057), RU2/RU6 (motor_058), SJ1/SJ2/SJ3 (motor_062), CV1/CV3/CV5 (motor_063).

---

## 5. V8 — 10 sub-fases (en curso)

Detalle completo en `RECOVERY_V8_BACKLOG.md`.

| # | Trabajo | Status | Riesgo |
|---|---|---|---|
| P0  | Baseline freeze + plan anchor                              | ⏳ | Bajo |
| P1  | `template_contamination_failure` hard block en render_gate | ⏳ | Bajo |
| P2  | CV6 chart `source_case_id` provenance                      | ⏳ | Medio |
| P3  | Hybrid Governance Object completo (10 campos)              | ⏳ | Medio |
| P4  | TAD Claim Sync rewrite (`DO_NOT_MODEL_YET`, etc.)          | ⏳ | Medio |
| P5  | Evidence Branching Engine (per-hypothesis matrix)          | ⏳ | Bajo |
| P6  | Source Authority Tier classification                       | ⏳ | Bajo |
| P7  | Section-level Fallback Governance (high-value sections)    | ⏳ | Bajo |
| P8  | Final Delivery Gate YAML block en motor_017                | ⏳ | Bajo |
| P9  | Stability suite V8 end-to-end (8 escenarios + control)     | ⏳ | Medio |
| P10 | Docs + final regression + push                             | ⏳ | Bajo |

### V7 (entregado) — referencia rápida

Detalle completo en `RECOVERY_DONE_V7.md`. 11 sub-fases (P0..P10) cerradas:
hard mode defaults ON, 4 combos migradas, 6 patterns con anti_asset_types,
hybrid narrative emitter, R12/R13 (motor_059), RU6 (motor_058), CV5
(motor_063), stability suite client_safe e2e, docs curados.

---

## 6. Cómo correr el framework

```bash
cd runtime-orchestrator
python3 cli.py run --pipeline-id <id> --inputs inputs/<case>.json --no-cache

# Dashboard:   http://localhost:7474/revisar
# Regression:  bash scripts/regression_cross_asset_recovery.sh
```

**Hard mode tras V7 P1: activo por defecto.** Soft / diagnostic mode es opt-out:
```bash
export ZLAB_VALIDATORS_HARD_BLOCK=0   # opt-out: severities vuelven a warning/critical
export ZLAB_RENDER_STRICT_DEFAULT=0   # opt-out: render permitido en cualquier state verde
```

---

## 7. Fuente de verdad (orden estricto)

1. `Phases/phase-{N}/docs/es/` — constitución (gobierna conflictos)
2. `CLAUDE.md` (este archivo) — doctrina operativa actual
3. `RECOVERY_V8_BACKLOG.md` — plan V8 (en curso)
4. `RECOVERY_DONE_V7.md` · `RECOVERY_DONE_V6.md` · `RECOVERY_DONE_V5.md` — cierres
5. `AGENTS.md` — guía operativa (subordinado a CLAUDE.md)
6. `runtime-orchestrator/` + suite de tests
7. `phase_registry.py` + `phase_units.py` (V5)
8. `AI_SCAFFOLDING_REGISTRY.md` (FROZEN en 9 items)
9. `docs/history/` — backlogs y planes antiguos archivados (V2-V7)

---

## 8. Pendiente post-V8 (V9 candidato)

V8 cierra el ajuste fino. V9 (si se requiere) puede retomar:

- **Phase 7 depth**: motor_054 belief_revision_event desde eventos reales (única fase superficial).
- **Cascade S1-S9**: regenerar AI_SCAFFOLDING_REGISTRY items desde extracción determinista (143 approved + V4 extractor).
- **Procesar 105 PDFs restantes** de la library.
- **Dashboard QA**: exponer QAScoreCard + RenderGateVerdict en `/revisar`.
- **CI smoke hard mode**: job que corra la suite con flags ON.

---

## 9. Lo que V8 NO hace (por doctrina)

- No añade motores, patterns o combinations nuevas.
- No añade LLM en ningún lado que no sea motor_019.
- No regenera el AI_SCAFFOLDING_REGISTRY.
- No procesa los 105 PDFs restantes.
- No expone dashboard QA.

**V8 = ajuste fino final para entrega cliente. Nada más.**
