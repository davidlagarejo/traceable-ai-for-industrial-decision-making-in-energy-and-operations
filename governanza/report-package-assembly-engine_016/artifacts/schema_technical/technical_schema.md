# Technical Schema — Report Package Assembly Engine

Motor ID: motor_016

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ensamblar Output Blocks en Report Package con vistas como technical_view y executive_view.
why_it_exists:  Un bloque no equivale a un reporte integrado.
key_inputs:     output_blocks (motor_015), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    report_package, technical_view, executive_view
key_objects:    ReportPackage, TechnicalView, ExecutiveView
what_not_to_do: No genera texto nuevo. No renderiza documentos finales. Solo ensambla paquetes desde bloques.
design_notes:   Ensambla sin transformar. Mantiene trazabilidad de bloques.

Sections completed for the schema_technical gate.
-->

## entities
### ReportPackage
- description: Primary package entity assembled by motor_016. It binds approved OutputBlock references, phase contract references, version records, deterministic ordering metadata, and view manifests into one reproducible report package.
- lives_in_stage: defined in schema_technical; produced in implementation; consumed by motor_017 after validation.

### TechnicalView
- description: View manifest inside a ReportPackage for technical consumers. It selects package block references tagged or required for technical_view and exposes trace-heavy metadata without rewriting block content.
- lives_in_stage: defined in schema_technical; produced in implementation as a child object of ReportPackage; consumed by motor_017.

### ExecutiveView
- description: View manifest inside a ReportPackage for executive-ready blocks. It selects package block references already tagged for executive_view and preserves their existing content without generating summaries or new prose.
- lives_in_stage: defined in schema_technical; produced in implementation as a child object of ReportPackage; consumed by motor_017.

## fields
### ReportPackage
- record_id: string (required) -- Stable persisted record identifier for this package record.
- motor_016_id: string (required) -- Assembly run identifier that ties the package and its view records to one execution of motor_016.
- package_id: string (required) -- Stable domain identifier for the assembled report package.
- package_type: enum[report_package] (required) -- Fixed object type emitted by this motor.
- target_phase_ref: string (required) -- Phase identifier authorized by the phase contract for this package.
- phase_contract_refs: list[string] (required) -- References to motor_001 phase contracts used to authorize scope, ordering, required categories, and views.
- block_refs: list[string] (required) -- Ordered list of included motor_015 OutputBlock.block_id values.
- block_manifest: list[dict] (required) -- Per-block manifest entries containing block_id, block_type, phase_ref, provenance_ref, block_trace_ref, source_version_refs, resolved_version_id, view_membership, ordering_key, and assembly_rule_ref.
- view_refs: list[string] (required) -- List containing the child view identifiers included in the package.
- technical_view_ref: string (required) -- Reference to the TechnicalView.view_id generated for this package.
- executive_view_ref: string (required) -- Reference to the ExecutiveView.view_id generated for this package; the referenced view may contain zero included blocks when permitted by contract.
- version_record_refs: list[string] (required) -- motor_002 version record ids used to resolve included blocks and contracts.
- assembly_manifest: dict (required) -- Deterministic manifest containing ordering_rule_ref, required_category_check, duplicate_resolution, excluded_superseded_versions, package_hash_inputs, and view_membership_summary.
- ordering_rule_ref: string (required) -- Identifier for the ordering rule applied from phase_contracts, with block_type and block_id tie-breakers when required.
- validation_status: enum[valid, rejected] (required) -- Package validation state; only valid packages are handed to motor_017, while rejected state is limited to structured validation output.
- validation_errors: list[dict] (required) -- Empty for valid packages; otherwise structured entries with error_code, field, object_ref, and message.
- version_id: string (required) -- Version identifier for this package record.
- created_at: datetime (required) -- ISO-8601 timestamp when this package version was produced.
- updated_at: datetime (required) -- ISO-8601 timestamp for the latest material version of this package record; equals created_at for immutable first emission.
- version_hash: string (required) -- Hash of the canonical package manifest and resolved source version references.
- source_ref: list[string] (required) -- Input references used to assemble this package: block ids, phase contract ids, and version record ids.
- produced_by_motor: enum[motor_016] (required) -- Fixed producing motor identifier.
- produced_at: datetime (required) -- ISO-8601 timestamp of package production.
- parent_id: string|null (required) -- Prior package_id when this package is a rebuild; null for first emission.

### TechnicalView
- record_id: string (required) -- Stable persisted record identifier for this technical view record.
- motor_016_id: string (required) -- Assembly run identifier shared with the parent ReportPackage.
- view_id: string (required) -- Stable domain identifier for this view.
- package_id: string (required) -- Parent ReportPackage.package_id.
- view_type: enum[technical_view] (required) -- Fixed view type.
- inclusion_rule_ref: string (required) -- Contract rule or rule set that determines technical_view membership.
- included_block_refs: list[string] (required) -- Ordered subset of ReportPackage.block_refs included in the technical view.
- excluded_block_refs: list[dict] (required) -- Package blocks excluded from this view, each with block_id and reason_code.
- ordering_rule_ref: string (required) -- Ordering rule applied to included_block_refs.
- trace_index: dict (required) -- Mapping from each included block_id to block_trace_ref, provenance_ref, resolved_version_id, package_id, and source OutputBlock reference.
- view_manifest: dict (required) -- Deterministic manifest containing view_type, inclusion rule, ordering key, included count, excluded count, and contract refs.
- validation_status: enum[valid, rejected] (required) -- View validation state; valid means every included block exists in the parent package and has trace_index coverage.
- validation_errors: list[dict] (required) -- Empty for valid views; otherwise structured entries with error_code, field, object_ref, and message.
- version_id: string (required) -- Version identifier for this view record.
- created_at: datetime (required) -- ISO-8601 timestamp when this view version was produced.
- updated_at: datetime (required) -- ISO-8601 timestamp for the latest material version of this view record; equals created_at for immutable first emission.
- version_hash: string (required) -- Hash of the canonical view manifest and included resolved source versions.
- source_ref: list[string] (required) -- Input block, phase contract, and version references used by this view.
- produced_by_motor: enum[motor_016] (required) -- Fixed producing motor identifier.
- produced_at: datetime (required) -- ISO-8601 timestamp of view production.
- parent_id: string|null (required) -- Parent ReportPackage.package_id for normal emission, or prior TechnicalView.view_id when describing a rebuild lineage edge.

### ExecutiveView
- record_id: string (required) -- Stable persisted record identifier for this executive view record.
- motor_016_id: string (required) -- Assembly run identifier shared with the parent ReportPackage.
- view_id: string (required) -- Stable domain identifier for this view.
- package_id: string (required) -- Parent ReportPackage.package_id.
- view_type: enum[executive_view] (required) -- Fixed view type.
- inclusion_rule_ref: string (required) -- Contract rule or rule set that determines executive_view membership.
- included_block_refs: list[string] (required) -- Ordered subset of ReportPackage.block_refs included in the executive view; may be empty only when the phase contract marks the view as optional.
- excluded_block_refs: list[dict] (required) -- Package blocks excluded from this view, each with block_id and reason_code.
- ordering_rule_ref: string (required) -- Ordering rule applied to included_block_refs.
- trace_index: dict (required) -- Mapping from each included block_id to block_trace_ref, provenance_ref, resolved_version_id, package_id, and source OutputBlock reference.
- view_manifest: dict (required) -- Deterministic manifest containing view_type, inclusion rule, ordering key, included count, excluded count, and contract refs.
- validation_status: enum[valid, rejected] (required) -- View validation state; valid means every included block exists in the parent package and has trace_index coverage.
- validation_errors: list[dict] (required) -- Empty for valid views; otherwise structured entries with error_code, field, object_ref, and message.
- version_id: string (required) -- Version identifier for this view record.
- created_at: datetime (required) -- ISO-8601 timestamp when this view version was produced.
- updated_at: datetime (required) -- ISO-8601 timestamp for the latest material version of this view record; equals created_at for immutable first emission.
- version_hash: string (required) -- Hash of the canonical view manifest and included resolved source versions.
- source_ref: list[string] (required) -- Input block, phase contract, and version references used by this view.
- produced_by_motor: enum[motor_016] (required) -- Fixed producing motor identifier.
- produced_at: datetime (required) -- ISO-8601 timestamp of view production.
- parent_id: string|null (required) -- Parent ReportPackage.package_id for normal emission, or prior ExecutiveView.view_id when describing a rebuild lineage edge.

## relationships
- ReportPackage.technical_view_ref -> TechnicalView.view_id: one-to-one required child reference; the referenced TechnicalView.package_id must equal ReportPackage.package_id.
- ReportPackage.executive_view_ref -> ExecutiveView.view_id: one-to-one required child reference; the referenced ExecutiveView.package_id must equal ReportPackage.package_id.
- TechnicalView.package_id -> ReportPackage.package_id: many-to-one in storage, with exactly one current technical view per package version.
- ExecutiveView.package_id -> ReportPackage.package_id: many-to-one in storage, with exactly one current executive view per package version.
- ReportPackage.block_refs -> motor_015.OutputBlock.block_id: external reference list; motor_016 does not own or mutate OutputBlock content.
- ReportPackage.phase_contract_refs -> motor_001.PhaseContract.contract_id: external reference list used for package scope, required categories, ordering, and permitted views.
- ReportPackage.version_record_refs -> motor_002.VersionRecord.version_id: external reference list used for rebuild, current-versus-superseded resolution, and audit.
- TechnicalView.included_block_refs -> ReportPackage.block_refs: subset constraint; every included block must exist in the parent package.
- ExecutiveView.included_block_refs -> ReportPackage.block_refs: subset constraint; every included block must exist in the parent package.
- TechnicalView.trace_index and ExecutiveView.trace_index -> ReportPackage.block_manifest: each view entry must map to exactly one package manifest entry and preserve block_trace_ref, provenance_ref, and resolved_version_id.
- parent_id references are lineage references only; they do not authorize mutation of parent package or view records.

## identifiers
- ReportPackage canonical identifier: package_id. The persisted record identifier is record_id, and motor_016_id identifies the assembly run that produced it.
- TechnicalView canonical identifier: view_id. It must be stable for the package version and unique within the scope of package_id plus view_type.
- ExecutiveView canonical identifier: view_id. It must be stable for the package version and unique within the scope of package_id plus view_type.
- Shared assembly identifier: motor_016_id. The same value appears on ReportPackage, TechnicalView, and ExecutiveView emitted by one assembly run.
- External identifiers are reference-only: block_id from motor_015, contract_id or phase_contract_ref from motor_001, and version_id from motor_002.
- Deterministic identifier recommendation: package_id is derived from target_phase_ref, sorted current block ids, phase_contract_refs, and resolved version ids; view_id is derived from package_id and view_type.

## versioning
- version_id: required on ReportPackage, TechnicalView, and ExecutiveView. It identifies the material version of the emitted object and must resolve to or be registerable by motor_002.
- created_at: required ISO-8601 timestamp on every entity. It records when the current object version was first emitted.
- updated_at: required ISO-8601 timestamp on every entity. Because motor_016 does not silently mutate outputs, a material change creates a new version; updated_at equals created_at for first emission.
- version_hash: required hash on every entity. It is computed from canonical JSON for stable fields, manifest fields, ordered references, source version refs, and lineage refs, excluding version_hash itself and non-deterministic runtime logging.
- Rebuild rule: with identical output_blocks, phase_contracts, version_records, and ordering rules, the same canonical manifest and version_hash must be produced.
- Supersession rule: when version_records mark duplicate block ids as superseded, only the current block version enters block_refs; superseded references can appear only in assembly_manifest.excluded_superseded_versions.

## lineage
- source_ref: required on ReportPackage, TechnicalView, and ExecutiveView. For ReportPackage it contains all input block ids, phase contract refs, and version record refs used by the package. For each view it contains the included block refs plus the parent package_id and contract refs that determined membership.
- produced_by_motor: required on every entity and fixed to motor_016. No downstream renderer or upstream block composer may be recorded as the producer of these package or view objects.
- produced_at: required ISO-8601 timestamp on every entity. It records when motor_016 emitted the package or view object.
- parent_id: required but nullable on every entity. For initial package creation it is null on ReportPackage and package_id on child views. For rebuilds or corrected emissions it points to the immediately prior package_id or view_id that the new object supersedes.
- Lineage preservation rule: every view entry must be reconstructible from view_id -> package_id -> block_manifest entry -> motor_015 OutputBlock.block_id -> block_trace_ref, provenance_ref, and motor_002 version_id.
- Non-mutation rule: lineage records may explain selection, ordering, exclusion, and supersession, but may not imply that motor_016 edited OutputBlock content or phase contract content.
