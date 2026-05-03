# Functional Contract — Output Block Composition Engine

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

## inputs
- `inference_records`: `list[InferenceRecord]` JSON-compatible records - source: `motor_014`; each record must identify the inferential result to expose, its `inference_id`, `case_id`, `phase_id`, `phase_contract_ref`, `contract_version`, `lineage_refs`, `rule_version`, `created_at`, and visible source fields allowed by the phase contract.
- `phase_contracts`: `list[PhaseContract]` JSON-compatible records - source: `motor_001`; each contract must declare the phase, allowed inputs, allowed outputs, handoff rules, output limits, and contract version relevant to Fase 3 block composition.
- `version_records`: `list[VersionRecord]` JSON-compatible records - source: `motor_002`; each record must provide `version_id`, `object_ref`, `object_type`, `phase_contract_ref`, `provenance_refs`, `content_hash` or equivalent payload fingerprint, and lineage references for the objects used in composition.

## outputs
- `output_block`: `OutputBlock` JSON-compatible record - destination: downstream Fase 3 assembly consumers, especially the Report Package Assembly Engine; represents one atomic visible block and never a full report.
- `block_trace`: `BlockTrace` JSON-compatible record - destination: audit, rebuild, conformance review and downstream consumers that must explain which inference, version and lineage produced each block segment.
- `composition_log`: `list[CompositionRecord]` JSON-compatible audit records - destination: orchestrator logs, conformance review and correction workflows; records accepted inputs, rejected inputs, deterministic rule versions and emitted block identifiers.

## limits
- Never accepts an `InferenceRecord` without `inference_id`, `case_id`, `phase_id`, `phase_contract_ref`, `lineage_refs`, `rule_version` and `created_at`.
- Never accepts an inference whose `phase_contract_ref` cannot be matched to a supplied `PhaseContract`.
- Never accepts a source inference or referenced object whose version cannot be resolved through `version_records`.
- Never accepts narrative notes, report outlines, rendered fragments or manually written claims as substitutes for governed `InferenceRecord` input.
- Never produces report packages, complete documents, rendered files, pagination instructions, visual layouts or final audience-specific views.
- Never produces new inferential conclusions, validation outcomes, source quality decisions or corrected upstream records.
- Never emits an `output_block` without a corresponding `block_trace` and `composition_log` entry.

## validations
- Before processing, every `inference_record.inference_id` must be a non-empty string and unique within the processing batch.
- Before processing, every `inference_record.phase_contract_ref` must resolve to a supplied `PhaseContract` whose `allowed_inputs` include `inference_records` and whose `allowed_outputs` include `output_block`, `block_trace` and `composition_log`.
- Before processing, every required `lineage_refs` entry must be non-empty and traceable to a supplied `VersionRecord` or to a lineage reference carried by a supplied `VersionRecord`.
- Before processing, every inference selected for composition must expose at least one contract-allowed visible source field; empty visible payloads are rejected.
- Before processing, the motor must find a deterministic block-type mapping for the inference category or reject the record with `UNSUPPORTED_BLOCK_MAPPING`.
- Before emitting output, every `OutputBlock` must include `block_id`, `motor_id`, `phase_id`, `block_type`, `visible_payload`, `source_inference_ids`, `phase_contract_ref`, `contract_version`, `version_refs`, `lineage_refs`, `trace_id`, `rule_version` and `created_at`.
- Before emitting output, every `BlockTrace` must reference an emitted `OutputBlock.block_id` and cover every addressable segment of `visible_payload`.
- Before emitting output, every `CompositionRecord` must include `composition_id`, `input_refs`, `accepted_refs`, `rejected_refs`, `rule_version`, `emitted_block_ids`, `status` and `created_at`.
- If any required validation fails, the motor emits a structured rejection in `composition_log` and does not emit a partial block for that invalid input.
