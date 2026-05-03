# Acceptance Tests — Pipeline Orchestration + Observability Engine

Motor ID: motor_023

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Orquestar ejecuciones, logs, retries, métricas, alertas y visibilidad operativa.
why_it_exists:  Si el sistema será automatizado, necesita operación continua y auditable.
key_inputs:     phase_contracts (motor_001), all motor execution events
key_outputs:    execution_log, metric_record, alert_event, retry_decision
key_objects:    ExecutionLog, MetricRecord, AlertEvent
what_not_to_do: No implementa lógica de negocio de ningún motor. Solo orquesta y observa.
design_notes:   Puede construirse temprano. Depende solo de motor_001.

All sections below contain completed content for the documentation_base gate.
-->

## happy_path
Input: phase_contracts de motor_001 declaran `motor_007` con etapa `tests`; llega un motor_execution_event con `source_event_id=evt-007-001`, `run_id=run-2026-04-16-001`, `motor_id=motor_007`, `stage_name=tests`, `event_type=stage_completed`, `status=succeeded`, `timestamp=2026-04-16T14:10:00Z` y `correlation_id=corr-001`.
Action: el motor valida que el motor y la etapa están autorizados, registra el evento y actualiza métricas de duración y éxito para esa etapa.
Expected output: un ExecutionLog con `log_id=log-evt-007-001` enlazado al evento original, un MetricRecord de `stage_completion_count=1`, ninguna alerta y un RetryDecision con `decision=suppress_retry` y `reason_code=no_failure`.

## edge_cases
- Evento duplicado: si llega dos veces `source_event_id=evt-007-001` con el mismo contenido, el motor conserva un único ExecutionLog canónico y emite MetricRecord de deduplicación operacional sin duplicar conteos de éxito.
- Fallo retryable al límite: si `attempt_number=2`, `max_attempts=3` y el error es `transient_io_timeout`, el motor emite AlertEvent de warning y RetryDecision con `decision=retry` y `retry_after_seconds` calculado por política determinista.
- Fallo no retryable: si el evento tiene `status=failed` y `error_type=contract_violation`, el motor emite AlertEvent de error y RetryDecision con `decision=abort`.
- Ausencia de heartbeat: si un run autorizado no emite eventos dentro del timeout operativo, el motor emite AlertEvent de timeout con linked_log_id del último log conocido y no inventa un estado final del motor observado.

## rejection_criteria
- Rechaza con `INVALID_EVENT_SHAPE` cualquier evento sin run_id, motor_id, stage_name, timestamp, status, event_type, correlation_id o source_event_id.
- Rechaza con `UNKNOWN_CONTRACT_SCOPE` cualquier evento cuyo motor_id o stage_name no exista en los phase_contracts vigentes.
- Rechaza con `INVALID_CAUSAL_ORDER` cualquier evento cuyo timestamp sea anterior al inicio registrado del run o contradiga la secuencia ya aceptada para la misma correlation_id.
- Rechaza con `UNSUPPORTED_OPERATION_REQUEST` cualquier payload que pida corregir artefactos, modificar motor_state.json, cambiar contratos o ejecutar lógica de negocio del motor observado.
