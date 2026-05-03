# Failure Modes — Validation Data Bridge

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

## failure_modes_list
- UNREGISTERED_SOURCE_LEAK: aparecen registros en `validation_data_set` cuyo `source_id` no existe en `source_registry` o no tiene perfil de derechos vigente.
- LINEAGE_BREAK: un `BridgeRecord` no puede reconstruirse hasta raw record, parsed record, normalized record, identity record cuando existe y quality record.
- SYNTHETIC_CONTAMINATION: objetos con `synthetic_data_flag`, `synthetic_support_flag` o procedencia sintetica entran al dataset.
- QUALITY_OVERRIDE: registros descalificados por motor_007 aparecen como elegibles sin razon de excepcion gobernada.
- RIGHTS_RESTRICTION_LOSS: restricciones de acceso, licencia o redistribucion desaparecen del `bridge_manifest` o de los `EvidentiaryLink`.
- IDENTITY_AMBIGUITY_COLLAPSE: registros con identidad ambigua son tratados como identidad resuelta sin conservar la bandera de ambiguedad.

## anti_patterns
- Usar el puente como una segunda normalizacion, editando valores canonicos o reescribiendo field mappings.
- Tratar `validation_data` como `field_evidence` y usarlo para cerrar claims sin pasar por el motor de verificacion correspondiente.
- Mezclar datos sinteticos con datos reales para completar huecos de cobertura.
- Ignorar restricciones de fuente porque el dato ya fue ingerido o normalizado.
- Excluir silenciosamente registros incomodos sin registrarlos en el manifiesto.

## degradation_signals
- Aumento sostenido de registros con lineage incompleto frente al total de candidatos.
- Porcentaje de exclusiones sin razon estructurada mayor que cero.
- Diferencia entre registros incluidos en `validation_data_set` y registros listados en `bridge_manifest`.
- Presencia de `source_id` no registrado, derechos vencidos o restricciones no propagadas.
- Caida abrupta del promedio de `fitness_score` sin cambio declarado en fuentes o criterios de inclusion.
- Crecimiento de registros `eligible` con `ambiguity_flag=true`, lo que indica colapso de ambiguedad.
- Aparicion de cualquier campo `synthetic_data_flag=true` o `synthetic_support_flag=true` en inputs aceptados.
