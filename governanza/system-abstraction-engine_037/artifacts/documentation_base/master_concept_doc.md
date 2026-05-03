# Master Concept Document — System Abstraction Engine

Motor ID: motor_037

## purpose
System Abstraction Engine convierte un target ya bounded y un arquetipo estructural seleccionado en una capa explícita de abstracción de sistema. Su responsabilidad es producir afirmaciones gobernadas sobre tipo de activo, función de negocio, mecanismo de valor, proceso dominante, drivers físicos y operativos, estructura de control, restricciones, economía y exposición regulatoria, siempre con `evidence_state` explícito. No cierra hipótesis de desempeño; fija el mapa conceptual mínimo desde el cual `motor_038` y los motores estructurales posteriores pueden razonar sin confundir hechos observados con priors o hipótesis condicionales.

## what_it_does
- toma `target_definition`, resumen canónico de screening, coverage pública, registros de campos observados y el `archetype_resolution` producido por `motor_039`;
- decide para cada statement si la base admisible es `OBSERVED_FACT`, `CONDITIONAL_HYPOTHESIS`, `ARCHETYPAL_PRIOR`, `NOT_OBSERVED` o `INADMISSIBLE_CLAIM`;
- materializa `system_abstraction` como un bundle de statements versionables para `asset_type`, `business_function`, `value_creation_mechanism`, `dominant_process_type`, `dominant_physical_drivers`, `dominant_operational_drivers`, `control_structure`, `constraint_structure`, `economic_driver`, `regulatory_exposure` y `evidence_maturity`;
- expone superficies derivadas simples para downstream: `system_abstraction_fields` y `system_abstraction_evidence_states`;
- degrada todo el bundle a inadmisible cuando el target todavía no es un activo físico operacional bounded.

## what_it_does_not_do
- no selecciona variables dominantes finales ni arma peer logic; eso pertenece a `motor_038` y posteriores;
- no convierte un prior arquetipal en verdad observada sin soporte explícito en registros de campo, datasets o fuentes;
- no calcula benchmarks, conflictos inter-capa, framing competitivo, finanzas ni rediseño;
- no emite recomendaciones ejecutivas ni claims de ahorro, CAPEX o ROI;
- no corrige clasificación upstream: si el target sigue inadmisible, lo refleja; no lo “arregla” narrativamente.

## why_it_exists
Existe como motor separado porque el framework necesitaba una frontera entre resolver arquetipos y empezar a razonar sobre variables o comparaciones. `motor_039` dice qué prior estructural es plausible; `motor_037` traduce ese prior y la evidencia disponible en statements auditables con jerarquía epistemológica explícita. Sin esta capa, downstream mezclaría regulaciones observadas, clues operativos y supuestos arquetipales en una misma superficie opaca.
