# Technical Schema — Governance Event & Exception Registry

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
- `GovernanceEvent`: objeto raíz inmutable que representa la captura de una señal de excepción, override o tensión proveniente de cualquier motor del sistema. Producido por motor_024 en respuesta a cada evento válido recibido.
- `ExceptionRecord`: objeto derivado que encapsula el payload estructurado de una excepción emitida por un motor. Vinculado a un único GovernanceEvent de tipo `exception`.
- `TensionSignal`: objeto derivado que captura la contradicción observable entre dos motores o políticas. Vinculado a un único GovernanceEvent de tipo `tension`.

## fields
**GovernanceEvent**
- `governance_event_id`: string — identificador canónico estable, generado con SHA-256 sobre (source_motor_id + event_type + captured_at + lineage_context_ref). Obligatorio.
- `event_type`: string — tipo del evento: `exception`, `override` o `tension`. Obligatorio.
- `source_motor_id`: string — identificador del motor que originó la señal (e.g. `motor_004`). Obligatorio.
- `captured_at`: string — timestamp ISO-8601 del momento en que el motor fuente registró la anomalía. Obligatorio.
- `phase_contract_ref`: string — referencia de contrato de fase de motor_001 vigente al momento de la captura. Obligatorio.
- `lineage_id`: string — referencia de lineage de motor_002 adjunta al evento. Obligatorio.
- `raw_event_payload`: dict — payload completo del evento entrante tal como fue recibido, sin modificaciones. Obligatorio.
- `version_id`: string — versión del objeto (formato `{governance_event_id}:v1`). Obligatorio.
- `version_hash`: string — hash SHA-256 del contenido canónico del objeto. Obligatorio.
- `created_at`: string — timestamp de creación del objeto por motor_024. Obligatorio.
- `updated_at`: string — igual a `created_at` (el objeto es inmutable). Obligatorio.
- `produced_by_motor`: string — siempre `motor_024`. Obligatorio.
- `produced_at`: string — timestamp de emisión. Obligatorio.
- `parent_id`: string — `lineage_context_ref` del evento entrante. Obligatorio.

**ExceptionRecord**
- `exception_record_id`: string — identificador canónico estable, generado con SHA-256 sobre (governance_event_id + exception_code). Obligatorio.
- `governance_event_id`: string — FK al GovernanceEvent raíz. Obligatorio.
- `source_motor_id`: string — motor que emitió la excepción. Obligatorio.
- `exception_code`: string — código estructurado de la excepción (e.g. `INGESTION_EMPTY_PAYLOAD`). Obligatorio.
- `exception_payload`: dict — payload completo de la excepción preservado sin modificaciones. Obligatorio.
- `lineage_id`: string — heredado de GovernanceEvent. Obligatorio.
- `version_id`: string. Obligatorio.
- `version_hash`: string. Obligatorio.
- `created_at`: string. Obligatorio.
- `produced_by_motor`: string — siempre `motor_024`. Obligatorio.
- `produced_at`: string. Obligatorio.

**TensionSignal**
- `tension_signal_id`: string — identificador canónico estable, generado con SHA-256 sobre (governance_event_id + motor_a_id + motor_b_id). Obligatorio.
- `governance_event_id`: string — FK al GovernanceEvent raíz. Obligatorio.
- `motor_a_id`: string — primer motor en la contradicción. Obligatorio.
- `motor_b_id`: string — segundo motor en la contradicción. Obligatorio. Debe ser distinto de motor_a_id.
- `conflict_description`: string — descripción concisa de la contradicción observada. Obligatorio. No vacío.
- `lineage_id`: string — heredado de GovernanceEvent. Obligatorio.
- `version_id`: string. Obligatorio.
- `version_hash`: string. Obligatorio.
- `created_at`: string. Obligatorio.
- `produced_by_motor`: string — siempre `motor_024`. Obligatorio.
- `produced_at`: string. Obligatorio.

## relationships
- `GovernanceEvent` → `ExceptionRecord`: relación 1:0..1. La FK es `exception_record.governance_event_id → governance_event.governance_event_id`. Solo existe cuando `event_type == "exception"`.
- `GovernanceEvent` → `TensionSignal`: relación 1:0..1. La FK es `tension_signal.governance_event_id → governance_event.governance_event_id`. Solo existe cuando `event_type == "tension"`.
- `ExceptionRecord` → `GovernanceEvent`: relación N:1 en el contexto de una sesión multi-evento.
- `TensionSignal` → `GovernanceEvent`: relación N:1 en el contexto de una sesión multi-evento.

## identifiers
- `GovernanceEvent`: clave canónica = `governance_event_id`. Generado determinísticamente con SHA-256 sobre (source_motor_id + event_type + captured_at + lineage_context_ref). Garantiza idempotencia: el mismo evento enviado dos veces produce el mismo ID.
- `ExceptionRecord`: clave canónica = `exception_record_id`. Generado con SHA-256 sobre (governance_event_id + exception_code).
- `TensionSignal`: clave canónica = `tension_signal_id`. Generado con SHA-256 sobre (governance_event_id + motor_a_id + motor_b_id).

## versioning
- Todos los objetos emitidos son inmutables una vez creados; `updated_at` siempre es igual a `created_at`.
- `version_id`: formato `{object_id}:v1`. Permite identificar inequívocamente la versión del objeto.
- `version_hash`: SHA-256 del JSON canónico del objeto (sort_keys=True, separators=(",",":"), sin el campo `version_hash` mismo). Permite detectar alteraciones post-emisión.
- No existe mecanismo de actualización ni versionado incremental; un nuevo evento produce un nuevo objeto con nuevo ID.

## lineage
- `lineage_id`: hereda directamente de `lineage_context_ref` del evento entrante — referencia de motor_002.
- `produced_by_motor`: siempre `motor_024` — identifica inequívocamente el motor productor.
- `produced_at`: timestamp ISO-8601 del momento de emisión del objeto por motor_024.
- `parent_id`: igual a `lineage_context_ref` del evento entrante — permite reconstruir la cadena de trazabilidad desde el evento raíz.
- `source_motor_id`: preservado directamente desde el evento entrante — identifica el motor fuente de la señal original.
