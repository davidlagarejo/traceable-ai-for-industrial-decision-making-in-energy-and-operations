# Acceptance Tests — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Sections below are completed with motor-specific content.
-->

## happy_path
Input: `phase_contracts` contains `contract_id=phase_contract_01` for `phase_id=ingestion`, requiring lineage preservation and approved handoff fields; `version_records` contains `object_id=dataset_alpha`, `version_id=v3`, `lineage_id=lineage_alpha`; `quality_records` contains `object_id=dataset_alpha`, `version_id=v3`, `quality_status=PASS`; `harness_results` contains `target_id=dataset_alpha`, `target_version_id=v3`, `result_status=PASS`.

Action: the motor matches `dataset_alpha@v3` to `phase_contract_01`, verifies that version lineage exists, quality status is acceptable and required harness assertions passed.

Expected output: one `ConformanceRecord` with `evaluated_object_id=dataset_alpha`, `evaluated_version_id=v3`, `contract_id=phase_contract_01`, `lineage_id=lineage_alpha`, `status=PASS` and non-empty `evidence_refs`; an empty `violation_log`; no `architectural_drift_signal`.

## edge_cases
- Sparse but evaluable evidence: if `quality_records` is present with `quality_status=WARNING` and harness results pass, the motor emits `ConformanceRecord.status=WARNING`, records no material contract violation unless a declared contract rule is broken, and preserves the quality warning in `evidence_refs`.
- Multiple harness results for the same target version: if one required harness assertion fails and another optional assertion passes, the motor emits `status=FAIL`, writes one `ViolationRecord` for the failed required assertion and does not collapse the result into an average score.
- Repeated boundary breach across versions: if `dataset_alpha@v2` and `dataset_alpha@v3` both violate the same handoff boundary, the motor emits related `ViolationRecord` entries and an `architectural_drift_signal` scoped to the affected artifact or handoff.
- No violations: if all required inputs are present and all checks pass, the motor emits exactly one conformance record for the evaluated unit and does not fabricate warnings.

## rejection_criteria
- Reject with `ERROR_MISSING_CONTRACT` when an evaluated object, phase or handoff cannot be matched to any `phase_contract`.
- Reject with `ERROR_MISSING_VERSION_RECORD` when a quality record or harness result references an object/version pair absent from `version_records`.
- Reject with `ERROR_UNTRACEABLE_INPUT` when any input used for evaluation lacks required provenance or evidence references.
- Reject with `ERROR_INVALID_STATUS` when `quality_status`, `result_status` or intended conformance status uses a value outside the declared enum.
