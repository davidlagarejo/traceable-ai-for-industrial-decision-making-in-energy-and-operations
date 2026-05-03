# Master Concept Document — Global Public Data Routing Engine

Motor ID: motor_035

## purpose
Global Public Data Routing Engine decide qué fuentes públicas son obligatorias, prioritarias, opcionales o inadmisibles para un caso antes de que el discovery runtime empiece a buscar. Toma la definición del sujeto y del target ya acotadas upstream, la clasificación del caso y el nivel de readiness técnico, y las convierte en un contrato operativo de routing público. Su trabajo no es traer evidencia ni validarla, sino fijar el mapa de búsqueda permitido para que el sistema no trate igual un activo operativo acotado, una sede corporativa o un caso todavía mal delimitado.

## what_it_does
- consume `subject_definition_contract`, `target_definition_contract` y `target_classification_object` desde los contratos ya gobernados del caso;
- resuelve la clase jurisdiccional US relevante para routing técnico y arma el `regulatory_stack` mínimo aplicable;
- clasifica si el target puede tratarse como activo operativo técnicamente enrutable o si debe degradarse a un brief de clasificación;
- construye `source_routing_plan` con `mandatory_sources`, `high_priority_sources`, `optional_sources` y `disallowed_substitutions`;
- deriva un `critical_field_summary` para hacer explícitos los campos mínimos faltantes antes de confiar en scraping o benchmarking técnico;
- recomienda el cambio de superficie de reporte vía `report_type_switch_recommendation` cuando el caso no soporta un reporte técnico fuerte;
- emite señales de conveniencia para downstream como `routing_ready`, `asset_type`, `decision_type`, `jurisdiction_class` y listas ya aplanadas de fuentes.

## what_it_does_not_do
- no ejecuta búsqueda web ni scraping; eso pertenece a `motor_028`;
- no materializa datasets públicos ni combina registros; eso pertenece a `motor_012`;
- no resuelve verdad del activo por sí solo ni mejora autoridad epistemológica de inputs declarados;
- no crea intake local ni hace binding de evidencia local; eso pertenece a `motor_049`;
- no decide tesis, comparables, pérdida, finanzas ni packaging del reporte;
- no permite que un benchmark genérico sustituya fuentes locales obligatorias cuando el contrato de routing lo prohíbe.

## why_it_exists
Existe como motor separado porque el framework necesitaba una capa que transformara clasificación + jurisdicción + readiness en reglas de búsqueda pública auditable antes de tocar discovery. Sin esta capa, `motor_028` tendría que inferir desde cero qué buscar, con alto riesgo de mezclar headquarters con activos operativos, usar sustituciones inadmisibles o pedir reportes técnicos sobre casos que todavía sólo admiten clasificación. `motor_035` impone disciplina previa: primero define el routing permitido y recién después el runtime público ejecuta ese plan.
