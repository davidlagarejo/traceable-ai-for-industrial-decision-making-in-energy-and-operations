# Functional Contract — Report Package Assembly Engine

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

## inputs
output_blocks: list[OutputBlock] — produced by motor_015; each item must include block_id, block_type, content_payload or content_ref, block_trace, provenance_ref, phase_ref, view_tags, status, and source_version_refs.

phase_contracts: list[PhaseContract] — produced by motor_001; defines allowed report package scope, required block categories, permitted view types, ordering rules, and handoff limits for the target phase.

version_records: list[VersionRecord] — produced by motor_002; provides version identifiers, lineage references, dependency records, and rebuild metadata for every block and contract used in the package.

## outputs
report_package: ReportPackage — consumed by motor_017 and downstream governance; contains package_id, package_manifest, ordered block references, view manifests, contract references, version references, and assembly validation status.

technical_view: TechnicalView — included inside report_package and consumed by motor_017; contains the deterministic list of technical block references, view-specific ordering, trace index, and required technical metadata.

executive_view: ExecutiveView — included inside report_package and consumed by motor_017; contains the deterministic list of executive-ready block references, view-specific ordering, trace index, and required executive metadata.

## limits
- The motor never accepts output_blocks with missing block_id, missing trace, unresolved status, unknown phase_ref, or absent version linkage.
- The motor never accepts blocks that are outside the allowed phase_contracts or whose view_tags are not permitted by the target report package contract.
- The motor never accepts duplicate block_id values unless the version_records identify exactly one current version and mark all others as superseded.
- The motor never produces new prose, inferred conclusions, synthetic summaries, rendered documents, delivery bundles, or source evidence.
- The motor never mutates block content; report_package, technical_view, and executive_view contain references and manifests, not rewritten block bodies.
- The motor never treats a package as valid when a required block category from the phase contract is absent.

## validations
- Before processing, validate that output_blocks is non-empty and every block has block_id, block_type, status, phase_ref, view_tags, block_trace, provenance_ref, and source_version_refs.
- Before processing, reject any block whose status is not approved_for_assembly.
- Before processing, validate that each block phase_ref is allowed by at least one supplied phase_contract.
- Before processing, validate that every source_version_ref in each block resolves to a version_records entry.
- Before processing, reject duplicate current block_id entries, conflicting version records, or lineage records with unresolved parent references.
- During assembly, apply only deterministic ordering rules from phase_contracts; ties are resolved by block_type and then block_id.
- Before emitting report_package, verify that all required block categories named by the phase contract are present in the package manifest.
- Before emitting any view, verify that every referenced block exists in report_package.block_refs and that every view entry has a trace back to an input OutputBlock.
- Before emitting output, verify that technical_view and executive_view declare their inclusion rule, excluded block ids, and reason codes for exclusion when a supplied block is not shown in that view.
