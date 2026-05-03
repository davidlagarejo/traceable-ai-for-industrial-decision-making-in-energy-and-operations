# Master Concept Document — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All open placeholders in this file have been resolved with concrete documentation.
-->

## purpose
The Library Curation Engine converts objects that are already structured, identity-reviewed, duplicate-controlled and quality-evaluated into reusable library assets for the framework. It does not discover or evaluate raw data; it decides which upstream objects are eligible for library use, preserves the evidence that makes them eligible and packages them into stable library objects, bundles and versions. Its output is a governed knowledge layer that downstream phases can reuse without rebuilding local ad hoc libraries.

## what_it_does
- Receives `quality_records` from `motor_007` and uses their evaluation status, scores, flags and disqualification reasons as eligibility evidence.
- Receives `identity_records` from `motor_006` and preserves the resolved or explicitly open identity state for every candidate object.
- Receives `dedup_records` from `motor_010` and uses duplicate clusters and deduplication recommendations to avoid repeated library entries.
- Selects only objects whose quality, identity and duplicate-control evidence meet the declared curation policy for the run.
- Creates `LibraryObject` records that reference the upstream object, quality record, identity record, duplicate evidence, provenance, lineage and rule version.
- Groups related `LibraryObject` records into `CuratedBundle` outputs for a declared scope such as phase, domain, facility class or downstream consumer.
- Emits `LibraryVersion` records whenever a library object or bundle is published, superseded or rebuilt under a new rule version.
- Records rejected candidate references with structured reasons so downstream consumers can distinguish absence from explicit ineligibility.

## what_it_does_not_do
- It does not ingest new data, fetch sources, parse raw files or call source discovery workflows.
- It does not evaluate quality, calculate fitness scores or override `quality_records`; those responsibilities belong to `motor_007`.
- It does not resolve entity identity, merge entity clusters or close identity ambiguity; those responsibilities belong to `motor_006`.
- It does not detect duplicates or compute similarity scores; it only consumes duplicate-control evidence produced by `motor_010`.
- It does not normalize records, create canonical entities, change taxonomies or repair upstream fields.
- It does not produce analytic claims, field evidence, inference records, reports or phase approval decisions.
- It does not delete, overwrite, rewrite or silently mutate upstream objects.

## why_it_exists
Library curation is a separate motor because reusable framework libraries require the completed Phase 1 evidence chain: normalization, identity resolution, quality evaluation and duplicate control must already exist before a library asset can be trusted. Without this motor, each downstream phase would assemble its own local pseudo-library, causing drift, repeated selection logic, inconsistent provenance and loss of versioned reuse.
