# Test Spec — Validation Data Bridge

Motor ID: motor_018

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Conectar datos estructurados del framework con evidencia local, medición y datos de sitio.
why_it_exists:  La verificación necesita anclarse al sistema completo de Fase 1.
key_inputs:     source_registry (motor_008), ingestion_records (motor_004), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    validation_data_set, bridge_manifest, evidentiary_record
key_objects:    ValidationDataSet, BridgeRecord, EvidentiaryLink
what_not_to_do: No puede ser sustituido por datos sintéticos. No produce field_evidence. Solo estructura datos reales para validación.
design_notes:   Produce evidencia de nivel validation_data (no synthetic_support). Requiere pipeline completo de Fase 1.

All test sections are completed with concrete validation scenarios.
-->

## happy_path
Input mínimo válido:
- `source_registry.snapshot_id="SRS-2026-04-VALIDATION"` contiene `source_id="SRC-LOCAL-001"` con `rights_profile_id="RIGHTS-VAL-001"`, `validation_use=true`, `access_class="internal_allowed"` y `restriction_refs=["license:internal-validation-only"]`.
- `ingestion_records` contiene `ingestion_record_id="ING-100"`, `source_id="SRC-LOCAL-001"`, `raw_record_ref="raw://local/100"`, `parsed_record_ref="parsed://local/100"` e `ingestion_lineage=["capture:site_meter_a","parse:v1"]`.
- `normalized_records` contiene `normalized_record_id="NORM-100"`, `source_id="SRC-LOCAL-001"`, `ingestion_record_id="ING-100"`, `original_value_ref="raw://local/100#value"`, `canonical_value_ref="norm://local/100#canonical"` y `normalization_rule_ref="rule://normalization/unit_kw_v1"`.
- `identity_records` contiene `identity_record_id="ID-100"`, `normalized_record_id="NORM-100"` y `ambiguity_flag=false`.
- `quality_records` contiene `quality_record_id="QUAL-100"`, `normalized_record_id="NORM-100"`, `fitness_score=0.94`, `quality_flags=[]` y `disqualification_reason=null`.
- Parámetros del dataset: `validation_scope="site_meter_validation_april_2026"`, `destination_policy_ref="policy:internal-validation"` e `inclusion_criteria=["registered_source","validation_rights_allowed","complete_ingestion_lineage","complete_normalization_trace","quality_not_disqualified"]`.

Expected output:
- `ValidationDataSet.evidence_level` es exactamente `validation_data`, `produced_by_motor="motor_018"`, `source_registry_snapshot_id="SRS-2026-04-VALIDATION"` y `bridge_record_ids` contiene un único id para `NORM-100`.
- El `BridgeRecord` para `NORM-100` conserva `source_id="SRC-LOCAL-001"`, `rights_profile_id="RIGHTS-VAL-001"`, `ingestion_record_id="ING-100"`, `raw_record_ref="raw://local/100"`, `normalized_record_id="NORM-100"`, `identity_record_id="ID-100"`, `identity_ambiguity_flag=false`, `quality_record_id="QUAL-100"`, `fitness_score=0.94`, `validation_status="eligible"`, `warning_codes=[]`, `exclusion_reason=null`, `evidence_level="validation_data"` y `restriction_refs=["license:internal-validation-only"]`.
- Se emiten `EvidentiaryLink` con `link_type` `source_rights`, `ingestion_lineage`, `normalization_trace`, `identity_resolution` y `quality_assessment`, cada uno con `evidence_level="validation_data"` y `produced_by_motor="motor_018"`.
- `BridgeManifest.included_record_ids` coincide exactamente con `ValidationDataSet.bridge_record_ids`, `excluded_record_refs=[]`, `exclusion_reasons={}`, `warning_reasons={}`, `restriction_refs=["license:internal-validation-only"]` y `rebuild_inputs` lista los ids de `source_registry`, `ingestion_records`, `normalized_records`, `identity_records` y `quality_records` usados.
- `EvidentiaryRecord.validation_data_set_id` referencia el dataset emitido, `bridge_manifest_id` referencia el manifiesto emitido, `evidence_level="validation_data"` y `limits_of_use` incluye que no es `field_evidence` y que no puede cerrar claims por si solo.

## sparse_case
Input con campos opcionales ausentes:
- Misma estructura que el caso estándar, pero `identity_records=[]`, el candidato `NORM-101` no tiene identidad resuelta, `parsed_record_ref=null` y `quality_records.QUAL-101.fitness_score=null`.
- Los campos obligatorios se mantienen presentes: `source_id="SRC-LOCAL-001"`, `rights_profile_id="RIGHTS-VAL-001"`, `ingestion_record_id="ING-101"`, `raw_record_ref="raw://local/101"`, `normalized_record_id="NORM-101"`, `original_value_ref="raw://local/101#value"`, `canonical_value_ref="norm://local/101#canonical"`, `normalization_rule_ref="rule://normalization/unit_kw_v1"`, `quality_record_id="QUAL-101"` y `disqualification_reason=null`.

Expected behavior:
- El motor no falla por ausencia de `identity_record_id`, porque esa relacion es opcional cuando no existe resolucion de identidad upstream.
- El `BridgeRecord` emitido conserva `identity_record_id=null`, `identity_ambiguity_flag=false`, `parsed_record_ref=null`, `fitness_score=null`, `validation_status="eligible"` y `warning_codes=[]`.
- No se emite `EvidentiaryLink` de tipo `identity_resolution` para ese registro, pero si se emiten enlaces `source_rights`, `ingestion_lineage`, `normalization_trace` y `quality_assessment`.
- `BridgeManifest.rebuild_inputs.identity_records=[]` o no incluye ids de identidad para ese candidato, y el resto de los grupos de rebuild sigue completo.
- El output sigue declarando `evidence_level="validation_data"` en dataset, record, links y evidentiary record.

## malformed_input
Casos de rechazo por input malformado:
- Si un `normalized_record` candidato usa `source_id="SRC-MISSING"` y ese id no existe en `source_registry`, el motor rechaza ese candidato con `SOURCE_NOT_REGISTERED`; no crea `BridgeRecord` elegible y registra la exclusion en `BridgeManifest.exclusion_reasons`.
- Si `source_registry.SRC-LOCAL-002.rights_profile.validation_use=false`, el motor rechaza todos los candidatos de esa fuente con `RIGHTS_PROFILE_DENIES_VALIDATION`; las restricciones se conservan en el manifiesto y no se relajan.
- Si `normalized_records.NORM-102` carece de `ingestion_record_id`, o el `ingestion_record` enlazado carece de `raw_record_ref` o `ingestion_lineage`, el motor rechaza con `MISSING_INGESTION_LINEAGE`.
- Si `normalized_records.NORM-103` no tiene `original_value_ref`, `canonical_value_ref` o `normalization_rule_ref`, el motor rechaza con `MISSING_NORMALIZATION_TRACE`.
- Si `normalized_records.NORM-104` no tiene `quality_record` correspondiente, el motor rechaza con `MISSING_QUALITY_RECORD`.
- Si cualquier input contiene `synthetic_data_flag=true`, `synthetic_support_flag=true` o `source_type="synthetic"`, el motor rechaza el lote afectado con `SYNTHETIC_INPUT_NOT_ALLOWED`; no debe producir registros sustitutos.
- Si un campo requerido tiene tipo invalido, por ejemplo `bridge_record_ids` como string, `quality_flags` como string, `identity_ambiguity_flag` como string o `fitness_score="high"`, el motor rechaza con `SCHEMA_VALIDATION_ERROR` e identifica el campo invalido.

## edge_cases
1. Identidad ambigua conservada:
   - Input: `identity_records.ID-200.ambiguity_flag=true`, fuente registrada, derechos validos, ingesta completa, normalizacion completa y `quality_records.QUAL-200.disqualification_reason=null`.
   - Expected behavior: el motor emite `BridgeRecord.validation_status="eligible_with_warning"`, conserva `identity_record_id="ID-200"`, fija `identity_ambiguity_flag=true`, agrega `warning_codes=["identity_ambiguous"]` y registra `BridgeManifest.warning_reasons[bridge_record_id]=["identity_ambiguous"]`. No cambia el objeto de identidad ni fuerza resolucion.

2. Calidad baja sin descalificacion:
   - Input: `quality_records.QUAL-300.fitness_score=0.61`, `quality_flags=["low_fitness_score"]`, `disqualification_reason=null` y umbral declarado del dataset `minimum_fitness_score=0.70`.
   - Expected behavior: el motor no recalcula el score. Si la politica permite inclusion con advertencia, emite `validation_status="eligible_with_warning"` y `warning_codes=["low_fitness_score"]`; si la politica exige exclusion bajo el umbral, emite exclusion con `exclusion_reason="LOW_FITNESS_SCORE"`. En ambos casos el manifiesto documenta la razon exacta.

3. Todos los candidatos excluidos:
   - Input: tres candidatos reales, dos con `RIGHTS_PROFILE_DENIES_VALIDATION` y uno con `quality_record.disqualification_reason="insufficient_traceability"`.
   - Expected behavior: el motor puede emitir `ValidationDataSet.bridge_record_ids=[]` solo si `BridgeManifest.excluded_record_refs` contiene los tres candidatos y `exclusion_reasons` asigna una razon explicita a cada uno. `exclusion_summary` debe contar `RIGHTS_PROFILE_DENIES_VALIDATION=2` e `QUALITY_DISQUALIFIED=1`. No se fabrican datos sinteticos para llenar el dataset.

4. Restriccion parcial de derechos:
   - Input: `source_registry.SRC-LOCAL-004` permite validacion interna, prohibe redistribucion y aporta `restriction_refs=["license:no-redistribution","access:internal"]`; `destination_policy_ref="policy:internal-validation"` respeta esa restriccion.
   - Expected behavior: el registro puede incluirse como `eligible` o `eligible_with_warning` segun politica declarada, pero cada `BridgeRecord`, `EvidentiaryLink`, `ValidationDataSet`, `BridgeManifest` y `EvidentiaryRecord` conserva las mismas `restriction_refs`. Si el destino declarado exige redistribucion, el candidato se excluye con `RIGHTS_RESTRICTION_CONFLICT`.

5. Rebuild deterministico:
   - Input: el mismo conjunto ordenado de upstream ids, criterios de inclusion, restricciones y scope se procesa dos veces.
   - Expected behavior: los ids canonicos y `version_hash` de `ValidationDataSet`, `BridgeRecord`, `EvidentiaryLink`, `BridgeManifest` y `EvidentiaryRecord` son identicos entre corridas. Si cambia un upstream id, restriccion, warning o exclusion, se emite nuevo `version_hash` y se conserva `parent_id` hacia la version anterior cuando aplica.

## pass_criteria
Un test pasa cuando todas estas condiciones observables se cumplen:
- Todos los objetos emitidos tienen `produced_by_motor="motor_018"`, `evidence_level="validation_data"` cuando el schema lo exige, `version_id`, `version_hash`, `created_at`, `updated_at`, `source_ref`, `produced_at` y `parent_id`.
- Ningun output declara `field_evidence`, `synthetic_support` ni otro nivel evidentiary distinto de `validation_data`.
- Cada `BridgeRecord` incluido referencia una fuente registrada, un perfil de derechos que permite el uso declarado, un `ingestion_record`, un `normalized_record`, un `quality_record` y un `identity_record` solo cuando existe upstream.
- Cada inclusion, exclusion, warning y restriccion aparece en `BridgeManifest` con codigo explicito y es reconstruible desde `rebuild_inputs`.
- `BridgeManifest.included_record_ids` coincide exactamente con `ValidationDataSet.bridge_record_ids`.
- Cada registro incluido tiene `EvidentiaryLink` para derechos de fuente, lineage de ingesta, traza de normalizacion y evaluacion de calidad; tiene enlace de identidad solo si existe `identity_record_id`.
- Las restricciones de motor_008 se propagan sin perdida a dataset, bridge records, links, manifest y evidentiary record.
- Los casos malformados producen los codigos de rechazo esperados y no generan registros elegibles.
- Las corridas repetidas con el mismo contenido producen hashes e ids deterministas.

## fail_criteria
Un test falla si se observa cualquiera de estas condiciones:
- Queda aceptado un registro con `source_id` ausente en `source_registry`, derechos que no permiten validacion, lineage de ingesta incompleto, traza de normalizacion incompleta o sin `quality_record`.
- Cualquier input marcado como sintetico entra al dataset o se usa para crear datos sustitutos.
- Cualquier output declara `evidence_level` diferente de `validation_data` o intenta representar `field_evidence`.
- Un `BridgeRecord` con identidad ambigua aparece como `validation_status="eligible"` sin `identity_ambiguity_flag=true` y sin warning `identity_ambiguous`.
- Un registro descalificado por `quality_record.disqualification_reason` aparece como elegible sin exclusion documentada.
- El motor corrige, normaliza, resuelve identidad, recalcula calidad, edita derechos o modifica registros upstream en lugar de copiar referencias y estados.
- `BridgeManifest` omite registros excluidos, warnings, restricciones, ids upstream o razones de exclusion necesarias para reconstruir el puente.
- `ValidationDataSet.bridge_record_ids` y `BridgeManifest.included_record_ids` divergen.
- Faltan `version_hash`, `version_id`, `source_ref`, `produced_by_motor`, `produced_at` o `parent_id` en cualquier entidad persistida.
- La misma entrada produce ids o hashes distintos sin cambio de contenido, o un cambio de contenido muta un id existente sin nueva version.
