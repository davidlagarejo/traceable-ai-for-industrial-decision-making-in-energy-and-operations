# Test Spec — Pipeline Orchestration + Observability Engine

Motor ID: motor_023

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Orquestar ejecuciones, logs, retries, métricas, alertas y visibilidad operativa.
why_it_exists:  Si el sistema será automatizado, necesita operación continua y auditable.
key_inputs:     phase_contracts (motor_001), all motor execution events
key_outputs:    execution_log, metric_record, alert_event, retry_decision
key_objects:    ExecutionLog, MetricRecord, AlertEvent
what_not_to_do: No implementa lógica de negocio de ningún motor. Solo orquesta y observa.
design_notes:   Puede construirse temprano. Depende solo de motor_001.

All sections below contain completed content for the tests gate.
-->

## happy_path
Input:
- `phase_contracts` declara que `motor_007` puede ejecutar la etapa `tests` dentro del run `run-2026-04-16-001`.
- `retry_policy_config` declara `max_attempts=3`, `retryable_error_types=["transient_io_timeout"]` y `backoff_profile=fixed_30_seconds`.
- Llega un `ObservedExecutionEvent` con `source_event_id=evt-007-tests-001`, `run_id=run-2026-04-16-001`, `motor_id=motor_007`, `stage_name=tests`, `event_type=stage_completed`, `status=succeeded`, `timestamp=2026-04-16T14:10:00Z`, `correlation_id=corr-run-001`, `received_at=2026-04-16T14:10:02Z`, `validation_status=accepted`, `version_id=motor_023.schema.v1`, `source_ref=instrumentation://motor_007/tests/evt-007-tests-001`, `produced_by_motor=motor_023` y `produced_at=2026-04-16T14:10:02Z`.

Expected output:
- El evento validado conserva `validation_status=accepted`, `rejection_code=null`, `source_event_id=evt-007-tests-001`, `run_id=run-2026-04-16-001`, `motor_id=motor_007`, `stage_name=tests`, `correlation_id=corr-run-001` y `produced_by_motor=motor_023`.
- Se emite exactamente un `ExecutionLog` con `log_id=log-evt-007-tests-001`, `source_event_id=evt-007-tests-001`, `event_type=stage_completed`, `status=succeeded`, `attempt_number=0`, `immutability_state=append_only`, `source_ref=evt-007-tests-001`, `produced_by_motor=motor_023` y `parent_id=null`.
- Se emite un `MetricRecord` con `metric_name=stage_completion_count`, `metric_value=1`, `unit=count`, `aggregation_method=count`, `motor_id=motor_007`, `stage_name=tests`, `run_id=run-2026-04-16-001`, `source_log_ids=["log-evt-007-tests-001"]`, `calculation_status=complete` y `produced_by_motor=motor_023`.
- No se emite `AlertEvent`.
- Se emite un `RetryDecision` con `decision=suppress_retry`, `reason_code=no_failure`, `attempt_number=0`, `max_attempts=3`, `retry_after_seconds=0`, `linked_failure_event_id=null`, `linked_log_id=log-evt-007-tests-001`, `run_id=run-2026-04-16-001`, `motor_id=motor_007`, `stage_name=tests`, `policy_ref=phase_contracts:motor_001:motor_007:tests` y `produced_by_motor=motor_023`.

## sparse_case
Input:
- `phase_contracts` autoriza `motor_007` para `tests`.
- Llega un evento válido de heartbeat con `source_event_id=evt-007-heartbeat-001`, `run_id=run-2026-04-16-001`, `motor_id=motor_007`, `stage_name=tests`, `event_type=heartbeat`, `status=running`, `timestamp=2026-04-16T14:05:00Z`, `correlation_id=corr-run-001`, `received_at=2026-04-16T14:05:01Z`, `validation_status=accepted`, `version_id=motor_023.schema.v1`, `source_ref=instrumentation://motor_007/tests/evt-007-heartbeat-001`, `produced_by_motor=motor_023` y `produced_at=2026-04-16T14:05:01Z`.
- Los campos opcionales `attempt_number`, `error_type`, `payload_ref` y `parent_id` no están presentes en el input.

Expected behavior:
- El motor no falla por la ausencia de campos opcionales.
- El evento se acepta con `rejection_code=null`.
- El `ExecutionLog` resultante fija `attempt_number=0`, `payload_ref=null`, `previous_log_id=null` si no existe un log anterior para `corr-run-001`, `parent_id=null`, `immutability_state=append_only` y `source_ref=evt-007-heartbeat-001`.
- Se puede emitir un `MetricRecord` de `heartbeat_age_seconds` o `stage_completion_count` solo si existe una ventana de cálculo válida; si no existe ventana suficiente, no debe inventar métricas ni producir alertas.
- La decisión de retry debe ser `decision=suppress_retry`, `reason_code=no_failure` y `retry_after_seconds=0`.

## malformed_input
Case A, missing required field:
- Input: evento con `source_event_id=evt-bad-001`, `run_id=run-2026-04-16-001`, `motor_id=motor_007`, `event_type=stage_completed`, `status=succeeded`, `timestamp=2026-04-16T14:10:00Z` y `correlation_id=corr-run-001`, pero sin `stage_name`.
- Expected rejection: `validation_status=rejected`, `rejection_code=INVALID_EVENT_SHAPE`, no `ExecutionLog`, no `MetricRecord`, no `AlertEvent` y no `RetryDecision`.

Case B, invalid enum value:
- Input: evento con todos los campos obligatorios, pero `event_type=finished_successfully` o `status=complete`.
- Expected rejection: `validation_status=rejected`, `rejection_code=INVALID_EVENT_SHAPE`, y ningún output derivado.

Case C, unknown contract scope:
- Input: evento completo con `motor_id=motor_999` o `stage_name=undocumented_stage`, no autorizado por `phase_contracts`.
- Expected rejection: `validation_status=rejected`, `rejection_code=UNKNOWN_CONTRACT_SCOPE`, no logs ni decisiones de retry.

Case D, unsupported operation request:
- Input: evento completo cuyo `payload_ref` apunta a una solicitud operacional que pide modificar `motor_state.json`, cambiar `phase_contracts` o ejecutar lógica de negocio del motor observado.
- Expected rejection: `validation_status=rejected`, `rejection_code=UNSUPPORTED_OPERATION_REQUEST`, y ningún objeto emitido debe ejecutar o representar esa modificación.

## edge_cases
1. Duplicate event with identical payload:
- Input: dos eventos con el mismo `source_event_id=evt-007-tests-001`, mismo `run_id`, mismo `correlation_id`, mismo `timestamp` y mismo contenido canónico.
- Correct behavior: conservar un único `ExecutionLog` canónico para `evt-007-tests-001`; no duplicar `stage_completion_count`; emitir o actualizar una métrica operacional `deduplicated_event_count` con `metric_value=1`, `source_event_ids=["evt-007-tests-001"]` y `calculation_status=complete`.

2. Conflicting duplicate event:
- Input: primer evento `source_event_id=evt-007-tests-002` con `status=succeeded`; segundo evento con el mismo `source_event_id` pero `status=failed` o `timestamp` distinto.
- Correct behavior: rechazar el segundo evento con `validation_status=rejected` y `rejection_code=INVALID_CAUSAL_ORDER` o `INVALID_EVENT_SHAPE` según la validación canónica; mantener append-only el `ExecutionLog` ya aceptado; no mutar el log previo ni recalcular métricas como si el conflicto fuera un evento válido.

3. Retryable failure below max attempts:
- Input: evento autorizado con `source_event_id=evt-007-fail-001`, `event_type=failed`, `status=failed`, `attempt_number=1`, `error_type=transient_io_timeout`, `max_attempts=3` y política `fixed_30_seconds`.
- Correct behavior: emitir `ExecutionLog`, `AlertEvent` con `alert_type=failure`, `severity=warning`, `linked_log_id=log-evt-007-fail-001`, `dedupe_key` determinista y `acknowledgement_status=unacknowledged`; emitir `RetryDecision` con `decision=retry`, `reason_code=retryable_failure`, `attempt_number=1`, `max_attempts=3`, `retry_after_seconds=30`, `linked_failure_event_id=evt-007-fail-001` y `policy_ref=phase_contracts:motor_001:motor_007:tests`.

4. Retry exhausted:
- Input: evento autorizado con `event_type=failed`, `status=failed`, `attempt_number=3`, `error_type=transient_io_timeout` y `max_attempts=3`.
- Correct behavior: emitir `AlertEvent` con `alert_type=retry_exhausted`, `severity=error` o `critical` según política; emitir `RetryDecision` con `decision=abort`, `reason_code=max_attempts_reached`, `retry_after_seconds=0`; no programar un retry adicional.

5. Missing heartbeat or timeout:
- Input: `clock_tick=2026-04-16T14:30:00Z` para un run autorizado cuyo último `ExecutionLog` es `log-evt-007-heartbeat-001` con `timestamp=2026-04-16T14:05:00Z`, excediendo el timeout configurado.
- Correct behavior: emitir `AlertEvent` con `alert_type=heartbeat_missing` o `timeout`, `severity=warning` o `error`, `linked_log_id=log-evt-007-heartbeat-001`, `source_ref=log-evt-007-heartbeat-001`; no inventar un evento `failed` ni cerrar la etapa del motor observado.

6. Missing provenance or lineage envelope:
- Input: evento completo en campos operativos, pero sin `source_ref`, sin `version_id` o con `produced_by_motor` distinto de `motor_023` en el wrapper validado.
- Correct behavior: rechazar con `validation_status=rejected`, `rejection_code=INVALID_EVENT_SHAPE`, y no emitir objetos sin lineage mínimo.

## pass_criteria
The test suite passes only if all observable conditions below are true:
- Every accepted event has `validation_status=accepted`, `rejection_code=null`, a stable `version_hash`, `source_ref`, `produced_by_motor=motor_023` and `produced_at`.
- Every accepted event produces at most one canonical `ExecutionLog` with `immutability_state=append_only`, `source_event_id`, `run_id`, `motor_id`, `stage_name`, `event_type`, `status`, `timestamp`, `correlation_id`, `version_id`, `source_ref` and `produced_by_motor=motor_023`.
- Metrics are calculated only from accepted `ExecutionLog` or accepted event identifiers listed in `source_log_ids` or `source_event_ids`; duplicate accepted inputs do not inflate counts.
- Alerts include `alert_id`, `alert_type`, `severity`, `triggering_condition`, `run_id`, `motor_id`, `linked_log_id`, `dedupe_key`, `acknowledgement_status`, `source_ref` and `produced_by_motor=motor_023`.
- Retry decisions use only the allowed enum values `retry`, `suppress_retry` or `abort`; each decision includes `reason_code`, `attempt_number`, `max_attempts`, `retry_after_seconds`, `policy_ref`, `source_ref` and the event or log that was evaluated.
- Rejected inputs expose the correct deterministic `rejection_code` and produce no downstream `ExecutionLog`, `MetricRecord`, `AlertEvent` or `RetryDecision` unless the schema explicitly allows a rejection wrapper.
- No output modifies `phase_contracts`, another motor's artifacts, another motor's business payload or any `motor_state.json`.

## fail_criteria
The test suite fails if any of these conditions is observed:
- A malformed event, unknown motor, unknown stage, invalid enum, invalid timestamp, unsupported operation request or missing lineage field is accepted.
- An accepted event lacks `source_event_id`, `run_id`, `motor_id`, `stage_name`, `timestamp`, `correlation_id`, `source_ref`, `version_id` or `produced_by_motor=motor_023`.
- An `ExecutionLog` is rewritten in place instead of represented as append-only with a new linked object.
- A metric is calculated from unvalidated events, free-text payload interpretation or missing `source_log_ids` and `source_event_ids`.
- Duplicate events inflate completion, failure, retry or alert counts.
- A retry is scheduled for a non-retryable error, for `attempt_number >= max_attempts`, or without a linked failure event or accepted log.
- An alert omits `linked_log_id`, `dedupe_key`, severity or source lineage.
- The motor emits business outputs, gate approvals, conformance judgments, dependency changes, contract edits or state mutations outside its orchestration and observability scope.
