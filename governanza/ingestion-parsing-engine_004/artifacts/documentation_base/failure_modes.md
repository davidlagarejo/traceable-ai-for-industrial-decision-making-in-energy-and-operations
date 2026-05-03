# Failure Modes — Ingestion + Parsing Engine

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
- `RAW_NOT_PRESERVED`: parsed output exists but the original payload reference, checksum or immutable raw storage entry is missing.
- `LINEAGE_GAP`: accepted records cannot be traced back to a source reference, phase contract, lineage context or ingestion event.
- `SILENT_PARSE_MUTATION`: extracted values differ from raw source values because the parser trimmed, normalized, inferred or corrected them without declaring a downstream transformation.
- `PARSER_OVERREACH`: the parser emits canonical categories, identity decisions, quality judgments or enriched fields outside direct raw extraction.
- `REJECTION_NOT_STRUCTURED`: invalid input disappears from processing logs without a structured rejection object and explicit error code.

## anti_patterns
- Treating successful parsing as permission to delete, compress destructively or overwrite the preserved raw payload.
- Adding normalization, deduplication, identity resolution or quality scoring into parser code because the fields are already visible.
- Using parser convenience rules to fill missing values from file names, operator notes or external memory without recording that the value was not in the raw payload.
- Combining multiple source files into a single parsed record before preserving each raw input independently.

## degradation_signals
- Count of `parsed_record` outputs exceeds count of linked `raw_record` outputs for the same ingestion window.
- Any accepted `RawRecord` has a null `content_hash`, null `raw_payload_ref` or null `lineage_id`.
- Increase in parse success rate while rejection and warning logs fall to zero after source format changes.
- Parsed values show systematic trimming, date conversion, case normalization or unit conversion compared with raw payload samples.
- Ingestion events exist without corresponding structured rejection, raw record or parsed status outcome.
- The parser profile changes without a corresponding versioned parser identifier in lineage.
