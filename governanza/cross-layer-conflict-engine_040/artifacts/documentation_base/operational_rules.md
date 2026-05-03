# Operational Rules — Cross-Layer Conflict Engine

Motor ID: motor_040

## rules
1. Si dos capas implican acciones incompatibles o claims prematuros, el conflicto debe emitirse.
2. Buildings con burden regulatorio y boundary no resuelta deben poder producir conflicto regulación vs control.
3. Supuestos financieros owner-capturable sin control probado deben salir como conflicto.
4. Manufacturing con proceso estructural no resuelto no puede avanzar con framing de ahorro simple sin conflicto explícito.
5. Si el builder estructural no devuelve conflictos, el motor debe traducir conflictos cross-layer de `motor_051`.

## invariants
- `cross_layer_conflict_count` debe igualar el largo real del register;
- todas las filas deben tener `layers_involved` no vacías;
- el fallback no puede perder `evidence_state`;
- un conflicto traducido debe conservar `why_it_matters` y `potential_redesign_direction`.

## forbidden_operations
- suprimir conflictos para facilitar decisión o benchmark;
- convertir conflicto en solución final;
- devolver filas sin capas involucradas;
- ignorar el fallback de `motor_051` cuando el register estructural queda vacío.
