# Failure Modes — Report Package Assembly Engine

Motor ID: motor_016

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ensamblar Output Blocks en Report Package con vistas como technical_view y executive_view.
why_it_exists:  Un bloque no equivale a un reporte integrado.
key_inputs:     output_blocks (motor_015), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    report_package, technical_view, executive_view
key_objects:    ReportPackage, TechnicalView, ExecutiveView
what_not_to_do: No genera texto nuevo. No renderiza documentos finales. Solo ensambla paquetes desde bloques.
design_notes:   Ensambla sin transformar. Mantiene trazabilidad de bloques.

Sections completed for the documentation_base gate.
-->

## failure_modes_list
TRACE_LOSS: the package or a view contains block references that cannot be traced back to an original OutputBlock, block_trace, provenance_ref, and version record.

CONTENT_MUTATION: the assembled package contains block content that differs from motor_015 output, indicating that the assembly layer rewrote or normalized content instead of referencing it.

VIEW_DRIFT: technical_view or executive_view contains blocks not allowed by the phase contract, omits required blocks, or applies a non-contractual ordering rule.

PARTIAL_PACKAGE_EMISSION: the motor emits a report_package after validation errors, creating a package that appears usable while required categories, lineage, or version records are missing.

VERSION_COLLISION: two current records for the same block_id enter the same package, making rebuild and audit ambiguous.

## anti_patterns
- Using this motor as a late-stage editor that rewrites blocks to make a report read better.
- Treating executive_view as a summarizer instead of a deterministic view over already approved executive-ready blocks.
- Passing raw inference records or uncomposed analysis objects directly into the package assembler instead of OutputBlocks from motor_015.
- Allowing the renderer to choose package contents because the assembly manifest was incomplete.

## degradation_signals
- Rising count of view entries without trace_index mappings to original block_trace values.
- Non-zero count of content hash differences between input OutputBlocks and package-referenced block payloads.
- Frequent use of generic exclusion reason codes instead of contract-specific reason codes.
- Packages with valid status but missing phase_contract_refs or version_record_refs.
- Repeated differences in package_manifest order across identical input runs.
- Growth in manual overrides needed to decide whether a block belongs in technical_view or executive_view.
