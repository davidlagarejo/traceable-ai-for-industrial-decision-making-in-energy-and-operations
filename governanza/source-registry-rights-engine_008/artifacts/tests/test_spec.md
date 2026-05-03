# Test Spec — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.

All placeholder markers have been resolved for Gate 3 review.
-->

## happy_path
Fixture `valid_public_api_registration`:

Input:
- Execution context supplies `phase_contract_ref = "phase_contract:motor_001:research_registry:v1"`.
- `source_declarations` contains one `SourceDeclaration`:
  - `source_id = "src_eia_api"`
  - `source_name = "U.S. Energy Information Administration API"`
  - `source_locator = "https://api.eia.gov"`
  - `source_type = "api"`
  - `declared_owner = "U.S. Energy Information Administration"`
  - `declared_use = "public_contextual_energy_data"`
  - `declared_refresh = "monthly"`
  - `declaration_ref = "declarations/src_eia_api_2026-04-01.json"`
  - `submitted_by = "source_registry_operator"`
  - `submitted_at = "2026-04-01T10:00:00Z"`
- `license_files` contains one `LicenseDocumentRef`:
  - `license_ref_id = "lic_eia_terms_20260401"`
  - `source_id = "src_eia_api"`
  - `document_ref = "licenses/eia_terms_2026-04-01.pdf"`
  - `license_basis = "public government terms with attribution requirement"`
  - `permitted_uses = ["analysis", "reporting", "derived_metadata"]`
  - `prohibited_uses = ["misattribution", "source_impersonation"]`
  - `restriction_notes = "Attribution to EIA required; no claim of EIA endorsement."`
  - `attribution_requirements = ["cite U.S. Energy Information Administration"]`
  - `effective_from = null`
  - `effective_to = null`
  - `observed_at = "2026-04-01T09:30:00Z"`
- `access_agreements` contains one `AccessAgreementRef`:
  - `agreement_ref_id = "agr_eia_api_key_20260401"`
  - `source_id = "src_eia_api"`
  - `document_ref = "agreements/eia_api_key_terms_2026-04-01.pdf"`
  - `access_basis = "public API key registration"`
  - `authentication_required = true`
  - `payment_required = false`
  - `quota_notes = "API key rate limit applies according to public terms."`
  - `embargo_until = null`
  - `territorial_restrictions = []`
  - `permitted_uses = ["analysis", "reporting", "derived_metadata"]`
  - `prohibited_uses = ["credential_sharing"]`
  - `effective_from = "2026-04-01"`
  - `effective_to = null`
  - `observed_at = "2026-04-01T09:40:00Z"`

Expected output:
- `source_registration.source_id = "src_eia_api"`, `registration_status = "active"`, `evidence_refs = ["lic_eia_terms_20260401", "agr_eia_api_key_20260401"]`, and `declaration_ref = "declarations/src_eia_api_2026-04-01.json"`.
- `rights_profile.source_id = "src_eia_api"`, `rights_status = "allowed_with_attribution"`, `license_basis = "public government terms with attribution requirement"`, `permitted_uses` includes `analysis`, `reporting`, and `derived_metadata`, and `prohibited_uses` includes `misattribution`, `source_impersonation`, and `credential_sharing`.
- `access_class.source_id = "src_eia_api"`, `access_class = "public"`, `authentication_required = true`, `payment_required = false`, and `supporting_document_refs` includes both evidence references.
- `refresh_schedule.source_id = "src_eia_api"`, `periodicity = "monthly"`, `next_review_at = "2026-05-01"`, `manual_review_condition = null`, and `schedule_basis_refs` includes the declaration and license references.
- All four accepted outputs preserve `phase_contract_ref = "phase_contract:motor_001:research_registry:v1"`, `produced_by_motor = "motor_008"`, non-empty `record_id`, `version_id`, `version_hash`, `source_ref`, `created_at`, `updated_at`, `produced_at`, and `parent_id = null`.

## sparse_case
Fixture `license_only_manual_review_registration`:

Input:
- Execution context supplies `phase_contract_ref = "phase_contract:motor_001:research_registry:v1"`.
- `source_declarations` contains one `SourceDeclaration` with required identity fields present:
  - `source_id = "src_city_open_data_catalog"`
  - `source_name = "City Open Data Catalog"`
  - `source_locator = "https://data.example-city.gov/catalog"`
  - `source_type = "open_data_catalog"`
  - `declared_owner = "Example City Data Office"`
  - `declared_use = "public_records_context"`
  - `declared_refresh = null`
  - `declaration_ref = "declarations/src_city_open_data_catalog_2026-04-02.json"`
  - `submitted_by = "municipal_sources_queue"`
  - `submitted_at = "2026-04-02T14:05:00Z"`
- `license_files` contains one `LicenseDocumentRef`:
  - `license_ref_id = "lic_city_open_terms_20260402"`
  - `source_id = "src_city_open_data_catalog"`
  - `document_ref = "licenses/city_open_terms_2026-04-02.html"`
  - `license_basis = "open data terms"`
  - `permitted_uses = ["analysis", "reporting"]`
  - `prohibited_uses = ["endorsement_claims"]`
  - `restriction_notes = "The terms page states updates are irregular; review when terms page changes."`
  - `attribution_requirements = []`
  - `effective_from = null`
  - `effective_to = null`
  - `observed_at = "2026-04-02T13:55:00Z"`
- `access_agreements = []`.

Expected behavior:
- The motor accepts the source because at least one traceable rights document exists even though no separate access agreement is present.
- `rights_profile.rights_status = "allowed"` because the license explicitly permits the declared uses and has no attribution requirement.
- `access_class.access_class = "public"`, `authentication_required = false`, `payment_required = false`, `quota_notes = null`, `embargo_until = null`, and `territorial_restrictions = []`.
- `refresh_schedule.periodicity = "manual_review"`, `next_review_at = null`, and `manual_review_condition = "on_terms_page_change"` because fixed cadence is absent but a manual review trigger is documented.
- The motor must not invent missing optional evidence, infer a fixed cadence, or treat the empty `access_agreements` list as a fatal error.

## malformed_input
Fixture `invalid_declaration_and_untraceable_license`:

Input:
- `source_declarations` contains one malformed `SourceDeclaration`:
  - `source_id = ""`
  - `source_name = "Unnamed Premium News Feed"`
  - `source_locator = ""`
  - `source_type = "subscription_feed"`
  - `declared_owner = "Example News Vendor"`
  - `declared_use = ["analysis", "reporting"]`
  - `declared_refresh = "daily"`
  - `declaration_ref = "declarations/news_feed_invalid_2026-04-03.json"`
  - `submitted_by = "source_registry_operator"`
  - `submitted_at = "2026-04-03T11:00:00Z"`
- `license_files` contains one malformed `LicenseDocumentRef`:
  - `license_ref_id = "lic_news_missing_doc_20260403"`
  - `source_id = ""`
  - `document_ref = ""`
  - `license_basis = "vendor terms"`
  - `permitted_uses = ["internal_analysis"]`
  - `prohibited_uses = ["redistribution"]`
  - `restriction_notes = "Document reference omitted by submitter."`
  - `attribution_requirements = []`
  - `effective_from = "2026-04-01"`
  - `effective_to = "2026-12-31"`
  - `observed_at` is absent.
- `access_agreements = []`.

Expected rejection:
- The motor emits no `SourceRecord`, no `RightsProfile`, no `AccessClass`, and no `RefreshSchedule`.
- The validation result includes a blocking `SourceRightsValidationError` with `error_code = "MISSING_SOURCE_ID"`, `source_id = null`, `rejected_input_ref = "declarations/news_feed_invalid_2026-04-03.json"`, and `field_path = "source_declarations[0].source_id"`.
- The validation result includes a blocking `SourceRightsValidationError` with `error_code = "MISSING_SOURCE_LOCATOR"` and `field_path = "source_declarations[0].source_locator"`.
- The validation result includes a blocking `SourceRightsValidationError` with `error_code = "CONTRACT_SCOPE_VIOLATION"` and `field_path = "source_declarations[0].declared_use"` because `declared_use` must be a string, not a list.
- The validation result includes a blocking `SourceRightsValidationError` with `error_code = "UNTRACEABLE_DOCUMENT_REF"` and `field_path = "license_files[0].document_ref"` or `field_path = "license_files[0].observed_at"` for the untraceable license evidence.
- No invalid value may be repaired silently: the engine must not generate a substitute source identifier, infer a locator, coerce `declared_use` into a string, or accept a license with missing `document_ref` or `observed_at`.

## edge_cases
1. Public URL without rights evidence:
   - Input: `source_declarations[0].source_id = "src_public_blog_archive"` and `source_locator = "https://example.org/blog/archive"` are present, but `license_files = []` and `access_agreements = []`.
   - Expected behavior: reject with blocking `SourceRightsValidationError.error_code = "MISSING_RIGHTS_EVIDENCE"` at `field_path = "license_files|access_agreements"` and emit no registry outputs. Public visibility must not be treated as permission.

2. Active documents with conflicting redistribution rights:
   - Input: license `lic_market_terms_20260404` permits `external_reporting`, while agreement `agr_market_contract_20260404` for the same `source_id = "src_market_terminal"` prohibits `external_reporting` and no precedence rule is supplied.
   - Expected behavior: reject with blocking `SourceRightsValidationError.error_code = "RIGHTS_CONFLICT"`, preserve both evidence references in the validation signal, and emit no `rights_status = "allowed"` or `access_class = "public"` output.

3. Expired access agreement:
   - Input: `access_agreements[0].effective_to = "2026-03-31"` and the validation run occurs on `2026-04-04`.
   - Expected behavior: emit blocking `SourceRightsValidationError.error_code = "EXPIRED_ACCESS_AGREEMENT"` for `field_path = "access_agreements[0].effective_to"` and do not emit an allowed access class from expired evidence.

4. Identical duplicate submission:
   - Input: the exact `valid_public_api_registration` fixture is submitted twice with the same declaration, evidence references, phase contract reference, and material content.
   - Expected behavior: the second run is idempotent. It returns the same logical `source_id`, `rights_profile_id`, `access_class_id`, `refresh_schedule_id`, and `version_hash` values, does not create conflicting current records, and does not mutate the first immutable version.

5. Duplicate source identifier with different material rights content and no parent link:
   - Input: a second declaration uses `source_id = "src_eia_api"` but changes `permitted_uses` from `["analysis", "reporting", "derived_metadata"]` to `["redistribution"]` without `parent_id` or governed supersession metadata.
   - Expected behavior: reject with blocking `SourceRightsValidationError.error_code = "RIGHTS_CONFLICT"` or `error_code = "CONTRACT_SCOPE_VIOLATION"` and preserve the original current registration unchanged.

## pass_criteria
The test suite passes only when every fixture produces the specified observable result:

- Valid fixtures emit exactly the expected accepted output families: `source_registration`, `rights_profile`, `access_class`, and `refresh_schedule`.
- Invalid fixtures emit blocking `SourceRightsValidationError` records and emit no accepted registry outputs for the invalid source.
- The accepted outputs for one source all share the same `source_id` and preserve the expected evidence references through `evidence_refs`, `license_document_refs`, `agreement_refs`, `supporting_document_refs`, and `schedule_basis_refs`.
- Every accepted output includes `phase_contract_ref`, `version_id`, `version_hash`, `source_ref`, `produced_by_motor = "motor_008"`, `produced_at`, `created_at`, `updated_at`, and a correct `parent_id` value.
- `rights_status`, `access_class`, and `periodicity` values are members of their declared vocabularies and match the expected case-specific value.
- Missing rights evidence, untraceable document references, expired agreements, unsupported field types, and conflicting active rights all produce the expected structured error code, `field_path`, `rejected_input_ref`, `blocking = true`, and explanatory message.
- No test output contains raw ingested data records, normalized records, quality scores, identity matches, inference records, or output blocks from other motors.

## fail_criteria
The test suite fails if any of these conditions is observed:

- Any fixture with missing source identity, missing locator, missing rights evidence, untraceable document evidence, expired access, or conflicting rights emits a `SourceRecord`, `RightsProfile`, `AccessClass`, or `RefreshSchedule`.
- A public locator is accepted as proof of permission when no license file or access agreement is attached.
- The motor silently repairs invalid input by inventing a `source_id`, `document_ref`, `observed_at`, `phase_contract_ref`, refresh cadence, permitted use, or access class.
- A malformed field is coerced without a blocking `SourceRightsValidationError`, such as converting `declared_use = ["analysis", "reporting"]` into a string.
- Accepted outputs for the same source contain mismatched `source_id` values or omit required provenance, lineage, versioning, or evidence reference fields.
- The engine emits an access class, rights status, refresh periodicity, or validation error code outside the vocabularies defined by the technical schema.
- Duplicate identical submissions create divergent current records or different `version_hash` values.
- Duplicate material changes overwrite an existing immutable record instead of requiring governed supersession through `parent_id`.
- Any output includes source payload ingestion, quality scoring, source truth assessment, identity matching, or inference behavior outside motor_008 boundaries.
