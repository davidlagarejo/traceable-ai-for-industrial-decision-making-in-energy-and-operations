# RECOVERY_DONE_V9.md — Final Architectural Closure (cerrado)

**Phase**: V9 Final Architectural Closure (Chief Systems Architect prompt)
**Anchor**: "100% client-ready arquitectónico. Contenido (industries / fetchers) = V10."
**Baseline**: V8 cerrado (HEAD `b184b8a`, 1806 tests, regression 7/7).
**Resultado**: V9 cerrado. **1846 tests verde** (+40 vs V8).

---

## Doctrina

V8 cerró el ajuste fino de ejecución (template contamination, CV6, hybrid governance, TAD sync, evidence branching, source authority tier, section-level fallback, Final Delivery Gate YAML).

V9 cierra los 3 mecanismos arquitectónicos finales del prompt Chief Systems Architect:
1. **Fair Comparison Engine 10-dim** (§ 4)
2. **Chart artifact safety section_id + hypothesis_supported** (§ 9)
3. **Industry Onboarding Workflow** (§ 12)

**Industry breadth + fetcher breadth NO son trabajo V9** — son trabajo de contenido / catálogo que V10 retomaría.

---

## Sub-fases entregadas

| # | Sub-fase | Status | Tests | Commit |
|---|---|---|---|---|
| P0 | Baseline + plan anchor                                | ✅ | 1806 | `c269ab1` |
| P1 | Fair Comparison Engine 10-dim + R14 blocking          | ✅ | 1818 | `cfafbb5` |
| P2 | Chart CV7 (section_id) + CV8 (hypothesis_supported)   | ✅ | 1829 | `0d9d3a8` |
| P3 | Industry Onboarding Workflow                          | ✅ | 1841 | `45b1d7a` |
| P4 | Final Architectural Stability Suite                   | ✅ | 1846 | `c3d831c` |
| P5 | Docs + regression + push                              | ✅ | 1846 | post-`c3d831c` |

---

## Mecanismos V9 nuevos

### 1. Fair Comparison Engine 10-dim (P1)

`fair_comparison.py`:
- `CANONICAL_PEER_DIMENSIONS` (10): asset_family, process_family, thermal_regime, throughput_band, operating_hours, dock_density, charging_profile, tariff_profile, control_boundary, regulatory_context.
- `PeerComparabilityContract` per-peer (matched/mismatched/missing + score + admissible).
- `ComparabilityVerdict` per-peer-set (admissible_peers, rejected_peers, peer_set_admissible).
- `evaluate_peer_set`, `peer_set_admissible`, `summarize_for_motor_output`.

motor_059: `R14_peer_ranking_with_incomplete_comparability` blocking rule
(en `_V6_BLOCKING_RULES` → hard mode default promueve a "blocking").

### 2. Chart Artifact Safety CV7 + CV8 (P2)

motor_063:
- `_detect_CV7_chart_without_section_id`: chart con binding pero sin section_id → warning.
- `_detect_CV8_chart_without_hypothesis_supported`: chart con binding pero sin hypothesis_supported / claim_id / thesis_id → warning.
- Ambas en `_V6_BLOCKING_RULES`.

**Combined V6/V7/V8/V9 chart validity**: CV1-CV8 (decorative_risk, unbound, decorative_ratio, no_charts_with_thesis, cross_asset_family, wrong_source_case_id, no_section_id, no_hypothesis_supported).

### 3. Industry Onboarding Workflow (P3)

`industry_onboarding.py`:
- `CANONICAL_INDUSTRY_REQUIREMENTS` (10): process_taxonomy, machine_taxonomy, dominant_variables, failure_modes, evidence_map, financial_translation, regulatory_triggers, combinations, tad_mapping, qa_tests.
- `IndustrySpec` dataclass JSON-serializable.
- `OnboardingVerdict` (ready + per_requirement + missing + reasons).
- `validate_industry_readiness(spec)` + `industry_onboarding_summary(verdicts)`.

V9 NO añade industrias reales — provee el framework para que V10 las añada con gate.

---

## V6 blocking set V9 = 23 reglas

- motor_057: GN1
- motor_058: RU2, RU6
- motor_059: R1, R2, R4, R8-R14 (11)
- motor_061: AF1, AF2
- motor_062: SJ1, SJ2, SJ3
- motor_063: CV1, CV3, CV5, CV6, **CV7**, **CV8** (V9, 6)

(V9 adds 3 rules: R14 + CV7 + CV8.)

---

## Test count trajectory

| Phase | Tests | Delta |
|---|---|---|
| V8 P10 baseline | 1806 | — |
| V9 P1           | 1818 | +12 |
| V9 P2           | 1829 | +11 |
| V9 P3           | 1841 | +12 |
| V9 P4           | 1846 | +5  |
| V9 P5 (docs)    | 1846 | +0  |

Total V9: **+40 tests** sobre baseline V8.

Regression cross-asset 7/7 PASS en cada paso bajo V9 hard mode default.

---

## Aceptación final V9 — cumplida

- [x] Fair Comparison emite contrato 10-dim explícito + admissibility score.
- [x] R14_peer_ranking_with_incomplete_comparability blocking en motor_059.
- [x] CV7 (section_id) + CV8 (hypothesis_supported) enforced en motor_063.
- [x] `validate_industry_readiness` checklist 10-requisitos canónico.
- [x] 1846 tests verde · regression cross-asset 7/7 PASS bajo V9 hard mode default.
- [x] Docs limpios.

---

## Lo que V9 NO hizo (por doctrina — V10 candidato)

- No añadió industrias reales (pharma, district energy, utilities).
- No añadió fetchers IIAR / ISA / IEEE / MEASUR / DOE Better Plants.
- No regeneró AI_SCAFFOLDING_REGISTRY.
- No procesó los 105 PDFs restantes.
- No expuso dashboard QA visual.

**V9 = cierre arquitectónico final del prompt Chief Systems Architect.
V10 = trabajo de contenido si se requiere.**

---

## V10 candidato (cuando llegue)

- **Industry breadth** (§ 1, § 12): autoría / extracción determinista de patterns para pharma, district energy, utilities, thermal process site. Usar V9 `validate_industry_readiness` como gate.
- **Source fetcher breadth** (§ 6): implementar fetchers para IIAR, ISA, IEEE, MEASUR, VERIFI, DOE Better Plants, DOE AMO, manufacturer docs.
- **AI_SCAFFOLDING_REGISTRY regeneration** desde 143 approved knowledge + extractor V4.
- **Dashboard QA visual** (QAScoreCard + RenderGateVerdict en /revisar).
- **CI hard-mode smoke job**.

**El cerebro V9 es 100% client-ready arquitectónico.**
