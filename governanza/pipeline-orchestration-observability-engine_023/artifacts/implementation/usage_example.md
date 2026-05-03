# Usage Example — Pipeline Orchestration + Observability Engine

Motor ID: motor_023

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Orquestar ejecuciones, logs, retries, métricas, alertas y visibilidad operativa.
why_it_exists:  Si el sistema será automatizado, necesita operación continua y auditable.
key_inputs:     phase_contracts (motor_001), all motor execution events
key_outputs:    execution_log, metric_record, alert_event, retry_decision
key_objects:    ExecutionLog, MetricRecord, AlertEvent
what_not_to_do: No implementa lógica de negocio de ningún motor. Solo orquesta y observa.
design_notes:   Puede construirse temprano. Depende solo de motor_001.

All implementation-stage sections below contain completed content.
-->

## example
El orquestador recibe un evento operacional emitido por `motor_007` al terminar la etapa `tests` dentro de un run autorizado por los contratos de fase de `motor_001`. `PipelineOrchestrationObservabilityEngine` valida que el motor y la etapa estén dentro de alcance, registra el evento como log append-only, calcula una métrica operacional y emite una decisión determinista de retry. Como el evento representa éxito, el resultado esperado conserva trazabilidad completa y suprime cualquier retry.

## inputs_used
```json
{
  "phase_contracts": {
    "motors": {
      "motor_007": {
        "stages": ["tests"]
      }
    }
  },
  "retry_policy_config": {
    "max_attempts": 3,
    "retryable_error_types": ["transient_io_timeout"],
    "backoff_profile": "fixed_30_seconds"
  },
  "motor_execution_event": {
    "source_event_id": "evt-007-tests-001",
    "run_id": "run-2026-04-16-001",
    "motor_id": "motor_007",
    "stage_name": "tests",
    "event_type": "stage_completed",
    "status": "succeeded",
    "timestamp": "2026-04-16T14:10:00Z",
    "received_at": "2026-04-16T14:10:02Z",
    "correlation_id": "corr-run-001",
    "validation_status": "accepted",
    "source_ref": "instrumentation://motor_007/tests/evt-007-tests-001",
    "version_id": "motor_023.schema.v1",
    "produced_by_motor": "motor_023",
    "produced_at": "2026-04-16T14:10:02Z"
  }
}
```

## expected_output
```json
{
  "observed_event": {
    "source_event_id": "evt-007-tests-001",
    "run_id": "run-2026-04-16-001",
    "motor_id": "motor_007",
    "stage_name": "tests",
    "event_type": "stage_completed",
    "status": "succeeded",
    "timestamp": "2026-04-16T14:10:00Z",
    "received_at": "2026-04-16T14:10:02Z",
    "correlation_id": "corr-run-001",
    "attempt_number": 0,
    "validation_status": "accepted",
    "rejection_code": null,
    "source_ref": "instrumentation://motor_007/tests/evt-007-tests-001",
    "version_id": "motor_023.schema.v1",
    "produced_by_motor": "motor_023",
    "produced_at": "2026-04-16T14:10:02Z",
    "version_hash": "deterministic-sha256"
  },
  "execution_log": {
    "log_id": "log-evt-007-tests-001",
    "source_event_id": "evt-007-tests-001",
    "run_id": "run-2026-04-16-001",
    "motor_id": "motor_007",
    "stage_name": "tests",
    "event_type": "stage_completed",
    "status": "succeeded",
    "timestamp": "2026-04-16T14:10:00Z",
    "correlation_id": "corr-run-001",
    "attempt_number": 0,
    "previous_log_id": null,
    "payload_ref": null,
    "immutability_state": "append_only",
    "source_ref": "evt-007-tests-001",
    "produced_by_motor": "motor_023",
    "parent_id": null
  },
  "metric_records": [
    {
      "metric_name": "stage_completion_count",
      "metric_value": 1,
      "unit": "count",
      "aggregation_method": "count",
      "motor_id": "motor_007",
      "stage_name": "tests",
      "run_id": "run-2026-04-16-001",
      "source_log_ids": ["log-evt-007-tests-001"],
      "source_event_ids": ["evt-007-tests-001"],
      "calculation_status": "complete",
      "produced_by_motor": "motor_023"
    }
  ],
  "alert_events": [],
  "retry_decision": {
    "decision": "suppress_retry",
    "reason_code": "no_failure",
    "attempt_number": 0,
    "max_attempts": 3,
    "retry_after_seconds": 0,
    "linked_failure_event_id": null,
    "linked_log_id": "log-evt-007-tests-001",
    "run_id": "run-2026-04-16-001",
    "motor_id": "motor_007",
    "stage_name": "tests",
    "policy_ref": "phase_contracts:motor_001:motor_007:tests",
    "produced_by_motor": "motor_023"
  }
}
```

## notes
El ejemplo presupone que `phase_contracts` ya fue emitido por `motor_001` y que autoriza explícitamente la combinación `motor_007` + `tests`. El motor no cierra gates, no cambia dependencias, no edita `motor_state.json` y no interpreta payloads de negocio; solo registra observabilidad operacional, métricas, alertas y decisiones de retry enlazadas a eventos aceptados.
