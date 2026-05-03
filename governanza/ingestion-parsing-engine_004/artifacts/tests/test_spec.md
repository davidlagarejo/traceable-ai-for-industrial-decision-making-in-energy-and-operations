# Test Spec — Ingestion + Parsing Engine

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
Input: one `api_response` capture with:
- `source_ref = "epa_facility_api:v1:facility/TX-001"`
- `status_code = 200`
- `media_type = "application/json"`
- `captured_at = "2026-04-16T14:10:00Z"`
- `phase_contract_ref = "motor_001:phase_public_ingestion:allow"`
- `lineage_context_ref = "motor_002:lineage_run_20260416_004"`
- `parser_profile = "json_flat_v1"`
- `parser_version = "1.0.0"`
- raw body bytes equal to `{"facility_id":"TX-001","name":"North Plant","zip":"00725","permit":"P-778"}`

Expected output:
- One `IngestionEvent` with `event_status = "accepted"`, `source_ref` equal to the input source, `phase_contract_ref` equal to the input phase contract, `lineage_context_ref` equal to the input lineage context, `produced_by_motor = "motor_004"`, `parent_id = "motor_002:lineage_run_20260416_004"`, one `raw_record_id`, one `parsed_record_id`, and no rejection ids.
- One `RawRecord` with `raw_preservation_status = "preserved"`, `source_ref = "epa_facility_api:v1:facility/TX-001"`, `media_type = "application/json"`, `captured_at = "2026-04-16T14:10:00Z"`, non-empty `raw_payload_ref`, deterministic `content_hash` calculated over the exact raw body bytes, `lineage_id = "motor_002:lineage_run_20260416_004"`, `parent_id` equal to the emitted `ingestion_event_id`, and `produced_by_motor = "motor_004"`.
- One `ParsedRecord` with `parse_status = "parsed"`, `raw_record_id` equal to the emitted raw record id, `source_ref` equal to the input source, `parser_profile = "json_flat_v1"`, `parser_version = "1.0.0"`, `parent_id` equal to the emitted raw record id, and `extracted_fields` containing exactly `facility_id = "TX-001"`, `name = "North Plant"`, `zip = "00725"`, and `permit = "P-778"` as observed values.

## sparse_case
Input: one `structured_feed` capture with:
- `source_ref = "state_permit_csv:daily:2026-04-16"`
- `media_type = "text/csv"`
- `captured_at = "2026-04-16T15:00:00Z"`
- `phase_contract_ref = "motor_001:phase_public_ingestion:allow"`
- `lineage_context_ref = "motor_002:lineage_run_20260416_004"`
- `parser_profile = "csv_header_row_v1"`
- `parser_version = "1.0.0"`
- raw body bytes equal to `facility_id,name,permit,operator_note\nTX-002,South Plant,,\n`

Expected output:
- The capture does not fail fatally because `permit` and `operator_note` are optional under the parser profile and the required provenance fields are present.
- One preserved `RawRecord` is emitted with the exact CSV bytes, content hash, media type, source reference and lineage reference.
- One `ParsedRecord` is emitted with `parse_status = "partially_parsed"`, `raw_record_id` linked to the preserved raw record, and `extracted_fields.facility_id = "TX-002"` and `extracted_fields.name = "South Plant"`.
- `extracted_fields` does not invent `permit` or `operator_note`; they are absent or represented only as source-empty raw values according to the parser profile.
- `parse_warnings` contains an explicit warning for source-empty optional fields, and the `IngestionEvent` uses `event_status = "accepted_with_parse_warning"`.

## malformed_input
Input: one `api_response` capture with:
- `source_ref = ""`
- `status_code = 200`
- `media_type = "application/json"`
- `captured_at = "2026-04-16T16:00:00Z"`
- `phase_contract_ref = "motor_001:phase_public_ingestion:allow"`
- `lineage_context_ref = "motor_002:lineage_run_20260416_004"`
- raw body bytes equal to `{"facility_id":"TX-003"}`

Expected output:
- The motor rejects the attempt with one `IngestionRejection` where `error_code = "INGESTION_MISSING_SOURCE_REF"` and `error_message` identifies that the stable source reference is absent.
- The `IngestionEvent` is still emitted for audit with `event_status = "rejected"`, `raw_record_ids = []`, `parsed_record_ids = []`, and `rejection_ids` containing the emitted rejection id.
- No `RawRecord` or `ParsedRecord` is emitted because required provenance failed before raw preservation was allowed.
- The rejection includes `phase_contract_ref`, `lineage_context_ref`, `produced_by_motor = "motor_004"`, version fields, and `parent_id` equal to the rejected event id.

## edge_cases
1. Unsupported declared format:
   - Input: `raw_source_file` with `source_ref = "operator_drop:macro_workbook_001"`, `media_type = "application/vnd.ms-excel.sheet.macroEnabled.12"`, valid capture timestamp, valid phase contract, valid lineage context, parser profile `binary_preserve_only_v1`, and non-empty binary bytes.
   - Expected behavior: the raw payload is preserved and hashed as a `RawRecord`; parsing emits `parse_status = "unsupported_format"` with empty `extracted_fields` and an explicit parse warning, or emits no parsed record if the implementation represents unsupported parsing as zero parsed outputs. In both representations, the event remains traceable and no synthetic fields are created.

2. Repeated capture with identical payload:
   - Input: two ingestion attempts from `source_ref = "epa_facility_api:v1:facility/TX-001"` with identical body bytes, identical media type, and the same lineage context, captured at `2026-04-16T14:10:00Z` and `2026-04-16T14:20:00Z`.
   - Expected behavior: two distinct `IngestionEvent` ids and two distinct `RawRecord` ids are emitted. The `content_hash` values may match, but the motor does not suppress the second event, merge records, mark duplicates, or emit any duplicate-resolution field.

3. Empty payload:
   - Input: `api_response` with valid `source_ref`, `media_type`, capture timestamp, phase contract and lineage context, but raw body bytes equal to zero length.
   - Expected behavior: the motor rejects the attempt with `INGESTION_EMPTY_PAYLOAD`, emits a rejected `IngestionEvent`, and emits no `RawRecord` or `ParsedRecord`.

4. Large structured feed:
   - Input: `structured_feed` with `source_ref = "state_ndjson:daily:2026-04-16"`, `media_type = "application/x-ndjson"`, valid phase contract, valid lineage context, parser profile `ndjson_line_v1`, and a payload large enough that partial parsing is allowed by resource policy.
   - Expected behavior: the full raw payload is preserved and hashed before any parsed output is considered valid. Parsed output may be `partially_parsed` with warnings, but raw preservation remains complete and immutable.

## pass_criteria
- Accepted cases emit an `IngestionEvent` with explicit status, phase contract reference, lineage context reference, version fields, `produced_by_motor = "motor_004"`, and correct parent lineage.
- Every accepted case emits a `RawRecord` before or with parsed output, with non-empty `raw_payload_ref`, deterministic `content_hash`, exact source media type, `raw_preservation_status = "preserved"`, version fields and parent event id.
- Every emitted `ParsedRecord` references exactly one preserved `RawRecord`, carries parser profile and parser version, has explicit `parse_status`, and preserves extracted values exactly as observed in the raw payload.
- Sparse or unsupported parsing cases complete without fatal failure when required provenance and non-empty raw bytes are present; they must expose partial or unsupported status through `parse_status`, `parse_warnings`, or zero parsed outputs according to the declared representation.
- Rejected cases emit a structured `IngestionRejection` with an allowed error code and an auditable rejected `IngestionEvent`, while emitting no raw or parsed records when preconditions fail before raw preservation.

## fail_criteria
- Any accepted output lacks a preserved raw payload reference, content hash, source reference, media type, version field, lineage reference, or parent event id.
- A parsed record exists without a valid `raw_record_id`, parser profile, parser version, explicit parse status, or link to the same ingestion event lineage.
- Extracted values are normalized, trimmed, case-converted, date-converted, type-converted, inferred from file names, enriched from external knowledge, or otherwise changed from the raw source representation.
- A malformed input is silently skipped, raises only an unstructured exception, or emits a rejection without one of the allowed error codes.
- A missing source reference, missing lineage context, missing content type, empty payload, or phase-contract denial produces a `RawRecord` instead of the corresponding structured rejection.
- Repeated identical payloads are merged, suppressed, marked as duplicate decisions, or used to overwrite an earlier raw record.
- Unsupported format handling deletes the raw payload, loses the event lineage, or invents extracted fields not present in the raw bytes.
