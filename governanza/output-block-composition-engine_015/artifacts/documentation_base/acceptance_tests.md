# Acceptance Tests — Output Block Composition Engine

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

## happy_path
Input: one `InferenceRecord` with `inference_id = "inf-014-0007"`, `case_id = "case-044"`, `phase_id = "fase_2"`, `phase_contract_ref = "pc-f3-output-blocks-v1"`, `contract_version = "1.0.0"`, `inference_category = "gap"`, `visible_statement = "Missing evidence for supplier renewal cadence."`, `lineage_refs = ["lin-103"]`, `rule_version = "m015-rules-v1"` and `created_at = "2026-04-17T10:00:00Z"`. The supplied `PhaseContract` allows `inference_records` as input and `output_block`, `block_trace` and `composition_log` as outputs. The supplied `VersionRecord` resolves `inf-014-0007` to `version_id = "ver-inf-014-0007-v1"` and includes the same lineage reference.

Action: the motor validates the contract, version and lineage references, maps `inference_category = "gap"` to an allowed block type, and composes the visible payload without adding a new claim.

Expected output: one `OutputBlock` with a stable `block_id`, `block_type = "gap_block"`, `visible_payload.statement = "Missing evidence for supplier renewal cadence."`, `source_inference_ids = ["inf-014-0007"]`, `version_refs = ["ver-inf-014-0007-v1"]`, `lineage_refs = ["lin-103"]`, and `trace_id` populated. One `BlockTrace` maps the statement segment to `inf-014-0007`, `ver-inf-014-0007-v1`, `lin-103` and `pc-f3-output-blocks-v1`. One `CompositionRecord` reports accepted input `inf-014-0007`, no rejected inputs, the applied rule version, and the emitted block identifier.

## edge_cases
- Sparse valid inference: if an `InferenceRecord` has the required identifiers, contract reference, version reference, lineage reference and one allowed visible field, but optional explanatory fields are empty, the motor emits a minimal `OutputBlock` and complete `BlockTrace` rather than inventing explanatory text.
- Shared version reference: if two valid inference records reference the same `VersionRecord`, the motor emits separate atomic blocks unless a phase contract explicitly authorizes their combination; both traces may reference the same version identifier without merging the inferential claims.
- Large valid batch: if a batch contains many valid inference records, output order is stable by deterministic source identifiers, and repeated runs with the same rule version produce the same `block_id` sequence.

## rejection_criteria
- Reject with `MISSING_TRACEABILITY` when an inference lacks `lineage_refs`, lacks a resolvable `VersionRecord`, or cannot be tied to a supplied phase contract.
- Reject with `PHASE_CONTRACT_VIOLATION` when the matching phase contract does not allow `inference_records` as input or does not allow `output_block`, `block_trace` and `composition_log` as outputs.
- Reject with `UNSUPPORTED_BLOCK_MAPPING` when the inference category has no deterministic mapping to an allowed `block_type`.
- Reject with `EMPTY_VISIBLE_PAYLOAD` when the inference has required metadata but no contract-allowed visible field to place in an atomic block.
