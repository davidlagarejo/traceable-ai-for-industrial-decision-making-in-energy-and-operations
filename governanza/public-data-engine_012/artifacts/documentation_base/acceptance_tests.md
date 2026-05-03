# Acceptance Tests — Public Data Engine

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

## happy_path
Input: `library_objects` contains `lib_obj_facility_profile_v1` and `lib_obj_utility_context_v1`, both with eligible curation status, source refs `src_100` and `src_205`, provenance, and version `1.0.0`; `source_registry` contains `src_100` and `src_205` with active rights metadata; `quality_records` contains `qr_100` for `lib_obj_facility_profile_v1` and `qr_205` for `lib_obj_utility_context_v1`. Action: the motor validates references, groups the eligible objects under `facility_ref = facility_alpha`, and emits the Fase 1 handoff. Expected output: one `FacilityPrior` referencing both library objects, at least one `ContextualBundle` with the same source and quality references, and one `Phase1Package` containing the prior, bundle refs, package version, generated timestamp, and lineage back to the three input snapshots.

## edge_cases
- Single eligible library object: when only one library object passes upstream eligibility and all references resolve, the motor emits a valid `FacilityPrior`, one minimal `ContextualBundle`, and a `Phase1Package` with one object reference rather than rejecting for low volume.
- Multiple quality records for one object: when a library object has several quality records from the same input snapshot, the motor preserves all relevant `quality_record_refs` and does not collapse them into a new quality score.
- Source registry contains extra unused sources: when the registry snapshot includes sources not referenced by eligible library objects, the motor leaves them unused and does not add them to bundles.
- Bundle scope is sparse: when context metadata is minimal but required identifiers, source refs, quality refs, provenance, and versions are present, the motor emits a bundle with `context_scope = minimal_prior` and explicit lineage.

## rejection_criteria
- Reject with `UNRESOLVED_SOURCE_REF` when any included library object references a `source_id` absent from `source_registry`.
- Reject with `MISSING_PROVENANCE` when a library object, source registry snapshot, or quality record lacks provenance or lineage metadata required for rebuild.
- Reject with `INELIGIBLE_LIBRARY_OBJECT` when all provided library objects have curation status that disallows reuse in a Fase 1 prior.
- Reject with `QUALITY_RECORD_TARGET_UNKNOWN` when a quality record points to an object or source not present in the validated input snapshot.
