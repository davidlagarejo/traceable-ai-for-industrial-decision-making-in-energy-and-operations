# Technical Schema — Cross-Layer Conflict Engine

Motor ID: motor_040

## entities
- `CrossLayerConflictRecord`
- `CrossLayerConflictRegister`

## fields
- `CrossLayerConflictRecord`
  `conflict: str (required)`
  `layers_involved: list[str] (required)`
  `why_it_matters: str (required)`
  `evidence_state: str (required)`
  `what_confirms_it: list[str] (required)`
  `what_falsifies_it: list[str] (required)`
  `potential_redesign_direction: str (required)`
- `CrossLayerConflictRegister`
  `cross_layer_conflict_register: list[CrossLayerConflictRecord] (required)`
  `cross_layer_conflict_count: int (required)`

## relationships
- structural abstraction, dominant variables, finance, claim permissions and decision fronts feed `CrossLayerConflictRecord`;
- fallback congruence conflicts from `motor_051` can be translated into the same record shape.

## identifiers
- Identificador natural de `CrossLayerConflictRecord`: `conflict`.
- Identificador natural de `CrossLayerConflictRegister`: target bounded del caso.

## versioning
- Cambios en variables dominantes, finance assumptions o cross-layer congruence alteran la versión lógica del register.
- El count plano debe regenerarse con cada nueva versión.

## lineage
- filas directas trazan lineage a `motor_037`, `motor_038`, `motor_014`, `motor_034` y `motor_033`;
- filas fallback trazan lineage a `motor_051.cross_layer_congruence_register`.
