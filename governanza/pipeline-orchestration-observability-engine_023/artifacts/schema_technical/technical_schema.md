# Technical Schema — Pipeline Orchestration + Observability Engine

Motor ID: motor_023

Purpose: orquestar ejecuciones, logs, retries, métricas, alertas y visibilidad operativa sin implementar lógica de negocio de los motores observados.

Boundary: el motor solo acepta eventos autorizados por `phase_contracts` de motor_001 y produce objetos operativos trazables. No modifica contratos, dependencias, gates, artefactos ni `motor_state.json` de otros motores.

## entities
ObservedExecutionEvent
- Description: input técnico validado que representa un evento operacional recibido desde un motor del framework antes de generar logs, métricas, alertas o decisiones de retry.
- Lives in stage: `schema_technical` como entidad de entrada; en ejecución runtime como input validado de motor_023.

ExecutionLog
- Description: registro operacional append-only de un evento aceptado, asociado a run, motor, etapa, estado, timestamp, correlation_id y fuente original.
- Lives in stage: `schema_technical` como entidad persistida; en ejecución runtime como output `execution_log`.

MetricRecord
- Description: medición operacional derivada de eventos o logs aceptados, expresada con nombre, valor, unidad, ventana temporal y alcance por motor, etapa o run.
- Lives in stage: `schema_technical` como entidad persistida; en ejecución runtime como output `metric_record`.

AlertEvent
- Description: señal operacional explícita emitida cuando una ejecución falla, excede timeout, agota retries, rompe orden causal o cruza un umbral operacional.
- Lives in stage: `schema_technical` como entidad persistida; en ejecución runtime como output `alert_event`.

RetryDecision
- Description: decisión determinista que indica `retry`, `suppress_retry` o `abort` para una ejecución concreta, siempre enlazada a un evento de fallo o a una condición sin fallo.
- Lives in stage: `schema_technical` como entidad persistida; en ejecución runtime como output `retry_decision`.

## fields
ObservedExecutionEvent
- source_event_id: string (required) — identificador estable del evento emitido por el motor observado.
- run_id: string (required) — ejecución operacional a la que pertenece el evento.
- motor_id: string (required) — motor emisor autorizado por `phase_contracts`.
- stage_name: string (required) — etapa declarada por el motor emisor y permitida por el contrato de fase.
- event_type: enum (required) — tipo cerrado: `queued`, `started`, `stage_completed`, `failed`, `retried`, `skipped`, `aborted`, `heartbeat`, `timeout`.
- status: enum (required) — estado cerrado: `pending`, `running`, `succeeded`, `failed`, `skipped`, `aborted`, `timed_out`.
- timestamp: datetime (required) — instante del evento original en formato ISO 8601.
- correlation_id: string (required) — identificador de correlación para reconstruir orden causal dentro de un run.
- attempt_number: integer (optional) — intento asociado al evento cuando aplica retry; mínimo 0.
- error_type: string (optional) — clase operacional de error reportada por el motor observado.
- payload_ref: string (optional) — referencia externa o hash del payload operativo validado, sin almacenar lógica de negocio del motor observado.
- received_at: datetime (required) — instante en que motor_023 recibió el evento.
- validation_status: enum (required) — resultado de validación: `accepted` o `rejected`.
- rejection_code: enum|null (optional) — código de rechazo: `INVALID_EVENT_SHAPE`, `UNKNOWN_CONTRACT_SCOPE`, `INVALID_CAUSAL_ORDER`, `UNSUPPORTED_OPERATION_REQUEST` o null.
- version_id: string (required) — versión del schema usada para validar el evento.
- created_at: datetime (required) — instante de creación del registro de entrada validado.
- updated_at: datetime (required) — igual a `created_at` salvo corrección append-only mediante nuevo evento enlazado.
- version_hash: string (required) — hash determinista de campos canónicos y versión.
- source_ref: string (required) — referencia al evento fuente o canal de instrumentación que originó el input.
- produced_by_motor: string (required) — valor fijo `motor_023` para el wrapper de validación.
- produced_at: datetime (required) — instante de producción del objeto validado por motor_023.
- parent_id: string|null (optional) — evento previo de la misma `correlation_id` cuando existe.

ExecutionLog
- log_id: string (required) — identificador estable del log operacional.
- source_event_id: string (required) — referencia al `ObservedExecutionEvent.source_event_id` aceptado.
- run_id: string (required) — ejecución operacional observada.
- motor_id: string (required) — motor observado.
- stage_name: string (required) — etapa observada.
- event_type: enum (required) — tipo cerrado heredado del evento aceptado.
- status: enum (required) — estado operacional aceptado.
- timestamp: datetime (required) — instante original del evento.
- correlation_id: string (required) — correlación causal del evento.
- attempt_number: integer (required) — intento registrado; 0 para eventos sin retry.
- previous_log_id: string|null (optional) — log anterior de la misma correlation_id, si existe.
- payload_ref: string|null (optional) — referencia trazable al payload operativo validado.
- immutability_state: enum (required) — valor `append_only`.
- version_id: string (required) — versión del schema del log.
- created_at: datetime (required) — instante de persistencia del log.
- updated_at: datetime (required) — igual a `created_at`; correcciones se registran como nuevo log enlazado.
- version_hash: string (required) — hash determinista del log canónico.
- source_ref: string (required) — referencia a `ObservedExecutionEvent.source_event_id`.
- produced_by_motor: string (required) — valor fijo `motor_023`.
- produced_at: datetime (required) — instante de emisión del log.
- parent_id: string|null (optional) — `previous_log_id` o null cuando el log inicia una cadena.

MetricRecord
- metric_id: string (required) — identificador estable de la métrica.
- metric_name: enum (required) — nombre cerrado: `stage_duration_seconds`, `stage_completion_count`, `failure_count`, `retry_count`, `heartbeat_age_seconds`, `deduplicated_event_count`, `alert_count`.
- metric_value: number (required) — valor numérico calculado desde logs o eventos aceptados.
- unit: string (required) — unidad: `seconds`, `count`, `ratio` u otra unidad operacional declarada.
- aggregation_method: enum (required) — método: `count`, `sum`, `min`, `max`, `avg`, `latest`, `ratio`.
- window_start: datetime (required) — inicio inclusivo de la ventana temporal.
- window_end: datetime (required) — fin exclusivo de la ventana temporal.
- motor_id: string (required) — motor observado o `all` para métrica global autorizada.
- stage_name: string|null (optional) — etapa observada cuando la métrica tiene alcance por etapa.
- run_id: string|null (optional) — run observado cuando la métrica tiene alcance por ejecución.
- source_log_ids: list[string] (required) — logs usados para calcular la métrica.
- source_event_ids: list[string] (required) — eventos usados cuando la métrica deriva directamente de inputs aceptados.
- calculation_status: enum (required) — `complete`, `partial_window` o `rejected`.
- version_id: string (required) — versión del schema de métrica.
- created_at: datetime (required) — instante de creación del registro métrico.
- updated_at: datetime (required) — instante de última recalculación determinista sobre la misma ventana.
- version_hash: string (required) — hash determinista de campos canónicos, ventana y fuentes.
- source_ref: string (required) — referencia compuesta a `source_log_ids` o `source_event_ids`.
- produced_by_motor: string (required) — valor fijo `motor_023`.
- produced_at: datetime (required) — instante de emisión de la métrica.
- parent_id: string|null (optional) — `metric_id` anterior si reemplaza una medición por recalculación trazable; null si es original.

AlertEvent
- alert_id: string (required) — identificador estable de la alerta.
- alert_type: enum (required) — tipo cerrado: `failure`, `timeout`, `retry_exhausted`, `causal_order_error`, `contract_scope_error`, `metric_threshold_crossed`, `heartbeat_missing`.
- severity: enum (required) — severidad: `info`, `warning`, `error`, `critical`.
- triggering_condition: string (required) — condición operacional exacta que activó la alerta.
- run_id: string (required) — run afectado.
- motor_id: string (required) — motor observado.
- stage_name: string|null (optional) — etapa afectada cuando aplica.
- linked_log_id: string (required) — `ExecutionLog.log_id` que originó la alerta o último log conocido en timeout.
- linked_metric_id: string|null (optional) — `MetricRecord.metric_id` cuando la alerta deriva de un umbral métrico.
- timestamp: datetime (required) — instante de emisión de la alerta.
- dedupe_key: string (required) — clave determinista para deduplicación por condición, motor, etapa, run y ventana.
- acknowledgement_status: enum (required) — `unacknowledged`, `acknowledged`, `suppressed_by_dedupe`.
- version_id: string (required) — versión del schema de alerta.
- created_at: datetime (required) — instante de persistencia de la alerta.
- updated_at: datetime (required) — instante de cambio de acknowledgement o deduplicación.
- version_hash: string (required) — hash determinista de la alerta canónica.
- source_ref: string (required) — referencia a `linked_log_id` o `linked_metric_id`.
- produced_by_motor: string (required) — valor fijo `motor_023`.
- produced_at: datetime (required) — instante de producción de la alerta.
- parent_id: string|null (optional) — alerta previa con la misma `dedupe_key` cuando existe.

RetryDecision
- decision_id: string (required) — identificador estable de la decisión.
- decision: enum (required) — `retry`, `suppress_retry` o `abort`.
- reason_code: enum (required) — `retryable_failure`, `max_attempts_reached`, `non_retryable_error`, `no_failure`, `invalid_event`, `missing_contract_scope`.
- attempt_number: integer (required) — intento evaluado.
- max_attempts: integer (required) — límite determinista aplicado.
- retry_after_seconds: integer (required) — demora calculada; 0 si no hay retry.
- linked_failure_event_id: string|null (optional) — `ObservedExecutionEvent.source_event_id` que representa el fallo, null en `suppress_retry` por ausencia de fallo.
- linked_log_id: string|null (optional) — `ExecutionLog.log_id` asociado al fallo o evento evaluado.
- run_id: string (required) — ejecución operacional evaluada.
- motor_id: string (required) — motor observado.
- stage_name: string (required) — etapa observada.
- policy_ref: string (required) — referencia a la política determinista de retry derivada de `phase_contracts`.
- timestamp: datetime (required) — instante de emisión de la decisión.
- version_id: string (required) — versión del schema de decisión.
- created_at: datetime (required) — instante de creación de la decisión.
- updated_at: datetime (required) — igual a `created_at`; cambios posteriores requieren nueva decisión enlazada.
- version_hash: string (required) — hash determinista de la decisión canónica.
- source_ref: string (required) — referencia a `linked_failure_event_id`, `linked_log_id` o evento evaluado.
- produced_by_motor: string (required) — valor fijo `motor_023`.
- produced_at: datetime (required) — instante de producción de la decisión.
- parent_id: string|null (optional) — decisión previa para el mismo fallo cuando se actualiza por agotamiento de intentos.

## relationships
- ObservedExecutionEvent.source_event_id → ExecutionLog.source_event_id: relación 1:1 para eventos aceptados; eventos rechazados no producen ExecutionLog.
- ObservedExecutionEvent.source_event_id → RetryDecision.linked_failure_event_id: relación 1:0..1 cuando el evento representa fallo o evaluación de no retry.
- ExecutionLog.log_id → MetricRecord.source_log_ids: relación N:N; una métrica puede agregarse desde muchos logs y un log puede alimentar varias métricas.
- ExecutionLog.log_id → AlertEvent.linked_log_id: relación 1:0..N; un log puede disparar cero o más alertas.
- MetricRecord.metric_id → AlertEvent.linked_metric_id: relación 1:0..N; una métrica puede disparar alertas por umbral.
- ExecutionLog.log_id → RetryDecision.linked_log_id: relación 1:0..1 para fallos elegibles o decisiones de abort.
- ExecutionLog.previous_log_id → ExecutionLog.log_id: relación self-reference para reconstruir orden causal por `correlation_id`.
- AlertEvent.parent_id → AlertEvent.alert_id: relación self-reference para deduplicar alertas repetidas con la misma `dedupe_key`.
- MetricRecord.parent_id → MetricRecord.metric_id: relación self-reference para recalculaciones trazables sobre la misma ventana.
- RetryDecision.parent_id → RetryDecision.decision_id: relación self-reference para decisiones posteriores sobre el mismo fallo.
- Todos los `motor_id` y `stage_name` referencian `phase_contracts` de motor_001 como autoridad externa de alcance; motor_023 valida esa referencia pero no la modifica.

## identifiers
- ObservedExecutionEvent: `source_event_id` es el identificador canónico del evento observado; debe ser único por emisor, run y correlation_id.
- ExecutionLog: `log_id` es el identificador canónico; convención recomendada `log-{source_event_id}` cuando el evento fuente ya es estable.
- MetricRecord: `metric_id` es el identificador canónico; debe derivarse de `metric_name`, alcance, ventana y hash de fuentes.
- AlertEvent: `alert_id` es el identificador canónico; `dedupe_key` es identificador secundario para agrupación operacional.
- RetryDecision: `decision_id` es el identificador canónico; debe vincularse a `linked_failure_event_id` o al evento evaluado.
- Cross-object run scope: `run_id` identifica la ejecución operacional y no sustituye al identificador canónico de cada entidad.
- Cross-object causal scope: `correlation_id` reconstruye cadenas causales y no sustituye a `log_id`, `metric_id`, `alert_id` ni `decision_id`.

## versioning
All persisted entities produced or validated by motor_023 carry the same versioning envelope:
- version_id: string (required) — version semántica del schema técnico de la entidad, por ejemplo `motor_023.schema.v1`.
- created_at: datetime (required) — instante en que la entidad fue creada por motor_023.
- updated_at: datetime (required) — instante de última actualización permitida del registro; para objetos append-only debe igualar `created_at` salvo campos de acknowledgement o recalculación explícita.
- version_hash: string (required) — hash determinista calculado sobre campos canónicos, `version_id` y referencias de fuente.

Versioning rules:
- ExecutionLog is append-only; no se reescribe. Una corrección se representa como nuevo ExecutionLog con `parent_id` o `previous_log_id`.
- RetryDecision is append-only; una decisión posterior sobre el mismo fallo enlaza la decisión anterior mediante `parent_id`.
- MetricRecord may be recalculated only for the same `metric_id`, `source_log_ids`, `window_start` and `window_end`; `updated_at` and `version_hash` must change if the deterministic calculation changes.
- AlertEvent may update only acknowledgement and deduplication state; the triggering condition, linked sources and severity are immutable after creation.
- ObservedExecutionEvent keeps the validation result that motor_023 assigned when the event was received; a corrected event must arrive as a distinct `source_event_id` or as a new object with `parent_id`.

## lineage
All entities include this lineage envelope:
- source_ref: string (required) — stable reference to the immediate source: input event, source log, source metric, policy reference or composed source set.
- produced_by_motor: string (required) — fixed value `motor_023` for objects emitted or wrapped by this motor.
- produced_at: datetime (required) — instant at which motor_023 produced the object.
- parent_id: string|null (optional) — stable identifier of the parent object when the entity extends, corrects, deduplicates or recalculates a prior object.

Lineage rules:
- ObservedExecutionEvent.source_ref points to the external event or instrumented channel that delivered the runtime event.
- ExecutionLog.source_ref points to `ObservedExecutionEvent.source_event_id`.
- MetricRecord.source_ref points to the ordered set of `ExecutionLog.log_id` and `ObservedExecutionEvent.source_event_id` values used in calculation.
- AlertEvent.source_ref points to `linked_log_id` for event-driven alerts or `linked_metric_id` for threshold-driven alerts.
- RetryDecision.source_ref points to the failure event, accepted log or no-failure event being evaluated.
- No lineage field may point to unvalidated business payload as authority. It must point to operational sources accepted under `phase_contracts` from motor_001.
