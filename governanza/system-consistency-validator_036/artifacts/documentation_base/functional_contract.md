# Functional Contract — System Consistency Validator

Motor ID: motor_036

## inputs

- `motor_016.report_package`
  Tipo: `dict`
  Productor: `motor_016`
  Uso: superficie visible a validar antes de render.
- `motor_014.claim_permission_register`, `motor_014.claim_permission_summary`, `motor_014.scenario_evidence_link_register`
  Tipo: `list[dict]` y `dict`
  Productor: `motor_014`
  Uso: autoridad base sobre claims, conteos y contratos escenario-evidencia.
- `motor_034.claim_permission_register`, `motor_034.claim_contract_register`, `motor_034.report_type_classifier_table`, `motor_034.report_output_mode_classifier_table`, `motor_034.structural_claim_permission_register`, `motor_034.structural_output_mode_classifier_table`, `motor_034.structural_output_mode_summary`, `motor_034.structural_primary_promotion_gate`, `motor_034.canonical_asset_context_summary`
  Tipo: `list[dict]` y `dict`
  Productor: `motor_034`
  Uso: autoridad sobre report mode, output-mode selection y bounded claim governance.
- `motor_012.asset_field_register`, `motor_012.dataset_coverage_register`, `motor_012.declared_input_downgrade_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: validar identidad visible, coverage pública y no-promoción de declared input.
- `motor_028.source_register`, `motor_028.search_attempt_ledger`
  Tipo: `list[dict]`
  Productor: `motor_028`
  Uso: validar source activation y coverage claims.
- `motor_033.decision_front_actions`, `motor_033.expanded_structural_tad_action_register`
  Tipo: `list[dict]`
  Productor: `motor_033`
  Uso: validar coherencia entre TAD visible y acciones estructurales expandidas.
- `motor_037`, `motor_043`, `motor_044`, `motor_045`, `motor_046`, `motor_049`, `motor_051`, `motor_052`, `motor_053`, `motor_054`
  Tipo: `dict` o `list[dict]` segun motor
  Productor: lane estructural, congruence lane y packaging inputs
  Uso: validar coherencia entre contradicciones, peer framing, redesign, finance, minimum evidence, local binding, maintenance, regulatory physics y strategic action surfaces.

## outputs

- `consistency_register`
  Tipo: `list[dict]`
  Consumidores: observabilidad, bloqueo de render y auditoria
  Contenido: una fila por chequeo con `check_id`, `passed`, `severity`, `message`, `location`.
- `critical_failures`
  Tipo: `list[dict]`
  Consumidores: gating de render
  Contenido: subset critico de checks fallidos con motivo bloqueante.
- `blocking_reason_register`
  Tipo: `list[dict]`
  Consumidores: UIs, operadores y pipelines de render
  Contenido: alias explcito de las razones bloqueantes.
- `canonical_report_state`
  Tipo: `dict`
  Consumidores: observabilidad y validadores downstream
  Contenido: `document_visible_type`, `canonical_asset_context_state`, `screening_supported`.
- `critical_failure_count`
  Tipo: `int`
  Consumidores: observabilidad y gating.
- `can_render_pdf`
  Tipo: `bool`
  Consumidores: render lane
  Contenido: `true` solo si no quedan fallos criticos.

## limits

- the validator may block, but it may not repair upstream content on its own;
- it may not invent missing evidence, claim traces or chart context to make the package pass;
- it may not overrule claim governance, local-binding state or entity-resolution conflicts for convenience;
- it must stay conservative: if the report package and the authoritative registers disagree, render remains blocked;
- it validates admissibility and coherence, not narrative quality or aesthetic merit.

## validations

- `critical_failures` must be the subset of `consistency_register` where `passed=false` and `severity=critical`;
- `can_render_pdf` must equal `critical_failure_count == 0`;
- visible report mode, outline mode and executive thesis mode must stay aligned;
- declared inputs, unresolved entity conflicts, foreign chart context and structurally invalid comparisons must remain render-blocking when present.
