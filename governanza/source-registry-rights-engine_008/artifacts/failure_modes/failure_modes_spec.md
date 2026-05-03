# Failure Modes Spec — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.

All placeholder markers have been resolved for Gate 4 review.
-->

## failure_modes_list
- FM-008-001 RIGHTS_AMBIGUITY_COLLAPSE: license or agreement evidence omits explicit permission for the declared use, but the engine emits `rights_status = "allowed"` or `access_class = "public"` -> downstream consumers treat restricted or unknown rights as usable -> recovery path: invalidate the emitted SourceRecord, RightsProfile, AccessClass and RefreshSchedule versions, emit blocking `SourceRightsValidationError.error_code = "MISSING_RIGHTS_EVIDENCE"` or `"RIGHTS_CONFLICT"`, require traceable license or agreement evidence, and reissue a superseding version with `parent_id`.
- FM-008-002 SOURCE_ID_COLLISION: a duplicate `source_id`, `rights_profile_id`, `access_class_id` or `refresh_schedule_id` appears with different material content and no governed `parent_id` -> current records for one logical source point to incompatible rights metadata -> recovery path: reject the newer submission with blocking `"RIGHTS_CONFLICT"` or `"CONTRACT_SCOPE_VIOLATION"`, preserve the previous immutable current record, and accept the change only as a governed supersession with explicit evidence references.
- FM-008-003 UNTRACEABLE_RIGHTS_EVIDENCE: `LicenseDocumentRef` or `AccessAgreementRef` lacks `document_ref`, `observed_at`, validity dates where required, or stable evidence identifier -> rights output cannot be reconstructed from source documents -> recovery path: emit blocking `"UNTRACEABLE_DOCUMENT_REF"` or `"INVALID_LICENSE_DATES"`, emit no accepted registry outputs for that source, and require corrected evidence with document reference and observation timestamp.
- FM-008-004 ACCESS_CLASS_DRIFT: access class is changed manually without matching active `RightsProfile`, supporting document references, assignment reason and version lineage -> `access_class` no longer follows deterministically from documented rights -> recovery path: mark the derived access class invalid with `"INVALID_ACCESS_CLASS"` or `"CONTRACT_SCOPE_VIOLATION"`, restore the last valid current class by reference, and require a new immutable version linked to evidence and prior record.
- FM-008-005 REFRESH_DISCIPLINE_GAP: accepted source lacks a valid `RefreshSchedule.periodicity`, `next_review_at` or explicit `manual_review_condition` -> rights and access metadata become stale without operational signal -> recovery path: block emission with `"MISSING_REFRESH_DISCIPLINE"` or issue a governed correction that adds schedule basis references and a deterministic review trigger before downstream use.
- FM-008-006 SCOPE_LEAK_TO_INGESTION_OR_QUALITY: implementation begins downloading source payloads, parsing records, scoring source quality, resolving entities or producing inference/reporting outputs -> motor_008 becomes a monolith and violates boundaries with ingestion, quality, identity and reporting motors -> recovery path: fail conformance, remove the out-of-scope output path, retain only source metadata and rights validation records, and route those responsibilities to their owning motors.

## anti_patterns
- Treating a public URL, API response, vendor reputation or institutional status as permission to use the source without a `LicenseDocumentRef` or `AccessAgreementRef`.
- Collapsing all ambiguous, premium or restricted cases into a generic allowed class instead of preserving specific prohibitions, attribution obligations, territorial limits, embargoes, quota notes and contractual limits.
- Updating `RightsProfile`, `AccessClass` or `RefreshSchedule` in place rather than emitting a new immutable version with `version_id`, `version_hash`, `parent_id`, `source_ref` and evidence references.
- Letting downstream ingestion, normalization, quality evaluation or reporting code rewrite source rights metadata owned by motor_008.
- Coercing malformed fields silently, such as converting a list-valued `declared_use` into a string or inventing a missing `source_id`, `document_ref`, `observed_at`, refresh cadence or access class.
- Combining source registration with raw content download, payload parsing, quality scoring, identity resolution, inference, report assembly or governance exception adjudication.
- Storing only human-readable license notes while dropping stable `license_ref_id`, `agreement_ref_id`, `document_ref`, `observed_at` and validity fields needed for audit.
- Generating access class labels with an LLM or free-text heuristic instead of deterministic rules over documented rights and access evidence.

## degradation_signals
- `rights_profiles_without_document_ref_count > 0` or any current `RightsProfile` whose `license_document_refs` and `agreement_refs` are both empty.
- Non-zero accepted outputs where `source_registration.source_id`, `rights_profile.source_id`, `access_class.source_id` and `refresh_schedule.source_id` do not match exactly.
- Increase in blocking validation errors with codes `"MISSING_RIGHTS_EVIDENCE"`, `"UNTRACEABLE_DOCUMENT_REF"`, `"RIGHTS_CONFLICT"` or `"MISSING_REFRESH_DISCIPLINE"` for the same `source_id` across repeated runs.
- More than one current `SourceRecord`, `RightsProfile`, `AccessClass` or `RefreshSchedule` for the same `source_id` without explicit supersession through `parent_id`.
- Any access class update with unchanged supporting document references but changed `access_class`, `authentication_required`, `payment_required`, `embargo_until` or territorial restrictions.
- High ratio of records using generic `restriction_notes` such as "see terms" while `prohibited_uses`, `attribution_requirements` or `manual_review_condition` remain empty.
- Logs showing accepted outputs after `SourceRightsValidationError.blocking = true` for the same source and validation run.
- Presence of raw payload fields, parsed record counts, quality scores, entity matches, inference identifiers or report block identifiers in motor_008 outputs.
- Stale schedule signal: `next_review_at` before the current run date for active sources, or `periodicity = "manual_review"` with empty `manual_review_condition`.
- Versioning signal: duplicate logical identifiers with different `version_hash` values and no `parent_id`, or identical submissions producing different hashes.

## expensive_errors
- Misclassifying restricted or contractual sources as `public`: expensive because downstream ingestion, reporting and reuse may already have depended on an unauthorized rights state, requiring rollback, audit review and regeneration of derived objects. Prevention: require explicit rights evidence, block ambiguous permissions, and derive `AccessClass` only from active license and agreement references.
- Losing document provenance for a rights decision: expensive because the team cannot prove why a source was accepted, restricted or blocked, and every downstream object that cites the source becomes suspect. Prevention: enforce non-empty `document_ref`, `observed_at`, evidence identifiers, `source_ref`, `phase_contract_ref` and supporting reference lists on every accepted output.
- Overwriting an existing rights profile in place: expensive because historical source usage cannot be reconstructed and stale downstream outputs cannot be identified accurately. Prevention: immutable record versions, deterministic `version_hash`, explicit `parent_id` on supersession, and rejection of material duplicate changes without lineage.
- Accepting conflicting active evidence without blocking: expensive because two incompatible usage policies can propagate to ingestion and reporting with no reliable precedence trail. Prevention: detect conflicting `permitted_uses` and `prohibited_uses`, emit `"RIGHTS_CONFLICT"`, preserve all conflicting evidence references in the validation signal, and require governed resolution before accepted output.
- Emitting a refresh schedule without a real cadence or trigger: expensive because license terms, access agreements and usage rights can expire unnoticed, forcing broad retroactive review. Prevention: require `periodicity` plus `next_review_at`, or `manual_review_condition` plus schedule basis references, before source registration is accepted.
- Allowing motor_008 to ingest or score source payloads: expensive because ownership boundaries blur and later fixes require separating mixed source metadata, payload data, quality conclusions and inference artifacts. Prevention: reject payload fields at the contract boundary, emit only registry and rights metadata, and keep quality, ingestion, normalization, identity and inference outputs out of this motor.
