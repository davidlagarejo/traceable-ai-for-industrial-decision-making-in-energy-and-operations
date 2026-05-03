# Conceptual Schema — System Abstraction Engine

Motor ID: motor_037

## entities
- `SystemAbstractionStatement`: una afirmación estructural individual con base epistemológica explícita.
- `SystemAbstractionBundle`: colección completa de statements emitidos para un activo.
- `RegulatoryObservation`: observación derivada de datasets, jurisdicción y source markers sobre exposición regulatoria.
- `EvidenceStateSurface`: vista plana que resume el `evidence_state` de cada dimensión.

## relationships
- `target_definition` + `archetype_resolution` + `archetype_library_register` → `SystemAbstractionBundle`
- `asset_field_register` + `dataset_coverage_register` + `source_register` → `RegulatoryObservation`
- `SystemAbstractionBundle` → `EvidenceStateSurface`

## key_fields
- `SystemAbstractionStatement`: `statement`, `evidence_state`, `evidence_basis`, `what_changes_it`, `minimum_evidence_required`
- `SystemAbstractionBundle`: `asset_type`, `business_function`, `value_creation_mechanism`, `dominant_process_type`, `dominant_physical_drivers`, `dominant_operational_drivers`, `control_structure`, `constraint_structure`, `economic_driver`, `regulatory_exposure`, `evidence_maturity`
- `RegulatoryObservation`: `statement`, `evidence_state`, `evidence_basis`
- `EvidenceStateSurface`: claves de dimensión y valor `evidence_state`
