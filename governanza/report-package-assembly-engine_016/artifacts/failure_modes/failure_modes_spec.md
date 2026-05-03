# Failure Modes Spec — Report Package Assembly Engine

Motor ID: motor_016

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ensamblar Output Blocks en Report Package con vistas como technical_view y executive_view.
why_it_exists:  Un bloque no equivale a un reporte integrado.
key_inputs:     output_blocks (motor_015), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    report_package, technical_view, executive_view
key_objects:    ReportPackage, TechnicalView, ExecutiveView
what_not_to_do: No genera texto nuevo. No renderiza documentos finales. Solo ensambla paquetes desde bloques.
design_notes:   Ensambla sin transformar. Mantiene trazabilidad de bloques.

Sections completed for the failure_modes gate.
-->

## failure_modes_list
TRACE_INDEX_GAP: an included block enters ReportPackage.block_refs or a view included_block_refs without a resolvable block_trace_ref, provenance_ref, source OutputBlock reference, or resolved_version_id -> package or view validation appears incomplete, audit reconstruction from view entry to original OutputBlock fails, and validation_errors names the missing trace field -> reject the full assembly, emit a structured validation error such as BLOCK_TRACE_MISSING or TRACE_INDEX_INCOMPLETE, and rebuild only after the upstream OutputBlock and version record are supplied with complete trace metadata.

CONTENT_MUTATION: assembly logic rewrites content_payload, changes content_ref, normalizes block text, or creates executive prose while building report_package, technical_view, or executive_view -> content hashes or content references differ from the motor_015 OutputBlock inputs, and the package cannot prove that it assembled without transforming source blocks -> discard the mutated package, preserve the original block references only, and rerun with validation that compares input content_ref or content hash against every package manifest entry.

VIEW_SCOPE_DRIFT: a view includes a block whose view_tags or contract rules do not authorize that view, or omits a required view block without an exclusion reason -> TechnicalView or ExecutiveView no longer matches phase_contracts, downstream rendering receives misleading view membership, and excluded_block_refs is incomplete or generic -> reject the view and package, reapply the phase contract inclusion rules deterministically, and record concrete reason_code values for every package block excluded from each view.

VERSION_COLLISION: two or more records with the same block_id are marked current, or a source_version_ref resolves to conflicting lineage in version_records -> block_manifest cannot identify exactly one resolved_version_id, version_hash is unstable, and rebuild cannot prove which block version was used -> reject the full assembly with DUPLICATE_CURRENT_BLOCK or VERSION_RECORD_CONFLICT, require motor_002 records to mark one current version and supersede the rest, then rebuild from the resolved current version set.

NON_DETERMINISTIC_ORDERING: the assembler falls back to input order, filesystem order, dictionary iteration, runtime timestamps, or an undocumented priority when contract ordering is incomplete -> repeated runs with identical inputs produce different block_refs, view manifests, assembly_manifest, or version_hash values -> prevent valid emission until ordering_rule_ref is present, then apply the phase_contract rule with block_type and block_id tie-breakers and verify repeated runs produce identical manifests.

PARTIAL_PACKAGE_EMISSION: validation detects missing required categories, unresolved phase contracts, unresolved version records, or malformed input but still emits a package or child view with validation_status = "valid" -> downstream motors consume a package that looks valid while critical contract, lineage, or block metadata is absent -> discard all partially valid output, emit only rejected structured validation output, and require pre-creation validation to pass before any ReportPackage, TechnicalView, or ExecutiveView can be marked valid.

PHASE_CONTRACT_MISMATCH: output_blocks contain phase_ref values, block_type categories, permitted view types, or ordering assumptions outside the supplied phase_contracts -> package_manifest contains blocks not authorized for the target phase or fails required_category_check -> reject the full assembly with PHASE_CONTRACT_MISMATCH or REQUIRED_CATEGORY_MISSING, then rerun with matching motor_001 phase contracts or corrected upstream block metadata.

EXCLUSION_REASON_LOSS: a block present in ReportPackage.block_refs is absent from technical_view or executive_view without an excluded_block_refs entry and concrete reason_code -> view membership is not auditable, downstream renderers may treat the absence as accidental, and conformance cannot distinguish valid exclusion from data loss -> reject the affected view and package, regenerate view manifests from package block_refs, and require a reason code such as view_tag_not_present, contract_view_not_permitted, or superseded_version_excluded for every exclusion.

## anti_patterns
- Treating motor_016 as a prose editor, executive summarizer, renderer, PDF builder, or delivery bundle generator instead of a deterministic assembler of references and manifests.
- Letting technical_view or executive_view own separate block content rather than being view manifests over ReportPackage.block_refs.
- Accepting raw inference records, evidence records, or analysis objects directly instead of approved OutputBlocks from motor_015.
- Inferring missing provenance_ref, block_trace, phase_ref, source_version_refs, or version records during assembly.
- Allowing downstream rendering preferences to choose block inclusion, ordering, or view membership when those rules must come from phase_contracts.
- Using input list order, unordered maps, timestamps, random ids, or runtime environment details as ordering or hashing inputs.
- Emitting partial valid packages after validation errors, especially when required block categories or version records are missing.
- Coupling directly to motor_015 or motor_002 internals beyond the declared OutputBlock and VersionRecord handoff fields.
- Recording generic exclusion labels such as "not used" when the contract requires auditable reason codes for view exclusion.
- Updating existing ReportPackage or view records in place rather than creating a new versioned emission when material inputs change.

## degradation_signals
- validation_errors count for BLOCK_TRACE_MISSING, VERSION_RECORD_UNRESOLVED, PHASE_CONTRACT_MISMATCH, REQUIRED_CATEGORY_MISSING, or DUPLICATE_CURRENT_BLOCK increases across consecutive assembly runs.
- Any valid package has a non-empty set of block_refs without matching block_manifest entries, resolved_version_id values, provenance_ref values, or block_trace_ref values.
- Any included_block_refs entry in technical_view or executive_view lacks a trace_index mapping to package_id, block_id, provenance_ref, block_trace_ref, and resolved_version_id.
- Content reference or content hash comparison shows differences between input OutputBlocks and package-referenced block content.
- Repeated runs with identical output_blocks, phase_contracts, and version_records produce different block_refs, view included_block_refs, assembly_manifest, or version_hash values.
- excluded_block_refs uses generic or null reason_code values, or the count of package blocks absent from a view differs from the count of recorded exclusions.
- Packages marked valid contain empty phase_contract_refs, empty version_record_refs, unresolved parent_id lineage, or source_ref entries that do not resolve to supplied inputs.
- Assembly logs show fallback ordering, manual override, inferred metadata, renderer-selected membership, or "best effort package" behavior.
- Duplicate current block_id conflicts appear frequently, indicating version_records are not being resolved before package creation.
- The ratio of rejected packages caused by missing required categories rises, indicating upstream OutputBlock coverage or phase_contract alignment is degrading before total assembly failure.

## expensive_errors
1. Silent content mutation inside a package.
   - Why it is expensive: once downstream motors render or distribute a package, auditors cannot tell whether the text came from motor_015 OutputBlocks or from motor_016 rewriting. Every rendered artifact may need to be invalidated and traced manually.
   - Prevention: treat content_payload and content_ref as immutable, store only references and manifest metadata, and compare package references against the original block content identifiers before marking validation_status = "valid".

2. Missing trace_index coverage for view entries.
   - Why it is expensive: technical_view and executive_view may be consumed independently, so a missing trace mapping breaks reconstruction from a view entry back to ReportPackage, OutputBlock, provenance, and version lineage.
   - Prevention: require trace_index entries for every included_block_refs value and fail the view when any mapping lacks package_id, block_trace_ref, provenance_ref, resolved_version_id, or source OutputBlock reference.

3. Accepting duplicate current versions for one block_id.
   - Why it is expensive: packages created from ambiguous current versions cannot be rebuilt deterministically, and later version cleanup cannot prove which block version informed rendered reports.
   - Prevention: resolve source_version_refs before assembly, reject duplicate current records with DUPLICATE_CURRENT_BLOCK, and allow superseded duplicates only when version_records identify exactly one current version.

4. Marking a partial package as valid after a required category is missing.
   - Why it is expensive: downstream motors may render an incomplete report as if it satisfied the phase contract, forcing late discovery during review, delivery, or audit.
   - Prevention: run required_category_check before package emission, block ReportPackage validity until every contract-required category is present, and emit rejected structured validation output instead of partial valid objects.

5. Non-deterministic ordering or hashing.
   - Why it is expensive: two packages with the same inputs can produce different manifests or version_hash values, making rebuild, comparison, and lineage review unreliable.
   - Prevention: use only phase_contract ordering_rule_ref plus stable block_type and block_id tie-breakers, canonicalize manifest inputs before hashing, and regression-test identical input runs for identical outputs.

6. View exclusion without reason codes.
   - Why it is expensive: downstream consumers cannot distinguish intentional contract-based exclusion from accidental omission, and later conformance review must inspect every block manually.
   - Prevention: derive exclusions by comparing each view against ReportPackage.block_refs and require concrete reason_code values for every excluded package block before a view can be valid.

7. Inferring missing contract or version metadata during assembly.
   - Why it is expensive: fabricated or assumed metadata contaminates package lineage and may force correction across packages, views, rendered documents, and version registries.
   - Prevention: reject missing phase_contract_refs, unresolved source_version_refs, and unresolved parent lineage; require upstream correction from motor_001, motor_002, or motor_015 instead of local repair in motor_016.
