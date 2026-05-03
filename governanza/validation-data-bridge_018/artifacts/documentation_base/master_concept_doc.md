# Master Concept Document — Validation Data Bridge

Motor ID: motor_018

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Conectar datos estructurados del framework con evidencia local, medición y datos de sitio.
why_it_exists:  La verificación necesita anclarse al sistema completo de Fase 1.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    validation_data_set, bridge_manifest, evidentiary_record
key_objects:    ValidationDataSet, BridgeRecord, EvidentiaryLink
what_not_to_do: No puede ser sustituido por datos sintéticos. No produce field_evidence. Solo estructura datos reales para validación.
design_notes:   Produce evidencia de nivel validation_data (no synthetic_support). Requiere pipeline completo de Fase 1.
-->

## purpose
Validation Data Bridge conecta los registros estructurados del framework con datos reales aptos para validacion local, medicion y contexto de sitio. Toma registros ya ingeridos, normalizados, resueltos por identidad, evaluados por calidad y respaldados por registro de fuente, y los organiza como `validation_data`. Su funcion es preparar un puente trazable entre datos reales estructurados y procesos posteriores de verificacion, sin producir evidencia de campo nueva.

## what_it_does
- Recibe `source_registry` desde motor_008 y verifica que cada fuente tenga derechos, clase de acceso y uso permitido compatibles con validacion.
- Recibe `ingestion_records` desde motor_004 y conserva referencias al raw, parsed record e ingestion lineage.
- Recibe `normalized_records` desde motor_005 y enlaza cada valor canonico con su valor original y traza de normalizacion.
- Recibe `identity_records` desde motor_006 y conserva resoluciones, clusters y banderas de ambiguedad sin forzar merges nuevos.
- Recibe `quality_records` desde motor_007 y filtra o marca registros no aptos segun fitness, flags y razones de descalificacion.
- Construye `BridgeRecord` para cada registro real elegible, con lineage completo hacia fuente, ingesta, normalizacion, identidad y calidad.
- Agrupa los `BridgeRecord` en un `ValidationDataSet` con alcance, version, criterios de inclusion y resumen de exclusiones.
- Produce un `bridge_manifest` que documenta fuentes usadas, registros incluidos, registros rechazados y restricciones de uso.
- Produce `evidentiary_record` de nivel `validation_data`, no `field_evidence`, para consumidores posteriores.

## what_it_does_not_do
- No puede ser sustituido por datos sinteticos ni por outputs de nivel `synthetic_support`.
- No produce `field_evidence`; solo estructura datos reales ya presentes para validacion.
- No ingesta archivos, APIs ni feeds; esa responsabilidad pertenece a motor_004.
- No normaliza valores ni aplica taxonomias canonicas; esa responsabilidad pertenece a motor_005.
- No resuelve identidad ni deduplicacion de entidades; esa responsabilidad pertenece a motor_006.
- No evalua calidad por primera vez ni corrige registros defectuosos; consume los resultados de motor_007.
- No registra licencias ni derechos de fuente; consume el registro gobernado por motor_008.
- No cierra claims ni decide veracidad; prepara insumos trazables para etapas de verificacion.

## why_it_exists
Existe como motor separado porque la conversion de registros estructurados a `validation_data` exige combinar metadatos de fuente, lineage, identidad y calidad sin invadir los motores que los producen. La verificacion necesita un insumo real y auditable de nivel `validation_data`, distinto de `field_evidence` y de cualquier soporte sintetico.
