# Conceptual Schema — Dataset / Object Test Harness Engine

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

## entities
- `TestResult`: resultado determinista de un caso de prueba aplicado a uno o varios objetos, contratos o handoffs del sistema.
- `HarnessReport`: reporte agregado de una ejecucion del harness, con cobertura, resumen de estados, referencias de contratos probados y decision operativa.
- `IntegrationFailure`: registro estructurado de una falla de integracion detectada entre contratos, versiones, taxonomia, records normalizados, identidades o calidad.

## relationships
- `phase_contracts.PhaseContract` -> `TestResult` (cada caso compara objetos observados contra requisitos contractuales declarados).
- `version_records.VersionRecord` -> `TestResult` (cada prueba de lineage o versionado usa versiones como evidencia de reconstruccion).
- `canonical_taxonomy.TaxonomySnapshot` -> `TestResult` (cada prueba de taxonomia valida terminos, tipos y relaciones contra la version canonica).
- `normalized_records.NormalizedRecord` -> `TestResult` (cada prueba de dataset valida estructura, referencias y compatibilidad con contrato).
- `identity_records.IdentityRecord` -> `TestResult` (cada prueba de identidad valida consistencia de entidad y alias usados por objetos bajo prueba).
- `quality_records.QualityRecord` -> `TestResult` (cada prueba de calidad verifica que el objeto bajo prueba tenga evaluacion esperada cuando el contrato la requiere).
- `TestResult` -> `IntegrationFailure` (un resultado `fail` o `warning` puede crear una o varias fallas estructuradas con severidad y evidencia).
- `TestResult` -> `HarnessReport` (cada reporte agrega muchos resultados de prueba de una misma ejecucion).
- `IntegrationFailure` -> `HarnessReport` (cada reporte enlaza las fallas que justifican decision `warning` o `fail`).

## key_fields
`TestResult`
- `test_id`: string
- `case_name`: string
- `status`: enum string (`pass`, `warning`, `fail`, `skipped`)
- `input_refs`: list[string]
- `expected_condition`: string
- `observed_condition`: string
- `failure_ids`: list[string]
- `severity`: enum string (`info`, `warning`, `critical`)
- `executed_at`: datetime string
- `harness_version`: string

`HarnessReport`
- `harness_run_id`: string
- `harness_version`: string
- `tested_contract_refs`: list[string]
- `tested_object_refs`: list[string]
- `result_counts`: object with integer counts for `pass`, `warning`, `fail` and `skipped`
- `coverage_summary`: object
- `failure_log_ref`: string|null
- `status`: enum string (`pass`, `warning`, `fail`)
- `generated_at`: datetime string

`IntegrationFailure`
- `failure_id`: string
- `failure_type`: enum string (`contract_mismatch`, `taxonomy_mismatch`, `unresolved_reference`, `lineage_gap`, `identity_conflict`, `quality_missing`, `handoff_incompatible`)
- `affected_object_ref`: string
- `expected_ref`: string
- `observed_value`: string
- `source_input_refs`: list[string]
- `severity`: enum string (`warning`, `critical`)
- `owner_motor_ref`: string
- `detected_at`: datetime string
