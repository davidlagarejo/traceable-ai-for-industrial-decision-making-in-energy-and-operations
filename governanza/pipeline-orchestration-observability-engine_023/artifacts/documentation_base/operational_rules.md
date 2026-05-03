# Operational Rules — Pipeline Orchestration + Observability Engine

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

## rules
1. Todo evento procesado debe estar autorizado por phase_contracts de motor_001 antes de crear logs, métricas, alertas o decisiones de retry.
2. Cada evento aceptado produce un ExecutionLog inmutable con source_event_id, run_id, motor_id, stage_name, timestamp y correlation_id.
3. Un RetryDecision solo puede emitirse después de un evento de fallo validado y solo si attempt_number es menor que max_attempts.
4. Un AlertEvent debe emitirse cuando una ejecución excede timeout configurado, agota retries, reporta fallo no retryable o presenta secuencia causal inválida.
5. MetricRecord debe derivarse de eventos y logs ya aceptados; no puede inventar mediciones sin fuente operacional trazable.
6. Todos los outputs deben conservar enlace al evento o log que los originó mediante source_event_id, linked_log_id o linked_failure_event_id.
7. Los estados operativos deben pertenecer a enums cerrados y no pueden inferirse desde texto libre del payload.

## invariants
- run_id, motor_id, stage_name y correlation_id permanecen presentes en todo objeto emitido o enlazado por el motor.
- Ningún output pierde la referencia a su fuente operacional inmediata.
- El motor nunca cambia el contenido de los phase_contracts recibidos desde motor_001.
- Un ExecutionLog aceptado se considera append-only y no se reescribe; cualquier corrección se expresa como nuevo evento enlazado.
- El contador de intentos de retry nunca disminuye dentro de un mismo run_id y linked_failure_event_id.
- Las métricas y alertas se derivan solo de información validada, no de suposiciones ni de reglas de negocio internas de otros motores.

## forbidden_operations
- Implementar lógica de negocio de cualquier motor observado.
- Editar artefactos, schemas, tests, failure modes, código o documentación de otros motores.
- Modificar manualmente motor_state.json o declarar cierres de etapa fuera del orquestador autorizado.
- Crear, eliminar o alterar dependencias entre motores.
- Cambiar phase_contracts o tratarlos como borradores corregibles.
- Convertir alertas operativas en veredictos epistemológicos, scores de calidad de datos o decisiones de reporting.
- Ejecutar retries infinitos, retries sin causa registrada o retries sobre errores marcados como no retryable.
