# Acceptance Tests — Dominant Variable Engine

Motor ID: motor_038

## happy_path
- Caso building NYC tipo One Vanderbilt: el register incluye `central_plant`, `tenant_metering`, `after_hours_occupancy`, `LL97_pathway` y `owner_control_boundary`; `LL97_pathway` sale observado y `central_plant` sale condicional si no hay topology directa.
- Caso manufacturing laminate: el register incluye `throughput`, `thermal_duty`, `compressed_air` y `downtime`, todos al menos como hipótesis condicionales cuando hay process clues.

## edge_cases
- Si `dominant_variable_hypotheses` omite `owner_control_boundary`, el motor debe inyectarla.
- Si no existe coverage regulatoria para building, `LL97_pathway` no puede salir observado.

## rejection_criteria
- Falla si el register pierde confirmaciones o falsaciones de una variable.
- Falla si `dominant_variable_count` o `observed_or_conditional_variable_count` no coinciden con el contenido real.
- Falla si una variable prior sale observada sin soporte en fields o datasets.
