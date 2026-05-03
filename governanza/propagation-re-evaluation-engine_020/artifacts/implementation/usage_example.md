# Usage Example — Propagation / Re-evaluation Engine

Motor ID: motor_020

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Re-evaluar objetos downstream cuando cambian fuentes, reglas, taxonomías, contratos o bibliotecas.
why_it_exists:  Versioning registra cambios, pero este motor decide qué debe re-evaluarse.
key_inputs:     version_records (motor_002), quality_records (motor_007), change_events (motor_009)
key_outputs:    re_evaluation_job, stale_set, propagation_log
key_objects:    ReEvaluationJob, StaleObject, PropagationRecord
what_not_to_do: No modifica objetos directamente. Encola y señaliza para re-evaluación.
design_notes:   Corre en respuesta a cambios detectados. Crea cadenas de re-evaluación.

All implementation-stage sections below are filled with concrete content.
-->

## example
El orquestador llama a `PropagationReEvaluationEngine` cuando motor_009 detecta que la fuente `SRC-418` cambio su schema y motor_002 registra que la version `VR-002-DATASET-418-v5` impacta dos objetos downstream. El motor valida la evidencia, enlaza el cambio con el version record y el quality record disponible, marca `OBJ-REPORT-121` y `OBJ-CLAIM-077` como stale, y encola una re-evaluacion trazable para cada objeto sin modificar los inputs.

## inputs_used
```json
{
  "rule_version": "prop-rules-020.1.0",
  "change_events": [
    {
      "event_id": "CE-009-2026-04-17-001",
      "source_id": "SRC-418",
      "change_type": "schema",
      "severity": "critical",
      "detected_at": "2026-04-17T10:00:00Z",
      "evidence_refs": ["ING-884"],
      "lineage_refs": ["LN-SRC-418"]
    }
  ],
  "version_records": [
    {
      "version_id": "VR-002-DATASET-418-v5",
      "object_id": "DATASET-418",
      "object_type": "normalized_dataset",
      "mutation_type": "update",
      "prior_version_ref": "VR-002-DATASET-418-v4",
      "impact_set": ["OBJ-REPORT-121", "OBJ-CLAIM-077"],
      "lineage_refs": ["LN-SRC-418", "LN-DATASET-418"],
      "phase_contract_ref": "PCR-F2-REPORTING",
      "created_at": "2026-04-17T09:55:00Z",
      "provenance_refs": ["ING-884"]
    }
  ],
  "quality_records": [
    {
      "quality_record_id": "QR-007-OBJ-REPORT-121",
      "subject_ref": "OBJ-REPORT-121",
      "phase_contract_ref": "PCR-F2-REPORTING",
      "evaluation_status": "conditional_pass",
      "quality_flags": ["contract_mismatch"],
      "fitness_score": 0.71,
      "evaluation_run_id": "QE-007-2026-04-17-004",
      "evaluated_at": "2026-04-17T10:02:00Z",
      "lineage_refs": ["LN-DATASET-418"]
    }
  ]
}
```

## expected_output
```json
{
  "re_evaluation_job": [
    {
      "target_object_ref": "OBJ-CLAIM-077",
      "target_version_ref": null,
      "trigger_ref": "CE-009-2026-04-17-001",
      "trigger_type": "change_event",
      "reason_code": "source_change",
      "priority": "urgent",
      "dependency_path": [
        "CE-009-2026-04-17-001",
        "SRC-418",
        "LN-SRC-418",
        "VR-002-DATASET-418-v5",
        "DATASET-418",
        "LN-DATASET-418",
        "OBJ-CLAIM-077"
      ],
      "input_refs": [
        "CE-009-2026-04-17-001",
        "VR-002-DATASET-418-v5",
        "QR-007-OBJ-REPORT-121"
      ],
      "evidence_refs": [
        "ING-884",
        "LN-SRC-418",
        "LN-DATASET-418",
        "CE-009-2026-04-17-001",
        "VR-002-DATASET-418-v5",
        "QR-007-OBJ-REPORT-121"
      ],
      "status": "queued",
      "propagation_rule_version": "prop-rules-020.1.0",
      "produced_by_motor": "motor_020",
      "job_id": "stable hash-derived identifier",
      "propagation_record_id": "stable hash-derived propagation record identifier",
      "stale_object_id": "stable hash-derived stale object identifier",
      "version_hash": "deterministic hash over canonical job content"
    },
    {
      "target_object_ref": "OBJ-REPORT-121",
      "target_version_ref": null,
      "trigger_ref": "CE-009-2026-04-17-001",
      "trigger_type": "change_event",
      "reason_code": "source_change",
      "priority": "urgent",
      "status": "queued",
      "produced_by_motor": "motor_020",
      "job_id": "stable hash-derived identifier"
    }
  ],
  "stale_set": [
    {
      "object_ref": "OBJ-CLAIM-077",
      "version_ref": null,
      "stale_reason": "source_changed",
      "trigger_ref": "CE-009-2026-04-17-001",
      "trigger_type": "change_event",
      "lineage_refs": ["LN-SRC-418", "LN-DATASET-418"],
      "dependency_path": [
        "CE-009-2026-04-17-001",
        "SRC-418",
        "LN-SRC-418",
        "VR-002-DATASET-418-v5",
        "DATASET-418",
        "LN-DATASET-418",
        "OBJ-CLAIM-077"
      ],
      "severity": "critical",
      "detected_at": "2026-04-17T10:00:00Z",
      "produced_by_motor": "motor_020",
      "stale_object_id": "stable hash-derived identifier",
      "job_id": "matching re_evaluation_job.job_id"
    },
    {
      "object_ref": "OBJ-REPORT-121",
      "version_ref": null,
      "stale_reason": "source_changed",
      "trigger_ref": "CE-009-2026-04-17-001",
      "trigger_type": "change_event",
      "severity": "critical",
      "produced_by_motor": "motor_020",
      "stale_object_id": "stable hash-derived identifier",
      "job_id": "matching re_evaluation_job.job_id"
    }
  ],
  "propagation_log": [
    {
      "trigger_ref": "CE-009-2026-04-17-001",
      "trigger_type": "change_event",
      "input_refs": [
        "CE-009-2026-04-17-001",
        "VR-002-DATASET-418-v5",
        "QR-007-OBJ-REPORT-121"
      ],
      "affected_object_refs": ["OBJ-CLAIM-077", "OBJ-REPORT-121"],
      "emitted_job_ids": ["stable job id for OBJ-CLAIM-077", "stable job id for OBJ-REPORT-121"],
      "stale_object_ids": ["stable stale id for OBJ-CLAIM-077", "stable stale id for OBJ-REPORT-121"],
      "decision": "jobs_emitted",
      "secondary_decisions": [],
      "error_code": null,
      "rule_version": "prop-rules-020.1.0",
      "evaluated_at": "2026-04-17T10:02:00Z",
      "produced_by_motor": "motor_020",
      "propagation_record_id": "stable hash-derived identifier",
      "version_hash": "deterministic hash over canonical propagation record content"
    }
  ]
}
```

## notes
La salida es una senal operacional: no corrige versiones, no recalcula quality scores, no recaptura fuentes y no declara ningun objeto como vigente. Si el cambio de fuente no puede conectarse con un `impact_set`, `lineage_refs`, `subject_ref` o dependency edge declarado, el motor debe emitir un `PropagationRecord` con error estructurado y dejar `re_evaluation_job` y `stale_set` vacios para esa rama.
