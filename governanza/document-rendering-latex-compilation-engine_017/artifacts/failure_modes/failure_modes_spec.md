# Failure Modes Spec — Document Rendering / LaTeX Compilation Engine

Motor ID: motor_017

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir Report Package aprobado en documento técnico formal reproducible.
why_it_exists:  El documento final no es accesorio; es parte del output serio del framework.
key_inputs:     report_package (motor_016)
key_outputs:    compiled_pdf, latex_source, render_manifest
key_objects:    RenderJob, LaTeXSource, CompiledDocument
what_not_to_do: No genera contenido. No toma decisiones analíticas. Solo renderiza paquetes aprobados.
design_notes:   Depende únicamente de motor_016. Output es reproducible y versionado.
-->

## failure_modes_list
- UNAPPROVED_PACKAGE_RENDERED: `report_package.approval_status` is missing or differs from `approved`, but rendering starts anyway -> a `compiled_pdf` or success manifest appears authoritative even though motor_016 did not close the package -> reject before source generation with `ERR_REPORT_PACKAGE_NOT_APPROVED`, emit no publishable PDF, and require a new approved package version upstream.
- PACKAGE_CONTENT_MUTATION: template mapping, escaping, section assembly or cleanup logic changes approved text, drops blocks, merges blocks or reorders sections -> `LaTeXSource.package_order_preserved = false`, `content_mutation_check = fail`, source diffs against the package are non-empty, or downstream reviewers see visible content not present in motor_016 output -> fail the render job, retain diagnostics, do not publish, and correct the template or upstream package without mutating the received package.
- RENDER_PROFILE_AMBIGUITY: the package render profile resolves to zero template versions, multiple template versions or an unstated compiler configuration -> two runs of the same package can select different templates or compiler flags -> stop with `ERR_RENDER_PROFILE_AMBIGUOUS` before source emission and require exactly one render profile, template version, template hash and compiler config hash.
- ASSET_INTEGRITY_FAILURE: a figure, appendix, bibliography file or static asset referenced by the package is absent, unreadable or has a hash different from the package declaration -> LaTeX compilation fails, the source bundle cannot rebuild, or the manifest points to an asset that is not the approved asset -> fail preflight or finalization with a structured error, record the missing or mismatched asset in diagnostics, and publish nothing until the package asset set is corrected upstream.
- LATEX_COMPILATION_FAILURE_MASKED: the compiler returns a fatal error or produces no valid PDF, but stale output from a prior run or a partial artifact is marked successful -> `CompiledDocument.published = true` while `compilation_status = failed`, compiler diagnostics contain fatal messages, or `pdf_hash` is empty or inherited from another job -> set `ERR_LATEX_COMPILATION_FAILED`, write diagnostics to the manifest, isolate build directories per `render_job_id`, and block successful publication.
- ARTIFACT_HASH_MISMATCH: source, PDF or asset content changes after hash calculation, or the manifest records a hash from a different artifact path -> `CompiledDocument.source_hash` does not equal `LaTeXSource.source_hash`, `RenderManifest.pdf_hash` does not match the finalized PDF, or a listed artifact path resolves to different bytes -> fail with `ERR_ARTIFACT_HASH_MISMATCH`, quarantine the artifact set, recompute from immutable inputs, and finalize artifacts atomically.
- NON_REPRODUCIBLE_RENDER_OUTPUT: identical `input_package_id`, `input_package_version`, `render_profile_id`, `template_version`, `template_hash` and compiler configuration produce different source hashes or materially different PDF hashes without a recorded deterministic exception -> rebuild comparison fails and the manifest cannot support audit replay -> treat the run as failed, record the nondeterministic source in diagnostics, and pin or remove the volatile template, compiler or environment setting before rerendering.
- MANIFEST_LINEAGE_LOSS: the renderer omits `lineage_refs`, `input_hash`, package version, source hash, PDF hash, template hash, compiler identity or artifact paths from `RenderManifest` -> the PDF cannot be traced or rebuilt even if it is visually correct -> mark the manifest failed, reject publication, and rebuild the manifest from the immutable render job rather than inferring missing upstream lineage.

## anti_patterns
- Editorial renderer: using motor_017 to rewrite approved sections, shorten conclusions, alter claim wording or change executive framing. This breaks the motor boundary because content authority belongs upstream, not to the rendering layer.
- Direct input bypass: accepting output blocks, inference records, source documents or free text directly instead of one approved `report_package` from motor_016. This bypasses report assembly, approval state and package lineage.
- Hidden template selection: choosing templates or render profiles from ambient defaults, filenames, current date, operator preference or local machine state rather than explicit package metadata and recorded configuration.
- Manifest as afterthought: writing PDF and source files first, then best-effort metadata later. This permits unlisted side artifacts, missing hashes and non-rebuildable outputs.
- Mutable shared build directory: compiling multiple render jobs in the same temporary folder or reusing prior PDFs. This allows stale artifacts to leak into a supposedly successful run.
- Visual-success validation: treating "the PDF opens" as sufficient success while ignoring source hash, compiler diagnostics, manifest completeness, lineage preservation and rebuild references.
- Upstream repair inside rendering: fabricating missing lineage, approval status, package versions, section IDs, asset hashes or template metadata in order to get a document out.
- Monolithic reporting-rendering merger: combining motor_016 assembly logic, analytical validation, content editing and LaTeX compilation in one implementation module. This makes motor_017 responsible for decisions it must only render.

## degradation_signals
- `render_jobs_total{approval_status!="approved"}` greater than zero, or any log entry showing source generation for a non-approved package.
- Increase in `ERR_REPORT_PACKAGE_INCOMPLETE`, `ERR_RENDER_PROFILE_AMBIGUOUS`, `ERR_LATEX_COMPILATION_FAILED` or `ERR_ARTIFACT_HASH_MISMATCH` rates for packages that previously rendered successfully.
- Rebuild check drift: repeated runs with the same package version, template hash and compiler config hash produce different `source_hash` values or non-equivalent manifest rebuild references.
- Manifest completeness drift: success manifests missing non-empty `input_hash`, `source_hash`, `pdf_hash`, `template_hash`, `compiler_identity`, `compiler_config_hash`, `lineage_refs` or `artifact_paths`.
- Artifact resolution drift: manifest paths for `latex_source`, `compiled_pdf`, diagnostics or assets fail existence checks, point outside the expected artifact root, or resolve to bytes whose hashes differ from the manifest.
- Compiler diagnostics trend upward for the same template version, especially repeated undefined references, missing assets, overfull boxes that indicate layout instability, or fatal LaTeX messages in successful jobs.
- Content mutation checks become noisy: rising counts of `package_order_preserved = false`, `content_mutation_check = fail`, block-count mismatches or section-order mismatches.
- Build isolation warnings appear, such as reuse of a previous `render_job_id` directory, stale PDF deletion failures, or multiple jobs writing the same output path.
- Manifest-to-object inconsistency appears, such as `CompiledDocument.source_hash` differing from `LaTeXSource.source_hash`, `RenderManifest.document_id` missing on success, or `published = true` with failed compilation status.

## expensive_errors
- Publishing a PDF from an unapproved package is expensive because external readers may treat draft or rejected analysis as authoritative, forcing recalls, audit explanations and upstream package re-approval. Prevent it with a hard pre-render approval check and `ERR_REPORT_PACKAGE_NOT_APPROVED` before any publishable artifact exists.
- Silent content mutation is expensive because the distributed document no longer matches the approved report package, and reconstructing what changed after distribution requires manual comparison across source, PDF and upstream blocks. Prevent it with deterministic escaping, section and block order checks, content mutation checks and refusal to publish when source differs from approved content.
- Missing lineage or hashes in the manifest is expensive because the PDF may be visually usable but cannot be audited, rebuilt or tied back to the exact package version, template and compiler configuration. Prevent it by making manifest finalization atomic and required before publication, with non-empty `lineage_refs`, `input_hash`, `source_hash`, `pdf_hash`, template metadata and compiler metadata.
- Unversioned template or compiler drift is expensive because future rerenders may produce different documents from the same package without a way to explain the difference. Prevent it by recording `template_version`, `template_hash`, `compiler_identity` and `compiler_config_hash`, and by rejecting ambient defaults that are not in the render job.
- Stale PDF publication after a failed compile is expensive because a prior artifact can be mistaken for the current report and may carry outdated content or metadata. Prevent it with isolated per-job build directories, deletion or quarantine of previous outputs before compilation, compiler exit-code checks and `published = false` unless final hash validation passes.
- Asset hash mismatch after publication is expensive because figures, appendices or static files may not correspond to the approved package, invalidating the rebuild record and possibly changing visible evidence presentation. Prevent it with asset preflight, content hashing before source generation, hash verification during finalization and failure on unresolved or changed asset references.
- Inferring missing package metadata inside the renderer is expensive because invented package IDs, lineage or approval values contaminate audit trails and mask upstream defects. Prevent it by treating missing metadata as `ERR_REPORT_PACKAGE_INCOMPLETE` and requiring motor_016 to emit a corrected package version.
