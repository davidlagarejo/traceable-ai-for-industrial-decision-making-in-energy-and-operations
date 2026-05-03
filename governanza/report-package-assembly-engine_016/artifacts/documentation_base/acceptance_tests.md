# Acceptance Tests — Report Package Assembly Engine

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

## happy_path
Input: three approved OutputBlocks from motor_015:
- block_id = "blk_method_001", block_type = "methodology", view_tags = ["technical_view"], phase_ref = "phase_3", source_version_refs = ["ver_blk_method_001"]
- block_id = "blk_finding_002", block_type = "finding", view_tags = ["technical_view", "executive_view"], phase_ref = "phase_3", source_version_refs = ["ver_blk_finding_002"]
- block_id = "blk_risk_003", block_type = "risk_register", view_tags = ["technical_view", "executive_view"], phase_ref = "phase_3", source_version_refs = ["ver_blk_risk_003"]

Action: the motor validates the three blocks against phase_contracts from motor_001, resolves each source_version_ref against version_records from motor_002, applies the phase contract ordering rule, and assembles one ReportPackage.

Expected output: report_package.validation_status is valid; report_package.block_refs contains the three block ids in deterministic order; technical_view.included_block_refs contains all three block ids; executive_view.included_block_refs contains "blk_finding_002" and "blk_risk_003"; every view entry maps back to the original block_trace and version record.

## edge_cases
- Empty optional view: if the phase contract permits executive_view but no block is tagged executive_view and executive_view is optional, the motor emits an empty ExecutiveView with included_block_refs = [] and excluded_block_refs listing every package block with reason_code = "view_tag_not_present".
- Single-block package: if the phase contract requires only one finding block and exactly one approved block is supplied, the motor emits a valid ReportPackage with one block_ref and one-entry technical_view when all lineage and version records resolve.
- Tie in ordering: if two blocks have the same contract priority and block_type, the motor orders them by block_id ascending and records ordering_rule_ref = "contract_priority_block_type_block_id".
- Superseded duplicate: if two records share block_id but version_records mark one as superseded and one as current, the motor includes only the current version and records the excluded superseded version in the package assembly_manifest.

## rejection_criteria
- Reject with error_code = "BLOCK_TRACE_MISSING" when any supplied OutputBlock lacks block_trace or provenance_ref.
- Reject with error_code = "VERSION_RECORD_UNRESOLVED" when any source_version_ref cannot be found in version_records.
- Reject with error_code = "PHASE_CONTRACT_MISMATCH" when a block phase_ref is not allowed by the supplied phase_contracts.
- Reject with error_code = "REQUIRED_BLOCK_CATEGORY_MISSING" when the phase contract requires a block_type that is absent from the approved block set.
- Reject with error_code = "DUPLICATE_CURRENT_BLOCK" when two current blocks share the same block_id and version_records do not mark exactly one current version.
