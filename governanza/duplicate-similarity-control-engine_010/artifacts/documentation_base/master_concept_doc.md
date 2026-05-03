# Master Concept Document — Duplicate / Similarity Control Engine

Motor ID: motor_010

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar duplicados exactos y near-duplicates a nivel raw, parsed y otros niveles.
why_it_exists:  No es lo mismo que identity resolution; controla repetición documental y dataset inflation.
key_inputs:     parsed_records (motor_004), normalized_records (motor_005), version_records (motor_002)
key_outputs:    duplicate_cluster, similarity_score, dedup_recommendation
key_objects:    DuplicateCluster, SimilarityRecord, DeduplicationDecision
what_not_to_do: No resuelve identidad de entidades. No evalúa calidad. Solo detecta repetición.
design_notes:   Opera antes de resolución de identidad. Controla repetición documental, no semántica.

Sections completed for Gate 1 validation.
-->

## purpose
Este motor detecta duplicados exactos y near-duplicates entre registros documentales en niveles raw, parsed y normalized. Compara representaciones trazables de contenido y campos estructurados para identificar repetición documental antes de que otros motores consuman el dataset. Su salida no afirma identidad de entidades ni calidad del registro; solo declara evidencia de repetición y recomienda tratamiento no destructivo.

## what_it_does
- Recibe `parsed_records` desde `motor_004`, `normalized_records` desde `motor_005` y `version_records` desde `motor_002`.
- Valida que cada registro comparable tenga identificador estable, provenance, lineage o referencia de versión suficiente para auditar la comparación.
- Construye fingerprints deterministas por nivel: raw content hash cuando existe, firma de campos parsed y firma de campos normalized.
- Detecta duplicados exactos cuando dos o más registros tienen fingerprints equivalentes en el mismo nivel de comparación.
- Detecta near-duplicates cuando la similitud determinista entre firmas normalizadas supera umbrales versionados y auditables.
- Agrupa pares aceptados en `DuplicateCluster` sin modificar los registros de origen.
- Emite `SimilarityRecord` por comparación aceptada o revisable, con score, nivel de comparación y evidencia usada.
- Emite `DeduplicationDecision` como recomendación no destructiva para consumidores downstream.

## what_it_does_not_do
- No resuelve identidad de entidades, organizaciones, personas, instalaciones ni conceptos.
- No evalúa calidad, fitness, confiabilidad, completitud ni valor epistemológico de los registros.
- No descarga, parsea, normaliza ni versiona datos; consume resultados ya producidos por motores upstream.
- No elimina, fusiona, sobrescribe ni corrige registros de origen.
- No convierte similitud documental en equivalencia semántica o en claim analítico.
- No decide políticas finales de curación; solo entrega evidencia y recomendación de deduplicación.

## why_it_exists
Existe como motor separado porque la repetición documental infla datasets y distorsiona conteos antes de la resolución de identidad. Su responsabilidad es controlar duplicación de documentos o registros reutilizando lineage y versionado, mientras que la identidad de entidades y la evaluación de calidad permanecen en motores distintos.
