# Acceptance Tests — Structural Benchmarking Engine

Motor ID: motor_042

## happy_path
- Building: aparece la dimensión `compliance and public screening context` y un peer `Class A NYC LL97-covered office towers`.
- Manufacturing: aparece benchmark `thermal-process laminate` y una interpretación que advierte no mapear intensidad directamente a waste.

## edge_cases
- Si el benchmark sólo es arquetipal, debe quedar claro en `evidence_state` e `interpretation`.

## rejection_criteria
- Falla si falta `interpretation`.
- Falla si el benchmark manufacturing colapsa a waste directo.
- Falla si `structural_benchmark_count` no coincide con el register.
