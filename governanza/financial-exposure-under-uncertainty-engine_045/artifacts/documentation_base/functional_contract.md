# Functional Contract — Financial Exposure Under Uncertainty Engine

Motor ID: motor_045

## inputs
- `system_abstraction`
  Tipo: `dict[str, dict]`
  Productor: `motor_037`
  Uso: delimitar capas y grado de observación real por dominio.
- `dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
  Uso: variables dominantes que pueden invalidar o sostener una hipótesis financiera.
- `cross_layer_conflict_register`
  Tipo: `list[dict]`
  Productor: `motor_040`
  Uso: contradicciones que vuelven prematuro un output financiero.
- `problem_framing_register`
  Tipo: `list[dict]`
  Productor: `motor_041`
  Uso: problema real que la capa financiera debe respetar.
- `competitive_comparison_register`
  Tipo: `list[dict]`
  Productor: `motor_043`
  Uso: referencia comparativa bounded, útil para riesgo de transferabilidad.
- `conditional_redesign_register`
  Tipo: `list[dict]`
  Productor: `motor_044`
  Uso: hipótesis de rediseño que cambian la lectura económica.
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012` / `motor_007`
  Uso: distinguir building vs manufacturing.

## outputs
- `structural_financial_exposure_register`
  Tipo: `list[dict]`
  Consumidores: síntesis, `motor_034`, reportes financieros bounded
  Contenido: `structural_assumption`, `evidence_state`, `financial_exposure_if_wrong`, `evidence_needed`, `allowed_financial_output`, `prohibited_financial_output`.
- `structural_financial_exposure_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de exposiciones emitidas.
- `evidence_state_by_layer_register`
  Tipo: `list[dict]`
  Consumidores: `motor_034`, validadores de consistencia, síntesis
  Contenido: `layer`, `evidence_state`, `dominant_open_questions`, `observed_support`, `structural_risk_if_wrong`, `linked_conflicts`, `linked_problem_frames`.
- `evidence_state_by_layer_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: número total de capas auditadas.

## limits
- no puede emitir ROI o payback si la exposición sigue abierta;
- no puede usar evidencia comparativa como sustituto de control boundary o process truth;
- la salida debe seguir siendo bounded aunque el caso sea financieramente atractivo;
- no convierte screening en underwriting final.

## validations
- building debe bloquear outputs de savings/ROI cuando el owner-only upside siga condicional;
- manufacturing debe ligar riesgo de CAPEX a proceso, throughput o downtime;
- `evidence_state_by_layer_register` debe cubrir las 12 capas definidas por el runtime;
- los counts deben coincidir con el largo de cada register.
