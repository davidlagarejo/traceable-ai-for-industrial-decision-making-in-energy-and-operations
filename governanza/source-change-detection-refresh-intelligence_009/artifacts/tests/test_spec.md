# Test Spec — Source Change Detection / Refresh Intelligence

Motor ID: motor_009

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar cambios de fuente, metodología, estructura, disponibilidad y prioridad de recaptura.
why_it_exists:  Sin este motor los datasets quedan stale sin que el sistema lo sepa.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), version_history (motor_002)
key_outputs:    change_detection_event, refresh_priority, staleness_signal
key_objects:    ChangeEvent, RefreshPriority, StalenessRecord
what_not_to_do: No descarga datos. No decide qué hacer con cambios. Solo detecta y señaliza.
design_notes:   Depende de motor_008, motor_004, motor_002.

All tests below refine the documentation-base acceptance tests for Gate 3 review.
-->

## happy_path
Input minimo valido:
- `source_registry` contiene un `SourceRecord` con `source_id = "src_facility_roster_001"`, `declared_refresh_interval = "P7D"`, `expected_schema_signature = "schema:v1:name,address,license_id"`, `declared_methodology_ref = "method:roster:v1"` y `source_locator_ref = "registry:src_facility_roster_001"`.
- `ingestion_records` contiene `ing_2026_04_01` para la misma fuente con `captured_at = "2026-04-01T00:00:00Z"`, `availability_status = "available"`, `observed_schema_signature = "schema:v1:name,address,license_id"`, `content_fingerprint = "sha256:old001"`, `record_count = 1200` y `raw_record_ref = "raw:ing_2026_04_01"`.
- `ingestion_records` contiene `ing_2026_04_10` para la misma fuente con `captured_at = "2026-04-10T00:00:00Z"`, `availability_status = "available"`, `observed_schema_signature = "schema:v2:name,address,license_id,status"`, `content_fingerprint = "sha256:new001"`, `record_count = 1214` y `raw_record_ref = "raw:ing_2026_04_10"`.
- `version_history` contiene `ver_100` y `ver_117` para `src_facility_roster_001`, con `previous_version_ref = "ver_100"` en `ver_117`, `lineage_refs = ["lin:src_facility_roster_001", "lin:ing_2026_04_10"]` y `change_summary = "schema signature changed"`.

Expected output:
- Se emite un `ChangeEvent` con `source_id = "src_facility_roster_001"`, `change_type = "schema"`, `severity = "warning"`, `previous_ingestion_ref = "ing_2026_04_01"`, `current_ingestion_ref = "ing_2026_04_10"`, `previous_version_ref = "ver_100"`, `current_version_ref = "ver_117"`, `detection_rule_ref = "rule.schema_signature.changed"`, `evidence_refs = ["ing_2026_04_01", "ing_2026_04_10", "ver_117"]`, `lineage_refs = ["lin:src_facility_roster_001", "lin:ing_2026_04_10"]`, `produced_by_motor = "motor_009"` y un `version_hash` no vacio calculado sobre contenido canonico.
- Se emite un `StalenessRecord` con `staleness_status = "watch"`, `last_observed_at = "2026-04-10T00:00:00Z"`, `expected_refresh_interval = "P7D"`, `age_days = 9`, `triggering_condition = "interval_exceeded_and_schema_changed"`, `basis_ingestion_refs = ["ing_2026_04_01", "ing_2026_04_10"]` y `basis_version_refs = ["ver_100", "ver_117"]`.
- Se emite un `RefreshPriority` con `priority_level = "high"`, `priority_reason = "schema_changed_and_refresh_interval_exceeded"`, `derived_from_event_ids` apuntando al `ChangeEvent.event_id`, `staleness_id` apuntando al `StalenessRecord.staleness_id`, `rule_ref = "rule.priority.schema_change.stale.high"` y `produced_by_motor = "motor_009"`.
- Ningun registro de `source_registry`, `ingestion_records` o `version_history` es modificado por el motor.

## sparse_case
Input parcialmente vacio permitido:
- `source_registry` contiene `source_id = "src_monthly_permit_feed_002"`, `declared_refresh_interval = null`, `expected_schema_signature = "schema:v1:permit_id,status,issued_at"` y `source_locator_ref = "registry:src_monthly_permit_feed_002"`.
- `ingestion_records` contiene una unica observacion `ing_2026_04_12` con `captured_at = "2026-04-12T09:00:00Z"`, `availability_status = "available"`, `observed_schema_signature = "schema:v1:permit_id,status,issued_at"`, `content_fingerprint = "sha256:solo001"`, `record_count = null` y sin `access_error_code`.
- `version_history` esta vacio para esta fuente.

Expected behavior:
- El motor acepta el caso porque el `source_id` existe y hay evidencia de comparacion suficiente en `availability_status`, `observed_schema_signature` y `content_fingerprint`.
- No emite `ChangeEvent` porque no existe una observacion previa ni un version record que demuestre cambio deterministico.
- Emite un `StalenessRecord` con `staleness_status = "unknown"`, `last_observed_at = "2026-04-12T09:00:00Z"`, `expected_refresh_interval = null`, `age_days = 5` cuando `calculated_at = "2026-04-17T09:00:00Z"`, `triggering_condition = "no_declared_refresh_interval"`, `basis_ingestion_refs = ["ing_2026_04_12"]`, `basis_version_refs = []` y lineage/provenance completos.
- Emite un `RefreshPriority` con `priority_level = "none"`, `priority_reason = "no_change_event_and_no_declared_refresh_interval"`, `derived_from_event_ids = []`, `staleness_id` apuntando al `StalenessRecord.staleness_id`, `rule_ref = "rule.priority.no_change.unknown_interval.none"` y sin generar una decision de recaptura.

## malformed_input
Casos de rechazo obligatorio:
- `INVALID_SOURCE_REFERENCE`: `ingestion_records` contiene `source_id = "src_missing_999"` y `source_registry` no contiene ese identificador. El motor rechaza el lote antes de emitir eventos, prioridades o staleness para esa fuente.
- `MISSING_COMPARISON_EVIDENCE`: una ingesta para `source_id = "src_facility_roster_001"` contiene `ingestion_id = "ing_empty_001"` y `captured_at = "2026-04-10T00:00:00Z"`, pero no incluye `availability_status`, `observed_schema_signature`, `content_fingerprint`, `record_count` ni `access_error_code`. El motor rechaza la comparacion y no crea evento parcial.
- `INVALID_TEMPORAL_ORDER`: `captured_at = "ten days ago"` o `version_history.created_at = "2026/04/10 00:00"` no es un timestamp ISO 8601 parseable y ordenable de forma deterministica. El motor rechaza el input temporal afectado.
- `UNTRACEABLE_CHANGE_EVENT`: la comparacion detecta diferencia de schema pero `version_history.lineage_refs = []` y los ingestion records carecen de referencias reconstruibles. El motor rechaza el evento propuesto porque no puede preservar `evidence_refs` y `lineage_refs` suficientes.

## edge_cases
1. Fuente recien observada sin cambio material:
   - Input: `src_daily_capacity_003` tiene `declared_refresh_interval = "P1D"` y dos ingestas del mismo dia con igual `availability_status = "available"`, igual `observed_schema_signature`, igual `content_fingerprint` e igual `record_count`.
   - Correct behavior: no emite `ChangeEvent`, emite `StalenessRecord.staleness_status = "fresh"`, mantiene `age_days = 0`, y cualquier `RefreshPriority` emitido usa `priority_level = "none"` con `derived_from_event_ids = []`.

2. Cambio de acceso critico:
   - Input: `ing_2026_04_01` tiene `availability_status = "available"` y `ing_2026_04_11` tiene `availability_status = "blocked"` con `access_error_code = "HTTP_403"` para el mismo `source_id`.
   - Correct behavior: emite `ChangeEvent.change_type = "access"`, `severity = "critical"`, conserva ambos ingestion ids en `evidence_refs`, emite `RefreshPriority.priority_level = "urgent"` por regla deterministica y no intenta descargar, autenticar ni corregir el acceso.

3. Fingerprint cambia sin cambio de schema:
   - Input: dos ingestas consecutivas tienen igual `observed_schema_signature = "schema:v1:name,address,license_id"` y distinto `content_fingerprint`.
   - Correct behavior: emite `ChangeEvent.change_type = "content_fingerprint"`, conserva `comparison_basis.previous_content_fingerprint` y `comparison_basis.current_content_fingerprint`, y no interpreta semanticamente el contenido ni normaliza registros.

4. Orden de entrada no deterministico:
   - Input: `ingestion_records` llega en orden inverso, con `ing_2026_04_10` antes que `ing_2026_04_01`, pero ambos tienen timestamps validos y el mismo `source_id`.
   - Correct behavior: el motor ordena logicamente por `source_id`, `captured_at` y version lineage para comparar el estado anterior contra el actual; los ids, hashes y outputs son identicos a los del mismo input entregado en orden cronologico.

## pass_criteria
Un test pasa cuando todas las condiciones aplicables son observables:
- Los outputs emitidos usan exclusivamente los objetos permitidos `ChangeEvent`, `RefreshPriority` y `StalenessRecord`.
- Cada output persistido contiene identificador estable (`event_id`, `priority_id` o `staleness_id`), `record_id`, `source_id`, `version_id`, `version_hash`, `source_ref`, `produced_by_motor = "motor_009"`, `produced_at` y `parent_id`.
- Cada `ChangeEvent` incluye `change_type`, `detected_at`, `severity`, `comparison_basis`, `evidence_refs`, `lineage_refs` y `detection_rule_ref`, con al menos una referencia de motor_004 o motor_002.
- Cada `RefreshPriority` deriva de `derived_from_event_ids` no vacio o de una regla temporal de staleness documentada con `rule_ref` y `evidence_refs`.
- Cada `StalenessRecord` incluye `staleness_status`, `last_observed_at`, `expected_refresh_interval`, `age_days`, `triggering_condition`, `basis_ingestion_refs` y `basis_version_refs`.
- Los errores esperados se reportan con codigo estructurado exacto y sin emitir outputs parciales para el caso rechazado.
- Los inputs upstream permanecen inmutables despues de la ejecucion.

## fail_criteria
Un test falla si se observa cualquiera de estas condiciones:
- El motor emite un evento para un `source_id` ausente en `source_registry`.
- Se genera `ChangeEvent` sin `evidence_refs`, sin `lineage_refs`, sin `detection_rule_ref` o sin referencia a motor_004 o motor_002.
- Se acepta una ingesta sin evidencia minima de comparacion.
- Se emite `RefreshPriority` como orden operativa de recaptura o con efectos laterales sobre descargas, APIs, source registry, ingestion records o version history.
- Se muta cualquier registro de motor_008, motor_004 o motor_002.
- Se infiere cambio de contenido desde narrativa, supuestos o campos no observables en lugar de `content_fingerprint`, schema signature, availability status, access error, record count o version_history.
- Se produce output con `produced_by_motor` distinto de `motor_009`, `version_hash` vacio, ids no reconstruibles, timestamps no parseables o `parent_id` apuntando a otra entidad distinta del mismo tipo.
