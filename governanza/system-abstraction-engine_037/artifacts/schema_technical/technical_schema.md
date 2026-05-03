# Technical Schema — System Abstraction Engine

Motor ID: motor_037

## entities
- `SystemAbstractionStatement`
  Una afirmación estructural individual sobre una dimensión del activo.
- `SystemAbstractionBundle`
  Bundle completo de once dimensiones estructurales emitidas por el motor.
- `SystemAbstractionEvidenceStateSurface`
  Vista plana de dimensión a `evidence_state`.

## fields
- `SystemAbstractionStatement`
  `statement: str (required)` — formulación textual de la dimensión estructural.
  `evidence_state: str (required)` — uno de `OBSERVED_FACT`, `CONDITIONAL_HYPOTHESIS`, `ARCHETYPAL_PRIOR`, `NOT_OBSERVED`, `INADMISSIBLE_CLAIM`.
  `supporting_sources: list[str] (required)` — referencias a target definition, fields, datasets, source markers o arquetipo.
  `falsification_condition: str (required)` — condición que invalidaría el statement actual.
  `minimum_evidence_required: list[str] (required)` — evidencia mínima para fortalecer o sostener el statement.
- `SystemAbstractionBundle`
  `asset_type: SystemAbstractionStatement (required)`
  `business_function: SystemAbstractionStatement (required)`
  `value_creation_mechanism: SystemAbstractionStatement (required)`
  `dominant_process_type: SystemAbstractionStatement (required)`
  `dominant_physical_drivers: SystemAbstractionStatement (required)`
  `dominant_operational_drivers: SystemAbstractionStatement (required)`
  `control_structure: SystemAbstractionStatement (required)`
  `constraint_structure: SystemAbstractionStatement (required)`
  `economic_driver: SystemAbstractionStatement (required)`
  `regulatory_exposure: SystemAbstractionStatement (required)`
  `evidence_maturity: SystemAbstractionStatement (required)`
- `SystemAbstractionEvidenceStateSurface`
  `<dimension_name>: str (required)` — evidencia plana por dimensión.

## relationships
- `target_definition` y `archetype_resolution` determinan la semántica base de `SystemAbstractionBundle`.
- `asset_field_register`, `dataset_coverage_register` y `source_register` elevan o degradan `evidence_state` en dimensiones específicas.
- `SystemAbstractionBundle` se proyecta a `SystemAbstractionEvidenceStateSurface`.

## identifiers
- Identificador natural de `SystemAbstractionStatement`: nombre de dimensión dentro del bundle.
- Identificador natural de `SystemAbstractionBundle`: target definido por `target_name` + `target_type` + `jurisdiction_scope`.
- Identificador natural de `SystemAbstractionEvidenceStateSurface`: mismo target del bundle.

## versioning
- La versión efectiva del bundle depende de la versión del arquetipo seleccionado y de la cobertura pública observada.
- Un cambio de `selected_archetype_id`, `supported_field_register` o `dataset_coverage_register` implica nueva versión lógica.
- La superficie plana de `system_abstraction_evidence_states` debe regenerarse en cada nueva versión del bundle.

## lineage
- `asset_type` y target framing nacen de `target_definition`.
- `business_function` y drivers base nacen de `archetype_resolution` y `archetype_library_register`.
- `regulatory_exposure` y `evidence_maturity` trazan lineage a `dataset_coverage_register`, `source_register` y `canonical_asset_context_summary`.
- `control_structure` y drivers condicionales trazan lineage a `asset_field_register`.
