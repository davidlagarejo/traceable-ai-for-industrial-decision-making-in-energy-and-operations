# Acceptance Tests — Document Rendering / LaTeX Compilation Engine

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

## happy_path
Input: `report_package` with `package_id = "rp-017-demo"`, `version = "1.0.0"`, `approval_status = "approved"`, approved `technical_view`, ordered output block references, lineage references from upstream motors and a declared render profile `latex_technical_v1`.

Action: the motor creates `RenderJob "rj-rp-017-demo-1.0.0"`, renders the approved package into LaTeX source using template version `latex_technical_v1`, compiles the source to PDF and records hashes for the input package, source bundle and PDF.

Expected output: `compiled_pdf` exists and is non-empty, `latex_source` exists and is rebuildable, and `render_manifest` records package id, package version, template version, compiler configuration, artifact paths, hashes, lineage references and `status = "success"`.

## edge_cases
- Large package: a package with hundreds of output blocks and multiple appendices must preserve the exact order declared by `motor_016`, compile through the selected template and emit hashes for every generated source or asset file.
- Minimal approved package: a package with only the required technical view and no optional appendix must still render a valid source bundle, a valid PDF and a manifest that records empty optional sections explicitly as omitted by input, not as render failure.
- Special characters in approved content: reserved LaTeX characters inside already approved text must be escaped deterministically in source while preserving the visible text meaning in the compiled PDF.
- Rebuild case: rendering the same package version with the same template version and compiler configuration must produce the same source hash and PDF hash, except where the compiler embeds unavoidable timestamp metadata that is explicitly recorded in the manifest.

## rejection_criteria
- If `approval_status` is not `approved`, the motor rejects the package with `ERR_REPORT_PACKAGE_NOT_APPROVED` and emits no successful `compiled_pdf`.
- If `package_id`, `version`, approved view content or lineage references are missing, the motor rejects the package with `ERR_REPORT_PACKAGE_INCOMPLETE`.
- If the render profile resolves to more than one template version or no template version, the motor rejects the job with `ERR_RENDER_PROFILE_AMBIGUOUS`.
- If LaTeX compilation fails, the motor returns `ERR_LATEX_COMPILATION_FAILED`, records compiler diagnostics in `render_manifest` and does not publish a successful document artifact.
