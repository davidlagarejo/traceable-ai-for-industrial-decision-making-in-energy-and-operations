# Usage Example — Ingestion + Parsing Engine

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

## example
Un conector autorizado captura una respuesta JSON de una API pública de instalaciones y la entrega a `IngestionParsingEngine` con contrato de fase permitido y contexto de lineage ya creado. El motor preserva los bytes originales como `RawRecord`, calcula el hash del contenido y extrae solamente los campos planos observables en el JSON. El resultado esperado es una ingesta aceptada con `RawRecord`, `ParsedRecord` e `IngestionEvent` enlazados, sin normalizar valores ni decidir calidad, duplicidad o identidad.

## inputs_used
```json
{
  "input_kind": "api_response",
  "source_ref": "epa_facility_api:v1:facility/TX-001",
  "status_code": 200,
  "headers": {
    "content-type": "application/json"
  },
  "url": "https://api.example.gov/facilities/TX-001",
  "media_type": "application/json",
  "captured_at": "2026-04-16T14:10:00Z",
  "phase_contract_ref": "motor_001:phase_public_ingestion:allow",
  "lineage_context_ref": "motor_002:lineage_run_20260416_004",
  "parser_profile": "json_flat_v1",
  "parser_version": "1.0.0",
  "payload": "{\"facility_id\":\"TX-001\",\"name\":\"North Plant\",\"zip\":\"00725\",\"permit\":\"P-778\"}"
}
```

## expected_output
```json
{
  "raw_record": {
    "raw_record_id": "raw_record_20234501ec9b18a95d592be8",
    "source_ref": "epa_facility_api:v1:facility/TX-001",
    "raw_payload_ref": "raw://motor_004/motor_002_lineage_run_20260416_004/raw_record_20234501ec9b18a95d592be8/ac13d245795693f8db6334e4748282bf817facdaf20b3a005ddb4dfffa5cf079",
    "content_hash": "ac13d245795693f8db6334e4748282bf817facdaf20b3a005ddb4dfffa5cf079",
    "media_type": "application/json",
    "captured_at": "2026-04-16T14:10:00Z",
    "lineage_id": "motor_002:lineage_run_20260416_004",
    "ingestion_event_id": "ingestion_event_55a459903c739733b8891300",
    "payload_size_bytes": 76,
    "raw_preservation_status": "preserved",
    "version_id": "raw_record_20234501ec9b18a95d592be8:v1",
    "created_at": "2026-04-16T14:10:00Z",
    "updated_at": "2026-04-16T14:10:00Z",
    "version_hash": "d21ea31f45ea7b7311055b352c5136aca5d7661a5528a34488f6127c995f418b",
    "produced_by_motor": "motor_004",
    "produced_at": "2026-04-16T14:10:00Z",
    "parent_id": "ingestion_event_55a459903c739733b8891300"
  },
  "parsed_record": {
    "parsed_record_id": "parsed_record_e1cf656006585f75ca88ee62",
    "raw_record_id": "raw_record_20234501ec9b18a95d592be8",
    "source_ref": "epa_facility_api:v1:facility/TX-001",
    "parser_profile": "json_flat_v1",
    "parser_version": "1.0.0",
    "parse_status": "parsed",
    "extracted_fields": {
      "facility_id": "TX-001",
      "name": "North Plant",
      "zip": "00725",
      "permit": "P-778"
    },
    "parse_warnings": [],
    "created_at": "2026-04-16T14:10:00Z",
    "ingestion_event_id": "ingestion_event_55a459903c739733b8891300",
    "version_id": "parsed_record_e1cf656006585f75ca88ee62:v1",
    "updated_at": "2026-04-16T14:10:00Z",
    "version_hash": "c36b78683e7c73db43777d6f3ce26a6fa2591a9ed2fe94eb4b5c0184cf2599de",
    "lineage_id": "motor_002:lineage_run_20260416_004",
    "produced_by_motor": "motor_004",
    "produced_at": "2026-04-16T14:10:00Z",
    "parent_id": "raw_record_20234501ec9b18a95d592be8"
  },
  "ingestion_lineage": {
    "ingestion_event_id": "ingestion_event_55a459903c739733b8891300",
    "source_ref": "epa_facility_api:v1:facility/TX-001",
    "phase_contract_ref": "motor_001:phase_public_ingestion:allow",
    "lineage_context_ref": "motor_002:lineage_run_20260416_004",
    "raw_record_ids": ["raw_record_20234501ec9b18a95d592be8"],
    "parsed_record_ids": ["parsed_record_e1cf656006585f75ca88ee62"],
    "rejection_ids": [],
    "event_status": "accepted",
    "occurred_at": "2026-04-16T14:10:00Z",
    "version_id": "ingestion_event_55a459903c739733b8891300:v1",
    "created_at": "2026-04-16T14:10:00Z",
    "updated_at": "2026-04-16T14:10:00Z",
    "version_hash": "478a5a3cdb8efadfc69852b970ce44fdf68f725e94811518a6329f454c0db6c6",
    "produced_by_motor": "motor_004",
    "produced_at": "2026-04-16T14:10:00Z",
    "parent_id": "motor_002:lineage_run_20260416_004"
  },
  "ingestion_rejection": null
}
```

## notes
El ejemplo asume que `phase_contract_ref` ya fue autorizado por motor_001 y que `lineage_context_ref` ya existe bajo motor_002. Los identificadores y hashes mostrados corresponden a una primera llamada en una instancia nueva del motor con esos bytes exactos. El motor preserva el raw completo antes de crear el parsed record y no corrige, recorta, normaliza, convierte fechas, resuelve duplicados ni asigna puntuaciones de calidad.
