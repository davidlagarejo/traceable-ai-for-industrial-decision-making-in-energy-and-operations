# Test Spec — Document Rendering / LaTeX Compilation Engine

Motor ID: motor_017

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir Report Package aprobado en documento técnico formal reproducible.
why_it_exists:  El documento final no es accesorio; es parte del output serio del framework.
key_inputs:     report_package (motor_016)
key_outputs:    compiled_pdf, latex_source, render_manifest
key_objects:    RenderJob, LaTeXSource, CompiledDocument
what_not_to_do: No genera contenido. No toma decisiones analíticas. Solo renderiza paquetes aprobados.
design_notes:   Depende únicamente de motor_016. Output es reproducible y versionado.

All required sections below are complete and must remain free of placeholder markers.
-->

## happy_path
Input:
- `report_package.package_id = "rp-017-demo"`
- `report_package.version = "1.0.0"`
- `report_package.approval_status = "approved"`
- `report_package.lineage_refs = ["motor_016:report_package:rp-017-demo:1.0.0", "motor_015:section_set:ss-017-demo"]`
- `report_package.render_profile_id = "latex_technical_v1"`
- `report_package.template_version = "latex_technical_v1.0.0"`
- `report_package.approved_views.technical_view.sections = [{"section_id": "s1", "title": "Executive Summary", "blocks": [{"block_id": "b1", "content": "Approved summary text."}]}, {"section_id": "s2", "title": "Findings", "blocks": [{"block_id": "b2", "content": "Approved finding text."}]}]`
- `report_package.assets = [{"asset_ref": "figures/figure-001.pdf", "hash": "sha256:asset001"}]`

Expected behavior:
- The motor creates one `RenderJob` with `input_package_id = "rp-017-demo"`, `input_package_version = "1.0.0"`, `approval_status = "approved"`, `render_profile_id = "latex_technical_v1"`, `template_version = "latex_technical_v1.0.0"`, `produced_by_motor = "motor_017"` and `error_code = "none"`.
- The motor emits one `LaTeXSource` whose `render_job_id` matches the job, whose `asset_refs` contain `figures/figure-001.pdf`, whose `package_order_preserved = true`, and whose `content_mutation_check = "pass"`.
- The motor compiles one `CompiledDocument` with `compilation_status = "success"`, `published = true`, a non-empty `pdf_path`, a non-empty `pdf_hash`, and `source_hash` equal to the emitted `LaTeXSource.source_hash`.
- The motor emits one `RenderManifest` with `status = "success"`, `input_package_id = "rp-017-demo"`, `input_package_version = "1.0.0"`, preserved `lineage_refs`, `artifact_paths.latex_source`, `artifact_paths.compiled_pdf`, `input_hash`, `source_hash`, `pdf_hash`, `compiler_identity`, `compiler_config_hash`, `template_hash`, and `rebuild_references`.

## sparse_case
Input:
- Same required fields as the happy path.
- `report_package.approved_views.technical_view.sections = [{"section_id": "s1", "title": "Summary", "blocks": [{"block_id": "b1", "content": "Minimal approved report text."}]}]`
- Optional appendices are absent.
- Optional static assets are absent.
- Optional compiler warning inputs are absent.

Expected behavior:
- The motor accepts the package because required identity, approval, lineage, render profile, template version and approved view content are present.
- `LaTeXSource.asset_refs = []` and `LaTeXSource.asset_hashes = {}`.
- `RenderManifest.artifact_paths` includes `latex_source` and `compiled_pdf`; asset-related entries are either absent or explicitly empty.
- `RenderManifest.compiler_diagnostics = []` for a clean build.
- `RenderManifest.status = "success"` and no failure code is emitted.
- The missing optional appendices or assets are not treated as render failure and are not backfilled with generated content.

## malformed_input
Rejection cases:
- If `report_package` is not an object, reject before creating source artifacts with `ERR_REPORT_PACKAGE_INCOMPLETE`.
- If `report_package.package_id` is missing, empty or not a string, reject with `ERR_REPORT_PACKAGE_INCOMPLETE`.
- If `report_package.version` is missing, empty or not a string, reject with `ERR_REPORT_PACKAGE_INCOMPLETE`.
- If `report_package.approval_status = "draft"`, `"partial"`, `"rejected"` or any value other than `"approved"`, reject with `ERR_REPORT_PACKAGE_NOT_APPROVED`.
- If `report_package.lineage_refs` is missing, empty or not a list of strings, reject with `ERR_REPORT_PACKAGE_INCOMPLETE`.
- If approved view content is missing or has no ordered sections and blocks, reject with `ERR_REPORT_PACKAGE_INCOMPLETE`.
- If the render profile resolves to zero template versions or more than one template version, reject with `ERR_RENDER_PROFILE_AMBIGUOUS`.
- If LaTeX compilation fails after valid source generation, emit `ERR_LATEX_COMPILATION_FAILED`, retain compiler diagnostics in the manifest and do not publish a successful `compiled_pdf`.

Expected behavior:
- Rejected inputs do not mutate the incoming package.
- Rejected inputs do not publish a PDF with `status = "success"`.
- Any manifest emitted for a failed accepted render attempt uses `status = "failed"` and records the structured `error_code`.

## edge_cases
- Large approved package: given an approved package with 500 ordered output blocks, 20 sections and 10 appendix references, the emitted LaTeX source preserves the exact section and block order from `motor_016`, records all generated file references, and records hashes for every required asset.
- Reserved LaTeX characters: given approved text containing characters such as `%`, `_`, `&`, `#`, `{` and `}`, the source escapes them deterministically while `content_mutation_check = "pass"` confirms that visible approved content was not analytically rewritten.
- Rebuild determinism: rendering the same `package_id`, `version`, `render_profile_id`, `template_version`, `template_hash` and compiler configuration twice produces the same `source_hash` and equivalent manifest rebuild references, with only run identifiers and execution timestamps allowed to differ.
- Artifact integrity mismatch: if the compiled PDF hash does not match the value recorded during artifact finalization, the job fails with `ERR_ARTIFACT_HASH_MISMATCH`, `CompiledDocument.published = false`, and the manifest does not claim a successful document.
- Missing provenance at the boundary: if the package contains visible report content but omits upstream `lineage_refs`, the motor rejects the input with `ERR_REPORT_PACKAGE_INCOMPLETE` rather than inferring lineage or fabricating references.

## pass_criteria
A test passes only when all applicable observable conditions are true:
- Accepted jobs start from exactly one `report_package` produced by `motor_016` with `approval_status = "approved"`.
- The output set contains `compiled_pdf`, `latex_source` and `render_manifest` for successful renders.
- `RenderJob.produced_by_motor`, `LaTeXSource.produced_by_motor`, `CompiledDocument.produced_by_motor` and `RenderManifest.produced_by_motor` all equal `motor_017`.
- `input_package_id`, `input_package_version`, `render_job_id`, `source_hash`, template metadata and compiler configuration references are consistent across all emitted objects.
- `RenderManifest.lineage_refs` exactly preserves the upstream lineage references from the input package.
- `CompiledDocument.source_hash` equals `LaTeXSource.source_hash`.
- `RenderManifest.status = "success"` only when the source bundle exists, the PDF exists, both hashes are non-empty, and the PDF is rebuildable from recorded source, template and compiler references.
- Failure cases return the expected structured error code and never publish a successful PDF.

## fail_criteria
A test fails if any of these observable conditions appear:
- A package with `approval_status` other than `approved` is rendered or published.
- The motor accepts raw output blocks, free text, inference records or any input that is not a `report_package` from `motor_016`.
- The emitted source reorders, drops, merges or rewrites approved sections or blocks.
- A successful manifest omits `input_hash`, `source_hash`, `pdf_hash`, `artifact_paths`, `compiler_identity`, `compiler_config_hash`, `template_version`, `template_hash` or `lineage_refs`.
- `CompiledDocument.published = true` while compilation failed, diagnostics indicate a fatal compiler error, or the PDF hash is missing.
- The manifest references an artifact path that does not exist or references an artifact not listed in `artifact_paths`.
- The motor fabricates missing lineage, approval, template or package version metadata instead of rejecting the input.
- The same deterministic input and compiler configuration produce different source hashes without an explicitly recorded non-deterministic compiler metadata reason.
