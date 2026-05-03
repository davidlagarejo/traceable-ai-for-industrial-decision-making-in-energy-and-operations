# Test Spec — System Abstraction Engine

Motor ID: motor_037

## happy_path
- Caso NYC commercial building con coverage de PLUTO, LL84 y LL97: `asset_type=OBSERVED_FACT`, `regulatory_exposure=OBSERVED_FACT`, `control_structure=CONDITIONAL_HYPOTHESIS`.
- Caso manufacturing laminate bounded: `dominant_process_type=CONDITIONAL_HYPOTHESIS`, `business_function=ARCHETYPAL_PRIOR`, `regulatory_exposure=OBSERVED_FACT`.

## sparse_case
- Caso con pocos `asset_field_register` pero arquetipo válido: el motor debe seguir emitiendo las once dimensiones y degradar a `ARCHETYPAL_PRIOR` o `NOT_OBSERVED` cuando falte base observada.

## malformed_input
- Si falta `target_type` o el arquetipo no es interpretable, el motor no puede fabricar observaciones fuertes y debe degradar el bundle.
- Si los registros de campos o coverage vienen en forma inválida, la superficie no debe salir con estados observados por accidente.

## edge_cases
- `selected_archetype_id=target_not_yet_structurally_modelable` debe producir once dimensiones en `INADMISSIBLE_CLAIM`.
- `screening_supported=false` debe impedir que `evidence_maturity` salga como `OBSERVED_FACT`.

## pass_criteria
- `system_abstraction_fields` coincide con las claves reales del bundle.
- `system_abstraction_evidence_states` replica exactamente los estados del bundle.
- Building y manufacturing muestran patrones distintos de evidencia compatibles con tests runtime.

## fail_criteria
- Falta una dimensión estructural gobernada.
- Una dimensión sale observada sin base admisible.
- La superficie plana queda desincronizada respecto al bundle estructurado.
