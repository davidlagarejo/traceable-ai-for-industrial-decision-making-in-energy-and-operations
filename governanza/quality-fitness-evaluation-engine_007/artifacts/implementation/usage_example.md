# Usage Example — Quality / Fitness Evaluation Engine

Motor ID: motor_007

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Evaluar calidad estructural, completitud, trazabilidad y aptitud de uso por fase u objeto.
why_it_exists:  Evita que objetos defectuosos o no aptos contaminen fases posteriores.
key_inputs:     identity_resolved_records, phase_contracts (motor_001)
key_outputs:    quality_record, fitness_score, quality_flags, disqualification_reason
key_objects:    QualityRecord, FitnessScore, QualityFlag
what_not_to_do: No modifica registros. No normaliza. Solo evalúa y emite señales de calidad.
design_notes:   Motor evaluador, no transformador. Depende de motor_006.

Implementation example completed for gate 5.
-->

## example
Un orquestador de curacion recibe un registro con identidad resuelta desde `motor_006` para una instalacion y debe decidir si puede pasar a la fase `phase_1`. `motor_007` evalua el registro contra el contrato vigente de `motor_001`, calcula completitud, trazabilidad, consistencia contractual y aptitud, y emite un `quality_record` sin modificar el registro original.

## inputs_used
```json
{
  "identity_resolved_records": [
    {
      "record_id": "idr_123",
      "identity_status": "resolved",
      "object_type": "facility",
      "phase_ref": "phase_1",
      "version": "1.0.0",
      "name": "Clinic Norte",
      "country": "CL",
      "source_url": "https://example.test/facility/123",
      "provenance": {
        "source_id": "src_01"
      },
      "lineage": {
        "parent_record_id": "norm_123"
      }
    }
  ],
  "phase_contracts": [
    {
      "contract_id": "phase_1_facility_prior_v2",
      "contract_version": "2.0.0",
      "object_type": "facility",
      "phase_ref": "phase_1",
      "required_fields": ["name", "country", "source_url"],
      "fitness_thresholds": {
        "total": 0.9,
        "dimensions": {
          "completeness": 0.9,
          "traceability": 0.8
        }
      }
    }
  ],
  "evaluation_context": {
    "evaluation_run_id": "eval_run_007_001",
    "scoring_rule_version": "quality_rules_v1",
    "timestamp": "2026-04-17T00:00:00Z"
  }
}
```

## expected_output
```json
{
  "quality_record": [
    {
      "quality_record_id": "motor_007:eval_run_007_001:idr_123:phase_1_facility_prior_v2:2.0.0",
      "subject_ref": "idr_123",
      "subject_version_ref": "1.0.0",
      "phase_contract_ref": "phase_1_facility_prior_v2",
      "phase_contract_version": "2.0.0",
      "evaluation_run_id": "eval_run_007_001",
      "evaluation_status": "pass",
      "fitness_score": {
        "total_score": 1.0,
        "dimension_scores": {
          "completeness": 1.0,
          "traceability": 1.0,
          "contract_consistency": 1.0,
          "fitness": 1.0
        },
        "threshold_applied": 0.9,
        "scoring_rule_version": "quality_rules_v1",
        "blocking_flag_present": false
      },
      "quality_flags": [],
      "disqualification_reason": null,
      "produced_by_motor": "motor_007"
    }
  ]
}
```

## notes
El registro ya debe venir de `motor_006` con identidad evaluada; este motor no resuelve ambiguedades ni normaliza campos. Si falta provenance, lineage o algun campo requerido, la salida correcta es una bandera estructurada y, segun umbrales contractuales, `conditional_pass` o `disqualified`, nunca una correccion silenciosa del input.
