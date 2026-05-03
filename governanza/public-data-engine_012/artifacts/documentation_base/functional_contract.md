# Functional Contract — Public Data Engine

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

## inputs
- `library_objects`: `list[LibraryObject]` as structured records with `library_object_id`, `source_refs`, `version`, `provenance`, and `curation_status` — produced by `motor_011`.
- `source_registry`: `SourceRegistrySnapshot` as structured registry entries with `source_id`, rights metadata, refresh metadata, and source lineage — produced by `motor_008`.
- `quality_records`: `list[QualityRecord]` as structured evaluation records with `quality_record_id`, `target_ref`, `fitness_status`, `score_or_grade`, and evaluation provenance — produced by `motor_007`.

## outputs
- `facility_prior`: `FacilityPrior` structured object — consumed by `motor_013` and later Fase 2 activation workflows as the authorized prior from Fase 1.
- `contextual_bundle`: `list[ContextualBundle]` structured objects — consumed by `motor_013` as contextual packets grouped around facility, domain, source family, or operational scope.
- `phase1_package`: `Phase1Package` structured package — retained as the complete handoff artifact for Fase 2, audit, rebuild, and conformance review.

## limits
- Never accepts raw unregistered sources, free-text evidence dumps, uncatalogued files, or records without upstream provenance.
- Never accepts `library_objects` whose `curation_status` is not eligible for reuse or whose required source references are missing from `source_registry`.
- Never accepts `quality_records` that do not point to a known library object, source, or bundle candidate.
- Never produces TADs, inference records, analytical conclusions, validation agendas, or final reports.
- Never creates new evidence, new source registrations, new quality judgments, new duplicate decisions, or new library curation decisions.
- Only packages the Fase 1 prior and its contextual bundles; any downstream activation or inference belongs to later motors.

## validations
- Reject input when any required collection is absent, empty where a non-empty handoff is required, or not represented as structured records.
- Reject each `LibraryObject` missing `library_object_id`, `source_refs`, `version`, `provenance`, or eligible `curation_status`.
- Reject any `source_ref` in a library object when the referenced `source_id` is absent from `source_registry`.
- Reject any `QualityRecord` missing `quality_record_id`, `target_ref`, `fitness_status`, or evaluation provenance.
- Before emitting output, verify that every `FacilityPrior`, `ContextualBundle`, and `Phase1Package` has stable identifiers, source references, quality references, version fields, generated timestamp, and lineage metadata.
- Before emitting output, verify that no output field asserts a conclusion, TAD, inference status, or decision-grade claim.
