# Functional Contract — Dataset / Object Test Harness Engine

Motor ID: motor_021

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
why_it_exists:  Los motores pueden pasar solos y aun así fallar juntos en integración.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    test_result, harness_report, integration_failure_log
key_objects:    TestResult, HarnessReport, IntegrationFailure
what_not_to_do: No modifica datos. No produce outputs analíticos. Solo prueba y reporta.
design_notes:   Harness transversal. Prueba el sistema integrado, no motores individuales.

Documentation-base content is filled for Gate 1 review.
-->

## inputs
- `phase_contracts`: list[PhaseContract-like object] — source: motor_001; contiene `contract_id`, `phase_id`, `required_inputs`, `required_outputs`, `allowed_object_types`, `field_requirements`, `handoff_rules`, `version`, `status` y provenance.
- `version_records`: list[VersionRecord-like object] — source: motor_002; contiene `version_id`, `object_id`, `object_type`, `object_version`, `lineage_refs`, `provenance_refs`, `prior_version_ref`, `created_at` y `change_reason`.
- `canonical_taxonomy`: TaxonomySnapshot-like object — source: motor_003; contiene `taxonomy_id`, `taxonomy_version`, `allowed_terms`, `object_type_registry`, `relationship_types`, `status`, `effective_at` y provenance.
- `normalized_records`: list[NormalizedRecord-like object] — source: motor_005; contiene `record_id`, `dataset_id`, `schema_ref`, `field_values`, `taxonomy_refs`, `version_ref`, `lineage_refs`, `normalized_at` y provenance.
- `identity_records`: list[IdentityRecord-like object] — source: motor_006; contiene `identity_id`, `entity_ref`, `canonical_entity_id`, `alias_refs`, `confidence_policy_ref`, `lineage_refs`, `version_ref` y `resolved_at`.
- `quality_records`: list[QualityRecord-like object] — source: motor_007; contiene `quality_record_id`, `subject_ref`, `phase_contract_ref`, `evaluation_status`, `quality_flags`, `fitness_score`, `evaluated_at`, `version_ref` y provenance.

## outputs
- `test_result`: TestResult object — destination: harness report, audit trail and downstream conformance consumers; contiene un resultado por caso con `test_id`, `case_name`, `status`, `input_refs`, `expected_condition`, `observed_condition`, `failure_ids`, `severity`, `executed_at` y `harness_version`.
- `harness_report`: HarnessReport object — destination: operators, orchestrator, conformance review and integration audit; contiene resumen de ejecucion, cobertura, conteos por estado, contratos probados, datasets probados, fallas enlazadas y decision `pass`, `warning` o `fail`.
- `integration_failure_log`: list[IntegrationFailure] — destination: audit trail, issue triage and correction workflow; registra cada falla con objeto afectado, contrato esperado, valor observado, tipo de falla, severidad, referencias de evidencia y accion recomendada para el motor propietario.

## limits
- No acepta inputs que no sean colecciones u objetos estructurados con identificadores estables y referencias de provenance o lineage cuando el contrato las exige.
- No acepta contratos de fase con `status` distinto de `active`, `approved` o equivalente cerrado para prueba.
- No acepta objetos bajo prueba sin `object_id`, `record_id`, `identity_id`, `quality_record_id` u otro identificador primario declarado.
- No acepta taxonomias sin version vigente, lista de terminos permitidos y registro de tipos de objeto.
- No produce datos modificados, records corregidos, contratos corregidos, taxonomias nuevas, identities fusionadas ni quality scores.
- No produce outputs analiticos, conclusiones de investigacion, decisiones epistémicas ni aprobaciones de conformidad arquitectonica.
- No emite `harness_report.status = pass` si existe una `IntegrationFailure` con severidad `critical` o un `TestResult.status = fail`.

## validations
- Rechaza el lote con `INVALID_HARNESS_INPUT` si todos los inputs principales estan vacios o si alguno no tiene la forma estructurada esperada.
- Rechaza cada contrato sin `contract_id`, `phase_id`, `required_outputs`, `field_requirements`, version y estado cerrado para prueba.
- Rechaza cada version record sin `version_id`, `object_id`, `object_type`, `object_version`, timestamp y al menos una referencia de lineage o provenance.
- Rechaza cada taxonomy snapshot sin `taxonomy_id`, `taxonomy_version`, `allowed_terms` y `object_type_registry`.
- Rechaza records normalizados que declaren `taxonomy_refs`, `schema_ref` o `version_ref` inexistentes en los inputs de taxonomia, contratos o versionado.
- Rechaza identity records que no tengan `identity_id`, `entity_ref`, `canonical_entity_id` y referencia de lineage o version.
- Rechaza quality records que no tengan `quality_record_id`, `subject_ref`, `evaluation_status`, `evaluated_at` y referencia al contrato o version evaluada.
- Antes de ejecutar cada caso, verifica que los objetos requeridos por el caso existan y que sus referencias cruzadas puedan resolverse dentro del lote.
- Antes de emitir `test_result`, asegura que cada resultado incluya `test_id`, `case_name`, `status`, `input_refs`, `expected_condition`, `observed_condition`, `executed_at` y `harness_version`.
- Antes de emitir `harness_report`, asegura que los conteos agregados coincidan con la lista de `test_result` y que toda falla referenciada exista en `integration_failure_log`.
- Emite errores estructurados `INVALID_HARNESS_INPUT`, `UNRESOLVED_REFERENCE`, `CONTRACT_MISMATCH`, `TAXONOMY_MISMATCH`, `LINEAGE_GAP` o `UNSAFE_HARNESS_REPORT` segun la condicion detectada.
