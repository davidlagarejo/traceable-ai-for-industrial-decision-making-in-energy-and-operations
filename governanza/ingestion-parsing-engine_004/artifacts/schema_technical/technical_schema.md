# Technical Schema — Ingestion + Parsing Engine

Motor ID: motor_004

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Capturar fuentes, preservar raw y extraer estructura parcial trazable.
why_it_exists:  Permite que el mundo real entre al sistema sin contaminarlo.
key_inputs:     raw source files, API responses, structured feeds
key_outputs:    raw_record (preserved), parsed_record, ingestion_lineage
key_objects:    RawRecord, ParsedRecord, IngestionEvent
what_not_to_do: No normaliza. No resuelve duplicados. No evalúa calidad. Solo ingesta y preserva.
design_notes:   Preserva siempre el raw. La extracción es parcial e inmutable. Depende de motor_001 y motor_002.

All placeholder content in this artifact has been completed.
-->

## entities
- `RawRecord`: entidad inmutable de preservación del payload capturado. Vive en la etapa `schema_technical` como objeto técnico mínimo y en `implementation` como modelo persistible de raw preservado.
- `ParsedRecord`: entidad derivada de extracción parcial y determinista desde exactamente un `RawRecord`. Vive en la etapa `schema_technical` como contrato de estructura extraída y en `implementation` como salida parser trazable.
- `IngestionEvent`: entidad de auditoría del intento de ingesta, aceptado o rechazado, que conecta fuente, contrato de fase, contexto de lineage, raw records y parsed records. Vive en la etapa `schema_technical` como ancla de reconstrucción y en `implementation` como evento emitido por cada intento.
- `IngestionRejection`: entidad de error estructurado emitida cuando una entrada no cumple precondiciones de ingesta. Vive en la etapa `schema_technical` como salida de rechazo del contrato funcional y en `implementation` como resultado fallido trazable al `IngestionEvent`.

## fields
### RawRecord
- `raw_record_id: string` — identificador estable del raw preservado. (required)
- `source_ref: string` — referencia estable de la fuente capturada. (required)
- `raw_payload_ref: string` — ruta, URI interna o handle de almacenamiento del payload original sin alteración. (required)
- `content_hash: string` — hash determinista del payload original usado para auditoría y reconstrucción. (required)
- `media_type: string` — tipo de contenido declarado o perfil de archivo usado para seleccionar preservación y parsing. (required)
- `captured_at: datetime` — timestamp de captura del payload desde la fuente. (required)
- `lineage_id: string` — referencia de lineage asignada por motor_002 para reconstrucción. (required)
- `ingestion_event_id: string` — referencia al evento que creó el raw record. (required)
- `payload_size_bytes: integer` — tamaño del payload preservado antes de cualquier parsing. (required)
- `raw_preservation_status: enum(preserved, rejected)` — estado explícito de preservación del raw. (required)
- `version_id: string` — versión técnica del registro emitida bajo motor_002. (required)
- `created_at: datetime` — timestamp de creación del registro técnico. (required)
- `updated_at: datetime` — timestamp de última actualización técnica; para raw inmutable debe coincidir con `created_at` salvo corrección de metadatos gobernada. (required)
- `version_hash: string` — hash de versión calculado sobre campos contractuales del registro. (required)
- `produced_by_motor: string` — motor productor; valor esperado `motor_004`. (required)
- `produced_at: datetime` — timestamp de emisión del objeto por motor_004. (required)
- `parent_id: string` — identificador padre de lineage; para `RawRecord` apunta a `ingestion_event_id`. (required)

### ParsedRecord
- `parsed_record_id: string` — identificador estable del resultado de parsing. (required)
- `raw_record_id: string` — referencia obligatoria al `RawRecord` preservado que sirve como base de reconstrucción. (required)
- `source_ref: string` — referencia de fuente heredada del `RawRecord`. (required)
- `parser_profile: string` — perfil determinista aplicado al contenido raw. (required)
- `parser_version: string` — versión del parser o regla de extracción usada para reproducibilidad. (required)
- `parse_status: enum(parsed, partially_parsed, unsupported_format, parse_failed)` — estado explícito del intento de parsing. (required)
- `extracted_fields: map[string, raw_value]` — campos observables extraídos sin normalización, inferencia ni conversión. (required)
- `parse_warnings: list[string]` — advertencias estructuradas de parsing parcial, campos no leídos o formato soportado parcialmente. (required)
- `created_at: datetime` — timestamp de creación del parsed record. (required)
- `ingestion_event_id: string` — evento que produjo o intentó producir el parsed record. (required)
- `version_id: string` — versión técnica del registro emitida bajo motor_002. (required)
- `updated_at: datetime` — timestamp de última actualización técnica; para parsing inmutable debe coincidir con `created_at` salvo corrección gobernada de metadatos. (required)
- `version_hash: string` — hash de versión calculado sobre `raw_record_id`, parser, estado y campos extraídos. (required)
- `lineage_id: string` — referencia de lineage compartida con el raw record y el contexto motor_002. (required)
- `produced_by_motor: string` — motor productor; valor esperado `motor_004`. (required)
- `produced_at: datetime` — timestamp de emisión del objeto por motor_004. (required)
- `parent_id: string` — identificador padre de lineage; para `ParsedRecord` apunta a `raw_record_id`. (required)

### IngestionEvent
- `ingestion_event_id: string` — identificador estable de cada intento de captura. (required)
- `source_ref: string` — referencia estable de la fuente intentada. (required)
- `phase_contract_ref: string` — contrato de fase motor_001 que autoriza o deniega la captura. (required)
- `lineage_context_ref: string` — contexto motor_002 al que se ancla el evento. (required)
- `raw_record_ids: list[string]` — lista de raw records creados por el evento; puede estar vacía si el intento fue rechazado antes de preservar raw. (required)
- `parsed_record_ids: list[string]` — lista de parsed records creados por el evento; puede estar vacía en parsing fallido, formato no soportado o rechazo temprano. (required)
- `rejection_ids: list[string]` — lista de rechazos estructurados emitidos durante el evento. (required)
- `event_status: enum(accepted, accepted_with_parse_warning, rejected)` — estado final del intento de ingesta. (required)
- `occurred_at: datetime` — timestamp operativo del intento de captura. (required)
- `version_id: string` — versión técnica del evento emitida bajo motor_002. (required)
- `created_at: datetime` — timestamp de creación del evento técnico. (required)
- `updated_at: datetime` — timestamp de última actualización técnica del evento. (required)
- `version_hash: string` — hash de versión calculado sobre fuente, contrato, lineage y resultados enlazados. (required)
- `produced_by_motor: string` — motor productor; valor esperado `motor_004`. (required)
- `produced_at: datetime` — timestamp de emisión del evento por motor_004. (required)
- `parent_id: string` — identificador padre de lineage; para `IngestionEvent` apunta a `lineage_context_ref`. (required)

### IngestionRejection
- `ingestion_rejection_id: string` — identificador estable del rechazo estructurado. (required)
- `ingestion_event_id: string` — evento de ingesta donde ocurrió el rechazo. (required)
- `source_ref: string` — fuente asociada al rechazo, cuando la precondición permite identificarla. (required)
- `error_code: enum(INGESTION_MISSING_SOURCE_REF, INGESTION_EMPTY_PAYLOAD, INGESTION_MISSING_CONTENT_TYPE, INGESTION_MISSING_LINEAGE_CONTEXT, INGESTION_PHASE_CONTRACT_DENIED)` — código de rechazo permitido por el contrato funcional. (required)
- `error_message: string` — descripción determinista y no inferencial del motivo de rechazo. (required)
- `rejected_at: datetime` — timestamp del rechazo. (required)
- `phase_contract_ref: string` — contrato de fase evaluado para el intento, cuando está disponible. (required)
- `lineage_context_ref: string` — contexto motor_002 asociado al intento, cuando está disponible. (required)
- `version_id: string` — versión técnica del rechazo emitida bajo motor_002. (required)
- `created_at: datetime` — timestamp de creación del rechazo técnico. (required)
- `updated_at: datetime` — timestamp de última actualización técnica del rechazo. (required)
- `version_hash: string` — hash de versión calculado sobre evento, código y contexto del rechazo. (required)
- `lineage_id: string` — referencia de lineage para auditoría del rechazo. (required)
- `produced_by_motor: string` — motor productor; valor esperado `motor_004`. (required)
- `produced_at: datetime` — timestamp de emisión del rechazo por motor_004. (required)
- `parent_id: string` — identificador padre de lineage; para `IngestionRejection` apunta a `ingestion_event_id`. (required)

## relationships
- `IngestionEvent.ingestion_event_id` → `RawRecord.ingestion_event_id`: relación uno a muchos; un evento aceptado puede crear uno o más raw records.
- `RawRecord.raw_record_id` → `ParsedRecord.raw_record_id`: relación uno a cero o uno por combinación de raw record y parser profile; parsing fallido o formato no soportado puede dejar cero parsed records.
- `IngestionEvent.ingestion_event_id` → `ParsedRecord.ingestion_event_id`: relación uno a muchos; el evento enumera los parsed records producidos durante el intento.
- `IngestionEvent.ingestion_event_id` → `IngestionRejection.ingestion_event_id`: relación uno a muchos; los rechazos quedan anclados al evento que evaluó la entrada.
- `IngestionEvent.lineage_context_ref` → motor_002 lineage context: referencia externa obligatoria para reconstrucción y auditoría.
- `IngestionEvent.phase_contract_ref` → motor_001 phase contract: referencia externa obligatoria para autorización de fase.
- `RawRecord.parent_id` → `IngestionEvent.ingestion_event_id`: relación de lineage padre-hijo entre evento y raw preservado.
- `ParsedRecord.parent_id` → `RawRecord.raw_record_id`: relación de lineage padre-hijo entre raw preservado y extracción parcial.
- `IngestionRejection.parent_id` → `IngestionEvent.ingestion_event_id`: relación de lineage padre-hijo entre evento y rechazo estructurado.

## identifiers
- `RawRecord`: ID canónico `raw_record_id`; debe ser estable, único dentro del dominio de motor_004 y nunca reutilizarse para otro payload.
- `ParsedRecord`: ID canónico `parsed_record_id`; debe ser estable para la combinación de `raw_record_id`, `parser_profile` y `parser_version`.
- `IngestionEvent`: ID canónico `ingestion_event_id`; debe emitirse para cada intento de captura, incluyendo rechazos.
- `IngestionRejection`: ID canónico `ingestion_rejection_id`; debe emitirse por cada rechazo estructurado.
- Referencias externas obligatorias: `phase_contract_ref` identifica autoridad motor_001 y `lineage_context_ref` o `lineage_id` identifica autoridad motor_002.
- La presencia de `content_hash` no convierte registros repetidos en duplicados resueltos; solo permite trazabilidad y comparación posterior fuera del alcance de motor_004.

## versioning
- Todo objeto emitido por motor_004 debe incluir `version_id`, `created_at`, `updated_at` y `version_hash`.
- `version_id` se asigna bajo el contexto de motor_002 y representa la versión técnica del objeto, no una corrección semántica del contenido de fuente.
- `created_at` registra cuándo se materializa el objeto técnico dentro de motor_004.
- `updated_at` registra correcciones gobernadas de metadatos técnicos; para `RawRecord` y `ParsedRecord` inmutables debe coincidir con `created_at` en emisión normal.
- `version_hash` se calcula sobre los campos contractuales mínimos del objeto y permite detectar mutación silenciosa.
- Una nueva captura del mismo payload debe crear un nuevo `IngestionEvent`; motor_004 puede conservar el mismo `content_hash`, pero no suprime el evento ni decide duplicidad.
- Cambios de `parser_profile` o `parser_version` producen un nuevo `ParsedRecord` o una nueva versión gobernada, siempre preservando vínculo al `RawRecord` original.

## lineage
- Todo objeto emitido por motor_004 debe incluir `source_ref`, `produced_by_motor`, `produced_at` y `parent_id`.
- `source_ref` conserva la referencia estable de la fuente original; si falta, el intento se rechaza con `INGESTION_MISSING_SOURCE_REF`.
- `produced_by_motor` debe ser `motor_004` para objetos creados por este motor.
- `produced_at` registra cuándo motor_004 emitió el objeto, separado de `captured_at`, `occurred_at` o `rejected_at`.
- `parent_id` define la cadena reconstruible: `IngestionEvent.parent_id = lineage_context_ref`, `RawRecord.parent_id = ingestion_event_id`, `ParsedRecord.parent_id = raw_record_id`, `IngestionRejection.parent_id = ingestion_event_id`.
- `lineage_context_ref` y `lineage_id` enlazan la salida con motor_002; motor_004 no redefine lineage global, solo adjunta sus objetos al contexto recibido.
- La extracción parcial queda subordinada al raw: ningún `ParsedRecord` es válido sin `raw_record_id`, `source_ref`, `parser_profile`, `parse_status` y lineage completo.
