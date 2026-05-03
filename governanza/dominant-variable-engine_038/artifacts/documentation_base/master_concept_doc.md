# Master Concept Document — Dominant Variable Engine

Motor ID: motor_038

## purpose
Dominant Variable Engine convierte la abstracción estructural y las hipótesis arquetipales en un registro gobernado de variables candidatas dominantes. Su trabajo es decidir qué variables merecen ser tratadas como hechos observados, hipótesis condicionales o simples priors arquetipales antes de que benchmarking, conflicto, framing o rediseño empiecen a operar sobre ellas. No resuelve todavía la tesis final; fija la capa de variables que downstream puede usar sin confundir una intuición estructural con evidencia admisible.

## what_it_does
- toma `target_definition`, `system_abstraction`, `dominant_variable_hypotheses`, `asset_field_register` y `dataset_coverage_register`;
- promueve o degrada el `evidence_state` de cada variable candidata según señales observadas de utility bills, EUI, metering, HVAC topology, throughput, process flow o coverage regulatoria;
- genera `dominant_variable_register` con `variable`, `layer`, `dominance`, `evidence_state`, `why_it_could_matter`, confirmaciones, falsaciones e impactos de decisión;
- asegura la presencia de `owner_control_boundary` aunque no venga explícita desde `motor_039`;
- expone conteos útiles para downstream sobre volumen total y variables que ya están en estado observado o condicional.

## what_it_does_not_do
- no selecciona peers ni construye fairness final;
- no traduce variables a correlaciones, contradicciones, finanzas o claims ejecutivos finales;
- no convierte un prior arquetipal en hecho observado sin soporte en fields o coverage;
- no modifica la abstracción estructural base ni reescribe el arquetipo seleccionado;
- no calcula benchmarks ni comparabilidad todavía.

## why_it_exists
Existe como motor separado porque la lane estructural necesitaba una frontera entre “cómo se abstrae el sistema” y “qué variables realmente dominan o podrían dominar”. `motor_037` habla de statements estructurales; `motor_038` convierte eso en un vocabulario de variables defendibles para las capas analíticas posteriores. Sin esta capa, los motores siguientes trabajarían con hipótesis sueltas sin una disciplina clara de promoción epistemológica.
