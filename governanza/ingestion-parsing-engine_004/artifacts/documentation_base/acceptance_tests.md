# Acceptance Tests — Ingestion + Parsing Engine

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

## happy_path
Input: `api_response` from `source_ref = "epa_facility_api:v1"` with `status_code = 200`, `media_type = "application/json"`, `captured_at = "2026-04-16T14:10:00Z"`, body `{"facility_id":"TX-001","name":"North Plant","permit":"P-778"}`, `phase_contract_ref = "motor_001:phase_1_public_data"`, and `lineage_context_ref = "motor_002:lineage_run_20260416_001"`.

Action: the motor validates provenance, preserves the response body as a `RawRecord`, computes a content hash, applies the declared JSON parser profile, extracts directly observable fields, and creates an `IngestionEvent`.

Expected output: one `raw_record` with the unmodified JSON body and content hash; one `parsed_record` with `extracted_fields.facility_id = "TX-001"`, `extracted_fields.name = "North Plant"` and `extracted_fields.permit = "P-778"`; one `ingestion_lineage` linking the source, event, raw record, parser profile and parsed record.

## edge_cases
- Empty but reachable feed: a CSV file with headers `facility_id,name,permit` and zero data rows is accepted as a `RawRecord`, produces `parse_status = "partially_parsed"` or an empty `extracted_fields` map, and records a parse warning without inventing rows.
- Large source file: a 250 MB NDJSON file with valid source metadata is accepted only if the raw payload can be preserved and hashed; parsed output may be partial by record count, but the `RawRecord` remains complete and immutable.
- Unsupported format: a binary spreadsheet macro file with declared media type is preserved as `RawRecord` when policy allows raw capture, but emits `parse_status = "unsupported_format"` and no synthetic extracted fields.
- Repeated capture of the same payload: identical content from the same source receives its own `IngestionEvent`; this motor may record matching checksums but must not decide duplicate status or suppress the new event.

## rejection_criteria
- Missing source reference: input without `source_ref` is rejected with `INGESTION_MISSING_SOURCE_REF` and no `raw_record` is emitted.
- Empty payload: input with zero bytes or an empty API body is rejected with `INGESTION_EMPTY_PAYLOAD` unless the capture contract explicitly defines an empty feed as a valid source artifact.
- Missing lineage context: input without `lineage_context_ref` is rejected with `INGESTION_MISSING_LINEAGE_CONTEXT`.
- Phase contract denial: input not allowed by `phase_contract_ref` is rejected with `INGESTION_PHASE_CONTRACT_DENIED`.
- Undeclared content type: payload with no media type, file extension or parser profile is rejected with `INGESTION_MISSING_CONTENT_TYPE` when the motor cannot preserve it under a declared raw capture policy.
