# Conceptual Schema — Output Block Composition Engine

Motor ID: motor_015

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Construir bloques visibles trazables para Fase 3 desde decisions e inferencias.
why_it_exists:  Separa contenido visible gobernado del ensamblaje documental final.
key_inputs:     inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    output_block, block_trace, composition_log
key_objects:    OutputBlock, BlockTrace, CompositionRecord
what_not_to_do: No ensambla reportes completos. No renderiza documentos. Solo construye bloques atómicos.
design_notes:   Cada bloque es trazable a su fuente inferencialmente.

Documentation-base content completed for this artifact.
-->

## entities
- `OutputBlock`: atomic visible content unit for Fase 3, derived from one or more authorized inference records and suitable for downstream assembly.
- `BlockTrace`: trace object that maps an output block and its visible payload segments to source inference records, version records, lineage references and phase contract.
- `CompositionRecord`: audit record for one composition operation, including accepted inputs, rejected inputs, deterministic rule version and emitted block identifiers.

## relationships
- `InferenceRecord` -> `OutputBlock` (one or more inference records provide the governed inferential content for a visible block).
- `PhaseContract` -> `OutputBlock` (the contract authorizes whether the block type and output boundary are allowed).
- `VersionRecord` -> `OutputBlock` (version records bind the block to immutable source object versions and payload fingerprints).
- `OutputBlock` -> `BlockTrace` (each emitted block has exactly one trace record covering the visible payload).
- `BlockTrace` -> `InferenceRecord` (the trace points back to every inference used by the block).
- `BlockTrace` -> `VersionRecord` (the trace points back to the version records needed for audit and rebuild).
- `CompositionRecord` -> `OutputBlock` (a composition operation records zero or more emitted blocks).
- `CompositionRecord` -> `BlockTrace` (a composition operation records the trace identifiers associated with emitted blocks).

## key_fields
`OutputBlock`
- `block_id`: `str`
- `motor_id`: `str`
- `phase_id`: `str`
- `block_type`: `str`
- `visible_payload`: `dict`
- `source_inference_ids`: `list[str]`
- `phase_contract_ref`: `str`
- `version_refs`: `list[str]`
- `lineage_refs`: `list[str]`
- `trace_id`: `str`

`BlockTrace`
- `trace_id`: `str`
- `block_id`: `str`
- `segment_refs`: `list[dict]`
- `source_inference_ids`: `list[str]`
- `version_refs`: `list[str]`
- `lineage_refs`: `list[str]`
- `phase_contract_ref`: `str`
- `rule_version`: `str`

`CompositionRecord`
- `composition_id`: `str`
- `input_refs`: `list[str]`
- `accepted_refs`: `list[str]`
- `rejected_refs`: `list[dict]`
- `emitted_block_ids`: `list[str]`
- `rule_version`: `str`
- `status`: `str`
- `created_at`: `datetime`
