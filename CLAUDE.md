# CLAUDE.md — ZLab Operational Truth Framework

> **Ancla constitucional para sesiones de Claude trabajando en este repo.**
> Leer ENTERO antes de tocar código.

**Última actualización: 2026-05-13 (post V5 P13, entrando V6 Stability Hardening)**

---

## 0. Doctrina actual: V6 STABILITY HARDENING

El framework V5 ya tiene la INTELIGENCIA. V4-V5 entregaron 8 fases canónicas, 64 motores cableados, 1483 tests, regression 7/7, deterministic extraction, narrator hardening.

**V6 NO añade inteligencia. V6 estabiliza el cerebro.**

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

## 4. Estado pre-V6 (2026-05-13)

- **64 motores** en `governanza/automation-base/motor_dependencies.json`
- **1483 tests passing** (`pytest tests/`)
- **Regression cross-asset 7/7** (6 representative + hybrid)
- **192 fuentes industriales** en catálogo (78/87/27 tier-1/2/3)
- **30 patterns** + **4 combinations approved** + **144 approved knowledge** (143 batch + 1 manual)
- **16 commits V5** en `main` local (no pushed)
- **Jurisdicción**: US-only para case discovery; combinations universales

---

## 5. V6 STABILITY HARDENING — los 18 items y su estado

Auditado 2026-05-13. La mayoría ya existe estructuralmente. **El trabajo V6 es PROMOTION de warn→BLOCK + 3 piezas nuevas pequeñas.**

| # | Item | Estado actual | Trabajo V6 |
|---|---|---|---|
| 1 | System State Machine (8 estados) | ✅ `report_state_machine.py` con los 8 exactos | Promover defaults a strict |
| 2 | Hard Block Validation Layer | ⚠️ Validators emiten WARN | Flip warn→BLOCK en motor_055-063 |
| 3 | Asset Family Isolation Engine | ✅ motor_061 + 30 patterns | Añadir `allowed_*`/`forbidden_*` declarations |
| 4 | Hybrid Justification Engine | ✅ motor_062 SJ1/SJ2/SJ3 + hybrids.json | Promover modo `block` por defecto |
| 5 | DUMB_RENDER (composer) | ✅ motor_017/019 con epistemic law | Auditoría — no introducir lógica |
| 6 | Chart Validity Engine | ✅ motor_063 CV1-CV4 | Promover warn→BLOCK |
| 7 | Combination Governance | ⚠️ approval workflow existe | Schema enforcement at write-time |
| 8 | Evidence Specialization | ✅ motor_056 ER1-ER3 | Promover warn→BLOCK + per-combo packs |
| 9 | Report Uniqueness Engine | ✅ motor_058 RU1-RU3 | Promover warn→BLOCK |
| 10 | Fallback Governance | ❌ **NO existe** | **CREAR** `fallback_policy.py` |
| 11 | Claim Synchronization | ⚠️ Disperso entre 5+ motores | **CREAR** single-source-of-truth audit |
| 12 | TAD Consistency Engine | ✅ motor_059 R1-R7 | Añadir precedencias jerárquicas duras |
| 13 | Source Execution Auditor | ❌ **NO existe** | **CREAR** auditor sobre motor_028 |
| 14 | CLIENT_SAFE_MODE | ✅ `client_safe` ya en state machine | Forzar como default render-gate |
| 15 | QA Score Engine | ⚠️ Scores dispersos en motor_031 | **CREAR** agregador cross-motor |
| 16 | Stability Test Suite | ⚠️ 1483 tests pero no contamination-specific | Suite nueva |
| 17 | Resultado final | — | — |
| 18 | Entregable | — | — |

**Resumen**: 3 piezas nuevas + 7 promotions + 1 audit = sustancialmente menos trabajo que añadir 18 sistemas nuevos.

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

Una vez V6 cerrado:
- V7 — Phase 7 depth (motor_054 belief_revision_event desde eventos reales)
- V7 — Cascade S1-S9 scaffolding registry (regenerar S4 patterns desde IIAR, S5 YAMLs, etc.)
- V7 — Procesar 105 PDFs restantes
- `git push` al remote
