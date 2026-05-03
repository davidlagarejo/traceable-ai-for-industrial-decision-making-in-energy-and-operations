# Failure Modes Spec — Output Block Composition Engine

Motor ID: motor_015

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Construir bloques visibles trazables para Fase 3 desde decisions e inferencias.
why_it_exists:  Separa contenido visible gobernado del ensamblaje documental final.
key_inputs:     inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    output_block, block_trace, composition_log
key_objects:    OutputBlock, BlockTrace, CompositionRecord
what_not_to_do: No ensambla reportes completos. No renderiza documentos. Solo construye bloques atómicos.
design_notes:   Cada bloque es trazable a su fuente inferencialmente.

Failure-mode content completed for this artifact.
-->

## failure_modes_list
- `TRACE_GAP`: an accepted `InferenceRecord` produces an `OutputBlock.visible_payload` field with no matching `BlockTrace.segment_refs` entry -> auditors or downstream assembly cannot prove which inference, version and lineage produced the visible segment -> reject the block before emission, record `TRACE_GAP` in `CompositionRecord.rejected_refs`, rebuild trace coverage for every payload path, then rerun composition with the same rule version.
- `MISSING_TRACEABILITY`: `phase_contract_ref`, `version_refs` or `lineage_refs` cannot be resolved from supplied `PhaseContract` and `VersionRecord` inputs -> the candidate block lacks required provenance and no deterministic rebuild path exists -> emit no `OutputBlock`, write a structured rejection with the unresolved reference names, and require upstream contract or version records before retry.
- `CONTRACT_DRIFT`: an inference references a stale or mismatched contract version, or the selected `block_type` / visible field is not allowed by the active `PhaseContract` -> output shape differs from the phase boundary expected by downstream Fase 3 assembly -> reject the input with a contract-resolution code, reload the correct contract bundle, and rerun without altering the upstream inference.
- `VERSION_MISMATCH`: a supplied `VersionRecord.object_ref`, `phase_contract_ref`, `content_hash` or lineage set does not match the source inference used for composition -> block metadata points to the wrong immutable upstream object -> reject the affected input, record the mismatched fields in `CompositionRecord.rejected_refs`, and require corrected upstream version registration.
- `EMPTY_VISIBLE_PAYLOAD`: the inference is structurally valid but none of the contract-allowed visible fields is present with non-empty content -> the motor would emit an atomic block with no governed visible unit -> reject the input, keep `emitted_block_ids` empty for that record, and request an upstream inference that exposes at least one allowed visible field.
- `UNSUPPORTED_BLOCK_MAPPING`: the inference category is not present in the phase contract's deterministic `block_type_map` -> the motor cannot select a governed atomic block type -> reject the input with the unsupported category named in the reason, and update the phase contract or upstream category outside this motor before retry.
- `BLOCK_SCOPE_CREEP`: output generation adds section ordering, audience-specific wording, report narrative, layout hints or rendered fragments -> the motor starts doing motor_016 or motor_017 work instead of atomic block composition -> remove report-level fields, keep only contract-allowed visible payload, and record any non-atomic input as rejected rather than producing a block.
- `NONDETERMINISTIC_COMPOSITION`: identical valid inputs under the same `contract_version` and motor `rule_version` produce different `block_id`, `trace_id`, `composition_id`, output ordering or accepted/rejected classification -> rebuilds cannot be compared and downstream packages become unstable -> canonicalize input ordering and hash material, exclude runtime-only values from deterministic identifiers, and rerun until identity is stable.

## anti_patterns
- Treating free-form analyst prose, report outlines or manually edited narrative as valid input instead of governed `InferenceRecord` objects from motor_014.
- Coupling this motor directly to report-package assembly, audience views, section sequencing, pagination, LaTeX, HTML, dashboards or other rendering concerns owned by downstream motors.
- Allowing `BlockTrace` or `CompositionRecord` creation to be optional, delayed, asynchronous or best-effort after `OutputBlock` emission.
- Silently normalizing upstream `InferenceRecord`, `PhaseContract` or `VersionRecord` fields to make composition pass.
- Using filesystem order, dictionary iteration side effects, wall-clock timestamps or random values inside canonical block, trace or composition identifiers.
- Copying all inference fields into `visible_payload` instead of filtering to the fields authorized by the matching phase contract.
- Emitting partial blocks for invalid records and relying on downstream assembly to ignore or repair them.
- Collapsing multiple unrelated inferences into one block when the phase contract does not explicitly authorize a combined visible unit and segment-level trace for each source.

## degradation_signals
- `trace_coverage_ratio < 1.0`: count of addressable `visible_payload` paths covered by `BlockTrace.segment_refs` divided by total addressable visible paths.
- Any emitted `OutputBlock` has empty `trace_id`, `source_inference_ids`, `version_refs`, `lineage_refs`, `phase_contract_ref`, `version_hash`, `source_ref` or `produced_by_motor`.
- `accepted_refs_count != emitted_block_ids_count` or `emitted_block_ids_count != trace_ids_count` in a `CompositionRecord` where each accepted input should produce one block.
- Rising frequency of `MISSING_TRACEABILITY`, `CONTRACT_DRIFT`, `VERSION_MISMATCH`, `EMPTY_VISIBLE_PAYLOAD` or `UNSUPPORTED_BLOCK_MAPPING` rejections for the same upstream batch.
- Rebuild checks show different `block_id`, `trace_id`, `composition_id`, output order or accepted/rejected classification for identical inputs, contract version and rule version.
- Average `visible_payload` size, nested depth or field count grows until blocks resemble report sections instead of atomic visible units.
- Logs contain accepted inputs whose `phase_contract_ref` or `contract_version` differs from the emitted block or trace metadata.
- Downstream assembly reports manual origin lookup, missing block trace, duplicate block identifiers or blocks containing rendering/layout fields.

## expensive_errors
- Untraced visible content reaches a report package: it is expensive because every downstream package, view and rendered document that consumed the block must be audited manually to reconstruct origin. Prevent it by requiring 100 percent `BlockTrace.segment_refs` coverage before any `OutputBlock` is emitted.
- Stale contract output is accepted: it is expensive because block shapes can become incompatible with the active phase boundary and later assembly may need package-level rebuilds. Prevent it by resolving `phase_contract_ref` and `contract_version` before block-type mapping and by rejecting any contract drift.
- Wrong upstream version is bound to a block: it is expensive because later corrections cannot tell whether the visible content came from the intended inference version. Prevent it by checking `VersionRecord.object_ref`, `phase_contract_ref`, `content_hash` and lineage references against the source inference before composition.
- Non-deterministic identifiers enter downstream storage: it is expensive because duplicate or drifting block IDs break rebuild comparison, lineage joins and package diffing. Prevent it by computing identifiers from canonical sorted inputs, stable metadata and `rule_version` only.
- Report-level logic is added inside this motor: it is expensive because responsibilities of motor_015, motor_016 and motor_017 become entangled and later changes require structural refactor. Prevent it by rejecting layout, rendering, section sequencing and audience-view fields at the boundary.
- Partial invalid blocks are emitted for rejected inputs: it is expensive because downstream consumers may treat invalid content as accepted and propagate it into final artifacts. Prevent it by making rejection atomic: invalid inputs create only `CompositionRecord.rejected_refs`, never `OutputBlock` or `BlockTrace` records.
