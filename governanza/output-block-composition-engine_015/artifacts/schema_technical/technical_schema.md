# Technical Schema — Output Block Composition Engine

Motor ID: motor_015

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Construir bloques visibles trazables para Fase 3 desde decisions e inferencias.
why_it_exists:  Separa contenido visible gobernado del ensamblaje documental final.
key_inputs:     inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    output_block, block_trace, composition_log
key_objects:    OutputBlock, BlockTrace, CompositionRecord
what_not_to_do: No ensambla reportes completos. No renderiza documentos. Solo construye bloques atómicos.
design_notes:   Cada bloque es trazable a su fuente inferencialmente.

Schema content completed for this artifact.
-->

## entities
- `OutputBlock`: primary output entity for one atomic visible Fase 3 content block. It is derived from one or more validated `InferenceRecord` objects and authorized by a matching `PhaseContract`. Stage: emitted by this motor during implementation and stored as a schema-governed output artifact for downstream report assembly.
- `BlockTrace`: trace entity for one emitted `OutputBlock`. It maps every addressable visible payload segment to source inference records, version records, lineage references and the phase contract that authorized the block. Stage: emitted alongside each accepted `OutputBlock`.
- `CompositionRecord`: audit entity for one deterministic composition operation. It records accepted input references, rejected input references with structured reasons, rule version, emitted block identifiers and operation status. Stage: emitted for every composition run, including runs that reject all candidate inputs.

## fields
`OutputBlock`
- `block_id`: `str` (required) - canonical stable identifier for the atomic visible block.
- `motor_id`: `Literal["motor_015"]` (required) - producing motor identifier.
- `phase_id`: `str` (required) - phase identifier copied from the source inference and checked against the phase contract.
- `block_type`: `str` (required) - deterministic block type selected from the inference category and contract-allowed output boundary.
- `visible_payload`: `dict[str, Any]` (required) - governed visible content payload; must contain only contract-allowed fields copied or structured from validated inference input.
- `source_inference_ids`: `list[str]` (required) - source `InferenceRecord.inference_id` values used to create the block.
- `phase_contract_ref`: `str` (required) - reference to the `PhaseContract` that authorizes the block.
- `contract_version`: `str` (required) - version of the phase contract used during composition.
- `version_refs`: `list[str]` (required) - `VersionRecord.version_id` or equivalent object version references that bind the block to immutable upstream versions.
- `lineage_refs`: `list[str]` (required) - upstream lineage references copied from validated inference and version records.
- `trace_id`: `str` (required) - identifier of the matching `BlockTrace`.
- `rule_version`: `str` (required) - deterministic composition rule version applied to this block.
- `version_id`: `str` (required) - version identifier for this emitted block record.
- `created_at`: `datetime` (required) - timestamp at which the block record was first emitted.
- `updated_at`: `datetime` (required) - timestamp of the latest controlled update to this block record; equal to `created_at` for first emission.
- `version_hash`: `str` (required) - stable hash over canonical block payload, source identifiers, contract version and rule version.
- `source_ref`: `list[str]` (required) - primary source references for lineage, normally the same inference identifiers represented in `source_inference_ids`.
- `produced_by_motor`: `Literal["motor_015"]` (required) - explicit lineage producer field.
- `produced_at`: `datetime` (required) - timestamp at which this motor produced the block.
- `parent_id`: `str | null` (required) - prior `block_id` if the block is a controlled successor of an earlier block; otherwise null.

`BlockTrace`
- `trace_id`: `str` (required) - canonical stable identifier for the trace record.
- `block_id`: `str` (required) - foreign-key reference to the emitted `OutputBlock.block_id`.
- `motor_id`: `Literal["motor_015"]` (required) - producing motor identifier.
- `segment_refs`: `list[dict[str, Any]]` (required) - segment-level trace entries; each entry includes `segment_id`, `payload_path`, `source_inference_id`, `version_ref`, `lineage_ref` and `phase_contract_ref`.
- `source_inference_ids`: `list[str]` (required) - complete list of inference identifiers covered by the trace.
- `version_refs`: `list[str]` (required) - complete list of version references required to rebuild or audit the block.
- `lineage_refs`: `list[str]` (required) - complete list of lineage references required to explain source provenance.
- `phase_contract_ref`: `str` (required) - reference to the phase contract applied to the traced block.
- `contract_version`: `str` (required) - phase contract version applied to the traced block.
- `rule_version`: `str` (required) - deterministic trace and block composition rule version.
- `version_id`: `str` (required) - version identifier for this emitted trace record.
- `created_at`: `datetime` (required) - timestamp at which the trace record was first emitted.
- `updated_at`: `datetime` (required) - timestamp of the latest controlled update to this trace record; equal to `created_at` for first emission.
- `version_hash`: `str` (required) - stable hash over canonical trace content, segment references, contract version and rule version.
- `source_ref`: `list[str]` (required) - source references covered by the trace, including the traced `block_id` and source inference identifiers.
- `produced_by_motor`: `Literal["motor_015"]` (required) - explicit lineage producer field.
- `produced_at`: `datetime` (required) - timestamp at which this motor produced the trace.
- `parent_id`: `str | null` (required) - prior `trace_id` if the trace is a controlled successor of an earlier trace; otherwise null.

`CompositionRecord`
- `composition_id`: `str` (required) - canonical stable identifier for the composition operation record.
- `motor_id`: `Literal["motor_015"]` (required) - producing motor identifier.
- `input_refs`: `list[str]` (required) - all input inference references considered in the operation.
- `accepted_refs`: `list[str]` (required) - input references accepted for block composition.
- `rejected_refs`: `list[dict[str, Any]]` (required) - rejected input entries; each entry includes `input_ref`, `rejection_code`, `rejection_reason` and any resolvable contract or version reference.
- `emitted_block_ids`: `list[str]` (required) - identifiers of `OutputBlock` records emitted by the operation.
- `trace_ids`: `list[str]` (required) - identifiers of `BlockTrace` records emitted by the operation.
- `phase_contract_refs`: `list[str]` (required) - phase contract references consulted by the operation.
- `version_refs`: `list[str]` (required) - version record references consulted by the operation.
- `rule_version`: `str` (required) - deterministic rule version applied to the operation.
- `status`: `Literal["PASS", "PARTIAL_REJECTION", "REJECTED"]` (required) - observable operation status.
- `version_id`: `str` (required) - version identifier for this emitted composition record.
- `created_at`: `datetime` (required) - timestamp at which the composition record was first emitted.
- `updated_at`: `datetime` (required) - timestamp of the latest controlled update to this composition record; equal to `created_at` for first emission.
- `version_hash`: `str` (required) - stable hash over canonical operation inputs, accepted references, rejected references, emitted identifiers and rule version.
- `source_ref`: `list[str]` (required) - primary source references considered by the operation, normally the same values represented in `input_refs`.
- `produced_by_motor`: `Literal["motor_015"]` (required) - explicit lineage producer field.
- `produced_at`: `datetime` (required) - timestamp at which this motor produced the composition record.
- `parent_id`: `str | null` (required) - prior `composition_id` if this record supersedes an earlier controlled run; otherwise null.

## relationships
- `OutputBlock.trace_id` references exactly one `BlockTrace.trace_id`.
- `BlockTrace.block_id` references exactly one `OutputBlock.block_id`.
- `CompositionRecord.emitted_block_ids[]` references zero or more `OutputBlock.block_id` values. Zero is allowed only when all candidate inputs are rejected.
- `CompositionRecord.trace_ids[]` references zero or more `BlockTrace.trace_id` values and must cover every emitted block listed in `emitted_block_ids`.
- `OutputBlock.source_inference_ids[]` references upstream `InferenceRecord.inference_id` values produced by `motor_014`.
- `BlockTrace.source_inference_ids[]` references the same upstream inference identifiers used by the traced block and must cover every source represented in `OutputBlock.visible_payload`.
- `OutputBlock.phase_contract_ref`, `BlockTrace.phase_contract_ref` and `CompositionRecord.phase_contract_refs[]` reference supplied `PhaseContract` records from `motor_001`.
- `OutputBlock.version_refs[]`, `BlockTrace.version_refs[]` and `CompositionRecord.version_refs[]` reference supplied `VersionRecord.version_id` values from `motor_002` or version references carried by those records.
- `lineage_refs[]` fields reference upstream lineage identifiers copied from validated inference and version records.
- `parent_id` fields reference a prior record of the same entity type only during controlled correction or rebuild; null represents first emission.

## identifiers
- `OutputBlock.block_id` is the canonical identifier for a block record. It is deterministic for the tuple `motor_id`, `phase_id`, `block_type`, sorted `source_inference_ids`, `phase_contract_ref`, `contract_version`, sorted `version_refs` and `rule_version`.
- `BlockTrace.trace_id` is the canonical identifier for a trace record. It is deterministic for the tuple `motor_id`, `block_id`, canonical `segment_refs`, `contract_version` and `rule_version`.
- `CompositionRecord.composition_id` is the canonical identifier for a composition operation. It is deterministic for the tuple `motor_id`, sorted `input_refs`, sorted `accepted_refs`, canonical `rejected_refs`, sorted `emitted_block_ids`, sorted `trace_ids` and `rule_version`.
- Every emitted entity also carries `motor_id = "motor_015"` and `produced_by_motor = "motor_015"` so storage or audit layers can group records by producer without reinterpreting the canonical entity identifier.

## versioning
- Every `OutputBlock`, `BlockTrace` and `CompositionRecord` includes `version_id`, `created_at`, `updated_at` and `version_hash`.
- `version_id` identifies the emitted version of the entity record and must not overwrite upstream `VersionRecord.version_id` values.
- `created_at` records first emission time for the entity record.
- `updated_at` records the latest controlled update time for the entity record and equals `created_at` on first emission.
- `version_hash` is computed from canonical JSON for the entity payload plus source identifiers, contract version and rule version. The hash is used for reproducibility checks and must change when governed content or critical metadata changes.
- Upstream version metadata is referenced through `version_refs`; this motor does not mutate, normalize or supersede `VersionRecord` objects.

## lineage
- Every `OutputBlock`, `BlockTrace` and `CompositionRecord` includes `source_ref`, `produced_by_motor`, `produced_at` and `parent_id`.
- `source_ref` stores the primary upstream references used to produce the entity. For blocks and traces this includes source inference identifiers; for composition records this includes the considered input references.
- `produced_by_motor` is always `motor_015`.
- `produced_at` records when this motor produced the entity and must be preserved for audit and rebuild.
- `parent_id` links to the prior same-type entity during controlled correction or rebuild; it is null for initial emissions.
- `lineage_refs` and `version_refs` remain copied references to upstream governed records. Missing or unresolvable lineage or version references must produce a structured rejection in `CompositionRecord.rejected_refs` instead of a partial `OutputBlock`.
