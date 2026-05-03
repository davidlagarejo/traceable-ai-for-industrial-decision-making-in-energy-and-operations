# Operational Rules — Public Data Engine

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

## rules
1. The motor must only process inputs produced by approved upstream motors: `library_objects` from `motor_011`, `source_registry` from `motor_008`, and `quality_records` from `motor_007`.
2. Every source reference used by an emitted object must resolve to a source entry in the input `source_registry`.
3. Every library object included in a `FacilityPrior` or `ContextualBundle` must have eligible curation status, version metadata, provenance, and at least one quality reference.
4. Every emitted output must preserve upstream identifiers rather than replacing them with local aliases.
5. Packaging must be deterministic for the same input snapshot: identical inputs and package configuration produce identical membership, references, and validation outcomes.
6. Any unresolved reference, missing provenance, or ineligible upstream record must produce an explicit rejection or exclusion record; the motor must not repair the input silently.
7. Output must remain a Fase 1 handoff artifact and must not contain inference claims, TAD status, decision grade, or downstream activation decisions.

## invariants
- `lineage_id` is present on every emitted entity and links back to the validated input snapshot.
- `library_object_refs`, `source_refs`, and `quality_record_refs` are never null; if no eligible item exists, processing rejects instead of emitting an empty implied prior.
- Upstream object identifiers remain immutable inside all outputs.
- `package_version` and source registry snapshot references are stable for the emitted `Phase1Package`.
- The motor never changes upstream quality values, rights metadata, source metadata, or curation statuses.
- All exclusions and rejections are explicit, structured, and traceable to a validation rule.

## forbidden_operations
- Performing inference, scoring conclusions, producing recommendations, or converting prior material into decision-grade claims.
- Producing TADs, reports, inference cases, inference records, validation agendas, or verification outputs.
- Ingesting new raw data, scraping external sources, or creating new source registry entries.
- Recalculating quality, fitness, rights, freshness, duplicate status, or library curation decisions.
- Mutating upstream records to make them eligible for packaging.
- Dropping provenance, lineage, version, rights, or quality references to simplify the package.
