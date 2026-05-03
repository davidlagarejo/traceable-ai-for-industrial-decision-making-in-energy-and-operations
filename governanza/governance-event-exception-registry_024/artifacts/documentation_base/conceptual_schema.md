# Conceptual Schema — Governance Event & Exception Registry

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

## entities
- `GovernanceEvent`: evento de gobernanza inmutable que representa la captura de una anomalía, override o tensión. Es el objeto raíz del que derivan todos los demás outputs de este motor.
- `ExceptionRecord`: registro estructurado de una excepción emitida por un motor del sistema. Siempre está vinculado a exactamente un `GovernanceEvent`.
- `TensionSignal`: señal de tensión entre dos motores o políticas con instrucciones contradictorias. Siempre está vinculada a exactamente un `GovernanceEvent`.

## relationships
- `GovernanceEvent` → `ExceptionRecord` (1:0..1): un GovernanceEvent de tipo `exception` produce exactamente un ExceptionRecord; otros tipos no producen ExceptionRecord.
- `GovernanceEvent` → `TensionSignal` (1:0..1): un GovernanceEvent de tipo `tension` produce exactamente un TensionSignal; otros tipos no producen TensionSignal.
- `ExceptionRecord` → `GovernanceEvent` (N:1): múltiples ExceptionRecord pueden existir en una sesión, cada uno referenciando su GovernanceEvent raíz.
- `TensionSignal` → `GovernanceEvent` (N:1): múltiples TensionSignal pueden existir en una sesión, cada uno referenciando su GovernanceEvent raíz.

## key_fields
**GovernanceEvent**
- `governance_event_id`: string — identificador estable único del evento, generado determinísticamente.
- `event_type`: string — tipo del evento: `exception`, `override` o `tension`.
- `source_motor_id`: string — identificador del motor que originó la señal.
- `captured_at`: string — timestamp ISO-8601 del momento de captura del evento.
- `lineage_id`: string — referencia de lineage de motor_002 para trazabilidad completa.
- `produced_by_motor`: string — siempre `motor_024`.
- `produced_at`: string — timestamp de emisión del objeto por este motor.
- `version_id`: string — versión del objeto para control de inmutabilidad.

**ExceptionRecord**
- `exception_record_id`: string — identificador estable único del registro de excepción.
- `governance_event_id`: string — referencia al GovernanceEvent raíz.
- `exception_code`: string — código estructurado de la excepción emitida por el motor fuente.
- `source_motor_id`: string — motor que emitió la excepción.
- `exception_payload`: dict — payload completo de la excepción tal como fue recibido, sin modificaciones.
- `lineage_id`: string — hereda de GovernanceEvent.

**TensionSignal**
- `tension_signal_id`: string — identificador estable único de la señal de tensión.
- `governance_event_id`: string — referencia al GovernanceEvent raíz.
- `motor_a_id`: string — primer motor involucrado en la contradicción.
- `motor_b_id`: string — segundo motor involucrado en la contradicción.
- `conflict_description`: string — descripción precisa de la contradicción detectada.
- `lineage_id`: string — hereda de GovernanceEvent.
