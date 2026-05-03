# Conceptual Schema — Pipeline Orchestration + Observability Engine

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

## entities
ExecutionLog: registro inmutable de un evento operacional asociado a un run, motor, etapa y correlation_id.
MetricRecord: medición operacional derivada de logs y eventos, expresada con nombre, valor, unidad y ventana temporal.
AlertEvent: señal explícita de degradación, fallo, timeout o condición operativa que requiere atención o bloqueo controlado.
RetryDecision: decisión determinista que indica si una ejecución fallida debe reintentarse, omitirse o abortarse.
ObservedExecutionEvent: input validado que representa el evento recibido desde un motor antes de convertirse en log, métrica, alerta o retry.

## relationships
ObservedExecutionEvent → ExecutionLog (cada evento aceptado produce exactamente un registro operacional inmutable).
ExecutionLog → MetricRecord (uno o más logs pueden agregarse en métricas por motor, etapa, run o ventana temporal).
ExecutionLog → AlertEvent (un log de fallo, timeout, ausencia de heartbeat o retry agotado puede producir una alerta).
ExecutionLog → RetryDecision (un log de fallo elegible puede producir una decisión de retry vinculada al mismo run_id).
RetryDecision → ExecutionLog (cuando el retry se ejecuta, el nuevo intento debe quedar enlazado al log de fallo original).
AlertEvent → MetricRecord (las alertas pueden derivarse de métricas cuando un umbral operacional se cruza).

## key_fields
ExecutionLog:
- log_id: string
- run_id: string
- motor_id: string
- stage_name: string
- event_type: enum
- status: enum
- timestamp: datetime
- correlation_id: string
- source_event_id: string

MetricRecord:
- metric_id: string
- metric_name: string
- metric_value: number
- unit: string
- window_start: datetime
- window_end: datetime
- motor_id: string
- run_id: string|null

AlertEvent:
- alert_id: string
- alert_type: enum
- severity: enum
- triggering_condition: string
- motor_id: string
- run_id: string
- linked_log_id: string
- timestamp: datetime

RetryDecision:
- decision_id: string
- decision: enum
- reason_code: enum
- attempt_number: integer
- max_attempts: integer
- retry_after_seconds: integer
- linked_failure_event_id: string
- run_id: string

ObservedExecutionEvent:
- source_event_id: string
- motor_id: string
- stage_name: string
- event_type: enum
- status: enum
- timestamp: datetime
- run_id: string
- correlation_id: string
