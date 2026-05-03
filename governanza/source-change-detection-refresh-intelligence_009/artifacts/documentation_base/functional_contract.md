# Functional Contract — Source Change Detection / Refresh Intelligence

Motor ID: motor_009

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar cambios de fuente, metodología, estructura, disponibilidad y prioridad de recaptura.
why_it_exists:  Sin este motor los datasets quedan stale sin que el sistema lo sepa.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), version_history (motor_002)
key_outputs:    change_detection_event, refresh_priority, staleness_signal
key_objects:    ChangeEvent, RefreshPriority, StalenessRecord
what_not_to_do: No descarga datos. No decide qué hacer con cambios. Solo detecta y señaliza.
design_notes:   Depende de motor_008, motor_004, motor_002.

All documentation-base sections are filled for gate verification.
-->

## inputs
- `source_registry`: object collection — motor_008; registros de fuente con `source_id`, `rights_profile_ref`, `access_class`, `declared_refresh_interval`, `declared_methodology_ref`, `expected_schema_signature`, `source_locator_ref` y estado de uso permitido.
- `ingestion_records`: object collection — motor_004; eventos de ingesta con `ingestion_id`, `source_id`, `captured_at`, `availability_status`, `observed_schema_signature`, `content_fingerprint`, `record_count`, `access_error_code` y `raw_record_ref` o `parsed_record_ref`.
- `version_history`: object collection — motor_002; registros de versionado con `version_id`, `object_ref`, `source_id`, `lineage_refs`, `created_at`, `previous_version_ref`, `change_summary` y dependencias afectadas.

## outputs
- `change_detection_event`: object — consumidores downstream del framework y audit trail; contiene el evento de cambio detectado, su tipo, severidad, evidencia comparada, referencias a input y lineage.
- `refresh_priority`: object — orquestacion o procesos de recaptura posteriores; contiene `source_id`, `priority_level`, `priority_reason`, `recommended_by_rule`, `evidence_refs` y timestamp de calculo.
- `staleness_signal`: object — consumidores que necesitan saber vigencia de datasets o fuentes; contiene `source_id`, `staleness_status`, `age_days`, `expected_refresh_interval`, `last_observed_at`, `triggering_condition` y referencias de version.

## limits
- Nunca acepta registros sin `source_id` estable y trazable.
- Nunca acepta inputs que no puedan vincularse a motor_008, motor_004 o motor_002 mediante referencias explicitas.
- Nunca produce datos descargados, registros raw, parsed records, objetos normalizados ni paquetes de reporte.
- Nunca produce una decision de recaptura obligatoria; `refresh_priority` es una senal estructurada, no una orden.
- Nunca altera licencias, derechos, refresh schedules declarados, version records ni ingestion records.
- Nunca infiere cambios de contenido sin evidencia observable como fingerprint, schema signature, timestamp, availability status o cambio versionado.

## validations
- Rechaza cualquier input item con `source_id` nulo, vacio o no presente en `source_registry`.
- Rechaza comparaciones cuando `ingestion_records.captured_at` o `version_history.created_at` no son timestamps parseables.
- Rechaza registros de ingesta sin al menos una evidencia de comparacion: `availability_status`, `observed_schema_signature`, `content_fingerprint`, `record_count` o `access_error_code`.
- Verifica que cada evento emitido incluya `event_id`, `source_id`, `change_type`, `detected_at`, `severity`, `evidence_refs` y `lineage_refs`.
- Verifica que cada `refresh_priority` derive de al menos un `change_detection_event` o una regla temporal de staleness documentada.
- Verifica que cada `staleness_signal` incluya `last_observed_at`, `expected_refresh_interval`, `age_days` y una condicion disparadora reproducible.
- Emite error estructurado `INVALID_SOURCE_REFERENCE` si una referencia de fuente no existe, `MISSING_COMPARISON_EVIDENCE` si no hay evidencia minima, y `UNTRACEABLE_CHANGE_EVENT` si el output no puede reconstruirse desde inputs y lineage.
