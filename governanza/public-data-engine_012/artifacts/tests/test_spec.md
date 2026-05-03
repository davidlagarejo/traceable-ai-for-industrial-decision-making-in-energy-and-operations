# Test Spec — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All placeholder markers have been replaced with concrete test content.
-->

## happy_path
Input mínimo válido:
- `library_objects`: dos registros estructurados de `motor_011`:
  - `lib_obj_facility_profile_v1` con `source_refs = ["src_100"]`, `version = "1.0.0"`, `curation_status = "eligible_for_reuse"`, `provenance = ["prov_lib_100"]`, `lineage_refs = ["lin_lib_100"]`, `facility_ref = "facility_alpha"`.
  - `lib_obj_utility_context_v1` con `source_refs = ["src_205"]`, `version = "1.0.0"`, `curation_status = "eligible_for_reuse"`, `provenance = ["prov_lib_205"]`, `lineage_refs = ["lin_lib_205"]`, `facility_ref = "facility_alpha"`.
- `source_registry`: snapshot `src_registry_snapshot_2026_04_01` with entries `src_100` and `src_205`, each carrying rights metadata, refresh metadata, `provenance_refs`, and `lineage_refs`.
- `quality_records`: `qr_100` targeting `lib_obj_facility_profile_v1` and `qr_205` targeting `lib_obj_utility_context_v1`, both with `fitness_status = "usable"`, evaluation provenance, and lineage.
- Packaging configuration: `prior_scope = "facility"`, `package_scope = "facility_alpha_phase1"`, `packaging_run_id = "pkg_run_012_0001"`, `eligibility_rule_version = "pde_rules_v1"`, `bundle_rule_version = "pde_bundle_v1"`, `packaging_rule_version = "pde_package_v1"`.

Expected output:
- One `FacilityPrior` with `produced_by_motor = "motor_012"`, `facility_ref = "facility_alpha"`, `prior_scope = "facility"`, `library_object_refs = ["lib_obj_facility_profile_v1", "lib_obj_utility_context_v1"]`, `source_refs = ["src_100", "src_205"]`, `quality_record_refs = ["qr_100", "qr_205"]`, non-empty `provenance_refs`, non-empty `lineage_refs`, non-empty `version_id`, and deterministic `version_hash`.
- At least one `ContextualBundle` with `facility_prior_ref` equal to the emitted `facility_prior_id`, `context_scope = "minimal_prior"` or another configured deterministic scope, source and quality references copied from the eligible members, and `bundle_fingerprint` derived from membership plus `bundle_rule_version`.
- One `Phase1Package` with `facility_prior_ref` equal to the emitted prior, `contextual_bundle_refs` matching the emitted bundle ids, `input_snapshot_refs.library_objects_snapshot`, `input_snapshot_refs.source_registry_snapshot`, and `input_snapshot_refs.quality_records_snapshot` populated, `validation_status = "accepted"`, `rejection_refs = []`, and no fields describing inference, TAD status, analytical conclusions, or decision-grade claims.

## sparse_case
Input:
- `library_objects`: one eligible record `lib_obj_facility_profile_v1` with required id, source refs, version, provenance, lineage, and `curation_status = "eligible_for_reuse"`.
- `source_registry`: snapshot `src_registry_snapshot_2026_04_01` containing only the referenced source `src_100`.
- `quality_records`: one usable record `qr_100` targeting `lib_obj_facility_profile_v1`.
- Optional context metadata such as source family label, utility profile, site group, display name, and previous `parent_id` is absent or null.

Expected behavior:
- The motor does not fail because optional descriptive context is missing.
- It emits one `FacilityPrior`, one minimal `ContextualBundle`, and one `Phase1Package`.
- The bundle uses `context_scope = "minimal_prior"` when no narrower deterministic context is available.
- Required collections and metadata remain present: `library_object_refs = ["lib_obj_facility_profile_v1"]`, `source_refs = ["src_100"]`, `quality_record_refs = ["qr_100"]`, `input_snapshot_refs` includes all three upstream snapshots, `parent_id = null` for first publication, and provenance and lineage arrays are non-empty.
- The package remains a Fase 1 handoff only; it does not synthesize missing context or create inferred facility attributes.

## malformed_input
Malformed input examples and required rejection:
- `library_objects` is a dict keyed by id instead of a list of structured records. The motor rejects before output emission with the structured validation message `library_objects must be a list of structured records` and does not emit `FacilityPrior`, `ContextualBundle`, or `Phase1Package`.
- A library object is missing `library_object_id`. The motor rejects that candidate with `INELIGIBLE_LIBRARY_OBJECT`, records the blocking rule for required library object identity, and prevents package acceptance when no other eligible object remains.
- `lib_obj_facility_profile_v1.source_refs = ["src_missing"]` while `source_registry` contains only `src_100`. The motor produces a `PackagingRejection` with `candidate_ref = "lib_obj_facility_profile_v1"`, `candidate_type = "library_object"`, `error_code = "UNRESOLVED_SOURCE_REF"`, `blocking_reference_refs = ["src_missing"]`, and the package is not emitted as accepted.
- `quality_records` contains `qr_unknown` with `target_ref = "lib_obj_not_in_snapshot"`. The motor rejects the record with `QUALITY_RECORD_TARGET_UNKNOWN` and does not silently retarget the quality record.
- Any input or candidate carrying fields such as `tad_status`, `inference_result`, `decision_grade`, or `conclusion_text` is rejected or excluded with `FORBIDDEN_INFERENCE_FIELD` because this motor only packages Fase 1 prior material.

## edge_cases
- Single eligible object boundary: when exactly one `LibraryObject` is eligible and all required source, quality, provenance, version, and lineage references resolve, the motor emits a valid prior, a minimal bundle, and a package instead of rejecting for low member count.
- Empty eligible input boundary: when `library_objects` is present but every item has `curation_status = "not_eligible_for_reuse"` or fails required eligibility, the motor emits `PackagingRejection` records with `INELIGIBLE_LIBRARY_OBJECT` and stops with `EMPTY_ELIGIBLE_INPUT`; it must not create an empty implied `FacilityPrior`.
- Extra registry entries boundary: when `source_registry` includes unused entries `src_777` and `src_888`, but eligible objects only reference `src_100`, the motor excludes unused entries from `FacilityPrior.source_refs`, `ContextualBundle.source_refs`, and `Phase1Package.source_refs` while preserving the registry snapshot reference.
- Multiple quality records boundary: when `qr_100_a` and `qr_100_b` both target `lib_obj_facility_profile_v1` in the same validated snapshot, the motor preserves both ids in `quality_record_refs` and does not merge them into a new quality score.
- Determinism boundary: two executions with identical input snapshots, rule versions, scopes, and `packaging_run_id` produce the same ordered membership, identifiers, rejection codes, and `version_hash` values.

## pass_criteria
A test passes only when all applicable observable conditions hold:
- Valid inputs produce exactly one accepted `Phase1Package` for the requested scope, one referenced `FacilityPrior`, and one or more referenced `ContextualBundle` records.
- Every emitted entity has its canonical id, matching `record_id`, `source_ref`, `produced_by_motor = "motor_012"`, `produced_at`, `version_id`, `version_hash`, `created_at`, `updated_at`, `parent_id`, non-empty `provenance_refs`, and non-empty `lineage_refs`.
- `FacilityPrior`, `ContextualBundle`, and `Phase1Package` preserve upstream identifiers from `motor_011`, `motor_008`, and `motor_007` without minting replacement ids for library objects, source entries, or quality records.
- All `source_refs` resolve against `source_registry_snapshot_ref`; all `quality_record_refs` target known validated objects or sources; all `contextual_bundle_refs` point to bundles whose `facility_prior_ref` matches the prior.
- Rejection scenarios produce structured `PackagingRejection` records using the expected error codes and blocking references.
- No emitted output contains inference claims, TAD objects, downstream activation decisions, generated evidence, recalculated quality, or mutated upstream curation/source metadata.

## fail_criteria
A test fails when any of these observable conditions appears:
- A valid input is rejected without a structured rejection code and blocking rule.
- Invalid input emits an accepted `Phase1Package`, a `FacilityPrior`, or a bundle without the required `PackagingRejection` records.
- Any required field from the technical schema is missing, null when required, typed incorrectly, or populated with an unresolved reference.
- The motor drops provenance, lineage, version, source registry snapshot, or quality references to simplify packaging.
- Outputs include raw unregistered sources, new source registry entries, changed upstream quality values, changed curation statuses, inferred facility attributes, TAD status, conclusions, recommendations, decision grades, or final reports.
- Re-running the same deterministic input changes object membership, identifiers, rejection codes, or `version_hash` values.
