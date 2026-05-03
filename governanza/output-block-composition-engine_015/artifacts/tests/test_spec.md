# Test Spec — Output Block Composition Engine

Motor ID: motor_015

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Construir bloques visibles trazables para Fase 3 desde decisions e inferencias.
why_it_exists:  Separa contenido visible gobernado del ensamblaje documental final.
key_inputs:     inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    output_block, block_trace, composition_log
key_objects:    OutputBlock, BlockTrace, CompositionRecord
what_not_to_do: No ensambla reportes completos. No renderiza documentos. Solo construye bloques atómicos.
design_notes:   Cada bloque es trazable a su fuente inferencialmente.

Test-spec content completed for this artifact.
-->

## happy_path
Input:
- `inference_records`: one record with `inference_id = "inf-014-0007"`, `case_id = "case-044"`, `phase_id = "fase_2"`, `phase_contract_ref = "pc-f3-output-blocks-v1"`, `contract_version = "1.0.0"`, `inference_category = "gap"`, `visible_statement = "Missing evidence for supplier renewal cadence."`, `lineage_refs = ["lin-103"]`, `rule_version = "m014-rules-v1"` and `created_at = "2026-04-17T10:00:00Z"`.
- `phase_contracts`: one contract with `contract_ref = "pc-f3-output-blocks-v1"`, `phase_id = "fase_2"`, `contract_version = "1.0.0"`, `allowed_inputs = ["inference_records"]`, `allowed_outputs = ["output_block", "block_trace", "composition_log"]`, `allowed_visible_fields = ["visible_statement"]` and `block_type_map = {"gap": "gap_block"}`.
- `version_records`: one record with `version_id = "ver-inf-014-0007-v1"`, `object_ref = "inf-014-0007"`, `object_type = "InferenceRecord"`, `phase_contract_ref = "pc-f3-output-blocks-v1"`, `provenance_refs = ["lin-103"]`, `lineage_refs = ["lin-103"]` and `content_hash = "sha256:inf0140007"`.

Expected output:
- One `OutputBlock` is emitted with `motor_id = "motor_015"`, `produced_by_motor = "motor_015"`, `phase_id = "fase_2"`, `block_type = "gap_block"`, `visible_payload.statement = "Missing evidence for supplier renewal cadence."`, `source_inference_ids = ["inf-014-0007"]`, `phase_contract_ref = "pc-f3-output-blocks-v1"`, `contract_version = "1.0.0"`, `version_refs = ["ver-inf-014-0007-v1"]`, `lineage_refs = ["lin-103"]`, a non-empty `block_id`, a non-empty `trace_id`, a non-empty `version_id`, a non-empty `version_hash`, and `parent_id = null`.
- One `BlockTrace` is emitted with `block_id` equal to the `OutputBlock.block_id`, `source_inference_ids = ["inf-014-0007"]`, `version_refs = ["ver-inf-014-0007-v1"]`, `lineage_refs = ["lin-103"]`, `phase_contract_ref = "pc-f3-output-blocks-v1"`, `contract_version = "1.0.0"`, and one `segment_refs` entry for `payload_path = "visible_payload.statement"` tied to `inf-014-0007`, `ver-inf-014-0007-v1` and `lin-103`.
- One `CompositionRecord` is emitted with `input_refs = ["inf-014-0007"]`, `accepted_refs = ["inf-014-0007"]`, `rejected_refs = []`, `emitted_block_ids` containing the emitted `block_id`, `trace_ids` containing the emitted `trace_id`, `phase_contract_refs = ["pc-f3-output-blocks-v1"]`, `version_refs = ["ver-inf-014-0007-v1"]`, and `status = "PASS"`.

## sparse_case
Input:
- `inference_records`: one record with all required metadata from the happy path but only one contract-allowed visible field: `visible_statement = "Renewal cadence cannot be confirmed from current records."`. Optional explanatory fields such as `analyst_note`, `confidence_comment`, `recommended_section`, `audience_hint` and `display_order` are absent.
- `phase_contracts`: the same contract shape as the happy path, with `allowed_visible_fields = ["visible_statement", "visible_rationale"]`.
- `version_records`: one resolvable `VersionRecord` for the inference with `version_id = "ver-inf-014-0011-v1"` and `lineage_refs = ["lin-211"]`.

Expected behavior:
- The motor accepts the input because all required identifiers, contract references, version references, lineage references and one allowed visible field are present.
- The emitted `OutputBlock.visible_payload` contains the supplied statement only and does not synthesize missing rationale, commentary, section labels or audience-specific narrative.
- The `BlockTrace.segment_refs` covers the single statement segment.
- The `CompositionRecord.status` is `"PASS"`, with `accepted_refs = ["inf-014-0011"]` and `rejected_refs = []`.

## malformed_input
Input:
- `inference_records`: one malformed record with `inference_id = ""`, `case_id = "case-081"`, `phase_id = "fase_2"`, `phase_contract_ref = "pc-f3-output-blocks-v1"`, `contract_version = "1.0.0"`, `inference_category = "gap"`, `visible_statement = "Supplier record is missing renewal date."`, `lineage_refs = "lin-301"` as a string instead of a list, and `created_at = "2026-04-17T11:00:00Z"`.
- `phase_contracts`: one otherwise valid contract matching `pc-f3-output-blocks-v1`.
- `version_records`: one otherwise valid version record for `object_ref = "inf-014-malformed"`.

Expected behavior:
- The motor rejects the malformed inference before composition because `inference_id` is empty and `lineage_refs` has the wrong type.
- No `OutputBlock` is emitted for the malformed record.
- No `BlockTrace` is emitted for the malformed record.
- One `CompositionRecord` is emitted with `input_refs` containing a stable representation of the malformed input reference, `accepted_refs = []`, `emitted_block_ids = []`, `trace_ids = []`, `status = "REJECTED"`, and `rejected_refs` containing an entry with `rejection_code = "MALFORMED_INFERENCE_RECORD"` and a `rejection_reason` that names the invalid fields `inference_id` and `lineage_refs`.

## edge_cases
1. Mixed valid and invalid batch:
   - Input contains `inf-014-0020`, a valid tension inference with resolvable version and lineage references, and `inf-014-0021`, an inference whose `phase_contract_ref = "pc-unknown"` cannot be resolved.
   - Expected behavior: the motor emits one atomic `OutputBlock` and one `BlockTrace` for `inf-014-0020`; it emits no block for `inf-014-0021`; the `CompositionRecord.status` is `"PARTIAL_REJECTION"`; `accepted_refs = ["inf-014-0020"]`; `rejected_refs` includes `{"input_ref": "inf-014-0021", "rejection_code": "MISSING_TRACEABILITY"}` or a stricter contract-resolution rejection used by the implementation; output ordering remains deterministic by source identifier.

2. Unsupported inference category:
   - Input contains a record with valid required metadata and visible payload but `inference_category = "freeform_summary"` while the phase contract's `block_type_map` only defines `gap`, `tension`, `conflict` and `opportunity`.
   - Expected behavior: the record is rejected with `rejection_code = "UNSUPPORTED_BLOCK_MAPPING"`; no partial `OutputBlock` is emitted; the `CompositionRecord.status` is `"REJECTED"` and names the unsupported category in the rejection reason.

3. Deterministic rebuild:
   - Input contains the same valid records as a prior run but supplied in reverse list order, with identical `contract_version`, `version_records` and motor `rule_version`.
   - Expected behavior: the emitted `block_id`, `trace_id`, `composition_id`, accepted and rejected classifications, and ordered `emitted_block_ids` are identical to the prior run.

4. Empty visible payload:
   - Input contains a valid inference identifier, phase contract reference, version reference and lineage reference, but all contract-allowed visible fields are missing or empty strings.
   - Expected behavior: the record is rejected with `rejection_code = "EMPTY_VISIBLE_PAYLOAD"`; no block or trace is emitted for that input; the rejection is recorded in `CompositionRecord.rejected_refs`.

## pass_criteria
A test passes only when all applicable observable conditions are true:
- Every accepted input produces exactly one atomic `OutputBlock` and exactly one matching `BlockTrace`.
- Every emitted `OutputBlock` has non-empty `block_id`, `trace_id`, `phase_contract_ref`, `source_inference_ids`, `version_refs`, `lineage_refs`, `rule_version`, `version_id`, `version_hash`, `source_ref`, `produced_by_motor = "motor_015"` and `produced_at`.
- Every `BlockTrace.block_id` resolves to an emitted `OutputBlock.block_id`, and every `OutputBlock.trace_id` resolves to an emitted `BlockTrace.trace_id`.
- Every addressable field in `OutputBlock.visible_payload` has a corresponding `BlockTrace.segment_refs` entry with `payload_path`, `source_inference_id`, `version_ref`, `lineage_ref` and `phase_contract_ref`.
- Every invalid input appears in `CompositionRecord.rejected_refs` with a deterministic `input_ref`, `rejection_code` and `rejection_reason`, and no invalid input produces an `OutputBlock`.
- Re-running the same input set with the same contract version and rule version yields the same block identifiers, trace identifiers, composition identifiers, accepted references, rejected references and output ordering.

## fail_criteria
A test fails when any of these observable conditions occurs:
- An accepted input emits an `OutputBlock` without a matching `BlockTrace` or without a `CompositionRecord` entry.
- An invalid input emits any partial `OutputBlock` or `BlockTrace`.
- A visible payload segment lacks source inference, version, lineage or phase contract coverage in `BlockTrace.segment_refs`.
- The motor accepts an inference whose phase contract is missing, whose version reference cannot be resolved, whose lineage references are empty, whose visible payload is empty, or whose category lacks a deterministic block-type mapping.
- The motor alters upstream identifiers, rewrites inference content as a new claim, adds report-level structure, emits a report package, or creates rendering instructions.
- Identical valid inputs under the same contract version and rule version produce different identifiers, different output ordering or different accepted and rejected classifications across runs.
