# Failure Modes Spec — Pipeline Orchestration + Observability Engine

Motor ID: motor_023

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Orquestar ejecuciones, logs, retries, métricas, alertas y visibilidad operativa.
why_it_exists:  Si el sistema será automatizado, necesita operación continua y auditable.
key_inputs:     phase_contracts (motor_001), all motor execution events
key_outputs:    execution_log, metric_record, alert_event, retry_decision
key_objects:    ExecutionLog, MetricRecord, AlertEvent
what_not_to_do: No implementa lógica de negocio de ningún motor. Solo orquesta y observa.
design_notes:   Puede construirse temprano. Depende solo de motor_001.

All sections below contain completed content for the failure_modes gate.
-->

## failure_modes_list
EVENT_LOSS: un evento autorizado no produce `ExecutionLog` append-only dentro de la ventana esperada -> huecos por `run_id`, `motor_id`, `stage_name` o `correlation_id`, métricas incompletas y ausencia de `source_event_id` en el audit trail -> detener derivaciones para esa cadena causal, emitir `AlertEvent` de severidad `error`, reconciliar contra el canal de instrumentación y reprocesar solo eventos fuente validados bajo `phase_contracts`.

INVALID_CONTRACT_SCOPE_ACCEPTED: llega un evento con `motor_id` o `stage_name` no permitido por `phase_contracts` y el motor lo acepta -> aparecen logs, métricas, alertas o decisiones para motores o etapas fuera de contrato -> marcar el input como `validation_status=rejected`, usar `rejection_code=UNKNOWN_CONTRACT_SCOPE`, suprimir outputs derivados y actualizar la métrica de rechazos por alcance.

CAUSAL_ORDER_BREAK: un evento llega con timestamp anterior al inicio del run, duplica un `source_event_id` con contenido conflictivo o rompe la cadena `previous_log_id` por `correlation_id` -> reconstrucciones de run no son deterministas y los conteos de etapas, fallos o retries divergen entre recálculos -> rechazar el evento con `INVALID_CAUSAL_ORDER` o `INVALID_EVENT_SHAPE`, preservar el log previo append-only y emitir alerta de `causal_order_error`.

RETRY_STORM: un fallo retryable se procesa sin respetar `max_attempts`, sin deduplicar eventos repetidos o sin enlazar `RetryDecision` al fallo original -> crecimiento sostenido de intentos, logs y alertas para el mismo `run_id` sin cierre operacional -> emitir `RetryDecision` determinista `abort` al alcanzar el límite, enlazar `parent_id` a decisiones previas y generar `AlertEvent` de `retry_exhausted`.

METRIC_DERIVATION_DRIFT: `MetricRecord` se calcula desde eventos no aceptados, payloads libres o ventanas temporales inconsistentes -> `metric_value`, `calculation_status` o `version_hash` cambian al recalcular la misma ventana con las mismas fuentes -> invalidar la métrica derivada, recalcular únicamente desde `source_log_ids` y `source_event_ids` aceptados, y registrar nueva versión trazable mediante `parent_id`.

ALERT_DUPLICATION_FATIGUE: condiciones repetidas se emiten como alertas independientes sin `dedupe_key` estable -> el operador recibe múltiples alertas equivalentes y puede perder fallos críticos reales -> agrupar por `dedupe_key`, actualizar solo estado de acknowledgement o deduplicación permitido, y conservar `parent_id` hacia la alerta previa.

LINEAGE_ENVELOPE_MISSING: un objeto aceptado o emitido carece de `source_ref`, `produced_by_motor`, `produced_at`, `version_id` o hash determinista -> no se puede reconstruir qué input produjo el log, métrica, alerta o decisión -> rechazar inputs sin lineage mínimo, bloquear emisión de objetos derivados y emitir señal operacional sobre pérdida de trazabilidad.

UNSUPPORTED_OPERATION_EXECUTED: el payload observado solicita cambiar `motor_state.json`, contratos, gates, artefactos o lógica de negocio de otro motor y motor_023 lo ejecuta o lo representa como decisión válida -> el orquestador se convierte en canal de mutación silenciosa fuera de su contrato -> rechazar con `UNSUPPORTED_OPERATION_REQUEST`, no emitir outputs de negocio y generar alerta de `contract_scope_error`.

## anti_patterns
- Convertir motor_023 en un ejecutor de lógica de negocio de motores observados. El motor puede decidir `retry`, `suppress_retry` o `abort`, pero no arregla datos, tests, schemas ni artefactos de otro motor.
- Aceptar eventos sin validación contra `phase_contracts` de motor_001. Esto rompe el límite de autoridad y permite observar etapas inexistentes o motores no autorizados.
- Reescribir `ExecutionLog`, `RetryDecision` o fuentes históricas para "limpiar" fallos. Las correcciones deben ser append-only y enlazadas por `parent_id`, `previous_log_id` o referencias equivalentes.
- Calcular métricas desde payloads libres o datos de negocio no validados. Las métricas operativas deben derivar de eventos aceptados y logs con `source_log_ids` o `source_event_ids` explícitos.
- Emitir alertas sin `dedupe_key`, `linked_log_id`, severidad o condición exacta. Esto degrada la visibilidad y convierte observabilidad en ruido.
- Configurar retries sin `max_attempts`, sin `reason_code`, sin `policy_ref` o sin enlace al evento fallido. Ese patrón produce tormentas de retry y decisiones imposibles de auditar.
- Usar este motor para aprobar gates, declarar conformidad, cambiar dependencias o mutar `motor_state.json`. Esas responsabilidades pertenecen al orquestador, a motores de evaluación o a procesos de gobernanza.
- Tratar rechazo de input como éxito silencioso. Todo rechazo debe tener `validation_status=rejected`, `rejection_code` determinista y ausencia explícita de outputs derivados no autorizados.
- Guardar solo dashboards agregados sin conservar logs fuente. La visibilidad operacional debe ser reconstruible desde objetos trazables, no desde resúmenes irreproducibles.

## degradation_signals
- Diferencia persistente entre eventos recibidos y `ExecutionLog` emitidos para la misma ventana, excluyendo rechazos explícitos.
- Incremento de `rejection_code=INVALID_EVENT_SHAPE`, `UNKNOWN_CONTRACT_SCOPE`, `INVALID_CAUSAL_ORDER` o `UNSUPPORTED_OPERATION_REQUEST` por motor, etapa o canal de instrumentación.
- `RetryDecision.decision=retry` emitido cuando `attempt_number >= max_attempts` o sin `linked_failure_event_id`.
- Aumento de retries por `run_id` sin reducción de fallos ni emisión posterior de `retry_exhausted` o `abort`.
- `MetricRecord.calculation_status=partial_window` sostenido para ventanas que ya deberían estar cerradas.
- Recalcular una ventana con los mismos `source_log_ids` y `source_event_ids` produce `metric_value` o `version_hash` distinto.
- Alertas repetidas con mismo `triggering_condition`, `motor_id`, `stage_name`, `run_id` y ventana temporal pero con `dedupe_key` diferente.
- Eventos aceptados sin `source_ref`, `version_id`, `version_hash`, `produced_by_motor=motor_023` o `produced_at`.
- Runs activos sin heartbeat más allá del timeout configurado y sin `AlertEvent` de `heartbeat_missing` o `timeout`.
- Outputs derivados que referencian payloads de negocio como autoridad en vez de `ExecutionLog`, `ObservedExecutionEvent`, `MetricRecord` o `policy_ref`.
- Crecimiento de logs aceptados para motores o etapas que no aparecen en los `phase_contracts` vigentes.

## expensive_errors
1. Aceptar eventos fuera de contrato.
   - Por qué es caro: contamina logs, métricas, alertas y retries con ejecuciones que nunca debieron existir dentro del alcance autorizado. La limpieza posterior exige distinguir outputs legítimos de derivados inválidos en múltiples entidades.
   - Prevención: validar `motor_id`, `stage_name` y scope operacional contra `phase_contracts` antes de emitir cualquier `ExecutionLog`, `MetricRecord`, `AlertEvent` o `RetryDecision`.

2. Reescribir logs históricos.
   - Por qué es caro: destruye la reconstrucción de runs, invalida hashes, rompe métricas previamente calculadas y oculta la causa original del incidente.
   - Prevención: aplicar append-only para `ExecutionLog` y `RetryDecision`; representar correcciones con nuevos objetos enlazados por `parent_id`, `previous_log_id` o referencia de fuente.

3. Calcular métricas sin fuente explícita.
   - Por qué es caro: un dashboard puede parecer correcto aunque no sea reproducible, y cualquier auditoría posterior queda obligada a inferir fuentes manualmente.
   - Prevención: exigir `source_log_ids`, `source_event_ids`, `window_start`, `window_end`, `aggregation_method`, `calculation_status` y `version_hash` en cada `MetricRecord`.

4. Programar retries sin límite ni lineage.
   - Por qué es caro: una tormenta de retry puede saturar el orquestador, multiplicar logs y alertas, y ocultar el fallo real detrás de ruido operacional.
   - Prevención: aplicar `max_attempts`, `retryable_error_types`, `policy_ref`, `linked_failure_event_id`, `linked_log_id` y `reason_code` antes de emitir una decisión `retry`.

5. Emitir alertas sin deduplicación.
   - Por qué es caro: genera fatiga operacional, reduce la probabilidad de atender condiciones críticas y complica el análisis de incidentes por duplicados.
   - Prevención: construir `dedupe_key` determinista por condición, motor, etapa, run y ventana; enlazar alertas repetidas mediante `parent_id` y actualizar solo estados permitidos.

6. Aceptar objetos sin envelope de lineage y versionado.
   - Por qué es caro: después no se puede probar qué evento produjo cada output, qué versión del schema lo validó ni si un cambio fue recalculado o inventado.
   - Prevención: bloquear inputs y outputs sin `source_ref`, `produced_by_motor=motor_023`, `produced_at`, `version_id`, `created_at`, `updated_at` y `version_hash`.

7. Interpretar payloads observados como instrucciones ejecutables.
   - Por qué es caro: convierte una capa de observabilidad en una vía de mutación de estado, contratos o artefactos, con efectos difíciles de aislar.
   - Prevención: tratar `payload_ref` solo como referencia trazable; rechazar solicitudes de modificación con `UNSUPPORTED_OPERATION_REQUEST` y no ejecutar acciones fuera de retry operativo.
