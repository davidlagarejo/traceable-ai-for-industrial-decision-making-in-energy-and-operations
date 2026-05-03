# Failure Modes — Pipeline Orchestration + Observability Engine

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

## failure_modes_list
EVENT_LOSS: faltan ExecutionLog esperados para eventos emitidos y aparecen huecos por run_id, motor_id o correlation_id.
RETRY_STORM: el conteo de retries crece de forma sostenida para el mismo fallo o motor sin cierre ni alerta de agotamiento.
METRIC_DRIFT: MetricRecord agregados no coinciden con los logs fuente o cambian cuando se recalculan sobre la misma ventana.
ALERT_FATIGUE: demasiadas alertas de baja severidad ocultan fallos críticos o repiten la misma condición sin deduplicación operacional.
CONTRACT_SCOPE_LEAK: el motor acepta eventos de motores, etapas o estados no autorizados por phase_contracts.
OBSERVABILITY_LAG: dashboards o métricas quedan atrasados respecto a ExecutionLog aceptados y degradan la visibilidad operativa.

## anti_patterns
- Usar este motor para corregir fallos de negocio de otros motores en vez de registrar, alertar y decidir retries operativos.
- Permitir payloads libres sin validación de contrato para acelerar la instrumentación.
- Reescribir logs históricos para ocultar fallos en lugar de emitir eventos correctivos enlazados.
- Tratar una alerta operacional como prueba de calidad de datos, verdad epistemológica o conformidad arquitectónica.
- Configurar retries sin límite, sin reason_code o sin enlace al evento fallido original.

## degradation_signals
- Aumento de eventos rechazados por `INVALID_EVENT_SHAPE` o `UNKNOWN_CONTRACT_SCOPE`.
- Diferencia persistente entre número de eventos recibidos y número de ExecutionLog emitidos.
- Crecimiento de retries por run sin reducción posterior de fallos.
- MetricRecord con ventanas temporales incompletas, superpuestas o imposibles de recalcular desde logs.
- AlertEvent repetidos con misma triggering_condition, motor_id y run_id sin deduplicación.
- Runs activos sin heartbeat durante más tiempo que el timeout configurado.
- Incremento de outputs sin linked_log_id, source_event_id o linked_failure_event_id.
