# Functional Contract — Governance Event & Exception Registry

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

## inputs
- `exception_event`: structured dict — señal de excepción emitida por cualquier motor cuando una regla, contrato o invariante no puede satisfacerse; debe incluir `source_motor_id`, `exception_code`, `captured_at` y `lineage_context_ref`.
- `override_record`: structured dict — registro de override emitido por proceso autorizado; debe incluir `override_id`, `source_motor_id`, `policy_ref`, `captured_at` y `lineage_context_ref`.
- `tension_signal_input`: structured dict — señal de tensión entre dos políticas o motores contradictorios; debe incluir `motor_a_id`, `motor_b_id`, `conflict_description`, `captured_at` y `lineage_context_ref`.
- `phase_contract_ref`: string — referencia de contrato de fase de motor_001 que autoriza la captura del evento en la fase actual.
- `lineage_context_ref`: string — referencia de lineage de motor_002 que permite adjuntar el evento a provenance reconstruible.

## outputs
- `governance_event`: GovernanceEvent object — evento de gobernanza inmutable con metadatos de trazabilidad completos; consumido por revisión humana y motores de evaluación de conformidad downstream.
- `exception_record`: ExceptionRecord object — registro estructurado de excepción vinculado a exactamente un `governance_event`; disponible para motor_022 (Evaluation / Conformance Engine) y revisión humana.
- `tension_signal`: TensionSignal object — señal de tensión entre motores o políticas, vinculada a un `governance_event`; disponible para motor_025 (Epistemic Governance Layer) y revisión humana.

## limits
- El motor nunca acepta un evento sin `source_motor_id` estable, `captured_at` válido y `lineage_context_ref` presente.
- El motor nunca acepta un evento si el `phase_contract_ref` no autoriza la captura en la fase actual.
- El motor nunca acepta un payload vacío o sin clasificación de tipo de evento (exception, override, tension).
- El motor nunca produce resoluciones, correcciones ni acciones compensatorias sobre los eventos registrados.
- El motor nunca modifica contratos, políticas, reglas operativas ni configuraciones de ningún motor.
- El motor nunca sobrescribe un `GovernanceEvent` ya emitido; cada nuevo evento produce un registro inmutable separado.
- El motor nunca infiere ni completa campos faltantes del evento entrante; rechaza el input si los campos mínimos no están presentes.

## validations
- Antes de procesar: verificar que `source_motor_id` no sea vacío, desconocido ni nulo.
- Antes de procesar: verificar que `captured_at` sea un timestamp ISO-8601 válido y no futuro.
- Antes de procesar: verificar que `lineage_context_ref` sea una referencia estable de motor_002.
- Antes de procesar: verificar que `phase_contract_ref` autorice la captura según motor_001.
- Antes de emitir `GovernanceEvent`: confirmar que `governance_event_id`, `event_type`, `source_motor_id`, `lineage_id`, `produced_by_motor` y `produced_at` estén presentes.
- Antes de emitir `ExceptionRecord`: confirmar que `governance_event_id` referencia un evento ya aceptado en esta sesión.
- Antes de emitir `TensionSignal`: confirmar que `motor_a_id` y `motor_b_id` son distintos y que `conflict_description` no está vacío.
