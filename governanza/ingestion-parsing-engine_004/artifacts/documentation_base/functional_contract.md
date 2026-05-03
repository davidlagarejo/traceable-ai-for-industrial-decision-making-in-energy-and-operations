# Functional Contract — Ingestion + Parsing Engine

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

## inputs
- `raw_source_file`: file payload — bytes or text file captured from an external source, operator drop zone, or approved source connector.
- `api_response`: HTTP response payload — response body plus status code, headers, URL, request timestamp and source identifier from an approved API capture.
- `structured_feed`: structured feed payload — CSV, JSON, XML, NDJSON or similar feed received from an external source or approved source connector.
- `phase_contract_ref`: string — contract reference from motor_001 defining whether the ingestion action is allowed in the current phase.
- `lineage_context_ref`: string — lineage/session reference from motor_002 used to attach ingestion outputs to reconstructible provenance.

## outputs
- `raw_record`: RawRecord object — preserved raw payload reference, checksum and capture metadata stored for audit, rebuild and downstream parsing traceability.
- `parsed_record`: ParsedRecord object — deterministic partial extraction linked to exactly one `raw_record`, available to downstream normalization and document hygiene motors when authorized.
- `ingestion_lineage`: IngestionEvent lineage object — event-level trace connecting source, capture action, phase contract, lineage context, raw record and parsed record.
- `ingestion_rejection`: structured error object — explicit rejection emitted when required provenance, payload, content type or parse preconditions are missing.

## limits
- The motor never accepts an input payload without a stable source reference, declared content type, capture timestamp and lineage context.
- The motor never accepts a payload that requires semantic correction, normalization or inferred missing values in order to be ingested.
- The motor never produces canonical normalized records, resolved entity identities, duplicate decisions, quality scores or evidentiary claims.
- The motor never overwrites an existing raw payload for the same `raw_record_id`; a new capture must become a new immutable record or versioned event.
- The motor never emits a `parsed_record` that is detached from a preserved `raw_record`.
- The motor never treats successful parsing as proof that the source is reliable, current, complete or fit for use.

## validations
- Reject input with `INGESTION_MISSING_SOURCE_REF` when `source_ref` is empty, unstable or absent.
- Reject input with `INGESTION_EMPTY_PAYLOAD` when the raw bytes or response body are empty.
- Reject input with `INGESTION_MISSING_CONTENT_TYPE` when no media type, file extension or parser profile can be declared.
- Reject input with `INGESTION_MISSING_LINEAGE_CONTEXT` when the event cannot be attached to a motor_002 lineage context.
- Reject input with `INGESTION_PHASE_CONTRACT_DENIED` when motor_001 does not allow the capture or handoff for the current phase.
- Before emitting `raw_record`, compute and store `content_hash`, `captured_at`, `source_ref`, `raw_payload_ref`, `media_type` and `lineage_id`.
- Before emitting `parsed_record`, verify that `raw_record_id`, `parser_profile`, `parse_status`, `extracted_fields` and `created_at` are present.
- The parser must preserve original field values exactly as observed; trimmed, normalized, inferred or converted values are not valid outputs of this motor.
- Every `ingestion_lineage` must reference one `IngestionEvent` and at least one `RawRecord`; if parsing succeeds, it must also reference the resulting `ParsedRecord`.
