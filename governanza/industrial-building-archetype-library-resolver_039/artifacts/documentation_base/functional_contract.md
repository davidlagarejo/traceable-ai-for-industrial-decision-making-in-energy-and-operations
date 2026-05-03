# Functional Contract — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## inputs
- `__pipeline__`
  Tipo: `dict`
  Productor: runtime orchestration
  Uso: sólo como fallback para `derive_target_definition` si `motor_012.facility_prior.target_definition` y `motor_007.target_definition_contract` no alcanzan.
- `motor_007.target_definition_contract`
  Tipo: `dict`
  Productor: `motor_007`
  Contenido mínimo esperado: `target_type`, `target_name` o `target_label`, `jurisdiction_scope`.
- `motor_007.target_classification_object`
  Tipo: `dict`
  Productor: `motor_007`
  Contenido mínimo esperado: `target_type` de clasificación operacional y `classification_confidence`.
- `motor_012.facility_prior`
  Tipo: `dict`
  Productor: `motor_012`
  Uso: fuente preferida de `target_definition` y de nombre contextual del activo.
- `motor_012.asset_field_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: señales observadas de tamaño, proceso, equipos, operating schedule y otros hints bounded para activar arquetipos específicos.
- `motor_012.dataset_coverage_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: registrar datasets aceptados que refuerzan la lectura contextual del activo.
- `motor_028.source_register`
  Tipo: `list[dict]`
  Productor: `motor_028`
  Uso: leer familias de fuente, tipos y títulos aceptados para reforzar selección genérica o jurisdiccional.

## outputs
- `archetype_resolution`
  Tipo: `dict`
  Consumidores: `motor_037` a `motor_046`, auditoría
  Contenido: `selected_archetype_id`, `label`, `match_confidence`, `resolver_state`, `archetype_evidence_state`, `why_selected`, `selection_basis_register`.
- `archetype_library_register`
  Tipo: `list[dict]`
  Consumidores: motores estructurales downstream
  Contenido: snapshot serializado del `ArchetypeDefinition` elegido.
- `archetype_selection_basis_register`
  Tipo: `list[dict]`
  Consumidores: auditoría, framing estructural
  Contenido: bases observadas de selección como `target_type`, `target_classification`, `jurisdiction_scope` y señales específicas.
- `dominant_variable_hypotheses`
  Tipo: `list[dict]`
  Consumidores: `motor_037`, `motor_038`, `motor_040`, `motor_042`, `motor_043`
  Contenido: variables dominantes hipotéticas con `why_it_could_matter`, `what_confirms_it`, `what_falsifies_it` y `decision_impact`.
- `archetype_minimum_evidence_register`
  Tipo: `list[str]`
  Consumidores: intake estructural, diseño de evidencia
  Contenido: evidencia mínima requerida para confirmar, corregir o falsar el prior.
- `system_abstraction_seed`
  Tipo: `dict`
  Consumidores: `motor_037`
  Contenido: campos estructurales falsables empaquetados como `EvidenceBoundField`.
- `anti_hallucination_contract`
  Tipo: `dict`
  Consumidores: reporting, validadores, packaging
  Contenido: `selected_archetype_evidence_state`, regla de uso permitido y usos prohibidos.
- señales derivadas planas
  Tipo: escalares
  Consumidores: dashboard y runtime general
  Contenido: `selected_archetype_id`, `selected_archetype_label`, `match_confidence`, `resolver_state`, `dominant_variable_count`.

## limits
- no acepta convertir clasificación no operativa en modelado estructural fuerte por mera narrativa del usuario;
- no acepta hints textuales como prueba de performance local ni como sustituto de evidencia asset-level;
- nunca produce hechos observados sobre el activo a partir del arquetipo; sólo priors estructurales falsables;
- nunca produce comparables, benchmarking numérico, ahorro, ROI, rediseño técnico o decisión final;
- nunca selecciona un arquetipo fuera de la librería estructural cerrada definida en `archetype_library.py`;
- nunca emite `selected_archetype_evidence_state=OBSERVED_FACT`; los arquetipos seleccionados salen como `ARCHETYPAL_PRIOR` o, si no modela aún, `INADMISSIBLE_CLAIM`.

## validations
- la resolución del `target_definition` debe seguir el orden: `facility_prior.target_definition` -> `motor_007.target_definition_contract` -> `derive_target_definition(__pipeline__)`;
- `target_classification_object.target_type` debe ser capaz de distinguir targets no operativos o ambiguos para forzar la degradación correcta;
- `asset_field_register`, `dataset_coverage_register` y `source_register` deben llegar como registros listables; si faltan, el motor sólo puede caer a un fallback más débil, no inventar soporte;
- toda selección específica de arquetipo debe venir acompañada por una `selection_basis_register` coherente con señales observables;
- si el arquetipo final es `target_not_yet_structurally_modelable`, `dominant_variable_count` debe ser `0` y `selected_archetype_evidence_state` debe salir como `INADMISSIBLE_CLAIM`;
- si el arquetipo final es modelable, `dominant_variable_count` debe igualar el largo de `dominant_variable_hypotheses` y el contrato anti-hallucination debe seguir prohibiendo cierre de decisión.
