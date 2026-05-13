# RECOVERY_DONE_V5 — Constitutional Realignment

**Período:** 2026-05-12 → 2026-05-13
**Status:** V5 P0 → V5 P6 entregados. P7/P8 parcial. Cascade S1-S9 abierto.

---

## Origen

V4 P2/P3 (commits `86f57aa` / `40ee9ae`) cableó un extractor LLM (Anthropic) DENTRO del Industrial Research Engine. Esto violaba la ley rectora de Phase 0:

> *"el LLM no es soberano. Solo puede participar como capa semántica gobernada para formulación, traducción, resumen y verificación semántica de material previamente acotado. No puede operar como motor analítico principal de la fase."*

El usuario detectó el desvío y solicitó reconciliar Arquitectura B (runtime, 64 motores en 6 capas A-F) con Arquitectura A (constitución, 8 fases canónicas de los Master Docs).

V5 Constitutional Realignment es esa reconciliación.

---

## Entregables

### V5 P0 — Cleanup (commit `ce2a898`)

**Eliminados (violaban Phase 0):**
- `industrial_research_engine/anthropic_llm_extractor.py`
- `industrial_research_engine/llm_extraction_interface.py`
- `industrial_research_engine/pdf_extraction_interface.py`
- `industrial_research_engine/pdfplumber_extractor.py`
- `industrial_research_engine/url_pdf_fetcher.py`
- `industrial_research_engine/extraction_orchestrator.py`
- `scripts/extract_from_pdf.py`
- `scripts/batch_extract_recursos.py`
- `tests/test_v4_phase2_pdf_llm.py`
- `tests/test_v4_phase3_url_retry.py`

**Refactorizados:**
- `industrial_research_engine/__init__.py` — exports limpios (schemas + write path únicamente, no extractor)
- `industrial_research_engine/engine.py` — añadido `propose_knowledge_from_manual_text()`; `extract_knowledge` redirige a zlab_skill como stub fail-loud
- `industrial_research_engine/routing.py` — `NotImplementedExtractor` redirige a zlab_skill
- `adapters/motor_065.py` — reporta path determinista vía zlab_skill, no `ExtractionOrchestrator`
- `scripts/extract_knowledge.py` — usa `propose_knowledge_from_manual_text` directo
- `tests/test_v4_phase1_extraction_infrastructure.py` — reescrito para test del manual path superviviente

### V5 P1 — phase_registry (commit `ce2a898`)

**Nuevo `phase_registry.py`** paralelo a `layer_registry.py`. Mapea cada uno de los 64 motores a:
- Phase 0-8 (constitucional, según Master Docs)
- O None para validators-crosscut / ML-extension / infra

APIs: `phase_of()`, `motors_in_phase()`, `phase_name()`, `canonical_unit_for_phase()`.

**16 tests de coherencia** garantizan que el set de motores en `phase_registry` == catálogo == `layer_registry`.

### V5 P2 — Canonical phase units (commit `23e61db`)

**Nuevo `phase_units.py`** con 6 proyecciones determinísticas que mapean los outputs internos de cada motor a las unidades epistemológicas canónicas mandadas por los Master Docs:

- `to_inference_case_register()` — Phase 2 §15 (6 atributos canónicos)
- `to_claim_upgrade_candidate_register()` — Phase 4 §5
- `to_financial_exposure_case_register()` — Phase 5 §4+§7 (ladder de 7 estados)
- `to_compliance_applicability_case_register()` — Phase 6 §4+§7 (ladder de 7 estados)
- `to_belief_revision_event_register()` — Phase 7 §4+§7 (9 campos por evento)
- `to_decision_admissibility_case_register()` — Phase 8 §4+§7 + las **8 action families canónicas** (`inspect/measure/classify/pilot/design/procure/implement/defer`) + `derive_defer_investigate_act_map()`

**6 motores patchados** (1 línea de import + 1 bloque de emisión cada uno):
- motor_014 → `inference_case_register_canonical`
- motor_034 → `claim_upgrade_candidate_register`
- motor_045 → `financial_exposure_case_register`
- motor_053 → `compliance_applicability_case_register`
- motor_054 → `belief_revision_event_register`
- motor_033 → `decision_admissibility_case_register` + `defer_investigate_act_map`

Cada row lleva markers `__phase__` y `__canonical_unit__`.

**20 tests** (16 unit + 4 integración motor↔phase_unit).

### V5 P3 — Deterministic bridge (commit `8153937`)

**Nuevo `industrial_research_engine/deterministic_bridge.py`** une `zlab_skill.local_pdf_autodraft` (extractor determinista existente) con `propose_knowledge`:
- `pattern_spec_to_knowledge_object(pattern_spec, source_id, ...)` — mapea registry pattern + provenance del extractor a KnowledgeObject canónico
- `propose_extracted_pattern(...)` — end-to-end bridge → propose_knowledge
- `load_pattern_spec(pattern_id)` — carga registry JSON

**Compatibilidad legacy asset_types** (S9 mitigación):
- `industrial_facility` → `manufacturing_facility`
- `large_commercial_building` → `commercial_building`
- `thermal_process_site` → `thermal_process_facility`
- `logistics_hub` → `logistics_terminal`
- `leased_asset`, `all_operational_assets` → drop (no son familias)

**Fallback de catalog**: cuando pattern asset_types es universal y resulta vacío después de normalizar, usa `source_by_id(source_id).asset_families`.

**Nueva CLI `scripts/extract_from_local_pdf.py`** (reemplaza la V4 P2 borrada):
- Single-PDF o batch-dir
- Manifest mapping pdf_filename → source_id
- Determinista, sin LLM
- Cae en `knowledge_pending/<kind>/` para `/revisar`

**Smoke test sobre 5 PDFs reales**: 22 candidates landed sin errores (DOE Goodyear, Ingersoll Rand, UPME Cementos, UPME Alimentos, CORPOEMA Calderas, Auditorías Edificios I).

**13 tests** del bridge.

### V5 P4 — Authority classifier (commit `4976a19`)

**Nuevo `industrial_research_engine/authority_classifier.py`**: clasifica fuentes en tier 1/2/3 determinísticamente por publisher token + type.

Audit del catálogo (192 entries):
- 152 aligned (79.2%)
- 35 promoted (catalog conservative, classifier higher) — ASHRAE Handbooks, DOE sourcebooks
- 5 demoted (catalog optimistic, classifier lower)

Las 40 divergencias son la señal de S6 scaffolding.

**14 tests** del classifier.

### V5 P5 — Canonical 6-type report maturity (commits `4f2c032`, `6f515a0`)

**Nuevo `report_maturity.py`**: implementa la familia canónica de 6 entregables (Phase 0 §10):

1. Integrated Preliminary Report (`unsupported / hypothesis / indication`)
2. Decision-Grade Report (`screening_grade / decision_grade`)
3. Hardened Decision Report (`partially_hardened`)
4. Validation-Oriented Report (`verification_ready`)
5. Verification-Supported Report (`verification_supported`)
6. Verified Report (`verified`)

APIs: `maturity_type_for_support_state()`, `aggregate_maturity_type()`, `derive_report_maturity_from_motor_025()`, `is_stronger_maturity()`.

**motor_025 wireado** para emitir `report_maturity_type` agregando sobre todos los `claim_support_state` registrados.

**27 tests** (25 unit + 2 motor_025 integration).

### V5 P6 — Wire maturity al render (commit `88edd37`)

**motor_017** ahora lee `motor_025.report_maturity_type` y lo emite en su return dict. El manifest del PDF lleva la maturity grade junto al recommended_report_type (topic). Las dos dimensiones son ortogonales y visibles en dashboard.

---

## Métricas V5

| Hito | Tests |
|---|---|
| V4 cierre (con deuda) | 1342 |
| V5 P0 cleanup (−45 tests LLM-extractor) | 1297 |
| V5 P1 phase_registry (+16) | 1313 |
| V5 P2 phase_units (+20) | 1333 |
| V5 P3 deterministic_bridge (+13) | 1346 |
| V5 P4 authority_classifier (+14) | 1360 |
| V5 P5 report_maturity (+25) | 1385 |
| V5 P5b motor_025 integration (+2) | 1387 |
| **V5 P6** | **1387** |

**Regression cross-asset 7/7 PASS** después de V5 P0+P1, V5 P2, V5 P3, V5 P4+P5, V5 P5b+P6.

---

## Lo que V5 NO cerró

- **V5 P7** Narrator hardening (cite-per-paragraph en motor_019 + orphan-claim validator)
- **Cascade S1-S9** del scaffolding registry (S6 audit existe pero sin aplicar; S4/S5 sin regenerar; S3 hybrids sin co-ocurrencia detection; S8/S9 sin cleanup)
- **Profundidad de las unidades canónicas**: las proyecciones cubren la superficie, pero motor_034/045/053/054/033 no construyen todos los campos canónicos (varios quedan vacíos o derivados)
- **Las 10 reglas autodraft faltantes** para los patterns cold-chain residentes (refrigeration_duty, defrost_profile, etc.)
- **Procesar los 110 PDFs de Recursos y cursos** en batch (sólo 5 smoke-tested)
- **motor_028 jurisdicciones no-US** (Colombia/España)

---

## Phase 0 anchor preservado

El LLM aparece en EXACTAMENTE UN motor (`motor_019` — narrador post-framework, bounded). Todo lo demás es determinista. La Industrial Research Engine es schema + write path, no extractor. La extracción real vive en `zlab_skill` con keyword rules y pdfplumber.

Ningún flujo del pipeline depende de Anthropic API. El framework corre 100% local-deterministic excepto el narrador (motor_019), que puede usar Codex CLI, Ollama local, o cualquier LLM porque su rol es "secretario que pasa a limpio", no analista.
