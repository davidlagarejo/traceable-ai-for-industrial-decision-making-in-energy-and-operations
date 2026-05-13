# Combination Engine — Auditoría real (no diseño)

> Versión inicial era un design doc para construir un combination engine. Tras
> revisión, el framework **ya tiene** ese engine en `zlab_skill/`. Este
> documento reemplaza el diseño original con una **auditoría de lo existente
> + gaps reales vs el prompt** (RECOVERY-2026-05-09).

---

## 1. Lo que ya existe en el repo

### 1.1 Catálogo de combinations (registry JSON)

Path: `runtime-orchestrator/zlab_skill/registry/combinations/`

| ID | asset_family | version |
|---|---|---|
| `warehouse_tariff_boundary_area_combo` | warehouse_distribution | 1.0.0 |
| `manufacturing_support_utility_maintenance_combo` | manufacturing | 1.0.0 |

Schema (de `warehouse_tariff_boundary_area_combo.v1.json`):

- `id`, `version`, `name`
- `pattern_ids[]` — qué patterns activan la combinación
- `trigger_logic[]` — condiciones de activación humanas
- `anti_triggers[]` — condiciones de bloqueo
- `combined_hypothesis` — la frase estructural
- `strategic_risk` — qué se rompe si se ignora
- `minimum_evidence[]` — evidence pack
- `financial_exposure[]` — traducción financiera
- `tad_action` — string con acciones TAD
- `prohibited_claims[]`
- `allowed_language` — frase
- `source_basis[]`
- `confidence_ceiling` — L0/L1/L2/L3/L4
- `adjudication_required: true`
- `tests[]`

### 1.2 Catálogo de patterns

Path: `runtime-orchestrator/zlab_skill/registry/patterns/`

23 patterns JSON, incluidos:
- `warehouse_mhe_charging_demand_peak`
- `warehouse_dock_infiltration_loss`
- `cold_chain_status_unknown`
- `value_boundary_leakage_owner_operator`
- `demand_charge_exposure_unknown`
- `reactive_power_exposure`
- `fair_comparison_invalid_area_metric`
- `benchmark_denominator_error`
- `digital_twin_prematurity`, `sensor_prematurity`
- `maintenance_maturity_not_evidenced`, `maintenance_hidden_value_driver`
- `compressed_air_leak_plausibility`
- `process_load_vs_waste`
- `procurement_vs_lifecycle_cost`, `procurement_vs_maintenance_conflict`
- `hvac_schedule_drift`
- `tenant_operator_boundary_unresolved`
- `compliance_vs_control_mismatch`
- `high_bay_lighting_waste`
- `steam_trap_failure_plausibility`
- `boiler_degradation_plausibility`, `chiller_degradation_plausibility`

### 1.3 Validators

Path: `runtime-orchestrator/zlab_skill/registry/validators/`

10 validators:
- `claim_governor_combination_minimum_evidence`
- `combination_use_evidence_ceiling`
- `fair_comparison_prohibited_claims`
- `financial_output_forbidden_terms`
- `memory_scope_cross_company_guard`
- `pattern_to_claim_allowed_language`
- `report_diversity_template_contamination`
- `report_output_template_contamination_guard`
- `source_traceability_source_basis`
- `tad_consistency_required_tad_action`

### 1.4 Engine code

- `zlab_skill/combination_engine.py` (523 LOC):
  - `build_combination_activation_register`
  - `build_latent_combination_candidate_register`
  - `build_admissible_combination_review_register`
  - `build_latent_combination_cluster_register`
  - `build_combination_review_register`
- `zlab_skill/combination_gap_analyzer.py` (200 LOC)
- `zlab_skill/combination_rerank_pipeline.py` (93 LOC)
- `zlab_skill/validator_engine.py` (`apply_combination_validators`)

### 1.5 Wiring

`motor_054.py` ya:
- línea 21: `from ..zlab_skill.combination_engine import build_combination_activation_register`
- línea 109: invoca `build_combination_activation_register(...)`
- línea 114: aplica `apply_combination_validators(...)`
- línea 273: emite `skill_combination_activation_register` en su output
- línea 293: emite `skill_combination_activation_count`

### 1.6 Memory policies

5 policies en `registry/memory_policies/`:
- `company_memory_company_confined`
- `contradiction_memory_company_confined`
- `pattern_memory_global_structured_prior`
- `source_memory_provider_family`
- `validation_memory_company_confined`

---

## 2. Mapeo prompt → realidad

| Prompt nuevo | Estado real |
|---|---|
| Capa 1 Knowledge Layer | ✅ existe (registry JSON, 23 patterns + 2 combos + 10 validators + 5 memory policies + 11 YAMLs) |
| Capa 2 Asset Family Engine | ⚠️ implícito via patterns (asset_family declarado en cada pattern) — **falta isolation validator explícito** |
| Capa 3 Pattern Activation | ✅ existe (`build_combination_activation_register` activa por pattern_ids) |
| Capa 4 Structural Combination Engine | ✅ **EXISTE Y ESTÁ WIRED** (523 LOC + motor_054 lo consume) |
| Capa 5 Hypothesis Engine | ✅ existe (`congruence_intelligence/hypothesis_backbone.py`) |
| Capa 6 Claim Governor (4 estados) | ✅ wired (recovery commits `b58d4d3`, `4a13590`, `ddcdb06`, `87c8879`) |
| Capa 7 Financial Translation | ✅ existe (`congruence_intelligence/finance_to_physics.py` + YAML) |
| Capa 8 TAD Engine | ✅ existe (`strategic_tad.py` + tad_action_rules.yaml) |
| Capa 9 Composer "tonto" | ✅ recovery hizo `executive_thesis.py` 2179 → 633 LOC con `composer_helpers/` |
| Capa 10 Validation Layer | ✅ 10 validators registry + 5 motors recovery (055-059) |

| Validador del prompt | Estado real |
|---|---|
| A. Asset Family Contamination | ❌ **FALTA** un motor explícito que bloquee patterns cross-family |
| B. Combination Validator | ✅ existe (`apply_combination_validators` + 2 validator JSONs específicos) |
| C. Report Uniqueness | ✅ motor_058 (recovery R-63) |
| D. Strategic Intelligence | ✅ motor_059 (recovery R-64) |
| E. Chart Validity Engine | ⚠️ chart_taxonomy.py existe pero **falta enforcement** que vincule cada chart a una combination/hipótesis activa y elimine si no |

---

## 3. Gaps REALES que sí hay que llenar

| # | Gap | Trabajo | Estimación |
|---|---|---|---|
| 1 | Catálogo de combinations es muy chico (solo 2) | Agregar 6-8 combinations seed: cold_chain_infiltration_logic, owner_operator_value_leakage (ya implícito en warehouse_tariff_boundary), manufacturing_compressed_air_maturity, process_heat_unbounded_duty, building_after_hours_phantom_load, datacenter_pue_composition_unclear, logistics_continuity_dispatch_dominance, wrong_denominator_area_normalized | 8 archivos JSON, ~400 LOC |
| 2 | Asset Family Isolation Validator (validador A del prompt) | Crear motor_061 que lee patterns activos + asset_family de motor_007 y bloquea cross-family contamination | adapter ~150 LOC + tests |
| 3 | Chart Validity Engine (validador E) | Crear motor_063 que verifica que cada chart en motor_018 output esté linkeado a una combination/hipótesis activa | adapter ~150 LOC + tests |
| 4 | Composer cableado a `skill_combination_activation_register` | motor_047 ya recibe motor_054; falta que executive_thesis exponga el register al output (similar a R-W01..R-W03 pero para combinations) | ~50 LOC |
| 5 | Tests de integración combinations end-to-end | Verificar que activación + validation + render funcionan en suite | ~150 LOC |

**Total**: ~900 LOC, 5 commits.

NO hay que construir un combination engine — **ya existe**. Solo agregar combinations al catálogo, los 2 validators faltantes (motor_061, motor_063), y wiring del composer.

---

## 4. Plan de implementación revisado

| # | Commit | Contenido |
|---|---|---|
| 1 | `docs(combination): replace design doc with real audit` | este archivo (sobrescribe el design original) |
| 2 | `feat(combinations): seed 8 new combinations to registry` | JSONs nuevos en `runtime-orchestrator/zlab_skill/registry/combinations/` |
| 3 | `recovery(motor_061): Asset Family Isolation Validator` | validador A del prompt |
| 4 | `recovery(motor_063): Chart Validity Engine` | validador E del prompt |
| 5 | `recovery(R-W06): wire skill_combination_activation_register al composer` | exponer al thesis output + render en cap. 4-5 |
| 6 | `tests(combinations): integration coverage` | end-to-end test |

Suite target: ≥ 920 passed.

Comprometeo: **no duplicar código existente**. Toco solo lo necesario.
