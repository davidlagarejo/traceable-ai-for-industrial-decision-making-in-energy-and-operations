# RECOVERY_V8_BACKLOG.md — Final Release Hardening (Chief QA Architect)

**Doctrina V8**: ya está al ~85-90% post-V7. Esto es el ajuste fino final para llegar a 98-99% client-deliverable. No se añade inteligencia, no se cambia lógica, no se hacen módulos nuevos grandes. Se **conectan piezas que ya existen pero no se aplican** y se **rellenan 8 gaps concretos** detectados por el QA audit.

**Anchor**: Chief QA Architect / Epistemic Governance Engineer / Final-Release Auditor prompt (2026-05-13).

---

## 0. Audit honesto: prompt vs realidad

| § Prompt | Pieza | Estado real |
|---|---|---|
| Error 1 | `template_contamination_failure` hard block | ✅ flag existe en motor_016/024/027; ❌ render_gate NO lo consume como hard block |
| Error 2 | Chart contamination | ✅ CV1/CV2/CV3 V6 + CV5 V7; ❌ NO existe `source_case_id` por chart, NO CV6 |
| Error 3 | Hybrid asset logic justification | ✅ V7 P4 narrative WHY; ❌ NO 10-field structured `HYBRID_JUSTIFICATION_OBJECT` |
| Error 4 | TAD ↔ Claim Governor sync | ✅ `DO_NOT_*` statuses ya canónicos en `tad_action_registry.py`; ⚠️ R8/R2/R3 detectan; ❌ NO enforced rewrite del posture cuando prerequisites unmet |
| Error 5 | Evidence packs repetidos | ✅ RU6 V7 detecta intra-run; ❌ NO per-hypothesis matrix output |
| Error 6 | Source routing required + unqueried | ✅ V6 P2 + V6 P13.2; ❌ NO authority tier (identity/permit/emissions/benchmark) classification |
| A. Final QA Gate | ✅ render_gate V6 P9 / V7 P8; ❌ NO YAML block embedded en motor_017 output / PDF |
| B. Chart Artifact Validator | ✅ motor_063 CV1-CV5; ❌ NO source_case_id / hypothesis_supported / reusable_generic fields |
| C. Hybrid Asset Governor | ✅ V7 P4 narrative; ❌ NO scope_allowed / scope_prohibited / sections_allowed / sections_blocked |
| D. TAD Sync Engine | ✅ R2/R3/R8-R13 detectan; ❌ NO motor_033 rewrite del action posture |
| E. Evidence Branching Engine | ✅ pattern_spec.evidence_required existe; ❌ NO motor agrega per-hypothesis matrix |
| F. Source Execution Gate | ✅ V6 P2; ❌ NO authority tier + per-tier policy |
| G. Fallback Governance | ✅ V6 P1 tri-modal; ❌ NO section-level (HIGH_VALUE_SECTIONS) |

**Conclusión**: ~70% del prompt ya está cubierto por V6/V7. V8 cubre el 30% residual con **extensiones quirúrgicas** a módulos existentes (sin nuevos motores).

---

## 1. Plan V8 — 10 sub-fases secuenciales

Cada sub-fase = un cambio concreto + tests + regression cross-asset + commit. Sin saltos.

---

### V8 P0 — Baseline freeze + DONE skeleton (½ día) · RIESGO BAJO

- Confirmar HEAD = `e0699d5` (1721 tests, regression 7/7 verde bajo hard mode default).
- Crear `RECOVERY_DONE_V8.md` skeleton con tabla de 10 sub-fases vacías.
- NO toca código.

**Aceptación**: commit `recovery(v8p0): baseline + plan anchor`.

---

### V8 P1 — `template_contamination_failure` hard block en render_gate (½ día) · RIESGO BAJO

**Problema (Error 1 del prompt)**: el flag se calcula y se propaga pero el render gate NO lo consume como hard block. Hoy llega a "Publish With Degradation" cuando debería ser `internal_debug_only`.

**Cambio**:
- `render_gate.evaluate_render_gate()` gana parámetro nuevo `template_contamination_failure: bool = False`.
- Si `True` en strict mode → `verdict.allowed = False`, reason `"template_contamination_failure_detected"`.
- motor_017 ya lee `motor_016.template_contamination_failure` (campo existe); le pasa al render_gate.

**Wiring**:
- motor_017 lee `m016.get("template_contamination_failure")` (ya disponible vía report_package o root).
- Pasa al render_gate.

**Tests**: 4 tests (true → refuse strict, true → allow soft, false → allow, integración motor_017).

**Aceptación**: 1725+ tests verde.

---

### V8 P2 — CV6 chart source_case_id provenance (1 día) · RIESGO MEDIO

**Problema (Error 2)**: el sistema NO bloquea un chart que viene de OTRO caso (Office GFA Breakdown en un cold-chain).

**Cambio**:
- motor_063: nuevo detector `_detect_CV6_chart_wrong_source_case_id`.
- Cada chart debe declarar en `intelligence_binding.source_case_id` el case_id del que proviene.
- Excepción: charts marcados `intelligence_binding.reusable_generic = true` (charts conceptuales que no carry case data).
- Si chart `source_case_id` ≠ current case AND no es reusable_generic → emit CV6 warning.
- CV6 entra a `_V6_BLOCKING_RULES` → hard mode default promueve a blocking.

**Wiring**:
- motor_018 (chart producer) debe ahora EMIT `source_case_id` en cada chart binding. Backfill: cuando no esté, defaultear al current case_id (asume motor_018 lo conoce vía motor_007).
- motor_063 lee target case_id desde motor_007 (ya añadido en V7 P7).

**Tests**: 7 tests + ajuste de tests existentes si motor_018 emite source_case_id nuevo.

**Aceptación**: 1735+ tests verde.

---

### V8 P3 — Hybrid Governance Object completo (1 día) · RIESGO MEDIO

**Problema (Error 3 + § C)**: V7 P4 emite la WHY string. Falta el objeto estructurado con scope_allowed, scope_prohibited, evidence_to_confirm, evidence_to_falsify, sections_allowed, sections_blocked, tad_impact.

**Cambio**:
- Extender `asset_family_hybrids.json` schema: añadir 7 campos opcionales por hybrid:
  - `scope_allowed: list[str]` — tipos de lógica admisibles
  - `scope_prohibited: list[str]` — lógica que NO se autoriza
  - `evidence_to_confirm: list[str]`
  - `evidence_to_falsify: list[str]`
  - `report_sections_allowed: list[str]`
  - `report_sections_blocked: list[str]`
  - `tad_impact: list[str]` — qué acciones TAD se desbloquean / restringen
- Backfill los 5 hybrids existentes con valores razonables.
- `hybrid_justification.py`: nueva función `build_hybrid_governance_object(hybrid, matched_triggers)` que devuelve dict completo.
- motor_061: emite `hybrid_governance_object` (dict con los 10 campos del prompt) además del narrative.

**Tests**: 8 tests (5 hybrids × 1 governance object presente + 3 unit).

**Aceptación**: 1743+ tests verde.

---

### V8 P4 — TAD Claim Sync rewrite enforcement (1 día) · RIESGO MEDIO

**Problema (Error 4 + § D)**: hoy motor_059 R8 emite warning si TAD propone digital_twin con dominant_variables unresolved, pero motor_033 sigue emitiendo el action con status "INVESTIGATE". El status canónico `DO_NOT_MODEL_YET` existe pero no se usa.

**Cambio**:
- Nuevo módulo `tad_claim_sync.py`:
  - `enforce_tad_action_posture(action, dominant_variables, claim_permissions) -> action_modified`
  - Si action es `build_digital_twin` y dominant_variables tienen estados {ARCHETYPAL_PRIOR, WEAK_SIGNAL} → reescribe `status` a `DO_NOT_MODEL_YET`, marca `forbidden_language=["investigate", "advance", "start modeling"]`.
  - Reglas equivalentes para `DO_NOT_SENSOR_YET`, `DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET`, `DO_NOT_RETROFIT_YET`, `REQUEST_EVIDENCE_FIRST`, `COMPARE_ONLY_AFTER_NORMALIZATION`.
- motor_033 al final del run llama `enforce_tad_action_posture` sobre cada acción.
- Test E2E: dominant variable unresolved + digital_twin action → final status = `DO_NOT_MODEL_YET`.

**Tests**: 10 tests.

**Aceptación**: 1753+ tests verde. regression cross-asset 7/7 (motor_033 cambia output — ajuste si rompe assertions).

---

### V8 P5 — Evidence Branching Engine (½ día) · RIESGO BAJO

**Problema (Error 5 + § E)**: el output actual repite el mismo "primary discriminator pack". Cada hipótesis debe tener su evidence branch.

**Cambio**:
- Nuevo módulo `evidence_branching.py`:
  - `build_evidence_branches(activated_patterns, activated_combinations) -> list[EvidenceBranch]`
  - Cada `EvidenceBranch` = {hypothesis_id, minimum_evidence, cheapest_path, escalation_path, confirms_when, falsifies_when, tad_impact}.
  - Lee `pattern_spec.evidence_required` + `pattern_spec.minimum_evidence_to_confirm` + `pattern_spec.minimum_evidence_to_activate` + `pattern_spec.falsification_conditions`.
- motor_014 (o motor_016 — el composer) emite `evidence_branching_register` con la matriz.
- Detección de repetición: si 3+ branches tienen Jaccard > 0.80 entre sus minimum_evidence → emit warning (refuerza RU6, no la sustituye).

**Tests**: 8 tests.

**Aceptación**: 1761+ tests verde.

---

### V8 P6 — Source Authority Tier classification (½ día) · RIESGO BAJO

**Problema (Error 6 + § F)**: el auditor distingue justificado / no, pero no por authority tier. El prompt exige reglas distintas por tier.

**Cambio**:
- Extender `source_execution_auditor.py`:
  - Nuevo enum `SourceAuthorityTier`: `IDENTITY` (county assessor, property records), `PERMIT_EMISSIONS` (state permits, air/water), `BENCHMARK` (ENERGY STAR, CBECS), `REFERENCE` (ASHRAE, IIAR), `OTHER`.
  - `_SOURCE_AUTHORITY_MAP: dict[source_key_prefix → tier]`.
  - `SourceGap` gana campos `tier`, `required_for_client_safe: bool`.
  - Nuevo helper `client_safe_compatible(report: SourceExecutionAuditReport) -> tuple[bool, list[str]]`.
- render_gate consume `client_safe_compatible` resultado: si False → refuse en strict mode.

**Tests**: 10 tests (5 tiers × clasificación + integración render_gate).

**Aceptación**: 1771+ tests verde.

---

### V8 P7 — Section-level Fallback Governance (½ día) · RIESGO BAJO

**Problema (Error G)**: fallback_policy es tri-modal pero NO por sección. Una sección crítica (Executive Thesis) downgrade silenciosa rompe el reporte client-safe.

**Cambio**:
- Extender `fallback_policy.py`:
  - Constante `_HIGH_VALUE_SECTIONS = frozenset({"executive_structural_thesis", "tad", "financial_exposure", "peer_comparison", "conditional_redesign", "case_adaptation_memo"})`.
  - `SectionFallbackVerdict` dataclass.
  - `assess_section_fallback(section_id, events) -> SectionFallbackVerdict`.
  - `FallbackPolicyVerdict` gana `high_value_section_downgrades: int`.
- motor_019 (narrador) registra section_id en cada FallbackEvent.
- motor_024 agrega el conteo.
- render_gate: si `high_value_section_downgrades > 0` → refuse en strict mode.

**Tests**: 8 tests.

**Aceptación**: 1779+ tests verde.

---

### V8 P8 — Final Delivery Gate YAML block (½ día) · RIESGO BAJO

**Problema (§ Required output changes)**: el render_gate verdict existe pero no se ve en el PDF. El prompt exige un YAML block.

**Cambio**:
- `render_gate.RenderGateVerdict` gana método `as_yaml_block() -> str`.
- motor_017 emite el YAML block como parte del PDF (sección "Final Delivery Gate") cuando el reporte se renderiza.
- También se guarda en `render_gate_verdict.yaml_block` en el output dict.

**Tests**: 6 tests (formato YAML, contenido de los 8 campos, integración motor_017).

**Aceptación**: 1785+ tests verde.

---

### V8 P9 — Stability suite V8 end-to-end (1 día) · RIESGO MEDIO

8 escenarios nuevos:

- S1  Template contamination → render refused
- S2  Chart from wrong case_id → CV6 fires
- S3  Hybrid sin scope_allowed → governance object refuses
- S4  TAD digital_twin con archetypal dominant var → status rewritten a DO_NOT_MODEL_YET
- S5  Evidence branches todas con Jaccard > 0.80 → warning
- S6  Identity-tier source no queried → client_safe = false
- S7  Executive thesis section downgraded a fallback → render refused
- S8  Final Delivery Gate YAML embedded correctamente

**Tests**: 8 tests + 1 control "clean run".

**Aceptación**: 1794+ tests verde.

---

### V8 P10 — Docs + final regression + push (½ día) · RIESGO BAJO

- Actualizar `CLAUDE.md`: V8 cerrado, número de tests, fecha.
- Completar `RECOVERY_DONE_V8.md` con trayectoria por sub-fase.
- Mover `RECOVERY_V7_BACKLOG.md` a `docs/history/` (V7 ya cerrado).
- Verificar `pytest -q` y regression cross-asset bajo V8 hard mode default.
- Commit `recovery(v8p10): close V8 Final Release Hardening`.
- `git push origin main` (con autorización).

---

## 2. Reglas inviolables del trabajo V8

1. **NO añadir** motores, patterns, combinations. Sólo extender módulos existentes.
2. **NO romper** las 1721 tests V7 ni la regression cross-asset 7/7.
3. **NO debilitar** lógica V5-V7 enumerada en "NO DAÑAR" del prompt:
   - reframing estratégico
   - combination intelligence
   - peer logic
   - capital allocation logic
   - no false closure (no ROI/savings/bankability/peer superiority/final redesign)
4. **Hard mode default ON** se mantiene de V7.
5. **NO push** sin autorización explícita al final.
6. Commit por sub-fase, mensajes `recovery(v8pN):`.
7. Cada cambio debe ser quirúrgico: archivos tocados ≤ 4 por sub-fase (salvo P3 hybrid backfill y P4 TAD).

---

## 3. Estimación

| Sub-fase | Esfuerzo | Riesgo |
|---|---|---|
| V8 P0 | ½ día | Bajo |
| V8 P1 template hard block | ½ día | Bajo |
| V8 P2 CV6 source_case_id | 1 día | Medio (motor_018 emite campo nuevo) |
| V8 P3 hybrid governance object | 1 día | Medio (backfill 5 hybrids JSON) |
| V8 P4 TAD sync rewrite | 1 día | Medio (motor_033 cambia output) |
| V8 P5 evidence branching | ½ día | Bajo |
| V8 P6 source authority tier | ½ día | Bajo |
| V8 P7 section-level fallback | ½ día | Bajo |
| V8 P8 YAML block | ½ día | Bajo |
| V8 P9 stability suite | 1 día | Medio |
| V8 P10 docs + push | ½ día | Bajo |
| **Total** | **~7 días** | — |

---

## 4. Aceptación final V8

Cerrado SOLO cuando:

- [x] `template_contamination_failure=True` ⇒ render_gate refuses (strict mode default).
- [x] CV6 chart source_case_id mismatch detecta charts de otros casos y bloquea.
- [x] Cada hybrid emite `hybrid_governance_object` con los 10 campos del prompt.
- [x] motor_033 reescribe action status a `DO_NOT_MODEL_YET` cuando prereqs unmet.
- [x] motor_016 (o motor_014) emite `evidence_branching_register` per hypothesis.
- [x] `source_execution_auditor` clasifica por authority tier y bloquea client_safe en gaps de tier IDENTITY/PERMIT.
- [x] `fallback_policy` bloquea client_safe cuando > 0 high-value sections downgraded.
- [x] motor_017 output dict (y opcionalmente PDF) incluye `final_delivery_gate` YAML block.
- [x] ~1795 tests verde · regression cross-asset 7/7 PASS bajo V8 hard mode default.
- [x] Docs limpios.

---

## 5. Lo que V8 NO hace (por doctrina)

- No añade motores, patterns, combinations.
- No re-diseña validators que ya funcionan.
- No cambia jurisdicción US-only.
- No regenera AI_SCAFFOLDING_REGISTRY (sigue FROZEN 9 items).
- No procesa los 105 PDFs restantes.
- No añade dashboard QA visual.
- No introduce LLM en otro motor que no sea motor_019.
- No relaja epistemología.

V8 = ajuste fino final del cerebro V7. **Nada más.**

---

## 6. Lo que V8 PRESERVA (lista explícita del prompt)

Mantener exactamente:

- Reframing estratégico (área-as-denominator → operational intensity)
- Combination intelligence (benchmark + thermal envelope, dock cycles + duty, control boundary + CAPEX, charging + tariff)
- Peer logic (subtype, service model, dock density, intensity, charging profile, tariff, control boundary, thermal regime)
- Capital allocation risk (CAPEX vs primary driver)
- No-false-closure (no ROI, no savings, no bankability, no compliance closure, no peer superiority, no final redesign recommendation)

Si cualquier sub-fase V8 amenaza romper uno de estos → revert + replan.

---

## 7. Estrategia de mitigación de riesgo

Cada sub-fase tiene un test de "no rompe regression cross-asset 7/7" antes de commit. Si rompe → revert local, ajustar, retry.

Para P4 (TAD rewrite) y P3 (hybrid governance object) — los más invasivos — añadir un test específico que verifica que un caso cold_chain con `force_render=True` sigue produciendo PDF en `exploratory_prior_brief` mode (no escalada involuntaria a client_safe).
