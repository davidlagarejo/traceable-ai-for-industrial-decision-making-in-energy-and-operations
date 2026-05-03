# Master Concept Document — Output Block Composition Engine

Motor ID: motor_015

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Construir bloques visibles trazables para Fase 3 desde decisions e inferencias.
why_it_exists:  Separa contenido visible gobernado del ensamblaje documental final.
key_inputs:     inference_records (motor_014), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    output_block, block_trace, composition_log
key_objects:    OutputBlock, BlockTrace, CompositionRecord
what_not_to_do: No ensambla reportes completos. No renderiza documentos. Solo construye bloques atómicos.
design_notes:   Cada bloque es trazable a su fuente inferencialmente.

Documentation-base content completed for this artifact.
-->

## purpose
El Output Block Composition Engine construye bloques visibles atomicos para Fase 3 a partir de registros de inferencia producidos por `motor_014`. Cada bloque conserva referencias explicitas al contrato de fase, a los registros de version y al lineage que autorizan su existencia. Su salida no es un reporte completo, sino una unidad visible gobernada que puede ser ensamblada despues por motores downstream.

## what_it_does
- Recibe `inference_records` producidos por `motor_014`.
- Recibe `phase_contracts` de `motor_001` para confirmar que la composicion de bloques esta autorizada.
- Recibe `version_records` de `motor_002` para adjuntar versionado y lineage al bloque visible.
- Valida que cada inferencia tenga identificador estable, contrato aplicable, referencias de lineage y version resolubles.
- Aplica reglas deterministas de mapeo entre tipo de inferencia y tipo de bloque permitido.
- Construye un `output_block` atomico con `block_id`, `block_type`, `visible_payload`, referencias de fuente y metadatos de contrato.
- Construye un `block_trace` que vincula cada parte visible del bloque con sus inferencias, versiones y lineage.
- Registra un `composition_log` con inputs usados, reglas aplicadas, rechazos y resultado de la operacion.

## what_it_does_not_do
- No ensambla reportes completos, paquetes de reporte, vistas tecnicas ni vistas ejecutivas.
- No renderiza documentos, paginas, PDF, HTML, LaTeX ni formatos visuales finales.
- No produce inferencias nuevas, no resuelve tensiones y no verifica claims.
- No modifica `inference_records`, `phase_contracts`, `version_records` ni lineage upstream.
- No decide orden global de un reporte ni narrativa inter-bloque.
- No acepta contenido narrativo libre que no provenga de inferencias y contratos autorizados.

## why_it_exists
Este motor existe para separar la construccion de contenido visible gobernado del ensamblaje documental final. La separacion permite que cada bloque sea auditable por si mismo y que el motor que arma reportes no oculte que inferencia, version y contrato autorizaron cada fragmento visible.
