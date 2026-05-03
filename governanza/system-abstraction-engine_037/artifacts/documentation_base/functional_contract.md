# Functional Contract — System Abstraction Engine

Motor ID: motor_037

## inputs
- `target_definition`
  Tipo: `dict`
  Productor: `motor_012.facility_prior.target_definition`, con fallback a `motor_007.target_definition_contract`
  Contenido mínimo: `target_type`, `target_name`, `jurisdiction_scope`.
- `canonical_asset_context_summary`
  Tipo: `dict`
  Productor: `motor_012`
  Contenido mínimo: `screening_supported` y `supported_field_register`.
- `asset_field_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: detectar evidencia observada de proceso, control, drivers y topología.
- `dataset_coverage_register`
  Tipo: `list[dict]`
  Productor: `motor_012`
  Uso: activar exposición regulatoria o madurez de evidencia cuando coverage pública es suficiente.
- `source_register`
  Tipo: `list[dict]`
  Productor: `motor_028`
  Uso: reforzar señales de observación regulatoria o routing público efectivo.
- `archetype_resolution`
  Tipo: `dict`
  Productor: `motor_039`
  Contenido mínimo: `selected_archetype_id`, `selected_archetype_label`, `resolver_state`.
- `archetype_library_register`
  Tipo: `list[dict]`
  Productor: `motor_039`
  Uso: extraer business function, control structure, dominant drivers y evidencia mínima del arquetipo seleccionado.

## outputs
- `system_abstraction`
  Tipo: `dict[str, dict]`
  Consumidores: `motor_038`, `motor_040`, benchmarking, framing
  Contenido: bundle de statements por dimensión estructural con `statement`, `evidence_state`, `evidence_basis`, `what_changes_it` y `minimum_evidence_required`.
- `system_abstraction_fields`
  Tipo: `list[str]`
  Consumidores: auditoría, packaging técnico
  Contenido: nombres ordenados de las dimensiones emitidas.
- `system_abstraction_evidence_states`
  Tipo: `dict[str, str]`
  Consumidores: validadores y downstream
  Contenido: mapa plano de dimensión a `evidence_state`.

## limits
- no acepta que un prior arquetipal sea presentado como `OBSERVED_FACT` sin soporte admisible;
- no produce statements fuera del vocabulario gobernado de abstracción de sistema;
- nunca reemplaza un target inadmisible por una abstracción “genérica” operativa;
- no emite dominancia cuantitativa, peer rank ni rediseño;
- no modifica ni reinterpreta la selección de arquetipo fuera de la evidencia disponible.

## validations
- debe existir un `target_type` resoluble para producir abstracción válida;
- si `selected_archetype_id=target_not_yet_structurally_modelable`, todas las dimensiones deben degradarse a `INADMISSIBLE_CLAIM`;
- `regulatory_exposure` sólo puede ser `OBSERVED_FACT` cuando coverage o source markers sustentan la observación;
- `control_structure` sólo puede subir a `OBSERVED_FACT` con evidencia de owner control, tenant metering, lease responsibility o metering topology;
- `evidence_maturity` debe reflejar si screening público soporta framing estructural o si el estado sigue siendo arquetipal.
