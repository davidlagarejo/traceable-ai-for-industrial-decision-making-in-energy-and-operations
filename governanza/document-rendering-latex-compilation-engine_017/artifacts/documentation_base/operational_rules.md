# Operational Rules — Document Rendering / LaTeX Compilation Engine

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

## rules
1. A render operation may start only from one approved `report_package` version produced by `motor_016`.
2. The input package must be treated as immutable; the motor reads it, renders it and records metadata without changing the package object.
3. The section order, block order and view selection must match the approved package exactly.
4. Every render must use a declared template version, render profile and compiler configuration recorded in the manifest.
5. Every successful output must include `compiled_pdf`, `latex_source` and `render_manifest`; partial success cannot be published as complete output.
6. Every emitted artifact must have a stable identifier, filesystem path or storage reference, and content hash.
7. A failed compilation must produce a structured failure status and diagnostics in `render_manifest`, not a silent empty or stale PDF.
8. Re-running the same package version with the same template and compiler configuration must produce equivalent source and equivalent manifest metadata except for execution timestamp and run identifier.

## invariants
- `input_package_id` is never null after a render job is created.
- `input_package_version` remains identical across `RenderJob`, `LaTeXSource`, `CompiledDocument` and `RenderManifest`.
- `lineage_refs` from the package are preserved in the manifest without deletion or rewriting.
- `latex_source` always points back to exactly one `render_job_id`.
- `compiled_pdf` always points back to the `source_hash` used for compilation.
- A manifest with `status = success` always references non-empty source and PDF artifacts.
- A manifest with `status = failed` never claims a valid `compiled_pdf` output.

## forbidden_operations
- Generating new analytical content, summaries, claims, recommendations or conclusions.
- Taking analytical decisions or changing evidence strength, confidence, priority or epistemic status.
- Rendering packages that are not explicitly approved by `motor_016`.
- Editing, reordering, merging or dropping output blocks from the package.
- Correcting missing lineage, missing approvals or malformed package fields silently.
- Calling upstream motors to rebuild content during rendering.
- Publishing a PDF that cannot be rebuilt from the emitted `latex_source` and recorded configuration.
- Treating visual polish as permission to alter the meaning, scope or traceability of the report.
