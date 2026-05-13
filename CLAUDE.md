# CLAUDE.md — ZLab Operational Truth Framework

> **Ancla constitucional para sesiones de Claude trabajando en este repo.**
> Leer ENTERO antes de tocar código.

**Última actualización: 2026-05-13 (V6 CERRADO — 1650 tests, regression 7/7)**

---

## 0. Doctrina actual: V6 STABILITY HARDENING (cerrado)

V6 está **cerrado**. Ver `RECOVERY_DONE_V6.md` para el cierre completo.

Resumen:
- **1650 tests passing** (+167 desde el baseline V5 de 1483).
- **Regression 7/7** verde en cada subfase.
- 14 commits V6 en `main` local (P0..P12).
- Reglas inviolables ahora **enforced en código**, no sólo en docs.

**V6 NO añadió inteligencia. V6 estabilizó el cerebro.**

El problema actual NO es:
- falta de hipótesis
- falta de patterns
- falta de combinations
- falta de arquitectura conceptual

El problema actual ES:
- validators detectan PERO NO bloquean
- contamination cross-asset-family aún posible
- fallbacks silenciosos degradan outputs
- rendering todavía acoplado a lógica analítica
- claim counts inconsistentes entre motores
- reportes generan aún cuando hay contamination

**Doctrina V6:**
> "Estabilizar antes de añadir. Las mismas reglas, los mismos validators, los mismos patterns, las mismas combinations deben producir outputs CONSISTENTES, LIMPIOS, GOBERNADOS y libres de CONTAMINATION."

**Reglas absolutas V6** (NUNCA romper):
1. No agregar más inteligencia hasta cerrar V6.
2. No relajar epistemología.
3. No permitir rendering thinking (motor_017/019 no introducen lógica analítica).
4. No permitir chart reuse cross-asset-family.
5. No permitir unsupported hybrid activation.
6. No permitir report generation después de validator failure.
7. No permitir fallback silencioso.

---

## 1. Ancla constitucional permanente (heredada V5)

**8 fases canónicas** (`Phases/phase-0..8/docs/es/`):

| Fase | Unidad canónica | Motor productor | Status depth |
|---|---|---|---|
| 0 | constitutional rules + 9-state ladder | motor_001/002/024/025/026 | ✅ |
| 1 | `facility_prior` | motor_012 + motor_028 (discovery US-only) | ✅ |
| 2 | `inference_case` | motor_014 (6 atributos canónicos) | ✅ V5 P2 |
| 3 | `output_block` + `report_package` | motor_015/016/017/019 | ✅ V5 P5/P6 (con maturity) |
| 4 | `claim_upgrade_candidate` | motor_034 | ✅ V5 P10 depth |
| 5 | `financial_exposure_case` | motor_045 | ✅ V5 P13 depth |
| 6 | `compliance_applicability_case` | motor_053 | ✅ V5 P12 depth |
| 7 | `belief_revision_event` | motor_054 | ⚠️ V5 P2 superficial (depth pendiente) |
| 8 | `decision_admissibility_case` | motor_033 | ✅ V5 P11 depth |

Phase 0 GOBIERNA cualquier conflicto. **El LLM NO es soberano — sólo motor_019 (narrador).**

---

## 2. Reglas inviolables enforced en código

1. **El LLM aparece en EXACTAMENTE UN motor** (`motor_019` — narrador, no analista). Con `narrator_validator.check_orphan_claims` desde V5 P7.
2. **Extracción de PDFs es DETERMINISTA.** `zlab_skill/local_pdf_autodraft.py` + keyword rules + V5 P9 derivador automático. NO Anthropic/OpenAI/Ollama en el path analítico.
3. **AI NO autoría contenido.** `AI_SCAFFOLDING_REGISTRY.md` FROZEN en 9 items.
4. **AI NO aprueba combinations.** Sólo el usuario en `/combinations` o `/revisar`.
5. **NUNCA escribir JSON a `combinations/` directo.** Usar `scripts/propose_combination.py`.
6. **NUNCA meter metadata de review en el PDF.** PDF = deliverable final limpio.
7. **NUNCA `git add -A`** con WIP del usuario sin consolidar.
8. **SIEMPRE responder en español al usuario.**
9. **SIEMPRE contrastar cambios contra los Master Docs.** Phase 0 gobierna.

---

## 3. Doble registro: cada motor está en DOS clasificaciones paralelas

| Registro | Eje | Archivo |
|---|---|---|
| **`layer_registry.py`** | Bus técnico A-F | A:Knowledge / B:Hypothesis / C:Claim Governor / D:TAD / E:Composer / F:Validators |
| **`phase_registry.py`** (V5) | Constitucional 0-8 | 0:Governance / 1:PIML / 2:Decision Core / 3:Reporting / 4:Verification / 5:Finance / 6:Regulatory / 7:Cognitive / 8:TAD |

APIs: `phase_of(motor_id)`, `motors_in_phase(n)`, `PHASE_CANONICAL_UNIT`.

---

## 4. Estado post-V6 (2026-05-13)

- **64 motores** en `governanza/automation-base/motor_dependencies.json`
- **1650 tests passing** (`pytest tests/`)
- **Regression cross-asset 7/7** (6 representative + hybrid)
- **192 fuentes industriales** en catálogo (78/87/27 tier-1/2/3)
- **30 patterns** + **4 combinations approved** + **144 approved knowledge** (143 batch + 1 manual)
- **16 commits V5 + 14 commits V6** en `main` local (no pushed)
- **Jurisdicción**: US-only para case discovery; combinations universales
- **V6 modules nuevos**: `fallback_policy`, `source_execution_auditor`, `qa_score`,
  `validator_severity_policy`, `pattern_isolation`, `claim_synchronization_auditor`,
  `render_gate`, `validate_combination_v6_strict`, R8-R11 en motor_059.

---

## 5. V6 STABILITY HARDENING — los 18 items y su estado

Auditado 2026-05-13. La mayoría ya existe estructuralmente. **El trabajo V6 es PROMOTION de warn→BLOCK + 3 piezas nuevas pequeñas.**

| # | Item | Status V6 | Módulo / commit |
|---|---|---|---|
| 1 | System State Machine | ✅ V6 P9 strict default | `render_gate.py` |
| 2 | Hard Block Validation Layer | ✅ V6 P4 + P4.1-4.8 | `validator_severity_policy.py` + 7 motores cableados |
| 3 | Asset Family Isolation Engine | ✅ V6 P5 | `pattern_isolation.py` |
| 4 | Hybrid Justification Engine | ✅ V6 P4 (SJ1/SJ2/SJ3 promovidas) | `validator_severity_policy.py` |
| 5 | DUMB_RENDER (composer) | ✅ V6 P10 | `test_v6_dumb_render_invariants.py` |
| 6 | Chart Validity Engine | ✅ V6 P4 (CV1/CV3 promovidas) | motor_063 wired |
| 7 | Combination Governance | ✅ V6 P6 | `validate_combination_v6_strict()` |
| 8 | Evidence Specialization | ✅ V6 P4 (ER1-ER3 promovidas) | motor_056 wired |
| 9 | Report Uniqueness Engine | ✅ V6 P4 (RU2 promovida) | motor_058 wired |
| 10 | Fallback Governance | ✅ V6 P1 | `fallback_policy.py` |
| 11 | Claim Synchronization | ✅ V6 P7 | `claim_synchronization_auditor.py` |
| 12 | TAD Consistency Engine | ✅ V6 P8 | motor_059 R8-R11 |
| 13 | Source Execution Auditor | ✅ V6 P2 | `source_execution_auditor.py` |
| 14 | CLIENT_SAFE_MODE | ✅ V6 P9 | `render_gate.py` strict default |
| 15 | QA Score Engine | ✅ V6 P3 | `qa_score.py` |
| 16 | Stability Test Suite | ✅ V6 P11 | `test_v6_stability_suite.py` (9 escenarios) |
| 17 | Resultado final | ✅ | 1650 tests, regression 7/7 |
| 18 | Entregable | ✅ | `RECOVERY_DONE_V6.md` |

**Resultado**: los 18 items cerrados. V6 totalmente entregado.

---

## 6. Cómo correr el framework

```bash
cd runtime-orchestrator
python3 cli.py run --pipeline-id <id> --inputs inputs/<case>.json --no-cache

# Dashboard: http://localhost:7474/revisar
# Regression: bash scripts/regression_cross_asset_recovery.sh
```

---

## 7. Fuente de verdad (orden estricto)

1. `Phases/phase-{N}/docs/es/` — constitución (gobierna conflictos)
2. `CLAUDE.md` (este archivo) — doctrina operativa actual
3. `AGENTS.md` — guía operativa (heredado, ahora subordinado a CLAUDE.md)
4. `runtime-orchestrator/` + suite de tests
5. `phase_registry.py` + `phase_units.py` (V5)
6. `AI_SCAFFOLDING_REGISTRY.md` (FROZEN en 9 items)

---

## 8. Pendiente post-V6

V6 cerrado. Próximas líneas (V7):
- V7 — Phase 7 depth (motor_054 belief_revision_event desde eventos reales)
- V7 — Cascade S1-S9 scaffolding registry (regenerar S4 patterns desde IIAR, S5 YAMLs, etc.)
- V7 — Procesar 105 PDFs restantes
- V7 — motor_017 opt-in a `enforce_render_gate()` para refuse-by-default
- V7 — Dashboard surface para QAScoreCard + RenderGateVerdict
- `git push` al remote (14 commits V6 + 16 V5 pendientes)

## 9. V6 hard mode (opt-in)

```bash
export ZLAB_VALIDATORS_HARD_BLOCK=1   # warn → BLOCK en 14 reglas canónicas
export ZLAB_RENDER_STRICT_DEFAULT=1   # refuse render si state != client_safe
```

Ver `RECOVERY_DONE_V6.md` para la lista completa.
