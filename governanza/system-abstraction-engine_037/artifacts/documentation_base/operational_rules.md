# Operational Rules — System Abstraction Engine

Motor ID: motor_037

## rules
1. Toda dimensión emitida debe llevar `evidence_state` explícito; no existen statements “implícitos”.
2. `asset_type` sólo sube a `OBSERVED_FACT` cuando el `target_type` está claramente definido.
3. `business_function` y `value_creation_mechanism` permanecen como `ARCHETYPAL_PRIOR` salvo evidencia directa que el motor hoy no consume como observación fuerte.
4. `control_structure` sólo puede ser `OBSERVED_FACT` si hay señales concretas de control, metering o lease boundary en `asset_field_register`.
5. `regulatory_exposure` sólo puede declararse `OBSERVED_FACT` cuando jurisdicción, coverage o source markers sustentan la observación regulatoria.
6. Si el arquetipo seleccionado es `target_not_yet_structurally_modelable`, todas las salidas deben quedar en `INADMISSIBLE_CLAIM`.

## invariants
- `system_abstraction_fields` debe coincidir con las claves reales de `system_abstraction`;
- `system_abstraction_evidence_states` debe reflejar exactamente el `evidence_state` de cada statement;
- el bundle siempre debe cubrir las once dimensiones estructurales gobernadas;
- una observación regulatoria observada no puede coexistir con bundle vacío o con target no bounded.

## forbidden_operations
- convertir clues de brochure o nomenclatura de asset en control facts sin soporte de campo;
- omitir `what_changes_it` o `minimum_evidence_required` para simplificar el statement;
- usar este motor para cerrar benchmarking, framing o claims económicos downstream;
- borrar el rastro entre prior arquetipal y observación real;
- devolver un bundle parcialmente poblado sin representación explícita de las demás dimensiones.
