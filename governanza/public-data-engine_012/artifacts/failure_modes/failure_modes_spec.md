# Failure Modes Spec — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All failure-mode placeholders have been replaced with concrete operational content.
-->

## failure_modes_list
- `UNRESOLVED_SOURCE_REF_CHAIN`: a `LibraryObject.source_refs[]`, `ContextualBundle.source_refs[]`, or aggregate `Phase1Package.source_refs[]` value is absent from the declared `source_registry_snapshot_ref` -> output validation reports unresolved references, package acceptance becomes unsafe, and downstream Fase 2 cannot reconstruct the source basis -> stop package acceptance, emit `PackagingRejection` with `error_code = "UNRESOLVED_SOURCE_REF"`, include the missing source ids in `blocking_reference_refs`, and require a corrected upstream source registry snapshot or corrected library object before rerun.
- `QUALITY_RECORD_TARGET_DRIFT`: a `QualityRecord.target_ref` points to a library object, source, or bundle candidate outside the validated input snapshot -> quality metadata cannot be attached deterministically and may be retargeted by mistake -> reject the quality record with `QUALITY_RECORD_TARGET_UNKNOWN`, leave upstream quality values unchanged, and rerun only after the producing quality stage emits a record targeting a known object or source.
- `PROVENANCE_LINEAGE_GAP`: any included library object, source registry entry, quality record, prior, bundle, package, or rejection lacks required provenance, lineage, version, or snapshot metadata -> the same `FacilityPrior`, `ContextualBundle`, or `Phase1Package` cannot be rebuilt from declared inputs -> block accepted output, emit `PackagingRejection` using `MISSING_PROVENANCE` when the failing candidate is an upstream item, and require upstream metadata repair rather than local reconstruction.
- `INELIGIBLE_OBJECT_LEAKAGE`: a library object with a curation status outside the allowed reuse set appears in `FacilityPrior.library_object_refs[]` or `ContextualBundle.library_object_refs[]` -> Fase 2 receives material that was not authorized by the curation pipeline -> exclude the candidate with `INELIGIBLE_LIBRARY_OBJECT`, keep an explicit rejection reference, and fail with `EMPTY_ELIGIBLE_INPUT` if no eligible objects remain.
- `FORBIDDEN_INFERENCE_PAYLOAD`: input or output carries fields such as `tad_status`, `inference_result`, `decision_grade`, `recommendation`, `conclusion_text`, or equivalent decision language -> motor_012 has crossed from deterministic Fase 1 packaging into inference or reporting responsibility -> reject or exclude the candidate with `FORBIDDEN_INFERENCE_FIELD`, remove no fields silently, and route any required inference work to downstream motors.
- `NONDETERMINISTIC_BUNDLE_MEMBERSHIP`: identical input snapshots, rule versions, scopes, and `packaging_run_id` produce different ordering, identifiers, bundle membership, rejection codes, or `version_hash` values across runs -> audits and downstream activation cannot compare packages reliably -> sort and hash membership from stable identifiers only, pin `eligibility_rule_version`, `bundle_rule_version`, and `packaging_rule_version`, and rerun after eliminating timestamp-only, process-order, or dictionary-order dependencies.
- `EMPTY_ELIGIBLE_INPUT_ACCEPTED`: every library object is absent, malformed, or ineligible, but the engine emits an accepted empty prior or empty package -> downstream stages treat absence of reusable Fase 1 material as a valid prior -> emit candidate-level rejections and a blocking empty-input validation result, do not emit accepted `FacilityPrior` or accepted `Phase1Package`, and require upstream curation correction or an explicit no-package outcome.

## anti_patterns
- Treating Public Data Engine as a repair layer for upstream source, quality, curation, deduplication, or provenance defects. The motor must reject or record failures; it must not fix source registries, quality targets, or curation status locally.
- Coupling package assembly directly to downstream `motor_013` activation needs, TAD fields, inference schemas, or report language. The output contract is the Fase 1 prior package, not a pre-activation inference case.
- Recomputing quality, freshness, rights, duplicate status, facility attributes, or confidence scores while packaging. Those decisions belong to upstream engines and must only be preserved as references.
- Dropping unresolved, sparse, or malformed candidates without a `PackagingRejection`. Silent exclusion destroys auditability and makes package membership impossible to explain.
- Minting replacement identifiers for upstream library objects, source entries, or quality records. The motor may mint package, prior, bundle, and rejection ids, but upstream ids must remain intact.
- Building identifiers or version hashes from mutable display labels, current list position, local file order, or emission timestamp alone. Determinism requires stable input ids, snapshot refs, rule versions, scope, and lineage fields.
- Collapsing `FacilityPrior`, `ContextualBundle`, `Phase1Package`, and `PackagingRejection` into one monolithic untyped payload. The four entities have different review, lineage, and validation responsibilities.
- Allowing manual override fields to mark a rejected package as accepted without a corresponding upstream correction, explicit rejection record, and changed version lineage.

## degradation_signals
- Increase in `PackagingRejection.error_code = "UNRESOLVED_SOURCE_REF"` per package run, especially when concentrated in one source registry snapshot or source family.
- Any accepted package where `provenance_refs`, `lineage_refs`, `input_snapshot_refs`, `source_registry_snapshot_ref`, `version_id`, or `version_hash` is null, empty, or inconsistent between contained entities.
- Repeated package runs with identical snapshot refs and rule versions producing different `facility_prior_id`, `bundle_id`, `package_id`, `bundle_fingerprint`, rejection refs, or `version_hash` values.
- Log entries showing candidates skipped, normalized, corrected, coerced, or retargeted without a matching `PackagingRejection.packaging_rejection_id`.
- Presence of forbidden vocabulary or fields in accepted outputs, including `TAD`, `tad_status`, `inference`, `conclusion`, `recommendation`, `decision_grade`, `final_report`, or equivalent localized labels.
- Rising ratio of `accepted_with_exclusions` packages compared with accepted packages, without a corresponding upstream correction cycle.
- Bundle membership that includes source ids or quality record ids not present in aggregate `Phase1Package.source_refs[]` or `Phase1Package.quality_record_refs[]`.
- `PackagingRejection.provenance_refs` is empty for error codes other than `MISSING_PROVENANCE`, indicating the rejection sidecar itself is losing available audit metadata.
- Package generation latency or memory use grows faster than input count because validation is repeatedly scanning full snapshots instead of using deterministic id indexes.

## expensive_errors
- Accepting a package with unresolved source references. It is expensive because downstream activation, inference, and reports may cite a prior whose source basis cannot be reconstructed. Prevent it by indexing the `source_registry` snapshot before package assembly and failing every missing source with `UNRESOLVED_SOURCE_REF`.
- Emitting a `FacilityPrior` without complete provenance and lineage arrays. It is expensive because the package may have to be withdrawn after dependent motors have already built cases from it. Prevent it by validating provenance, lineage, version, and snapshot fields before ids and hashes are finalized.
- Silently excluding ineligible library objects. It is expensive because auditors cannot distinguish intentional curation exclusion from accidental data loss, and later rebuilds cannot explain membership changes. Prevent it by creating `PackagingRejection` records for each excluded candidate and linking them through `exclusion_record_refs` or `rejection_refs`.
- Letting inference or TAD fields into the Fase 1 package. It is expensive because it contaminates the epistemic boundary between prior material and downstream analysis, forcing conformance review across multiple motors. Prevent it with a denylist check for inference, TAD, conclusion, recommendation, and decision-grade fields at input and output boundaries.
- Using nondeterministic ordering for ids, bundle fingerprints, or version hashes. It is expensive because identical input snapshots generate incomparable package versions and false lineage changes. Prevent it by sorting stable identifiers before hashing and by excluding runtime-only values from deterministic hash payloads.
- Retargeting quality records locally when their targets do not resolve. It is expensive because it creates unsupported quality claims that cannot be traced back to `motor_007`. Prevent it by rejecting with `QUALITY_RECORD_TARGET_UNKNOWN` and requiring the quality stage to produce a corrected record.
- Emitting an accepted empty package when no eligible library object remains. It is expensive because later motors may interpret the empty prior as a valid absence of risk or context. Prevent it by treating empty eligible input as a blocking validation result and by withholding accepted `FacilityPrior` and `Phase1Package` outputs.
- Reusing upstream identifiers as package, bundle, prior, or rejection identifiers. It is expensive because storage and lineage systems can no longer separate source objects from derived handoff objects. Prevent it by deriving motor_012 entity ids from `motor_012`, scope, stable upstream refs, rule versions, and package run metadata while preserving upstream ids only as references.
