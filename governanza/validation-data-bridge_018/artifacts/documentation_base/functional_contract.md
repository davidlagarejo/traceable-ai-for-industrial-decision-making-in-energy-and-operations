# Functional Contract — Validation Data Bridge

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

## inputs
- source_registry: SourceRegistrySnapshot — motor_008; contiene `source_registration`, `rights_profile`, `access_class`, restricciones de uso y calendario de refresco.
- ingestion_records: list[IngestionRecord] — motor_004; contiene referencias a `raw_record`, `parsed_record` e `ingestion_lineage` para datos reales de fuentes locales, mediciones o sitio.
- normalized_records: list[NormalizedRecord] — motor_005; contiene valores canonicos, valores originales preservados, `normalization_rule_log` y `field_mapping_trace`.
- identity_records: list[IdentityRecord] — motor_006; contiene resoluciones de entidad, clusters, conflictos y `ambiguity_flag` cuando la identidad no esta cerrada.
- quality_records: list[QualityRecord] — motor_007; contiene `fitness_score`, `quality_flags`, completitud, trazabilidad y `disqualification_reason` cuando aplica.

## outputs
- validation_data_set: ValidationDataSet — paquete versionado para Verification Bridge, Decision Core y motores de evaluacion que requieran datos reales estructurados.
- bridge_manifest: BridgeManifest — manifiesto auditable para observabilidad, revision de conformidad y reconstruccion del puente.
- evidentiary_record: EvidentiaryRecord — registro de nivel `validation_data` que declara alcance, fuente, lineage y limites de uso para consumidores posteriores.

## limits
- Nunca acepta datos sinteticos, `synthetic_generation_run`, `capability_demonstration_report` ni cualquier objeto marcado como `synthetic_support`.
- Nunca produce `field_evidence`; la salida maxima de este motor es `validation_data`.
- Nunca acepta registros sin referencia valida a fuente registrada en `source_registry`.
- Nunca acepta registros que no tengan lineage de ingesta, normalizacion y calidad.
- Nunca corrige, normaliza, fusiona, re-clasifica o re-puntua registros de entrada.
- Nunca produce decisiones de verificacion, cierres de claim, inferencias finales ni rankings.
- Nunca elimina restricciones de licencia, acceso o uso declaradas por motor_008.

## validations
- Rechaza todo registro cuyo `source_id` no exista en `source_registry` o cuyo `rights_profile` prohiba el uso para validacion.
- Rechaza todo registro sin `ingestion_record_id`, `raw_record_ref` o `ingestion_lineage`.
- Rechaza todo `normalized_record` que no conserve referencia al valor original y a la regla de normalizacion aplicada.
- Marca como `identity_ambiguous` todo registro cuyo `identity_record` tenga `ambiguity_flag=true`; no fuerza resolucion.
- Excluye de `validation_data_set` todo registro con `quality_record.disqualification_reason` no vacio.
- Emite advertencia estructurada cuando `fitness_score` existe pero esta por debajo del umbral declarado para el dataset.
- Antes de emitir salida, verifica que cada `BridgeRecord` tenga referencias cruzadas a fuente, ingesta, normalizacion, identidad cuando exista, calidad y restricciones de uso.
- Antes de emitir salida, verifica que `validation_data_set.evidence_level` sea exactamente `validation_data`.
- Antes de emitir salida, verifica que `bridge_manifest` liste incluidos, excluidos y razones de exclusion de forma reconstruible.
