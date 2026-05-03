# Conceptual Schema — Ingestion + Parsing Engine

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
- `RawRecord`: immutable preserved representation of the captured payload and its capture metadata.
- `ParsedRecord`: deterministic partial structure extracted from one `RawRecord` without normalizing or judging the values.
- `IngestionEvent`: auditable event that records how, when and under which contract a source payload entered the system.

## relationships
- `IngestionEvent` → `RawRecord` (one event creates one or more raw records when a capture batch contains multiple payloads).
- `RawRecord` → `ParsedRecord` (one raw record may produce zero or one parsed record for a given parser profile; zero is valid when parsing fails or is unsupported).
- `ParsedRecord` → `RawRecord` (every parsed record must reference exactly one preserved raw record as its reconstruction base).
- `IngestionEvent` → `ParsedRecord` (the event records the parser profile and parse status for any parsed output produced during capture).
- `IngestionEvent` → `ingestion_lineage` (the event is the anchor used by downstream systems to reconstruct source, raw preservation and parsing path).

## key_fields
### RawRecord
- `raw_record_id`: string
- `source_ref`: string
- `raw_payload_ref`: string
- `content_hash`: string
- `media_type`: string
- `captured_at`: datetime
- `lineage_id`: string

### ParsedRecord
- `parsed_record_id`: string
- `raw_record_id`: string
- `parser_profile`: string
- `parse_status`: enum(`parsed`, `partially_parsed`, `unsupported_format`, `parse_failed`)
- `extracted_fields`: map[string, raw_value]
- `created_at`: datetime

### IngestionEvent
- `ingestion_event_id`: string
- `source_ref`: string
- `phase_contract_ref`: string
- `lineage_context_ref`: string
- `raw_record_ids`: list[string]
- `parsed_record_ids`: list[string]
- `event_status`: enum(`accepted`, `accepted_with_parse_warning`, `rejected`)
- `occurred_at`: datetime
