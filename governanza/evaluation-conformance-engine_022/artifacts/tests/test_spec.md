# Test Spec — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Sections below are completed with test-stage content.
-->

## happy_path
Input bundle:
- `phase_contracts`: one contract with `contract_id=phase_contract_ingestion_v1`, `contract_version_id=pcv1`, `phase_id=ingestion`, `required_outputs=["dataset_alpha"]`, `boundary_rules=["preserve_lineage", "respect_handoff_fields"]`, `handoff_rules=["handoff.dataset_alpha.requires.versioned_output"]`.
- `version_records`: one record with `object_id=dataset_alpha`, `version_id=v3`, `lineage_id=lineage_alpha`, `created_at=2026-04-18T10:00:00Z`, `supersedes=v2`, `provenance_ref=source:ingestion_run_77`.
- `quality_records`: one record with `object_id=dataset_alpha`, `version_id=v3`, `quality_status=PASS`, `fitness_score=0.96`, `failed_checks=[]`, `evidence_refs=["quality:qr_dataset_alpha_v3"]`.
- `harness_results`: one result with `test_run_id=harness_run_11`, `target_id=dataset_alpha`, `target_version_id=v3`, `result_status=PASS`, `failed_assertions=[]`, `evidence_refs=["harness:run_11:dataset_alpha_v3"]`.

Expected behavior:
- The motor resolves `dataset_alpha@v3` to `phase_contract_ingestion_v1` and the compatible `version_record`.
- It emits exactly one `ConformanceRecord` with `record_id=motor_022:dataset:dataset_alpha:v3:phase_contract_ingestion_v1:pcv1`, `evaluated_object_id=dataset_alpha`, `evaluated_object_type=dataset`, `evaluated_version_id=v3`, `contract_id=phase_contract_ingestion_v1`, `contract_version_id=pcv1`, `lineage_id=lineage_alpha`, `status=PASS`, `status_reason=all_required_contract_lineage_quality_and_harness_checks_passed`, `violation_ids=[]`, `drift_signal_ids=[]`, non-empty `evidence_refs`, `produced_by_motor=motor_022` and a non-empty `version_hash`.
- It emits an empty `violation_log`.
- It emits no `DriftSignal`.

## sparse_case
Input bundle:
- Same `phase_contracts` and `version_records` as the happy path.
- `quality_records`: one record with `object_id=dataset_alpha`, `version_id=v3`, `quality_status=WARNING`, `fitness_score=0.72`, `failed_checks=["optional_completeness_soft_check"]`, `evidence_refs=["quality:qr_dataset_alpha_v3_warning"]`.
- `harness_results`: empty list because no applicable harness result has been produced yet for this object/version.

Expected behavior:
- The motor does not crash and does not invent a harness result.
- It emits one `ConformanceRecord` for `dataset_alpha@v3` with `status=WARNING`, `quality_record_ids=["qr_dataset_alpha_v3_warning"]`, `harness_result_ids=[]`, non-empty `evidence_refs`, and `status_reason=quality_warning_or_missing_nonblocking_harness_evidence`.
- It emits either an empty `violation_log` or one non-material `ViolationRecord` with `violation_type=missing_evidence`, `severity=LOW`, `material=false`, `rule_ref=handoff.dataset_alpha.harness_evidence_expected_when_available`, and the missing harness condition recorded in `expected_condition`.
- It emits no `DriftSignal` unless a linked prior violation set already proves repeated missing evidence for the same scope.

## malformed_input
Malformed input examples and required rejection:
- If `phase_contracts` is not a collection, reject the whole evaluation with `ERROR_INVALID_INPUT_COLLECTION` and identify `input_ref=phase_contracts`.
- If a `harness_result` has `target_id=dataset_alpha` but omits `target_version_id`, reject with `ERROR_MISSING_TARGET_VERSION` and do not emit a `ConformanceRecord`.
- If a `quality_record` uses `quality_status=GREEN` instead of `PASS`, `WARNING` or `FAIL`, reject with `ERROR_INVALID_STATUS` and identify the offending record in `input_ref`.
- If `quality_records[0].version_id=v9` but no `version_records` entry exists for `dataset_alpha@v9`, reject with `ERROR_MISSING_VERSION_RECORD`.
- If an evaluated object cannot be matched to any `phase_contract`, reject with `ERROR_MISSING_CONTRACT`.

Expected behavior:
- Rejections are structured and deterministic.
- No upstream contract, version record, quality record, harness result, dataset, artifact or motor state is modified.
- If rejection occurs before a parent conformance record can be built, no orphan `ViolationRecord` is emitted; the rejection payload preserves `error_code`, `input_ref`, `expected_condition` and `observed_value`.

## edge_cases
1. Required harness assertion fails while quality passes:
   - Input: `quality_status=PASS`; `harness_results[0].result_status=FAIL`; `failed_assertions=["handoff.dataset_alpha.required_field_present"]`.
   - Expected output: one `ConformanceRecord.status=FAIL`; one material `ViolationRecord` with `violation_type=harness`, `severity=HIGH`, `rule_ref=handoff.dataset_alpha.required_field_present`, `material=true`, and `input_ref=harness:run_11:dataset_alpha_v3`; no silent downgrade to `WARNING`.

2. Contract boundary breach with valid lineage:
   - Input: lineage and quality are valid, but the evaluated artifact includes an output field prohibited by `boundary_rules=["no_cross_phase_reporting_fields"]`.
   - Expected output: one `ConformanceRecord.status=FAIL`; one material `ViolationRecord` with `violation_type=boundary`, `rule_ref=no_cross_phase_reporting_fields`, `expected_condition=artifact_outputs_exclude_cross_phase_reporting_fields`, and the observed prohibited field recorded in `observed_value`.

3. Repeated same-rule violation across versions:
   - Input: prior evidence contains a material `ViolationRecord` for `dataset_alpha@v2` and the current evaluation detects the same `rule_ref` on `dataset_alpha@v3`.
   - Expected output: the current evaluation emits a new material `ViolationRecord`; it also emits one `DriftSignal` with `scope=dataset`, `scope_ref=dataset_alpha`, `basis=repeated_violation`, `related_violation_ids` containing both version-specific violations, and non-empty `evidence_refs`.

4. Missing lineage on otherwise passing inputs:
   - Input: contract, quality and harness records are present and passing, but `version_records[0].lineage_id=null`.
   - Expected output: `ConformanceRecord.status=FAIL`; one material `ViolationRecord` with `violation_type=lineage`, `severity=CRITICAL`, `rule_ref=version_records.lineage_id.required`, `expected_condition=lineage_id_is_non_empty`, and no `PASS` record.

## pass_criteria
The test passes only when all observable conditions below are true:
- Valid happy-path input produces exactly one `ConformanceRecord` and no mutation of any input collection.
- The happy-path `ConformanceRecord.status` is `PASS`, `violation_ids=[]`, `drift_signal_ids=[]`, `lineage_id` is non-empty, `evidence_refs` is non-empty and `produced_by_motor=motor_022`.
- Sparse but evaluable input produces `status=WARNING` rather than a fatal exception, while preserving the missing or warning evidence in `evidence_refs` or in a non-material `ViolationRecord`.
- Malformed input is rejected with the exact expected `error_code` and no orphan output entities.
- Material harness, boundary or lineage violations always create linked `ViolationRecord` entries with `rule_ref`, `severity`, `input_ref`, `expected_condition` and `observed_value`.
- A `DriftSignal` is emitted only when linked violations provide the deterministic basis for drift.

## fail_criteria
The test fails if any observable condition below occurs:
- The motor emits `PASS` when contract authority, compatible version record, lineage, required quality evidence or required harness evidence is missing.
- The motor accepts a malformed status, missing `target_version_id`, missing `lineage_id` or non-collection input without the required structured error.
- A material violation is summarized only in prose and no linked `ViolationRecord` is emitted.
- A `ViolationRecord` is emitted without `conformance_record_id`, `rule_ref`, `input_ref`, `expected_condition` or `observed_value`.
- A `DriftSignal` is emitted without non-empty `related_violation_ids` and `evidence_refs`.
- The motor modifies upstream `phase_contracts`, `version_records`, `quality_records`, `harness_results`, evaluated datasets, artifacts or motor state as part of evaluation.
