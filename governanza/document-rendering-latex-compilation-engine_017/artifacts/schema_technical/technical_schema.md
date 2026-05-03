# Technical Schema — Document Rendering / LaTeX Compilation Engine

Motor ID: motor_017

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir Report Package aprobado en documento técnico formal reproducible.
why_it_exists:  El documento final no es accesorio; es parte del output serio del framework.
key_inputs:     report_package (motor_016)
key_outputs:    compiled_pdf, latex_source, render_manifest
key_objects:    RenderJob, LaTeXSource, CompiledDocument
what_not_to_do: No genera contenido. No toma decisiones analíticas. Solo renderiza paquetes aprobados.
design_notes:   Depende únicamente de motor_016. Output es reproducible y versionado.

This schema derives from the approved documentation base for motor_017.
-->

## entities
- RenderJob: execution record for one deterministic rendering attempt. It binds one approved `report_package` version from `motor_016` to one render profile, one LaTeX template version and one compiler configuration. Lives in the `schema_technical`, `tests`, `implementation` and `conformance_review` stages as the primary runtime object to validate.
- LaTeXSource: source bundle emitted by a `RenderJob`. It contains the generated `.tex` entrypoint plus declared static asset references, hashes and template metadata required to rebuild the PDF without changing approved report content. Lives in the `schema_technical`, `implementation` and `conformance_review` stages as a produced artifact object.
- CompiledDocument: PDF artifact produced by compiling a specific `LaTeXSource`. It records document path, document hash, compiler result and the source hash used for compilation. Lives in the `schema_technical`, `implementation` and `conformance_review` stages as a produced artifact object.
- RenderManifest: audit and rebuild record for the render job. It records input package identity, lineage references, render configuration, artifact paths, hashes, compiler diagnostics and final status. Lives in the `schema_technical`, `tests`, `implementation` and `conformance_review` stages as the canonical metadata output.

## fields
RenderJob:
- render_job_id: string (required) — stable identifier for this rendering execution.
- input_package_id: string (required) — package identifier received from `report_package.package_id`.
- input_package_version: string (required) — immutable package version received from `report_package.version`.
- input_package_hash: string (required) — deterministic hash of the approved input package payload used for rendering.
- approval_status: enum(approved) (required) — approval state copied from the input package; only `approved` is accepted.
- render_profile_id: string (required) — deterministic render profile selected or declared for the package.
- template_version: string (required) — LaTeX template version used to generate source.
- template_hash: string (required) — content hash of the resolved template bundle.
- compiler_config: object (required) — compiler executable, command flags, environment-relevant settings and deterministic build options.
- compiler_identity: string (required) — compiler family and version used for compilation.
- status: enum(created, source_generated, success, failed) (required) — current render job state.
- error_code: enum(ERR_REPORT_PACKAGE_NOT_APPROVED, ERR_REPORT_PACKAGE_INCOMPLETE, ERR_RENDER_PROFILE_AMBIGUOUS, ERR_LATEX_COMPILATION_FAILED, ERR_ARTIFACT_HASH_MISMATCH, none) (required) — structured failure reason or `none` for non-failed states.
- diagnostics_ref: string (optional) — path or storage reference for compiler diagnostics when a failure or warning must be retained.
- version_id: string (required) — version identifier for this job record.
- created_at: datetime (required) — timestamp when the job record was created.
- updated_at: datetime (required) — timestamp when the job record was last changed.
- version_hash: string (required) — hash of the serialized job record excluding volatile timestamps.
- source_ref: string (required) — canonical reference to the approved input package from `motor_016`.
- produced_by_motor: string (required) — fixed value `motor_017`.
- produced_at: datetime (required) — timestamp when the job was produced.
- parent_id: string (required) — upstream package version reference, normally `{input_package_id}:{input_package_version}`.

LaTeXSource:
- source_id: string (required) — stable identifier for the generated source bundle.
- render_job_id: string (required) — foreign key to `RenderJob.render_job_id`.
- input_package_id: string (required) — copied package identifier for audit joins.
- input_package_version: string (required) — copied package version for audit joins.
- source_path: string (required) — filesystem path or storage reference to the `.tex` entrypoint or source bundle root.
- source_hash: string (required) — deterministic hash of the generated source bundle.
- template_version: string (required) — template version used to generate this source.
- template_hash: string (required) — hash of the template bundle used to generate this source.
- asset_refs: list[string] (required) — declared assets required by the source bundle; empty list if no assets are needed.
- asset_hashes: object (required) — map of asset reference to content hash.
- generated_file_refs: list[string] (required) — generated `.tex` and support file references included in the source bundle.
- package_order_preserved: boolean (required) — validation flag confirming section and output block order match the approved package.
- content_mutation_check: enum(pass, fail) (required) — validation result confirming the source did not add, remove or reorder approved content.
- version_id: string (required) — version identifier for this source record.
- created_at: datetime (required) — timestamp when the source record was created.
- updated_at: datetime (required) — timestamp when the source record was last changed.
- version_hash: string (required) — hash of the serialized source record excluding volatile timestamps.
- source_ref: string (required) — canonical reference to the approved input package and render job.
- produced_by_motor: string (required) — fixed value `motor_017`.
- produced_at: datetime (required) — timestamp when the source bundle was emitted.
- parent_id: string (required) — `RenderJob.render_job_id`.

CompiledDocument:
- document_id: string (required) — stable identifier for the compiled PDF artifact.
- render_job_id: string (required) — foreign key to `RenderJob.render_job_id`.
- source_id: string (required) — foreign key to `LaTeXSource.source_id`.
- input_package_id: string (required) — copied package identifier for audit joins.
- input_package_version: string (required) — copied package version for audit joins.
- pdf_path: string (required) — filesystem path or storage reference to the compiled PDF.
- pdf_hash: string (required) — deterministic hash of the compiled PDF artifact when compilation succeeds.
- source_hash: string (required) — source bundle hash used for compilation; must equal `LaTeXSource.source_hash`.
- compiler_identity: string (required) — compiler family and version used to produce the PDF.
- compiler_config_hash: string (required) — hash of the compiler configuration recorded on the render job.
- compilation_status: enum(success, failed) (required) — compiler result for this document.
- diagnostics_ref: string (optional) — path or storage reference to retained compiler diagnostics.
- published: boolean (required) — true only when compilation succeeds and hash checks pass.
- version_id: string (required) — version identifier for this document record.
- created_at: datetime (required) — timestamp when the document record was created.
- updated_at: datetime (required) — timestamp when the document record was last changed.
- version_hash: string (required) — hash of the serialized document record excluding volatile timestamps.
- source_ref: string (required) — canonical reference to the `LaTeXSource` used for compilation.
- produced_by_motor: string (required) — fixed value `motor_017`.
- produced_at: datetime (required) — timestamp when the document artifact was produced or the failed compilation was recorded.
- parent_id: string (required) — `LaTeXSource.source_id`.

RenderManifest:
- manifest_id: string (required) — stable identifier for the manifest.
- render_job_id: string (required) — foreign key to `RenderJob.render_job_id`.
- source_id: string (required) — foreign key to `LaTeXSource.source_id` when source generation completed.
- document_id: string (optional) — foreign key to `CompiledDocument.document_id` when a document record exists.
- input_package_id: string (required) — approved package identifier copied from `motor_016`.
- input_package_version: string (required) — approved package version copied from `motor_016`.
- lineage_refs: list[string] (required) — upstream lineage references preserved from the package without rewriting.
- render_profile_id: string (required) — render profile used for this job.
- template_version: string (required) — LaTeX template version used for this job.
- template_hash: string (required) — hash of the resolved template bundle.
- compiler_identity: string (required) — compiler family and version used by the job.
- compiler_config_hash: string (required) — deterministic hash of compiler configuration.
- input_hash: string (required) — hash of the approved package payload.
- source_hash: string (required) — hash of the emitted source bundle.
- pdf_hash: string (optional) — hash of the compiled PDF; absent when compilation failed before producing a valid PDF.
- artifact_paths: object (required) — object containing `latex_source`, `compiled_pdf`, `diagnostics` and supporting asset references as applicable.
- status: enum(success, failed) (required) — final manifest status for the render job.
- error_code: enum(ERR_REPORT_PACKAGE_NOT_APPROVED, ERR_REPORT_PACKAGE_INCOMPLETE, ERR_RENDER_PROFILE_AMBIGUOUS, ERR_LATEX_COMPILATION_FAILED, ERR_ARTIFACT_HASH_MISMATCH, none) (required) — structured failure reason or `none` for success.
- compiler_diagnostics: list[string] (required) — normalized compiler warnings or errors; empty list for clean successful builds.
- rebuild_references: object (required) — package, source, template and compiler references needed to reproduce the output.
- version_id: string (required) — version identifier for this manifest record.
- created_at: datetime (required) — timestamp when the manifest record was created.
- updated_at: datetime (required) — timestamp when the manifest record was last changed.
- version_hash: string (required) — hash of the serialized manifest excluding volatile timestamps.
- source_ref: string (required) — canonical reference to the approved input package and render job.
- produced_by_motor: string (required) — fixed value `motor_017`.
- produced_at: datetime (required) — timestamp when the manifest was emitted.
- parent_id: string (required) — `RenderJob.render_job_id`.

## relationships
- `report_package.package_id` and `report_package.version` from `motor_016` reference `RenderJob.input_package_id` and `RenderJob.input_package_version`; this is an external immutable source reference, not an owned entity.
- `RenderJob.render_job_id` → `LaTeXSource.render_job_id` is a one-to-one required relationship. A completed source bundle must belong to exactly one render job.
- `RenderJob.render_job_id` → `CompiledDocument.render_job_id` is a one-to-zero-or-one relationship. A document record may be absent if the job is rejected before source generation, and exists with `compilation_status = failed` when compilation diagnostics must be retained.
- `LaTeXSource.source_id` → `CompiledDocument.source_id` is a one-to-zero-or-one relationship. A successful PDF must be compiled from exactly one source bundle.
- `LaTeXSource.source_hash` → `CompiledDocument.source_hash` is a required integrity reference. The values must match for a compiled document to be publishable.
- `RenderJob.render_job_id` → `RenderManifest.render_job_id` is a one-to-one required relationship. Every accepted render attempt emits exactly one manifest.
- `LaTeXSource.source_id` → `RenderManifest.source_id` is a required reference after source generation and remains the source audit link for failed compilation.
- `CompiledDocument.document_id` → `RenderManifest.document_id` is optional for failed jobs and required for successful jobs.
- `RenderManifest.lineage_refs` preserves upstream lineage references from `report_package.lineage_refs`; the renderer may copy and record these values but must not rewrite them.
- `RenderManifest.artifact_paths` references all emitted files. No source, PDF, diagnostic log or asset generated by this motor is valid unless it is listed in the manifest.

## identifiers
- RenderJob canonical ID: `render_job_id`. Recommended deterministic form is `motor_017:render_job:{input_package_id}:{input_package_version}:{render_profile_id}:{template_version}:{compiler_config_hash}:{run_sequence}`.
- LaTeXSource canonical ID: `source_id`. Recommended deterministic form is `motor_017:latex_source:{render_job_id}:{source_hash}`.
- CompiledDocument canonical ID: `document_id`. Recommended deterministic form is `motor_017:compiled_document:{render_job_id}:{pdf_hash}` for successful builds and `motor_017:compiled_document:{render_job_id}:failed` for retained failed compilation records.
- RenderManifest canonical ID: `manifest_id`. Recommended deterministic form is `motor_017:render_manifest:{render_job_id}:{version_hash}`.
- External input reference: `input_package_id` plus `input_package_version` identify the upstream `report_package`; motor_017 does not mint or mutate package identifiers.
- Record-level fallback: `record_id` may be used by storage adapters as an internal persistence key, but it must never replace the canonical IDs above in manifests or lineage.

## versioning
- Every entity record includes `version_id: string (required)`, `created_at: datetime (required)`, `updated_at: datetime (required)` and `version_hash: string (required)`.
- `version_id` identifies the schema record version for `RenderJob`, `LaTeXSource`, `CompiledDocument` or `RenderManifest`; it is distinct from `input_package_version` and must not overwrite upstream package versioning.
- `created_at` records initial creation of the local motor_017 entity record. It is allowed to differ from `produced_at` when a record is opened before an artifact is emitted.
- `updated_at` records the last local metadata update. Updates are allowed only for state transitions and diagnostics inside the same render attempt, never for silent correction of package content.
- `version_hash` is computed from canonical serialized entity fields and excludes volatile execution timestamp fields when deterministic rebuild comparison requires it.
- Version continuity rule: `input_package_version`, `template_version`, `template_hash` and `compiler_config_hash` must remain consistent across `RenderJob`, `LaTeXSource`, `CompiledDocument` and `RenderManifest` for the same `render_job_id`.
- Rebuild rule: rerendering the same `input_package_id`, `input_package_version`, `render_profile_id`, `template_version`, `template_hash` and compiler configuration should produce equivalent `source_hash` and `pdf_hash`, except for compiler metadata explicitly recorded in the manifest.

## lineage
- Every entity record includes `source_ref: string (required)`, `produced_by_motor: string (required)`, `produced_at: datetime (required)` and `parent_id: string (required)`.
- `source_ref` for `RenderJob` points to the approved `report_package` from `motor_016`, using `input_package_id` and `input_package_version`.
- `source_ref` for `LaTeXSource` points to both the approved package reference and `RenderJob.render_job_id`, establishing that the source bundle is a deterministic projection of the approved package.
- `source_ref` for `CompiledDocument` points to `LaTeXSource.source_id` and `LaTeXSource.source_hash`, establishing that the PDF came from the emitted source.
- `source_ref` for `RenderManifest` points to the approved package reference and the render job it audits.
- `produced_by_motor` is always `motor_017`; upstream lineage remains in `RenderManifest.lineage_refs` and is not rewritten as if motor_017 produced upstream analytical objects.
- `produced_at` records the timestamp when each local entity or artifact was emitted or finalized by motor_017.
- `parent_id` for `RenderJob` is `{input_package_id}:{input_package_version}`.
- `parent_id` for `LaTeXSource` is `RenderJob.render_job_id`.
- `parent_id` for `CompiledDocument` is `LaTeXSource.source_id`.
- `parent_id` for `RenderManifest` is `RenderJob.render_job_id`.
- Lineage preservation rule: missing package lineage references are a blocking input error, not data to infer or repair inside the renderer.
