# Operational Rules — Validation Data Bridge

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

## rules
1. Todo `BridgeRecord` debe referenciar un `source_id` existente en `source_registry` y un `rights_profile` que permita uso para validacion.
2. Todo `BridgeRecord` debe preservar referencias a `ingestion_record`, `normalized_record` y `quality_record`; si falta una de esas referencias, el registro se rechaza.
3. Todo dato incluido en `validation_data_set` debe provenir de registros reales procesados por motores 004, 005, 006 cuando aplique, 007 y 008.
4. Todo registro con `disqualification_reason` no vacio queda excluido del dataset y registrado en `bridge_manifest`.
5. Todo registro con identidad ambigua puede incluirse solo con `validation_status=eligible_with_warning` y con la bandera de ambiguedad preservada.
6. Ningun output puede declarar nivel evidentiary distinto de `validation_data`.
7. El motor debe registrar razon explicita para cada exclusion, advertencia o restriccion propagada.
8. El motor debe ser reconstruible desde los ids de fuente, ingesta, normalizacion, identidad, calidad y version del dataset.

## invariants
- `evidence_level` permanece igual a `validation_data` en `ValidationDataSet`, `BridgeRecord` y `EvidentiaryLink`.
- `source_id` nunca es nulo en registros incluidos ni en registros excluidos documentados.
- `ingestion_record_id`, `normalized_record_id` y `quality_record_id` nunca son nulos para un `BridgeRecord` emitido.
- Las restricciones de derechos y acceso de motor_008 se conservan sin relajacion.
- Los valores originales preservados por motor_005 siguen referenciables desde cada registro incluido.
- Las banderas de identidad ambigua y calidad degradada se propagan, no se corrigen silenciosamente.
- El manifiesto siempre permite reconstruir el conjunto de incluidos y excluidos.

## forbidden_operations
- Sustituir datos reales por datos sinteticos o por `synthetic_support`.
- Producir `field_evidence` o declararse como fuente primaria de medicion de campo.
- Ingerir fuentes nuevas, leer archivos crudos no registrados o llamar APIs externas.
- Modificar raw records, parsed records, normalized records, identity records o quality records.
- Normalizar valores, resolver identidad, calcular fitness score o editar derechos de fuente.
- Elevar un registro con restriccion de uso a un estado permitido sin autorizacion upstream.
- Cerrar verificaciones, emitir decisiones de verdad, producir TAD final o actualizar claims.
- Ocultar registros excluidos para mejorar artificialmente cobertura o calidad aparente.
