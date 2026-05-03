# Functional Contract — Dominant Variable Engine

Motor ID: motor_038

## inputs
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012.facility_prior.target_definition`, con fallback a `motor_007.target_definition_contract`
  Contenido mínimo: `target_type`, `target_name`, `jurisdiction_scope`.
- `system_abstraction`
  Tipo: `dict[str, dict]`
  Productor: `motor_037`
  Uso: contexto estructural sobre control, drivers, madurez y exposición regulatoria.
- `dominant_variable_hypotheses`
  Tipo: `list[dict]`
  Productor: `motor_039`
  Uso: variables candidatas iniciales y sus rutas de confirmación o falsación.
- `asset_field_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: promover variables a `OBSERVED_FACT` o `CONDITIONAL_HYPOTHESIS`.
- `dataset_coverage_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: detectar cobertura suficiente para variables regulatorias como `LL97_pathway`.

## outputs
- `dominant_variable_register`
  Tipo: `list[dict]`
  Consumidores: `motor_040`, `motor_042`, `motor_043`, `motor_044`
  Contenido: variables candidatas con `dominance`, `evidence_state`, racional y paths de validación.
- `dominant_variable_count`
  Tipo: `int`
  Consumidores: observabilidad y validadores
  Contenido: número total de variables emitidas.
- `observed_or_conditional_variable_count`
  Tipo: `int`
  Consumidores: monitoreo y gatekeepers downstream
  Contenido: cantidad de variables que ya superaron el estado de prior arquetipal puro.

## limits
- no acepta una variable como observada si sólo existe por hipótesis arquetipal;
- no emite variables fuera del vocabulario gobernado por `motor_039` más la inyección controlada de `owner_control_boundary`;
- nunca colapsa cobertura regulatoria en comparabilidad o benchmark final;
- no produce peer logic, correlation graph ni framing estratégico;
- no reescribe confirmaciones o falsaciones de una variable para encajar narrativas downstream.

## validations
- cada variable emitida debe conservar `variable`, `layer`, `evidence_state`, `why_it_could_matter`, `what_confirms_it`, `what_falsifies_it` y `decision_impact`;
- `LL97_pathway` sólo puede ser `OBSERVED_FACT` cuando la cobertura pública del building lo soporta;
- `tenant_metering` y `owner_control_boundary` no pueden quedar como hechos observados sin señales de control o lease responsibility;
- si una variable de manufacturing no tiene field directo pero sí process clues, puede subir como `CONDITIONAL_HYPOTHESIS`, no como hecho observado;
- `owner_control_boundary` debe existir aunque no venga en `dominant_variable_hypotheses`.
