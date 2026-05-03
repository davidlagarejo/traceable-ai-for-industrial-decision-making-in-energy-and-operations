# Test Spec — Governance Event & Exception Registry

Motor ID: motor_024

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar anomalías, overrides, excepciones recurrentes y tensiones de gobernanza relevantes.
why_it_exists:  La gobernanza necesita señales explícitas y no solo intuición.
key_inputs:     exception events from all motors, override records
key_outputs:    governance_event, exception_record, tension_signal
key_objects:    GovernanceEvent, ExceptionRecord, TensionSignal
what_not_to_do: No resuelve excepciones. No cambia políticas. Solo registra para revisión humana.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Solo requiere motor_001 y motor_002.

-->

## happy_path
**Test: excepción válida de motor_004 → GovernanceEvent + ExceptionRecord emitidos**
- Input: `exception_event` con `source_motor_id="motor_004"`, `exception_code="INGESTION_EMPTY_PAYLOAD"`, `captured_at="2026-04-16T10:00:00Z"`, `lineage_context_ref="lineage_abc123"`, `phase_contract_ref="phase_01_capture"`.
- Acción: invocar `register_event(event)` en el motor.
- Output esperado:
  - `result.governance_event` no es None.
  - `result.governance_event.event_type == "exception"`.
  - `result.governance_event.source_motor_id == "motor_004"`.
  - `result.governance_event.lineage_id == "lineage_abc123"`.
  - `result.governance_event.produced_by_motor == "motor_024"`.
  - `result.exception_record` no es None.
  - `result.exception_record.exception_code == "INGESTION_EMPTY_PAYLOAD"`.
  - `result.exception_record.governance_event_id == result.governance_event.governance_event_id`.
  - `result.tension_signal` es None (tipo no es tension).
  - `result.rejection` es None.

**Test: override válido → GovernanceEvent sin ExceptionRecord ni TensionSignal**
- Input: `override_record` con `source_motor_id="motor_001"`, `override_id="ovr_001"`, `policy_ref="phase_01_capture:allow_extension"`, `captured_at="2026-04-16T10:05:00Z"`, `lineage_context_ref="lineage_abc123"`, `phase_contract_ref="phase_01_capture"`.
- Output esperado: `result.governance_event.event_type == "override"`, `result.exception_record is None`, `result.tension_signal is None`.

**Test: tensión válida → GovernanceEvent + TensionSignal emitidos**
- Input: `tension_signal_input` con `motor_a_id="motor_013"`, `motor_b_id="motor_014"`, `conflict_description="motor_013 requiere datos aún no producidos por motor_014"`, `captured_at="2026-04-16T10:10:00Z"`, `lineage_context_ref="lineage_abc123"`, `phase_contract_ref="phase_01_capture"`.
- Output esperado: `result.governance_event.event_type == "tension"`, `result.tension_signal.motor_a_id == "motor_013"`, `result.tension_signal.motor_b_id == "motor_014"`, `result.exception_record is None`.

## sparse_case
**Test: evento con solo los campos mínimos obligatorios**
- Input: `exception_event` con exactamente `source_motor_id`, `exception_code`, `captured_at`, `lineage_context_ref`, `phase_contract_ref`. Sin campos opcionales adicionales (sin descripción extendida, sin contexto extra).
- Output esperado: el motor acepta el evento, emite GovernanceEvent y ExceptionRecord correctamente, `raw_event_payload` contiene exactamente los campos enviados sin modificación.

**Test: override sin `policy_ref` (campo opcional)**
- Input: `override_record` con `source_motor_id`, `override_id`, `captured_at`, `lineage_context_ref`, `phase_contract_ref`, pero sin `policy_ref`.
- Output esperado: el motor acepta el evento (si `policy_ref` es opcional en el contrato) o rechaza con `GOV_MISSING_REQUIRED_FIELD` si es obligatorio. El motor nunca falla silenciosamente ni infiere el campo faltante.

## malformed_input
**Test: `captured_at` con formato inválido**
- Input: `exception_event` con `captured_at="16-04-2026"` (formato no ISO-8601).
- Output esperado: `result.rejection` no es None, `result.rejection.error_code == "GOV_INVALID_TIMESTAMP"`. Ningún GovernanceEvent ni objeto derivado es emitido.

**Test: `source_motor_id` vacío**
- Input: `exception_event` con `source_motor_id=""`.
- Output esperado: `result.rejection.error_code == "GOV_MISSING_REQUIRED_FIELD"`. No se produce ningún objeto de salida.

**Test: tipo de evento desconocido**
- Input: evento con campo `event_type="warning"` (no es exception, override ni tension).
- Output esperado: `result.rejection.error_code == "GOV_UNKNOWN_EVENT_TYPE"`.

## edge_cases
**Test: mismo evento enviado dos veces (idempotencia)**
- Input: misma llamada con idénticos `source_motor_id`, `exception_code`, `captured_at`, `lineage_context_ref`.
- El `governance_event_id` calculado será idéntico en ambas llamadas.
- Output esperado: la segunda llamada produce `result.rejection.error_code == "GOV_DUPLICATE_EVENT"`. El primer GovernanceEvent no es sobrescrito ni duplicado.

**Test: motor_a_id == motor_b_id en TensionSignal**
- Input: `tension_signal_input` con `motor_a_id="motor_013"` y `motor_b_id="motor_013"`.
- Output esperado: `result.rejection.error_code == "GOV_INVALID_TENSION_ACTORS"`. No se puede registrar una tensión de un motor consigo mismo.

**Test: `phase_contract_ref` con token de denegación**
- Input: cualquier evento con `phase_contract_ref="phase_01_capture:deny"`.
- Output esperado: `result.rejection.error_code == "GOV_PHASE_CONTRACT_DENIED"`.

**Test: `lineage_context_ref` con valor inestable**
- Input: evento con `lineage_context_ref="unknown"`.
- Output esperado: `result.rejection.error_code == "GOV_MISSING_REQUIRED_FIELD"`.

## pass_criteria
- El resultado contiene exactamente un `GovernanceEvent` con `governance_event_id`, `lineage_id` y `produced_by_motor="motor_024"` no nulos.
- Para eventos de tipo `exception`: `exception_record` no es None y referencia el mismo `governance_event_id`.
- Para eventos de tipo `tension`: `tension_signal` no es None con `motor_a_id != motor_b_id`.
- Para eventos de tipo `override`: ni `exception_record` ni `tension_signal` son emitidos.
- El `raw_event_payload` del GovernanceEvent contiene los mismos campos del input sin modificaciones.
- El `governance_event_id` es reproducible: invocar con los mismos inputs produce el mismo ID.
- Todos los objetos emitidos tienen `version_id`, `version_hash`, `created_at` y `produced_at` presentes.

## fail_criteria
- El motor emite un GovernanceEvent sin `governance_event_id` (nulo o cadena vacía).
- El motor emite un objeto sin `lineage_id` o con `lineage_id == "unknown"`.
- El motor modifica cualquier campo del `raw_event_payload` respecto al input original.
- El motor emite un `ExceptionRecord` sin `governance_event_id` referenciando un GovernanceEvent existente.
- El motor emite un `TensionSignal` con `motor_a_id == motor_b_id`.
- El motor acepta un evento cuyo `phase_contract_ref` contiene tokens de denegación.
- El motor acepta dos veces el mismo evento (mismo `governance_event_id`) sin detectar el duplicado.
- El motor produce un output parcial cuando la validación de precondiciones falla (en lugar de emitir únicamente el rechazo).
