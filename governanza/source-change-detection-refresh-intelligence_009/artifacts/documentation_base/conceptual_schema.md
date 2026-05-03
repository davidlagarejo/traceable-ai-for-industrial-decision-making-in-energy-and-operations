# Conceptual Schema — Source Change Detection / Refresh Intelligence

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

## entities
- `ChangeEvent`: objeto creado por el motor para representar una diferencia detectada entre fuente registrada, observacion de ingesta y version history.
- `RefreshPriority`: objeto derivado que resume la prioridad de recaptura recomendada para una fuente o dataset por razones trazables.
- `StalenessRecord`: objeto creado para representar vigencia, antiguedad y condicion de stale state de una fuente o dataset asociado.

## relationships
- `source_registry.SourceRecord` -> `ChangeEvent` (cada evento referencia exactamente una fuente registrada por `source_id`).
- `ingestion_records.IngestionEvent` -> `ChangeEvent` (un evento de cambio usa una o mas observaciones de ingesta como evidencia).
- `version_history.VersionRecord` -> `ChangeEvent` (un evento de cambio conserva las versiones comparadas y sus lineage refs).
- `ChangeEvent` -> `RefreshPriority` (uno o mas eventos pueden justificar una prioridad de recaptura para el mismo `source_id`).
- `ChangeEvent` -> `StalenessRecord` (un cambio de disponibilidad, frecuencia o antiguedad puede generar o actualizar una senal de stale state).
- `StalenessRecord` -> `RefreshPriority` (un registro stale puede elevar la prioridad cuando supera umbrales documentados).

## key_fields
`ChangeEvent`
- `event_id`: string
- `source_id`: string
- `change_type`: enum string (`availability`, `methodology`, `schema`, `frequency`, `access`, `content_fingerprint`)
- `detected_at`: datetime string
- `severity`: enum string (`info`, `warning`, `critical`)
- `evidence_refs`: list[string]
- `lineage_refs`: list[string]

`RefreshPriority`
- `priority_id`: string
- `source_id`: string
- `priority_level`: enum string (`none`, `low`, `medium`, `high`, `urgent`)
- `priority_reason`: string
- `derived_from_event_ids`: list[string]
- `calculated_at`: datetime string
- `rule_ref`: string

`StalenessRecord`
- `staleness_id`: string
- `source_id`: string
- `staleness_status`: enum string (`fresh`, `watch`, `stale`, `unknown`)
- `last_observed_at`: datetime string
- `expected_refresh_interval`: duration string
- `age_days`: integer
- `triggering_condition`: string
