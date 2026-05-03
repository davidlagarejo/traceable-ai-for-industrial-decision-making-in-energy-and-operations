# Technical Schema — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All open placeholders in this file have been resolved with concrete technical schema content.
-->

## entities
- `FacilityPrior`: primary persisted output that materializes the authorized Fase 1 prior for one `facility_ref` or declared operational context. It lives in the `schema_technical` stage as the canonical prior snapshot consumed by downstream activation without adding inference, TAD status, conclusions, or decision-grade claims.
- `ContextualBundle`: scoped packet of eligible library objects, source references, and quality references anchored to one `FacilityPrior`. It lives in the `schema_technical` stage as the deterministic grouping unit prepared for Fase 2 activation.
- `Phase1Package`: complete handoff artifact that binds the facility prior, contextual bundles, upstream input snapshots, validation status, version metadata, and rebuild lineage. It lives in the `schema_technical` stage as the publication and audit envelope for the Fase 1 handoff.
- `PackagingRejection`: structured validation and exclusion audit record for upstream items or bundle candidates that cannot be included because a packaging rule failed. It lives in the `schema_technical` stage as a traceability sidecar and does not create quality, source, curation, inference, or TAD decisions.

## fields
`FacilityPrior`
- `facility_prior_id: string` (required) — stable canonical identifier for the materialized prior.
- `record_id: string` (required) — generic record identifier equal to `facility_prior_id` for storage and audit interfaces that require a common key name.
- `facility_ref: string` (required) — facility or operational context represented by the prior.
- `prior_scope: string` (required) — declared scope of the prior, such as facility, site group, source family, or minimal operational context.
- `library_object_refs: list[string]` (required) — ordered references to eligible `motor_011` library objects included in the prior.
- `source_refs: list[string]` (required) — source identifiers used by included library objects and resolved against the input source registry snapshot.
- `source_registry_snapshot_ref: string` (required) — reference to the `motor_008` source registry snapshot used for source resolution.
- `quality_record_refs: list[string]` (required) — references to `motor_007` quality records preserved with the included library objects or sources.
- `contextual_bundle_refs: list[string]` (required) — references to `ContextualBundle.bundle_id` values emitted for this prior.
- `input_snapshot_refs: dict[string, string]` (required) — map containing `library_objects_snapshot`, `source_registry_snapshot`, and `quality_records_snapshot` references used to build the prior.
- `eligibility_rule_version: string` (required) — version of the deterministic packaging rules used to decide inclusion and exclusion.
- `packaging_run_id: string` (required) — run identifier for the deterministic materialization event.
- `exclusion_record_refs: list[string]` (required) — references to `PackagingRejection.packaging_rejection_id` records associated with excluded upstream candidates; empty list when no exclusions occurred.
- `provenance_refs: list[string]` (required) — upstream provenance references copied from included library objects, source registry entries, and quality records.
- `lineage_refs: list[string]` (required) — upstream lineage references sufficient to rebuild the prior from the same validated snapshots.
- `source_ref: string` (required) — canonical lineage anchor for this prior, normally the input snapshot manifest or the source registry snapshot reference.
- `produced_by_motor: string` (required) — constant value `motor_012`.
- `produced_at: datetime` (required) — timestamp when the prior record was emitted.
- `parent_id: string | null` (required) — prior `facility_prior_id` superseded by this record; null for the first emitted prior for the same scope.
- `version_id: string` (required) — stable version identifier for this prior record.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — latest metadata update timestamp; equal to `created_at` for immutable first emission.
- `version_hash: string` (required) — deterministic hash over stable prior payload, upstream references, eligibility rule version, and lineage fields.

`ContextualBundle`
- `bundle_id: string` (required) — stable canonical identifier for the contextual bundle.
- `record_id: string` (required) — generic record identifier equal to `bundle_id`.
- `facility_prior_ref: string` (required) — reference to the `FacilityPrior.facility_prior_id` that this bundle contextualizes.
- `facility_ref: string` (required) — facility or operational context copied from the referenced prior for local validation.
- `context_scope: string` (required) — deterministic bundle scope, such as `minimal_prior`, facility profile, utility context, source family, or operational scope.
- `library_object_refs: list[string]` (required) — ordered references to eligible `motor_011` library objects included in the bundle.
- `source_refs: list[string]` (required) — ordered source identifiers used by the bundle and resolved in the source registry snapshot.
- `quality_record_refs: list[string]` (required) — quality records attached to the bundled library objects or sources.
- `source_registry_snapshot_ref: string` (required) — source registry snapshot used to validate every `source_refs` entry.
- `bundle_rule_version: string` (required) — version of deterministic membership and grouping rules used for this bundle.
- `bundle_fingerprint: string` (required) — deterministic hash of `context_scope`, member object refs, source refs, quality refs, and bundle rule version.
- `exclusion_record_refs: list[string]` (required) — `PackagingRejection` references explaining excluded candidates for this bundle scope; empty list when none apply.
- `provenance_refs: list[string]` (required) — upstream provenance references aggregated from included members.
- `lineage_refs: list[string]` (required) — upstream lineage references needed to rebuild bundle membership.
- `source_ref: string` (required) — canonical lineage anchor for the bundle, normally the bundle scope plus input snapshot manifest.
- `produced_by_motor: string` (required) — constant value `motor_012`.
- `produced_at: datetime` (required) — timestamp when the bundle was emitted.
- `parent_id: string | null` (required) — prior `bundle_id` superseded by this bundle; null for first publication.
- `version_id: string` (required) — stable version identifier for this bundle.
- `created_at: datetime` (required) — bundle creation timestamp.
- `updated_at: datetime` (required) — latest metadata update timestamp; equal to `created_at` for immutable first emission.
- `version_hash: string` (required) — deterministic hash over membership, context scope, upstream references, bundle rule version, and lineage fields.

`Phase1Package`
- `package_id: string` (required) — stable canonical identifier for the Fase 1 handoff package.
- `record_id: string` (required) — generic record identifier equal to `package_id`.
- `package_version: string` (required) — publication label for the emitted package; does not replace `version_id`.
- `package_scope: string` (required) — declared scope of the handoff package.
- `generated_at: datetime` (required) — package generation timestamp; equal to `produced_at` for the package record.
- `facility_prior_ref: string` (required) — reference to the single `FacilityPrior.facility_prior_id` contained in the package.
- `contextual_bundle_refs: list[string]` (required) — ordered references to `ContextualBundle.bundle_id` values contained in the package.
- `input_snapshot_refs: dict[string, string]` (required) — map of source snapshots used by the package, including library objects, source registry, and quality records.
- `source_registry_snapshot_ref: string` (required) — source registry snapshot used for all package-level source checks.
- `library_object_refs: list[string]` (required) — aggregate ordered library object references present across the prior and bundles.
- `source_refs: list[string]` (required) — aggregate ordered source references present across the prior and bundles.
- `quality_record_refs: list[string]` (required) — aggregate ordered quality record references present across the prior and bundles.
- `validation_status: enum[accepted, accepted_with_exclusions, rejected]` (required) — deterministic result of package validation.
- `rejection_refs: list[string]` (required) — `PackagingRejection` references produced during package validation; empty list only when validation has no exclusions or rejections.
- `packaging_run_id: string` (required) — run identifier for the materialization event.
- `packaging_rule_version: string` (required) — version of package assembly and validation rules.
- `provenance_refs: list[string]` (required) — aggregate provenance references from all contained objects and snapshots.
- `lineage_refs: list[string]` (required) — complete lineage references needed to rebuild the package.
- `source_ref: string` (required) — canonical lineage anchor for the package, normally the input snapshot manifest reference.
- `produced_by_motor: string` (required) — constant value `motor_012`.
- `produced_at: datetime` (required) — timestamp when the package was emitted.
- `parent_id: string | null` (required) — prior `package_id` superseded by this package; null for first publication.
- `version_id: string` (required) — stable version identifier for this package.
- `created_at: datetime` (required) — package record creation timestamp.
- `updated_at: datetime` (required) — latest metadata update timestamp; equal to `created_at` for immutable first emission.
- `version_hash: string` (required) — deterministic hash over contained object references, input snapshots, rule version, validation status, and lineage fields.

`PackagingRejection`
- `packaging_rejection_id: string` (required) — stable canonical identifier for the rejection or exclusion audit record.
- `record_id: string` (required) — generic record identifier equal to `packaging_rejection_id`.
- `candidate_ref: string` (required) — upstream object, source reference, quality record, bundle candidate, or package candidate that failed validation.
- `candidate_type: enum[library_object, source_ref, quality_record, bundle_candidate, package_candidate]` (required) — type of rejected or excluded candidate.
- `error_code: enum[UNRESOLVED_SOURCE_REF, MISSING_PROVENANCE, INELIGIBLE_LIBRARY_OBJECT, QUALITY_RECORD_TARGET_UNKNOWN, EMPTY_ELIGIBLE_INPUT, FORBIDDEN_INFERENCE_FIELD]` (required) — deterministic rejection signal.
- `blocking_rule: string` (required) — packaging rule identifier that produced the rejection.
- `blocking_reference_refs: list[string]` (required) — upstream references that caused the rule failure.
- `affected_output_ref: string | null` (required) — `facility_prior_id`, `bundle_id`, or `package_id` affected by the rejection; null when validation stops before output creation.
- `exclusion_scope: string` (required) — scope in which the candidate was rejected, such as prior, bundle, or package.
- `provenance_refs: list[string]` (required) — provenance references available for the rejected candidate; empty only when the error code is `MISSING_PROVENANCE`.
- `lineage_refs: list[string]` (required) — lineage references available for the rejected candidate or validation run.
- `source_ref: string` (required) — canonical source, candidate, or snapshot reference that anchors the rejection.
- `produced_by_motor: string` (required) — constant value `motor_012`.
- `produced_at: datetime` (required) — timestamp when the rejection record was emitted.
- `parent_id: string | null` (required) — prior rejection record superseded by this one for the same candidate and rule; null when none exists.
- `version_id: string` (required) — stable version identifier for this rejection record.
- `created_at: datetime` (required) — rejection record creation timestamp.
- `updated_at: datetime` (required) — latest metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over candidate, error code, blocking rule, references, and lineage fields.

## relationships
- `FacilityPrior.library_object_refs[]` references `motor_011.LibraryObject.library_object_id`; this relationship is read-only and cannot mutate curation status or library membership.
- `FacilityPrior.source_refs[]` references `motor_008` source registry entry identifiers present in `FacilityPrior.source_registry_snapshot_ref`.
- `FacilityPrior.quality_record_refs[]` references `motor_007.QualityRecord.quality_record_id`; this relationship preserves upstream quality evidence and cannot recalculate quality.
- `FacilityPrior.contextual_bundle_refs[]` references `ContextualBundle.bundle_id`; every referenced bundle must carry `facility_prior_ref` pointing back to the same prior.
- `ContextualBundle.facility_prior_ref` references `FacilityPrior.facility_prior_id`.
- `ContextualBundle.library_object_refs[]`, `ContextualBundle.source_refs[]`, and `ContextualBundle.quality_record_refs[]` reference the same upstream namespaces as the matching `FacilityPrior` fields and must be subsets of, or explicitly traceable to, the package input snapshots.
- `Phase1Package.facility_prior_ref` references exactly one `FacilityPrior.facility_prior_id`.
- `Phase1Package.contextual_bundle_refs[]` references one or more `ContextualBundle.bundle_id` values produced from the same `input_snapshot_refs` and `packaging_run_id`.
- `Phase1Package.library_object_refs[]`, `Phase1Package.source_refs[]`, and `Phase1Package.quality_record_refs[]` aggregate references from the contained prior and bundles without creating new upstream identifiers.
- `FacilityPrior.exclusion_record_refs[]`, `ContextualBundle.exclusion_record_refs[]`, and `Phase1Package.rejection_refs[]` reference `PackagingRejection.packaging_rejection_id`.
- `PackagingRejection.affected_output_ref` may reference a `FacilityPrior.facility_prior_id`, `ContextualBundle.bundle_id`, or `Phase1Package.package_id` when the affected output exists.
- `parent_id` fields reference the prior emitted entity of the same type only; they must not point to upstream source, quality, library, or downstream inference records.

## identifiers
- `FacilityPrior`: canonical identifier is `facility_prior_id`; `record_id` carries the same value for generic persistence interfaces. It is derived deterministically from `motor_012`, `facility_ref`, `prior_scope`, `input_snapshot_refs`, and `eligibility_rule_version`.
- `ContextualBundle`: canonical identifier is `bundle_id`; `record_id` carries the same value. It is derived deterministically from `motor_012`, `facility_prior_ref`, `context_scope`, `bundle_fingerprint`, and `bundle_rule_version`.
- `Phase1Package`: canonical identifier is `package_id`; `record_id` carries the same value. It is derived deterministically from `motor_012`, `package_scope`, `facility_prior_ref`, `contextual_bundle_refs`, `input_snapshot_refs`, and `packaging_rule_version`.
- `PackagingRejection`: canonical identifier is `packaging_rejection_id`; `record_id` carries the same value. It is derived deterministically from `motor_012`, `candidate_ref`, `candidate_type`, `error_code`, `blocking_rule`, and `packaging_run_id`.
- Upstream references retain their original identifiers from `motor_011`, `motor_008`, and `motor_007`; this motor does not mint replacement identifiers for library objects, source entries, or quality records.
- No entity uses mutable list position, display name, natural-language label, or timestamp alone as a stable identifier.

## versioning
- All emitted entities carry `version_id`, `created_at`, `updated_at`, and `version_hash`.
- `FacilityPrior.version_hash` is computed from `facility_ref`, `prior_scope`, sorted `library_object_refs`, sorted `source_refs`, sorted `quality_record_refs`, `source_registry_snapshot_ref`, `input_snapshot_refs`, `eligibility_rule_version`, `exclusion_record_refs`, and lineage fields.
- `ContextualBundle.version_hash` is computed from `facility_prior_ref`, `context_scope`, sorted `library_object_refs`, sorted `source_refs`, sorted `quality_record_refs`, `source_registry_snapshot_ref`, `bundle_rule_version`, `bundle_fingerprint`, `exclusion_record_refs`, and lineage fields.
- `Phase1Package.version_hash` is computed from `package_scope`, `package_version`, `facility_prior_ref`, sorted `contextual_bundle_refs`, `input_snapshot_refs`, aggregate upstream references, `validation_status`, `rejection_refs`, `packaging_rule_version`, and lineage fields.
- `PackagingRejection.version_hash` is computed from `candidate_ref`, `candidate_type`, `error_code`, `blocking_rule`, `blocking_reference_refs`, `affected_output_ref`, `exclusion_scope`, `packaging_run_id`, and lineage fields.
- `created_at` is set once at first emission. `updated_at` changes only for governed metadata correction that preserves audit history; material changes to membership, validation status, upstream snapshots, rule version, package scope, or lineage require a new `version_id`.
- `package_version` is the handoff publication label for `Phase1Package`; it must not be used as the sole version key because all entities still require `version_id` and `version_hash`.
- `parent_id` links a new versioned record to the prior emitted record of the same entity type when a rebuild, supersession, or correction occurs.

## lineage
- All emitted entities carry `source_ref`, `produced_by_motor`, `produced_at`, and `parent_id`.
- `produced_by_motor` is always `motor_012`; this motor must not claim authorship of upstream library objects, source registry entries, quality records, curation decisions, or downstream inference objects.
- `source_ref` identifies the input snapshot manifest for `FacilityPrior` and `Phase1Package`, the bundle scope plus snapshot manifest for `ContextualBundle`, and the failed candidate or validation snapshot for `PackagingRejection`.
- `produced_at` is the emission timestamp for the record and must be stable once persisted.
- `parent_id` is null for first publication and otherwise references the previous emitted entity of the same type for the same scope, candidate, or package.
- `input_snapshot_refs`, `provenance_refs`, and `lineage_refs` must be sufficient to rebuild the same prior, bundles, package, and rejection records from the same `library_objects`, `source_registry`, `quality_records`, and packaging rule versions.
- Lineage must preserve unresolved reference failures, provenance failures, ineligible records, and unknown quality targets as explicit `PackagingRejection` records rather than silently repairing, dropping, or reclassifying upstream input.
