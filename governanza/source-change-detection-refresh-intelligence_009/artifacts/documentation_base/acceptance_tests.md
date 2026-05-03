# Acceptance Tests — Source Change Detection / Refresh Intelligence

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

## happy_path
Input: `source_registry` contiene `source_id = "src_facility_roster_001"`, `declared_refresh_interval = "P7D"`, `expected_schema_signature = "schema:v1:name,address,license_id"`, y fuente permitida para uso analitico. `ingestion_records` contiene una observacion previa del 2026-04-01 con `observed_schema_signature = "schema:v1:name,address,license_id"` y una nueva observacion del 2026-04-10 con `observed_schema_signature = "schema:v2:name,address,license_id,status"`, `availability_status = "available"` y `content_fingerprint = "sha256:9fd1"`. `version_history` contiene version anterior `ver_100` y version nueva `ver_117` con lineage refs trazables.

Action: el motor compara la firma esperada, la observacion nueva y el historial de versionado para `src_facility_roster_001`.

Expected output: emite un `change_detection_event` con `change_type = "schema"`, `severity = "warning"`, `evidence_refs = ["ing_2026_04_10", "ver_117"]` y `lineage_refs` heredados del version history. Tambien emite `refresh_priority.priority_level = "high"` porque la estructura cambio y la ultima observacion supera el intervalo esperado de siete dias, y un `staleness_signal.staleness_status = "watch"` con `age_days = 9`.

## edge_cases
- Case: fuente con refresh interval diario y ultima ingesta correcta hace cero dias. Correct behavior: no emite `change_detection_event`, emite `staleness_signal.staleness_status = "fresh"` y `refresh_priority.priority_level = "none"` si no hay cambios de schema, disponibilidad o fingerprint.
- Case: fuente registrada pero sin ingestas recientes por bloqueo de acceso con `access_error_code = "HTTP_403"`. Correct behavior: emite `change_detection_event.change_type = "access"` con severidad `critical` si el estado anterior era accesible, y genera `refresh_priority.priority_level = "urgent"` sin intentar descargar ni corregir el acceso.
- Case: dos ingestas consecutivas tienen igual schema signature pero distinto content fingerprint. Correct behavior: emite `change_detection_event.change_type = "content_fingerprint"` con severidad dependiente de regla, conserva ambos ingestion ids en `evidence_refs` y no interpreta semanticamente el contenido.

## rejection_criteria
- Rechaza con `INVALID_SOURCE_REFERENCE` cuando un `ingestion_record.source_id` no existe en `source_registry`.
- Rechaza con `MISSING_COMPARISON_EVIDENCE` cuando una ingesta no incluye availability status, schema signature, content fingerprint, record count ni access error code.
- Rechaza con `INVALID_TEMPORAL_ORDER` cuando `captured_at` o version timestamps no pueden ordenarse de forma determinista.
- Rechaza con `UNTRACEABLE_CHANGE_EVENT` cuando el evento propuesto no puede incluir `evidence_refs` y `lineage_refs` suficientes para reconstruccion.
