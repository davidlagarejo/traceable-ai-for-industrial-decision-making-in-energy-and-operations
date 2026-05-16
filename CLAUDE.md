# CLAUDE.md — ZLab Operational Truth Framework

> **Ancla constitucional para sesiones de Claude trabajando en este repo.**
> Leer ENTERO antes de tocar código.

**Última actualización: 2026-05-16 (V10 P4 ARRANCANDO — Combination Proposer multi-strategy)**

---

## 0. Doctrina actual: V10 P4 — Multi-strategy Combination Proposer

V10 P0/P1/P2/P3 cerradas (industry corpus + regulatory layer + evidence wiring).

**V10 P4 ahora:** construir un **proponente determinístico de combinaciones**. Hoy solo hay 4 combinations aprobadas a mano. El framework debería generar muchas (60-150 por familia) a partir de:

- Co-ocurrencia en el corpus (sin LLM, cosine similarity)
- Co-mención en regulaciones (regex)
- **Predicados de contexto** — temporal/climático/regulatorio/comfort
- Compliance violations (decisión propuesta vs regulación aplicable)
- Comfort/safety windows (ASHRAE 55, OSHA 1910.1000, NFPA 70E)
- Investment trap detection (CapEx vs corpus alternatives + reg horizon)

**Phase 0 doctrine intact:**
- LLM sigue siendo solo narrador (motor_019)
- El proposer es 100% determinístico (regex + cosine + clustering)
- La hipótesis de cada combinación es **cita verbatim del corpus**, no parafraseada
- Curación humana = accept/reject/modify (gate de calidad), no creación

Detalle del plan completo: § 5 abajo.

---

## 1. Reglas inviolables (NUNCA romper)

### Reglas fundacionales (todas las versiones)

1. **El LLM aparece en EXACTAMENTE UN motor** (`motor_019` — narrador, no analista).
2. **Extracción de PDFs es DETERMINISTA** (`zlab_skill/local_pdf_autodraft.py`). No Anthropic/OpenAI/Ollama en el path analítico.
3. **AI NO autoría contenido.** `AI_SCAFFOLDING_REGISTRY.md` FROZEN en 9 items.
4. **AI NO inventa combinations.** El proposer V10 P4 genera candidates; humano aprueba en `/combinations`.
5. **NUNCA escribir JSON a `combinations/` directo.** Va a `combinations_pending/`, aprobación humana mueve a `combinations/`.
6. **NUNCA meter metadata de review en el PDF.** PDF = deliverable final limpio.
7. **NUNCA `git add -A`** con WIP del usuario sin consolidar.
8. **SIEMPRE responder en español al usuario.**
9. **SIEMPRE contrastar cambios contra los Master Docs** de fase. Phase 0 gobierna conflictos.
10. **Cada flip de defaults es hacia MÁS estricto, no menos.**
11. **No silent fallback.** Todo fallback registrado, clasificado, gobernado.
12. **No client-facing output con state ≠ client_safe** en hard mode.

### Reglas V10 (industry corpus + proposer)

13. **El corpus enriquece motors 012/019/033/054** vía `industry_corpus.evidence_wire`.
14. **Retriever determinístico.** Cosine similarity, numpy. Cero LLM en retriever.
15. **Solo se indexa lo aprobado.** `chunks_pending/` nunca llega al retriever.
16. **Narrator cita verbatim o no cita.** Regla 11 de motor_019 system prompt: copia entre comillas + `[source_id::chunk_id]`. Prohibido parafrasear.
17. **Feature flag `INDUSTRY_CORPUS_ENABLED=auto`** (default). Detecta automáticamente si hay índices construidos.
18. **El proposer genera, NO inventa.** Hipótesis = cita verbatim del corpus. Predicados = constantes de regulaciones (ASHRAE 55 dice 73-79°F, ese ES el predicado).

---

## 2. Ancla constitucional permanente

**8 fases canónicas** (`Phases/phase-0..8/docs/es/`):

| Fase | Unidad canónica | Motor productor |
|---|---|---|
| 0 | constitutional rules + 9-state ladder | motor_001/002/024/025/026 |
| 1 | `facility_prior` + `real_discovery_bundle` + `regulatory_applicability_bundle` | motor_012 + motor_028 |
| 2 | `inference_case` | motor_014 |
| 3 | `output_block` + `report_package` | motor_015/016/017/019 |
| 4 | `claim_upgrade_candidate` | motor_034 |
| 5 | `financial_exposure_case` | motor_045 |
| 6 | `compliance_applicability_case` | motor_053 |
| 7 | `belief_revision_event` + **combination activation + proposer (V10 P4)** | motor_054 |
| 8 | `decision_admissibility_case` (TAD) | motor_033 |

Phase 0 gobierna conflictos. **El LLM NO es soberano — sólo motor_019.**

---

## 3. Estado actual del corpus + regulatory (post-V10 P3)

- **64 motores** · **30 patterns** · **4 combinations approved** · **144 approved knowledge memories**
- **276 fuentes en industry_corpus** (DOE OSTI + EIA + NREL + PNNL + ORNL + LBNL + EU + NYC + Steamloc)
- **12,956 chunks aprobados** indexados (6 asset_families, 384-dim MiniLM)
- **15 CFR parts descargados** vía eCFR API
- **360 citas regulatorias** detectadas (112 únicas)
- **5 paths de auto-approve:** federal+system_verified, open_access+system_verified, vendor_whitepaper+allowlist, us_federal_regulation, public_domain_government

**Wires V10 P3 activos:**
- motor_012 → `facility_prior.regulatory_applicability_bundle` (Phase 1)
- motor_054 → cada combination decorated con `industry_evidence` (Phase 7)
- motor_033 → VoI bumped por corpus + regulatory signals (Phase 8)
- motor_019 → narrator cita verbatim `[source_id::chunk_id]` (Phase 3)

---

## 4. Doble registro motores

| Registro | Eje | API |
|---|---|---|
| `layer_registry.py` | Bus técnico A-F | A:Knowledge / B:Hypothesis / C:Claim Governor / D:TAD / E:Composer / F:Validators |
| `phase_registry.py` | Constitucional 0-8 | `phase_of(motor_id)`, `motors_in_phase(n)` |

---

## 5. V10 P4 — Combination Proposer multi-strategy (EN CURSO)

**Problema:** solo 4 combinations aprobadas a mano. Por caso típico activan 0-1. La diversidad analítica está bloqueada por un cuello de botella manual.

**Solución:** proposer determinístico que genera 60-150 candidates por familia. Curación humana = accept/reject/modify.

### 5.1 Arquitectura

```
runtime-orchestrator/src/runtime_orchestrator/combination_proposer/
├── __init__.py
├── proposer.py              # API pública: propose_combinations(asset_family, …)
├── strategy_corpus.py       # Strategy 1: co-occurrence en corpus (cosine)
├── strategy_regulatory.py   # Strategy 2: co-mention en regulations (regex)
├── strategy_context.py      # Strategy 3: pattern × context_predicate
├── strategy_compliance.py   # Strategy 4: decision vs regulation conflict
├── strategy_comfort.py      # Strategy 5: ASHRAE 55 / OSHA window
├── strategy_invest_trap.py  # Strategy 6: CapEx + reg horizon + alternatives
├── predicate_evaluator.py   # Evalúa predicados de contexto vs caso real
├── constraint_matrix.yaml   # Pattern × context_dimension (curada, manageable)
└── audit_log.py             # Auditoría completa de cada propuesta
```

### 5.2 Las 6 estrategias

| # | Estrategia | Cómo opera | Volumen por familia |
|---|---|---|---|
| 1 | corpus_cooccurrence | Pairs/triples de patterns activos → query combinado al corpus → si sim_combined > max(sim_individual)+0.10 → candidate | 20-30 |
| 2 | regulatory_comention | Para cada reg downloaded, extraer qué patterns menciona; ≥2 patterns → candidate | 15-25 |
| 3 | constraint_x_pattern | Matriz `pattern → context_dimension` (mes, clima, ocupación) → cuando caso matchea → candidate con predicado activo | 30-50 |
| 4 | compliance_violation | Decisión propuesta vs cada reg aplicable; conflict → candidate con `decision_implication=block` | 10-20 |
| 5 | comfort_safety_window | ASHRAE 55, OSHA, NFPA 70E definen ventanas → decisión fuera de ventana → `defer_window` | 5-15 |
| 6 | investment_trap | CapEx + corpus muestra alternativa con payback corto, O reg horizon <24mo, O obsolescencia ASHRAE → `investigate_first` | 10-20 |
| **Total pool** | | | **90-160** |

### 5.3 Shape de cada candidate

```yaml
id: hvac_replacement_summer_peak_violation
proposal_method: comfort_safety_window
generated_at: 2026-05-16T10:00:00Z
generated_by: framework_auto
confidence_score: 0.87
status: pending_human_review

pattern_set:
  - hvac_aging_high_load
  - summer_peak_occupancy_critical
  - comfort_setpoint_safety_margin_thin

context_predicates:
  all:
    - {field: current_month, op: in, value: [6, 7, 8]}
    - {field: climate_zone, op: in, value: [2A, 2B, 3A, 3B]}
    - {field: occupancy_density, op: ge, value: 0.6}

evidence:
  corpus_citations:
    - chunk_id: "ashrae_55::chunk_0014"
      verbatim: "Operative temperature ranges to maintain occupant comfort: 73-79°F (summer)"
      similarity: 0.78
    - chunk_id: "doe_better_buildings::chunk_0042"
      verbatim: "HVAC replacement during peak cooling season can result in indoor temperatures exceeding 90°F"
      similarity: 0.71
  regulatory_basis:
    - citation: "ashrae 55"
      title: "Thermal Environmental Conditions for Human Occupancy"
    - citation: "29 cfr 1910.1000"
      title: "OSHA — air contaminants / heat exposure"

combined_hypothesis: |
  "Operative temperature ranges to maintain occupant comfort: 73-79°F (summer)"
  [ashrae_55::chunk_0014]

decision_implication:
  action: DEFER_TO_WINDOW
  allowed_windows: [Sep, Oct, Nov, Mar, Apr, May]
  alternative: provide_temporary_cooling_capacity_ge_design_load

consequence_if_ignored:
  - occupant heat stress events
  - ASHRAE 55 violation in operating logs
  - potential OSHA citation
```

### 5.4 Predicate evaluator

Lee el caso real (motor_012.facility_prior, motor_028.real_discovery_bundle, current_date) y evalúa `context_predicates`. Solo activan las combinations cuyos predicados matchean.

**Esto es lo que vuelve "muchas y específicas":** misma combinación se activa o no según el caso. HVAC en julio + zona 2A → activa. HVAC en octubre + zona 5A → no.

### 5.5 TAD priority remap (Phase 8)

motor_033 lee `decision_implication` de cada combination activada:

| `decision_implication.action` | Efecto en TAD |
|---|---|
| `BLOCK_COMPLIANCE` | priority=URGENT, posture=no_go, blocking=true |
| `DEFER_TO_WINDOW` | priority=normal, posture=`defer_until_${window}` |
| `INVESTIGATE_FIRST` | priority=high, posture=`evidence_blocker` |
| `ALTERNATIVE_VIABLE` | priority=high, posture=`reconsider_design` |
| `URGENT_COMPLIANCE` | priority=URGENT, posture=`act_now`, deadline embedded |

### 5.6 Plan de sub-fases V10 P4

| # | Trabajo | Días |
|---|---|---|
| F1 | Esqueleto `combination_proposer/` + Strategy 1 (corpus_cooccurrence) + audit log + output a `combinations_pending/` | 1 |
| F2 | Strategy 2 (regulatory_comention) | 0.5 |
| F3 | Strategy 3 (constraint × pattern matrix) + constraint_matrix.yaml curada | 1 |
| F4 | Strategy 4 (compliance_violation) | 0.5 |
| F5 | Strategy 5 (comfort_safety_window) | 0.5 |
| F6 | Strategy 6 (investment_trap) | 0.5 |
| F7 | Predicate evaluator + wire en motor_054 | 0.5 |
| F8 | Decision implications → motor_033 TAD | 0.5 |
| F9 | UI `/combinations` enriquecida (3-col layout con evidence) | 1 |
| F10 | Tests + Phase 0 enforcement | 0.5 |
| **Total** | | **6 días** |

### 5.7 Phase 0 inscribed (en docstring del proposer)

> Esta es generación determinística. La hipótesis viene del corpus verbatim,
> nunca de un LLM. Los predicados vienen de regulaciones literal. El humano
> aprueba/rechaza/modifica, NO inventa desde cero. Phase 0: el LLM sigue
> siendo solo narrador (motor_019).

---

## 6. Cómo correr el framework

```bash
cd runtime-orchestrator
python3 cli.py run --pipeline-id <id> --inputs inputs/<case>.json --no-cache

# Dashboard del Dock → abre /curar (V10 P3)
# URL directa:           http://localhost:7474/curar
# Curación corpus:       http://localhost:7474/corpus_curar
# Curación combinations: http://localhost:7474/combinations  ← V10 P4 aquí
# Regression:            bash scripts/regression_cross_asset_recovery.sh
```

**Hard mode default ON.** Opt-out:
```bash
export ZLAB_VALIDATORS_HARD_BLOCK=0
export ZLAB_RENDER_STRICT_DEFAULT=0
```

---

## 7. Fuente de verdad (orden estricto)

1. `Phases/phase-{N}/docs/es/` — constitución
2. `CLAUDE.md` (este archivo) — doctrina operativa actual
3. `RECOVERY_DONE_V*.md` — cierres versionados (V5-V9)
4. `AGENTS.md` — guía operativa subordinada
5. `runtime-orchestrator/` + suite de tests
6. `phase_registry.py` + `phase_units.py`
7. `AI_SCAFFOLDING_REGISTRY.md` (FROZEN en 9 items)

---

## 8. Layout del corpus + regulatory

```
runtime-orchestrator/
├── industry_corpus/
│   ├── sources/<asset_family>/*.yaml          # 276 manifests
│   ├── chunks_approved/<sha>/chunk_NNNN.json  # 12,956 chunks
│   ├── chunks_pending/<sha>/                  # human gate
│   ├── chunks_rejected/<sha>/                 # auditoría
│   ├── index/<asset_family>/vectors.npy       # 6 índices
│   ├── raw_pdfs/ extracted_text/ embeddings/  # gitignored
│   └── sources_quarantine/                    # URLs 404 con audit
│
└── regulatory_corpus/
    ├── regulations/us_federal/*.yaml          # 15 CFR parts
    ├── applicability/<asset_family>.json      # auto-derivado
    └── citations_extracted/*.json             # mapping
```

```
runtime-orchestrator/src/runtime_orchestrator/industry_corpus/
├── manifest.py                                # CorpusSource/Chunk + auto-approve gate
├── chunker.py                                 # page-aware splitter determinístico
├── embedder.py                                # MiniLM 384-dim
├── indexer.py                                 # build per-family vectors.npy
├── retriever.py                               # API pública: retrieve()
├── etl.py                                     # ingest_source(yaml)
├── licensed_etl.py                            # IEEE/Springer/Scopus (paywall)
├── local_ingestor.py                          # PDFs desde disco
├── evidence_wire.py                           # API unificada motors 012/054/033/019
├── regulatory/
│   ├── citation_extractor.py
│   ├── ecfr_fetcher.py
│   ├── state_international_fetcher.py
│   └── applicability_mapper.py
└── discovery/
    ├── orchestrator.py
    ├── osti_discoverer.py
    ├── arxiv_discoverer.py
    ├── licensed_journal_discoverer.py
    ├── openalex_citation_resolver.py
    └── vendor_whitepaper_crawler.py

(V10 P4 añade:)
└── combination_proposer/
    ├── proposer.py
    ├── strategy_corpus.py
    ├── strategy_regulatory.py
    ├── strategy_context.py
    ├── strategy_compliance.py
    ├── strategy_comfort.py
    ├── strategy_invest_trap.py
    ├── predicate_evaluator.py
    ├── constraint_matrix.yaml
    └── audit_log.py
```

---

## 9. Lo que CLAUDE.md NO contiene (intencional)

- Detalle de V5/V6/V7/V8/V9 — está en `RECOVERY_DONE_V*.md` correspondiente
- Detalle de catálogo de patterns — está en `zlab_skill/registry/patterns/`
- Detalle de fuentes corpus individuales — está en `industry_corpus/sources/`

CLAUDE.md mantiene SOLO la doctrina operativa activa.
