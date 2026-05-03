# Conceptual Schema — Validation Data Bridge

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

## entities
- ValidationDataSet: paquete versionado que agrupa `BridgeRecord` elegibles y declara alcance, nivel evidentiary, fuentes, criterios de inclusion y exclusiones.
- BridgeRecord: registro atomico que conecta un dato real normalizado con su fuente, ingesta, identidad, evaluacion de calidad y estado de aptitud para validacion.
- EvidentiaryLink: enlace trazable entre un `BridgeRecord` y los artefactos upstream que justifican su uso como `validation_data`.

## relationships
- ValidationDataSet -> BridgeRecord (contiene uno o mas registros elegibles para un alcance de validacion especifico).
- BridgeRecord -> EvidentiaryLink (cada registro contiene uno o mas enlaces que prueban fuente, lineage, normalizacion, identidad y calidad).
- BridgeRecord -> source_registry entry (cada registro debe apuntar a exactamente una fuente registrada y permitida).
- BridgeRecord -> ingestion_record (cada registro debe conservar referencia al raw o parsed record que origino el dato real).
- BridgeRecord -> normalized_record (cada registro debe apuntar al valor canonico y a su valor original preservado).
- BridgeRecord -> identity_record (cada registro apunta a una resolucion de identidad cuando existe; si queda ambigua, la ambiguedad se conserva).
- BridgeRecord -> quality_record (cada registro debe apuntar a una evaluacion de aptitud y trazabilidad emitida por motor_007).
- EvidentiaryLink -> bridge_manifest (cada enlace queda resumido en el manifiesto para reconstruccion y auditoria).

## key_fields
ValidationDataSet:
- validation_data_set_id: string
- dataset_version: string
- evidence_level: enum[`validation_data`]
- generated_at: datetime
- bridge_record_ids: list[string]
- source_registry_snapshot_id: string
- exclusion_summary: dict[string, integer]

BridgeRecord:
- bridge_record_id: string
- source_id: string
- ingestion_record_id: string
- normalized_record_id: string
- identity_record_id: string|null
- quality_record_id: string
- validation_status: enum[`eligible`, `eligible_with_warning`, `excluded`]
- lineage_refs: list[string]

EvidentiaryLink:
- evidentiary_link_id: string
- bridge_record_id: string
- upstream_artifact_ref: string
- link_type: enum[`source_rights`, `ingestion_lineage`, `normalization_trace`, `identity_resolution`, `quality_assessment`]
- evidence_level: enum[`validation_data`]
- restriction_refs: list[string]
