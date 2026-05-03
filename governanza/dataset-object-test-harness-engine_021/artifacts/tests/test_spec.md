# Test Spec — Dataset / Object Test Harness Engine

Motor ID: motor_021

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
why_it_exists:  Los motores pueden pasar solos y aun así fallar juntos en integración.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    test_result, harness_report, integration_failure_log
key_objects:    TestResult, HarnessReport, IntegrationFailure
what_not_to_do: No modifica datos. No produce outputs analíticos. Solo prueba y reporta.
design_notes:   Harness transversal. Prueba el sistema integrado, no motores individuales.

Tests-stage content is filled for Gate 3 review.
-->

## happy_path
Input minimo valido:
- `phase_contracts` incluye `contract_id = PC-001-normalized-handoff`, `phase_id = normalization`, `required_outputs = [normalized_record]`, `field_requirements = [record_id, dataset_id, taxonomy_refs, version_ref, lineage_refs]`, `handoff_rules.requires_quality_record = true`, `version = 1.0.0`, `status = approved` y `provenance_refs = [PROV-PC-001]`.
- `version_records` incluye `version_id = VR-002-NR-884-v1`, `object_id = NR-884`, `object_type = normalized_record`, `object_version = 1`, `lineage_refs = [LN-SRC-12, LN-NORM-884]`, `provenance_refs = [PROV-NR-884]`, `created_at = 2026-04-18T00:00:00Z` y `change_reason = initial_normalization`.
- `canonical_taxonomy` incluye `taxonomy_id = TAX-003-main`, `taxonomy_version = 2026.04`, `allowed_terms = [sector.energy, geography.us.tx]`, `object_type_registry = [normalized_record, identity_record, quality_record]`, `relationship_types = [describes_entity]`, `status = active`, `effective_at = 2026-04-01T00:00:00Z` y `provenance_refs = [PROV-TAX-003]`.
- `normalized_records` incluye `record_id = NR-884`, `dataset_id = DS-55`, `schema_ref = PC-001-normalized-handoff`, `field_values = {entity_ref: supplier:acme-grid, amount: 1200}`, `taxonomy_refs = [sector.energy, geography.us.tx]`, `version_ref = VR-002-NR-884-v1`, `lineage_refs = [LN-SRC-12, LN-NORM-884]`, `normalized_at = 2026-04-18T00:05:00Z` y `provenance_refs = [PROV-NR-884]`.
- `identity_records` incluye `identity_id = ID-006-ENT-17`, `entity_ref = supplier:acme-grid`, `canonical_entity_id = ENT-17`, `alias_refs = [ACME Grid]`, `confidence_policy_ref = CP-006-default`, `lineage_refs = [LN-ID-17]`, `version_ref = VR-002-ID-17-v2` y `resolved_at = 2026-04-18T00:06:00Z`.
- `quality_records` incluye `quality_record_id = QR-007-NR-884`, `subject_ref = NR-884`, `phase_contract_ref = PC-001-normalized-handoff`, `evaluation_status = pass`, `quality_flags = []`, `fitness_score = 0.97`, `evaluated_at = 2026-04-18T00:07:00Z`, `version_ref = VR-002-QR-884-v1` y `provenance_refs = [PROV-QR-884]`.

Expected output:
- The harness executes `contract_required_fields_present`, `version_ref_resolves`, `taxonomy_refs_allowed`, `identity_ref_resolves` and `quality_record_present`.
- It emits exactly five `TestResult` objects with `status = pass`, `severity = info`, `error_code = null`, populated `input_refs`, populated `expected_condition`, populated `observed_condition`, `failure_ids = []`, `harness_version`, `executed_at`, `version_id`, `version_hash`, `source_ref = PC-001-normalized-handoff` or `NR-884`, and `produced_by_motor = motor_021`.
- It emits one `HarnessReport` with `status = pass`, `tested_contract_refs = [PC-001-normalized-handoff]`, `tested_object_refs` including `NR-884`, `ID-006-ENT-17`, `QR-007-NR-884`, `VR-002-NR-884-v1` and `TAX-003-main:2026.04`, `result_counts = {pass: 5, warning: 0, fail: 0, skipped: 0}`, `failure_ids = []`, `failure_log_ref = null`, a non-empty `coverage_summary`, and `produced_by_motor = motor_021`.
- It emits `integration_failure_log = []` and does not modify any input object.

## sparse_case
Input with optional fields absent:
- `phase_contracts`, `version_records`, `canonical_taxonomy`, `normalized_records` and `quality_records` are the same as the happy path.
- `identity_records` contains `identity_id = ID-006-ENT-17`, `entity_ref = supplier:acme-grid`, `canonical_entity_id = ENT-17`, `lineage_refs = [LN-ID-17]`, `version_ref = VR-002-ID-17-v2` and `resolved_at = 2026-04-18T00:06:00Z`, but omits optional `alias_refs`.
- `quality_records[0].quality_flags = []` and no optional explanatory notes are supplied.

Expected output:
- The harness accepts the batch because all required fields and resolvable references are present.
- `identity_ref_resolves` returns `TestResult.status = pass` with `observed_condition = identity ID-006-ENT-17 resolves supplier:acme-grid to ENT-17 without alias evidence`.
- The `HarnessReport.status` remains `pass`, `result_counts.fail = 0`, and no `IntegrationFailure` is emitted for omitted optional alias or note fields.
- Coverage metadata records that optional alias evidence was absent, without changing source identity or quality records.

## malformed_input
Malformed input case:
- `phase_contracts` is a string value `PC-001-normalized-handoff` instead of a list of structured contract objects.
- `canonical_taxonomy` is present but omits `taxonomy_version`.
- `normalized_records` contains `record_id = NR-884` and `version_ref = VR-unknown`, where `VR-unknown` is not present in `version_records`.

Expected rejection:
- The harness rejects the batch before producing an aggregate `pass` report.
- The primary structured error is `INVALID_HARNESS_INPUT` for the non-collection `phase_contracts` and incomplete taxonomy authority.
- If validation proceeds far enough to inspect the normalized record, the unresolved version reference is reported as `UNRESOLVED_REFERENCE` with `affected_object_ref = NR-884`, `expected_ref = version_records.version_id`, `observed_value = VR-unknown`, `owner_motor_ref = motor_005` for the bad object reference, and `source_input_refs` containing `NR-884`.
- No source contract, taxonomy, version, normalized, identity or quality object is modified or filled in by the harness.

## edge_cases
1. Empty object set with valid authorities:
   - Input: `phase_contracts`, `version_records`, `canonical_taxonomy`, `identity_records` and `quality_records` are structured and valid, but `normalized_records = []`.
   - Expected behavior: cases that require a normalized record emit `TestResult.status = skipped`, `severity = warning`, populated `input_refs` for the authorities used, and no fabricated `tested_object_refs`. `HarnessReport.status = warning` when required object coverage is incomplete, with `coverage_summary.required_cases_skipped` listing the skipped case names.

2. Taxonomy snapshot contains many unused allowed terms:
   - Input: `canonical_taxonomy.allowed_terms` contains 500 terms, while `normalized_records[0].taxonomy_refs = [sector.energy, geography.us.tx]`.
   - Expected behavior: the harness validates only observed taxonomy references against the snapshot. It does not fail because unused allowed terms are present, and `taxonomy_refs_allowed` emits `status = pass` when the two observed terms are allowed.

3. Critical taxonomy mismatch:
   - Input: `normalized_records[0].taxonomy_refs = [sector.unregistered]` and `canonical_taxonomy.allowed_terms = [sector.energy, geography.us.tx]`.
   - Expected behavior: `taxonomy_refs_allowed` emits `TestResult.status = fail`, `severity = critical`, `error_code = TAXONOMY_MISMATCH`, and one `IntegrationFailure` with `failure_type = taxonomy_mismatch`, `affected_object_ref = NR-884`, `expected_ref = TAX-003-main:2026.04`, `observed_value = sector.unregistered`, `owner_motor_ref = motor_005`, and source refs for the normalized record and taxonomy snapshot. `HarnessReport.status = fail`.

4. Report reconciliation guard:
   - Input: executable cases produce three pass results, one warning result and one fail result.
   - Expected behavior: `HarnessReport.result_counts` must equal `{pass: 3, warning: 1, fail: 1, skipped: 0}` and `test_result_ids` must contain five result ids. If any aggregate count differs from the result list, report emission is rejected with `UNSAFE_HARNESS_REPORT`.

## pass_criteria
The test specification passes when these observable conditions are true:
- Every required input accepted by a case is structured, has stable identifiers, and carries the provenance, lineage or version references required by its contract.
- Every emitted `TestResult` includes `test_id`, `harness_run_id`, `case_name`, `case_version`, `status`, `input_refs`, `expected_condition`, `observed_condition`, `failure_ids`, `severity`, `error_code`, `harness_version`, `executed_at`, versioning fields, lineage fields and `produced_by_motor = motor_021`.
- A passing case has `status = pass`, `severity = info`, `error_code = null`, `failure_ids = []`, and an `observed_condition` that satisfies the declared `expected_condition`.
- `HarnessReport.result_counts` reconciles exactly with linked `TestResult.status` values, `failure_ids` reconciles with `integration_failure_log`, and `status = pass` appears only when there are no required failures, no critical failures and no failed required test results.
- `integration_failure_log` is empty for the happy path and contains structured `IntegrationFailure` objects for warning or fail outcomes.

## fail_criteria
The test specification fails when any of these observable conditions occur:
- Any required authority input has the wrong type, lacks required identifiers, lacks required provenance or lineage, or contains an unresolved cross-reference that should have been rejected.
- A required case emits `status = pass` while a contract field is missing, a taxonomy term is not allowed, a `version_ref` cannot be resolved, identity evidence is incompatible, quality evidence is missing when required, or lineage cannot be reconstructed.
- Any `TestResult` omits required result, versioning or lineage fields, uses an unrecognized `status`, `severity` or `error_code`, or links a `failure_id` that does not exist in `integration_failure_log`.
- Any `IntegrationFailure` omits `failure_type`, `affected_object_ref`, `expected_ref`, `observed_value`, `source_input_refs`, `severity`, `owner_motor_ref`, `recommended_action` or lineage/versioning fields.
- `HarnessReport.status = pass` when at least one required `TestResult.status = fail`, when a linked failure has `severity = critical`, or when `result_counts` do not match the linked result list.
- The harness mutates, repairs, normalizes, retaxonomizes, reidentifies or rescores any upstream input instead of only testing and reporting it.
