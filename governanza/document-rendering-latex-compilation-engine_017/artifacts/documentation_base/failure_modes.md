# Failure Modes — Document Rendering / LaTeX Compilation Engine

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
- UNAPPROVED_PACKAGE_RENDERED: a PDF is produced from a package whose approval status is not `approved`, making the document appear authoritative without upstream closure.
- CONTENT_MUTATION_DURING_RENDER: the compiled document differs semantically from the approved package because the render layer edited, omitted or reordered content.
- NON_REPRODUCIBLE_OUTPUT: the PDF cannot be rebuilt from the emitted source, template version and compiler configuration recorded in the manifest.
- LATEX_COMPILATION_FAILURE_MASKED: LaTeX fails but the system publishes a stale, empty or partial PDF as if compilation succeeded.
- LINEAGE_LOSS_IN_MANIFEST: the render manifest omits package version, input hash, source hash, PDF hash or lineage references, breaking auditability.

## anti_patterns
- Using the render engine as an editorial engine that rewrites sections, compresses claims or changes executive wording.
- Passing raw output blocks or inference records directly into the renderer instead of an approved `report_package` from `motor_016`.
- Treating a visually successful PDF as proof that the report package is analytically valid.
- Allowing ad hoc template edits during a run without recording template version and hash.

## degradation_signals
- Increase in render jobs where `source_hash` or `pdf_hash` is absent from the manifest.
- Repeated differences in source hash for identical package version, template version and compiler configuration.
- Compilation warnings that grow across runs for the same template without corresponding package changes.
- Manifests with artifact paths that do not resolve to existing files or storage objects.
- PDF files published without matching `latex_source` bundles.
- Render jobs accepting package statuses other than `approved`.
