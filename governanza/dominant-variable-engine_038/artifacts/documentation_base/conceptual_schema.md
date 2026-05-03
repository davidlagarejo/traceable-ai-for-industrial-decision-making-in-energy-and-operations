# Conceptual Schema — Dominant Variable Engine

Motor ID: motor_038

## entities
- `DominantVariableRecord`: variable candidata dominante con estado de evidencia y semántica de decisión.
- `DominantVariableRegister`: colección completa de variables emitidas para el activo.
- `VariablePromotionRule`: regla que promueve una variable desde prior a condicional u observado.

## relationships
- `dominant_variable_hypotheses` + `asset_field_register` + `dataset_coverage_register` → `DominantVariableRegister`
- `system_abstraction` condiciona la lectura y legitimidad del register
- `VariablePromotionRule` determina el `evidence_state` final de cada `DominantVariableRecord`

## key_fields
- `DominantVariableRecord`: `variable`, `layer`, `dominance`, `evidence_state`, `why_it_could_matter`, `what_confirms_it`, `what_falsifies_it`, `decision_impact`
- `DominantVariableRegister`: lista de `DominantVariableRecord`
- `VariablePromotionRule`: `variable`, `field_signals`, `dataset_signals`, `promotion_target`
