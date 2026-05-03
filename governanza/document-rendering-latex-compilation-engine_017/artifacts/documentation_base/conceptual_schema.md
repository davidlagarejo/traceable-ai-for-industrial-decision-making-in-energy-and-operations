# Conceptual Schema — Document Rendering / LaTeX Compilation Engine

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

## entities
- RenderJob: execution record that binds one approved `report_package` version to one deterministic render profile, template version and compiler configuration.
- LaTeXSource: generated source bundle representing the approved package in LaTeX form without analytical or editorial modification.
- CompiledDocument: compiled PDF artifact produced from a specific `LaTeXSource` and tied to the original package through hashes and lineage.
- RenderManifest: audit object that records inputs, outputs, configuration, hashes, status and reproducibility metadata for the render job.

## relationships
- report_package → RenderJob (one approved package version initiates one render execution unless a new render profile version is requested).
- RenderJob → LaTeXSource (the job produces exactly one source bundle for the selected template version).
- LaTeXSource → CompiledDocument (the compiled document is generated only from the emitted source bundle).
- RenderJob → RenderManifest (the job emits one manifest that records status, configuration and artifact references).
- RenderManifest → LaTeXSource (the manifest stores the source hash and source artifact path).
- RenderManifest → CompiledDocument (the manifest stores the PDF hash, compilation status and document artifact path).
- RenderManifest → report_package (the manifest preserves package id, package version and lineage references from `motor_016`).

## key_fields
RenderJob:
- render_job_id: string
- input_package_id: string
- input_package_version: string
- render_profile_id: string
- template_version: string
- compiler_config: object

LaTeXSource:
- source_id: string
- render_job_id: string
- source_path: string
- source_hash: string
- template_version: string
- asset_refs: list[string]

CompiledDocument:
- document_id: string
- render_job_id: string
- pdf_path: string
- pdf_hash: string
- source_hash: string
- compilation_status: enum(success, failed)

RenderManifest:
- manifest_id: string
- render_job_id: string
- input_package_id: string
- input_package_version: string
- input_hash: string
- source_hash: string
- pdf_hash: string
- artifact_paths: object
- lineage_refs: list[string]
- status: enum(success, failed)
