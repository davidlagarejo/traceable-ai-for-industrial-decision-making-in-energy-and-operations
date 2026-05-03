# Test Spec — Report Package Assembly Engine

Motor ID: motor_016

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ensamblar Output Blocks en Report Package con vistas como technical_view y executive_view.
why_it_exists:  Un bloque no equivale a un reporte integrado.
key_inputs:     output_blocks (motor_015), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    report_package, technical_view, executive_view
key_objects:    ReportPackage, TechnicalView, ExecutiveView
what_not_to_do: No genera texto nuevo. No renderiza documentos finales. Solo ensambla paquetes desde bloques.
design_notes:   Ensambla sin transformar. Mantiene trazabilidad de bloques.
-->

## happy_path
Input fixture:
- output_blocks contains three records with status = "approved_for_assembly":
  - block_id = "blk_method_001", block_type = "methodology", phase_ref = "phase_3", view_tags = ["technical_view"], provenance_ref = "prov_method_001", block_trace.trace_id = "trace_method_001", source_version_refs = ["ver_blk_method_001"], content_ref = "content://blocks/blk_method_001"
  - block_id = "blk_finding_002", block_type = "finding", phase_ref = "phase_3", view_tags = ["technical_view", "executive_view"], provenance_ref = "prov_finding_002", block_trace.trace_id = "trace_finding_002", source_version_refs = ["ver_blk_finding_002"], content_ref = "content://blocks/blk_finding_002"
  - block_id = "blk_risk_003", block_type = "risk_register", phase_ref = "phase_3", view_tags = ["technical_view", "executive_view"], provenance_ref = "prov_risk_003", block_trace.trace_id = "trace_risk_003", source_version_refs = ["ver_blk_risk_003"], content_ref = "content://blocks/blk_risk_003"
- phase_contracts contains one contract with contract_id = "phase_contract_003", target_phase_ref = "phase_3", permitted_view_types = ["technical_view", "executive_view"], required_block_categories = ["methodology", "finding", "risk_register"], and ordering_rule_ref = "contract_priority_block_type_block_id".
- version_records contains current records for "ver_blk_method_001", "ver_blk_finding_002", "ver_blk_risk_003", and "ver_phase_contract_003"; each record has status = "current" and resolvable lineage parent references.

Expected result:
- The motor emits one ReportPackage with package_type = "report_package", target_phase_ref = "phase_3", validation_status = "valid", validation_errors = [], produced_by_motor = "motor_016", and phase_contract_refs = ["phase_contract_003"].
- ReportPackage.block_refs equals ["blk_method_001", "blk_finding_002", "blk_risk_003"] after applying ordering_rule_ref = "contract_priority_block_type_block_id".
- ReportPackage.block_manifest contains one entry per included block with the original block_id, block_type, phase_ref, provenance_ref, block_trace_ref, source_version_refs, resolved_version_id, view_membership, ordering_key, and assembly_rule_ref.
- ReportPackage.version_record_refs includes the three block version ids and the phase contract version id.
- TechnicalView.view_type = "technical_view", TechnicalView.included_block_refs equals all three package block refs, TechnicalView.excluded_block_refs = [], and TechnicalView.trace_index has one mapping for each included block.
- ExecutiveView.view_type = "executive_view", ExecutiveView.included_block_refs equals ["blk_finding_002", "blk_risk_003"], and ExecutiveView.excluded_block_refs contains {"block_id": "blk_method_001", "reason_code": "view_tag_not_present"}.
- No output field contains newly generated prose or mutated block content; package and view outputs use references, manifests, and trace indexes only.

## sparse_case
Input fixture:
- output_blocks contains one approved block:
  - block_id = "blk_finding_single_001", block_type = "finding", phase_ref = "phase_3", view_tags = ["technical_view"], provenance_ref = "prov_single_001", block_trace.trace_id = "trace_single_001", source_version_refs = ["ver_blk_finding_single_001"], content_ref = "content://blocks/blk_finding_single_001".
- phase_contracts contains contract_id = "phase_contract_sparse_003", target_phase_ref = "phase_3", permitted_view_types = ["technical_view", "executive_view"], required_block_categories = ["finding"], optional_view_types = ["executive_view"], and ordering_rule_ref = "contract_priority_block_type_block_id".
- version_records contains current records for the block and contract.
- Optional fields such as human_readable_title, display_label, executive_section_hint, and non-required renderer hints are absent.

Expected result:
- The motor emits a valid ReportPackage because all required fields and required block categories are present.
- ReportPackage.block_refs equals ["blk_finding_single_001"].
- TechnicalView.included_block_refs equals ["blk_finding_single_001"] and has trace_index coverage for "blk_finding_single_001".
- ExecutiveView is emitted because the contract permits it, but ExecutiveView.included_block_refs = [] and ExecutiveView.excluded_block_refs contains {"block_id": "blk_finding_single_001", "reason_code": "view_tag_not_present"}.
- Missing optional presentation fields are not inferred, synthesized, or backfilled. They are simply absent from optional metadata or represented as null only where the schema requires an explicit nullable field.
- validation_errors remains empty for package and views.

## malformed_input
Malformed fixture A:
- output_blocks is a dict keyed by block_id instead of a list.

Expected rejection A:
- The motor does not emit a valid ReportPackage.
- validation_status = "rejected".
- validation_errors contains error_code = "INVALID_INPUT_TYPE", field = "output_blocks", object_ref = "input.output_blocks".

Malformed fixture B:
- output_blocks is a list, but one block has block_id = "blk_no_trace_001", status = "approved_for_assembly", phase_ref = "phase_3", view_tags = ["technical_view"], provenance_ref = "prov_no_trace_001", source_version_refs = ["ver_blk_no_trace_001"], and no block_trace field.

Expected rejection B:
- The motor does not emit a valid ReportPackage or valid view manifests.
- validation_status = "rejected".
- validation_errors contains error_code = "BLOCK_TRACE_MISSING", field = "block_trace", object_ref = "blk_no_trace_001".

Malformed fixture C:
- output_blocks contains block_id = "blk_unresolved_version_001" with source_version_refs = ["ver_missing_001"].
- version_records does not contain "ver_missing_001".

Expected rejection C:
- The motor does not create a partial package.
- validation_status = "rejected".
- validation_errors contains error_code = "VERSION_RECORD_UNRESOLVED", field = "source_version_refs", object_ref = "blk_unresolved_version_001".

## edge_cases
1. Empty optional executive view:
   - Input: a valid package set where every approved block has view_tags = ["technical_view"], the phase contract permits executive_view, and executive_view is optional.
   - Expected behavior: ReportPackage.validation_status = "valid"; TechnicalView includes all technical blocks; ExecutiveView.included_block_refs = []; ExecutiveView.excluded_block_refs lists every package block with reason_code = "view_tag_not_present"; no executive summary or replacement text is generated.

2. Duplicate block_id with one current version and one superseded version:
   - Input: two records share block_id = "blk_finding_002"; version_records marks "ver_blk_finding_002_v1" as "superseded" and "ver_blk_finding_002_v2" as "current".
   - Expected behavior: the package includes "blk_finding_002" once, resolved_version_id = "ver_blk_finding_002_v2"; assembly_manifest.excluded_superseded_versions records "ver_blk_finding_002_v1"; validation_status = "valid".

3. Duplicate block_id with conflicting current versions:
   - Input: two records share block_id = "blk_finding_conflict_001" and version_records marks both "ver_blk_finding_conflict_a" and "ver_blk_finding_conflict_b" as "current".
   - Expected behavior: the motor rejects the full assembly with error_code = "DUPLICATE_CURRENT_BLOCK", field = "block_id", object_ref = "blk_finding_conflict_001"; no partial package or view output is marked valid.

4. Deterministic ordering tie:
   - Input: two approved finding blocks have the same contract priority and block_type: block_id = "blk_finding_a_001" and block_id = "blk_finding_b_001".
   - Expected behavior: the ordered ReportPackage.block_refs places "blk_finding_a_001" before "blk_finding_b_001"; ordering_rule_ref = "contract_priority_block_type_block_id"; repeated runs with identical inputs produce the same block_refs, assembly_manifest, and version_hash.

5. Phase contract mismatch:
   - Input: output_blocks contains block_id = "blk_wrong_phase_001" with phase_ref = "phase_4", while the supplied phase_contracts authorize only target_phase_ref = "phase_3".
   - Expected behavior: the motor rejects with error_code = "PHASE_CONTRACT_MISMATCH", field = "phase_ref", object_ref = "blk_wrong_phase_001".

## pass_criteria
- A valid scenario passes only when ReportPackage.validation_status, TechnicalView.validation_status, and ExecutiveView.validation_status are all "valid" and their validation_errors lists are empty.
- ReportPackage.block_refs is deterministic, contains only approved current OutputBlock.block_id values, and matches the ordering rule declared in ReportPackage.ordering_rule_ref.
- Every ReportPackage.block_manifest entry preserves the input block_id, phase_ref, provenance_ref, block_trace_ref, source_version_refs, resolved_version_id, and assembly_rule_ref without mutating content_payload or content_ref.
- TechnicalView.included_block_refs and ExecutiveView.included_block_refs are subsets of ReportPackage.block_refs.
- Every included block in each view has a trace_index entry that maps to the parent package_id, the original OutputBlock reference, provenance_ref, block_trace_ref, and resolved_version_id.
- Every package block excluded from a view has an excluded_block_refs entry with a concrete reason_code.
- version_record_refs and phase_contract_refs are populated and resolve to supplied inputs.
- Re-running the same fixture produces identical block_refs, view included_block_refs, assembly_manifest, and version_hash.

## fail_criteria
- The motor marks a package or view as valid when any required input field is missing, any block status is not "approved_for_assembly", any source_version_ref is unresolved, or any phase_ref is outside the supplied phase contracts.
- A package contains a block_id that is absent from the supplied output_blocks or not authorized by phase_contracts.
- A package includes duplicate current versions for the same block_id instead of rejecting with error_code = "DUPLICATE_CURRENT_BLOCK".
- A view includes a block that is not present in ReportPackage.block_refs.
- A view omits trace_index coverage for any included block.
- A block excluded from a view lacks a concrete exclusion reason code.
- The motor rewrites, summarizes, normalizes, or generates block content instead of preserving references and manifests.
- A validation error produces a partially valid ReportPackage, TechnicalView, or ExecutiveView rather than a rejected structured validation output.
- Identical inputs produce different ordering, package_manifest content, view manifests, or version_hash values across runs.
