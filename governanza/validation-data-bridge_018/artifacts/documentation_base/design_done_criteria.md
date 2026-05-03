# Design Done Criteria — Validation Data Bridge

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

## criteria
- `master_concept_doc.md` define proposito, acciones, limites y razon de existencia especificos para Validation Data Bridge.
- `functional_contract.md` lista los cinco inputs obligatorios desde motores 004, 005, 006, 007 y 008, y los tres outputs `validation_data_set`, `bridge_manifest` y `evidentiary_record`.
- `functional_contract.md`, `conceptual_schema.md` y `operational_rules.md` no contienen marcadores abiertos ni placeholders.
- `conceptual_schema.md` define `ValidationDataSet`, `BridgeRecord` y `EvidentiaryLink` con campos minimos, relaciones y nivel `validation_data`.
- `operational_rules.md` prohibe explicitamente datos sinteticos, produccion de `field_evidence`, mutacion de registros upstream y cierre de claims.
- `acceptance_tests.md` cubre happy path, identidad ambigua, derechos parciales, dataset sin elegibles y criterios de rechazo estructurados.
- `failure_modes.md` enumera contaminacion sintetica, ruptura de lineage, perdida de restricciones y colapso de ambiguedad como fallos observables.
- Todo output conceptual preserva referencias a fuente, ingesta, normalizacion, identidad cuando existe, calidad, derechos y version del dataset.
