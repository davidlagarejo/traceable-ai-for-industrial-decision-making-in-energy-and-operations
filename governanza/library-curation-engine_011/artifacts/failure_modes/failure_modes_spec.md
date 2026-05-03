# Failure Modes Spec — Library Curation Engine

Motor ID: motor_011

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir objetos ya estructurados y evaluados en bibliotecas reutilizables del framework.
why_it_exists:  Evita que cada fase arme su propia pseudo-biblioteca local.
key_inputs:     quality_records (motor_007), identity_records (motor_006), dedup_records (motor_010)
key_outputs:    library_object, curated_bundle, library_version
key_objects:    LibraryObject, CuratedBundle, LibraryVersion
what_not_to_do: No ingesta datos nuevos. No evalúa calidad. Solo selecciona y organiza objetos aptos como biblioteca.
design_notes:   Requiere el pipeline completo de Fase 1.

All placeholder markers in this file have been replaced with concrete failure-mode content.
-->

## failure_modes_list
- `CURATION_POLICY_BLOCKED`: `curation_policy.curation_run_id`, `curation_policy.curation_rule_version` or `curation_policy.bundle_scope` is missing or empty -> the run cannot evaluate candidates without fabricating publication context -> abort before emitting any `LibraryObject`, `CuratedBundle` or `LibraryVersion`; return structured policy failure and require a complete policy from the caller.
- `QUALITY_REF_MISSING_OR_COLLIDING`: a candidate has zero matching `quality_records` or more than one active `quality_record.subject_ref` for the same source object -> eligibility cannot be proven deterministically and downstream membership would be ambiguous -> reject the candidate with `CURATION_QUALITY_REF_MISSING`, preserve the candidate reference in `CurationRejection`, and require upstream quality evidence to be corrected by `motor_007`.
- `QUALITY_GATE_BYPASS`: a candidate with `evaluation_status = rejected`, `evaluation_status = disqualified` or a policy-blocking `quality_flags` value is promoted -> a non-eligible source object appears in `LibraryObject` or `CuratedBundle.member_library_object_refs` -> remove the candidate from membership, emit `CURATION_QUALITY_NOT_ELIGIBLE`, create a new `LibraryVersion` for any corrected bundle, and never mutate the prior published version in place.
- `IDENTITY_REF_MISSING`: no `identity_record` resolves to the candidate `source_object_ref` or accepted entity cluster -> the library object would not carry auditable identity evidence -> reject the candidate with `CURATION_IDENTITY_REF_MISSING`; keep quality evidence read-only and require upstream identity evidence from `motor_006`.
- `IDENTITY_AMBIGUITY_PROMOTION`: an identity record with unresolved ambiguity, low confidence where policy blocks it, or contradictory evaluated refs is treated as eligible -> the library promotes an object whose entity identity is not governed for reuse -> reject or downgrade to non-member rejection with `CURATION_IDENTITY_AMBIGUOUS`; preserve ambiguity evidence in `blocking_evidence_refs`.
- `DEDUP_EVIDENCE_INCONSISTENT`: a dedup record references an unknown candidate, a duplicate cluster with fewer than two distinct members, or a recommendation that conflicts with available cluster membership -> bundle membership may suppress or retain the wrong candidate -> reject the affected candidate or duplicate decision with `CURATION_DEDUP_REF_INVALID`, preserve all dedup references, and require a corrected `motor_010` decision before membership changes.
- `DUPLICATE_SUPPRESSION_WITHOUT_TRACE`: a duplicate candidate is excluded from the bundle without `excluded_candidate_refs`, `rejection_refs` or dedup rationale references -> downstream users cannot distinguish governed suppression from data loss -> rebuild the bundle from the same inputs, emit a `CurationRejection` or explicit exclusion trace, and publish a new bundle `LibraryVersion`.
- `MEMBER_REFERENCE_ORPHANED`: `CuratedBundle.member_library_object_refs` contains an id that was not emitted as a `LibraryObject` for the same `curation_run_id` and `bundle_scope` -> bundle consumers receive unresolved or cross-run references -> block bundle emission, recompute membership only from emitted object ids, and surface the orphaned ids in validation logs.
- `CROSS_SCOPE_MEMBERSHIP_LEAK`: a `LibraryObject` curated for one `bundle_scope` is inserted into a bundle for another scope without a new eligibility decision under that scope -> phase-specific libraries become indistinguishable and reuse boundaries are broken -> reject the member reference, require curation under the target scope, and create a separate `LibraryVersion` if the object is valid there.
- `LINEAGE_OR_PROVENANCE_LOSS`: any emitted `LibraryObject`, `CuratedBundle`, `LibraryVersion` or `CurationRejection` lacks required `source_ref`, `provenance_refs`, `lineage_refs`, `produced_by_motor`, `produced_at` or upstream evidence refs -> rebuild and audit become impossible after publication -> block persistence, emit a structural validation failure, and require upstream references instead of filling synthetic placeholders.
- `NON_DETERMINISTIC_MEMBERSHIP`: the same `quality_records`, `identity_records`, `dedup_records` and `curation_policy` produce different `member_library_object_refs`, `membership_fingerprint`, `content_fingerprint` or `version_hash` across runs -> published libraries cannot be reproduced or compared -> sort by stable identifiers, exclude timestamps from deterministic hash payloads unless contractually part of content, and rerun before publishing.
- `VERSION_MUTATION_IN_PLACE`: a material change in membership, curation rule version, upstream evidence, duplicate handling or lineage overwrites an existing `LibraryVersion` instead of creating a new one -> audit history and downstream cache invalidation are corrupted -> restore the previous version from audit storage, publish a new `LibraryVersion` with `prior_version_ref`, and flag the overwritten record for conformance review.
- `UPSTREAM_RECORD_MUTATION`: the curation process edits quality, identity, deduplication, source object or cluster records while preparing library outputs -> ownership boundaries of `motor_006`, `motor_007` and `motor_010` are violated -> stop the run, discard partial outputs, restore read-only upstream inputs, and move required corrections back to the owning motor.
- `PARTIAL_OUTPUT_PERSISTENCE_AFTER_ABORT`: a run with invalid policy or malformed candidate data persists some `LibraryObject` or `LibraryVersion` records before failing -> consumers can ingest incomplete library state -> enforce validate-before-emit sequencing and transactional publication; quarantine partial records and rerun from original inputs after the blocking error is resolved.
- `LOCAL_PSEUDO_LIBRARY_DRIFT`: downstream phases maintain their own selected object lists because curated bundles are incomplete, unstable or lack required metadata -> multiple unofficial libraries diverge from governed `motor_011` output -> treat downstream lists as symptoms, not authority; backfill missing curation evidence and publish governed bundles with deterministic versions.

## anti_patterns
- Recomputing `fitness_score`, suppressing `quality_flags` or changing `evaluation_status` inside library curation. Eligibility must be selected from `motor_007` evidence, not re-evaluated here.
- Resolving entity identity, merging clusters or closing ambiguity inside this motor. Identity evidence is read-only and owned by `motor_006`.
- Detecting duplicates, calculating similarity scores or rewriting duplicate recommendations as part of bundle construction. Duplicate evidence is read-only and owned by `motor_010`.
- Accepting raw records, parsed-only records, analyst notes or hand-built spreadsheets as direct library candidates without quality, identity and duplicate-control evidence.
- Using input order, wall-clock timestamp, display title or natural-language label as the primary source of `library_object_id`, `curated_bundle_id`, `membership_fingerprint` or `version_hash`.
- Treating duplicate suppression as deletion. Suppressed candidates must remain auditable through `excluded_candidate_refs`, `rejection_refs` and dedup evidence references.
- Updating bundle membership or version fields in place when inputs, rule version, lineage or duplicate policy changes. Material changes require a new `LibraryVersion`.
- Building one catch-all library that ignores `bundle_scope`, phase boundary or downstream reuse context.
- Letting downstream motors maintain private curation lists and then importing those lists as if they were governed `CuratedBundle` versions.
- Filling missing provenance, lineage, policy or evidence refs with synthetic values such as `unknown`, empty strings, generated timestamps or language-model summaries.
- Emitting generic errors without `CurationRejection.error_code`, `candidate_ref` and `blocking_evidence_refs`.
- Allowing a language model, reviewer preference or convenience ranking to decide eligibility outside the deterministic `curation_policy`.

## degradation_signals
- `missing_required_ref_rate`: any non-zero share of emitted records with empty `quality_record_ref`, `identity_record_ref`, `source_ref`, `provenance_refs`, `lineage_refs`, `version_id` or `version_hash`.
- `policy_block_rate`: repeated `CURATION_POLICY_BLOCKED` failures across runs, especially when candidate data is otherwise valid.
- `candidate_rejection_spike`: sudden increase in `CURATION_QUALITY_REF_MISSING`, `CURATION_IDENTITY_REF_MISSING` or `CURATION_DEDUP_REF_INVALID` compared with recent runs for the same `bundle_scope`.
- `unexplained_exclusion_count`: excluded candidates present in `CuratedBundle.excluded_candidate_refs` without matching `CurationRejection` records or dedup rationale references.
- `orphan_member_ref_count`: any `member_library_object_refs` value that cannot be resolved to an emitted `LibraryObject` from the same `curation_run_id` and `bundle_scope`.
- `fingerprint_drift_without_input_change`: `membership_fingerprint`, `content_fingerprint` or `version_hash` changes when upstream input fingerprints and `curation_rule_version` are unchanged.
- `duplicate_member_violation_count`: duplicate cluster members included together when active `duplicate_policy` requires a single representative.
- `warning_inclusion_ratio`: rising share of `curation_status = included_with_warning` without corresponding policy change, governance review or explicit allowed warning list.
- `version_churn_same_content`: multiple `LibraryVersion` records with identical `content_fingerprint` but different ids or unstated rationale.
- `cross_scope_ref_count`: bundle members whose `LibraryObject.bundle_scope` differs from `CuratedBundle.bundle_scope`.
- `partial_publish_log_pattern`: logs showing object emission before policy validation, followed by abort, rollback or validation failure.
- `downstream_raw_input_requests`: downstream motors requesting raw quality, identity or dedup inputs because `LibraryObject` and `CuratedBundle` metadata is insufficient for reuse.

## expensive_errors
- Publishing a bundle with non-eligible quality records. It is expensive because downstream consumers may cache, cite or build inference inputs from objects that the framework should have blocked. Prevent it by checking `evaluation_status`, `quality_flags` and `accepted_quality_statuses` before any output is emitted.
- Publishing a library object without provenance or lineage. It is expensive because rebuild, audit and conformance review cannot reconstruct why the object entered the library. Prevent it by making `provenance_refs`, `lineage_refs`, `source_ref` and upstream evidence refs mandatory emission gates.
- Overwriting an existing `LibraryVersion` after membership or evidence changes. It is expensive because historical consumers lose the exact version they used and comparisons become unreliable. Prevent it by treating versions as immutable and requiring `prior_version_ref` for material changes.
- Using nondeterministic identifiers or fingerprints. It is expensive because repeated valid runs create incompatible ids, duplicate versions and unstable downstream references. Prevent it by deriving ids and hashes from stable sorted payloads, rule version and upstream refs only.
- Suppressing duplicates without an audit trail. It is expensive because later reviewers cannot know whether a candidate was excluded by policy, duplicate handling, data loss or manual choice. Prevent it by recording `excluded_candidate_refs`, `rejection_refs`, `dedup_evidence_refs` and rationale refs for every suppressed candidate.
- Mutating upstream quality, identity or dedup records during curation. It is expensive because ownership boundaries break and other motors may observe changed evidence without a governed upstream run. Prevent it by enforcing read-only input handling and emitting separate curation outputs only.
- Allowing cross-scope membership leaks. It is expensive because phase-specific or consumer-specific libraries silently inherit objects that were never evaluated for that scope. Prevent it by requiring `LibraryObject.bundle_scope` to match `CuratedBundle.bundle_scope` and by re-curating candidates for new scopes.
- Persisting partial outputs after a failed run. It is expensive because consumers may ingest incomplete state before the operator notices the failure. Prevent it by validating policy and candidate contracts before persistence and by publishing outputs atomically.
- Promoting unresolved identity ambiguity. It is expensive because once a library object is reused, downstream bundles and inference cases may rely on the wrong entity identity. Prevent it by rejecting ambiguous identity evidence under the active policy and preserving ambiguity references in `CurationRejection`.
- Letting unofficial downstream lists replace governed bundles. It is expensive because multiple local pseudo-libraries diverge and later reconciliation requires manual comparison across phases. Prevent it by making `CuratedBundle` the only publication unit and by treating downstream private lists as non-authoritative diagnostics.
