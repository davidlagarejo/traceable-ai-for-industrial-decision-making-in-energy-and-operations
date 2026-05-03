# Master Concept Document — Ingestion + Parsing Engine

Motor ID: motor_004

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Capturar fuentes, preservar raw y extraer estructura parcial trazable.
why_it_exists:  Permite que el mundo real entre al sistema sin contaminarlo.
key_inputs:     raw source files, API responses, structured feeds
key_outputs:    raw_record (preserved), parsed_record, ingestion_lineage
key_objects:    RawRecord, ParsedRecord, IngestionEvent
what_not_to_do: No normaliza. No resuelve duplicados. No evalúa calidad. Solo ingesta y preserva.
design_notes:   Preserva siempre el raw. La extracción es parcial e inmutable. Depende de motor_001 y motor_002.

All placeholder content in this artifact has been completed.
-->

## purpose
El Ingestion + Parsing Engine captura entradas provenientes de archivos fuente, respuestas de API y feeds estructurados sin alterar su contenido original. Su responsabilidad principal es preservar el raw como registro reconstruible y extraer una estructura parcial, explícitamente trazada al raw y al evento de ingesta que la produjo. La extracción parcial solo organiza campos observables; no convierte valores a forma canónica ni decide si los datos son correctos, duplicados o aptos para uso analítico.

## what_it_does
- Recibe payloads de entrada desde archivos fuente, respuestas de API o feeds estructurados autorizados por el contrato de fase vigente.
- Registra un `IngestionEvent` con identificador estable, origen, timestamp de captura, contrato de fase aplicable y referencia de lineage.
- Preserva el payload original como `RawRecord`, incluyendo ubicación del raw, media type declarado, checksum y metadatos de captura.
- Ejecuta parsing mínimo y determinista para extraer campos observables sin modificar los valores originales.
- Produce un `ParsedRecord` vinculado uno a uno con su `RawRecord` cuando el parser aplicable puede extraer estructura parcial.
- Emite `ingestion_lineage` que conecta fuente, evento de ingesta, raw preservado, parser utilizado y parsed record resultante.
- Registra rechazos explícitos cuando falta provenance, el payload está vacío, el tipo de contenido no está declarado o el formato no puede procesarse sin pérdida de raw.

## what_it_does_not_do
- No normaliza valores, nombres, unidades, categorías, fechas ni identificadores hacia una forma canónica.
- No resuelve duplicados exactos, near-duplicates ni equivalencias entre registros.
- No evalúa calidad, completitud, confiabilidad, autoridad de fuente ni aptitud de uso.
- No resuelve identidad de entidades ni decide si dos registros describen el mismo objeto real.
- No corrige silenciosamente errores de formato, encoding, campos faltantes o valores inconsistentes.
- No descarta el raw después del parsing ni reemplaza el raw con la estructura extraída.
- No produce claims analíticos, inferencias, reportes visibles ni decisiones downstream.

## why_it_exists
Existe como motor separado porque el punto de entrada del mundo real debe quedar aislado de normalización, evaluación y razonamiento. Su diseño garantiza que todo dato capturado conserva una copia raw inmutable y que cualquier estructura extraída queda subordinada a ese raw, con lineage registrado mediante las capacidades de versionado y trazabilidad del motor_002 y bajo los límites de fase definidos por motor_001.
