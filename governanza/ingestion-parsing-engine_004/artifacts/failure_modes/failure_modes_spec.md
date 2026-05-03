# Failure Modes Spec — Ingestion + Parsing Engine

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

## failure_modes_list
- `FM004_RAW_PRESERVATION_LOSS`: accepted capture is parsed before durable raw preservation or without `raw_payload_ref` and `content_hash` → `ParsedRecord` exists but the original payload cannot be reconstructed or rehashed → reject the parsed output, quarantine the event, re-run capture from the original source if available, and require raw preservation before any new parsed output is emitted.
- `FM004_LINEAGE_CONTEXT_GAP`: input lacks `lineage_context_ref`, loses `lineage_id`, or emits objects with inconsistent `parent_id` values → downstream records cannot reconstruct the chain from motor_002 context to `IngestionEvent`, `RawRecord`, and `ParsedRecord` → emit `INGESTION_MISSING_LINEAGE_CONTEXT` before raw preservation when context is absent, or invalidate the affected event and rebuild outputs from the preserved raw plus a valid lineage context.
- `FM004_PHASE_CONTRACT_BYPASS`: capture proceeds when `phase_contract_ref` is missing, stale, or denied by motor_001 → unauthorized source data enters the system with apparently accepted status → emit `INGESTION_PHASE_CONTRACT_DENIED`, record a rejected `IngestionEvent`, and block raw or parsed output until an allowed phase contract reference is supplied.
- `FM004_SILENT_PARSE_MUTATION`: parser trims, normalizes, type-converts, infers, enriches, or repairs values while creating `extracted_fields` → extracted values no longer match the preserved payload even though `parse_status` appears successful → discard the mutated `ParsedRecord`, keep the immutable `RawRecord`, correct the parser profile, and re-emit parsing with observed raw values only.
- `FM004_UNSTRUCTURED_REJECTION`: malformed input is skipped, logged only as a generic exception, or rejected with an error outside the allowed rejection codes → operators cannot distinguish missing source, empty payload, missing content type, missing lineage, or phase denial → convert the failure into an `IngestionRejection` with the contractually allowed code and attach it to a rejected `IngestionEvent`.
- `FM004_DUPLICATE_DECISION_OVERREACH`: identical `content_hash` values cause the motor to suppress a capture, overwrite an existing `RawRecord`, merge events, or mark records as duplicates → repeated source observations disappear from ingestion history and later identity engines lose evidence → emit separate `IngestionEvent` and `RawRecord` objects for every capture attempt, preserving matching hashes only as trace data.
- `FM004_UNSUPPORTED_FORMAT_DATA_LOSS`: unsupported or partially supported media type causes payload deletion, no event, or invented extracted fields → raw evidence is unavailable and the parser masks unsupported format status → preserve the raw bytes, emit `unsupported_format` or an explicit parse warning, and leave `extracted_fields` empty unless values were directly observed.

## anti_patterns
- Coupling ingestion directly to normalization, identity resolution, deduplication, quality scoring, or evidentiary assessment instead of emitting raw and parsed records for downstream motors.
- Treating `content_hash` equality as a duplicate-resolution decision or as permission to overwrite an earlier `RawRecord`.
- Letting parser profiles repair source data by trimming whitespace, changing case, converting dates, converting units, filling missing fields, or enriching from file names and external knowledge.
- Making `ParsedRecord` the primary artifact and treating raw preservation as optional once parsing succeeds.
- Emitting accepted events without `phase_contract_ref`, `lineage_context_ref`, version fields, `produced_by_motor`, and explicit parent lineage.
- Handling malformed input through ad hoc logs, exceptions, or skipped files instead of structured `IngestionRejection` objects.
- Designing parser behavior that depends on nondeterministic model output, external memory, mutable prompts, or hidden operator state.
- Combining multiple payloads into one logical parsed record before each source payload has its own preserved raw record and event trace.

## degradation_signals
- Count of accepted `ParsedRecord` objects exceeds count of preserved linked `RawRecord` objects for the same ingestion window.
- Any accepted `RawRecord` has empty `raw_payload_ref`, empty `content_hash`, missing `media_type`, missing `lineage_id`, or `raw_preservation_status` other than `preserved`.
- Any accepted `IngestionEvent` lacks `phase_contract_ref`, `lineage_context_ref`, version fields, `produced_by_motor = "motor_004"`, or a parent id pointing to the lineage context.
- Parse success rate rises while `parse_warnings`, `unsupported_format`, and structured rejections drop to zero after a source format change.
- Sample comparisons show extracted values with changed casing, stripped leading zeros, normalized dates, trimmed whitespace, converted numeric types, or inferred fields not present in the payload.
- Repeated identical payload captures produce fewer events than capture attempts, indicating suppression or duplicate handling inside motor_004.
- Logs contain generic parser exceptions without matching `IngestionRejection` ids and rejected `IngestionEvent` records.
- Parser profile or parser version changes without corresponding changes in emitted `parser_profile`, `parser_version`, version hash, or lineage metadata.
- Large structured feeds produce partial parsed output before the full raw payload has been preserved and hashed.

## expensive_errors
- Losing or mutating the raw payload is expensive because every downstream normalized, identity, quality, and evidence object may become impossible to audit or rebuild. Prevention: require durable `raw_payload_ref`, deterministic `content_hash`, media type, capture timestamp, and immutable raw status before any parsed output is accepted.
- Emitting parsed records without lineage is expensive because downstream consumers may retain apparently valid structure that cannot be tied back to source, phase authority, or version history. Prevention: block accepted output without `lineage_context_ref`, `lineage_id`, `parent_id`, version fields, and `produced_by_motor`.
- Normalizing during parsing is expensive because later motors cannot separate observed source values from derived canonical values. Prevention: parser tests must compare extracted values against raw payload samples and fail on trimming, case conversion, date conversion, unit conversion, inferred values, or external enrichment.
- Suppressing repeated captures is expensive because temporal source observations disappear and later change detection or provenance review cannot distinguish repeated identical evidence from missing ingestion. Prevention: create a new `IngestionEvent` and `RawRecord` for every capture attempt even when `content_hash` matches an earlier record.
- Accepting payloads without phase-contract authorization is expensive because unauthorized data can propagate into governed artifacts and require broad rollback. Prevention: validate `phase_contract_ref` before raw preservation and emit `INGESTION_PHASE_CONTRACT_DENIED` with a rejected event when authorization is absent or denied.
- Skipping malformed input without structured rejection is expensive because operators lose the reason for data gaps and cannot distinguish source defects from system defects. Prevention: map precondition failures to the allowed `IngestionRejection` codes and attach each rejection to an auditable `IngestionEvent`.
- Inventing fields for unsupported formats is expensive because downstream motors may treat fabricated structure as source-observed fact. Prevention: preserve unsupported payloads as raw, emit `unsupported_format` or explicit parse warnings, and keep extracted fields empty unless the values are directly observable.
