# Technical Schema — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All open placeholders in this file have been resolved with concrete technical schema content.
-->

## entities
- `LibraryObject`: output record that promotes one upstream structured object into reusable library form after the active curation policy validates quality, identity and duplicate-control evidence. It lives in the `schema_technical` stage as the primary persisted output shape and is later implemented as a serializable model.
- `CuratedBundle`: output record that groups `LibraryObject` references for one declared `bundle_scope`, such as a phase, domain, facility class or downstream consumer. It lives in the `schema_technical` stage as the membership container and publication unit.
- `LibraryVersion`: immutable output record that versions a `LibraryObject` or `CuratedBundle` by stable identifier, content hash, curation rule version and prior version reference. It lives in the `schema_technical` stage as the version registry shape.
- `CurationRejection`: audit output record for a candidate that is not promoted to a `LibraryObject` or is excluded from bundle membership. It lives in the `schema_technical` stage as an error and exclusion trace, not as a separate quality, identity or deduplication decision.

## fields
`LibraryObject`
- `library_object_id: string` (required) — stable canonical identifier for the reusable library object.
- `source_object_ref: string` (required) — reference to the upstream structured object being curated.
- `quality_record_ref: string` (required) — reference to the `motor_007` quality record that authorizes eligibility.
- `identity_record_ref: string` (required) — reference to the `motor_006` identity record used for identity evidence.
- `dedup_evidence_refs: list[string]` (required) — references to `motor_010` duplicate clusters, similarity records or deduplication decisions considered during curation.
- `curation_status: enum[included, included_with_warning, excluded_duplicate, rejected]` (required) — deterministic curation result assigned under the active policy.
- `curation_rule_version: string` (required) — version of the rule set used to evaluate eligibility and membership.
- `curation_run_id: string` (required) — run identifier from the active curation policy.
- `bundle_scope: string` (required) — declared reuse scope for which the object was curated.
- `warning_refs: list[string]` (required) — quality or policy warning references preserved when `curation_status` is `included_with_warning`; empty list when no warnings apply.
- `rejection_reason_ref: string | null` (required) — reference to a `CurationRejection` record when the object is represented as rejected or excluded.
- `provenance_refs: list[string]` (required) — upstream provenance references copied from accepted evidence.
- `lineage_refs: list[string]` (required) — upstream lineage references sufficient to rebuild the object.
- `source_ref: string` (required) — canonical lineage source reference; equal to `source_object_ref` unless a governed alias is supplied by the upstream object.
- `produced_by_motor: string` (required) — constant value `motor_011`.
- `produced_at: datetime` (required) — timestamp when this output record was emitted.
- `parent_id: string | null` (required) — prior `library_object_id` when this object supersedes a previous object; null for first publication.
- `version_id: string` (required) — current `LibraryVersion.library_version_id` for this object.
- `created_at: datetime` (required) — creation timestamp for this record.
- `updated_at: datetime` (required) — latest metadata update timestamp; equal to `created_at` for immutable first emission.
- `version_hash: string` (required) — deterministic hash over the stable object payload, upstream references and `curation_rule_version`.

`CuratedBundle`
- `curated_bundle_id: string` (required) — stable canonical identifier for the scoped bundle.
- `bundle_scope: string` (required) — declared scope of reuse.
- `member_library_object_refs: list[string]` (required) — ordered stable references to included `LibraryObject.library_object_id` values.
- `excluded_candidate_refs: list[string]` (required) — references to candidate objects excluded by policy, duplicate recommendation, quality failure or identity failure.
- `rejection_refs: list[string]` (required) — references to `CurationRejection` records explaining each exclusion.
- `selection_rule_version: string` (required) — version of deterministic membership and duplicate-handling rules.
- `curation_run_id: string` (required) — run identifier from the curation policy that produced the bundle.
- `membership_fingerprint: string` (required) — deterministic hash of sorted member identifiers, excluded candidate references and selection rule version.
- `provenance_refs: list[string]` (required) — aggregate provenance references from member library objects and exclusions.
- `lineage_refs: list[string]` (required) — aggregate lineage references needed to rebuild bundle membership.
- `source_ref: string` (required) — canonical source reference for the bundle scope or publication manifest.
- `produced_by_motor: string` (required) — constant value `motor_011`.
- `produced_at: datetime` (required) — timestamp when the bundle was emitted.
- `parent_id: string | null` (required) — prior `curated_bundle_id` when this bundle supersedes a previous bundle; null for first publication.
- `version_id: string` (required) — current `LibraryVersion.library_version_id` for this bundle.
- `created_at: datetime` (required) — bundle creation timestamp.
- `updated_at: datetime` (required) — latest metadata update timestamp; equal to `created_at` for immutable first emission.
- `version_hash: string` (required) — deterministic hash over membership, exclusions, scope and rule version.

`LibraryVersion`
- `library_version_id: string` (required) — stable canonical identifier for the version record.
- `version_id: string` (required) — alias field carrying the same value as `library_version_id` for generic version interfaces.
- `versioned_object_ref: string` (required) — `library_object_id` or `curated_bundle_id` being versioned.
- `versioned_object_type: enum[library_object, curated_bundle]` (required) — type of object referenced by `versioned_object_ref`.
- `content_fingerprint: string` (required) — deterministic fingerprint of the versioned object content.
- `version_hash: string` (required) — deterministic hash over `versioned_object_ref`, `content_fingerprint`, `curation_rule_version`, `parent_id` and lineage fields.
- `prior_version_ref: string | null` (required) — prior `library_version_id` when the object is superseded or rebuilt; null for first version.
- `curation_rule_version: string` (required) — curation rule version that produced the versioned object.
- `rebuild_manifest_ref: string | null` (required) — manifest reference for rebuild context when one exists.
- `source_ref: string` (required) — source object, bundle manifest or publication event that anchors this version.
- `produced_by_motor: string` (required) — constant value `motor_011`.
- `produced_at: datetime` (required) — timestamp when the version record was emitted.
- `parent_id: string | null` (required) — equal to `prior_version_ref` for generic lineage traversal.
- `lineage_refs: list[string]` (required) — lineage references needed to rebuild the versioned object.
- `created_at: datetime` (required) — version creation timestamp.
- `updated_at: datetime` (required) — latest metadata update timestamp; immutable records set this equal to `created_at`.

`CurationRejection`
- `curation_rejection_id: string` (required) — stable canonical identifier for the rejection audit record.
- `candidate_ref: string` (required) — upstream candidate object that was not promoted or was excluded.
- `error_code: enum[CURATION_QUALITY_REF_MISSING, CURATION_QUALITY_NOT_ELIGIBLE, CURATION_IDENTITY_REF_MISSING, CURATION_IDENTITY_AMBIGUOUS, CURATION_DEDUP_REF_INVALID, CURATION_POLICY_BLOCKED]` (required) — deterministic rejection signal.
- `blocking_evidence_refs: list[string]` (required) — quality, identity, duplicate or policy references that caused rejection.
- `quality_record_ref: string | null` (required) — related `motor_007` record when present.
- `identity_record_ref: string | null` (required) — related `motor_006` record when present.
- `dedup_evidence_refs: list[string]` (required) — related `motor_010` evidence references when present.
- `curation_run_id: string` (required) — run identifier from the active curation policy.
- `curation_rule_version: string` (required) — rule version that produced the rejection.
- `source_ref: string` (required) — canonical upstream source reference for lineage.
- `produced_by_motor: string` (required) — constant value `motor_011`.
- `produced_at: datetime` (required) — timestamp when the rejection record was emitted.
- `parent_id: string | null` (required) — prior rejection record if a later run supersedes an earlier rejection for the same candidate; null otherwise.
- `created_at: datetime` (required) — rejection record creation timestamp.
- `updated_at: datetime` (required) — latest metadata update timestamp.
- `version_hash: string` (required) — deterministic hash over candidate, code, evidence references and rule version.

## relationships
- `LibraryObject.quality_record_ref` references `motor_007.QualityRecord.quality_record_id`; the relationship is read-only and does not permit quality recalculation.
- `LibraryObject.identity_record_ref` references `motor_006.IdentityRecord.identity_record_id`; the relationship is read-only and does not permit identity resolution or cluster mutation.
- `LibraryObject.dedup_evidence_refs[]` references `motor_010` duplicate cluster, similarity record or deduplication decision identifiers; the relationship is read-only and non-destructive.
- `LibraryObject.rejection_reason_ref` references `CurationRejection.curation_rejection_id` when the library object carries `curation_status = rejected` or `excluded_duplicate`.
- `CuratedBundle.member_library_object_refs[]` references `LibraryObject.library_object_id`; every member reference must resolve to an emitted library object from the same curation run and scope.
- `CuratedBundle.excluded_candidate_refs[]` references upstream candidate identifiers; each excluded reference must be explained by at least one `CurationRejection` in `CuratedBundle.rejection_refs[]`.
- `CuratedBundle.rejection_refs[]` references `CurationRejection.curation_rejection_id`.
- `LibraryVersion.versioned_object_ref` references `LibraryObject.library_object_id` when `versioned_object_type = library_object`.
- `LibraryVersion.versioned_object_ref` references `CuratedBundle.curated_bundle_id` when `versioned_object_type = curated_bundle`.
- `LibraryVersion.prior_version_ref` references `LibraryVersion.library_version_id` for supersession, rebuild or rule-version change.
- `LibraryObject.version_id` and `CuratedBundle.version_id` reference `LibraryVersion.library_version_id`.
- `parent_id` fields reference the prior emitted entity of the same type only; they must not point to upstream quality, identity or duplicate records.

## identifiers
- `LibraryObject`: canonical identifier is `library_object_id`. It is derived deterministically from `motor_011`, `source_object_ref`, `bundle_scope`, `curation_rule_version` and the accepted evidence references.
- `CuratedBundle`: canonical identifier is `curated_bundle_id`. It is derived deterministically from `motor_011`, `bundle_scope`, `curation_rule_version` and `membership_fingerprint`.
- `LibraryVersion`: canonical identifier is `library_version_id`; generic version consumers may also read the same value through `version_id`.
- `CurationRejection`: canonical identifier is `curation_rejection_id`. It is derived from `motor_011`, `candidate_ref`, `error_code`, `curation_run_id` and blocking evidence references.
- Upstream references keep their original identifiers: `quality_record_ref`, `identity_record_ref`, `dedup_evidence_refs`, `source_object_ref` and `candidate_ref` are foreign references, not new identifiers owned by this motor.
- No entity uses mutable list position, display name, natural-language title or timestamp alone as an identifier.

## versioning
- All versioned outputs carry `version_id`, `created_at`, `updated_at` and `version_hash`.
- `LibraryObject.version_id` references the current `LibraryVersion` for that object; `version_hash` is computed from `source_object_ref`, quality, identity and duplicate evidence refs, `curation_status`, `curation_rule_version`, provenance and lineage refs.
- `CuratedBundle.version_id` references the current `LibraryVersion` for that bundle; `version_hash` is computed from `bundle_scope`, stable member refs, excluded candidate refs, rejection refs, `selection_rule_version`, provenance and lineage refs.
- `LibraryVersion.version_id` equals `library_version_id`; `version_hash` is computed from `versioned_object_ref`, `versioned_object_type`, `content_fingerprint`, `prior_version_ref`, `curation_rule_version`, `source_ref` and lineage refs.
- `CurationRejection` is version-hashed for audit stability but is not a publication unit. A later run that changes the rejection outcome creates a new rejection record or references the previous record through `parent_id`.
- `created_at` is set once at emission time. `updated_at` changes only for metadata correction that preserves audit history; immutable publication semantics require a new `LibraryVersion` for material content, membership, policy or evidence changes.
- A change in eligible membership, duplicate handling, curation policy, upstream quality record, identity record, duplicate evidence, provenance, lineage or `curation_rule_version` requires a new `LibraryVersion`.

## lineage
- All emitted records carry `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` identifies the upstream candidate object for `LibraryObject` and `CurationRejection`, the bundle scope or publication manifest for `CuratedBundle`, and the versioned object or publication event for `LibraryVersion`.
- `produced_by_motor` is always `motor_011`; this motor does not claim production of upstream quality, identity or duplicate evidence.
- `produced_at` is the emission timestamp for the record and must be stable once persisted.
- `parent_id` links to the previous record of the same entity type when a governed rebuild, supersession or corrected publication exists; null means no prior emitted entity.
- `provenance_refs` and `lineage_refs` must be copied or aggregated from upstream evidence and preserved without silent repair.
- Lineage must be sufficient to rebuild each `LibraryObject`, `CuratedBundle` and `LibraryVersion` from the same upstream `quality_records`, `identity_records`, `dedup_records` and `curation_policy`.
