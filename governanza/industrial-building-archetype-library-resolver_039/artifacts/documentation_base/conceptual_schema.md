# Conceptual Schema — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## entities
- `TargetDefinition`
  Definición normalizada del target físico o del objetivo todavía no resoluble. Incluye `target_type`, `target_name` y `jurisdiction_scope`.
- `TargetClassificationObject`
  Clasificación operacional upstream que decide si el target admite modelado estructural o debe degradarse.
- `ArchetypeResolution`
  Resultado central del motor: arquetipo elegido, confianza, estado del resolver, por qué fue elegido y bajo qué evidencia-state.
- `ArchetypeDefinitionSnapshot`
  Snapshot serializado del arquetipo de la librería con su función de negocio, drivers, constraints, riesgos y métricas relevantes.
- `ArchetypeSelectionBasis`
  Registro de bases observadas que justifican la selección, con dimensión, valor, fuente y evidence state.
- `DominantVariableHypothesis`
  Hipótesis estructural de variable dominante que downstream debe confirmar o falsar.
- `SystemAbstractionSeed`
  Mapa de campos estructurales empaquetados como evidencia bound para arrancar el modelado abstracto.
- `AntiHallucinationContract`
  Contrato explícito que gobierna cómo puede usarse el prior y qué usos quedan prohibidos.

## relationships
- `TargetDefinition` + `TargetClassificationObject` + señales de `asset_field_register` -> `ArchetypeResolution`
- `dataset_coverage_register` + `source_register` -> enriquecen `ArchetypeSelectionBasis` y ayudan a decidir si sólo hay fallback genérico o una selección más acotada
- `ArchetypeResolution.selected_archetype_id` -> selecciona exactamente un `ArchetypeDefinitionSnapshot` de la librería
- `ArchetypeDefinitionSnapshot` -> genera cero o muchas `DominantVariableHypothesis`
- `ArchetypeDefinitionSnapshot` -> genera exactamente un `archetype_minimum_evidence_register`
- `ArchetypeDefinitionSnapshot` + `ArchetypeResolution` -> producen un único `SystemAbstractionSeed`
- `ArchetypeResolution.archetype_evidence_state` -> gobierna el `AntiHallucinationContract` y sus usos permitidos/prohibidos
- el adapter aplana parte de `ArchetypeResolution` y del conteo de hipótesis a señales simples para el runtime general

## key_fields
- `TargetDefinition`
  - `target_type: str`
  - `target_name: str`
  - `jurisdiction_scope: list[str]`
- `TargetClassificationObject`
  - `target_type: str`
  - `classification_confidence: str`
- `ArchetypeResolution`
  - `selected_archetype_id: str`
  - `label: str`
  - `match_confidence: str`
  - `resolver_state: str`
  - `archetype_evidence_state: str`
  - `why_selected: str`
  - `selection_basis_register: list[dict]`
- `ArchetypeDefinitionSnapshot`
  - `asset_type: str`
  - `business_function: str`
  - `value_creation_mechanism: str`
  - `dominant_process_type: str`
  - `dominant_physical_drivers: list[str]`
  - `dominant_operational_drivers: list[str]`
  - `minimum_evidence_required: list[str]`
- `ArchetypeSelectionBasis`
  - `dimension: str`
  - `value: str`
  - `evidence_state: str`
  - `source: str`
- `DominantVariableHypothesis`
  - `variable: str`
  - `layer: str`
  - `dominance: str`
  - `evidence_state: str`
  - `why_it_could_matter: str`
  - `what_confirms_it: list[str]`
  - `what_falsifies_it: list[str]`
  - `decision_impact: list[str]`
- `SystemAbstractionSeed`
  - `asset_type: dict`
  - `business_function: dict`
  - `value_creation_mechanism: dict`
  - `dominant_process_type: dict`
  - `dominant_physical_drivers: dict`
  - `dominant_operational_drivers: dict`
  - `control_structure: dict`
  - `constraint_structure: dict`
  - `economic_driver: dict`
  - `regulatory_exposure: dict`
  - `evidence_maturity: dict`
- `AntiHallucinationContract`
  - `selected_archetype_evidence_state: str`
  - `rule: str`
  - `allowed_use: list[str]`
  - `prohibited_use: list[str]`
