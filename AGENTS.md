# AGENTS.md — ZLab Operational Truth Framework

> Lee este archivo completo antes de ejecutar cualquier comando.
> Es la guía operativa actual del framework.

**Última actualización: 2026-05-13 (V5 Constitutional Realignment)**

---

## 0. Ancla constitucional NO NEGOCIABLE

El framework está gobernado por **8 fases canónicas** definidas en los Master Docs:

```
Phases/phase-0/docs/es/0_Documento_Maestro_Fase_0.md   ← Constitución
Phases/phase-1/docs/es/...                              ← Public Data + PIML
Phases/phase-2/docs/es/2_Documento_Maestro_Fase_2.md   ← Decision Core
Phases/phase-3/docs/es/3_Documento_Maestro_Fase_3.md   ← Reporting
Phases/phase-4/docs/es/4_Documento_Maestro_Fase_4.md   ← Verification Bridge
Phases/phase-5/docs/es/5_Documento_Maestro_Fase_5.md   ← Probabilistic Finance
Phases/phase-6/docs/es/6_Documento_Maestro_Fase_6.md   ← Computable Regulatory
Phases/phase-7/docs/es/7_Documento_Maestro_Fase_7.md   ← Cognitive / Belief Update
Phases/phase-8/docs/es/8_Documento_Maestro_Fase_8.md   ← TAD Final Decision
```

Si Phase 0 entra en conflicto con cualquier otra fase, **Phase 0 gobierna**.

**Ley rectora**: *"claridad financiera y decisional bajo incertidumbre física, sin delegar la verdad final al LLM ni permitir que la narrativa sustituya la evidencia."*

### Reglas inviolables (enforced en código, no en docs)

1. **El LLM NO es soberano.** Aparece en exactamente UN motor (`motor_019` — narrador, no analista). Cualquier otro uso de LLM en código analítico viola Phase 0.
2. **La extracción de PDFs es DETERMINISTA.** `runtime_orchestrator/zlab_skill/local_pdf_autodraft.py` + keyword rules. NO Anthropic / OpenAI / Ollama en el path analítico.
3. **AI NO autoría contenido.** `AI_SCAFFOLDING_REGISTRY.md` está FROZEN en 9 items. No añadir.
4. **AI NO aprueba combinations.** Solo el usuario en `/combinations` o `/revisar`.
5. **NUNCA escribir JSON a `combinations/` directo.** Usar `scripts/propose_combination.py`.
6. **NUNCA meter metadata de review en el PDF.** El PDF es deliverable final limpio. Review center = dashboard.
7. **NUNCA `git add -A`** con WIP del usuario sin consolidar.
8. **SIEMPRE responder en español al usuario.**
9. **SIEMPRE contrastar cambios contra los Master Docs de fase.**

---

## 1. Estado del proyecto

### Métricas (post V5 P6, 2026-05-13)

- **64 motores** en `governanza/automation-base/motor_dependencies.json`
- **runtime-orchestrator/** implementa los 64 con adapters
- **1387 tests passing** (`pytest tests/`)
- **Regression cross-asset 7/7 PASS** (6 representative cases + hybrid E2E)
- **192 fuentes industriales** en catálogo (`industrial_source_catalog.json`)
- **30 patterns** + **4 combinations approved** + **1 approved knowledge real** (`hydraulic_to_electric_injection_molding_loss`)

### Doble registro: cada motor está en DOS clasificaciones paralelas

| Registro | Eje | Archivo |
|---|---|---|
| **`layer_registry.py`** | Bus técnico A-F | A: Knowledge / B: Hypothesis / C: Claim Governor / D: TAD / E: Composer / F: Validation |
| **`phase_registry.py`** (V5) | Constitucional 0-8 | 0: Governance / 1: PIML / 2: Decision Core / 3: Reporting / 4: Verification / 5: Finance / 6: Regulatory / 7: Cognitive / 8: TAD |

APIs canónicas: `phase_of(motor_id)`, `motors_in_phase(phase_id)`, `PHASE_CANONICAL_UNIT`, `phase_name(phase_id)`.

### Unidades canónicas por fase (V5 P2)

| Fase | Unidad canónica | Motor productor | Emite |
|---|---|---|---|
| 1 | `facility_prior` (12 bundles) | motor_012 | `facility_prior` dict |
| 2 | `inference_case` (6 atributos) | motor_014 | `inference_case_register_canonical` |
| 3 | `output_block` + `report_package` | motor_015 + motor_016 | 9 block types + C1-C9+A1-A3 sections |
| 4 | `claim_upgrade_candidate` | motor_034 | `claim_upgrade_candidate_register` |
| 5 | `financial_exposure_case` | motor_045 | `financial_exposure_case_register` |
| 6 | `compliance_applicability_case` | motor_053 | `compliance_applicability_case_register` |
| 7 | `belief_revision_event` | motor_054 | `belief_revision_event_register` |
| 8 | `decision_admissibility_case` | motor_033 | `decision_admissibility_case_register` + `defer_investigate_act_map` |

Cada row lleva `__phase__` y `__canonical_unit__` para auditoría.

### Familia de 6 entregables (Phase 0 §10)

`report_maturity.py` clasifica el Report Package en 6 grados:

| Maturity grade | Se desbloquea cuando max claim_support_state ≥ |
|---|---|
| Integrated Preliminary Report | `unsupported / hypothesis / indication` |
| Decision-Grade Report | `screening_grade / decision_grade` |
| Hardened Decision Report | `partially_hardened` |
| Validation-Oriented Report | `verification_ready` |
| Verification-Supported Report | `verification_supported` |
| Verified Report | `verified` |

motor_025 emite `report_maturity_type`. motor_017 lo lleva al manifest del PDF.

---

## 2. Cómo correr el framework

### Pipeline E2E (caso real)

```bash
cd /Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator

# 1) Pipeline produce scenarios + BLOQUEA render hasta aprobación
unset ZLAB_AUTO_APPROVE_SCENARIOS
python3 cli.py run --pipeline-id <id> --inputs inputs/<case>.json --no-cache

# 2) Dashboard → http://localhost:7474/scenarios → approve/edit/reject
#    Cada scenario lleva trigger/source/process_clue/industrial_reason/asset_family_reason

# 3) Re-correr → ahora SÍ genera el PDF
python3 cli.py run --pipeline-id <id> --inputs inputs/<case>.json --no-cache

# Bypass para CI / regression
export ZLAB_AUTO_APPROVE_SCENARIOS=1
bash scripts/regression_cross_asset_recovery.sh
```

### Extractor determinista de PDFs locales (V5 P3)

```bash
# Single PDF
python3 scripts/extract_from_local_pdf.py \
  --pdf-path "/path/to/file.pdf" \
  --source-id <catalog_source_id> \
  --id-suffix v5p3_run1

# Batch + manifest
echo '{"file1.pdf":"source_id_1","file2.pdf":"source_id_2"}' > /tmp/manifest.json
python3 scripts/extract_from_local_pdf.py \
  --batch-dir /path/to/pdfs \
  --manifest /tmp/manifest.json \
  --id-suffix v5p3_batch \
  --out /tmp/batch_result.json
```

Los candidatos caen en `knowledge_pending/<kind>/`. Aprobar en **http://localhost:7474/revisar** (UI simple en español).

### Dashboard

```bash
python3 runtime-orchestrator/dashboard.py
# → http://localhost:7474
# Entrada principal: /revisar (V5)
# Otras: /scenarios, /combinations, /knowledge
```

App dock: `/Applications/ZLab Dashboard.app`

---

## 3. Fuente de verdad (orden estricto)

1. `Phases/phase-{N}/docs/es/` — **constitución, gobierna todo conflicto**
2. `runtime-orchestrator/` + suite de tests (1387 verde)
3. `runtime-orchestrator/src/runtime_orchestrator/phase_registry.py` — mapeo motor↔fase canónico
4. `runtime-orchestrator/src/runtime_orchestrator/phase_units.py` — proyecciones canónicas por fase
5. `governanza/automation-base/motor_dependencies.json` — catálogo de 64 motores
6. `AI_SCAFFOLDING_REGISTRY.md` — contenido Claude-autorado pendiente de regenerar (FROZEN en 9 items)

No usar el backlog dinámico para inferir estado actual.

---

## 4. Recovery history

- **V1 (2026-05-09)** — 6-layer arch + LayerBundle bus + motor_055-063. 938 tests.
- **V2 estructural (2026-05-10)** — Gaps A-F: motor_062 scenario validator, 139-source catalog, hybrids, source routing, cold-chain patterns, knowledge YAMLs. 970 tests.
- **V2-LIVE / V2-CRITICAL / Course correction (2026-05-10/11)** — dashboard review center, 5 scenario fields, hybrid E2E. 1107 tests.
- **V3 stabilization + V3 residual (2026-05-11/12)** — 11 items machinery. 1289 tests.
- **V4 P0/P1 (2026-05-12)** — Industrial Research Engine infrastructure (schemas, validators, taxonomy, family_scope, routing, memory, propose_knowledge). 1313 tests.
- **V4 P2/P3 (2026-05-12) — CERRADAS CON DEUDA**: cableé LLM-extractor Anthropic que VIOLABA Phase 0. Eliminado en V5 P0.
- **V5 Constitutional Realignment (2026-05-12/13)** — 6 sub-fases entregadas:
  - V5 P0+P1 — Cleanup + `phase_registry.py` (commit `ce2a898`)
  - V5 P2 — `phase_units.py` + 6 motores patchados (commit `23e61db`)
  - V5 P3 — `deterministic_bridge.py` + CLI `extract_from_local_pdf.py` (commit `8153937`)
  - V5 P4 — `authority_classifier.py` (commit `4976a19`)
  - V5 P5 — `report_maturity.py` (commit `4f2c032`)
  - V5 P5b — wire motor_025 (commit `6f515a0`)
  - V5 P6 — wire motor_017 manifest (commit `88edd37`)

Último commit: `88edd37` (recovery v5p6).

---

## 5. Pendiente — V5 P7, P8 + scaffolding registry

### V5 todavía abierto

- **V5 P7** Narrator hardening — cite-per-paragraph en motor_019 + validator de orphan claims
- **V5 P8** Docs final — RECOVERY_DONE_V5.md (parcialmente cubierto por este archivo)

### AI_SCAFFOLDING_REGISTRY cascade (S1-S9)

Orden de regeneración recomendado (lowest risk → highest):

1. **S6** — Catálogo de fuentes. `audit_catalog_against_classifier` detecta 40 divergencias. Decidir si aplicar.
2. **S5** — 4 knowledge YAMLs regenerados desde S6.
3. **S4** — 7 cold-chain patterns extraídos de IIAR/ASHRAE/Danfoss. Requiere PDFs autoritativos.
4. **S8** — tad_actions caen gratis cuando S4 se regenera.
5. **S3** — Hybrids emergentes por co-ocurrencia.
6. **S1 + S2** — Derivar de S4+S6+S3.
7. **S9** — Refactor per-family branches en `structural_intelligence/`.
8. **S7** — `combination_engine` propone, usuario aprueba.

### Profundidad de las unidades canónicas

V5 P2 cubre la superficie. Pendiente que cada motor **construya** todos los campos:

- Phase 4 — motor_034 computar `baseline_hardening_state`, `instrument_dependency`, `validity_domain`
- Phase 5 — motor_045 los 6 objetos operativos (`financial_assumption_register`, `tariff_basis_record`, etc.)
- Phase 6 — motor_053 los registers `trigger_field_register`, `threshold_register`, `exception_register`
- Phase 7 — motor_054 belief_revision events de eventos reales de evidencia (no synth de claim_contract)
- Phase 8 — motor_033 `irreversibility_profile`, `downside_profile`, `no_go_condition_register`

---

## 6. Mapeo motor → fase canónica (referencia rápida)

```
Phase 0 (Governance):  001 002 024 025 026
Phase 1 (PIML):        003 004 005 006 007 008 009 010 011 012
                       028 035 039 049 050 065
Phase 2 (Decision):    013 014 029 037 038 040 041 042 046 052
Phase 3 (Reporting):   015 016 017 018 019 027 047 048 060
Phase 4 (Verification): 021 022 034 043 044
Phase 5 (Finance):     045
Phase 6 (Regulatory):  053
Phase 7 (Cognitive):   020 054
Phase 8 (TAD):         033 051
Validators (crosscut): 036 055 056 057 058 059 061 062 063
ML extension:          030 031 032
Infra:                 023
```

---

## 7. Tests + regression rápido

```bash
cd runtime-orchestrator
python3 -m pytest tests/ -q                          # 1387 expected
bash scripts/regression_cross_asset_recovery.sh      # 7/7 expected (~10 min)
```
