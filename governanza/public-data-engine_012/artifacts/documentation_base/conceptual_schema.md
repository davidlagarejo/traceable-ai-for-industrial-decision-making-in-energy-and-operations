# Conceptual Schema — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All placeholder markers have been replaced with concrete content.
-->

## entities
- `FacilityPrior`: materialized Fase 1 prior for a facility or operational context, composed from eligible library objects, source registry references, and quality snapshots.
- `ContextualBundle`: scoped grouping of library objects, source references, and quality records prepared for downstream case activation without adding inference.
- `Phase1Package`: complete handoff artifact that contains the facility prior, contextual bundles, input snapshot references, package metadata, and rebuild lineage.

## relationships
- `Phase1Package` -> `FacilityPrior` (contains exactly one prior snapshot for the packaged Fase 1 handoff).
- `Phase1Package` -> `ContextualBundle` (contains one or more contextual bundles produced from the same validated input snapshot).
- `FacilityPrior` -> `ContextualBundle` (each bundle is derived from and references the prior it contextualizes).
- `ContextualBundle` -> `LibraryObject` (each bundle references one or more eligible library objects from `motor_011`).
- `ContextualBundle` -> `SourceRegistrySnapshot` (each source reference used by bundled objects must resolve in the source registry from `motor_008`).
- `ContextualBundle` -> `QualityRecord` (each included object or source must carry the relevant quality references from `motor_007`).

## key_fields
`FacilityPrior`
- `facility_prior_id`: `string`
- `facility_ref`: `string`
- `library_object_refs`: `list[string]`
- `source_registry_snapshot_ref`: `string`
- `quality_record_refs`: `list[string]`
- `lineage_id`: `string`

`ContextualBundle`
- `bundle_id`: `string`
- `facility_prior_ref`: `string`
- `context_scope`: `string`
- `library_object_refs`: `list[string]`
- `source_refs`: `list[string]`
- `quality_record_refs`: `list[string]`

`Phase1Package`
- `package_id`: `string`
- `package_version`: `string`
- `generated_at`: `datetime`
- `facility_prior_ref`: `string`
- `contextual_bundle_refs`: `list[string]`
- `input_snapshot_refs`: `dict[string, string]`
