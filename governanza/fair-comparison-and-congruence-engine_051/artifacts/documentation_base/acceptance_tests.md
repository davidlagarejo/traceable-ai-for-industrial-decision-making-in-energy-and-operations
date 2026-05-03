# Acceptance Tests — Fair Comparison and Congruence Engine

Motor ID: motor_051

## happy_path
- Caso building: aparece el riesgo `whole_building_owner_capturable_comparison` y la normalización `owner_tenant_control_boundary`.
- Caso manufacturing: `area_based_energy_intensity_comparison` sale `comparable=false` y exige `throughput by shift`.
- Caso logistics: `warehouse_area_only_comparison` sale `comparable=false` y exige `service level` normalization.
- Casos building y manufacturing producen contradicciones cross-layer y correlaciones estructurales cuando corresponde.

## edge_cases
- Si faltan boundaries o bindings suficientes, el motor debe bloquear comparaciones y no esconder el gap.
- Si el caso hereda hipótesis rivales o claim impacts desde `motor_049`, deben preservarse en la salida.

## rejection_criteria
- Falla si una comparación inválida aparece como comparable.
- Falla si la salida pierde risks, blockers o contradicciones esperables.
- Falla si los counts planos no coinciden con los registros estructurados.
