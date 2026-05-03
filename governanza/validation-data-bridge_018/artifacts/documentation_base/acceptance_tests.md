# Acceptance Tests — Validation Data Bridge

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

## happy_path
Input: `source_registry` contiene `SRC-LOCAL-001` con `rights_profile.validation_use=true`; `ingestion_records` contiene `ING-100` con `raw_record_ref=RAW-100` e ingestion lineage completo; `normalized_records` contiene `NORM-100` con `source_value="12.4"` y `canonical_value=12.4`; `identity_records` contiene `ID-100` sin ambiguedad; `quality_records` contiene `QUAL-100` con `fitness_score=0.94` y sin `disqualification_reason`.

Action: el motor cruza los ids, verifica derechos, lineage, normalizacion, identidad y calidad, y construye un puente de validacion.

Expected output: `validation_data_set` con `evidence_level=validation_data`, un `BridgeRecord` elegible para `NORM-100`, un `bridge_manifest` que lista `SRC-LOCAL-001` y cero exclusiones, y un `evidentiary_record` con enlaces a `ING-100`, `NORM-100`, `ID-100`, `QUAL-100` y el perfil de derechos de la fuente.

## edge_cases
- Registro con identidad ambigua: si `identity_records.ID-200.ambiguity_flag=true` pero fuente, ingesta, normalizacion y calidad son validas, el motor emite `BridgeRecord.validation_status=eligible_with_warning`, conserva `identity_record_id=ID-200` y registra la advertencia en `bridge_manifest`.
- Registro apto pero con calidad baja: si `QUAL-300.fitness_score=0.61` y el umbral declarado del dataset es `0.70`, el motor no corrige el score; emite advertencia o exclusion segun politica declarada y registra la razon exacta.
- Fuente con derechos parciales: si `SRC-LOCAL-004` permite uso interno pero no redistribucion, el motor puede incluir el registro solo si el destino declarado respeta esa restriccion y debe propagar `restriction_refs` en cada `EvidentiaryLink`.
- Dataset sin registros elegibles: si todos los registros reales son excluidos por calidad o derechos, el motor emite `validation_data_set` vacio con `exclusion_summary` completo y no fabrica datos sustitutos.

## rejection_criteria
- Rechaza con `SOURCE_NOT_REGISTERED` cuando un registro referencia `source_id=SRC-MISSING` que no existe en `source_registry`.
- Rechaza con `SYNTHETIC_INPUT_NOT_ALLOWED` cuando cualquier input declara `synthetic_data_flag=true`, `synthetic_support_flag=true` o proviene de un objeto sintetico.
- Rechaza con `MISSING_INGESTION_LINEAGE` cuando un registro carece de `ingestion_record_id`, `raw_record_ref` o lineage de ingesta.
- Rechaza con `MISSING_QUALITY_RECORD` cuando un `normalized_record` candidato no tiene evaluacion de calidad correspondiente.
- Rechaza con `RIGHTS_PROFILE_DENIES_VALIDATION` cuando la fuente existe pero su perfil de derechos prohibe uso para validacion.
