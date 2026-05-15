# CLAUDE.md — ZLab Operational Truth Framework

> **Ancla constitucional para sesiones de Claude trabajando en este repo.**
> Leer ENTERO antes de tocar código.

**Última actualización: 2026-05-15 (V10 P0 ARRANCANDO — Industry Corpus / RAG additivo, no rompe V9)**

---

## 0. Doctrina actual: V9 — FINAL ARCHITECTURAL CLOSURE (cerrado)

V9 cerrado. Ver `RECOVERY_DONE_V9.md` para el cierre completo.

Resumen:
- **1846 tests passing** (+40 vs V8 baseline 1806).
- **Regression cross-asset 7/7** verde bajo V9 hard mode default ON.
- 6 commits V9 (P0..P5).
- 3 mecanismos arquitectónicos finales del prompt Chief Systems Architect cerrados:
  1. **Fair Comparison Engine 10-dim** (§ 4) — `fair_comparison.py` + R14 blocking.
  2. **Chart artifact safety** (§ 9) — CV7 (section_id) + CV8 (hypothesis_supported).
  3. **Industry Onboarding Workflow** (§ 12) — `industry_onboarding.py` checklist 10-req.

**El cerebro V9 es 100% client-ready arquitectónico.**
Industry breadth + fetcher breadth = V10 (trabajo de contenido).

---

## 0.bis V8 — Final Release Hardening (referencia)

V8 cerrado en HEAD `b184b8a`. Ver `RECOVERY_DONE_V8.md`.

Resumen:
- **1806 tests passing** (+85 desde V7 baseline 1650 → ahora 1721).
- **Regression cross-asset 7/7** verde bajo V8 hard mode default ON.
- 11 commits V8 (P0..P10).
- 8 gaps residuales del prompt Chief QA Architect cerrados:
  1. `template_contamination_failure` ahora hard block en render_gate.
  2. CV6 chart `source_case_id` provenance.
  3. Hybrid Governance Object completo (10 campos).
  4. TAD Claim Sync rewrite (`DO_NOT_MODEL_YET` enforcement).
  5. Evidence Branching Engine per-hypothesis matrix.
  6. Source Authority Tier classification.
  7. Section-level Fallback Governance (high-value sections).
  8. Final Delivery Gate YAML block en motor_017 output.

**V8 lleva el framework de ~85-90% post-V7 a 98-99% client-deliverable.**
No reinventó, no añadió inteligencia, no añadió motores. Sólo cerró los 8 gaps con extensiones quirúrgicas.

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
- **1846 tests passing** · regression cross-asset **7/7 PASS bajo V9 hard mode default ON**
- **60 commits V5-V9** en `main` local (V9 P5 pendiente de push)
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

**V6 blocking set V9 = 23 reglas**: R1/R2/R4 + R8-**R14** (motor_059, 11), AF1/AF2 (motor_061), GN1 (motor_057), RU2/RU6 (motor_058), SJ1/SJ2/SJ3 (motor_062), CV1/CV3/CV5/CV6/**CV7**/**CV8** (motor_063, 6). V9 adds: R14 peer_ranking_with_incomplete_comparability + CV7 chart_without_section_id + CV8 chart_without_hypothesis_supported.

**Módulos V9 nuevos**: `fair_comparison.py` (P1 — 10-dim peer comparability), `industry_onboarding.py` (P3 — checklist 10-req scalability).
**Módulos V8 nuevos / extendidos**: `tad_claim_sync.py` (P4), `evidence_branching.py` (P5), `hybrid_justification.build_hybrid_governance_object` (P3), `source_execution_auditor.SourceAuthorityTier` (P6), `fallback_policy.HIGH_VALUE_SECTIONS` (P7), `render_gate.as_yaml_block` + `publication_mode` (P8).

---

## 5. V9 — 6 sub-fases (entregadas)

Detalle completo en `RECOVERY_DONE_V9.md`.

| # | Trabajo | Status |
|---|---|---|
| P0 | Baseline + plan anchor                                | ✅ |
| P1 | Fair Comparison Engine 10-dim + R14 blocking          | ✅ |
| P2 | Chart CV7 (section_id) + CV8 (hypothesis_supported)   | ✅ |
| P3 | Industry Onboarding Workflow                          | ✅ |
| P4 | Final Architectural Stability Suite (4 + control)     | ✅ |
| P5 | Docs + final regression + push                        | ⏳ |

### V8 (entregado) — referencia rápida

Detalle completo en `RECOVERY_DONE_V8.md`. 11 sub-fases:
template_contamination hard block, CV6 chart provenance, hybrid governance
object completo, TAD claim sync rewrite, evidence branching engine, source
authority tier, section-level fallback, Final Delivery Gate YAML, stability
suite 8 escenarios.

### V7 + V6 (entregados) — referencia rápida

- V7 (`RECOVERY_DONE_V7.md`): hard mode defaults ON, 4 combos migradas, 6 patterns con anti_asset_types, hybrid narrative emitter, R12/R13 (motor_059), RU6 (motor_058), CV5 (motor_063), stability suite client_safe e2e.
- V6 (`RECOVERY_DONE_V6.md`): 8 módulos governance creados y cableados, render_gate strict default, 14 V6 blocking rules.

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
3. `RECOVERY_DONE_V9.md` · `RECOVERY_DONE_V8.md` · `RECOVERY_DONE_V7.md` · `RECOVERY_DONE_V6.md` · `RECOVERY_DONE_V5.md` — cierres
5. `AGENTS.md` — guía operativa (subordinado a CLAUDE.md)
6. `runtime-orchestrator/` + suite de tests
7. `phase_registry.py` + `phase_units.py` (V5)
8. `AI_SCAFFOLDING_REGISTRY.md` (FROZEN en 9 items)
9. `docs/history/` — backlogs y planes antiguos archivados (V2-V7)

---

## 7.bis V10 P0 — Industry Corpus / RAG (EN CURSO, 2026-05-15)

**Decisión arquitectónica:** se construye un **industry corpus RAG** para enriquecer la narrativa de motor_019 con citas verbatim de fuentes públicas. **NO toca la cadena de decisión** (motors 001-018, 020-064). 100% additivo, behind feature flag `INDUSTRY_CORPUS_ENABLED=false` por defecto.

### Reglas inviolables de V10 P0 (additivas a las V8)

10. **El corpus solo enriquece motor_019.** Ningún otro motor importa `industry_corpus.retriever`. Si lo hacés, violás Phase 0.
11. **Retriever es determinístico.** Cosine similarity sobre numpy flat index. Cero llamadas LLM en el retriever.
12. **Solo se indexa lo aprobado.** `chunks_pending/` nunca llega al retriever. `chunks_approved/` sí. Auto-approve permitido solo para fuentes con `license=public_domain` Y `added_by=system_verified` (DOE, EPA, EIA, NREL, PNNL).
13. **Narrator cita verbatim o no cita.** Regla 11 del system prompt motor_019: si usa un industry fact, copia el texto entre comillas y cita `[source_id::chunk_id]`. Prohibido parafrasear.
14. **Feature flag por defecto OFF.** `INDUSTRY_CORPUS_ENABLED=false` → output de motor_019 BIT-IDENTICAL a V9. Test de no-regresión obligatorio.
15. **Corpus separado de knowledge_memory.** `industry_corpus/` ≠ `knowledge_pending/knowledge_approved/`. El primero es *material de referencia* citable, el segundo son *reglas de decisión* validadas.

### Arquitectura V10 P0

```
runtime-orchestrator/
├── industry_corpus/                          # datos
│   ├── sources/<asset_family>/*.yaml         # manifests de fuentes
│   ├── raw_pdfs/<sha>.pdf                    # binarios (reutiliza pdf_url_fetcher)
│   ├── extracted_text/<sha>.txt              # pdfplumber output
│   ├── chunks_pending/<sha>/chunk_NNNN.json  # ← gate humano
│   ├── chunks_approved/<sha>/chunk_NNNN.json # único leído por retriever
│   ├── chunks_rejected/<sha>/                # auditoría
│   ├── embeddings/<sha>/<chunk_id>.npy       # float32[384]
│   └── index/<asset_family>/                 # vectors.npy + manifest.json
└── src/runtime_orchestrator/industry_corpus/  # código
    ├── manifest.py    # CorpusSource, CorpusChunk dataclasses
    ├── etl.py         # ingest_source(yaml) — descarga + extrae + chunkea
    ├── chunker.py     # split() determinista, page-aware, 512 tok / 50 overlap
    ├── embedder.py    # MiniLM 384-dim (sentence-transformers, CPU)
    ├── indexer.py     # build_index(asset_family) → vectors.npy
    └── retriever.py   # retrieve(query, asset_family, k) — única API pública
```

### Dependencias V10 P0 (nuevas, opcionales)

`requirements-corpus.txt`:
- `sentence-transformers>=2.6` (arrastra `torch` ~800 MB)
- `numpy>=1.24`
- `tiktoken>=0.6` (opcional — token counting determinístico)

Si no están instaladas → `_CORPUS_AVAILABLE=False` → motor_019 funciona igual que V9. Sin regresión.

### Plan de 6 fases

| Fase | Días | Entregable |
|---|---|---|
| F1 | 1 | Esqueleto + ETL (`etl.py`, `chunker.py`, `manifest.py`) |
| F2 | 1 | Embeddings + index (`embedder.py`, `indexer.py`) |
| F3 | 0.5 | Retriever (`retriever.py`) + tests de determinismo |
| F4 | 0.5 | Curación: CLI bulk + auto-approve federal whitelist + dashboard `/corpus_curar` |
| F5 | 0.5 | Wire motor_019 detrás de flag + no-regression test |
| F6 | 0.5 | Seed corpus (50+ fuentes federales) + index build inicial |

**Total: ~4 días.** Cero cambios en motors fuera de motor_019.

### Confirmaciones del usuario (2026-05-15)

1. Acepta dependencia `sentence-transformers + torch` (~1 GB). ✓
2. Seed mínimo: 50 fuentes. ✓
3. Auto-approve para fuentes federales (DOE/EPA/EIA/NREL/PNNL), curación manual para todo lo demás (IIAR, Wikipedia, corporate sites). ✓

---

## 8. Pendiente post-V9 (V10 candidato — trabajo de CONTENIDO, no framework)

V9 cierra los 3 mecanismos arquitectónicos finales del prompt Chief Systems Architect. V10 (si llega) sería trabajo de catálogo:

- **Industry breadth** (§ 1, § 12): autoría/extracción de patterns para pharma, district energy, utilities, thermal process. V9 `validate_industry_readiness` es el gate.
- **Source fetcher breadth** (§ 6): implementar fetchers para IIAR, ISA, IEEE, MEASUR, VERIFI, DOE Better Plants, DOE AMO, manufacturer docs.
- **Phase 7 depth**: motor_054 belief_revision_event desde eventos reales (única fase canónica superficial).
- **Cascade S1-S9**: regenerar AI_SCAFFOLDING_REGISTRY items desde extractor determinista + 143 approved knowledge.
- **Procesar 105 PDFs restantes** de la library.
- **Dashboard QA visual** (QAScoreCard + RenderGateVerdict en `/revisar`).
- **CI smoke hard-mode job**.

---

## 9. Lo que V9 NO hace (por doctrina)

- No añade industrias reales (V10).
- No añade fetchers IIAR / ISA / IEEE / etc (V10).
- No añade LLM en otro motor que no sea motor_019.
- No regenera AI_SCAFFOLDING_REGISTRY.
- No procesa los 105 PDFs restantes.
- No expone dashboard QA visual.

**V9 = cierre arquitectónico final. El cerebro es 100% client-ready arquitectónicamente. Trabajo de contenido (V10) si llega.**
