# Usage Example — Source Change Detection / Refresh Intelligence

Motor ID: motor_009

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar cambios de fuente, metodología, estructura, disponibilidad y prioridad de recaptura.
why_it_exists:  Sin este motor los datasets quedan stale sin que el sistema lo sepa.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), version_history (motor_002)
key_outputs:    change_detection_event, refresh_priority, staleness_signal
key_objects:    ChangeEvent, RefreshPriority, StalenessRecord
what_not_to_do: No descarga datos. No decide qué hacer con cambios. Solo detecta y señaliza.
design_notes:   Depende de motor_008, motor_004, motor_002.

Implementation example uses deterministic comparison evidence only.
-->

## example
El orquestador de investigación llama a `SourceChangeDetectionRefreshIntelligence` después de recibir dos ingestas de la misma fuente regulatoria y su historial de versionado. La segunda ingesta conserva disponibilidad, pero trae una firma de schema distinta a la esperada y llega nueve días después de la última observación para una fuente con intervalo declarado de siete días. El motor debe emitir un evento de cambio de schema, una señal de staleness en observación y una prioridad alta de recaptura como señal advisory.

## inputs_used
```json
{
  "calculated_at": "2026-04-19T00:00:00Z",
  "source_registry": [
    {
      "source_id": "src_facility_roster_001",
      "rights_profile_ref": "rights:public_roster:v1",
      "access_class": "public",
      "declared_refresh_interval": "P7D",
      "declared_methodology_ref": "method:roster:v1",
      "expected_schema_signature": "schema:v1:name,address,license_id",
      "source_locator_ref": "registry:src_facility_roster_001",
      "use_status": "permitted"
    }
  ],
  "ingestion_records": [
    {
      "ingestion_id": "ing_2026_04_01",
      "source_id": "src_facility_roster_001",
      "captured_at": "2026-04-01T00:00:00Z",
      "availability_status": "available",
      "observed_schema_signature": "schema:v1:name,address,license_id",
      "content_fingerprint": "sha256:old001",
      "record_count": 1200,
      "raw_record_ref": "raw:ing_2026_04_01"
    },
    {
      "ingestion_id": "ing_2026_04_10",
      "source_id": "src_facility_roster_001",
      "captured_at": "2026-04-10T00:00:00Z",
      "availability_status": "available",
      "observed_schema_signature": "schema:v2:name,address,license_id,status",
      "content_fingerprint": "sha256:new001",
      "record_count": 1214,
      "raw_record_ref": "raw:ing_2026_04_10"
    }
  ],
  "version_history": [
    {
      "version_id": "ver_100",
      "object_ref": "dataset:facility_roster",
      "source_id": "src_facility_roster_001",
      "lineage_refs": ["lin:src_facility_roster_001", "lin:ing_2026_04_01"],
      "created_at": "2026-04-01T00:10:00Z",
      "previous_version_ref": null,
      "change_summary": "baseline ingestion",
      "affected_dependencies": []
    },
    {
      "version_id": "ver_117",
      "object_ref": "dataset:facility_roster",
      "source_id": "src_facility_roster_001",
      "lineage_refs": ["lin:src_facility_roster_001", "lin:ing_2026_04_10"],
      "created_at": "2026-04-10T00:10:00Z",
      "previous_version_ref": "ver_100",
      "change_summary": "schema signature changed",
      "affected_dependencies": ["dataset:facility_roster"]
    }
  ]
}
```

## expected_output
```json
{
  "change_detection_event": [
    {
      "source_id": "src_facility_roster_001",
      "change_type": "schema",
      "severity": "warning",
      "previous_ingestion_ref": "ing_2026_04_01",
      "current_ingestion_ref": "ing_2026_04_10",
      "previous_version_ref": "ver_100",
      "current_version_ref": "ver_117",
      "comparison_basis": {
        "previous_schema_signature": "schema:v1:name,address,license_id",
        "current_schema_signature": "schema:v2:name,address,license_id,status",
        "expected_schema_signature": "schema:v1:name,address,license_id"
      },
      "evidence_refs": ["ing_2026_04_01", "ing_2026_04_10", "ver_117"],
      "lineage_refs": ["lin:src_facility_roster_001", "lin:ing_2026_04_01", "lin:ing_2026_04_10"],
      "detection_rule_ref": "rule.schema_signature.changed",
      "produced_by_motor": "motor_009",
      "event_id": "stable hash-derived identifier",
      "version_hash": "deterministic hash over canonical event content"
    }
  ],
  "staleness_signal": [
    {
      "source_id": "src_facility_roster_001",
      "staleness_status": "watch",
      "last_observed_at": "2026-04-10T00:10:00Z",
      "expected_refresh_interval": "P7D",
      "age_days": 8,
      "triggering_condition": "interval_exceeded_and_schema_changed",
      "trigger_event_ids": ["schema change event_id"],
      "basis_ingestion_refs": ["ing_2026_04_01", "ing_2026_04_10"],
      "basis_version_refs": ["ver_100", "ver_117"],
      "produced_by_motor": "motor_009",
      "version_hash": "deterministic hash over canonical staleness content"
    }
  ],
  "refresh_priority": [
    {
      "source_id": "src_facility_roster_001",
      "priority_level": "high",
      "priority_reason": "schema_changed_and_refresh_interval_exceeded",
      "derived_from_event_ids": ["schema change event_id"],
      "staleness_id": "staleness record id",
      "rule_ref": "rule.priority.schema_change.stale.high",
      "evidence_refs": ["schema change event_id", "staleness record id", "ing_2026_04_01", "ing_2026_04_10", "ver_100", "ver_117"],
      "produced_by_motor": "motor_009",
      "version_hash": "deterministic hash over canonical priority content"
    }
  ],
  "errors": []
}
```

## notes
El motor presupone que `source_registry`, `ingestion_records` y `version_history` ya fueron producidos por los motores upstream correspondientes y que sus identificadores son trazables. La prioridad emitida no descarga datos, no agenda trabajos y no modifica registros upstream; solo señaliza una condición reproducible para consumidores posteriores. Si faltan `source_id`, timestamps parseables, evidencia comparable o lineage reconstruible, el motor emite errores estructurados y no produce salidas parciales para la fuente afectada.
