# Conceptual Schema — Cross-Layer Conflict Engine

Motor ID: motor_040

## entities
- `CrossLayerConflictRecord`: contradicción explícita entre capas del modelo.
- `ConflictEvidenceBasis`: base de confirmación o falsación del conflicto.
- `FallbackCongruenceConflict`: conflicto traducido desde `motor_051`.

## relationships
- `system_abstraction` + `dominant_variable_register` + finanzas + claim permissions + decision fronts → `CrossLayerConflictRecord`
- `cross_layer_congruence_register` → `FallbackCongruenceConflict` → `CrossLayerConflictRecord`

## key_fields
- `CrossLayerConflictRecord`: `conflict`, `layers_involved`, `why_it_matters`, `evidence_state`, `what_confirms_it`, `what_falsifies_it`, `potential_redesign_direction`
- `ConflictEvidenceBasis`: listas de confirmación y falsación
- `FallbackCongruenceConflict`: `contradiction`, `layers`, `strategic_risk`, `possible_redesign`, `evidence_state`
