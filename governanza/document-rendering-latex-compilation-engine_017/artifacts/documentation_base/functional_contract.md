# Functional Contract — Document Rendering / LaTeX Compilation Engine

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

## inputs
- report_package: structured object — source `motor_016`; approved report package containing package id, version, approved views, ordered output blocks, lineage references and render-ready metadata.

## outputs
- compiled_pdf: binary document — destination report archive, downstream distribution workflow or conformance review; compiled PDF generated from the approved package.
- latex_source: source bundle — destination artifact store and rebuild workflow; deterministic `.tex` source plus any declared static assets required for recompilation.
- render_manifest: JSON object — destination lineage, audit and rebuild consumers; records input references, render configuration, hashes, compiler result and produced artifact identifiers.

## limits
- The motor accepts only a `report_package` produced by `motor_016`; raw `output_blocks`, inference records, source documents or free text are rejected.
- The motor accepts only packages with explicit approval status and stable package version; draft, partial or unapproved packages are rejected.
- The motor never generates analytical content, editorial interpretation, claim wording, evidence ranking or executive conclusions.
- The motor never mutates the received `report_package`; corrections must happen upstream and produce a new package version.
- The motor never emits undocumented side artifacts; every emitted file must be referenced from `render_manifest`.
- The motor never treats a successful PDF compilation as analytical validation of the report content.

## validations
- Before processing, `report_package.package_id`, `report_package.version`, `report_package.approval_status`, `report_package.lineage_refs` and approved view content must be present and non-empty.
- Before processing, `report_package.approval_status` must equal `approved`; any other value returns `ERR_REPORT_PACKAGE_NOT_APPROVED`.
- Before rendering, the package must declare or resolve to exactly one deterministic render profile and one LaTeX template version; ambiguity returns `ERR_RENDER_PROFILE_AMBIGUOUS`.
- Before compiling, every referenced asset required by the LaTeX source must be present, readable and covered by an input hash.
- The generated `latex_source` must preserve the package order of sections and output blocks exactly as provided by `motor_016`.
- The generated `compiled_pdf` must be produced from the emitted `latex_source`; a PDF without a matching source hash is invalid.
- The `render_manifest` must include `render_job_id`, `input_package_id`, `input_package_version`, `template_version`, compiler identity, input hash, source hash, pdf hash, artifact paths, timestamp and status.
- If compilation fails, the motor emits a structured failure record in the manifest and does not publish a successful `compiled_pdf`.
