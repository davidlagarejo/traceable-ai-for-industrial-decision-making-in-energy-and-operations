# Failure Modes — Output Block Composition Engine

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

## failure_modes_list
- `TRACE_GAP`: an emitted block contains visible payload that cannot be mapped segment-by-segment to inference, version and lineage references.
- `CONTRACT_DRIFT`: blocks are emitted using a stale or mismatched phase contract, so downstream assembly receives block types or output boundaries not authorized for the current phase.
- `BLOCK_SCOPE_CREEP`: an `OutputBlock` grows into a report section, narrative sequence or audience-specific view instead of remaining atomic.
- `VERSION_MISMATCH`: `version_refs` on the block do not match the supplied `VersionRecord` for the source inference or payload fingerprint.
- `NONDETERMINISTIC_COMPOSITION`: identical inputs under the same rule version produce different block identifiers, ordering or payload structures across runs.

## anti_patterns
- Feeding manually written report prose into the motor and treating it as if it were a governed `InferenceRecord`.
- Using this motor to assemble full report packages or audience-specific narratives before the downstream assembly stage.
- Paraphrasing or strengthening inference content during block composition instead of using deterministic templates and authorized visible fields.
- Ignoring rejected inputs in `composition_log` and allowing downstream assembly to proceed as though all expected blocks were produced.

## degradation_signals
- Any emitted `OutputBlock` has an empty `trace_id`, empty `version_refs` or empty `lineage_refs`.
- The count of `TRACE_GAP`, `VERSION_MISMATCH` or `PHASE_CONTRACT_VIOLATION` rejection codes increases across runs for the same upstream batch.
- Re-running the same valid batch with the same rule version changes block identifiers, output order or accepted/rejected classification.
- Average visible payload size grows until blocks resemble report sections rather than atomic visible units.
- Composition records show accepted inputs without matching emitted block identifiers or emitted block identifiers without matching trace identifiers.
- Downstream assembly requires manual interpretation of block origin because trace coverage is incomplete or inconsistent.
