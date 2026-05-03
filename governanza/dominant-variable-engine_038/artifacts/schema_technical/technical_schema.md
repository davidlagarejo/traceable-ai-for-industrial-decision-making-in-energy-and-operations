# Technical Schema — Dominant Variable Engine

Motor ID: motor_038

## entities
- `DominantVariableRecord`
  Variable candidata dominante con estado de evidencia.
- `DominantVariableRegister`
  Colección completa de variables candidatas emitidas por el motor.

## fields
- `DominantVariableRecord`
  `variable: str (required)` — nombre de la variable candidata.
  `layer: str (required)` — capa estructural o de control a la que pertenece.
  `dominance: str (required)` — etiqueta de dominancia como `observed_candidate_dominant`, `conditional_candidate_dominant` o `archetypal_candidate`.
  `evidence_state: str (required)` — estado epistemológico final.
  `why_it_could_matter: str (required)` — racional técnico de relevancia.
  `what_confirms_it: list[str] (required)` — evidencias que la confirmarían.
  `what_falsifies_it: list[str] (required)` — evidencias que la refutarían.
  `decision_impact: list[str] (required)` — impactos sobre decisiones downstream.
- `DominantVariableRegister`
  `dominant_variable_register: list[DominantVariableRecord] (required)`
  `dominant_variable_count: int (required)`
  `observed_or_conditional_variable_count: int (required)`

## relationships
- `dominant_variable_hypotheses` se convierten en `DominantVariableRecord`.
- `asset_field_register` y `dataset_coverage_register` modifican `evidence_state` y `dominance`.
- `system_abstraction` condiciona el contexto semántico del register aunque hoy no reescriba filas directamente.

## identifiers
- Identificador natural de `DominantVariableRecord`: `variable`.
- Identificador natural de `DominantVariableRegister`: target definido por `target_type` + `target_name` + `jurisdiction_scope`.

## versioning
- Una nueva observación de field o coverage puede cambiar el `evidence_state` y por tanto la versión lógica del record.
- Cambios en el arquetipo o en el target definition exigen regenerar el register.
- Los counts planos deben regenerarse en cada nueva versión del register.

## lineage
- `variable`, `layer`, confirmaciones y falsaciones nacen de `dominant_variable_hypotheses`.
- `evidence_state` nace de la combinación entre hipótesis y señales observadas en fields y datasets.
- `owner_control_boundary` puede ser introducida localmente por el motor cuando falta upstream.
