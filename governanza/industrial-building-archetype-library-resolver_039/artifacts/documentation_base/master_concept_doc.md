# Master Concept Document — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## purpose
Industrial / Building Archetype Library Resolver selecciona un arquetipo estructural acotado para el target actual usando la definición del activo, su clasificación operativa, señales del `facility_prior` y contexto mínimo de fuentes públicas observadas. Su salida no pretende demostrar cómo funciona el activo real, sino fijar un prior estructural gobernado para que la lane de inteligencia estructural tenga un punto de partida auditable. También publica un contrato anti-hallucination para impedir que ese prior se venda como hecho observado.

## what_it_does
- consume `target_definition`, `target_classification_object`, `asset_field_register`, `dataset_coverage_register` y `source_register` desde `motor_007`, `motor_012`, `motor_028` y, en último fallback, desde `__pipeline__`;
- resuelve una selección dentro de la librería estructural cerrada: arquetipos específicos como `commercial_office_tower_nyc`, `manufacturing_laminate` o `utility_heavy_site_generic`, o bien fallbacks genéricos y el estado `target_not_yet_structurally_modelable`;
- construye `archetype_selection_basis_register` con la base observable que justificó la selección, sin convertirla en verdad local del activo;
- emite `dominant_variable_hypotheses`, `archetype_minimum_evidence_register` y `system_abstraction_seed` para que los motores `037` a `046` continúen con abstracción, comparables, conflict framing y packaging estructural;
- devuelve campos de conveniencia ya aplanados como `selected_archetype_id`, `selected_archetype_label`, `match_confidence`, `resolver_state` y `dominant_variable_count`;
- fija `anti_hallucination_contract` para recordar que el arquetipo sólo puede usarse en estructuración de hipótesis, diseño de evidencia y motores estructurales posteriores.

## what_it_does_not_do
- no prueba que el activo real opere exactamente como el arquetipo seleccionado;
- no convierte hints públicos o nombres de campos en performance local observada;
- no hace benchmarking, comparación competitiva, stress financiero ni diseño de rediseño; eso pertenece a motores posteriores de la lane estructural;
- no emite claims de ROI, ahorro, CAPEX o cierre de tesis;
- no materializa evidencia faltante ni pide intake local; sólo declara cuál sería la evidencia mínima necesaria para falsar o fortalecer el prior;
- no puede saltarse la degradación a `target_not_yet_structurally_modelable` cuando el target sigue clasificado como HQ, mailing address o objetivo ambiguo.

## why_it_exists
Existe como motor separado porque el framework necesitaba desacoplar la selección del prior estructural del resto de la lane analítica. Si `motor_037` a `motor_046` intentaran inferir el arquetipo al vuelo, mezclarían comparación, abstracción del sistema y framing económico con una hipótesis base no gobernada. `motor_039` impone esa disciplina: primero selecciona un arquetipo bounded, declara por qué fue elegido, explicita qué evidencia faltaría para falsarlo y sólo entonces deja que downstream razone sobre ese marco.
