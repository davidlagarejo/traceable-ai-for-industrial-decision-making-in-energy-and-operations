# Test Spec — Dominant Variable Engine

Motor ID: motor_038

## happy_path
- Caso building NYC: el register incluye `central_plant`, `tenant_metering`, `after_hours_occupancy`, `LL97_pathway` y `owner_control_boundary`, con `LL97_pathway=OBSERVED_FACT`.
- Caso manufacturing: el register incluye `throughput`, `thermal_duty`, `compressed_air` y `downtime`, todos al menos como `CONDITIONAL_HYPOTHESIS`.

## sparse_case
- Si faltan fields observados pero existe arquetipo válido, las variables deben quedar como priors arquetipales o hipótesis condicionales, no desaparecer.

## malformed_input
- Si faltan hipótesis dominantes o la estructura de inputs es inválida, el motor no puede promover variables a observado por accidente.

## edge_cases
- `owner_control_boundary` debe ser inyectada cuando no viene upstream.
- `LL97_pathway` no puede ser observado fuera del contexto building NYC con coverage suficiente.

## pass_criteria
- El register conserva todas las claves estructurales por fila.
- Los counts planos coinciden con el contenido real.
- Building y manufacturing muestran patrones distintos y coherentes de promoción.

## fail_criteria
- Variables observadas sin soporte admisible.
- Omisión de `owner_control_boundary`.
- Counts desincronizados respecto al register.
