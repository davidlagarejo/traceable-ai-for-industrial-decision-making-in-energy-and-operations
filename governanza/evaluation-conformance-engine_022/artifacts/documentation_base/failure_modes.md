# Failure Modes — Evaluation / Conformance Engine

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

## failure_modes_list
- CONTRACT_MATCH_FAILURE: evaluated objects are marked as rejected because no applicable `phase_contract` can be resolved, even though upstream contracts are expected to exist.
- LINEAGE_BLIND_PASS: output contains `PASS` records with missing or null `lineage_id`, making the conformance decision unreconstructable.
- VIOLATION_SUPPRESSION: material harness, quality or boundary failures are summarized in prose but no `ViolationRecord` is emitted.
- DRIFT_OVEREMISSION: `architectural_drift_signal` is emitted for isolated non-material warnings without repeated pattern, material severity or explicit violation evidence.
- SOURCE_DESYNCHRONIZATION: quality records, harness results and version records refer to incompatible object versions, producing inconsistent status assignments.

## anti_patterns
- Using this motor as an auto-fixer that edits contracts, datasets or motor artifacts after detecting non-conformance.
- Treating a narrative reviewer opinion as contract authority instead of using `phase_contracts` and structured upstream records.
- Collapsing quality, harness and conformance into a single aggregate score that hides the failed rule and input evidence.
- Emitting drift signals from vague trend language without linking them to concrete violation identifiers.

## degradation_signals
- Rising count of `ConformanceRecord.status=PASS` with empty or repeated `evidence_refs`.
- Increasing share of rejected evaluations caused by `ERROR_MISSING_CONTRACT` or `ERROR_MISSING_VERSION_RECORD`.
- Violation logs with missing `rule_ref`, missing `input_ref` or severity defaulted to the same value across unrelated violations.
- Drift signals whose `related_violation_ids` list is empty or references unknown violations.
- Frequent mismatches between `quality_status`, `harness result_status` and emitted conformance status for the same object/version pair.
- Decline in unique contract references across evaluations, indicating that broad generic contracts may be masking boundary-specific failures.
