# RECOVERY_V9_BACKLOG.md — Final Architectural Closure (Chief Systems Architect)

**Doctrina V9**: post-V8 el cerebro ya es production-ready (~95-96% del prompt Chief Systems Architect). V9 cierra los 3 mecanismos arquitectónicos finales del prompt SIN entrar al trabajo de contenido (industry breadth + fetcher breadth = V10).

**Anchor**: Chief Systems Architect / Industrial Intelligence Lead / Epistemic Governance Engineer prompt (2026-05-14).

**Baseline**: V8 cerrado (HEAD `b184b8a`, 1806 tests, regression 7/7 hard mode default).

---

## 0. Audit honesto: 13 secciones vs realidad

| § Prompt | Estado | Veredicto |
|---|---|---|
| 1 Industrial Operating Intelligence | 144 approved + 30 patterns; breadth limitado | ⚠️ V10 (contenido) |
| 2 Knowledge Memory | 5-state dirs + 8 fields validados | ✅ |
| 3 Combination Engine | 9 fields strict V6/V7/V8 | ✅ |
| 4 Fair Comparison Engine | motor_051 sin objeto 10-dim explícito | ❌ **V9 P1** |
| 5 Hybrid Asset Governance | V7 P4 + V8 P3 | ✅ |
| 6 Source Routing & Execution | 7-10 fetchers reales, 7-10 stubs | ⚠️ V10 (contenido) |
| 7 Evidence Branching | V8 P5 | ✅ |
| 8 Final Client Ready Gate | V8 P8 | ✅ |
| 9 Artifact / Chart Safety | section_id + hypothesis_supported NO enforced | ❌ **V9 P2** |
| 10 TAD Synchronization | V8 P4 | ✅ |
| 11 Reporting Engine | output_blocks + claim ceiling existen | ✅ |
| 12 Scalability | sin workflow industrial onboarding | ❌ **V9 P3** |
| 13 QA Hardening | 11 hard validators wired | ✅ |

**Veredicto**: 3 gaps arquitectónicos (V9 P1/P2/P3). Industry breadth + fetcher breadth = V10 (trabajo de contenido, no framework).

---

## 1. Plan V9 — 6 sub-fases secuenciales

### V9 P0 — Baseline + skeleton (½ día) · BAJO

- HEAD `b184b8a` · 1806 tests · regression 7/7.
- Crear `RECOVERY_DONE_V9.md` esqueleto.
- Commit `recovery(v9p0): baseline + plan anchor`.

---

### V9 P1 — Fair Comparison Engine 10-dim (1 día) · MEDIO

**Problema (§ 4)**: motor_051 hace fair_comparison pero no emite el contrato 10-dimensional canónico ni un `comparability_score` explícito.

**Cambio**:
- Nuevo módulo `fair_comparison.py`:
  - `PeerComparabilityContract` dataclass (10 dimensiones: asset_family, process_family, thermal_regime, throughput_band, operating_hours, dock_density, charging_profile, tariff_profile, control_boundary, regulatory_context).
  - `evaluate_peer_set(candidate, peer_set) → ComparabilityVerdict` (per-dimension match + overall_score).
  - `requires_blocking_when_incomplete=True` por defecto.
  - Helper `peer_set_admissible(verdict) → bool`.
- motor_051 wire: emite `peer_set_comparability_contract` en output.
- motor_059 R14_peer_ranking_with_incomplete_comparability nueva regla en _V6_BLOCKING_RULES.

**Tests**: ~10 (10 dimensiones individuales + cardinality + score threshold + admissibility + motor_051 integration).

---

### V9 P2 — Chart CV7 + CV8 (½ día) · BAJO

**Problema (§ 9)**: V7 P7 CV5 (asset_family) + V8 P2 CV6 (source_case_id) cubren 2 de las 6 declaraciones. Faltan `section_id` y `hypothesis_supported`.

**Cambio en motor_063**:
- `_detect_CV7_chart_without_section_id`: chart con `intelligence_binding` no vacío pero sin `section_id` → warning.
- `_detect_CV8_chart_without_hypothesis_supported`: chart con `intelligence_binding` no vacío pero sin `hypothesis_supported` (o `claim_id` o `thesis_id`) → warning.
- Ambas en `_V6_BLOCKING_RULES`.

**Tests**: ~8 (CV7 + CV8 unit + integration + V6 blocking promotion).

---

### V9 P3 — Industry Onboarding Workflow (1 día) · MEDIO

**Problema (§ 12)**: añadir industria nueva = autoría manual sin checklist canónico.

**Cambio**:
- Nuevo módulo `industry_onboarding.py`:
  - `IndustryOnboardingChecklist` dataclass con 10 requisitos:
    1. process_taxonomy (lista de procesos canónicos)
    2. machine_taxonomy
    3. dominant_variables (lista)
    4. failure_modes
    5. evidence_map (per-hypothesis)
    6. financial_translation
    7. regulatory_triggers
    8. combinations (≥1 combo activable)
    9. tad_mapping (mínimo 3 acciones canónicas)
    10. qa_tests (mínimo 1 acceptance scenario)
  - `validate_industry_readiness(spec) → OnboardingVerdict` con `ready: bool` + per-requirement status.
  - `IndustrySpec` dataclass + JSON schema (`industries/<industry_id>.json`).
- Test fixture: una industria sintética demo (`thermal_process_demo`) ready + una incompleta (missing combinations).

**NO añade** industrias reales (eso es V10). Sólo el framework de onboarding.

**Tests**: ~12 (10 requirement checks + 2 e2e).

---

### V9 P4 — Stability suite V9 (½ día) · BAJO

4 escenarios + control:
- S0 Clean peer set + clean charts + ready industry → allows
- S1 Incomplete peer set (3 dims missing) → refuses
- S2 Chart sin section_id (CV7) → refuses
- S3 Chart sin hypothesis_supported (CV8) → refuses
- S4 Industry onboarding incomplete → validate_industry_readiness rejects

**Tests**: 5.

---

### V9 P5 — Docs + regression + push (¼ día) · BAJO

- Actualizar `CLAUDE.md` a V9 cerrado.
- Completar `RECOVERY_DONE_V9.md` con trayectoria.
- Archivar `RECOVERY_V9_BACKLOG.md` a `docs/history/`.
- `pytest -q` y regression cross-asset 7/7 bajo V9 hard mode default.
- Commit `recovery(v9p5): close V9 Final Architectural Closure`.
- Push.

---

## 2. Reglas inviolables V9

1. NO añadir motores, patterns, combinations.
2. NO romper 1806 tests V8 ni regression 7/7.
3. NO debilitar lógica V5-V8 enumerada en "NO DAÑAR" del prompt.
4. NO push sin autorización al final.
5. Commit por sub-fase, mensajes `recovery(v9pN):`.
6. V9 NO toca industry breadth ni fetcher breadth (V10).

---

## 3. Aceptación final V9

- [x] Fair Comparison emite peer_set_comparability_contract con 10 dimensiones explícitas.
- [x] CV7 + CV8 enforced en motor_063, en V6 blocking set.
- [x] Industry onboarding checklist validable con `validate_industry_readiness`.
- [x] ~1840+ tests verde · regression 7/7 PASS.

---

## 4. Lo que V9 NO hace

- No añade pharma / district energy / utilities patterns (V10).
- No añade IIAR / ISA / IEEE / MEASUR fetchers (V10).
- No regenera AI_SCAFFOLDING_REGISTRY.
- No procesa los 105 PDFs restantes.

**V9 = cierre arquitectónico final. V10 = trabajo de contenido si llega.**
