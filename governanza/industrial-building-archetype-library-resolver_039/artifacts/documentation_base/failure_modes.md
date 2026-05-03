# Failure Modes — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## failure_modes_list
1. `non_operating_promotion`
   Síntoma: un HQ, mailing address o target ambiguo termina con arquetipo modelable y variables dominantes no vacías.
   Riesgo: toda la lane estructural razona sobre un activo físico que ni siquiera estaba cerrado.
2. `premature_specific_selection`
   Síntoma: el motor elige un arquetipo muy específico sin base suficiente en jurisdicción, hints o clasificación.
   Riesgo: downstream queda sesgado hacia comparables, riesgos y drivers que no corresponden.
3. `generic_fallback_overuse`
   Síntoma: casos con señales fuertes siguen cayendo a `commercial_building_generic`, `manufacturing_generic` u otros fallbacks.
   Riesgo: la lane pierde resolución útil y subestima variables dominantes reales del caso.
4. `anti_hallucination_break`
   Síntoma: el output o el consumidor downstream trata el arquetipo como observación confirmada.
   Riesgo: claims de diseño o inversión pasan a reporte final sin soporte asset-level.
5. `basis_register_drift`
   Síntoma: `archetype_selection_basis_register` no explica por qué se eligió el arquetipo, o cita fuentes que no corresponden con los inputs.
   Riesgo: la selección deja de ser auditable y no puede falsarse correctamente.

## anti_patterns
1. Tratar cualquier activo en NYC como si automáticamente fuera un office tower high-rise.
2. Confundir palabras como `laminate`, `curing` o `utility island` con verdad completa del proceso local, en lugar de usarlas sólo como bounded clue.
3. Usar el arquetipo seleccionado como si ya fuera recomendación de CAPEX, comparación competitiva o cierre financiero.

## degradation_signals
- aumento repetido de casos `fallback_unresolved` o `fallback_generic` en targets que sí tienen señales observadas suficientes;
- apariciones de `match_confidence=high` sin `selection_basis_register` consistente con jurisdicción o clues del `asset_field_register`;
- `dominant_variable_count` distinto del número real de hipótesis serializadas;
- casos `target_not_yet_structurally_modelable` con hipótesis dominantes no vacías o con evidence state distinto de `INADMISSIBLE_CLAIM`;
- downstream que empieza a citar `business_function`, `economic_driver` o `regulatory_exposure` como si fueran hechos confirmados del activo.
