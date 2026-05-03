# Functional Contract — Cross-Layer Conflict Engine

Motor ID: motor_040

## inputs
- `system_abstraction`
  Tipo: `dict[str, dict]`
  Productor: `motor_037`
  Uso: estructura regulatoria, control, drivers y madurez.
- `dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
  Uso: variables que pueden entrar en contradicción con claims, finanzas o decisión.
- `financial_exposure_register`
  Tipo: `list[dict]`
  Productor: `motor_014`
  Uso: supuestos financieros que pueden depender de control o evidencia no probada.
- `claim_permission_register`
  Tipo: `list[dict]`
  Productor: `motor_034`
  Uso: permisos de claim que pueden estar prematuramente abiertos.
- `decision_front_actions`
  Tipo: `list[dict]`
  Productor: `motor_033`
  Uso: acciones o frentes de decisión que pueden ser prematuros.
- `cross_layer_congruence_register`
  Tipo: `list[dict]`
  Productor: `motor_051`
  Uso: fallback traducible cuando el constructor estructural no produce conflictos propios.

## outputs
- `cross_layer_conflict_register`
  Tipo: `list[dict]`
  Consumidores: `motor_041`, `motor_044`, capas de claim governance
  Contenido: `conflict`, `layers_involved`, `why_it_matters`, `evidence_state`, `what_confirms_it`, `what_falsifies_it`, `potential_redesign_direction`.
- `cross_layer_conflict_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de conflictos emitidos.

## limits
- no puede omitir conflictos sólo porque downstream quiera accionar;
- no convierte una contradicción en causalidad ni en solución definitiva;
- no reencuadra el problema por sí mismo;
- no requiere que todas las capas existan para emitir conflictos: puede trabajar con subsets y fallback;
- nunca degrada un conflicto real a nota blanda si afecta claim, CAPEX o comparabilidad.

## validations
- toda fila debe incluir conflicto, capas involucradas, importancia estratégica y dirección potencial de rediseño;
- si el constructor estructural no devuelve filas, el fallback desde `motor_051` debe producir una traducción válida;
- buildings deben poder exponer conflicto entre regulación, control y finanzas owner-capturable;
- manufacturing debe poder exponer conflicto entre framing energético, proceso y mantenimiento;
- `cross_layer_conflict_count` debe coincidir con el largo del register.
