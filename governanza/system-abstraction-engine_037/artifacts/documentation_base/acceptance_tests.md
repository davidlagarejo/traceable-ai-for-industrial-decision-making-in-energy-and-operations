# Acceptance Tests — System Abstraction Engine

Motor ID: motor_037

## happy_path
- Caso NYC building con coverage de PLUTO, LL84 y LL97 y arquetipo `commercial_office_tower_nyc`: `asset_type` y `regulatory_exposure` salen como `OBSERVED_FACT`, mientras `control_structure` queda como `CONDITIONAL_HYPOTHESIS`.
- Caso manufacturing bounded con arquetipo `manufacturing_laminate`: `dominant_process_type` queda `CONDITIONAL_HYPOTHESIS`, `business_function` queda `ARCHETYPAL_PRIOR` y `regulatory_exposure` sale observado por coverage industrial.

## edge_cases
- Si el arquetipo seleccionado es `target_not_yet_structurally_modelable`, todas las dimensiones deben degradarse a `INADMISSIBLE_CLAIM`.
- Si no existe screening público suficiente, `evidence_maturity` debe quedar como framing arquetipal y no como soporte observado.

## rejection_criteria
- Falla si el bundle omite alguna de las dimensiones estructurales gobernadas.
- Falla si `system_abstraction_evidence_states` no coincide con los `evidence_state` del bundle.
- Falla si `control_structure` aparece como `OBSERVED_FACT` sin evidencia de boundary o metering.
