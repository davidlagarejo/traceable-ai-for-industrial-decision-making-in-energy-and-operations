# Master Concept Document — Report Package Assembly Engine

Motor ID: motor_016

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ensamblar Output Blocks en Report Package con vistas como technical_view y executive_view.
why_it_exists:  Un bloque no equivale a un reporte integrado.
key_inputs:     output_blocks (motor_015), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    report_package, technical_view, executive_view
key_objects:    ReportPackage, TechnicalView, ExecutiveView
what_not_to_do: No genera texto nuevo. No renderiza documentos finales. Solo ensambla paquetes desde bloques.
design_notes:   Ensambla sin transformar. Mantiene trazabilidad de bloques.

Sections completed for the documentation_base gate.
-->

## purpose
El Report Package Assembly Engine ensambla Output Blocks aprobados en un ReportPackage integrado y reproducible. Produce vistas estructuradas como technical_view y executive_view mediante selección, ordenamiento y referencia de bloques existentes, sin reescribirlos ni generar contenido nuevo. Su trabajo principal es convertir bloques trazables en un paquete de reporte coherente, con manifest de ensamblaje, referencias de contrato de fase y vínculos de versionado.

## what_it_does
- Recibe output_blocks emitidos por motor_015 y verifica que cada bloque tenga identidad, tipo, contenido cerrado, provenance y block_trace.
- Recibe phase_contracts desde motor_001 y usa sus reglas para validar que los bloques pertenecen a la fase y al tipo de reporte permitidos.
- Recibe version_records desde motor_002 y adjunta referencias de versión y lineage al paquete ensamblado.
- Ordena los bloques de forma determinista usando la prioridad declarada por contrato, el tipo de bloque y el identificador estable del bloque.
- Construye report_package como contenedor integrado con manifest de bloques, vistas disponibles, referencias de origen y checksum lógico de ensamblaje.
- Construye technical_view como una vista de bloques técnicos completos, con referencias explícitas a los block_id incluidos y a sus trazas.
- Construye executive_view como una vista de bloques ya marcados como aptos para consumo ejecutivo, preservando su contenido original.
- Registra errores estructurados cuando faltan bloques requeridos, metadatos críticos o compatibilidad con el contrato de fase.

## what_it_does_not_do
- No genera texto nuevo, resúmenes, conclusiones, claims, recomendaciones ni narrativa editorial.
- No renderiza documentos finales, PDFs, LaTeX, HTML, slides ni entregables externos.
- No crea Output Blocks; solo ensambla paquetes desde bloques producidos y trazados por motor_015.
- No recalcula inferencias, calidad, derechos de fuente, identity resolution, taxonomías ni validación de campo.
- No modifica el contenido interno de los bloques recibidos; solo puede referenciarlos, ordenarlos y agruparlos.
- No decide si un reporte es epistemológicamente verdadero; solo verifica que el ensamblaje cumple contrato, lineage y límites de fase.

## why_it_exists
Un Output Block aislado no equivale a un reporte integrado: falta una estructura reproducible que declare qué bloques forman el paquete, en qué vistas aparecen y bajo qué contrato fueron ensamblados. Este motor existe separado de la composición de bloques y del rendering final para ensamblar sin transformar, mantener trazabilidad bloque por bloque y permitir que motores posteriores rendericen documentos desde un paquete ya gobernado.
