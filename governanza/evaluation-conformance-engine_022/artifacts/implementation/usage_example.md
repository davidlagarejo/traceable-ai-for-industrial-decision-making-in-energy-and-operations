# Usage Example — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Implementation-stage usage content is fully resolved.
-->

## example
An orchestration review calls motor_022 after `dataset_alpha@v3` has a phase contract, a lineage record, a quality record and a harness result. The engine verifies the evidence without editing any upstream object and emits a PASS conformance record because contract authority, lineage, quality and harness evidence all agree. Governance consumers can store the conformance record and empty violation log as audit evidence for the evaluated dataset version.

## inputs_used
```json
{
  "phase_contracts": [
    {
      "contract_id": "phase_contract_ingestion_v1",
      "contract_version_id": "pcv1",
      "phase_id": "ingestion",
      "required_outputs": ["dataset_alpha"],
      "allowed_inputs": ["raw_source_alpha"],
      "handoff_rules": ["handoff.dataset_alpha.requires.versioned_output"],
      "boundary_rules": ["preserve_lineage", "respect_handoff_fields"],
      "version_id": "pcv1"
    }
  ],
  "version_records": [
    {
      "object_id": "dataset_alpha",
      "version_id": "v3",
      "lineage_id": "lineage_alpha",
      "created_at": "2026-04-18T10:00:00Z",
      "supersedes": "v2",
      "provenance_ref": "source:ingestion_run_77"
    }
  ],
  "quality_records": [
    {
      "quality_record_id": "qr_dataset_alpha_v3",
      "object_id": "dataset_alpha",
      "version_id": "v3",
      "quality_status": "PASS",
      "fitness_score": 0.96,
      "failed_checks": [],
      "evidence_refs": ["quality:qr_dataset_alpha_v3"]
    }
  ],
  "harness_results": [
    {
      "test_run_id": "harness_run_11",
      "target_id": "dataset_alpha",
      "target_version_id": "v3",
      "result_status": "PASS",
      "failed_assertions": [],
      "evidence_refs": ["harness:run_11:dataset_alpha_v3"]
    }
  ],
  "evaluated_object_id": "dataset_alpha",
  "evaluated_version_id": "v3",
  "evaluated_object_type": "dataset",
  "evaluated_at": "2026-04-18T10:05:00Z"
}
```

## expected_output
```json
{
  "conformance_record": {
    "record_id": "motor_022:dataset:dataset_alpha:v3:phase_contract_ingestion_v1:pcv1",
    "evaluated_object_id": "dataset_alpha",
    "evaluated_object_type": "dataset",
    "evaluated_version_id": "v3",
    "contract_id": "phase_contract_ingestion_v1",
    "contract_version_id": "pcv1",
    "lineage_id": "lineage_alpha",
    "quality_record_ids": ["qr_dataset_alpha_v3"],
    "harness_result_ids": ["harness_run_11"],
    "status": "PASS",
    "status_reason": "all_required_contract_lineage_quality_and_harness_checks_passed",
    "violation_ids": [],
    "drift_signal_ids": [],
    "evidence_refs": [
      "phase_contract:phase_contract_ingestion_v1:pcv1",
      "source:ingestion_run_77",
      "quality:qr_dataset_alpha_v3",
      "harness:run_11:dataset_alpha_v3"
    ],
    "evaluated_at": "2026-04-18T10:05:00Z",
    "produced_by_motor": "motor_022"
  },
  "violation_log": [],
  "architectural_drift_signal": null
}
```

## notes
The example assumes that `phase_contract_ingestion_v1` is the applicable authority for `dataset_alpha`, that `dataset_alpha@v3` is present in `version_records`, and that both quality and harness evidence explicitly reference the same version. If any material harness assertion fails, lineage is missing, version evidence is incompatible or contract authority cannot be resolved, motor_022 emits a structured rejection or linked `ViolationRecord`; it does not repair contracts, datasets, motor state, quality scores or harness results.
