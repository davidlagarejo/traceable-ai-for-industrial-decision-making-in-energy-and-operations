# Technical Schema — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.

Schema sections below are complete for Gate 2 review.
-->

## entities
- SourceDeclaration: input DTO that declares one candidate source before registration. It carries the stable source identity, locator, owner, declared use and declared refresh cadence supplied by a human operator, acquisition system or institutional catalog. Stage: `schema_technical` defines the accepted input shape; `implementation` validates it before emitting any registered output.
- LicenseDocumentRef: input DTO that references a license, terms-of-use document or legal basis for source usage. It preserves document reference, observation timestamp, validity dates and declared permissions or prohibitions. Stage: `schema_technical` defines the accepted input shape; `implementation` uses it as rights evidence and never treats it as source payload.
- AccessAgreementRef: input DTO that references a contract, subscription, credential approval or access agreement for a source. It records authentication, payment, quota, embargo, territory and allowed-use constraints. Stage: `schema_technical` defines the accepted input shape; `implementation` uses it as access evidence and never uses it to ingest data.
- SourceRecord: persisted source registration record with stable source identity, owner, locator, declared use, registration status, evidence references and links to the current rights, access and refresh outputs. Stage: `schema_technical` defines the canonical persistent entity; `implementation` emits it as `source_registration`.
- RightsProfile: persisted profile of permissions, prohibitions, obligations, restriction notes and rights status for one registered source. Stage: `schema_technical` defines the canonical rights entity; `implementation` emits it as `rights_profile`.
- AccessClass: persisted deterministic access classification for one registered source, justified by the active RightsProfile and supporting license or agreement evidence. Stage: `schema_technical` defines the access classification entity; `implementation` emits it as `access_class`.
- RefreshSchedule: persisted review cadence for one registered source, including periodicity, next review date or explicit manual review condition. Stage: `schema_technical` defines the schedule entity; `implementation` emits it as `refresh_schedule`.
- SourceRightsValidationError: immutable blocking or warning signal emitted when source declarations, license references, access agreements or derived outputs violate the contract. Stage: `schema_technical` defines the structured error output; `implementation` emits it instead of silently repairing ambiguous or invalid rights metadata.

## fields
SourceDeclaration:
- source_id: string (required) — stable source identifier supplied by the declaration; it must be non-empty before any output is emitted.
- source_name: string (required) — human-readable source name.
- source_locator: string (required) — URL, catalog path, registry key or other locator for the source.
- source_type: string (required) — declared source type, stored as metadata without authorizing ingestion behavior.
- declared_owner: string (required) — declared owner, publisher or contractual counterparty for the source.
- declared_use: string (required) — intended use declared for the source within the framework.
- declared_refresh: string|null (required) — declared periodicity or event trigger; null only when a manual review condition is supplied by another input.
- declaration_ref: string (required) — document, registry entry or request reference for the declaration.
- submitted_by: string (required) — actor or system that submitted the declaration.
- submitted_at: datetime (required) — timestamp when the declaration entered motor_008 validation.

LicenseDocumentRef:
- license_ref_id: string (required) — stable identifier for this license reference.
- source_id: string (required) — SourceDeclaration.source_id to which the license applies.
- document_ref: string (required) — location or identifier of the license, terms document or legal basis.
- license_basis: string (required) — concise license or terms basis used to construct the RightsProfile.
- permitted_uses: list[string] (required) — uses explicitly permitted by the referenced license.
- prohibited_uses: list[string] (required) — uses explicitly prohibited or not granted by the referenced license.
- restriction_notes: string (required) — human-readable restrictions that must be preserved for audit and downstream checks.
- attribution_requirements: list[string] (required) — attribution, citation or notice obligations; empty only when the document explicitly has none.
- effective_from: date|null (required) — first date the license applies; null only when the document has no stated start date.
- effective_to: date|null (required) — last date the license applies; null only when the document has no stated expiration.
- observed_at: datetime (required) — timestamp when the license document was observed or recorded.

AccessAgreementRef:
- agreement_ref_id: string (required) — stable identifier for this access agreement reference.
- source_id: string (required) — SourceDeclaration.source_id to which the agreement applies.
- document_ref: string (required) — location or identifier of the contract, subscription, credential approval or access document.
- access_basis: string (required) — concise basis for access, such as public account, paid subscription, contract or internal authorization.
- authentication_required: boolean (required) — true when credentials, keys or login are required.
- payment_required: boolean (required) — true when payment, subscription or paid contract is required.
- quota_notes: string|null (required) — quota, rate limit or seat-limit statement; null only when no quota is stated.
- embargo_until: date|null (required) — date until which usage or release is embargoed; null when no embargo is documented.
- territorial_restrictions: list[string] (required) — documented geographic restrictions; empty only when none are stated.
- permitted_uses: list[string] (required) — uses explicitly permitted by the agreement.
- prohibited_uses: list[string] (required) — uses explicitly prohibited by the agreement.
- effective_from: date|null (required) — first date the agreement applies; null only when the document has no stated start date.
- effective_to: date|null (required) — last date the agreement applies; null only when the document has no stated expiration.
- observed_at: datetime (required) — timestamp when the agreement was observed or recorded.

SourceRecord:
- record_id: string (required) — immutable storage identifier for this persisted source registration version.
- source_id: string (required) — stable logical identifier for the registered source.
- source_name: string (required) — registered source name copied from the accepted declaration.
- source_locator: string (required) — registered locator copied from the accepted declaration.
- source_type: string (required) — declared source type preserved as metadata.
- declared_owner: string (required) — registered source owner, publisher or contractual counterparty.
- declared_use: string (required) — intended use accepted for registration.
- declared_refresh: string|null (required) — declared refresh cadence or event trigger from the source declaration.
- registration_status: enum[active, restricted, blocked, retired] (required) — current registry status without making quality or truth claims.
- registration_reason: string (required) — concise reason for the registration status.
- declaration_ref: string (required) — source declaration reference used to create or update this record.
- evidence_refs: list[string] (required) — license_ref_id and agreement_ref_id values considered during registration; at least one rights evidence reference is required.
- rights_profile_id: string (required) — current RightsProfile.rights_profile_id for this source.
- access_class_id: string (required) — current AccessClass.access_class_id for this source.
- refresh_schedule_id: string (required) — current RefreshSchedule.refresh_schedule_id for this source.
- phase_contract_ref: string (required) — motor_001 phase contract reference that authorizes source registry behavior.
- version_id: string (required) — stable technical key for this immutable SourceRecord version.
- created_at: datetime (required) — timestamp when this source registration version was first emitted.
- updated_at: datetime (required) — timestamp when registry metadata for this immutable version was last updated.
- version_hash: string (required) — deterministic hash of normalized SourceRecord content and immutable metadata.
- source_ref: string (required) — primary declaration or registry reference used to produce this SourceRecord.
- produced_by_motor: string (required) — fixed value `motor_008`.
- produced_at: datetime (required) — timestamp when motor_008 emitted this SourceRecord.
- parent_id: string|null (required) — previous SourceRecord.record_id when this version supersedes another version; null for the first accepted registration.

RightsProfile:
- record_id: string (required) — immutable storage identifier for this persisted rights profile version.
- rights_profile_id: string (required) — stable logical identifier for the rights profile.
- source_id: string (required) — SourceRecord.source_id governed by this profile.
- license_basis: string (required) — license or terms basis used to justify rights status.
- license_document_refs: list[string] (required) — LicenseDocumentRef.license_ref_id values that support the profile.
- agreement_refs: list[string] (required) — AccessAgreementRef.agreement_ref_id values that support or constrain the profile; may be empty only when license_document_refs is non-empty.
- permitted_uses: list[string] (required) — explicit uses allowed for this source.
- prohibited_uses: list[string] (required) — explicit uses prohibited or not granted for this source.
- restriction_notes: string (required) — preserved explanation of restrictions, ambiguity, contractual limits or blocking reasons.
- attribution_requirements: list[string] (required) — citation, attribution or notice obligations derived from evidence.
- rights_status: enum[allowed, allowed_with_attribution, restricted, blocked, expired, conflict] (required) — deterministic rights state derived from documented evidence.
- effective_from: date|null (required) — earliest effective date across active rights evidence when known.
- effective_to: date|null (required) — earliest expiration date across active rights evidence when known.
- evidence_observed_at: datetime (required) — latest observation timestamp among rights evidence used for this profile.
- phase_contract_ref: string (required) — motor_001 phase contract reference that authorizes rights-profile output.
- version_id: string (required) — stable technical key for this immutable RightsProfile version.
- created_at: datetime (required) — timestamp when this rights profile version was first emitted.
- updated_at: datetime (required) — timestamp when registry metadata for this immutable version was last updated.
- version_hash: string (required) — deterministic hash of normalized RightsProfile content and immutable metadata.
- source_ref: string (required) — primary license, agreement or declaration reference used to produce this RightsProfile.
- produced_by_motor: string (required) — fixed value `motor_008`.
- produced_at: datetime (required) — timestamp when motor_008 emitted this RightsProfile.
- parent_id: string|null (required) — previous RightsProfile.record_id when this version supersedes another version; null for the first accepted profile.

AccessClass:
- record_id: string (required) — immutable storage identifier for this persisted access class version.
- access_class_id: string (required) — stable logical identifier for the access classification.
- source_id: string (required) — SourceRecord.source_id governed by this class.
- rights_profile_id: string (required) — RightsProfile.rights_profile_id whose permissions and restrictions justify the class.
- access_class: enum[public, premium, restricted, contractual, internal, blocked] (required) — allowed access vocabulary for motor_008.
- assignment_reason: string (required) — deterministic reason for the assigned class.
- supporting_document_refs: list[string] (required) — license_ref_id and agreement_ref_id values used to justify the class.
- authentication_required: boolean (required) — true when the class depends on credentials, keys or login.
- payment_required: boolean (required) — true when the class depends on paid access.
- quota_notes: string|null (required) — quota, rate-limit or seat-limit statement when documented.
- embargo_until: date|null (required) — embargo date when documented.
- territorial_restrictions: list[string] (required) — geographic restrictions that affect access or use.
- effective_from: date|null (required) — first date the class is supported by active evidence when known.
- effective_to: date|null (required) — last date the class is supported by active evidence when known.
- phase_contract_ref: string (required) — motor_001 phase contract reference that authorizes access-class output.
- version_id: string (required) — stable technical key for this immutable AccessClass version.
- created_at: datetime (required) — timestamp when this access class version was first emitted.
- updated_at: datetime (required) — timestamp when registry metadata for this immutable version was last updated.
- version_hash: string (required) — deterministic hash of normalized AccessClass content and immutable metadata.
- source_ref: string (required) — primary rights profile, license or agreement reference used to produce this AccessClass.
- produced_by_motor: string (required) — fixed value `motor_008`.
- produced_at: datetime (required) — timestamp when motor_008 emitted this AccessClass.
- parent_id: string|null (required) — previous AccessClass.record_id when this version supersedes another version; null for the first accepted class.

RefreshSchedule:
- record_id: string (required) — immutable storage identifier for this persisted refresh schedule version.
- refresh_schedule_id: string (required) — stable logical identifier for the refresh schedule.
- source_id: string (required) — SourceRecord.source_id governed by this schedule.
- periodicity: enum[daily, weekly, monthly, quarterly, annual, event_driven, manual_review] (required) — explicit review cadence or trigger class.
- next_review_at: date|null (required) — next review date; null only when manual_review_condition supplies the trigger.
- manual_review_condition: string|null (required) — explicit condition for manual or event-driven review; null only when next_review_at is present.
- refresh_reason: string (required) — reason the cadence or manual condition was assigned.
- schedule_basis_refs: list[string] (required) — declaration, license or agreement references used to justify the schedule.
- phase_contract_ref: string (required) — motor_001 phase contract reference that authorizes refresh-schedule output.
- version_id: string (required) — stable technical key for this immutable RefreshSchedule version.
- created_at: datetime (required) — timestamp when this schedule version was first emitted.
- updated_at: datetime (required) — timestamp when registry metadata for this immutable version was last updated.
- version_hash: string (required) — deterministic hash of normalized RefreshSchedule content and immutable metadata.
- source_ref: string (required) — primary declaration, license or agreement reference used to produce this RefreshSchedule.
- produced_by_motor: string (required) — fixed value `motor_008`.
- produced_at: datetime (required) — timestamp when motor_008 emitted this RefreshSchedule.
- parent_id: string|null (required) — previous RefreshSchedule.record_id when this version supersedes another version; null for the first accepted schedule.

SourceRightsValidationError:
- record_id: string (required) — immutable storage identifier for this validation signal.
- error_id: string (required) — stable identifier for the emitted error.
- error_code: enum[MISSING_SOURCE_ID, MISSING_SOURCE_LOCATOR, MISSING_OWNER, MISSING_DECLARED_USE, MISSING_RIGHTS_EVIDENCE, UNTRACEABLE_DOCUMENT_REF, INVALID_LICENSE_DATES, EXPIRED_ACCESS_AGREEMENT, RIGHTS_CONFLICT, INVALID_ACCESS_CLASS, MISSING_REFRESH_DISCIPLINE, CONTRACT_SCOPE_VIOLATION] (required) — machine-readable rejection or warning reason.
- source_id: string|null (required) — affected source_id when known; null only when the source identifier itself is missing.
- rejected_input_ref: string (required) — declaration, license reference, agreement reference or derived object that failed validation.
- field_path: string (required) — dotted path to the invalid, missing or conflicting field.
- message: string (required) — concise human-readable explanation of the validation result.
- blocking: boolean (required) — true when the error prevents emission of source_registration, rights_profile, access_class or refresh_schedule.
- detected_at: datetime (required) — timestamp when the validation result was detected.
- phase_contract_ref: string|null (required) — motor_001 phase contract reference when supplied; null only for contract-reference validation failures.
- version_id: string (required) — stable technical key for this immutable validation signal.
- created_at: datetime (required) — timestamp when this validation signal was first emitted.
- updated_at: datetime (required) — immutable audit timestamp; for validation errors it must equal created_at.
- version_hash: string (required) — deterministic hash of normalized validation-error content and immutable metadata.
- source_ref: string (required) — declaration, license, agreement or output reference that caused the validation signal.
- produced_by_motor: string (required) — fixed value `motor_008`.
- produced_at: datetime (required) — timestamp when motor_008 emitted this validation signal.
- parent_id: string|null (required) — prior SourceRightsValidationError.record_id if a later validation supersedes an earlier signal; null for a new signal.

## relationships
- LicenseDocumentRef.source_id references SourceDeclaration.source_id.
- AccessAgreementRef.source_id references SourceDeclaration.source_id.
- SourceRecord.source_id is derived from exactly one accepted SourceDeclaration.source_id.
- SourceRecord.evidence_refs references accepted LicenseDocumentRef.license_ref_id and AccessAgreementRef.agreement_ref_id values; at least one evidence reference must exist before registration.
- SourceRecord.rights_profile_id references the current RightsProfile.rights_profile_id for the same source_id.
- SourceRecord.access_class_id references the current AccessClass.access_class_id for the same source_id.
- SourceRecord.refresh_schedule_id references the current RefreshSchedule.refresh_schedule_id for the same source_id.
- RightsProfile.source_id references SourceRecord.source_id and there must be exactly one current RightsProfile per current SourceRecord.
- RightsProfile.license_document_refs reference LicenseDocumentRef.license_ref_id values for the same source_id.
- RightsProfile.agreement_refs reference AccessAgreementRef.agreement_ref_id values for the same source_id when agreements are present.
- AccessClass.source_id references SourceRecord.source_id and there must be exactly one current AccessClass per current SourceRecord.
- AccessClass.rights_profile_id references RightsProfile.rights_profile_id; access_class assignment must be justified by the referenced profile and supporting_document_refs.
- RefreshSchedule.source_id references SourceRecord.source_id and there must be exactly one current RefreshSchedule per current SourceRecord.
- SourceRightsValidationError.rejected_input_ref references the declaration, license, agreement or derived output that failed validation.
- phase_contract_ref fields reference the governing motor_001 phase contract; motor_008 stores and validates the reference but does not modify motor_001 contracts.
- parent_id on persisted outputs references a prior record_id of the same entity type only when a governed version supersedes another version.
- No relationship may point to raw ingested source payloads, parsed records, normalized records, quality scores, identity matches or inference outputs.

## identifiers
- SourceDeclaration stable identifier: source_id; declaration_ref identifies the submitted declaration instance.
- LicenseDocumentRef stable identifier: license_ref_id, derived from source_id, document_ref and observed_at when deterministic generation is available.
- AccessAgreementRef stable identifier: agreement_ref_id, derived from source_id, document_ref and observed_at when deterministic generation is available.
- SourceRecord storage identifier: record_id; canonical logical identifier: source_id.
- RightsProfile storage identifier: record_id; canonical logical identifier: rights_profile_id.
- AccessClass storage identifier: record_id; canonical logical identifier: access_class_id.
- RefreshSchedule storage identifier: record_id; canonical logical identifier: refresh_schedule_id.
- SourceRightsValidationError storage identifier: record_id; canonical logical identifier: error_id.
- record_id identifies one immutable persisted version and must not be reused across entity types or material versions.
- source_id is the shared source key across source_registration, rights_profile, access_class and refresh_schedule outputs.
- Deterministic identifier generation should use normalized entity type, source_id, logical identifier, evidence references, version key and content hash so duplicate identical submissions remain idempotent.
- Empty identifiers, reused identifiers across incompatible content or conflicting identifiers with different version_hash values are invalid and produce SourceRightsValidationError rather than silent mutation.

## versioning
- Every persisted motor_008 output includes version_id, created_at, updated_at and version_hash.
- version_id identifies one immutable version of SourceRecord, RightsProfile, AccessClass, RefreshSchedule or SourceRightsValidationError.
- created_at is set once when motor_008 emits the persisted version.
- updated_at records registry metadata updates for the same immutable version. For immutable validation errors, updated_at must equal created_at.
- version_hash is computed deterministically from normalized material content, logical identifiers, evidence references, phase_contract_ref, lineage fields and parent linkage, excluding non-material registry timestamps.
- A material change to source locator, owner, declared use, license basis, permitted uses, prohibited uses, restriction notes, access class, refresh cadence, evidence references, phase contract reference or parent linkage creates a new record_id, new version_id and new version_hash.
- A duplicate submission with the same logical identifier and same version_hash is idempotent.
- A duplicate source_id, rights_profile_id, access_class_id or refresh_schedule_id with a different version_hash and no explicit parent_id is rejected with SourceRightsValidationError.
- Current records, historical records and validation signals remain separate. Superseding versions link to earlier immutable records through parent_id rather than rewriting prior content.
- SourceDeclaration, LicenseDocumentRef and AccessAgreementRef are input DTOs; they are preserved through accepted output lineage or SourceRightsValidationError records rather than treated as published registry outputs.

## lineage
- Every persisted motor_008 output includes source_ref, produced_by_motor, produced_at and parent_id.
- source_ref records the primary declaration, license document, access agreement or derived output reference used to construct the persisted entity.
- produced_by_motor is always motor_008 for records emitted by the Source Registry + Rights Engine.
- produced_at records when motor_008 emitted the accepted output or validation signal, independent of the observed_at timestamp on license or agreement evidence.
- parent_id links a superseding persisted record to the previous immutable record_id; it is null when no predecessor exists.
- Accepted SourceRecord, RightsProfile, AccessClass and RefreshSchedule records retain source provenance through declaration_ref, license_document_refs, agreement_refs, supporting_document_refs, schedule_basis_refs and the governing phase_contract_ref.
- SourceRightsValidationError records retain enough lineage to reconstruct the failed input, the failed field path, the evidence reference, the phase contract reference when present and the blocking decision.
- The motor does not infer missing rights evidence from public visibility, source reputation or downstream use. Missing source_ref, produced_by_motor, produced_at, parent_id where required, document_ref or observed_at produces SourceRightsValidationError.
- Lineage for source registration history is explicit: operational links use source_id and current output identifiers, while historical supersession uses parent_id; these references must not be collapsed.
- Downstream motors consume source_registration, rights_profile, access_class and refresh_schedule by reference. They do not gain authority to rewrite motor_008 lineage, identifiers, rights metadata or version history.
