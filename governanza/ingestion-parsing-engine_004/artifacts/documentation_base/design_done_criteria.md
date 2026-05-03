# Design Done Criteria — Ingestion + Parsing Engine

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

## criteria
- `master_concept_doc.md` states the motor purpose, concrete actions, exclusions and separate design rationale without open placeholders.
- `functional_contract.md` defines raw source files, API responses, structured feeds, phase contract references and lineage context references as inputs.
- `functional_contract.md` defines `raw_record`, `parsed_record`, `ingestion_lineage` and structured ingestion rejection as outputs.
- `conceptual_schema.md` defines `RawRecord`, `ParsedRecord` and `IngestionEvent` with required fields and traceable relationships.
- `operational_rules.md` prohibits normalization, duplicate resolution, quality evaluation, identity resolution, silent correction and raw deletion.
- `acceptance_tests.md` includes one concrete happy path, multiple edge cases and explicit rejection criteria with error signals.
- `failure_modes.md` lists raw preservation, lineage, silent mutation, parser overreach and structured rejection risks.
- All documentation base artifacts contain no unresolved placeholder markers and are ready to drive the schema technical stage without inventing new responsibilities.
