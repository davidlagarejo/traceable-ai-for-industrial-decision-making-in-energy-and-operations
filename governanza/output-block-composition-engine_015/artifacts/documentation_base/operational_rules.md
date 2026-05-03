# Operational Rules — Output Block Composition Engine

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

## rules
1. The motor composes blocks only from `InferenceRecord` inputs produced by `motor_014` and authorized by a matching `PhaseContract` from `motor_001`.
2. Every emitted `OutputBlock` must be atomic: it contains one governed visible unit and must not contain a full report, view, section sequence or rendered document.
3. Every visible payload segment must be linked to at least one source inference identifier, one version reference and one lineage reference.
4. The motor must apply deterministic mapping rules from inference category to `block_type`; identical valid inputs under the same rule version produce the same block identity and payload structure.
5. The motor must preserve upstream identifiers exactly as received and must not silently correct inference, contract, lineage or version metadata.
6. Invalid inputs must be recorded in `composition_log` with a structured rejection code and must not produce partial `OutputBlock` records.
7. Batch output ordering must be deterministic, using stable source identifiers and rule version rather than filesystem order or runtime iteration side effects.
8. A block may reference multiple inference records only when the phase contract allows their combined visible unit and the trace covers each contributing inference separately.

## invariants
- `motor_id` for emitted objects is always `motor_015`.
- `phase_contract_ref` is never empty on emitted `OutputBlock`, `BlockTrace` or `CompositionRecord` entries that describe accepted input.
- Every emitted `OutputBlock.trace_id` resolves to exactly one emitted `BlockTrace.trace_id`.
- `BlockTrace.segment_refs` covers every addressable segment in `OutputBlock.visible_payload`.
- `version_refs` and `lineage_refs` are copied from validated upstream records or supplied version records; they are not invented by this motor.
- Upstream `InferenceRecord`, `PhaseContract` and `VersionRecord` content remains immutable from this motor's perspective.
- Re-running the same valid input set with the same contract version and rule version produces the same block identifiers, trace identifiers and accepted/rejected classification.

## forbidden_operations
- Assembling complete report packages, technical views, executive views, appendices or final document outlines.
- Rendering PDF, HTML, LaTeX, slides, dashboards, paginated documents or other final presentation formats.
- Creating new inferential claims, resolving analytical tensions or changing validation agendas.
- Verifying claims, assigning evidence quality or changing source quality decisions.
- Editing, overwriting, normalizing or superseding upstream `InferenceRecord`, `PhaseContract` or `VersionRecord` objects.
- Accepting manually written narrative fragments as direct output blocks when they are not derived from governed inference records.
- Emitting any block without `BlockTrace` and `CompositionRecord` coverage.
