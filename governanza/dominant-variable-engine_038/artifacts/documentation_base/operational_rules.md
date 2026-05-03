# Operational Rules — Dominant Variable Engine

Motor ID: motor_038

## rules
1. Toda variable parte de una hipótesis o prior; sólo se promueve con señales concretas de fields o coverage.
2. `utility_baseline` no puede ser observado sin utility bills; con `current_eui` sólo puede llegar a condicional.
3. `LL97_pathway` sólo puede salir observado para buildings NYC con cobertura pública suficiente.
4. `tenant_metering` y `owner_control_boundary` deben permanecer condicionadas salvo evidencia de metering, lease responsibility o boundary explícito.
5. Variables de manufacturing como `throughput`, `thermal_duty`, `downtime` o `compressed_air` pueden subir a condicional con process clues, pero a observado sólo con field directo.
6. El motor debe añadir `owner_control_boundary` si upstream no la incluyó.

## invariants
- `dominant_variable_count` debe coincidir con el largo real del register;
- `observed_or_conditional_variable_count` debe contar sólo `OBSERVED_FACT` y `CONDITIONAL_HYPOTHESIS`;
- cada variable debe conservar su `layer` y su racional de decisión;
- ningún register puede quedar vacío si existe al menos un arquetipo estructural modelable upstream.

## forbidden_operations
- transformar priors arquetipales en hechos observados para facilitar benchmarking;
- omitir `owner_control_boundary` porque “ya se entiende” desde la abstracción;
- declarar variables regulatorias observadas sin coverage;
- usar este motor para emitir comparabilidad, contradicciones o plan de acción final;
- borrar confirmaciones o falsaciones para simplificar el registro.
