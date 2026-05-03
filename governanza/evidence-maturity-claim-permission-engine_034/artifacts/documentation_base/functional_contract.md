# Functional Contract — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## inputs

- `motor_007.target_definition_contract`
  Tipo: `dict`
  Productor: `motor_007`
  Uso: fijar jurisdiccion, target type y contexto base del activo.
- `motor_007.target_classification_object`
  Tipo: `dict`
  Productor: `motor_007`
  Uso: distinguir operating asset, headquarters u otros contextos de clasificacion.
- `motor_007.technical_substrate_readiness`
  Tipo: `str`
  Productor: `motor_007`
  Uso: decidir si el caso puede aspirar a `Exploratory Prior Brief` o a `Full Technical Decision Intelligence Report`.
- `motor_007.recommended_report_type`
  Tipo: `str`
  Productor: `motor_007`
  Uso: propuesta inicial de report type que el motor puede mantener o degradar.
- `motor_012.asset_field_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: base principal para derivar madurez variable por variable.
- `motor_012.missing_evidence_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: evidencias faltantes que condicionan report readiness y claim permission.
- `motor_012.compliance_applicability_case`
  Tipo: `dict`
  Productor: `motor_012`
  Uso: contexto regulatorio y postura de screening.
- `motor_028.source_register`
  Tipo: `list[dict]`
  Productor: `motor_028`
  Uso: soporte de dataset coverage, source authority y upgrades de madurez.
- `motor_035`, `motor_037`, `motor_038`, `motor_039`, `motor_040`, `motor_041`, `motor_042`, `motor_043`, `motor_044`, `motor_045`, `motor_046`, `motor_049`, `motor_051`
  Tipo: `dict` o `list[dict]` segun motor
  Productor: lane estructural y de congruencia
  Uso: activar canonical problem frame, structural claim permission, structural output modes y promotion gate.

## outputs

- `dataset_coverage_register`
  Tipo: `list[dict]`
  Consumidores: auditabilidad, screening y upgrades de madurez.
- `variable_maturity_register`
  Tipo: `list[dict]`
  Consumidores: claim governance, decision gating y report selection.
- `cluster_maturity_register`
  Tipo: `list[dict]`
  Consumidores: canonical asset context y screening profile.
- `cluster_report_readiness_profile`
  Tipo: `dict`
  Consumidores: report gating y `maturity_summary`.
- `canonical_asset_context_summary`
  Tipo: `dict`
  Consumidores: report classifiers y surfaces de screening.
- `claim_permission_register`
  Tipo: `list[dict]`
  Consumidores: synthesis, validators y output governance.
- `structural_claim_permission_register`
  Tipo: `list[dict]`
  Consumidores: structural mode selection y bounded technical outputs.
- `claim_contract_register`
  Tipo: `list[dict]`
  Consumidores: downstream synthesis con razonamiento explicito.
- `decision_permission_register`
  Tipo: `list[dict]`
  Consumidores: decision-core y report admissibility layers.
- `report_readiness_register`
  Tipo: `dict`
  Consumidores: report classifiers, synthesis y dashboards.
- `report_type_classifier_table`
  Tipo: `list[dict]`
  Consumidores: selector primario de report type.
- `structural_output_mode_classifier_table`
  Tipo: `list[dict]`
  Consumidores: lane estructural y promotion logic.
- `structural_output_mode_summary`
  Tipo: `dict`
  Consumidores: promotion gate y `maturity_summary`.
- `report_output_mode_classifier_table`
  Tipo: `list[dict]`
  Consumidores: publicacion, selection basis y visible output mode control.
- `canonical_problem_frame`
  Tipo: `dict`
  Consumidores: structural reasoning, synthesis y bounded action reports.
- `structural_primary_promotion_gate`
  Tipo: `dict`
  Consumidores: promotion logic entre output estructural y report primario.
- `maturity_summary`
  Tipo: `dict`
  Consumidores: observabilidad y compresion de estado.

## limits

- missing critical variables such as `GFA` must block strong numeric EUI and ROI claims;
- benchmark-only signals may unlock screening or directional outputs, but not decision-grade closure;
- declared-input rows must remain capped and visible as lower-trust evidence;
- accepted NYC public records may upgrade maturity only when the observed field value is also present;
- NYC-specific LL97 claim surfaces must not appear in non-NYC contexts;
- structural lane activation may turn on canonical problem framing without automatically promoting the primary report type;
- a requested `Full Technical Decision Intelligence Report` must be clamped down when maturity or substrate readiness remains below threshold.

## validations

- output permission must be evidence-led, not request-led;
- row-level maturity and top-level report permission must stay logically aligned;
- structural output modes must not bypass blocked claim permissions;
- report classifiers and readiness outputs must remain internally consistent with `maturity_summary`.
