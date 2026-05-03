# Operational Rules — Report Package Assembly Engine

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

## rules
1. The motor must assemble only from OutputBlocks whose status is approved_for_assembly and whose block_trace is present.
2. Every included block must resolve to a phase_contract and at least one current version_record before it can enter a ReportPackage.
3. Block content is immutable during assembly; the motor may copy references and metadata but must not rewrite content_payload or content_ref.
4. Ordering must be deterministic and derived from phase_contract ordering rules; if the contract does not define a tie-breaker, the motor uses block_type and then block_id.
5. The report_package must include a package_manifest listing every included block_id, version id, trace id, view membership, and assembly rule reference.
6. The technical_view and executive_view must be generated as view manifests over package block references, not as separate content objects.
7. Any block excluded from a view but present in the package must have an exclusion reason code recorded in that view manifest.
8. The motor must reject the entire assembly when required block categories from the phase contract are absent.
9. The motor must emit structured errors instead of partial packages when validation fails before package creation.

## invariants
- Each output block that enters a package remains addressable by the same block_id after assembly.
- Each package and view preserves traceability from view entry to ReportPackage entry to original OutputBlock.
- Each package references the phase contracts and version records used to assemble it.
- No operation removes provenance_ref, block_trace, source_version_refs, or phase_ref from any referenced block.
- The set of included_block_refs in each view is a subset of ReportPackage.block_refs.
- Re-running assembly with the same inputs, contract versions, and ordering rules produces the same package_manifest and view manifests.

## forbidden_operations
- Generating new text, summaries, claims, recommendations, labels, or explanatory prose.
- Rendering final documents such as PDF, LaTeX, HTML, slide decks, images, or delivery bundles.
- Creating, editing, splitting, merging, or rewriting OutputBlocks.
- Inferring missing metadata, silently repairing broken lineage, or fabricating version records.
- Accepting orphan blocks that cannot be traced to motor_015 output and motor_002 version records.
- Changing phase contracts or overriding contract-defined required categories.
- Performing field validation, evidence validation, inference scoring, source rights checks, or quality evaluation that belongs to other motors.
