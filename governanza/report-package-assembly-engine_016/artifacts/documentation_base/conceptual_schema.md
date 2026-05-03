# Conceptual Schema — Report Package Assembly Engine

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

## entities
ReportPackage: integrated container that binds approved OutputBlock references, phase contract references, version records, assembly rules, and view manifests into one reproducible report package.

TechnicalView: deterministic view manifest inside a ReportPackage that selects technical block references and exposes trace-heavy metadata for audit, implementation review, and technical rendering.

ExecutiveView: deterministic view manifest inside a ReportPackage that selects blocks already tagged as executive-ready and exposes concise package structure without creating new executive prose.

## relationships
ReportPackage -> TechnicalView (one package contains exactly one technical view when the phase contract permits technical_view).

ReportPackage -> ExecutiveView (one package contains exactly one executive view when the phase contract permits executive_view).

ReportPackage -> OutputBlock references (one package contains one or more approved block references from motor_015).

TechnicalView -> OutputBlock references (the view includes a subset of package block references whose view_tags include technical_view or whose block_type is required by the technical contract).

ExecutiveView -> OutputBlock references (the view includes a subset of package block references whose view_tags include executive_view and whose status is approved_for_assembly).

ReportPackage -> PhaseContract references (the package records the contract ids that authorized its scope, ordering, required categories, and view rules).

ReportPackage -> VersionRecord references (the package records version ids for every included block and contract so the package can be rebuilt).

## key_fields
ReportPackage:
- package_id: string
- package_type: string
- phase_contract_refs: list[string]
- block_refs: list[string]
- view_refs: list[string]
- version_record_refs: list[string]
- assembly_manifest: dict
- validation_status: enum[valid, rejected]

TechnicalView:
- view_id: string
- package_id: string
- view_type: enum[technical_view]
- included_block_refs: list[string]
- excluded_block_refs: list[dict]
- ordering_rule_ref: string
- trace_index: dict

ExecutiveView:
- view_id: string
- package_id: string
- view_type: enum[executive_view]
- included_block_refs: list[string]
- excluded_block_refs: list[dict]
- ordering_rule_ref: string
- trace_index: dict
