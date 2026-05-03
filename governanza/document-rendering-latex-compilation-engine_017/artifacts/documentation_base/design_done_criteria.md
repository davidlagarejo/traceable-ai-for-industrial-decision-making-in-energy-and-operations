# Design Done Criteria — Document Rendering / LaTeX Compilation Engine

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

## criteria
- `functional_contract.md` defines `report_package` as the only accepted input and defines `compiled_pdf`, `latex_source` and `render_manifest` as required outputs.
- `functional_contract.md` states that unapproved, partial or non-`motor_016` packages are rejected.
- `conceptual_schema.md` defines `RenderJob`, `LaTeXSource`, `CompiledDocument` and `RenderManifest` with required identifiers, hashes and lineage fields.
- `operational_rules.md` prohibits content generation, analytical decisions and silent mutation of package content.
- `acceptance_tests.md` covers a successful approved package render, large package handling, minimal package handling and explicit rejection conditions.
- `failure_modes.md` identifies non-reproducible output, content mutation, masked compilation failure and lineage loss as observable risks.
- The documentation base contains no open placeholder markers and is ready to drive the technical schema stage without inventing new motor responsibilities.
