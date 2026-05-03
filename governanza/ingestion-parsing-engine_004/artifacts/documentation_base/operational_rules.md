# Operational Rules — Ingestion + Parsing Engine

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

## rules
1. Every accepted input must produce a preserved `RawRecord` before any parsed output is considered complete.
2. Every `RawRecord` must include a stable source reference, capture timestamp, media type, content hash, raw payload reference and lineage identifier.
3. Parsing must be deterministic for the same raw payload, parser profile and parser version.
4. Parsing may extract only fields directly observable in the raw payload; missing or ambiguous fields remain absent or explicitly marked as unparsed.
5. Every `ParsedRecord` must reference exactly one preserved `RawRecord`.
6. Every ingestion run must create an `IngestionEvent` whether the payload is accepted, partially parsed or rejected.
7. Rejections must be explicit structured errors; the motor must not silently skip malformed or under-specified input.
8. The motor must preserve original values exactly as captured, including casing, whitespace inside field values and source-provided formatting.

## invariants
- `raw_payload_ref` and `content_hash` are never changed after a `RawRecord` is emitted.
- `lineage_id` or `lineage_context_ref` is never null on accepted outputs.
- `parsed_record.raw_record_id` always points to an existing `RawRecord`.
- `ingestion_event_id` is unique for each capture attempt.
- `parse_status` is always explicit; there is no implicit success state.
- A parsing failure never deletes or mutates the preserved raw record.
- Original raw values remain distinguishable from any downstream derived values.

## forbidden_operations
- Normalizing values into canonical units, canonical names, canonical categories or canonical date formats.
- Resolving duplicate records, near-duplicates, document similarity or entity identity.
- Computing or assigning quality, fitness, trust, confidence or evidentiary scores.
- Correcting malformed source data without emitting a rejection or parse warning.
- Enriching records with external knowledge not present in the captured payload.
- Merging two raw records into one logical entity.
- Deleting raw payloads because parsing succeeded.
- Producing downstream analytical claims, reports or recommendations.
