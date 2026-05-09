# WIP Analysis — qué hay sin commitear y cómo agruparlo

> Análisis no-destructivo del working tree al 2026-05-08, hecho por Claude para ayudarte a
> escribir commits honestos. **No se modificó código fuente** durante este análisis — solo
> lectura.
>
> Si no estás de acuerdo con un agrupamiento, ignora este doc. Es un mapa, no una orden.

---

## 1. Volumen total

```
55 archivos modificados   +20,594 −2,146 LOC
48 entradas untracked    (≈30+ archivos fuente nuevos + outputs/docs)
```

Mi convención de mensaje propuesta sigue tu estilo histórico (`framework: <verb> <object>`,
`Add <thing>`, etc.). Si prefieres otra, ajusta los títulos pero respeta el agrupamiento.

---

## 2. Cinco ejes detectados

| Eje | Naturaleza | Tamaño aproximado |
|---|---|---|
| **A. zlab_skill autonomous research loop** | Funcionalidad nueva (módulo + dashboard + tests + scripts + yaml configs + docs gobernanza) | ~13,000 LOC |
| **B. congruence_intelligence refactor** | Refactor del módulo + adapters consumidores + tests | ~3,000 LOC |
| **C. Composer touchups** | Cambios en `executive_thesis.py`, `report_compression.py`, `render_section_contract.py` | ~1,000 LOC |
| **D. Compliance auditor outputs** | Regeneración de outputs (no source) | ~30 LOC |
| **E. Misc** | `apply_adjustments.py`, `apply_en_adjustments.py`, `Recursos genericos/`, `wiki-front-vault/` | desconocido |

Eje A y Eje B son **temáticamente independientes**. Eje C **toca** parte de Eje B y por eso
debe ir junto o después de B. Eje D es output, debería ir solo. Eje E necesita decisión tuya
(ver §5).

---

## 3. Plan de commits propuesto (orden importa)

### Commit 1 — **`feat(zlab_skill): autonomous research loop infrastructure`**

**Scope**: el módulo nuevo + sus tests + scripts CLI + yaml de configuración + integración
en dashboard.

**Archivos** (untracked):
- `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/` (35 archivos: research_campaign, knowledge_atom_store, combination_engine, licensed_acquisition, provider_sessions, etc.)
- `runtime-orchestrator/zlab_skill/` (3 yaml: asset_archetypes, culture_execution_proxies, fair_comparison_rules)
- `runtime-orchestrator/scripts/bootstrap_licensed_provider_session.py`
- `runtime-orchestrator/scripts/import_licensed_discovery_export.py`
- `runtime-orchestrator/scripts/import_scopus_discovery_export.py`
- `runtime-orchestrator/scripts/ingest_local_licensed_artifacts.py`
- `runtime-orchestrator/scripts/scaffold_local_licensed_artifacts.py`
- `runtime-orchestrator/tests/test_zlab_skill_*.py` (15 tests)
- `runtime-orchestrator/tests/test_autonomous_research_loop_acceptance.py`
- `runtime-orchestrator/tests/test_manufacturing_operational_intelligence_acceptance.py`
- `runtime-orchestrator/tests/test_operational_intelligence_*.py` (3 tests)

**Archivos** (modified):
- `runtime-orchestrator/dashboard.py` (+11,419 LOC; todo es integración con `zlab_skill`: importa 30+ funciones del módulo y registra ~26 directorios `_*_DIR` para persistir el research-loop state)

**Mensaje propuesto**:
```
feat(zlab_skill): autonomous research loop infrastructure

Add the zlab_skill module (35 files) implementing the autonomous research
loop: research campaigns, combination engine, knowledge atom store,
licensed acquisition with Playwright, provider session handoffs, scopus
discovery queue, and registry-staged candidate flow.

Dashboard integrates the loop with 26 new run-registry directories
(combination-decisions, research-loop-state, knowledge-atom-refresh,
licensed-discovery-queues, etc.) and surfaces the loop state via the
existing Flask UI.

Adds CLI scripts for bootstrapping licensed provider sessions and
importing discovery exports. Configuration in YAML (asset_archetypes,
culture_execution_proxies, fair_comparison_rules).

Test coverage: 18 new test files across module units, autonomous loop
acceptance, and operational intelligence dashboard contracts.
```

> **Nota**: si prefieres separar dashboard de zlab_skill, el commit se vuelve dos: primero
> el módulo + tests + scripts + yaml; segundo el dashboard wiring. Mismo total, mejor para
> revisar diffs grandes.

---

### Commit 2 — **`feat(governance): autonomous research loop documentation`**

**Scope**: docs de gobernanza nuevos (untracked) que describen el research loop a nivel
formal.

**Archivos** (untracked):
- `governanza/automation-base/autonomous_research_loop_execution_backlog_latest.md`
- `governanza/automation-base/autonomous_research_loop_master_plan_latest.md`
- `governanza/automation-base/latent_combination_research_expansion_plan_latest.md`
- `governanza/automation-base/operational_intelligence_skill_execution_backlog_latest.md`
- `governanza/automation-base/operational_intelligence_skill_phase_closure_latest.md`
- `governanza/automation-base/operational_intelligence_skill_reentry_boundary_latest.md`
- `governanza/automation-base/report_98_readiness_closure_plan_latest.md`
- `governanza/automation-base/research_brain_100_percent_completion_backlog_latest.md`
- `governanza/automation-base/research_brain_100_percent_completion_plan_latest.md`
- `governanza/automation-base/research_brain_100_percent_completion_review_latest.md`
- `governanza/automation-base/strategic_regression_audit_conditional_archetypal_intelligence_latest.md`

**Mensaje propuesto**:
```
docs(governance): autonomous research loop authority documents

Add 11 governance documents formalizing the autonomous research loop:
master plan, execution backlogs, phase closures, reentry boundaries,
and a strategic regression audit on conditional archetypal intelligence.

These are authority documents under governanza/automation-base/ and
follow the *_latest.md naming convention for reentry-stable references.
```

---

### Commit 3 — **`refactor(congruence_intelligence): expand 4-state epistemic model`**

**Scope**: el refactor del módulo `congruence_intelligence/` + los 14 adapters que lo
consumen, junto con sus tests.

**Archivos** (modified):
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/claim_governor.py` (+3 LOC; introduce `WEAK_SIGNAL` y `ARCHETYPAL_PRIOR` en el conjunto de `permission="allowed"`)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/congruence_engine.py` (+145 LOC)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/fair_comparison.py` (+10)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/finance_to_physics.py` (+20)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/gold_nuggets.py` (+140)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/loss_patterns.py` (+14)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/operational_logic.py` (+41)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/peer_normalization.py` (+18)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/process_mapping.py` (+28)
- `runtime-orchestrator/src/runtime_orchestrator/congruence_intelligence/strategic_tad.py` (+104)
- `runtime-orchestrator/src/runtime_orchestrator/structural_intelligence/competitive_comparison.py` (+286)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py` (+370 LOC; chart engine)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py` (+8)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py` (+95)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py` (+25)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py` (+44; era stub, ahora real)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py` (+30; era stub, ahora real)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py` (+204; ahora emite `congruence_claim_contract_register`)

**Tests** (modified + nuevos):
- `tests/test_congruence_chart_generation.py` (+136, nuevo)
- `tests/test_congruence_gold_nuggets.py` (+90, nuevo)
- `tests/test_congruence_report_compression.py` (+68, nuevo)
- `tests/test_evidence_maturity_wiring.py` (+46, nuevo)
- `tests/test_executive_thesis_congruence_bridge.py` (+40)
- `tests/test_expanded_strategic_tad_engine.py` (+13)
- `tests/test_finance_to_physics_translation.py` (+14)
- `tests/test_financial_exposure_type_engine.py` (+10)
- `tests/test_gold_nugget_generator.py` (+28)
- `tests/test_loss_pattern_activator.py` (+52, nuevo)
- `tests/test_structural_intelligence_benchmarking_and_competition.py` (+48)
- `tests/test_system_consistency_validator.py` (+69)
- `tests/test_system_consistency_validator_congruence.py` (+13)
- `tests/test_target_seed_workflow.py` (+10)
- `tests/test_warehouse_dynamic_congruence_acceptance.py` (+2)
- `tests/test_structural_correlation_graph_engine.py` (+12)
- `tests/test_asset_operational_logic_engine.py` (+10)

**Mensaje propuesto**:
```
refactor(congruence_intelligence): four-state epistemic model + producer wiring

Expand the claim governor from a binary OBSERVED/CONDITIONAL model to a
four-state epistemic vocabulary: OBSERVED_FACT, CONDITIONAL_HYPOTHESIS,
WEAK_SIGNAL, ARCHETYPAL_PRIOR. Each claim contract carries allowed_use,
prohibited_use, and falsification_condition.

Producers updated:
- motor_054 emits congruence_claim_contract_register from claim_governor
- motor_052 / motor_053 graduated from stubs to real adapters
  (loss_patterns, regulatory_physics, finance_to_physics)
- motor_018 (chart engine) +370 LOC of congruence-aware visualizations
- motor_047 / motor_048 (composer chain) consume new gold-nugget paths
- structural_intelligence/competitive_comparison expanded for archetypal-
  allowed peer comparison

Test coverage: 4 new test files, 13 updated. Total +1,663 LOC of tests.

Note: composer (motor_015/016/017 + executive_thesis) does NOT yet
consume congruence_claim_contract_register. That wiring is tracked
separately in RECOVERY_BACKLOG.md (R-W01..R-W05).
```

> **Decisión a tomar**: ¿quieres separar este commit en dos — uno para el refactor del
> módulo, otro para los adapters? El criterio honesto: si el refactor del módulo es
> consumible sin los adapters (los tests pasan en aislado), separar. Si están acoplados
> (los tests fallarían), un solo commit.

---

### Commit 4 — **`refactor(composer): incremental updates to executive_thesis and compression`**

**Scope**: cambios al composer que **no** completan el wiring (eso queda como work pendiente
R-W01..R-W05) pero sí ajustan funciones existentes.

**Archivos** (modified):
- `runtime-orchestrator/src/runtime_orchestrator/executive_thesis.py` (+947 LOC)
- `runtime-orchestrator/src/runtime_orchestrator/render_section_contract.py` (−4 LOC)
- `runtime-orchestrator/src/runtime_orchestrator/report_compression.py` (+24 LOC)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py` (+29 LOC; LaTeX rendering)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py` (+58 LOC; governance event)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py` (+42 LOC; artifact export)
- `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py` (+2,748 LOC; report package assembly)

**Tests** (modified):
- `tests/test_executive_thesis_report_hierarchy.py` (+666)
- `tests/test_report_conformance.py` (+573)

**Mensaje propuesto**:
```
refactor(composer): incremental support for ARCHETYPAL_PRIOR and bounded claims

Extend executive_thesis with confidence-level mapping for ARCHETYPAL_PRIOR
and INADMISSIBLE_CLAIM (executive_thesis.py:1048). Update report package
assembly (motor_016) and LaTeX rendering (motor_017) to carry the
expanded claim metadata. Adjust artifact export and governance-event
adapters accordingly.

Composer is not yet fully wired to congruence_claim_contract_register;
follow-up tracked in RECOVERY_BACKLOG.md (R-W01..R-W05).
```

> **Sospecha a verificar antes de commitear**: `motor_016.py +2,748 LOC` es muy grande
> para un solo refactor incremental. Posiblemente este archivo merece un commit separado.
> Si tienes contexto, separa.

---

### Commit 5 — **`chore(auditor): regenerate compliance outputs`**

**Scope**: outputs regenerados del compliance auditor — no es source code, es output.

**Archivos** (modified):
- `framework_compliance_auditor/outputs/audit_compiled_pdf_with_references_20260418/audit_manifest.json`
- `framework_compliance_auditor/outputs/audit_compiled_pdf_with_references_20260418/audit_scorecard.json`
- `framework_compliance_auditor/outputs/audit_compiled_pdf_with_references_20260418/audit_summary.md`
- `framework_compliance_auditor/outputs/audit_compiled_pdf_with_references_20260418/compiled_contract.json`
- `framework_compliance_auditor/outputs/audit_compiled_pdf_with_references_20260418/phase_compliance_report.json`
- `framework_compliance_auditor/outputs/audit_compiled_pdf_with_references_20260418/revision_packet.json`
- `framework_compliance_auditor/reports/reporte_comparacion_referencias_2026-04-18.{md,pdf,tex}`

**Mensaje propuesto**:
```
chore(auditor): regenerate compliance outputs (April 2026 batch)
```

> **Considera**: ¿deberías ignorar estos outputs vía `.gitignore` en el futuro? Outputs
> regenerables suelen no ir al repo. Decisión tuya — no la tomo.

---

## 4. Untracked sin clasificar — necesitas decidir

| Path | Tamaño | Mi sospecha | Pregunta para ti |
|---|---|---|---|
| `apply_adjustments.py` | 1 archivo Python en raíz | script utility de migración | ¿permanente o efímero? Si efímero → `.gitignore`, si permanente → `chore(scripts):` |
| `apply_en_adjustments.py` | 1 archivo Python en raíz | script utility (variante en inglés) | mismo |
| `Recursos genericos/` | directorio en raíz | recursos compartidos | ¿qué contiene? si binarios, considerar git-lfs o ignorar |
| `wiki-front-vault/` | directorio en raíz | wiki/vault | si es vault privado → `.gitignore`, si público → `docs(wiki):` |
| `runtime-orchestrator/tests/fixtures/operational_intelligence_dashboard_live_contract_snapshot.json` | 1 fixture | test fixture del Eje A | va con Commit 1 |

---

## 5. Notas y advertencias

### 5.1 `motor_016.py` — sospecha de bloat

+2,748 LOC en un solo adapter es enorme. Posibles explicaciones:
1. Refactor legítimo que añade capacidad de rendering nueva.
2. Código duplicado / código generado.
3. Rama experimental que no debería ir.

Antes de commitear el Commit 4, verifica:
```bash
git diff HEAD -- runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py | head -100
```

### 5.2 `dashboard.py` — 5x el tamaño

`dashboard.py` pasa de **2,674 → 14,093 LOC**. Casi todo es boilerplate de directorios y
funciones de surface del research loop. Es legítimo si reemplaza código fuera de Python
(JSONs, configs ad-hoc) por código tipado, pero es **mucha superficie pública nueva**. Si
quieres trazabilidad fina, considera dividir en sub-módulos del dashboard antes de
commitear (ej: `dashboard_research_loop.py`, `dashboard_combination_review.py`).

### 5.3 Tests no agrupados todavía

Hay tests modificados que pueden pertenecer a varios ejes. Ejemplo: `test_report_conformance.py`
(+573 LOC) puede ser del eje C (composer) o del eje B (congruence_intelligence). El criterio
honesto: pertenece al eje cuya función testea. Mira el test antes de mover.

### 5.4 La auditoría de Claude se basó en este WIP

`RECOVERY_ARCHITECTURE_PLAN.md` y `RECOVERY_BACKLOG.md` (commit `9dc333c`) se escribieron
contra **HEAD**, no contra este WIP. Tras commitear los 4-5 commits propuestos, conviene
re-auditar (o pedirle a Claude que lo haga) para que el plan refleje la realidad post-WIP.

---

## 6. Resumen ejecutivo

```
Trabajo previo de 20,594 LOC se puede consolidar en 4-5 commits temáticos:

  1. feat(zlab_skill): autonomous research loop infrastructure       (~13K LOC)
  2. docs(governance): autonomous research loop authority documents  (~  500 LOC)
  3. refactor(congruence_intelligence): four-state epistemic model   (~ 3K  LOC)
  4. refactor(composer): incremental support for ARCHETYPAL_PRIOR    (~ 5K  LOC)
  5. chore(auditor): regenerate compliance outputs                   (    30 LOC)

Untracked sin clasificar:
  - apply_adjustments.py / apply_en_adjustments.py (decidir)
  - Recursos genericos/ (decidir)
  - wiki-front-vault/ (decidir, posible .gitignore)

Después de esto:
  - Working tree limpio.
  - R-00 desbloqueado.
  - La recovery propiamente dicha empieza.
  - El primer trabajo visible es R-W01..R-W05 (~160 LOC) — destrabar el cableado
    composer ↔ congruence_claim_contract_register que tu propio WIP construyó.
```

Si seguir este plan al pie de la letra es demasiado, recuerda: **un commit es mejor que
ninguno**, y **2-3 commits razonables son mejores que un commit gigante**. El objetivo es
que en 6 meses, mirando `git log`, sepas qué pasó.
