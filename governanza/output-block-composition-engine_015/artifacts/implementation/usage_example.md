# Usage Example — Output Block Composition Engine

Motor ID: motor_015

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Construir bloques visibles trazables para Fase 3 desde decisions e inferencias.
why_it_exists:  Separa contenido visible gobernado del ensamblaje documental final.
key_inputs:     inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    output_block, block_trace, composition_log
key_objects:    OutputBlock, BlockTrace, CompositionRecord
what_not_to_do: No ensambla reportes completos. No renderiza documentos. Solo construye bloques atómicos.
design_notes:   Cada bloque es trazable a su fuente inferencialmente.

Implementation-stage placeholders are fully resolved in this artifact.
-->

## example
The Report Package Assembly Engine calls `motor_015` after `motor_014` has emitted a governed inference about a missing supplier-renewal cadence. The caller supplies the inference record, the active phase contract that authorizes visible Fase 3 blocks, and the version record that binds the inference to immutable lineage. The expected result is one atomic output block, one trace covering its visible segment, and one composition log entry showing that the source inference was accepted.

## inputs_used
```json
{
  "inference_records": [
    {
      "inference_id": "inf-014-0007",
      "case_id": "case-044",
      "phase_id": "fase_2",
      "phase_contract_ref": "pc-f3-output-blocks-v1",
      "contract_version": "1.0.0",
      "inference_category": "gap",
      "visible_statement": "Missing evidence for supplier renewal cadence.",
      "lineage_refs": ["lin-103"],
      "rule_version": "m014-rules-v1",
      "created_at": "2026-04-17T10:00:00Z"
    }
  ],
  "phase_contracts": [
    {
      "contract_ref": "pc-f3-output-blocks-v1",
      "phase_id": "fase_2",
      "contract_version": "1.0.0",
      "allowed_inputs": ["inference_records"],
      "allowed_outputs": ["output_block", "block_trace", "composition_log"],
      "allowed_visible_fields": ["visible_statement"],
      "block_type_map": {
        "gap": "gap_block"
      }
    }
  ],
  "version_records": [
    {
      "version_id": "ver-inf-014-0007-v1",
      "object_ref": "inf-014-0007",
      "object_type": "InferenceRecord",
      "phase_contract_ref": "pc-f3-output-blocks-v1",
      "provenance_refs": ["lin-103"],
      "lineage_refs": ["lin-103"],
      "content_hash": "sha256:inf0140007"
    }
  ]
}
```

## expected_output
```json
{
  "output_blocks": [
    {
      "block_id": "output_block:<stable-hash>",
      "motor_id": "motor_015",
      "phase_id": "fase_2",
      "block_type": "gap_block",
      "visible_payload": {
        "statement": "Missing evidence for supplier renewal cadence."
      },
      "source_inference_ids": ["inf-014-0007"],
      "phase_contract_ref": "pc-f3-output-blocks-v1",
      "contract_version": "1.0.0",
      "version_refs": ["ver-inf-014-0007-v1"],
      "lineage_refs": ["lin-103"],
      "trace_id": "block_trace:<stable-hash>",
      "rule_version": "m015-rules-v1",
      "version_id": "output_block_version:<stable-hash>",
      "version_hash": "sha256:<stable-hash>",
      "source_ref": ["inf-014-0007"],
      "produced_by_motor": "motor_015",
      "parent_id": null
    }
  ],
  "block_traces": [
    {
      "trace_id": "block_trace:<stable-hash>",
      "block_id": "output_block:<stable-hash>",
      "motor_id": "motor_015",
      "segment_refs": [
        {
          "segment_id": "block_segment:<stable-hash>",
          "payload_path": "visible_payload.statement",
          "source_inference_id": "inf-014-0007",
          "version_ref": "ver-inf-014-0007-v1",
          "lineage_ref": "lin-103",
          "phase_contract_ref": "pc-f3-output-blocks-v1"
        }
      ],
      "source_inference_ids": ["inf-014-0007"],
      "version_refs": ["ver-inf-014-0007-v1"],
      "lineage_refs": ["lin-103"],
      "phase_contract_ref": "pc-f3-output-blocks-v1",
      "contract_version": "1.0.0",
      "rule_version": "m015-rules-v1"
    }
  ],
  "composition_log": [
    {
      "composition_id": "composition_record:<stable-hash>",
      "motor_id": "motor_015",
      "input_refs": ["inf-014-0007"],
      "accepted_refs": ["inf-014-0007"],
      "rejected_refs": [],
      "emitted_block_ids": ["output_block:<stable-hash>"],
      "trace_ids": ["block_trace:<stable-hash>"],
      "phase_contract_refs": ["pc-f3-output-blocks-v1"],
      "version_refs": ["ver-inf-014-0007-v1"],
      "rule_version": "m015-rules-v1",
      "status": "PASS",
      "produced_by_motor": "motor_015"
    }
  ]
}
```

## notes
The example assumes the phase contract version referenced by the inference is the same version supplied to the motor, and that the version record resolves the inference lineage. The motor copies only the contract-allowed `visible_statement` into the payload and maps it to `visible_payload.statement`; it does not create report sections, audience-specific wording, layout instructions, or new inferential claims. If the version record or lineage reference is missing, the motor emits a structured rejection in `composition_log` and emits no partial block for that input.
