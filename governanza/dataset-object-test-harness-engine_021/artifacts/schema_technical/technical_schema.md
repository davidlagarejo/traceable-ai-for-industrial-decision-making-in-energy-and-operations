# Technical Schema — Dataset / Object Test Harness Engine

Motor ID: motor_021

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
why_it_exists:  Los motores pueden pasar solos y aun así fallar juntos en integración.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    test_result, harness_report, integration_failure_log
key_objects:    TestResult, HarnessReport, IntegrationFailure
what_not_to_do: No modifica datos. No produce outputs analíticos. Solo prueba y reporta.
design_notes:   Harness transversal. Prueba el sistema integrado, no motores individuales.

Schema content is completed for Gate 2 review.
-->

## entities
- `TestResult`: technical record emitted by the schema_technical and implementation stages for one deterministic harness case executed against datasets, handoffs, contracts, or objects. It records the case identity, evaluated inputs, expected condition, observed condition, status, severity, failure links, version metadata, and lineage metadata. It does not mutate or repair the tested object.
- `HarnessReport`: technical aggregate emitted by the schema_technical and implementation stages for one harness run. It groups the `TestResult` records and `IntegrationFailure` records produced in the run, records coverage and status counts, and emits the operational decision `pass`, `warning`, or `fail`. It is a report of integration test outcomes, not an architectural conformance approval.
- `IntegrationFailure`: technical failure record emitted when a harness case detects a contract mismatch, taxonomy mismatch, unresolved reference, lineage gap, identity conflict, missing quality evidence, or incompatible handoff. It identifies the affected object, expected authority, observed value, source evidence, severity, suggested owner motor, version metadata, and lineage metadata.

## fields
`TestResult`
- `test_id`: string (required) -- stable identifier for this test result.
- `harness_run_id`: string (required) -- stable reference to the `HarnessReport` run that aggregates this result.
- `case_name`: string (required) -- deterministic test case name, such as `contract_required_fields_present`, `version_ref_resolves`, `taxonomy_refs_allowed`, `identity_ref_resolves`, or `quality_record_present`.
- `case_version`: string (required) -- version of the test case definition used for execution.
- `status`: enum string (required) -- one of `pass`, `warning`, `fail`, or `skipped`.
- `input_refs`: list[string] (required) -- identifiers of phase contracts, version records, taxonomy snapshots, normalized records, identity records, or quality records evaluated by the case.
- `expected_condition`: string (required) -- canonical statement of the condition required by the contract, taxonomy, lineage, identity, quality, or handoff rule.
- `observed_condition`: string (required) -- canonical statement of the observed condition in the accepted inputs.
- `failure_ids`: list[string] (required) -- `IntegrationFailure.failure_id` values produced by this case; empty when no failure is produced.
- `severity`: enum string (required) -- one of `info`, `warning`, or `critical`; `pass` results use `info`, warnings use `warning`, and hard failures use `critical` when downstream safety is compromised.
- `error_code`: enum string|null (required) -- one of `INVALID_HARNESS_INPUT`, `UNRESOLVED_REFERENCE`, `CONTRACT_MISMATCH`, `TAXONOMY_MISMATCH`, `LINEAGE_GAP`, `UNSAFE_HARNESS_REPORT`, or null when the case has no structured error.
- `harness_version`: string (required) -- version of the deterministic harness rules used to execute the case.
- `executed_at`: datetime string (required) -- timestamp when the case was executed.
- `version_id`: string (required) -- version identifier for this `TestResult` record.
- `created_at`: datetime string (required) -- timestamp when this result record was created.
- `updated_at`: datetime string (required) -- timestamp for the latest state-preserving update to this result record; equals `created_at` when no later update exists.
- `version_hash`: string (required) -- deterministic hash over the canonical serialized result fields.
- `source_ref`: string (required) -- primary input or contract reference that caused this result to exist.
- `produced_by_motor`: string (required) -- constant value `motor_021`.
- `produced_at`: datetime string (required) -- timestamp when motor_021 emitted this result.
- `parent_id`: string|null (required) -- parent `HarnessReport.harness_run_id` when the result is already aggregated; null only while staging an unaggregated result inside the same run.

`HarnessReport`
- `harness_run_id`: string (required) -- stable identifier for one harness execution and the canonical identifier for this report.
- `harness_version`: string (required) -- version of the deterministic harness rules used for the run.
- `test_result_ids`: list[string] (required) -- ordered list of `TestResult.test_id` values included in this report.
- `tested_contract_refs`: list[string] (required) -- `phase_contracts.contract_id` values tested by the run.
- `tested_object_refs`: list[string] (required) -- stable identifiers of normalized records, identity records, quality records, version records, taxonomy snapshots, or handoff objects tested by the run.
- `result_counts`: object (required) -- integer counts for `pass`, `warning`, `fail`, and `skipped` results; counts must match `test_result_ids`.
- `coverage_summary`: object (required) -- deterministic coverage summary describing required cases executed, required cases skipped, objects covered, contracts covered, and reasons for partial coverage.
- `failure_ids`: list[string] (required) -- `IntegrationFailure.failure_id` values linked to this run; empty when no integration failure is detected.
- `failure_log_ref`: string|null (required) -- persisted reference to the materialized integration failure log when stored separately; null when the failure list is embedded in the report.
- `status`: enum string (required) -- one of `pass`, `warning`, or `fail`; cannot be `pass` when any linked failure has severity `critical` or any required `TestResult.status` is `fail`.
- `decision_reason`: string (required) -- deterministic explanation for the aggregate status, based on counts, severity, and coverage.
- `generated_at`: datetime string (required) -- timestamp when the report was generated.
- `version_id`: string (required) -- version identifier for this `HarnessReport` record.
- `created_at`: datetime string (required) -- timestamp when this report record was created.
- `updated_at`: datetime string (required) -- timestamp for the latest state-preserving update to this report record; equals `created_at` when no later update exists.
- `version_hash`: string (required) -- deterministic hash over the canonical serialized report fields.
- `source_ref`: string (required) -- primary run input reference, normally the run manifest or ordered set of accepted input references.
- `produced_by_motor`: string (required) -- constant value `motor_021`.
- `produced_at`: datetime string (required) -- timestamp when motor_021 emitted this report.
- `parent_id`: string|null (required) -- prior `HarnessReport.harness_run_id` when this report supersedes a previous report for the same input set and harness version; null for a root run.

`IntegrationFailure`
- `failure_id`: string (required) -- stable identifier for this integration failure.
- `harness_run_id`: string (required) -- reference to the `HarnessReport` run that contains this failure.
- `test_id`: string (required) -- reference to the `TestResult` that detected this failure.
- `failure_type`: enum string (required) -- one of `contract_mismatch`, `taxonomy_mismatch`, `unresolved_reference`, `lineage_gap`, `identity_conflict`, `quality_missing`, or `handoff_incompatible`.
- `affected_object_ref`: string (required) -- stable identifier of the object, record, handoff, contract output, or dataset element affected by the failure.
- `expected_ref`: string (required) -- contract, taxonomy, version, identity, quality, or lineage authority reference that defines the expected condition.
- `observed_value`: string (required) -- canonical representation of the value, reference, field set, or absence observed in the input batch.
- `source_input_refs`: list[string] (required) -- input references used as evidence for the failure.
- `severity`: enum string (required) -- one of `warning` or `critical`.
- `owner_motor_ref`: string (required) -- suggested producer motor responsible for correction, such as `motor_001`, `motor_002`, `motor_003`, `motor_005`, `motor_006`, or `motor_007`.
- `recommended_action`: string (required) -- deterministic correction direction for the owning workflow, expressed without modifying the object in this motor.
- `detected_at`: datetime string (required) -- timestamp when the failure was detected.
- `version_id`: string (required) -- version identifier for this `IntegrationFailure` record.
- `created_at`: datetime string (required) -- timestamp when this failure record was created.
- `updated_at`: datetime string (required) -- timestamp for the latest state-preserving update to this failure record; equals `created_at` when no later update exists.
- `version_hash`: string (required) -- deterministic hash over the canonical serialized failure fields.
- `source_ref`: string (required) -- primary input reference that caused this failure to exist.
- `produced_by_motor`: string (required) -- constant value `motor_021`.
- `produced_at`: datetime string (required) -- timestamp when motor_021 emitted this failure.
- `parent_id`: string|null (required) -- parent `TestResult.test_id`; null only for a batch-level input rejection that prevents case execution.

## relationships
- `phase_contracts.contract_id` -> `TestResult.input_refs`: external reference from motor_001; contract fields, required outputs, limits, and handoff rules are authority for contract and handoff cases.
- `version_records.version_id` -> `TestResult.input_refs`: external reference from motor_002; version and lineage records are evidence for version resolution and reconstructibility cases.
- `canonical_taxonomy.taxonomy_id` and `canonical_taxonomy.taxonomy_version` -> `TestResult.input_refs`: external reference from motor_003; taxonomy snapshots are authority for allowed terms, object types, and relationship types.
- `normalized_records.record_id` -> `TestResult.input_refs`: external reference from motor_005; normalized records are objects under test for schema, taxonomy, version, lineage, and quality requirements.
- `identity_records.identity_id` -> `TestResult.input_refs`: external reference from motor_006; identity records are authority for entity and alias resolution checks.
- `quality_records.quality_record_id` -> `TestResult.input_refs`: external reference from motor_007; quality records are authority for required quality status and fitness evidence.
- `HarnessReport.harness_run_id` -> `TestResult.harness_run_id`: one harness report aggregates zero or many test results from the same execution.
- `TestResult.test_id` -> `IntegrationFailure.test_id`: one test result can produce zero or many integration failures.
- `IntegrationFailure.failure_id` -> `TestResult.failure_ids`: each failure linked by a result must exist in the integration failure log for the same `harness_run_id`.
- `IntegrationFailure.failure_id` -> `HarnessReport.failure_ids`: each failure linked by a report must be traceable to a `TestResult` in `test_result_ids`.
- `TestResult.test_id` -> `HarnessReport.test_result_ids`: each result counted in `result_counts` must be listed in the report.
- `HarnessReport.failure_log_ref` -> materialized `integration_failure_log`: optional storage reference for the list of `IntegrationFailure` records produced by the run.
- `IntegrationFailure.owner_motor_ref` -> upstream motor id: suggested correction ownership reference; motor_021 does not apply the correction or change upstream state.

## identifiers
- `TestResult.test_id`: canonical stable ID. It is generated deterministically from `motor_021`, `harness_run_id`, `case_name`, ordered `input_refs`, and `harness_version`.
- `HarnessReport.harness_run_id`: canonical stable ID. It is generated deterministically from `motor_021`, ordered accepted input references, selected test case set, and `harness_version`.
- `IntegrationFailure.failure_id`: canonical stable ID. It is generated deterministically from `motor_021`, `harness_run_id`, `test_id`, `failure_type`, `affected_object_ref`, `expected_ref`, and canonical `observed_value`.
- `record_id`: optional storage alias permitted for stores that require a generic key. When present, it must equal the canonical entity ID (`test_id`, `harness_run_id`, or `failure_id`) and must not replace the entity-specific identifier.
- External identifiers are never rewritten by this motor: contract ids, version ids, taxonomy ids, record ids, identity ids, quality record ids, lineage refs, provenance refs, and owner motor refs remain references to their upstream authority.

## versioning
Each `TestResult`, `HarnessReport`, and `IntegrationFailure` carries the following required versioning fields:
- `version_id`: string (required) -- stable version identifier for the emitted motor_021 output record. It versions the harness output, not the upstream object under test.
- `created_at`: datetime string (required) -- creation timestamp for the emitted record.
- `updated_at`: datetime string (required) -- timestamp for the latest state-preserving update to the emitted record; equals `created_at` when no later update exists.
- `version_hash`: string (required) -- deterministic hash over the canonical serialized record after excluding non-semantic transport metadata.

Versioning rules:
- `version_id` on motor_021 outputs does not create, mutate, or supersede upstream versions managed by motor_002.
- `version_hash` must change when any semantic field in the emitted result, report, or failure changes.
- Re-running the same input set with the same `harness_version` must produce the same canonical IDs and hashes unless timestamps are explicitly excluded from hash material.
- A report cannot change from `fail` to `pass` by editing the report; a new run with a new `harness_run_id` or new `version_id` must be emitted when inputs, case set, or harness version change.
- `harness_version` and `case_version` are rule-version references for deterministic test logic; they are separate from output `version_id`.

## lineage
Each `TestResult`, `HarnessReport`, and `IntegrationFailure` carries the following required lineage fields:
- `source_ref`: string (required) -- primary upstream reference or run input reference that caused the record to exist.
- `produced_by_motor`: string (required) -- constant value `motor_021`.
- `produced_at`: datetime string (required) -- timestamp when motor_021 emitted the record.
- `parent_id`: string|null (required) -- parent report, test result, or prior same-type record used to reconstruct the run lineage; null only for root report records or batch-level rejections without an executable case.

Lineage rules:
- `input_refs`, `source_input_refs`, `tested_contract_refs`, `tested_object_refs`, `failure_ids`, and `test_result_ids` must be sufficient to reconstruct why each output exists.
- A `TestResult` must never omit `input_refs`, `expected_condition`, `observed_condition`, `executed_at`, or `harness_version`.
- An `IntegrationFailure` must never exist without `failure_type`, `affected_object_ref`, `expected_ref`, `observed_value`, `source_input_refs`, `severity`, and `owner_motor_ref`.
- A `HarnessReport` must never claim `status = pass` if any linked `IntegrationFailure.severity = critical` or any required linked `TestResult.status = fail`.
- `HarnessReport.result_counts` must reconcile exactly with linked `TestResult.status` values.
- This motor records test lineage only; it does not create new upstream lineage nodes, modify source records, approve conformance, or close gates for other motors.
