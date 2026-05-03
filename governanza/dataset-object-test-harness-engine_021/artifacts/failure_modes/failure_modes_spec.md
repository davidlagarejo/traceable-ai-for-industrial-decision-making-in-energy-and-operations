# Failure Modes Spec — Dataset / Object Test Harness Engine

Motor ID: motor_021

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
why_it_exists:  Los motores pueden pasar solos y aun así fallar juntos en integración.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    test_result, harness_report, integration_failure_log
key_objects:    TestResult, HarnessReport, IntegrationFailure
what_not_to_do: No modifica datos. No produce outputs analíticos. Solo prueba y reporta.
design_notes:   Harness transversal. Prueba el sistema integrado, no motores individuales.
-->

## failure_modes_list
- FALSE_PASS_ON_BROKEN_HANDOFF: a `normalized_record`, `identity_record`, `quality_record` or handoff object misses fields required by an active `phase_contract`, but the required case emits `TestResult.status = pass` -> downstream engines consume an object that appears integration-safe while later contract checks fail repeatedly -> reject the result, emit `IntegrationFailure.failure_type = contract_mismatch`, set `HarnessReport.status = fail` when severity is critical, and route correction to the upstream owner motor without modifying the object.
- UNRESOLVED_REFERENCE_ESCAPES: `version_ref`, `taxonomy_ref`, `identity_ref`, `quality_record.subject_ref` or `phase_contract_ref` does not resolve inside the accepted input batch -> the harness report contains green coverage with broken `input_refs` or missing `IntegrationFailure` evidence -> emit `UNRESOLVED_REFERENCE`, bind the failure to the affected object and expected authority, and block aggregate `pass` until every linked reference is either resolved or explicitly reported as skipped or failed.
- LINEAGE_GAP_UNDETECTED: an object under test lacks required `lineage_refs`, `provenance_refs` or a resolvable `version_record`, but the harness validates only surface shape -> rebuild and audit paths cannot reconstruct why the object passed integration -> emit `LINEAGE_GAP`, set severity to `critical` when lineage is contract-required, and preserve the observed missing reference in `IntegrationFailure.observed_value`.
- TAXONOMY_DRIFT_ACCEPTED: a normalized object uses a term, object type or relationship not present in the provided `canonical_taxonomy` snapshot -> invalid terms propagate into integration reports as if they were canonical -> emit `TAXONOMY_MISMATCH`, use the taxonomy snapshot version as `expected_ref`, set `owner_motor_ref` to the producing motor for the bad reference, and fail the report when the term is required for the handoff.
- REPORT_RECONCILIATION_BREAK: `HarnessReport.result_counts`, `test_result_ids`, `failure_ids` or `failure_log_ref` does not reconcile with emitted `TestResult` and `IntegrationFailure` objects -> operators cannot trust aggregate pass, warning or fail status -> reject report emission with `UNSAFE_HARNESS_REPORT`, regenerate the aggregate from the canonical result list, and never downgrade a critical linked failure to `pass`.
- COVERAGE_INFLATION: required cases are skipped because inputs are missing, malformed or outside the case preconditions, but `coverage_summary` reports full coverage -> integration readiness is overstated and missing tests become invisible -> record each skipped required case with populated authority `input_refs`, set the report to `warning` or `fail` according to contract severity, and list skipped cases with deterministic reasons.
- HARNESS_SCOPE_OVERREACH: the harness fills missing fields, maps taxonomy terms, merges identities, creates quality scores or updates upstream state while testing -> the true owning motor never receives a visible correction signal and source objects are silently mutated -> abort the run as an unsafe harness operation, emit a critical failure or implementation defect record, and restore execution to read-only validation and reporting.
- NONDETERMINISTIC_RUN_OUTPUT: the same ordered input set, case definitions and `harness_version` produce different IDs, statuses, counts or hashes across runs -> audit comparisons and rebuild checks cannot distinguish real input change from harness drift -> canonicalize input ordering, derive IDs and hashes from stable fields, exclude non-semantic timestamps from hash material when required, and treat unexplained drift as a failed harness self-check.

## anti_patterns
- Mutating or repairing source inputs during test execution, including completing missing lineage, retaxonomizing values, correcting contracts, merging identities or rescoring quality records.
- Treating narrative messages as sufficient output instead of structured `TestResult`, `HarnessReport` and `IntegrationFailure` records with stable identifiers, input references, expected conditions, observed conditions, severity and version metadata.
- Coupling test logic directly to one upstream motor implementation instead of evaluating the explicit objects and contracts supplied to the run.
- Declaring integration success from isolated producer checks without validating cross-object handoffs among contracts, versions, taxonomy snapshots, normalized records, identity records and quality records.
- Using implicit, unversioned test rules that make `case_name`, `case_version`, `harness_version` and deterministic result reproduction impossible.
- Collapsing `skipped`, `warning` and `fail` into `pass` to keep a pipeline green, especially when required objects are absent or critical references do not resolve.
- Emitting aggregate reports before reconciling result counts, linked failure identifiers and failure log contents.
- Assigning failures to generic owners such as `unknown` or `system` when the observed condition identifies a likely upstream owner motor.
- Converting this motor into a conformance approval engine; motor_021 reports dataset/object integration test outcomes and does not approve architectural conformity or close gates for other motors.

## degradation_signals
- `HarnessReport.result_counts` differs from the count of linked `TestResult.status` values, even by one result.
- Any `HarnessReport.status = pass` while a linked `IntegrationFailure.severity = critical` exists or a required `TestResult.status = fail` exists.
- Increasing ratio of `skipped` required cases without explicit `coverage_summary.required_cases_skipped` reasons and authority `input_refs`.
- Repeated `UNRESOLVED_REFERENCE`, `TAXONOMY_MISMATCH` or `LINEAGE_GAP` for the same contract or object type across runs with unchanged upstream versions.
- Any `TestResult` missing `input_refs`, `expected_condition`, `observed_condition`, `harness_version`, `case_version`, `version_hash` or `produced_by_motor = motor_021`.
- Any `IntegrationFailure` missing `affected_object_ref`, `expected_ref`, `observed_value`, `source_input_refs`, `severity`, `owner_motor_ref` or a link back to its detecting `TestResult`.
- Stable input set and stable `harness_version` produce different deterministic IDs, status decisions or semantic hashes between two executions.
- Failure logs contain failures not linked by `TestResult.failure_ids`, or results link `failure_ids` absent from the run-level failure log.
- Logs contain phrases or event types indicating input modification by the harness, such as source object rewrite, taxonomy repair, identity merge, quality score update or contract patch.
- Large growth in `warning` results with no corresponding owner routing or recommended action, indicating that warning states are becoming untriaged backlog rather than controlled degradation.

## expensive_errors
- Silent false pass on contract-required fields: expensive because downstream reports, rebuild jobs and conformance checks may rely on objects that never satisfied their handoff contract; prevented by strict required-field cases, critical `CONTRACT_MISMATCH` failures and a rule that aggregate `pass` is impossible while required cases fail.
- Broken lineage accepted as valid: expensive because later audits cannot reconstruct source evidence or determine which version introduced the defect; prevented by mandatory lineage and provenance checks against `version_records` before any `TestResult.status = pass`.
- Taxonomy drift hidden by local coercion: expensive because non-canonical terms can contaminate joins, coverage metrics and entity comparisons across datasets; prevented by validating observed terms only against the supplied taxonomy snapshot and reporting mismatches without mapping or inventing terms.
- Unreconciled report counts: expensive because operators may trust a green aggregate while failed results or critical failures exist in the detailed log; prevented by deriving `result_counts`, `failure_ids` and `status` from the canonical result and failure lists and rejecting inconsistent aggregates with `UNSAFE_HARNESS_REPORT`.
- Harness mutation of upstream records: expensive because it destroys accountability for the producing motor and can overwrite evidence needed for correction; prevented by read-only input handling, explicit forbidden-operation checks and output-only correction recommendations.
- Unversioned test rule changes: expensive because a status change cannot be traced to input drift versus harness-rule drift; prevented by requiring `case_version`, `harness_version`, deterministic identifiers and semantic hashes on every emitted output.
- Missing owner routing on integration failures: expensive because remediation stalls and failures become generic operational noise; prevented by requiring `owner_motor_ref` and `recommended_action` for each `IntegrationFailure` based on the authority that was violated and the object that supplied the bad value.
