# Master Concept Document — Document Rendering / LaTeX Compilation Engine

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

## purpose
Este motor convierte un `report_package` aprobado por `motor_016` en un documento tecnico formal, reproducible y versionado. Toma el contenido ya ensamblado, lo proyecta sobre una fuente LaTeX determinista, compila el PDF resultante y registra el manifiesto exacto del render. Su responsabilidad termina en producir artefactos documentales reconstruibles; no altera el contenido analitico ni decide que debe aparecer en el reporte.

## what_it_does
- Recibe un `report_package` producido por `motor_016` con estado de aprobacion explicito.
- Valida que el paquete contenga identificador, version, vistas aprobadas, referencias de lineage y bloques de salida ya ensamblados.
- Selecciona de forma determinista la plantilla LaTeX y el perfil de render declarados para el paquete.
- Transforma las vistas aprobadas del paquete en `latex_source` sin reescribir ni ampliar contenido.
- Compila la fuente LaTeX en `compiled_pdf` usando una configuracion de compilacion registrada.
- Calcula hashes de entrada, fuente generada, PDF y configuracion de render.
- Emite un `render_manifest` con parametros, versiones, hashes, lineage y resultado de compilacion.

## what_it_does_not_do
- No genera contenido nuevo para el reporte.
- No toma decisiones analiticas ni selecciona conclusiones, claims, tensiones u oportunidades.
- No ensambla `output_blocks`; esa responsabilidad pertenece a `motor_016`.
- No corrige silenciosamente texto, datos, trazabilidad, taxonomias ni metadatos del paquete.
- No valida evidencia de campo ni eleva el nivel epistemico de ningun claim.
- No produce versiones alternativas del reporte por preferencia editorial no declarada.

## why_it_exists
Existe como motor separado porque el ensamblaje del paquete y la renderizacion documental son responsabilidades distintas. `motor_016` entrega un paquete aprobado; `motor_017` garantiza que ese paquete pueda convertirse en un documento tecnico reproducible, auditable y versionado sin redisenar el contenido ni mezclar logica de reporting con logica de compilacion.
