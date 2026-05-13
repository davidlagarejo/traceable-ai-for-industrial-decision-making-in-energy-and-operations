# RECOVERY V6 — Stability Hardening Backlog

**Open: 2026-05-13. Doctrina: V5 P0-P13 cerró la INTELIGENCIA. V6 estabiliza el CEREBRO.**

---

## V6 P0 — Baseline freeze (THIS COMMIT)

### Invariantes que V6 NO debe romper

```
tests passing       : 1483    ← hard floor; cada sub-fase puede subir, nunca bajar
regression 7/7      : PASS    ← cold_chain + manufacturing + warehouse + datacenter
                                 + building + infrastructure + hybrid_e2e
phase 0-8 coverage  : ✓       ← las 8 unidades canónicas emiten cleanly
LLM containment     : motor_019 only    ← Phase 0 inviolable
extraction path     : deterministic     ← zlab_skill.local_pdf_autodraft
combinations approved: 4               ← 2 user + 2 S7 scaffolding
patterns registry   : 30
approved knowledge  : 144              ← 1 manual + 143 batch v5
catalog sources     : 192 (78/87/27 tier-1/2/3)
```

### Doctrina V6 (heredada del prompt del usuario)

> "No agregar más inteligencia. Estabilizar."

**Reglas absolutas durante V6:**
1. No agregar más inteligencia hasta cerrar V6.
2. No relajar epistemología.
3. No permitir rendering thinking.
4. No permitir chart reuse cross-asset-family.
5. No permitir unsupported hybrid activation.
6. No permitir report generation después de validator failure.
7. No permitir fallback silencioso.

---

## V6 — Las 12 sub-fases (orden quirúrgico)

| # | Sub-fase | Trabajo | Esfuerzo | Riesgo |
|---|---|---|---|---|
| P0 | Baseline freeze | Este doc + CLAUDE.md | 30 min | None |
| P1 | `fallback_policy.py` | Pieza nueva — tri-modal policy | 1h | Bajo |
| P2 | `source_execution_auditor.py` | Pieza nueva — audit motor_028 gaps | 1h | Bajo |
| P3 | `qa_score.py` | Pieza nueva — 7 scores agregados | 1.5h | Medio |
| P4 | Promote validators warn→BLOCK | motor_055-063 flip por rule | 2h | **Alto** |
| P5 | Asset Family Isolation declarations | Extender 30 patterns con `isolation.*` | 1h | Medio |
| P6 | Combination Governance schema gate | validate_combination V6 schema | 45 min | Bajo |
| P7 | Claim Synchronization Auditor | Audit cross-motor claim counts | 1h | Medio |
| P8 | TAD R8-R11 precedence | motor_059 + hard precedences | 45 min | Bajo |
| P9 | CLIENT_SAFE_MODE default strict | State machine default → `{client_safe}` | 30 min | **Alto** |
| P10 | DUMB Render audit | composer_invariant_test suite | 1h | Medio |
| P11 | Stability Test Suite | 9 contamination escenarios | 1.5h | Bajo |
| P12 | RECOVERY_DONE_V6 + AGENTS.md | Docs | 30 min | None |

**Total: ~13h. 3-4 sesiones de trabajo.**

---

## V6 — Mapeo a 18 items del prompt

```
Prompt item                              → V6 sub-fase
─────────────────────────────────────────────────────────
1.  System State Machine (8 states)      → P9 (existe, sólo strict-default)
2.  Hard Block Validation Layer          → P4 (promote warn→BLOCK)
3.  Asset Family Isolation Engine        → P5 (declarations) + P4 (motor_061 block)
4.  Hybrid Justification Engine          → P4 (motor_062 block default)
5.  DUMB Render Composer                 → P10 (audit invariant)
6.  Chart Validity Engine                → P4 (motor_063 CV1/CV3 block)
7.  Combination Governance               → P6 (schema gate at propose)
8.  Evidence Specialization              → P4 (motor_056 block) + P5 (per-combo packs)
9.  Report Uniqueness Engine             → P4 (motor_058 RU2 block)
10. Fallback Governance                  → P1 (CREATE)
11. Claim Synchronization                → P7 (CREATE auditor)
12. TAD Consistency Engine               → P8 (R8-R11)
13. Source Execution Auditor             → P2 (CREATE)
14. CLIENT_SAFE_MODE                     → P9 (strict default)
15. QA Score Engine                      → P3 (CREATE aggregator)
16. Stability Test Suite                 → P11 (CREATE 9 escenarios)
17. Resultado: stable framework          → cumulativo
18. Entregable                           → cumulativo
```

**3 piezas verdaderamente nuevas** (P1, P2, P3, P7, P11).
**7 promoçoes** de warn→BLOCK (P4 + P8 + P9).
**1 schema enforcement** (P6).
**1 declarations extension** (P5).
**1 invariant test** (P10).
**1 docs** (P12).

---

## V6 — Qué NUNCA debe romperse

- Regression 7/7 cross-asset
- 1483 tests baseline (puede subir, nunca bajar)
- Phase 0 anchor (LLM sólo en motor_019)
- 8 unidades canónicas (V5 P10-P13)
- Loop deterministic extraction sin LLM

---

## V6 — Pendiente post-V6 (V7+)

- Phase 7 depth (motor_054 belief_revision_event eventos reales)
- Cascade S1-S9 + nuevo S10 (V6 P5 isolation declarations)
- Procesar 105 PDFs restantes en batch
- `git push` al remote
