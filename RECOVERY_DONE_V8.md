# RECOVERY_DONE_V8.md — Final Release Hardening (cerrado)

**Phase**: V8 Final Release Hardening (Chief QA Architect prompt)
**Anchor**: "Ajuste fino para llegar a 98-99% client-deliverable."
**Baseline**: V7 cerrado (HEAD `e0699d5`, 1721 tests, regression 7/7).
**Resultado**: V8 cerrado en HEAD post-`e049cef`. **1806 tests verde** (+85 vs V7).

---

## Doctrina

V7 endureció la ejecución (hard mode default, catálogo migrado).
V8 cerró los 8 gaps residuales del Chief QA Architect audit:
template contamination hard block, CV6 chart provenance, hybrid
governance object completo, TAD claim sync rewrite, evidence
branching engine, source authority tier, section-level fallback,
Final Delivery Gate YAML.

V8 NO reinventó nada. Sólo conectó/extendió piezas existentes.

---

## Sub-fases entregadas

| # | Sub-fase | Status | Tests | Commit |
|---|---|---|---|---|
| P0  | Baseline freeze + skeleton                                  | ✅ | 1721 | `2ebb503` |
| P1  | `template_contamination_failure` hard block en render_gate  | ✅ | 1728 | `02f3dc0` |
| P2  | CV6 chart `source_case_id` provenance                       | ✅ | 1738 | `219ff4b` |
| P3  | Hybrid Governance Object (10 campos)                        | ✅ | 1745 | `e3a4ed8` |
| P4  | TAD Claim Sync rewrite (DO_NOT_*)                           | ✅ | 1756 | `be2e007` |
| P5  | Evidence Branching Engine (per-hypothesis matrix)           | ✅ | 1766 | `3409e31` |
| P6  | Source Authority Tier classification                        | ✅ | 1778 | `5cffd5c` |
| P7  | Section-level Fallback Governance                           | ✅ | 1788 | `29c8c2f` |
| P8  | Final Delivery Gate YAML block                              | ✅ | 1797 | `9179e58` |
| P9  | Stability suite V8 end-to-end (8 + control)                 | ✅ | 1806 | `e049cef` |
| P10 | Docs + regression + push                                    | ✅ | 1806 | post-`e049cef` |

---

## Endurecimientos V8 (vs V7)

### 1. Template Contamination hard block (P1)

- `template_contamination_is_blocking` nuevo en motor_016 (narrow signal,
  sólo cuando comparison_summary detecta heritage real).
- `render_gate` rechaza en AMBOS modos (soft + strict). Bypass via
  `pipeline_inputs.__template_contamination_force_render__=True`.
- motor_017 surface el block_reason independiente del strict mode.

### 2. CV6 chart provenance (P2)

- `_detect_CV6_chart_wrong_source_case_id` en motor_063.
- Chart `intelligence_binding.source_case_id` ≠ current case_id (case-insensitive)
  AND no `reusable_generic=True` ⇒ blocking.
- En _V6_BLOCKING_RULES → hard mode default promueve a "blocking".

### 3. Hybrid Governance Object (P3)

- 5 hybrids en `asset_family_hybrids.json` backfilled con 7 campos nuevos:
  scope_allowed, scope_prohibited, evidence_to_confirm, evidence_to_falsify,
  report_sections_allowed, report_sections_blocked, tad_impact.
- `build_hybrid_governance_object` devuelve dict con los 10 campos canónicos.
- motor_061 emite `hybrid_governance_object` además del narrative WHY.

### 4. TAD Claim Sync (P4)

- Nuevo módulo `tad_claim_sync.py` con 6 rewrites canónicos:
  DO_NOT_MODEL_YET, DO_NOT_SENSOR_YET, DO_NOT_RETROFIT_YET,
  DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET, COMPARE_ONLY_AFTER_NORMALIZATION,
  REQUEST_EVIDENCE_FIRST.
- `tad_action_registry.py` añade 3 statuses nuevos.
- motor_033 aplica `enforce_tad_action_postures` antes de emitir el register.
- Cada rewrite incluye `forbidden_language` list para motor_019 (narrador).

### 5. Evidence Branching Engine (P5)

- Nuevo módulo `evidence_branching.py`:
  - `EvidenceBranch` dataclass (hypothesis_id + 6 paths).
  - `build_evidence_branch_from_spec` / `build_evidence_branches`.
  - `audit_branch_repetition` (EB1_branch_evidence_repetition warning).
  - `summarize_branches` helper.

### 6. Source Authority Tier (P6)

- `SourceAuthorityTier` enum: IDENTITY / PERMIT_EMISSIONS / BENCHMARK / REFERENCE / OTHER.
- Prefix-map sec_, county_, epa_, npdes_, energystar_, cbecs_, iiar_, ashrae_, eia_, etc.
- `SourceGap` gana fields `authority_tier`, `blocks_client_safe`.
- `client_safe_compatible` helper consumed por render_gate.

### 7. Section-level Fallback (P7)

- `HIGH_VALUE_SECTIONS` constant (6 secciones canónicas).
- `FallbackEvent.section_id` field + `is_high_value_section()`.
- `FallbackPolicyVerdict.high_value_section_downgrades`.
- render_gate refuses cuando high_value_section_downgrades > 0 en strict.

### 8. Final Delivery Gate YAML (P8)

- `RenderGateVerdict.publication_mode()` → "client_safe" / "publish_with_degradation" / "internal_debug_only" / "blocked".
- `RenderGateVerdict.as_yaml_block()` → string YAML con los 8 gates canónicos.
- motor_017 surface en output: `final_delivery_gate_yaml` + `publication_mode`.

---

## V6 blocking set V8 = 20 reglas

- motor_057: GN1
- motor_058: RU2, RU6
- motor_059: R1, R2, R4, R8-R13 (10 rules)
- motor_061: AF1, AF2
- motor_062: SJ1, SJ2, SJ3
- motor_063: CV1, CV3, CV5, **CV6** (V8)

(R12+R13 V7 + CV5 V7 + CV6 V8 son las adiciones recientes.)

---

## Test count trajectory

| Phase | Tests | Delta |
|---|---|---|
| V7 P10 baseline | 1721 | — |
| V8 P1           | 1728 | +7  |
| V8 P2           | 1738 | +10 |
| V8 P3           | 1745 | +7  |
| V8 P4           | 1756 | +11 |
| V8 P5           | 1766 | +10 |
| V8 P6           | 1778 | +12 |
| V8 P7           | 1788 | +10 |
| V8 P8           | 1797 | +9  |
| V8 P9           | 1806 | +9  |
| V8 P10 (docs)   | 1806 | +0  |

Total V8: **+85 tests** sobre baseline V7.

Regression cross-asset 7/7 PASS en cada paso bajo hard mode default.

---

## Aceptación final V8 — cumplida

- [x] `template_contamination_failure` → render refused (ambos modos).
- [x] CV6 chart source_case_id mismatch detectado y bloqueado.
- [x] Hybrid governance object con 10 campos completos.
- [x] motor_033 reescribe `DO_NOT_MODEL_YET` etc cuando prereqs unmet.
- [x] Evidence branching engine emite per-hypothesis matrix.
- [x] Source audit clasifica por authority tier; identity/permit gaps bloquean client_safe.
- [x] Fallback section-level bloquea high-value section downgrades.
- [x] motor_017 output incluye `final_delivery_gate_yaml`.
- [x] 1806 tests verde · regression 7/7 PASS bajo V8 hard mode default.
- [x] Docs limpios.

---

## Lo que V8 NO hizo (por doctrina)

- No añadió motores, patterns o combinations.
- No añadió LLM en otro motor que no sea motor_019.
- No regeneró AI_SCAFFOLDING_REGISTRY.
- No procesó los 105 PDFs restantes.
- No expuso dashboard QA.
- No relajó epistemología.

**V8 = ajuste fino final. El cerebro es production-ready.**

---

## V9 candidato (cuando llegue)

- Phase 7 depth (motor_054 belief_revision_event) — única fase superficial.
- Cascade S1-S9 scaffolding regeneration desde extracción determinista.
- Procesamiento de los 105 PDFs restantes.
- Dashboard QA visual (QAScoreCard + RenderGateVerdict en `/revisar`).
- CI smoke job con hard mode default ON.
